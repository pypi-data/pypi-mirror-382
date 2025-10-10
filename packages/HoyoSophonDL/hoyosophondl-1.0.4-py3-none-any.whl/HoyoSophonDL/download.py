import sqlite3
import time
import requests
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from HoyoSophonDL.help import (
    decompress,
    get_file_hashs,
    get_md5_hash,
    set_row_hashs,
    logger,
)
from HoyoSophonDL.structs.SophonManifest import (
    SophonManifestProtoAsset,
    SophonManifestProtoAssets,
    SophonManifestProtoChunkAsset,
)

# ────────────────────────────────────────────────
# Exceptions / Global state
# ────────────────────────────────────────────────
class DownloadCancelled(Exception):
    """Raised when a download is cancelled by user."""

class GlobalDownloadData:
    def __init__(self):
        self.TotalSize = 0
        self.TotalFSize = ""
        self.TotalAssetsCount = 0
        self.TotalChunksCount = 0
        self.current_chunk = None
        self.current_asset = None
        self.TotalDownloadBytes = 0
        self.ExistFiles = 0
        self.NotExistFiles = 0
        self.stop_error = False
        self.stop_error_msg = ""
        self.CompletedChunks = 0
        self.Errors = 0
        self.CompletedAssets = 0
        self.SucceededFiles = []
        self.CorruptedFiles: list[SophonManifestProtoChunkAsset] = []
        self.lock = threading.Lock()
        self.Percent = "0.0%"
        self.FloatPercent = 0.0

        # callback hooks
        self.on_progress_callback = None
        self.on_finish_callback = None
        self.on_cancel_callback = None
        self.on_pause_callback = None

        # control events
        self.pause_event = threading.Event()
        self.cancel_event = threading.Event()

    def update_progress(self):
        total = self.TotalSize or 0
        if total <= 0:
            self.FloatPercent = 0.0
            self.Percent = "0.0%"
            return
        pct = (self.TotalDownloadBytes / total) * 100.0
        pct = max(0.0, min(100.0, pct))
        self.FloatPercent = pct
        self.Percent = f"{pct:.2f}%"

    @property
    def isPaused(self): return self.pause_event.is_set()
    @property
    def isCancelled(self): return self.cancel_event.is_set()
    @property
    def isCompeleted(self): return self.TotalAssetsCount == self.CompletedAssets


