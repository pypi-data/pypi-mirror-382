import lupy
from tests.fixtures import Foo
import os
import pytest


def test_sync_method():
    # Use a module-qualified target so record() can import and replace it.
    with lupy.record(
        targets={
            'tests.fixtures.Foo.expensive_method': None
        },
        recordings_dir='tests/fixtures/recordings/',
    ):
        foo = Foo()

        # On first call there is no recording, so the original is invoked
        # and a compressed file is written; call_count should increase to 1.
        return_value1 = foo.expensive_method()
        assert return_value1 is True
        assert foo.call_count == 1

        # assert compressed file is generated
        recording_files = os.listdir('tests/fixtures/recordings/')
        assert len(recording_files) == 1
        assert recording_files[0].endswith('.zst') or recording_files[0].endswith('.pkl.gz')

        # Calling again should read from the recording and not call original.
        return_value2 = foo.expensive_method()
        assert return_value2 is True
        assert foo.call_count == 1


@pytest.mark.asyncio
async def test_async_method():
    from tests.fixtures import Bar

    with lupy.record(
        targets={
            'tests.fixtures.Bar.expensive_method': ['x', 'y']
        },
        recordings_dir='tests/fixtures/recordings/',
    ):
        bar = Bar()

        # First call: executes original async method and writes recording
        r1 = await bar.expensive_method(5, y=2)
        assert r1 == 7
        assert bar.call_count == 1

        # Second call: reads from recording; call_count should not increase
        r2 = await bar.expensive_method(5, y=2)
        assert r2 == 7
        assert bar.call_count == 1


@pytest.mark.asyncio
async def test_async_exception_saved():
    from tests.fixtures import Baz

    # ensure recordings dir cleaned from previous tests
    recordings_dir = 'tests/fixtures/recordings/'

    with lupy.record(
        targets={
            'tests.fixtures.Baz.expensive_method': ['x', 'y']
        },
        recordings_dir=recordings_dir,
    ):
        baz = Baz()

        # First call should raise and write the exception to disk
        with pytest.raises(ValueError):
            await baz.expensive_method(1, y=2)

        # call_count incremented on real invocation
        assert baz.call_count == 1

        # Subsequent call should read the exception from the recording and re-raise
        with pytest.raises(ValueError):
            await baz.expensive_method(1, y=2)

        # call_count should NOT have increased because the original should not be invoked
        assert baz.call_count == 1


@pytest.mark.asyncio
async def test_module_method():
    from tests import fixtures

    with lupy.record(
        targets={
            'tests.fixtures.module_level_function': ['p']
        },
        recordings_dir='tests/fixtures/recordings/',
    ):
        # First call: executes original function and writes recording
        r1 = fixtures.module_level_function({'a': 1})
        assert r1 is True
        assert fixtures.module_counter == 1

        # Second call: reads from recording; call_count should not increase
        r2 = fixtures.module_level_function({'a': 1})
        assert r2 is True
        assert fixtures.module_counter == 1
