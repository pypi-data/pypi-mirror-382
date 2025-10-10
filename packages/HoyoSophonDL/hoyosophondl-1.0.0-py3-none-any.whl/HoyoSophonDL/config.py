from enum import Enum
import urllib.parse
from HoyoSophonDL.help import fix_url,logger


LOG_FILE = "SophonDownloader.log"


def configure_logger(verbose: bool = False):
    """
    Configure global logger.

    Args:
        verbose (bool): Enable DEBUG logs if True, else INFO only.
    """
    logger.remove()

    if verbose:
        format = ("<green>{time:HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>")
    else:
        format = ("<level>[{level}]</level> <level>{message}</level>")

    logger.add(
        sink=lambda msg: print(msg, end=""),
        colorize=True,
        level="DEBUG" if verbose else "INFO",
        format=format
    )

    # File output
    logger.add(
        LOG_FILE,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="DEBUG",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )


class Region(Enum):
    EUROPE = "OSREL"
    CHINESE = "CNREL"


class Branch(Enum):
    MAIN = "main"
    DEV = "dev"
    PreDownload = "pre_download"


# ------------------------- CONFIGURATION ------------------------- #
class LauncherConfig:
    """
    A configuration manager for handling launcher API endpoints, regions, and build branches.

    Attributes:
        INFO_API (str): Base URL for game and branch information APIs.
        SOPHON_API (str): Base URL for Sophon (asset/chunk) APIs.
        LauncherID (str): Unique launcher identifier required for API calls.
        LauncherPlatformApp (str): Platform application ID for the launcher.
        DefaultBranch (str): Currently selected branch (e.g., 'main', 'dev').
    """

    def __init__(self, branch: Branch = Branch.MAIN, region: Region = Region.EUROPE, verbose: bool = False):
        """
        Initialize configuration and automatically configure logger.

        Args:
            branch (Branch): Launcher branch (default: MAIN)
            region (Region): Game region (default: EUROPE)
            verbose (bool): Enable verbose DEBUG logging if True
        """
        logger.info(f"Logger initialized with verbose={'ON' if verbose else 'OFF'}")
        self.verbose = verbose
        configure_logger(verbose)
        self.setRegion(region)
        self.setBranch(branch)
        logger.debug(f"Config created for region={region.name}, branch={branch.name}")
        logger.debug(f"Initialized LauncherConfig with Branch={branch}, Region={region}")

    def setLauncherID(self, NewLauncherID: str):
        """
        Set a custom launcher ID.

        Args:
            NewLauncherID (str): New launcher ID to use.
        """
        self.LauncherID = NewLauncherID
        logger.info(f"Launcher ID set to {NewLauncherID}")

    def setLauncherPlatform(self, NewPlatform: str):
        """
        Set a custom platform application ID.

        Args:
            NewPlatform (str): New platform application ID.
        """
        self.LauncherPlatformApp = NewPlatform
        logger.info(f"Launcher platform app set to {NewPlatform}")

    def setRegion(self, region: Region):
        """
        Configure API endpoints and default launcher credentials based on region.

        Args:
            region (Region): Target region (EUROPE or CHINESE).

        Raises:
            ValueError: If the provided region is unsupported.
        """
        logger.debug(f"Setting region to {region}")
        if region == Region.EUROPE:
            self.INFO_API = "https://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api"
            self.SOPHON_API = "https://sg-public-api.hoyoverse.com/downloader/sophon_chunk/api/getBuild"
            self.LauncherID = "VYTpXlbWo8"
            self.LauncherPlatformApp = "ddxf6vlr1reo"
        elif region == Region.CHINESE:
            self.INFO_API = "https://hyp-api.mihoyo.com/hyp/hyp-connect/api"
            self.SOPHON_API = "https://api-takumi.mihoyo.com/downloader/sophon_chunk/api/getBuild"
            self.LauncherID = "jGHBHlcOq1"
            self.LauncherPlatformApp = "ddxf5qt290cg"
        else:
            logger.error(f"Unknown region provided: {region}")
            raise ValueError(f"Unknown region: {region}")
        logger.info(f"Region set to {region.name} with API={self.INFO_API}")

    def setBranch(self, branch: Branch):
        """
        Set the current branch for the launcher configuration.

        Args:
            branch (Branch): The branch to set (MAIN, DEV, PreDownload).
        """
        self.DefaultBranch = branch.value
        logger.info(f"Branch set to {branch.value}")

    def getAvalibaleGamesInfoURL(self) -> str:
        """
        Construct the URL for fetching the list of available games.

        Returns:
            str: Full URL for the available games API.
        """
        url = fix_url(
            f"{self.INFO_API}/getGames?launcher_id={self.LauncherID}&language=en-us"
        )
        logger.debug(f"Available games URL: {url}")
        return url

    def getGameInfoURL(self, game_id: str) -> str:
        """
        Construct the URL for fetching detailed branch information about a specific game.

        Args:
            game_id (str): The unique game ID.

        Returns:
            str: Full URL for the game info API.
        """
        url = fix_url(
            f"{self.INFO_API}/getGameBranches?game_ids[]={game_id}&launcher_id={self.LauncherID}"
        )
        logger.debug(f"Game info URL for game_id={game_id}: {url}")
        return url

    def get_correct_version(self, user_version: str) -> str:
        """
        Normalize a user-provided version string into a three-part version (X.Y.Z).

        Args:
            user_version (str): The raw version string.

        Returns:
            str: Normalized version string or None if no version provided.
        """
        if user_version is None:
            return None
        parts = user_version.strip().split(".")
        while len(parts) < 3:
            parts.append("0")
        normalized_version = ".".join(parts[:3])
        logger.debug(f"Normalized version: {normalized_version}")
        return normalized_version

    def buildDirectManifestURL(
        self, branch_id: str, package_id: str, password: str, version: str
    ) -> str:
        """
        Build a URL to directly access the Sophon manifest for a specific game build.

        Args:
            branch_id (str): ID of the branch to fetch.
            package_id (str): Package ID of the game build.
            password (str): Password required for manifest retrieval.
            version (str): Version of the game build.

        Returns:
            str: Fully constructed direct manifest URL.
        """
        url = fix_url(
            f"{self.SOPHON_API}?{urllib.parse.urlencode({ 
                'branch': branch_id,
                'package_id': package_id,
                'password': password,
                'plat_app': self.LauncherPlatformApp,
                'tag': self.get_correct_version(version)
            })}"
        )
        logger.debug(f"Direct manifest URL: {url}")
        return url
