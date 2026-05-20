"""
article_cache.py — Caché persistente de análisis de artículos.

Evita re-enviar a Claude artículos ya analizados, reduciendo tokens consumidos
en ciclos donde la mayoría de noticias ya fueron procesadas.

- Artículos: TTL de 24 horas (la noticia no cambia, su análisis tampoco)
- Análisis general por categoría: TTL de 6 horas (refleja el ciclo de regeneración)
- Persistido en article_cache.json (sobrevive reinicios del scheduler, no del servidor)
"""

import json
import time
import hashlib
import threading
from pathlib import Path

_CACHE_FILE    = Path("article_cache.json")
_TTL_ARTICULO  = 24 * 3600   # 24 horas
_TTL_CATEGORIA =  6 * 3600   #  6 horas


class ArticleCache:
    def __init__(self):
        self._lock  = threading.Lock()
        self._data  = self._cargar()
        self._dirty = False

    def _cargar(self) -> dict:
        try:
            if _CACHE_FILE.exists():
                return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {"articulos": {}, "categorias": {}}

    @staticmethod
    def _clave(url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    # ── Artículos ────────────────────────────────────────────────────────

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

    # ── Análisis general por categoría ───────────────────────────────────

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

    # ── Persistencia ─────────────────────────────────────────────────────

    def guardar(self) -> None:
        with self._lock:
            if not self._dirty:
                return
            _CACHE_FILE.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self._dirty = False

    def stats(self) -> dict:
        with self._lock:
            return {
                "articulos_cacheados": len(self._data["articulos"]),
                "categorias_cacheadas": len(self._data["categorias"]),
            }
