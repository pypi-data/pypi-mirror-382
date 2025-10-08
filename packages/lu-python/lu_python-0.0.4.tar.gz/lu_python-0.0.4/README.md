# lupy

Lightweight recorder/fixture helper (formerly `mcr`).

This package provides a small context-manager `record()` which can patch
module-qualified functions or instance methods to record return values (or
exceptions) to compressed pickle files and write a `manifest.json` of the
recordings.

Usage example:

```py
import lupy
with lupy.record({ 'tests.fixtures.Foo.expensive_method': None }, recordings_dir='tests/fixtures/recordings/'):
    foo = Foo()
    foo.expensive_method()
```

See tests in `tests/test_lupy.py` for more examples.
