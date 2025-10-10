import shutil
from typing import Any, Callable
import requests
from packaging.version import Version

from HoyoSophonDL.download import GlobalDownloadData, HoyoDownloader
from HoyoSophonDL.parser import (
    LauncherParser,
    SophonMainAPI,
    SophonMainAPIData,
    AvaliableGamesEnum,
    GameBranchEnum,
    SophonManifestProtoAssets,
    Branch,
    Region,
    AvaliableGame
)

# Import logger from config
from HoyoSophonDL.config import logger


class LauncherClient:
    """
    Client for interacting with the Sophon Launcher API.

    Handles fetching available games, game info, manifests, and downloading assets.
    """

    _trace = None
    def __init__(self, branch: Branch = Branch.MAIN, region: Region = Region.EUROPE, verbose: bool = False):
        """
        Initialize the client with a branch and region.

        Args:
            branch (Branch): Launcher branch (default: MAIN).
            region (Region): Game region (default: EUROPE).
            verbose (bool): Enable verbose DEBUG logging if True.
        """
        # Pass verbose flag down to parser/config
        self._httpClient = requests.Session()
        self.parser = LauncherParser(branch, region,verbose)
        logger.debug(f"Initialized LauncherClient with branch={branch.name}, region={region.name}")

    @property
    def config(self):
        """Return the configuration used by the parser."""
        return self.parser.config

    def _check_response(self, _data: requests.Response, json_data=True):
        """
        Check an HTTP response for success.

        Args:
            _data (requests.Response): The HTTP response.
            json_data (bool): Whether to parse JSON (default True).

        Returns:
            dict or bytes: JSON dictionary if json_data=True, raw content otherwise.
        """
        if _data.status_code == 200:
            if json_data:
                response: dict = _data.json()
                if response.get("retcode") == 0 and response.get("message") == "OK":
                    return response
            else:
                return _data.content
        logger.error(f"HTTP request failed with status {_data.status_code}")
        return None

    def get_avalibale_games(self) -> AvaliableGamesEnum:
        """Fetch available games from the API."""
        logger.info("Fetching available games...")
        _url = self.config.getAvalibaleGamesInfoURL()
        _data = self._httpClient.get(_url)
        response = self._check_response(_data)
        if response:
            logger.debug("Available games response received.")
            return self.parser.parse_avaliable_games_api(response.get("data", []))
        logger.error("No games found.")
        raise requests.exceptions.RequestException("[+] No Games Found")

    def get_game_info(self, game: AvaliableGame) -> GameBranchEnum:
        """Fetch game branch info for a specific game."""
        logger.info(f"Fetching game info for: (ID={game.ID})")
        _data = self._httpClient.get(self.config.getGameInfoURL(game.ID))
        response = self._check_response(_data)
        if response:
            logger.debug(f"Game info retrieved for {game.Name}")
            return self.parser.parse_game_info_api(game, response.get("data", []))
        logger.error(f"Game info not found for {game.Name} (ID={game.ID})")
        raise requests.exceptions.RequestException(
            f"[+] Game ID: [{game.Name} - {game.ID}] Not Found"
        )

    def get_main_manifest(
        self, game_data: GameBranchEnum, version: str = None
    ) -> SophonMainAPI:
        """Fetch the main manifest for a game and optional version."""
        if version is None:
            version = game_data.LastVersion
        logger.info(f"Fetching main manifest for {game_data.GameData.Name} v{version}")
        manifest_url = self.config.buildDirectManifestURL(
            game_data.BranchID, game_data.PackageID, game_data.Password, version
        )
        _data = self._httpClient.get(manifest_url)
        response = self._check_response(_data)
        if response:
            logger.debug(f"Main manifest received for {game_data.GameData.Name} v{version}")
            return self.parser.parse_main_sophon_manifest(game_data, response.get("data"))
        logger.error(f"No manifest found for {game_data.GameData.Name} v{version}")
        raise requests.exceptions.RequestException(
            f"[+] Game: [{game_data.GameData.Name}] , No Manifest Found For Version: [{version}]"
        )

    def get_manifest_assets(
        self, game_data: GameBranchEnum, manifest: SophonMainAPIData
    ) -> SophonManifestProtoAssets:
        """Fetch the assets manifest for a specific game version."""
        logger.info(f"Fetching assets manifest: {manifest.category_name} v{manifest.version}")
        _data = self._httpClient.get(manifest.DirectURL, stream=True)
        response = self._check_response(_data, False)
        if response:
            logger.debug(f"Assets manifest parsed: {manifest.category_name} v{manifest.version}")
            return self.parser.parse_sophon_manifest_assets(game_data, manifest, response)
        logger.error(f"Failed to fetch assets manifest: {manifest.category_name}")
        raise requests.exceptions.RequestException(
            f"[+] Game Manifest: [{manifest.category_name}] , Error While Request Assets"
        )

    def get_target_assets(self, _info: AvaliableGame, current, update, matching):
        """
        Determine the assets that need to be updated or downloaded.

        Returns:
            SophonManifestProtoAssets: Assets that should be downloaded.
        """
        if _info is None:
            logger.error("UnKnown Game")
            raise ValueError("[ERR] UnKnown Game")
        logger.info(f"Preparing target assets for {_info.Name} (matching='{matching}')")
        game_data = self.get_game_info(_info)
        current_manifest = self.get_main_manifest(game_data, current)
        update_manifest = self.get_main_manifest(game_data, update) if update else None
        current_asset = current_manifest.getBySrc(matching)
        if current_asset is None:
            logger.error(f"Unknown matching_field: '{matching}' for version '{current}'")
            raise ValueError(f"[ERROR] Unknown matching_field: '{matching}' for version '{current}', Source: {_info}")

        update_asset = None
        if update:
            update_asset = update_manifest.getBySrc(matching)
            if update_asset is None:
                logger.error(f"Unknown matching_field for update version '{update}'")
                raise ValueError(f"[ERROR] Unknown matching_field: '{matching}' for update version '{current}', Source: {_info}")
            
            cur_v = Version(current_asset.version)
            upd_v = Version(update_asset.version)
            if cur_v > upd_v:
                temp_ = current_asset
                current_asset = update_asset
                update_asset = temp_
                del temp_
                logger.warning(f"switch update older <=> newer : cannot update from {current_asset.version} to older {update_asset.version}")
                # raise ValueError(f"[ERROR] Cannot update from older version {current_asset.version} to {update_asset.version}")
            if cur_v == upd_v:
                return self.get_manifest_assets(game_data, update_asset)
            
        return self.parser.compare_assets(
            self.get_manifest_assets(game_data, current_asset),
            self.get_manifest_assets(game_data, update_asset) if update else None
        )
    
    def set_download(self,assets:SophonManifestProtoAssets,output_dir:str,workers:int):
        logger.info(f"Starting download of {assets.FilesCount} assets...")
        hoyo_down = HoyoDownloader(assets, output_dir, workers)
        self._trace = hoyo_down.trace
        return hoyo_down
    
    def download_assets(
        self,
        hoyo_down: HoyoDownloader,
        on_progress_callback: Callable[[GlobalDownloadData], Any] = None,
        on_finish_callback: Callable[[GlobalDownloadData], Any] = None,
        on_cancel_callback: Callable[[GlobalDownloadData], Any] = None,
        on_pause_callback: Callable[[GlobalDownloadData], Any] = None,
    ) -> GlobalDownloadData:
        _trace = hoyo_down.download(on_progress_callback,on_finish_callback,on_cancel_callback,on_pause_callback)
        if _trace.isCompeleted:
            shutil.rmtree(hoyo_down.parser())
            logger.success("All assets downloaded and assembled successfully.")
        else:
            logger.warning("ALL Assets Not Downloaded Cancelled Flag")
        return _trace


# _Launcher = LauncherClient()

# game = _Launcher.get_avalibale_games().getByName("Genshin Impact")
# print(game.DisplayStatus)
# _info = _Launcher.get_game_info(game.GameID)
# print(_info.LastVersion)

# manifest = _Launcher.get_main_manifest(_info)
# for m in manifest.manifests:
#     print(vars(m))

# manifest = manifest.getByName("game")
# assets = _Launcher.get_manifest_assets(manifest)

# print(assets.version)
# print(assets.FilesCount)
# print(assets.TotalFSize)
# print(assets.TotalSize)
# print(assets.ChunksCount)

# open("ResponseAPIs/getManifestAssets.json", "wb").write(assets.getJson().encode())

# open("ResponseAPIs/getAvaliableGames.json","wb").write(.getJson().encode())
