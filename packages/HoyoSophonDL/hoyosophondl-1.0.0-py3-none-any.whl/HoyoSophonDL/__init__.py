from typing import Any, Callable
from HoyoSophonDL.download import GlobalDownloadData
from HoyoSophonDL.structs.SophonManifest import SophonManifestProtoAssets
from HoyoSophonDL.structs.GamesInfo import AvaliableGame
from HoyoSophonDL.client import LauncherClient
from HoyoSophonDL.config import Branch, Region


class HoyoSophonDL:
    """
    A high-level launcher client for interacting with HoYo games.
    
    This class provides methods to:
        - Fetch available games.
        - Get information about specific games.
        - Retrieve asset information for games.
        - Download game assets.

    Attributes:
        _launcher (LauncherClient): Internal client to handle requests and downloads.
    """

    def __init__(
        self,
        branch: Branch = Branch.MAIN,
        region: Region = Region.EUROPE,
        verbose: bool = False,
    ):
        """
        Initialize the HoyoSophonDL.

        Args:
            branch (Branch): The branch of the game (default: Branch.MAIN).
            region (Region): The game server region (default: Region.EUROPE).
        """
        self._launcher = LauncherClient(branch, region, verbose)

    @property
    def config(self):
        """
        Get the launcher's configuration.

        Returns:
            dict: Configuration dictionary.
        """
        return self._launcher.config

    def get_available_games(self):
        """
        Fetch all available games from the launcher.

        Returns:
            AvaliableGamesEnum: object mapping game source names to AvaliableGame objects.
        """
        return self._launcher.get_avalibale_games()

    def get_game_by_source(self, source: str):
        """
        Get a specific game by its source string.

        Args:
            source (str): The game's source string (e.g., "genshin impact").

        Returns:
            AvaliableGame | None: The corresponding AvaliableGame object if found, else None.
        """
        games = self.get_available_games()
        return games.getBySource(source)

    def get_game_info(self, game: AvaliableGame):
        """
        Get detailed information about a specific game.

        Args:
            game (AvaliableGame): The game object to retrieve info for.

        Returns:
            GameBranchEnum: Detailed information about the game.
        """
        return self._launcher.get_game_info(game)

    def get_assets_info(
        self,
        game: str | AvaliableGame,
        current_version: str | None = None,
        update_version: str | None = None,
        category: str = "game",
    ) -> SophonManifestProtoAssets:
        """
        Retrieve asset information for a specific game.

        Args:
            game (str | AvaliableGame): Either the game source string or an AvaliableGame object.
            current_version (str | None): Current version of the game (optional).
            update_version (str | None): Target update version (optional).
            category (str): Category of assets to retrieve (default: "game").

        Returns:
            SophonManifestProtoAssets: Object containing the game's asset information.
        """
        if isinstance(game, str):
            game = self.get_game_by_source(game)
        return self._launcher.get_target_assets(
            game, current_version, update_version, category.lower()
        )

    def set_download_assets(self,
        assets: SophonManifestProtoAssets,
        output_dir: str | None = None,
        workers: int = 20
    ):
        return self._launcher.set_download(assets, output_dir, workers)

    def download_assets(
        self,
        downloader,
        on_progress_callback: Callable[[GlobalDownloadData], Any] = None,
        on_finish_callback: Callable[[GlobalDownloadData], Any] = None,
        on_cancel_callback: Callable[[GlobalDownloadData], Any] = None,
        on_pause_callback: Callable[[GlobalDownloadData], Any] = None,
    ) -> GlobalDownloadData:
        """
        Download the specified assets to a given directory.

        Args:
            assets (SophonManifestProtoAssets): The assets object to download.
            output_dir (str | None): Directory to save downloaded assets (default: None = current directory).
            workers (int|None): Number of concurrent download threads.
            on_progress_callback (callable, optional):
                Function to call on every progress update; receives the global trace.
            on_finish_callback (callable, optional):
                Called once a chunk or an entire asset finishes downloading.
            on_cancel_callback (callable, optional):
                Called when the download is cancelled.
            on_pause_callback (callable, optional):
                Called repeatedly while the download is paused.
        Returns:
            Any: Result of the download process as (GlobalDownloadData)
        """
        return self._launcher.download_assets(
            downloader,
            on_progress_callback,
            on_finish_callback,
            on_cancel_callback,
            on_pause_callback,
        )

    @property
    def trace_download(self):
        return self._launcher._trace
