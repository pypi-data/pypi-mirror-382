from dataclasses import dataclass, asdict
import json


@dataclass
class AvaliableGame:
    ID: str = None
    Name: str = None
    Icon: str = None
    Background: str = None
    Biz: str = None
    Logo: str = None
    Language: str = None
    DisplayStatus: str = None


class AvaliableGamesEnum:
    def __init__(self, Games: list[str,dict]):
        self.Games: list[AvaliableGame] = []
        for Game in Games:
            DisplayData = Game.get("display")
            DisplayStatus = Game.get("display_status")
            self.Games.append(
                AvaliableGame(
                    ID=Game.get("id"),
                    Name=DisplayData.get("name"),
                    Icon=DisplayData.get("icon", {}).get("url"),
                    Background=DisplayData.get("background", {}).get("url"),
                    Biz=Game.get("biz").replace("_global", ""),
                    Logo=DisplayData.get("logo", {}).get("url"),
                    Language=DisplayData.get("language"),
                    DisplayStatus=DisplayStatus,
                )
            )

    @property
    def getGamesByNames(self) -> dict[str, AvaliableGame]:
        return {game.Name.lower(): game for game in self.Games}

    @property
    def getGamesNames(self) -> list[str]:
        return list(self.getGamesByNames.keys())

    @property
    def getGamesByID(self) -> dict[str, AvaliableGame]:
        return {game.ID.lower(): game for game in self.Games}

    @property
    def getGamesID(self) -> list[str]:
        return list(self.getGamesByID.keys())

    @property
    def getGamesByBiz(self) -> dict[str, AvaliableGame]:
        return {game.Biz.lower(): game for game in self.Games}

    @property
    def getGamesBiz(self) -> list[str]:
        return list(self.getGamesByBiz.keys())

    def getBySource(self, _string: str):
        _string = _string.lower().strip()
        by_name = self.getByName(_string)
        if by_name:
            return by_name
        by_name = self.getByID(_string)
        if by_name:
            return by_name
        by_name = self.getByBiz(_string)
        if by_name:
            return by_name
        return None

    def getByName(self, name: str):
        return self.getGamesByNames.get(
            name.lower(), self.getGamesByNames.get(name)
        )

    def getByID(self, id: str):
        return self.getGamesByID.get(id, None)

    def getByBiz(self, biz: str):
        return self.getGamesByBiz.get(biz, None)

    @property
    def getDict(self):
        return {"Games": [asdict(game) for game in self.Games]}

    @property
    def getJson(self):
        return json.dumps(self.getDict)


@dataclass
class GameBranchCategoryEnum:
    matching_field: str = None
    category_id: str = None


class GameBranchEnum:
    GameData: AvaliableGame = None
    BranchID: str = None
    LastVersion: str = None
    OtherVersion: list[str] = []
    PackageID: str = None
    Password: str = None

    def __init__(self, game: AvaliableGame, branch: dict):
        self.GameData = game
        self.BranchID = branch["branch"]
        self.PackageID = branch["package_id"]
        self.Password = branch["password"]
        self.LastVersion = branch["tag"]
        self.OtherVersion = branch["diff_tags"]
        self.Categories = [
            GameBranchCategoryEnum(
                matching_field=cat["matching_field"], category_id=cat["category_id"]
            )
            for cat in branch["categories"]
        ]

    def getGameCategory(self):
        return self.getCategoryByName("game")
    
    def getLanguageCategory(self,lang:str):
        return self.getCategoryByName(lang)

    def getCategoryByID(self, id: str=None):
        if id is None:
            return [cat.category_id for cat in self.Categories]
        for cat in self.Categories:
            if id == cat.category_id:
                return cat
        return None

    def getCategoryByName(self, name: str = None):
        if name is None:
            return [cat.matching_field for cat in self.Categories]
        name = name.lower()
        for cat in self.Categories:
            if cat.matching_field.lower().startswith(name):
                return cat
        return None

    @property
    def getDict(self):
        # Convert manually since self is not a dataclass
        return {
            "BranchData": {
                "GameData": asdict(self.GameData),
                "BranchID": self.BranchID,
                "LastVersion": self.LastVersion,
                "OtherVersion": self.OtherVersion,
                "PackageID": self.PackageID,
                "Password": self.Password,
                "Categories": [asdict(c) for c in self.Categories],
            }
        }

    @property
    def getJson(self):
        return json.dumps(self.getDict, indent=4)
