import json
import inspect
import hashlib
from typing import Any, Optional, Tuple, Dict, Callable, List
from .serializer import default_serialize


def method_args(func: Callable) -> Tuple[List[str], bool]:
    """Return parameter names for a callable and whether it expects 'self'.

    Returns (param_names, has_self) where param_names excludes 'self' when
    present. This lets callers handle both bound/unbound methods and
    module-level functions uniformly.
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    has_self = len(params) > 0 and params[0] == 'self'
    if has_self:
        return params[1:], True
    return params, False


def make_deterministic_dict(
    func_identifier: str,
    self_dict: Dict[str, Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> dict:
    """
    Returns a deterministic dict for (self_dict, args, kwargs).
    """
    # Canonicalize self
    self_part = default_serialize(self_dict)
    # Serialize args and kwargs deterministically
    args_part = default_serialize(list(args))
    # Ensure kwargs are represented with sorted keys
    kwargs_part = default_serialize({k: kwargs[k] for k in sorted(kwargs.keys())})

    return {
        "fn": func_identifier,
        "self": self_part,
        "args": args_part,
        "kwargs": kwargs_part,
    }


def make_deterministic_id(*args, short_hex_length: Optional[int] = None, **kwargs) -> str:
    """
    Returns a deterministic hex id for (self_dict, args, kwargs).

    Parameters
    - short_hex_length: if provided, the returned hex digest is truncated to
      this many hex characters. Truncating reduces collision resistance in
      exchange for shorter identifiers. If None (default), a full sha256
      hex digest is returned (64 hex characters).
    """
    # Extract optional param from kwargs if passed positionally via kwargs
    payload = make_deterministic_dict(*args, **kwargs)

    # Canonical JSON: sorted keys and compact separators -> deterministic bytes
    json_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    # Hash to produce fixed-length identifier (sha256 by default)
    h = hashlib.sha256(json_bytes).hexdigest()

    if short_hex_length is not None:
        if short_hex_length <= 0:
            raise ValueError("short_hex_length must be > 0")
        return h[:short_hex_length]

    return h
