from dataclasses import dataclass
import json
import os
from HoyoSophonDL.help import fix_url, format_bytes
import uuid

class SophonManifestProtoChunkAsset:
    """
        "ChunkName": "b0e83c52eece2882_5d71b037cf036981e17d8240d2b0661e",
        "ChunkDecompressedHashMd5": "5d71b037cf036981e17d8240d2b0661e",
        "ChunkSize": "34",
        "ChunkSizeDecompressed": "21"
    """
    def __init__(self,_parent, base_url: str, _chunk: dict,index:int):
        self._parent = _parent
        self.error = None
        self.ChunkName = _chunk.get("ChunkName")
        self.ChunkUrl = f"{fix_url(base_url)}/{_chunk.get('ChunkName')}"
        self.ChunkDecompressedHashMd5 = _chunk.get("ChunkDecompressedHashMd5")
        self.ChunkSize = int(_chunk.get("ChunkSize", 0))
        self.ChunkFSize = format_bytes(self.ChunkSize)
        self.ChunkSizeDecompressed = int(_chunk.get("ChunkSizeDecompressed", 0))
        self.ChunkFSizeDecompressed = format_bytes(self.ChunkSizeDecompressed)
        self.index = index
        
    @property
    def identity(self):
        return self.ChunkDecompressedHashMd5
        uuid.uuid3(
            uuid.NAMESPACE_DNS,
            f'{self.ChunkName}:{self.ChunkDecompressedHashMd5}:{self.ChunkSize}:{self.ChunkSizeDecompressed}'
        )

    def getDict(self):
        return {k: (v if not isinstance(v, list) else [_.getDict() for _ in v])
                for k, v in self.__dict__.items() if k.startswith("Chunk")}

    def getJson(self):
        return json.dumps(self.getDict(), ensure_ascii=False, indent=2)

    def __repr__(self):
        return self.getJson()


class SophonManifestProtoAsset:
    """
      "AssetName": "Game_Data/app.info",
      "AssetChunks": [],
      "AssetSize": "21",
      "AssetHashMd5": "5d71b037cf036981e17d8240d2b0661e"
    """
    def __init__(self, base_url: str, _asset: dict):
        self.AssetFilePath = _asset.get("AssetName")
        self.AssetName = os.path.basename(self.AssetFilePath)
        self.AssetPath = os.path.dirname(self.AssetFilePath)
        self.AssetNameWithoutExtention, self.AssetExtention = os.path.splitext(self.AssetName)
        self.AssetSize = int(_asset.get("AssetSize", 0))
        self.AssetFSize = format_bytes(self.AssetSize)
        self.AssetHashMd5 = _asset.get("AssetHashMd5")
        self.AssetChunks:list[SophonManifestProtoChunkAsset] = []
        for _chunk in _asset.get("AssetChunks", []):
            self.AssetChunks.append(SophonManifestProtoChunkAsset(self,base_url, _chunk,len(self.AssetChunks)))
        self.AssetChunksCount = len(self.AssetChunks)

    @property
    def identity(self):
        return uuid.uuid3(
            uuid.NAMESPACE_DNS,
            f"{self.AssetFilePath}:{self.AssetSize}:{self.AssetHashMd5}"
        )
    def getDict(self):
        return {k: (v if not isinstance(v, list) else [_.getDict() for _ in v])
                for k, v in self.__dict__.items() if k.startswith("Asset")}

    def getJson(self):
        return json.dumps(self.getDict(), ensure_ascii=False, indent=2)

    def __repr__(self):
        return self.getJson()


