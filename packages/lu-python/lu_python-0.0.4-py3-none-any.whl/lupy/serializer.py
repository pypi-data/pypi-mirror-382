from typing import Any


def default_serialize(obj: Any):
    """Return a JSON-serializable representation for obj.
    This attempts common containers and simple objects. For arbitrary
    objects we fallback to a stable-ish representation:
      - if object has a .__getstate__ or .__dict__, use that
      - otherwise use repr(obj) (may include addresses -> not stable across runs)
    Prefer passing a custom self_key for instances you care about.
    """
    # Primitives
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # bytes -> base64-like deterministic repr
    if isinstance(obj, (bytes, bytearray)):
        # hex is deterministic and portable
        return {"__bytes_hex__": obj.hex()}

    # containers
    if isinstance(obj, (list, tuple)):
        return [ default_serialize(x) for x in obj ]
    if isinstance(obj, (set, frozenset)):
        # sort serialized items to make deterministic
        return {"__set__": sorted(default_serialize(x) for x in obj)}
    if isinstance(obj, dict):
        # keys should be strings for json; convert and sort when dumping
        return { str(k): default_serialize(v) for k, v in obj.items() }

    # dataclass-like or objects with state
    if hasattr(obj, "__getstate__"):
        return {"__class__": f"{obj.__class__.__module__}.{obj.__class__.__qualname__}",
                "__state__": default_serialize(obj.__getstate__())}
    if hasattr(obj, "__dict__"):
        # Capture the class identity and the sorted dict of attributes
        return {"__class__": f"{obj.__class__.__module__}.{obj.__class__.__qualname__}",
                "__dict__": default_serialize(obj.__dict__)}

    # Fallback: repr (may contain addresses -> not stable across runs)
    return {"__repr__": repr(obj)}
