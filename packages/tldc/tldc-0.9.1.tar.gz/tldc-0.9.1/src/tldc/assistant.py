from __future__ import annotations
from typing import Type
from pydantic import BaseModel, Field
from xai_sdk.chat import tool
from .db import DB
from .dirtree import DirTree

_registry: dict[str, Type[Assistant]] = {}

class ListFilesRequest(BaseModel):
    pass

class ReadFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")

class WriteFileRequest(BaseModel):
    path: str = Field(description="Path to the file, relative to the working directory.")
    text: str = Field(description="New contents of the file.")

class Assistant:
    def __init__(self, model, provider, settings, db: DB, dirtree: DirTree):
        self.model = model
        self.provider = provider
        self.db = db
        self.dirtree = dirtree

    tool_definitions = [
        tool(
            name="list_files",
            description="Returns json containing list of existing files, with paths relative to the working directory, and with is_synced flag which describes wether file contents changed since the last time it was fetched via read_file tool (0 - file contents changed, 1 - no change).",
            parameters=ListFilesRequest.model_json_schema(),
        ),
        tool(
            name="read_file",
            description="Returns file contents from given path.",
            parameters=ReadFileRequest.model_json_schema(),
        ),
        tool(
            name="write_file",
            description="Writes new file contents to given path - replaces entire file.",
            parameters=WriteFileRequest.model_json_schema(),
        ),
    ]

    request_classes = {
        "list_files": ListFilesRequest,
        "read_file": ReadFileRequest,
        "write_file": WriteFileRequest,
    }

    def list_files(self, request: ListFilesRequest):
        return self.dirtree.get_files()

    def read_file(self, request: ReadFileRequest):
        return self.dirtree.read_file(request.path)

    def write_file(self, request: WriteFileRequest):
        self.dirtree.write_file(request.path, request.text)

    tools_map = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
    }

    def prompt(self, prompt):
        pass

    def reset(self):
        self.db.reset_response_id(self.dirtree.cwd)
        self.db.del_history(self.dirtree.cwd)
        self.dirtree.reset()

    @classmethod
    def create(cls, model, provider, settings, db: DB, dirtree: DirTree) -> Assistant:
        sub_cls: Type[Assistant] = _registry.get(provider)
        if sub_cls is None:
            raise ValueError(f"Provider not implemented: {provider}")
        return sub_cls(model, provider, settings, db, dirtree)

def register(provider, cls: Type[Assistant]):
    _registry[provider] = cls