class SophonManifestProtoAssets:
    def __init__(self,game_data,asset_cat,version:str, base_url: str, json_data: dict={},update_from:str=None):
        self.GameData = game_data.GameData
        self.Assets:list[SophonManifestProtoAsset] = []
        self.TotalSize = 0
        self.ChunksCount = 0
        self.version = version
        self.base_url = base_url
        self.AssetCategory = asset_cat
        assets = json_data.get("Assets")
        self.update_from = update_from
        if not assets:
            return

        for asset in assets:
            obj = SophonManifestProtoAsset(base_url, asset)
            self.TotalSize += obj.AssetSize
            self.ChunksCount += obj.AssetChunksCount
            self.Assets.append(obj)

    @property
    def TotalFSize(self):
        return format_bytes(self.TotalSize)

    @property
    def FilesCount(self):
        return len(self.Assets)
    
    def getDict(self):
        return {
            "Category":self.AssetCategory,
            "UpdateFrom":self.update_from,
            "Version":self.version,
            "TotalSize": self.TotalSize,
            "TotalFSize": self.TotalFSize,
            "FilesCount": self.FilesCount,
            "ChunksCount": self.ChunksCount,
            "Assets": [a.getDict() for a in self.Assets],
        }

    def getJson(self):
        return json.dumps(self.getDict(), ensure_ascii=False, indent=2)

    @property
    def AssetsHashs(self) -> list[str]:
        return [asset.AssetHashMd5 for asset in self.Assets]

    def getBySrc(self,source:str):
        source = source.lower()
        for asset in self.Assets:
            if source in [asset.AssetHashMd5.lower(),asset.AssetName.lower(),asset.AssetNameWithoutExtention]:
                return asset
        return None

    def isHashExist(self,hash:str):
        return hash in self.AssetsHashs

    def AddAsset(self,asset:SophonManifestProtoAsset):
        self.TotalSize += asset.AssetSize
        self.ChunksCount += asset.AssetChunksCount
        self.Assets.append(asset)

    def RemoveAsset(self,asset:SophonManifestProtoAsset):
        self.TotalSize -= asset.AssetSize
        self.ChunksCount -= asset.AssetChunksCount
        self.Assets.remove(asset)


    def __repr__(self):
        return self.getJson()

@dataclass
class SophonMainAPIData:
    category_id: str = None
    category_name: str = None
    matching_field: str = None
    isChunksCompressed: bool = None
    isManifestCompressed: bool = None
    ChunksBaseURL: str = None
    ManifestBaseURL: str = None
    DirectURL: str = None
    version:str = None
    
    def __init__(self, main_manifest_data: dict,version:str):
        self.version = version
        self.category_id = main_manifest_data.get("category_id")
        self.category_name = main_manifest_data.get("category_name")
        self.matching_field = main_manifest_data.get("matching_field")
        self.isChunksCompressed = bool(main_manifest_data.get("chunk_download", {}).get("compression"))
        self.ChunksBaseURL = main_manifest_data.get("chunk_download", {}).get("url_prefix")
        self.isManifestCompressed = bool(main_manifest_data.get("manifest_download", {}).get("compression"))
        self.ManifestBaseURL = main_manifest_data.get("manifest_download", {}).get("url_prefix")
        self.DirectURL = fix_url(self.ManifestBaseURL + "/" + main_manifest_data.get("manifest", {}).get("id"))

    def getDict(self):
        return self.__dict__

    def getJson(self):
        return json.dumps(self.getDict(), ensure_ascii=False, indent=2)

    def __repr__(self):
        return self.getJson()



class SophonMainAPI:
    def __init__(self,game_data, main_manifest_data: dict):
        self.GameData = game_data
        self.build_id = main_manifest_data.get("build_id")
        self.version = main_manifest_data.get("tag")
        self.manifests = [SophonMainAPIData(_,self.version) for _ in main_manifest_data.get("manifests", [])]


    def isSourceExist(self,source:str):
        return source in self.ManifestsNames or source in self.ManifestsIDs
    
    def getBySrc(self,source:str):
        source = source.lower()
        for manifest in self.manifests:
            if manifest.matching_field.lower().startswith(source) or manifest.category_id.lower().startswith(source):
                return manifest
        return None

    @property
    def ManifestsNames(self):
        return [m.matching_field.lower() for m in self.manifests]

    @property
    def ManifestsIDs(self):
        return [m.category_id.lower() for m in self.manifests]

    def getByName(self, name: str):
        return next((m for m in self.manifests if m.matching_field.lower().startswith(name.lower())), None)

    def getByID(self, id: str):
        return next((m for m in self.manifests if m.category_id.lower().startswith(id.lower())), None)

    def getDict(self):
        return {
            "build_id": self.build_id,
            "version": self.version,
            "manifests": [m.getDict() for m in self.manifests],
        }

    def getJson(self):
        return json.dumps(self.getDict(), ensure_ascii=False, indent=2)

    def __repr__(self):
        return self.getJson()
