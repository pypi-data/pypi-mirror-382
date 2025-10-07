# metadata.py — versión 2025‑07‑30 (soporta YAML remotos)
# ==============================================================
#  ✦ Módulo unificado de metadatos con:
#    • update · printSchema · info · describe (con validate previo)
#    • validate · compare · export_schema · generate_expectations
#    • quality_report · transform · snapshot / load_snapshot / list_snapshots
#    • research (IA)
# --------------------------------------------------------------
import base64
import json
import os
import pathlib
import re
import tempfile
import copy
import unicodedata
import warnings
import zipfile
import urllib.request
import urllib.parse
import logging
from urllib.error import URLError
from difflib import get_close_matches
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

_DEFAULT_OPENAI_CALL_PARAMS: Dict[str, Any] = {
    "model": "gpt-4o-mini",
    "temperature": 0.1,
    "max_tokens": 800,
}

import numpy as np
import pandas as pd
import yaml
from pandas.api.types import CategoricalDtype

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

# ---------- dependencias opcionales ----------
try:
    import openai
except ImportError:                                 # se inicializa solo si hay key
    openai = None

try:
    from tdigest import TDigest
except ImportError:
    TDigest = None

try:
    from datasketch import HyperLogLog
except ImportError:
    HyperLogLog = None
# ---------------------------------------------


# ╔════════════════════════════════════════════╗
# ║ Helpers para fuentes locales y remotas     ║
# ╚════════════════════════════════════════════╝
def _is_url(src: Union[str, pathlib.Path]) -> bool:
    """Devuelve True si la ruta apunta a un recurso http(s)."""
    return isinstance(src, (str, pathlib.Path)) and str(src).lower().startswith(("http://", "https://"))


