# src/paragon_py/utils.py
import sys, json, ctypes, platform
from pathlib import Path
from typing import List, Tuple, Optional, Any
from importlib.resources import files

PKG_DIR = files("paragon_py")
_RTLD_GLOBAL = getattr(ctypes, "RTLD_GLOBAL", 0)

def _lib_path() -> Path:
    plat = sys.platform
    arch = platform.machine().lower()
    arch_key = {"x86_64":"amd64","amd64":"amd64","aarch64":"arm64","arm64":"arm64"}.get(arch, arch)
    if plat.startswith("linux"):
        p = PKG_DIR / f"linux_{arch_key}" / f"teleport_{arch_key}_linux.so"
    elif plat == "darwin":
        # prefer native slice; universal is a fallback if you ship it
        p = PKG_DIR / f"darwin_{arch_key}" / f"teleport_{arch_key}_darwin.dylib"
        if not p.is_file():
            p = PKG_DIR / "darwin_universal" / "teleport_universal_darwin.dylib"
    elif plat.startswith("win"):
        p = PKG_DIR / "windows_amd64" / "teleport_amd64_windows.dll"
    else:
        raise RuntimeError(f"Unsupported platform: {plat} ({arch})")
    if not Path(p).is_file():
        raise FileNotFoundError(f"Paragon native library not found at {p}")
    return Path(p)

_LIB = ctypes.CDLL(str(_lib_path()), mode=_RTLD_GLOBAL)

def _sym(name: str):
    try:
        return getattr(_LIB, name)
    except AttributeError:
        return None

def _steal(cptr) -> str:
    if not cptr:
        return ""
    return ctypes.cast(cptr, ctypes.c_char_p).value.decode("utf-8", errors="replace")

def _json(obj: Any) -> bytes:
    return json.dumps(obj).encode()

def _parse_handle(txt: str) -> Optional[int]:
    s = (txt or "").strip()
    if s.isdigit():
        return int(s)
    try:
        obj = json.loads(s)
    except json.JSONDecodeError:
        return None
    if isinstance(obj, dict):
        for k in ("handle","Handle","id","ID","network_handle","NetworkHandle"):
            v = obj.get(k)
            if isinstance(v, int):
                return int(v)
        res = obj.get("result")
        if isinstance(res, dict):
            for k in ("handle","Handle","id","ID"):
                v = res.get(k)
                if isinstance(v, int):
                    return int(v)
    return None

# ---- required symbols --------------------------------------------------------
CALL = _sym("Paragon_Call")
if not CALL:
    raise AttributeError("Paragon_Call not exported")
CALL.restype  = ctypes.c_char_p
CALL.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_char_p]

NEW = _sym("Paragon_NewNetworkFloat32")
if not NEW:
    raise AttributeError("Paragon_NewNetworkFloat32 not exported")
NEW.restype  = ctypes.c_char_p
NEW.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool, ctypes.c_bool]

FREE = _sym("Paragon_Free")
if FREE:
    FREE.argtypes = [ctypes.c_longlong]

# ---- tiny public API ---------------------------------------------------------

def get_phase_methods_json() -> str:
    h = new_network(shapes=[(1,1)], activations=["linear"], trainable=[True], use_gpu=False)
    raw = CALL(h, b"GetphaseMethodsJSON", b"[]")
    txt = _steal(raw)
    try:
        return json.dumps(json.loads(txt), indent=2)
    except json.JSONDecodeError:
        return txt

def new_network(*, shapes: List[Tuple[int,int]], activations: List[str], trainable: List[bool], use_gpu: bool) -> int:
    layers = [{"Width": w, "Height": h} for (w, h) in shapes]
    resp = _steal(NEW(_json(layers), _json(list(activations)), _json(list(trainable)), bool(use_gpu), False))
    h = _parse_handle(resp)
    if not h:
        raise RuntimeError(f"NewNetwork failed: {resp}")
    return h

def forward(handle: int, image_2d: List[List[float]]) -> None:
    _ = _steal(CALL(int(handle), b"Forward", _json([image_2d])))

def extract_output(handle: int) -> List[float]:
    txt = _steal(CALL(int(handle), b"ExtractOutput", b"[]"))

    def _coerce(seq):
        out = []
        for v in seq:
            if isinstance(v, (list, tuple)):
                out.extend(_coerce(v))
            else:
                out.append(float(v))
        return out

    def _parse_any(s: str):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            try:
                return json.loads(s.strip('"'))
            except json.JSONDecodeError:
                raise RuntimeError(f"Unexpected ExtractOutput response: {s!r}")

    obj = _parse_any(txt)
    if isinstance(obj, dict) and "result" in obj:
        obj = obj["result"]
    if isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
        try:
            obj = json.loads(obj[0])
        except json.JSONDecodeError:
            pass
    if isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], (list, tuple)):
        obj = obj[0]
    if not isinstance(obj, list):
        raise RuntimeError(f"ExtractOutput did not return a list: {type(obj)} — content: {obj!r}")
    return _coerce(obj)

def cleanup_gpu(handle: int) -> None:
    try:
        _ = _steal(CALL(int(handle), b"CleanupOptimizedGPU", b"[]"))
    except Exception:
        pass

# --- extras: explicit GPU init + training via CALL (thin wrappers) ------------

def initialize_gpu(handle: int) -> bool:
    """Best-effort GPU init; returns True if OK, else False (caller may still run CPU)."""
    txt = _steal(CALL(int(handle), b"InitializeOptimizedGPU", b"[]"))
    # if native returns JSON, accept either {"ok":true}, {"error":...}, or ""
    try:
        obj = json.loads(txt or "null")
        if isinstance(obj, dict):
            return bool(obj.get("ok", True)) and not obj.get("error")
    except json.JSONDecodeError:
        pass
    # empty / non-error string: assume success
    return True if (txt.strip() == "" or "fail" not in txt.lower()) else False

def train(handle: int,
          inputs: List[List[List[float]]],
          targets: List[List[List[float]]],
          epochs: int,
          lr: float,
          shuffle: bool = False,
          clip_max: float = 2.0,
          clip_min: float = -2.0) -> None:
    """
    Calls Paragon's Train: signature mirrors Go: Train(inputs, targets, epochs, lr, shuffle, clipMax, clipMin)
    """
    args = [inputs, targets, int(epochs), float(lr), bool(shuffle), float(clip_max), float(clip_min)]
    _ = _steal(CALL(int(handle), b"Train", _json(args)))

def eval_model(handle: int, expected: List[float], actual: List[float]) -> None:
    """Calls Paragon's EvaluateModel(expected, actual). Performance fields are internal on the C# side,
    so this is mainly for parity; we compute ADHD-style metrics in notebooks."""
    args = [list(expected), list(actual)]
    _ = _steal(CALL(int(handle), b"EvaluateModel", _json(args)))
