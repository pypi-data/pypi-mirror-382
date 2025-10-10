from dataclasses import dataclass

@dataclass
class FileHashes:
    identity:str
    md5: str
    sha1: str
    sha256: str
    size:int