def _read_yaml(src: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """
    Lee un YAML desde disco o desde una URL y lo devuelve como dict.
    Lanza FileNotFoundError / URLError si el recurso no existe.
    """
    if _is_url(src):
        with urllib.request.urlopen(str(src)) as resp:
            data = resp.read().decode("utf-8")
        return yaml.safe_load(data)
    else:
        path = pathlib.Path(src)
        if not path.exists():
            raise FileNotFoundError(path)
        return yaml.safe_load(path.read_text(encoding="utf-8"))


def _read_json(src: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """Lee un JSON local o remoto y lo devuelve como dict."""
    if _is_url(src):
        with urllib.request.urlopen(str(src)) as resp:
            data = resp.read().decode("utf-8")
        return json.loads(data)
    else:
        path = pathlib.Path(src)
        if not path.exists():
            raise FileNotFoundError(path)
        return json.loads(path.read_text(encoding="utf-8"))


def _read_meta(src: Union[str, pathlib.Path]) -> Dict[str, Any]:
    """Lectura unificada de YAML o JSON."""
    lower = str(src).lower()
    if lower.endswith(".json"):
        return _read_json(src)
    return _read_yaml(src)


def _tdigest_b64(series: pd.Series) -> Optional[str]:
    if TDigest is None or not pd.api.types.is_numeric_dtype(series):
        return None
    t = TDigest()
    t.batch_update(series.dropna().astype(float))
    return base64.b64encode(json.dumps(t.to_dict()).encode()).decode()


def _hll(series: pd.Series, p: int = 14) -> Optional[int]:
    if HyperLogLog is None:
        return None
    hll = HyperLogLog(p=p)
    for x in series.dropna():
        hll.update(str(x).encode())
    return int(hll.count())


def _infer_logic(series: pd.Series) -> str:
    dtype = series.dtype

    if pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    if pd.api.types.is_integer_dtype(dtype):
        return "integer"
    if pd.api.types.is_float_dtype(dtype):
        return "float"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "datetime"
    if isinstance(dtype, CategoricalDtype):
        return "categorical"
    if series.map(lambda x: isinstance(x, str) or pd.isna(x)).all():
        return "text"
    return "string"


def _extract_openai_content(choice: Any) -> str:
    """Obtiene el contenido del primer mensaje sin importar la versión del SDK."""
    if choice is None:
        raise RuntimeError("Respuesta OpenAI sin contenido.")

    if isinstance(choice, dict):
        if "message" in choice and isinstance(choice["message"], dict):
            content = choice["message"].get("content")
            if content:
                return str(content).strip()
        if "text" in choice and choice["text"]:
            return str(choice["text"]).strip()

    message = getattr(choice, "message", None)
    if isinstance(message, dict):
        content = message.get("content")
        if content:
            return str(content).strip()
    if message is not None and hasattr(message, "content"):
        content = getattr(message, "content")
        if content:
            return str(content).strip()

    text = getattr(choice, "text", None)
    if text:
        return str(text).strip()

    raise RuntimeError("No se pudo extraer contenido de la respuesta de OpenAI.")


def _call_openai(
    prompt: str,
    *,
    api: Optional[Any] = None,
    api_key: Optional[str] = None,
    request_params: Optional[Dict[str, Any]] = None,
) -> str:
    """Encapsula la llamada, permitiendo inyectar un cliente OpenAI personalizado."""
    client = api or openai
    if client is None:
        raise RuntimeError("OpenAI API no disponible.")

    messages = [
        {"role": "system", "content": "You are a helpful data assistant."},
        {"role": "user", "content": prompt},
    ]
    kwargs: Dict[str, Any] = {**_DEFAULT_OPENAI_CALL_PARAMS, "messages": messages}

    if request_params:
        kwargs.update(request_params)
    kwargs.setdefault("messages", messages)

    chat_endpoint = getattr(getattr(client, "chat", None), "completions", None)
    chat_create = getattr(chat_endpoint, "create", None)
    if callable(chat_create):
        response = chat_create(**kwargs)
        choice = response.choices[0]
        return _extract_openai_content(choice)

    legacy_chat = getattr(client, "ChatCompletion", None)
    legacy_create = getattr(legacy_chat, "create", None)
    if callable(legacy_create):
        key = api_key or getattr(client, "api_key", None) or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OpenAI API no disponible.")
        try:
            setattr(client, "api_key", key)
        except Exception:
            pass
        response = legacy_create(**kwargs)
        if isinstance(response, dict):
            choice = response["choices"][0]
        else:
            choice = response.choices[0]
        return _extract_openai_content(choice)

    raise RuntimeError("Cliente OpenAI no soportado.")


# ╔════════════════════════════════════════════╗
# ║ ----------- PROCESADO DE BLOQUES --------- ║
# ╚════════════════════════════════════════════╝
def _process_meta_block(
    meta: Dict[str, Any],
    series: pd.Series,
    hll_p: int,
    verbose: bool,
) -> Dict[str, Any]:
    """
    Enriquecer un bloque de metadatos con:
      • statistics  → n_total, n_non_null, n_distinct, missing_ratio
      • numeric_summary o text_summary según el tipo
      • sketch      → tdigest_b64 + hll_cardinality
      • domain.numeric.min/max si faltan
    """
    inferred = _infer_logic(series)
    meta.setdefault("type", {})["logical_type"] = inferred

    # ---------- estadísticas básicas ----------
    stats = {
        "n_total": int(series.size),
        "n_non_null": int(series.notna().sum()),
        "n_distinct": int(series.nunique(dropna=True)),
        "missing_ratio": float(series.isna().mean()),
    }

    # ---------- métricas numéricas ----------
    if inferred in {"integer", "float"}:
        desc = series.describe(percentiles=[0.25, 0.50, 0.75, 0.95])
        stats["numeric_summary"] = {
            "count": int(desc["count"]),
            "mean": float(desc["mean"]),
            "std": float(desc["std"]),
            "min": float(desc["min"]),
            "p25": float(desc["25%"]),
            "p50": float(desc["50%"]),
            "p75": float(desc["75%"]),
            "p95": float(desc["95%"]),
            "max": float(desc["max"]),
        }
        dom = meta.setdefault("domain", {}).setdefault("numeric", {})
        dom.setdefault("min", float(desc["min"]))
        dom.setdefault("max", float(desc["max"]))

    # ---------- métricas de texto ----------
    elif inferred in {"text", "string"}:
        lengths = series.dropna().astype(str).str.len()
        stats["text_summary"] = {
            "avg_length": float(lengths.mean()),
            "max_length": int(lengths.max()),
        }

    # ---------- sketches ----------
    meta["statistics"] = stats
    meta["sketch"] = {
        "tdigest_b64": _tdigest_b64(series),
        "hll_cardinality": _hll(series, p=hll_p),
    }
    return meta


def _gather_blocks(unified_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Aplana schema → lista de bloques variable"""
    if "schema" in unified_meta:
        return unified_meta["schema"]
    return [unified_meta]


def _var_name(block: Dict[str, Any]) -> str:
    """Obtiene el nombre de la variable desde varios posibles campos."""
    try:
        return block["identity"]["variable_id"].split(":")[-1]
    except Exception:
        pass
    try:
        name = block.get("identity", {}).get("name")
        if isinstance(name, str) and name:
            return name
    except Exception:
        pass
    if isinstance(block.get("name"), str) and block.get("name"):
        return block["name"]
    lbl = block.get("identity", {}).get("label_i18n", {})
    if isinstance(lbl, dict) and lbl:
        return next(iter(lbl.values()))
    return "<unknown>"


# ---------- utils de coincidencia ----------
_UNIT_SUFFIX_RE = re.compile(r"_[a-z]{1,3}$")  # ej. _cm, _usd, _pct


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _normalize(s: str) -> str:
    s = _strip_accents(s.lower())
    s = _UNIT_SUFFIX_RE.sub("", s)
    return re.sub(r"[^a-z0-9]", "", s)


def _match_df_column(meta_name: str, df_cols: Sequence[str]) -> Optional[str]:
    """Devuelve el nombre real de la columna del DataFrame que mejor coincide con meta_name."""
    if meta_name in df_cols:
        return meta_name
    low_map = {c.lower(): c for c in df_cols}
    if meta_name.lower() in low_map:
        return low_map[meta_name.lower()]
    norm_map = {_normalize(c): c for c in df_cols}
    norm_name = _normalize(meta_name)
    if norm_name in norm_map:
        return norm_map[norm_name]
    cand = get_close_matches(norm_name, norm_map.keys(), n=1, cutoff=0.9)
    return norm_map[cand[0]] if cand else None


# ---------- YAML→DataFrame helpers ----------
def _flatten(d: Dict[str, Any], *, parent: str = "", sep: str = ".") -> Dict[str, Any]:
    out = {}
    for k, v in d.items():
        key = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            out.update(_flatten(v, parent=key, sep=sep))
        else:
            out[key] = v
    return out


def _to_frame(meta_dict: Dict[str, Dict[str, Any]], *, flat: bool = True, sep: str = ".") -> pd.DataFrame:
    recs = []
    for col, block in meta_dict.items():
        rec = _flatten(block, sep=sep) if flat else block.copy()
        # ``InsideForest.metadata.run_experiments`` espera la columna ``rule_token``
        # con el identificador de la regla original. Algunos flujos reutilizan
        # ``Metadata.df`` (el DataFrame generado por ``_to_frame``) para alimentar
        # dicho pipeline, por lo que añadimos esta llave explícita para mantener
        # compatibilidad con esa API externa.
        rec.setdefault("rule_token", col)
        rec["__column__"] = col
        recs.append(rec)
    return pd.DataFrame(recs).set_index("__column__")


def _unflatten(d: Dict[str, Any], *, sep: str = ".") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if k == "__column__" or (isinstance(v, float) and pd.isna(v)):
            continue
        current = out
        parts = k.split(sep)
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = v
    return out


def _from_frame(df: pd.DataFrame, *, sep: str = ".") -> Dict[str, Dict[str, Any]]:
    meta: Dict[str, Dict[str, Any]] = {}
    for col, row in df.iterrows():
        meta[col] = _unflatten(row.to_dict(), sep=sep)
    return meta


class Metadata:
    """Objeto principal para gestionar y validar metadatos.

    Parameters
    ----------
    cache_dir:
        Carpeta opcional donde se almacenan snapshots y cachés.
    loglevel:
        Nivel de logging para el objeto.
    openai_api:
        Cliente o API key a utilizar para las funciones asistidas por OpenAI. Puede
        ser una instancia del SDK oficial (`OpenAI` o módulo `openai`), una tupla
        ``(cliente, api_key)`` o directamente una cadena con la API key.
    openai_params:
        Diccionario con los parámetros por defecto que se enviarán al endpoint de
        chat de OpenAI (modelo, temperatura, etc.). Si es ``None`` se utilizan los
        valores por defecto del paquete.
    """

    def __init__(
        self,
        cache_dir: Optional[Union[str, pathlib.Path]] = None,
        *,
        loglevel: Union[str, int] = "INFO",
        openai_api: Optional[Any] = None,
        openai_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._df_cache: Optional[pd.DataFrame] = None
        self._df_prev: Optional[pd.DataFrame] = None
        self._history: Dict[str, Dict[str, Any]] = {}
        self._cache_dir = pathlib.Path(cache_dir) if cache_dir else None
        self._openai_api: Optional[Any] = None
        self._openai_api_key: Optional[str] = None
        self._openai_params: Dict[str, Any] = dict(_DEFAULT_OPENAI_CALL_PARAMS)
        self.logger = logger
        if isinstance(loglevel, str):
            loglevel = getattr(logging, loglevel.upper(), logging.INFO)
        self.logger.setLevel(loglevel)
        if self._cache_dir:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self._cache_dir / "df_cache.pkl"
            if cache_file.exists():
                try:
                    self._df_cache = pd.read_pickle(cache_file)
                    self._attach_upgrade()
                except Exception:
                    self._df_cache = None
        self.set_openai_api(openai_api)
        if openai_params is not None:
            self.set_openai_params(openai_params)

    def _attach_upgrade(self) -> None:
        if self._df_cache is None:
            return

        def upgrade(output: Optional[Union[str, pathlib.Path]] = None) -> None:
            self._meta = _from_frame(self._df_cache)
            if output:
                path = pathlib.Path(output)
                path.parent.mkdir(parents=True, exist_ok=True)
                data = {"schema": list(self._meta.values())}
                path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
            if self._cache_dir:
                try:
                    self._df_cache.to_pickle(self._cache_dir / "df_cache.pkl")
                except Exception:
                    pass

        def revert() -> None:
            if self._df_prev is None:
                return
            self._df_cache = self._df_prev.copy(deep=True)
            self._df_prev = None
            self._attach_upgrade()
            if self._cache_dir:
                try:
                    self._df_cache.to_pickle(self._cache_dir / "df_cache.pkl")
                except Exception:
                    pass

        setattr(self._df_cache, "upgrade", upgrade)
        setattr(self._df_cache, "revert", revert)

    def set_openai_api(self, openai_api: Optional[Any], *, api_key: Optional[str] = None) -> None:
        """Permite configurar el cliente de OpenAI o la API key a utilizar."""
        if isinstance(openai_api, tuple) and api_key is None:
            if len(openai_api) != 2:
                raise ValueError("Esperado tuple (cliente, api_key) para OpenAI.")
            openai_api, api_key = openai_api  # type: ignore[assignment]

        if isinstance(openai_api, str) and api_key is None:
            api_key = openai_api
            openai_api = openai

        if openai_api is None and api_key is not None:
            if openai is None:
                raise RuntimeError("El paquete openai no está instalado.")
            openai_api = openai

        self._openai_api = openai_api
        self._openai_api_key = api_key

    def set_openai_params(self, params: Optional[Dict[str, Any]], *, merge: bool = False) -> None:
        """Actualiza los parámetros por defecto para las llamadas a OpenAI."""
        if params is None:
            self._openai_params = dict(_DEFAULT_OPENAI_CALL_PARAMS)
            return

        if merge:
            merged = dict(self._openai_params)
            merged.update(params)
            self._openai_params = merged
        else:
            updated = dict(_DEFAULT_OPENAI_CALL_PARAMS)
            updated.update(params)
            self._openai_params = updated

    def _get_openai_client(self) -> Tuple[Any, Optional[str]]:
        client = self._openai_api if self._openai_api is not None else openai
        if client is None:
            raise RuntimeError("OpenAI API no disponible.")
        return client, self._openai_api_key

    def _prepare_openai_params(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = dict(self._openai_params)
        if overrides:
            params.update(overrides)
        return params

    # ------------------------------------------------------------------
    #                           UPDATE
    # ------------------------------------------------------------------
    def update(
        self,
        df: pd.DataFrame,
        meta_source: Union[str, pathlib.Path, Sequence[Union[str, pathlib.Path]]],
        *,
        inplace: bool = False,
        output: Optional[Union[str, pathlib.Path]] = None,
        overwrite: bool = True,
        hll_p: int = 14,
        verbose: bool = True,
    ) -> None:
        """
        Enriquecer YAML(s) con statistics/sketch y poblar self._meta.
        Acepta rutas locales o URLs http(s).
        """
        aggregated: Dict[str, Dict[str, Any]] = {}

        # -------- funciones internas (clausura) --------
        def _handle_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
            if "schema" in meta:
                new_schema = []
                for block in meta["schema"]:
                    col_yaml = _var_name(block)
                    col_df = _match_df_column(col_yaml, df.columns)
                    if col_df:
                        block = _process_meta_block(block, df[col_df], hll_p, verbose)
                    else:
                        if verbose:
                            self.logger.warning("[update] '%s' no tiene columna equivalente en el DataFrame.", col_yaml)
                    new_schema.append(block)
                    aggregated[col_yaml] = block
                meta["schema"] = new_schema
                return meta

            # esquema para bloque individual
            col_yaml = _var_name(meta)
            col_df = _match_df_column(col_yaml, df.columns)
            if col_df:
                meta = _process_meta_block(meta, df[col_df], hll_p, verbose)
            else:
                if verbose:
                    self.logger.warning("[update] Columna '%s' no encontrada en el DataFrame.", col_yaml)
            aggregated[col_yaml] = meta
            return meta

        def _save_meta(meta: Dict[str, Any], dest: pathlib.Path):
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and not overwrite:
                raise FileExistsError(dest)
            dest.write_text(yaml.safe_dump(meta, sort_keys=False, allow_unicode=True), encoding="utf-8")

        # -------- procesamiento principal --------
        if isinstance(meta_source, (str, pathlib.Path)) and str(meta_source).lower().endswith(".zip"):
            # ---------------- ZIP local o remoto ----------------
            src_zip = pathlib.Path(str(meta_source))
            tmp_path: Optional[pathlib.Path] = None

            if _is_url(meta_source):
                if inplace:
                    raise RuntimeError("No se puede sobrescribir un recurso HTTP; usa inplace=False.")
                if verbose:
                    self.logger.info("[update] Descargando %s...", meta_source)
                try:
                    with urllib.request.urlopen(str(meta_source)) as resp:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                            tmp.write(resp.read())
                            tmp_path = pathlib.Path(tmp.name)
                    src_zip = tmp_path
                except URLError as e:
                    raise RuntimeError(f"Error al descargar {meta_source}: {e.reason}") from e
            else:
                if not src_zip.exists():
                    raise FileNotFoundError(src_zip)

            updated: Dict[str, bytes] = {}
            with zipfile.ZipFile(src_zip, "r") as zin:
                for fname in zin.namelist():
                    lower = fname.lower()
                    if not lower.endswith((".yml", ".yaml", ".json")):
                        updated[fname] = zin.read(fname)
                        continue
                    data = zin.read(fname).decode()
                    if lower.endswith(".json"):
                        meta = json.loads(data)
                    else:
                        meta = yaml.safe_load(data)
                    meta = _handle_meta(meta)
                    updated[fname] = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).encode()

            if _is_url(meta_source):
                dst_zip = pathlib.Path(output or tempfile.gettempdir()) / src_zip.name
            else:
                dst_zip = src_zip if inplace else pathlib.Path(output or src_zip.with_name(src_zip.stem + "_updated.zip"))
            if dst_zip.exists() and not overwrite:
                raise FileExistsError(dst_zip)
            with zipfile.ZipFile(dst_zip, "w") as zout:
                for fname, data in updated.items():
                    zout.writestr(fname, data)
            if verbose:
                self.logger.info("✔ ZIP escrito en %s", dst_zip)
            if tmp_path is not None:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        else:
            files = [meta_source] if isinstance(meta_source, (str, pathlib.Path)) else meta_source
            for src in files:
                meta = _read_meta(src)
                meta = _handle_meta(meta)

                if _is_url(src):  # ---------- Fuente remota (solo lectura) ----------
                    if inplace:
                        raise RuntimeError("No se puede sobrescribir un recurso HTTP; usa inplace=False.")
                    fname = pathlib.Path(urllib.parse.urlparse(str(src)).path).name or "schema.yaml"
                    dest = pathlib.Path(output or tempfile.gettempdir()) / fname
                else:  # ---------- Fuente local ----------
                    path = pathlib.Path(src)
                    dest = path if inplace else pathlib.Path(output or path)

                _save_meta(meta, dest)
                if verbose:
                    self.logger.info("✔ %s actualizado", dest)

        # -------- snapshot interno + df cache --------
        self._meta = aggregated
        if self._df_cache is not None:
            self._df_prev = self._df_cache.copy(deep=True)
        self._df_cache = _to_frame(aggregated)
        self._attach_upgrade()
        if self._cache_dir:
            try:
                self._df_cache.to_pickle(self._cache_dir / "df_cache.pkl")
            except Exception:
                pass
        setattr(self, "_df_cache", self._df_cache)

    # ------------------------------------------------------------------
    #                  MÉTODOS AUXILIARES DE VISUALIZACIÓN
    # ------------------------------------------------------------------
    def _ensure_loaded(self) -> None:
        if not self._meta:
            raise RuntimeError("metadata.update() no se ha ejecutado aún.")

    @property
    def df(self) -> Optional[pd.DataFrame]:
        if self._df_cache is not None:
            if not hasattr(self._df_cache, "upgrade"):
                self._attach_upgrade()
            if self._df_prev is None:
                self._df_prev = self._df_cache.copy(deep=True)
        return self._df_cache

    def to_frame(self, *, flat: bool = True, sep: str = ".") -> pd.DataFrame:
        df = _to_frame(self._meta, flat=flat, sep=sep)
        if self._df_cache is not None:
            self._df_prev = self._df_cache.copy(deep=True)
        self._df_cache = df
        self._attach_upgrade()
        if self._cache_dir:
            try:
                self._df_cache.to_pickle(self._cache_dir / "df_cache.pkl")
            except Exception:
                pass
        return df

    def printSchema(self) -> None:
        self._ensure_loaded()
        self.logger.info("root")
        for col, block in self._meta.items():
            dtype = block["type"]["logical_type"]
            nullable = block.get("domain", {}).get("allowed_nulls_pct", 0) > 0
            self.logger.info(" |-- %s: %s (nullable = %s)", col, dtype, str(nullable).lower())

    def info(self) -> None:
        self._ensure_loaded()
        self.logger.info("<class 'metadata.dataset'>")
        self.logger.info("Columns: %d entries", len(self._meta))
        self.logger.info(" #   Column            Non-Null Count   Dtype")
        self.logger.info("---  ------            --------------   -----")
        dtype_counts: Dict[str, int] = {}
        for i, (col, block) in enumerate(self._meta.items()):
            stats = block.get("statistics", {})
            nn = stats.get("n_non_null", "‑‑")
            dtype = block["type"]["logical_type"]
            self.logger.info("%2d   %-18s %14s   %s", i, col, nn, dtype)
            dtype_counts[dtype] = dtype_counts.get(dtype, 0) + 1
        self.logger.info("dtypes: %s", ", ".join(f"{k}({v})" for k, v in dtype_counts.items()))

    # ------------------------------------------------------------------
    #                            VALIDATE
    # ------------------------------------------------------------------
    def validate(
        self,
        df: pd.DataFrame,
        *,
        detail: int = 0,
        capitalize: bool = False,
        message: bool = True,
    ) -> bool:

        self._ensure_loaded()
        passed = True
        yaml_cols = set(self._meta.keys())
        df_cols = set(df.columns)

        # --- autocorrección opcional de capitalización ---
        if capitalize:
            fixes = {y: d for y in yaml_cols for d in df_cols if y.lower() == d.lower() and y != d}
            for y, d in fixes.items():
                self._meta[d] = self._meta.pop(y)
                blk = self._meta[d]
                try:
                    blk["identity"]["variable_id"] = d
                except Exception:
                    pass
                if self._df_cache is not None and y in self._df_cache.index:
                    self._df_cache.rename(index={y: d}, inplace=True)
            if fixes and message:
                self.logger.info("[FIXED] Columnas actualizadas en YAML: %s", list(fixes.items()))
            yaml_cols = set(self._meta.keys())

        # ---------- checks originales ----------
        missing = yaml_cols - df_cols
        extra = df_cols - yaml_cols
        if missing or extra:
            passed = False
            if message:
                if missing:
                    self.logger.info("[MISSING] Columnas faltantes en DF: %s", sorted(missing))
                if extra:
                    self.logger.info("[EXTRA]   Columnas no esperadas en DF: %s", sorted(extra))

        common = yaml_cols & df_cols
        for col in common:
            series = df[col]
            block = self._meta[col]

            logic_real = _infer_logic(series)
            logic_yaml = block["type"]["logical_type"]
            if logic_real != logic_yaml:
                passed = False
                if message:
                    self.logger.info("[TYPE] %s: %s != %s", col, logic_real, logic_yaml)

            # --- detalle 1 ---
            if detail >= 1:
                dom = block.get("domain", {})
                if "numeric" in dom:
                    lo, hi = dom["numeric"].get("min"), dom["numeric"].get("max")
                    if lo is not None and series.min() < lo - 1e-9:
                        passed = False
                        if message:
                            self.logger.info("[RANGE] %s: min %s < %s", col, series.min(), lo)
                    if hi is not None and series.max() > hi + 1e-9:
                        passed = False
                        if message:
                            self.logger.info("[RANGE] %s: max %s > %s", col, series.max(), hi)
                if "categorical" in dom and dom["categorical"].get("closed"):
                    allowed = set(dom["categorical"].get("codes", [])) | set(
                        dom["categorical"].get("labels", {}).values()
                    )
                    invalid = series.dropna().loc[~series.dropna().isin(allowed)]
                    if not invalid.empty:
                        passed = False
                        if message:
                            sample = invalid.unique()[:5]
                            self.logger.info("[DOMAIN] %s: %d invalid -> %s", col, len(invalid), sample)
                if pattern := dom.get("pattern"):
                    bad = series.dropna().astype(str).loc[
                        ~series.dropna().astype(str).str.match(pattern)
                    ]
                    if not bad.empty:
                        passed = False
                        if message:
                            self.logger.info("[PATTERN] %s: %d no cumplen /%s/", col, len(bad), pattern)

            # --- detalle 2 ---
            if detail >= 2:
                allowed_null = block.get("domain", {}).get("allowed_nulls_pct", 0)
                mr = series.isna().mean()
                if mr > allowed_null + 1e-9:
                    passed = False
                    if message:
                        self.logger.info("[NULLS] %s: %.2f%% > %.2f%%", col, mr*100, allowed_null*100)
                if block.get("domain", {}).get("unique"):
                    dups = series.duplicated().sum()
                    if dups:
                        passed = False
                        if message:
                            self.logger.info("[UNIQUE] %s: %d duplicados", col, dups)
        return passed

    # ------------------------------------------------------------------
    #                           COMPARE
    # ------------------------------------------------------------------
    def compare(
        self,
        meta_a: Union[str, pathlib.Path],
        meta_b: Union[str, pathlib.Path],
        *,
        detail: int = 1,
        drift_threshold: float = 0.1,
        message: bool = True,
    ) -> bool:
        """Comparación de dos esquemas (o snapshot vs archivo)."""

        def _load_meta(source: Union[str, pathlib.Path]) -> Dict[str, Dict[str, Any]]:
            if isinstance(source, (str, pathlib.Path)) and str(source).lower().endswith(".yaml"):
                m = _read_yaml(source)
                blocks = _gather_blocks(m)
                return {_var_name(b): b for b in blocks}
            if source in self._history:
                return self._history[source]
            raise ValueError(f"No meta source found for {source}")

        a = _load_meta(meta_a)
        b = _load_meta(meta_b)
        passed = True

        if set(a) != set(b):
            missing = set(a).symmetric_difference(b)
            passed = False
            if message:
                self.logger.info("[COLUMNS] sets differ: %s", missing)

        for col in set(a) & set(b):
            if a[col]["type"]["logical_type"] != b[col]["type"]["logical_type"]:
                passed = False
                if message:
                    self.logger.info("[TYPE] %s: %s -> %s", col, a[col]['type']['logical_type'], b[col]['type']['logical_type'])
            if a[col]["type"].get("measurement_scale") != b[col]["type"].get("measurement_scale"):
                passed = False
                if message:
                    self.logger.info(
                        "[SCALE] %s: %s -> %s",
                        col,
                        a[col]['type'].get('measurement_scale'),
                        b[col]['type'].get('measurement_scale'),
                    )

        if detail >= 1:
            for col in set(a) & set(b):
                sa, sb = a[col]["statistics"], b[col]["statistics"]
                for k in ("missing_ratio",):
                    diff = abs(sa[k] - sb[k])
                    if diff > drift_threshold:
                        passed = False
                        if message:
                            self.logger.info("[DRIFT] %s.%s Δ=%.2f%%", col, k, diff*100)
                if "numeric_summary" in sa and "numeric_summary" in sb:
                    for p in ("p50", "p95"):
                        base = sa["numeric_summary"][p] or 1e-9
                        diff = abs(sb["numeric_summary"][p] - sa["numeric_summary"][p]) / abs(base)
                        if diff > drift_threshold:
                            passed = False
                            if message:
                                self.logger.info("[DRIFT] %s.%s Δ=%.2f%%", col, p, diff*100)
        return passed

    # ------------------------------------------------------------------
    #                    OTROS MÉTODOS (export, describe, ...)
    # ------------------------------------------------------------------
    # ... (los métodos export_schema, generate_expectations, quality_report,
    #      transform, snapshot, load_snapshot, list_snapshots, research,
    #      describe, show, filter permanecen idénticos al original y se
    #      omiten aquí por brevedad. Copia/pega tus versiones si tenías
    #      cambios locales).
    def export_schema(self,
                      target: str,
                      *,
                      dialect: Optional[str] = None,
                      style_hint: str = "",
                      **llm_kwargs) -> Any:
        self._ensure_loaded()
        if target.lower() == "spark" and dialect is None:
            from pyspark.sql.types import (StructField, StructType,
                                           StringType, IntegerType, FloatType,
                                           BooleanType, TimestampType)
            map_py = {
                "string": StringType(),
                "text": StringType(),
                "integer": IntegerType(),
                "float": FloatType(),
                "boolean": BooleanType(),
                "datetime": TimestampType(),
                "categorical": StringType(),
                "array": StringType()
            }
            fields = [StructField(col, map_py[b["type"]["logical_type"]], True)
                      for col, b in self._meta.items()]
            return StructType(fields)

        prompt = f"""You will receive a YAML schema. Convert it to a {target} artifact.
        Dialect: {dialect or 'generic'}. Style guide: {style_hint}. Return ONLY the artifact."""
        schema_yaml = yaml.safe_dump({"schema": list(self._meta.values())},
                                     sort_keys=False, allow_unicode=True)
        client, api_key = self._get_openai_client()
        overrides = dict(llm_kwargs)
        request_params = self._prepare_openai_params(overrides)
        return _call_openai(
            prompt + "\n\n---\n" + schema_yaml,
            api=client,
            api_key=api_key,
            request_params=request_params,
        )

    def generate_expectations(self,
                              framework: str = "great_expectations",
                              *,
                              descriptive: bool = True,
                              **llm_kwargs) -> str:
        self._ensure_loaded()
        prompt = f"""Convert the following YAML schema into a {framework} expectation suite.
        Include descriptions: {descriptive}. Return only the suite."""
        schema_yaml = yaml.safe_dump({"schema": list(self._meta.values())},
                                     sort_keys=False, allow_unicode=True)
        client, api_key = self._get_openai_client()
        overrides = dict(llm_kwargs)
        request_params = self._prepare_openai_params(overrides)
        return _call_openai(
            prompt + "\n\n---\n" + schema_yaml,
            api=client,
            api_key=api_key,
            request_params=request_params,
        )

    def quality_report(self,
                       df: Optional[pd.DataFrame] = None,
                       *,
                       baseline: Optional[str] = None,
                       weights: Optional[Dict[str, float]] = None,
                       message: bool = True) -> Dict[str, Any]:
        """Devuelve una puntuación de calidad según los datos validados."""
        self._ensure_loaded()
        weights = weights or {"completeness": .6, "drift": .4}

        if df is None:
            df = self._df_cache
            if df is None:
                self.logger.warning("[quality_report] No DataFrame en caché ni provisto.")

        df_val = df if df is not None else pd.DataFrame({})
        comp_pass = self.validate(df_val, detail=2, message=False)
        completeness = 1.0 if comp_pass else 0.5
        drift_score  = 1.0
        if baseline:
            drift_ok    = self.compare(baseline, "current", detail=1, message=False)
            drift_score = 1.0 if drift_ok else 0.5
        score = 100 * (weights["completeness"] * completeness +
                       weights["drift"] * drift_score)
        grade = ("A" if score >= 90 else
                 "B" if score >= 75 else
                 "C" if score >= 60 else
                 "D" if score >= 40 else "F")
        if message:
            self.logger.info("Quality score: %.1f (%s)", score, grade)
        return {"score": score, "grade": grade}

    def _coerce(self, series: pd.Series, logic: str):
        if logic == "integer":
            return pd.to_numeric(series, errors="coerce").astype("Int64")
        if logic == "float":
            return pd.to_numeric(series, errors="coerce")
        if logic == "boolean":
            return series.astype("boolean")
        if logic == "datetime":
            return pd.to_datetime(series, errors="coerce", utc=True)
        return series

    def transform(self,
                  df: pd.DataFrame,
                  *,
                  coerce_types: bool = True,
                  add_missing: bool = True,
                  drop_extra: bool = True,
                  fillna: Union[str, float, Dict[str, Any], None] = None) -> pd.DataFrame:
        """Devuelve un nuevo DataFrame ajustado al esquema."""
        self._ensure_loaded()
        df2 = df.copy()
        for col, block in self._meta.items():
            if col not in df2.columns:
                if add_missing:
                    df2[col] = np.nan
                else:
                    continue
            if coerce_types:
                df2[col] = self._coerce(df2[col], block["type"]["logical_type"])
            if fillna is not None:
                value = fillna.get(col) if isinstance(fillna, dict) else fillna
                if value is not None:
                    if isinstance(df2[col].dtype, CategoricalDtype):
                        if value not in df2[col].cat.categories:
                            df2[col] = df2[col].cat.add_categories([value])
                    df2[col] = df2[col].fillna(value)
        if drop_extra:
            extra = set(df2.columns) - set(self._meta.keys())
            df2 = df2.drop(columns=list(extra))
        return df2

    def snapshot(self, label: str) -> None:
        self._ensure_loaded()
        self._history[label] = copy.deepcopy(self._meta)

    def load_snapshot(self, label: str) -> None:
        if label not in self._history:
            raise KeyError(label)
        self._meta = copy.deepcopy(self._history[label])

    def list_snapshots(self) -> List[str]:
        return list(self._history.keys())

    def research(self,
                 df: pd.DataFrame,
                 *,
                 sample_rows: int = 500,
                 temperature: float = .2,
                 topics: Sequence[str] = ("correlations", "clusters", "anomalies"),
                 **llm_kwargs) -> Dict[str, Any]:
        self._ensure_loaded()
        samp = df.sample(n=min(sample_rows, len(df)), random_state=42)
        csv_preview = samp.to_csv(index=False, max_cols=15, line_terminator="\n")[:40_000]
        prompt = f"""You are a senior data scientist.
        Topics requested: {', '.join(topics)}.
        Analyse the following CSV sample (header in first row).
        Return JSON with keys exactly {list(topics)}."""
        client, api_key = self._get_openai_client()
        overrides = dict(llm_kwargs)
        overrides.setdefault("temperature", temperature)
        overrides.setdefault("max_tokens", 1200)
        request_params = self._prepare_openai_params(overrides)
        analysis = _call_openai(
            prompt + "\n\n" + csv_preview,
            api=client,
            api_key=api_key,
            request_params=request_params,
        )
        try:
            return json.loads(analysis)
        except json.JSONDecodeError:
            return {"raw": analysis}


    def describe(self,
                 df: Optional[pd.DataFrame] = None,
                 *,
                 require_valid: bool = False,
                 detail: int = 0,
                 message: bool = False) -> Optional[pd.DataFrame]:
        self._ensure_loaded()
        if df is not None and require_valid and not self.validate(df, detail=detail, message=message):
            if message:
                self.logger.info("❌  describe() abortado: metadata.validate() no pasó.")
            return None

        metrics  = ["count", "mean", "std", "min", "p25", "p50", "p75", "p95", "max"]
        rows     = {m: [] for m in metrics}
        headers  = []

        for col, block in self._meta.items():
            ns = block.get("statistics", {}).get("numeric_summary")
            if ns:
                headers.append(col)
                for m in metrics:
                    rows[m].append(ns.get(m, np.nan))

        if not headers:
            if message:
                self.logger.info("No numeric_summary stored in YAML; run metadata.update() primero.")
            return None

        df_desc = (pd.DataFrame.from_dict(rows, orient="index", columns=headers)
                            .astype(float)
                            .round(3))
        if message:
            self.logger.info("%s", df_desc)
        return df_desc


    def show(self,
             column: Optional[str] = None,
             *,
             fields: Sequence[str] = ("identity.label_i18n",
                                      "type.logical_type",
                                      "domain",
                                      "statistics")) -> None:
        self._ensure_loaded()

        def _extract(d: Dict[str, Any], path: str):
            for part in path.split("."):
                d = d.get(part, {})
            return d

        cols = [column] if column else self._meta.keys()
        for col in cols:
            block = self._meta[col]
            self.logger.info("\u2500\u2500 %s", col)
            for f in fields:
                self.logger.info("  %s: %s", f, _extract(block, f))
            self.logger.info("")

    def filter(self,
               *,
               logical_type: Optional[Union[str, Sequence[str]]] = None,
               tag: Optional[str] = None,
               name_regex: Optional[str] = None,
               has_domain: bool = False) -> pd.DataFrame:
        """Devuelve un DataFrame resumen de columnas que cumplan criterios."""
        self._ensure_loaded()
        ltypes = {logical_type} if isinstance(logical_type, str) else set(logical_type or [])
        rows: List[Dict[str, Any]] = []
        for col, block in self._meta.items():
            if ltypes and block["type"]["logical_type"] not in ltypes:
                continue
            if tag and tag not in block["identity"].get("tags", []):
                continue
            if name_regex and not re.search(name_regex, col):
                continue
            if has_domain and not block.get("domain"):
                continue
            rows.append({
                "column":       col,
                "logical_type": block["type"]["logical_type"],
                "description":  block["identity"]["description_i18n"].get("es")
                                  or block["identity"]["description_i18n"].get("en", ""),
                "tags":         ", ".join(block["identity"].get("tags", []))
            })
        return pd.DataFrame(rows)


__all__ = ["Metadata"]
