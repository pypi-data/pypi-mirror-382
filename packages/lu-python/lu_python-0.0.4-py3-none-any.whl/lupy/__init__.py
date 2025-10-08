import os
import json
import importlib
import functools
import inspect
from typing import Dict, Any, Optional
from .id import make_deterministic_id, make_deterministic_dict, method_args
from .io import _write_compressed_pickle, _read_compressed_pickle, _COMPRESSOR


# Package version
__version__ = "0.0.4"


class Recorder:
    """Context manager that installs recording wrappers and writes a manifest
    at exit.

    Usage:
        with record(targets, recordings_dir):
            ... run tests ...

    `targets` should be a dict mapping dotted target -> list_of_keys
    (same as previous API).
    """

    def __init__(self, targets: Dict[str, Any], recordings_dir: str, manifest_file: Optional[str] = None, short_hex_length: Optional[int] = None):
        self.targets = targets
        self.recordings_dir = recordings_dir
        self.manifest_file = manifest_file or os.path.join(recordings_dir, "recordings.json")
        self._originals = []  # list of tuples (parent, func_name, original_obj)
        self._manifest_entries = {}
        self.short_hex_length = short_hex_length

    def __enter__(self):
        os.makedirs(self.recordings_dir, exist_ok=True)

        for target, keys in self.targets.items():
            parts = target.split('.')

            # Find the longest importable module prefix.
            module = None
            importable_index = 0
            for i in range(len(parts), 0, -1):
                module_path = '.'.join(parts[:i])
                try:
                    module = importlib.import_module(module_path)
                    importable_index = i
                    break
                except ModuleNotFoundError:
                    continue

            if module is None:
                raise ImportError(f"Could not import any prefix of target '{target}'")

            # Traverse remaining attribute names to reach the parent of the final attribute.
            parent = module
            for name in parts[importable_index:-1]:
                parent = getattr(parent, name)

            func_name = parts[-1]
            original_func_obj = getattr(parent, func_name)

            # Save original so we can restore on exit
            self._originals.append((parent, func_name, original_func_obj))

            # extract positional arg names and whether callable expects 'self'
            args_names, expects_self = method_args(original_func_obj)
            
            # create and install wrapper; bind variables into defaults to avoid late-binding
            def make_wrapper(__original=original_func_obj, _target=target, _keys=keys, _args_names=args_names, _expects_self=expects_self):
                # Create a wrapper that matches the original function's sync/async nature.
                if inspect.iscoroutinefunction(__original):
                    @functools.wraps(__original)
                    async def wrapper(*w_args, **kwargs):
                        # Determine if this is a method (expects self) or a plain function
                        if _expects_self:
                            obj, *call_args = w_args
                            key_self = {k: v for k, v in obj.__dict__.items() if k in (_keys or [])}
                        else:
                            call_args = list(w_args)
                            key_self = {}

                        key_args = [arg for name, arg in zip(_args_names, call_args) if name in (_keys or [])]
                        key_kwargs = {k: v for k, v in kwargs.items() if k in (_keys or [])}

                        # deterministic id and payload
                        entry_payload = make_deterministic_dict(_target, key_self, key_args, key_kwargs)
                        entry_id = make_deterministic_id(_target, key_self, key_args, key_kwargs, short_hex_length=self.short_hex_length)
                        # choose extension based on available compressor
                        ext = ".zst" if _COMPRESSOR == "zstd" else ".pkl.gz"
                        recording_file = os.path.join(self.recordings_dir, f"{entry_id}{ext}")

                        if os.path.exists(recording_file):
                            loaded = _read_compressed_pickle(recording_file)
                            # If the recording was an exception, re-raise it
                            if isinstance(loaded, Exception):
                                action = "read_exception"
                                manifest_entry = {
                                    "target": _target,
                                    "self": entry_payload.get("self"),
                                    "args": entry_payload.get("args"),
                                    "kwargs": entry_payload.get("kwargs"),
                                    "file": recording_file,
                                    "format": "compressed_pickle",
                                    "compressor": _COMPRESSOR,
                                    "action": action,
                                    "exception": True,
                                }
                                self._manifest_entries[entry_id] = manifest_entry
                                raise loaded
                            else:
                                result = loaded
                                action = "read"
                        else:
                            try:
                                if _expects_self:
                                    result = await __original(obj, *call_args, **kwargs)
                                else:
                                    result = await __original(*call_args, **kwargs)
                                _write_compressed_pickle(result, recording_file)
                                action = "write"
                            except Exception as exc:
                                # Persist the exception so future runs can replay it
                                _write_compressed_pickle(exc, recording_file)
                                action = "write_exception"
                                manifest_entry = {
                                    "target": _target,
                                    "self": entry_payload.get("self"),
                                    "args": entry_payload.get("args"),
                                    "kwargs": entry_payload.get("kwargs"),
                                    "file": recording_file,
                                    "format": "compressed_pickle",
                                    "compressor": _COMPRESSOR,
                                    "action": action,
                                    "exception": True,
                                }
                                self._manifest_entries[entry_id] = manifest_entry
                                raise

                        # record manifest entry (write/read) with the payload and file path
                        manifest_entry = {
                            "target": _target,
                            "self": entry_payload.get("self"),
                            "args": entry_payload.get("args"),
                            "kwargs": entry_payload.get("kwargs"),
                            "file": recording_file,
                            "format": "compressed_pickle",
                            "compressor": _COMPRESSOR,
                            "action": action,
                        }
                        self._manifest_entries[entry_id] = manifest_entry

                        return result

                    return wrapper
                else:
                    @functools.wraps(__original)
                    def wrapper(*w_args, **kwargs):
                        # Determine if this is a method (expects self) or a plain function
                        if _expects_self:
                            obj, *call_args = w_args
                            key_self = {k: v for k, v in obj.__dict__.items() if k in (_keys or [])}
                        else:
                            call_args = list(w_args)
                            key_self = {}

                        key_args = [arg for name, arg in zip(_args_names, call_args) if name in (_keys or [])]
                        key_kwargs = {k: v for k, v in kwargs.items() if k in (_keys or [])}

                        # deterministic id and payload
                        entry_payload = make_deterministic_dict(_target, key_self, key_args, key_kwargs)
                        entry_id = make_deterministic_id(_target, key_self, key_args, key_kwargs, short_hex_length=self.short_hex_length)
                        # choose extension based on available compressor
                        ext = ".zst" if _COMPRESSOR == "zstd" else ".pkl.gz"
                        recording_file = os.path.join(self.recordings_dir, f"{entry_id}{ext}")

                        if os.path.exists(recording_file):
                            loaded = _read_compressed_pickle(recording_file)
                            if isinstance(loaded, Exception):
                                action = "read_exception"
                                manifest_entry = {
                                    "target": _target,
                                    "self": entry_payload.get("self"),
                                    "args": entry_payload.get("args"),
                                    "kwargs": entry_payload.get("kwargs"),
                                    "file": recording_file,
                                    "format": "compressed_pickle",
                                    "compressor": _COMPRESSOR,
                                    "action": action,
                                    "exception": True,
                                }
                                self._manifest_entries[entry_id] = manifest_entry
                                raise loaded
                            else:
                                result = loaded
                                action = "read"
                        else:
                            try:
                                if _expects_self:
                                    result = __original(obj, *call_args, **kwargs)
                                else:
                                    result = __original(*call_args, **kwargs)
                                _write_compressed_pickle(result, recording_file)
                                action = "write"
                            except Exception as exc:
                                _write_compressed_pickle(exc, recording_file)
                                action = "write_exception"
                                manifest_entry = {
                                    "target": _target,
                                    "self": entry_payload.get("self"),
                                    "args": entry_payload.get("args"),
                                    "kwargs": entry_payload.get("kwargs"),
                                    "file": recording_file,
                                    "format": "compressed_pickle",
                                    "compressor": _COMPRESSOR,
                                    "action": action,
                                    "exception": True,
                                }
                                self._manifest_entries[entry_id] = manifest_entry
                                raise

                        # record manifest entry (write/read) with the payload and file path
                        manifest_entry = {
                            "target": _target,
                            "self": entry_payload.get("self"),
                            "args": entry_payload.get("args"),
                            "kwargs": entry_payload.get("kwargs"),
                            "file": recording_file,
                            "format": "compressed_pickle",
                            "compressor": _COMPRESSOR,
                            "action": action,
                        }
                        self._manifest_entries[entry_id] = manifest_entry

                        return result

                    return wrapper

            wrapper = make_wrapper()
            setattr(parent, func_name, wrapper)

        return self

    def __exit__(self, exc_type, exc, tb):
        # restore originals
        for parent, func_name, original in self._originals:
            setattr(parent, func_name, original)

        # ensure recordings dir exists
        os.makedirs(self.recordings_dir, exist_ok=True)

        # write manifest file
        try:
            # Load existing manifest (if any) and merge entries, then write back.
            existing = {}
            if os.path.exists(self.manifest_file):
                try:
                    with open(self.manifest_file, 'r', encoding='utf-8') as mf:
                        loaded = json.load(mf)
                        if isinstance(loaded, dict):
                            existing = loaded
                except Exception:
                    # If the existing file is unreadable or malformed, ignore and overwrite
                    existing = {}

            # Update existing with current session entries (current entries take precedence)
            existing.update(self._manifest_entries)

            with open(self.manifest_file, 'w', encoding='utf-8') as mf:
                json.dump(existing, mf, indent=2, sort_keys=True, ensure_ascii=False)
        except Exception:
            # don't raise in __exit__; let test framework handle other exceptions
            pass


def record(targets: Dict[str, Any], recordings_dir: str, manifest_file: Optional[str] = None, short_hex_length: int = 6) -> Recorder:
    """Factory for creating a Recorder context manager.

    Use as:
        with record(targets, recordings_dir):
            ...
    """
    return Recorder(targets, recordings_dir, manifest_file, short_hex_length)
