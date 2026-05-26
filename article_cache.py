"""
article_cache.py — Caché persistente de análisis de artículos y síntesis.

Evita re-enviar a Claude artículos ya analizados, reduciendo tokens consumidos
en ciclos donde la mayoría de noticias ya fueron procesadas.

TTLs:
- Artículos individuales: 72 horas
- Análisis general por categoría: 6 horas
- Síntesis cruzada: 6 horas

Backends disponibles (en orden de preferencia):
1. Redis — si REDIS_URL está configurada en el entorno. Persistente en Render.
2. JSON en disco — fallback local (se pierde al reiniciar en Render gratuito).

Uso: importa el singleton `shared` en lugar de crear instancias nuevas,
para que analyzer.py y synthesizer.py compartan el mismo estado en memoria
y no se pisoteen al escribir el archivo.
"""

import json
import os
import time
import hashlib
import threading
from pathlib import Path

_CACHE_FILE    = Path("article_cache.json")
_TTL_ARTICULO  = 72 * 3600   # 72 horas
_TTL_CATEGORIA =  6 * 3600   #  6 horas
_TTL_SINTESIS  =  6 * 3600   #  6 horas

_REDIS_URL = os.getenv("REDIS_URL", "")
_REDIS_KEY = "noticias:cache"


def _conectar_redis():
    """Devuelve un cliente Redis si REDIS_URL está configurada, o None."""
    if not _REDIS_URL:
        return None
    try:
        import redis
        client = redis.from_url(_REDIS_URL, decode_responses=True, socket_timeout=3)
        client.ping()
        print("  ✓ Caché Redis conectada")
        return client
    except Exception as e:
        print(f"  ⚠ Redis no disponible ({e}), usando caché en disco")
        return None


class ArticleCache:
    def __init__(self):
        self._lock   = threading.Lock()
        self._redis  = _conectar_redis()
        self._data   = self._cargar()
        self._dirty  = False

    # ── Carga / guardado ─────────────────────────────────────────────────────

    def _cargar(self) -> dict:
        data = None
        if self._redis:
            try:
                raw = self._redis.get(_REDIS_KEY)
                if raw:
                    data = json.loads(raw)
            except Exception as e:
                print(f"  ⚠ Error leyendo Redis: {e}")
        if data is None:
            try:
                if _CACHE_FILE.exists():
                    data = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        if data is None:
            data = {}
        data.setdefault("articulos",  {})
        data.setdefault("categorias", {})
        data.setdefault("sintesis",   {})
        return data

    def guardar(self) -> None:
        with self._lock:
            if not self._dirty:
                return
            self._data.setdefault("sintesis", {})
            blob = json.dumps(self._data, ensure_ascii=False)
            if self._redis:
                try:
                    self._redis.setex(_REDIS_KEY, _TTL_ARTICULO, blob)
                    self._dirty = False
                    return
                except Exception as e:
                    print(f"  ⚠ Error guardando en Redis: {e}, usando disco")
            _CACHE_FILE.write_text(blob, encoding="utf-8")
            self._dirty = False

    # ── Utilidades ───────────────────────────────────────────────────────────

    @staticmethod
    def _clave(texto: str) -> str:
        return hashlib.md5(texto.encode()).hexdigest()

    # ── Artículos individuales ───────────────────────────────────────────────

    def get_articulo(self, url: str) -> dict | None:
        clave = self._clave(url)
        with self._lock:
            entrada = self._data["articulos"].get(clave)
            if not entrada:
                return None
            if time.time() - entrada["ts"] > _TTL_ARTICULO:
                del self._data["articulos"][clave]
                self._dirty = True
                return None
            return entrada["v"]

    def set_articulo(self, url: str, analisis: dict) -> None:
        clave = self._clave(url)
        with self._lock:
            self._data["articulos"][clave] = {"v": analisis, "ts": time.time()}
            self._dirty = True

    # ── Análisis general por categoría ───────────────────────────────────────

    def get_analisis_general(self, categoria: str) -> str | None:
        with self._lock:
            entrada = self._data["categorias"].get(categoria)
            if not entrada:
                return None
            if time.time() - entrada["ts"] > _TTL_CATEGORIA:
                del self._data["categorias"][categoria]
                self._dirty = True
                return None
            return entrada["v"]

    def set_analisis_general(self, categoria: str, texto: str) -> None:
        with self._lock:
            self._data["categorias"][categoria] = {"v": texto, "ts": time.time()}
            self._dirty = True

    # ── Síntesis cruzada ─────────────────────────────────────────────────────

    def get_sintesis(self, clave: str) -> list | None:
        with self._lock:
            entrada = self._data["sintesis"].get(clave)
            if not entrada:
                return None
            if time.time() - entrada["ts"] > _TTL_SINTESIS:
                del self._data["sintesis"][clave]
                self._dirty = True
                return None
            return entrada["v"]

    def set_sintesis(self, clave: str, grupos: list) -> None:
        with self._lock:
            self._data["sintesis"][clave] = {"v": grupos, "ts": time.time()}
            self._dirty = True

    # ── Estadísticas ─────────────────────────────────────────────────────────

    def stats(self) -> dict:
        with self._lock:
            return {
                "articulos_cacheados":  len(self._data["articulos"]),
                "categorias_cacheadas": len(self._data["categorias"]),
                "sintesis_cacheadas":   len(self._data.get("sintesis", {})),
                "backend":              "redis" if self._redis else "disco",
            }

    # ── Redis directo (claves arbitrarias para uso externo) ──────────────────

    def _redis_set(self, key: str, value: str, ex: int | None = None) -> bool:
        if not self._redis:
            return False
        try:
            if ex:
                self._redis.setex(key, ex, value)
            else:
                self._redis.set(key, value)
            return True
        except Exception:
            return False

    def _redis_get(self, key: str) -> str | None:
        if not self._redis:
            return None
        try:
            return self._redis.get(key)
        except Exception:
            return None

    # ── Pool de artículos (últimos 3 días) ──────────────────────────────────

    def _pool_disco_path(self, categoria: str) -> Path:
        return Path(f"pool_{categoria.lower().replace(' ','_')}.json")

    def _pool_disco_get(self, categoria: str) -> list[dict]:
        p = self._pool_disco_path(categoria)
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            cutoff = time.time() - 72 * 3600
            return [a for a in data if a.get("_ts", 0) >= cutoff]
        except Exception:
            return []

    def _pool_disco_set(self, categoria: str, articulos: list[dict]) -> None:
        try:
            p = self._pool_disco_path(categoria)
            p.write_text(json.dumps(articulos, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def get_pool(self, categoria: str) -> list[dict]:
        """Devuelve artículos del pool de los últimos 3 días para esta categoría."""
        if self._redis:
            raw = self._redis_get(f"noticias:pool:{categoria}")
            if raw:
                try:
                    return json.loads(raw)
                except Exception:
                    pass
        return self._pool_disco_get(categoria)

    def update_pool(self, categoria: str, articulos: list[dict]) -> None:
        """Fusiona los artículos nuevos en el pool (dedup por enlace), TTL 72h."""
        pool = {a["enlace"]: a for a in self.get_pool(categoria)}
        ts = time.time()
        for a in articulos:
            if a.get("enlace"):
                pool[a["enlace"]] = {**a, "_ts": ts}
        merged = list(pool.values())
        if self._redis:
            self._redis_set(
                f"noticias:pool:{categoria}",
                json.dumps(merged, ensure_ascii=False),
                ex=72 * 3600,
            )
        else:
            self._pool_disco_set(categoria, merged)


# Singleton compartido: importar esto en lugar de crear instancias nuevas
shared = ArticleCache()
