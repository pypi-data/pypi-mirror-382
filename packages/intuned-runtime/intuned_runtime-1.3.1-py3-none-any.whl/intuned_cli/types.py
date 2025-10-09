from pydantic import BaseModel
from pydantic import RootModel


class FileSystemTree(RootModel[dict[str, "DirectoryNode | FileNode"]]):
    root: dict[str, "DirectoryNode | FileNode"]


class DirectoryNode(BaseModel):
    directory: "FileSystemTree"


class FileNodeContent(BaseModel):
    contents: str


class FileNode(BaseModel):
    file: "FileNodeContent"


FileSystemTree.model_rebuild()