# ────────────────────────────────────────────────
# Metadata DB
# ────────────────────────────────────────────────
class _LauncherDownloadMetadata:
    file_name = "metadata"
    path = None
    table_name = "SophonMetadataDB"
    hash_map = None
    db_lock = threading.Lock()
    download_trace = GlobalDownloadData()

    @classmethod
    def start(cls, base_path: str = ""):
        cls.path = Path(base_path, f"{cls.file_name}.db")
        cls.hash_map = sqlite3.connect(cls.path, check_same_thread=False)
        cls._create_table()
        cls.download_trace = GlobalDownloadData()

    @classmethod
    def _create_table(cls):
        with cls.hash_map:
            cls.hash_map.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {cls.table_name} (
                    identity TEXT PRIMARY KEY,
                    md5 TEXT,
                    sha1 TEXT,
                    sha256 TEXT,
                    size INTEGER
                )
                """
            )

    @classmethod
    def set_hash(cls, identity: str, hashs):
        with cls.db_lock, cls.hash_map:
            cls.hash_map.execute(
                f"""
                INSERT INTO {cls.table_name} (identity, md5, sha1, sha256, size)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(identity) DO UPDATE SET
                    md5=excluded.md5,
                    sha1=excluded.sha1,
                    sha256=excluded.sha256,
                    size=excluded.size
                """,
                (identity, hashs.md5, hashs.sha1, hashs.sha256, hashs.size),
            )

    @classmethod
    def get_hash(cls, identity: str):
        with cls.db_lock:
            cur = cls.hash_map.cursor()
            cur.execute(
                f"SELECT identity, md5, sha1, sha256, size FROM {cls.table_name} WHERE identity=?",
                (identity,),
            )
            return cur.fetchone()

    @classmethod
    def close(cls):
        if cls.hash_map:
            cls.hash_map.close()
            cls.hash_map = None


# ────────────────────────────────────────────────
# Main Downloader
# ────────────────────────────────────────────────
class HoyoDownloader:
    def __init__(self, manifest: SophonManifestProtoAssets, output_dir: str, workers=20):
        self.main_output_dir = Path(output_dir, f"{manifest.GameData.Name} {manifest.AssetCategory}")
        self.output_dir = Path(output_dir, f"tmp_{manifest.GameData.Name} {manifest.AssetCategory}")
        self.output_dir.mkdir(0o777, parents=True, exist_ok=True)
        self.manifest = manifest
        self.workers = workers

        _LauncherDownloadMetadata.file_name = f"{get_md5_hash(f'{manifest.GameData.Biz}:{manifest.GameData.ID}'.encode())}.resume"
        _LauncherDownloadMetadata.start(self.output_dir)
        t = _LauncherDownloadMetadata.download_trace
        t.TotalSize = manifest.TotalSize
        t.TotalFSize = manifest.TotalFSize
        t.TotalChunksCount = manifest.ChunksCount
        t.TotalAssetsCount = manifest.FilesCount

    @property
    def trace(self):
        return _LauncherDownloadMetadata.download_trace

    # ────────── Helpers ──────────
    def __safe_callback(self, callback, *args):
        if not callback:
            return
        trace = self.trace
        with trace.lock:
            try:
                callback(*args)
                trace.update_progress()
            except Exception as e:
                trace.stop_error = True
                trace.stop_error_msg = str(e)
                logger.exception(f"Callback {callback} failed >>> {e}")

    # ────────── Download logic ──────────
    def __download_chunk(self, chunk: SophonManifestProtoChunkAsset, asset_path):
        asset_path = Path(asset_path)
        chunk_path = Path(asset_path, f"{chunk.identity}.part{chunk.index:03}")
        asset_path.mkdir(parents=True, exist_ok=True)
        t = self.trace
        t.current_chunk = chunk

        # already downloaded?
        if chunk_path.exists():
            row = _LauncherDownloadMetadata.get_hash(chunk.identity)
            if row is not None and get_file_hashs(chunk.identity, chunk_path) == set_row_hashs(row):
                logger.info(f"Chunk {chunk.identity} already downloaded; skipping")
                with t.lock:
                    t.ExistFiles += 1
                    t.CompletedChunks += 1
                    t.SucceededFiles.append(chunk)
                t.update_progress()
                self.__safe_callback(t.on_progress_callback,t)
                _LauncherDownloadMetadata.set_hash(chunk.identity, get_file_hashs(chunk.identity, chunk_path))
                return True

        logger.info(f"Downloading chunk {chunk.identity}")
        try:
            response = requests.get(chunk.ChunkUrl, stream=True, timeout=30)
            response.raise_for_status()
            with open(chunk_path, "wb") as f:
                for data in response.iter_content(chunk_size=8192 * 8):
                    if not data:
                        continue
                    self.__safe_callback(t.on_progress_callback, t)
                    f.write(data)
                    f.flush()
                    with t.lock:
                        t.TotalDownloadBytes += len(data)
            self.__safe_callback(t.on_progress_callback, t)
        except DownloadCancelled:
            logger.warning(f"Chunk {chunk.identity} cancelled")
            return False
        except Exception as e:
            chunk.error = str(e)
            logger.error(f"Error while downloading chunk {chunk.identity}: {chunk.error}")
        finally:
            if getattr(chunk, "error", None) is None:
                with t.lock:
                    t.NotExistFiles += 1
                    t.CompletedChunks += 1
                    t.SucceededFiles.append(chunk)
                    _LauncherDownloadMetadata.set_hash(chunk.identity, get_file_hashs(chunk.identity, chunk_path))
                return True
            with t.lock:
                t.NotExistFiles += 1
                t.CompletedChunks += 1
                t.Errors += 1
                t.CorruptedFiles.append(chunk)
            chunk_path.unlink(missing_ok=True)
            return False

    def __download_asset(self, asset: SophonManifestProtoAsset):
        t = self.trace
        asset_path = Path(self.output_dir, asset.AssetHashMd5)
        ok = True
        for chunk in asset.AssetChunks:
            t.current_asset = asset
            while t.isPaused:
                if t.isCancelled or t.stop_error:
                    return False
                self.__safe_callback(t.on_pause_callback, t)
                time.sleep(0.2)
            if t.isCancelled:
                self.__safe_callback(t.on_cancel_callback, t)
                return False
            if not self.__download_chunk(chunk, asset_path):
                ok = False
        logger.info(f"Asset: {asset.AssetName} {'OK!' if ok else 'Not OK!'}")
        with t.lock:
            t.CompletedAssets += 1
        return True

    # ────────── Public download ──────────
    def download(self, on_progress_callback=None, on_finish_callback=None,
                 on_cancel_callback=None, on_pause_callback=None):
        t = self.trace
        t.on_progress_callback = on_progress_callback
        t.on_finish_callback = on_finish_callback
        t.on_cancel_callback = on_cancel_callback
        t.on_pause_callback = on_pause_callback

        try:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = {executor.submit(self.__download_asset, a): a for a in self.manifest.Assets}
                for future in as_completed(futures):
                    if t.isCancelled:
                        logger.warning("Cancelling remaining futures…")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    asset = futures[future]
                    try:
                        success = future.result()
                        if not success:
                            logger.warning(f"Asset failed or cancelled: {asset.AssetName}")
                    except Exception as e:
                        logger.error(f"Error downloading asset: {e}")
                        logger.exception(f"Error downloading asset {asset.AssetName}")
        except KeyboardInterrupt:
            logger.error("Download interrupted by user.")
            t.cancel_event.set()
        finally:
            if t.isCancelled:
                logger.warning("Download Canceled by user.")
            else:
                logger.info("Download Completed.")
            self.__safe_callback(t.on_finish_callback, t)
            _LauncherDownloadMetadata.close()
            return t

    # ────────── Assemble files ──────────
    def parser(self):
        for asset in self.manifest.Assets:
            logger.info(f"Assembling asset: {asset.AssetFilePath}")
            asset_path = Path(self.main_output_dir, asset.AssetFilePath)
            asset_path.parent.mkdir(parents=True, exist_ok=True)

            for chunk in asset.AssetChunks:
                chunk_path = Path(self.output_dir, asset.AssetHashMd5) / f"{chunk.identity}.part{chunk.index:03}"
                if not chunk_path.exists():
                    logger.error(f"Missing chunk: {chunk_path} , Skip…")
                    continue
                logger.debug(f"Decompressing chunk: {chunk_path}")
                start = time.time()
                try:
                    with open(chunk_path, "rb") as part_file:
                        data = decompress(part_file)
                        if data:
                            md5_hash = get_md5_hash(data)
                            if chunk.ChunkDecompressedHashMd5 == md5_hash:
                                with open(asset_path, "wb") as asset_file:
                                    for i in range(0, len(data), 8192):
                                        asset_file.write(data[i:i+8192])
                            else:
                                logger.warning(
                                    f"Hash mismatch for chunk: {chunk.identity}"
                                )
                        else:
                            logger.warning(f"No data returned from decompress for chunk: {chunk_path}")
                except Exception as e:
                    logger.error(f"Failed to decompress {chunk_path}: {e}")
                finally:
                    logger.debug(f"Chunk {chunk_path} decompressed in {time.time()-start:.2f}s")
        return self.output_dir
