import json
from HoyoSophonDL.structs.SophonManifest import SophonMainAPIData, SophonManifestProtoAssets, SophonMainAPI
from HoyoSophonDL.structs.GamesInfo import AvaliableGame, AvaliableGamesEnum, GameBranchEnum
from HoyoSophonDL.config import Branch, LauncherConfig, Region, logger
from google.protobuf.json_format import MessageToJson
from HoyoSophonDL.proto import SophonManifestProto, SophonPatchProto
from HoyoSophonDL.help import decompress


class LauncherParser:
    """
    Parser for Sophon Launcher API responses and manifest data.
    """

    def __init__(self, branch: Branch = Branch.MAIN, region: Region = Region.EUROPE,verbose:bool = False):
        self.config = LauncherConfig(branch, region,verbose)
        logger.info(f"Initialized LauncherParser with Branch={branch}, Region={region}")

    def parse_avaliable_games_api(self, _api: dict) -> AvaliableGamesEnum:
        logger.debug("Parsing available games from API response.")
        Games = _api.get("games")
        if not Games:
            logger.error("No games found in the API response.")
            raise ValueError("[+] No Games Found")

        games = []
        for Game in Games:
            DisplayStatus = Game.get("display_status")
            if DisplayStatus == "LAUNCHER_GAME_DISPLAY_STATUS_AVAILABLE":
                games.append(Game)
                logger.info(f"Game available: {Game.get('display', {}).get('name')}")
            else:
                logger.warning(
                    f"Unknown status: {DisplayStatus} - ID: {Game.get('id')} "
                    f"=> {Game.get('display', {}).get('name')}"
                )

        logger.info(f"Total available games parsed: {len(games)}")
        return AvaliableGamesEnum(games)

    def parse_game_info_api(self, game: AvaliableGame, _api: dict) -> GameBranchEnum:
        logger.debug(f"Parsing game info for {game.Name} (ID: {game.ID})")
        GameInfo = _api.get("game_branches", [])
        if not GameInfo:
            logger.error(f"No branches found for game: {game.Name}")
            raise ValueError(f"[+] No Branch Found For This Game ID: {game}")

        if len(GameInfo) > 1:
            logger.warning(
                f"Multiple branches found for {game.Name}, using "
                f"[{self.config.DefaultBranch}] branch."
            )

        logger.info(f"Selected branch for {game.Name}: {self.config.DefaultBranch}")
        return GameBranchEnum(game, GameInfo[0][self.config.DefaultBranch])

    def compare_assets(
        self,
        old_assets: SophonManifestProtoAssets,
        new_assets: SophonManifestProtoAssets
    ) -> SophonManifestProtoAssets:
        logger.debug("Comparing asset manifests.")
        if new_assets is None:
            logger.info("No new assets provided; returning old assets.")
            return old_assets

        logger.info(
            f"Old assets: {len(old_assets.AssetsHashs)} | "
            f"New assets: {len(new_assets.AssetsHashs)}"
        )

        final_asset = SophonManifestProtoAssets(
            new_assets,
            new_assets.AssetCategory,
            new_assets.version,
            new_assets.base_url,
            {},
            old_assets.version
        )

        new_count = 0
        for _nh in new_assets.AssetsHashs:
            if not old_assets.isHashExist(_nh):
                final_asset.AddAsset(new_assets.getBySrc(_nh))
                new_count += 1

        logger.info(f"Identified {new_count} new/updated assets.")
        return final_asset

    def parse_main_sophon_manifest(self, game_data: GameBranchEnum, manifest_data: dict) -> SophonMainAPI:
        logger.debug(f"Parsing main Sophon manifest for {game_data.GameData.Name}")
        return SophonMainAPI(game_data, manifest_data)

    def parse_sophon_manifest_assets(
        self,
        game_data: GameBranchEnum,
        manifest: SophonMainAPIData,
        manifest_bytes: bytes
    ) -> SophonManifestProtoAssets:
        logger.debug(f"Parsing asset manifest for category: {manifest.category_name}")
        if manifest.isManifestCompressed:
            logger.info("Manifest is compressed; attempting decompression.")
            manifest_bytes = decompress(manifest_bytes)
            if not manifest_bytes:
                logger.error(f"Decompression failed for {manifest.category_name}")
                raise ValueError(
                    f"[+] Decompression Assets Failed: {manifest.category_name} - {manifest.matching_field}"
                )
            logger.info("Decompression successful.")

        manifest_sophon = SophonManifestProto.SophonManifestProto()
        manifest_sophon.ParseFromString(manifest_bytes)
        logger.debug("Manifest protobuf parsed successfully.")

        json_data = MessageToJson(manifest_sophon, preserving_proto_field_name=True)
        logger.info(f"Manifest '{manifest.category_name}' converted to JSON.")

        return SophonManifestProtoAssets(
            game_data,
            manifest.matching_field,
            manifest.version,
            manifest.ChunksBaseURL,
            json.loads(json_data)
        )

    def __ReadProtoFromPatchInfo(self, patch_info: bytes) -> dict:
        logger.debug("Parsing patch info protobuf.")
        manifest = SophonPatchProto.SophonPatchProto()
        manifest.ParseFromString(patch_info)
        json_data = MessageToJson(manifest, preserving_proto_field_name=True)
        logger.info("Patch info parsed to JSON successfully.")
        return json.loads(json_data)
