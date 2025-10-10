import gzip
import hashlib
import io
import os
from urllib.parse import quote, urlparse, urlunparse
import zstandard as zstd
import lz4.frame as lz4
import zlib
import magic
from HoyoSophonDL.structs.Assets import FileHashes
from loguru import logger as logger

def format_bytes(size: int, decimals: int = 2) -> str:
    """Convert bytes into human-readable format (KB, MB, GB...)."""
    size = int(size)
    if size == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    power = 1024
    i = 0
    while size >= power and i < len(units) - 1:
        size /= power
        i += 1
    
    return f"{size:.{decimals}f} {units[i]}"

def fix_url(url: str, default_scheme="https") -> str:
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = urlparse(f"{default_scheme}://{url}")
    path = quote(parsed.path.rstrip('/'), safe="/")
    query = quote(parsed.query, safe="=&?")
    fragment = quote(parsed.fragment, safe="")
    fixed = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, query, fragment))
    return fixed

def decompress(_in, _out=None):
    """
    Detect and decompress Sophon manifest/patch data.
    Falls back to original data if format not recognised.
    """

    data = _in if isinstance(_in, bytes) else _in.read()
    mime = magic.from_buffer(data, mime=True)
    desc = magic.from_buffer(data)
    logger.debug(f"Detected compression: desc={desc}, mime={mime}")

    bytes_ = data
    try:
        if "zstandard" in desc.lower() or "x-zstd" in mime:
            logger.debug("Attempting Zstandard decompression.")
            try:
                bytes_ = zstd.ZstdDecompressor().decompress(data)
            except zstd.ZstdError as e:
                logger.warning(f"Standard decompression failed ({e}), retrying stream mode.")
                dctx = zstd.ZstdDecompressor()
                with dctx.stream_reader(io.BytesIO(data)) as reader:
                    bytes_ = reader.read()
        elif "lz4" in desc.lower():
            logger.debug("Attempting LZ4 decompression.")
            bytes_ = lz4.decompress(data)
        elif "gzip" in desc.lower():
            logger.debug("Attempting GZIP decompression.")
            bytes_ = gzip.decompress(data)
        elif "zlib" in desc.lower() or mime == "application/zlib":
            logger.debug("Attempting ZLIB decompression.")
            bytes_ = zlib.decompress(data)
        else:
            logger.info("Unknown compression type; returning original data.")
    except Exception as e:
        logger.error(f"Decompression failed: {e}")
        bytes_ = data   # fall back to original

    if _out:
        _out.write(bytes_)
        _out.flush()
        _out.close()
        return True
    return bytes_

def get_file_hashs(identity:str,file_path: str|bytes) -> FileHashes:
    BUF_SIZE = 2 * 1024 * 1024
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()

    if isinstance(file_path,bytes):
        chunk = file_path
        md5.update(chunk)
        sha1.update(chunk)
        sha256.update(chunk)
        _size = len(chunk)
    else:
        file_path = str(file_path)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(BUF_SIZE), b""):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)
        _size = os.path.getsize(file_path)
    return FileHashes(
        identity=identity,
        md5=md5.hexdigest(),
        sha1=sha1.hexdigest(),
        sha256=sha256.hexdigest(),
        size=_size
    )

def get_md5_hash(file_path:str|bytes) -> str:
    BUF_SIZE = 2 * 1024 * 1024
    md5 = hashlib.md5()

    if isinstance(file_path,bytes):
        chunk = file_path
        md5.update(chunk)
    else:
        file_path = str(file_path)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(BUF_SIZE), b""):
                md5.update(chunk)
    return md5.hexdigest()


def set_row_hashs(_row):
    identity,md5,sha1,sha256,size = _row
    return FileHashes(
        identity=identity,
        md5=md5,
        sha1=sha1,
        sha256=sha256,
        size=size
    )
