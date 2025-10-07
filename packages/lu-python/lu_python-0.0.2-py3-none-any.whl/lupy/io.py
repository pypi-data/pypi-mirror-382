import gzip
import pickle

# Prefer zstandard if available for better compression/speed; fall back to gzip
try:
    import zstandard as zstd  # type: ignore
    _COMPRESSOR = "zstd"
except Exception:
    zstd = None
    _COMPRESSOR = "gzip"


def _write_compressed_pickle(obj, path):
    if _COMPRESSOR == "zstd":
        b = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        cctx = zstd.ZstdCompressor(level=3)
        with open(path, "wb") as f:
            f.write(cctx.compress(b))
    else:
        # gzip fallback
        with gzip.open(path, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def _read_compressed_pickle(path):
    if _COMPRESSOR == "zstd":
        dctx = zstd.ZstdDecompressor()
        with open(path, "rb") as f:
            data = f.read()
        return pickle.loads(dctx.decompress(data))
    else:
        with gzip.open(path, "rb") as f:
            return pickle.load(f)
