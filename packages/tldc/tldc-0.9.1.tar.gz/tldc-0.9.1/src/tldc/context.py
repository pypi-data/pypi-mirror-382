import os
from .constants import DEFAULT_OLLAMA_MODEL
from .db import DB
from .dirtree import DirTree
from .assistant import Assistant
from .providers import xai, ollama
from .logger import _logger

class Context:
    @_logger
    def __init__(self, cwd=os.getcwd()):
        self.db = DB()
        self.cwd = cwd
        self.dirtree = DirTree(cwd, self.db)
        model = self.db.get_model(self.get_active_model())
        self.assistant = Assistant.create(model["model_name"], model["provider"], model["settings"],
                                          self.db, self.dirtree)

    @_logger
    def prompt(self, prompt):
        return self.assistant.prompt(prompt)

    @_logger
    def get_models(self):
        return self.db.get_models()

    @_logger
    def get_active_model(self):
        model_name = self.db.get_config_value("active_model")
        return model_name if model_name else DEFAULT_OLLAMA_MODEL

    @_logger
    def set_active_model(self, model_name):
        self.db.set_config_value("active_model", model_name)

    @_logger
    def add_model(self, model_name, provider, settings):
        self.db.add_model(model_name, provider, settings)

    @_logger
    def del_model(self, model_name):
        if model_name != DEFAULT_OLLAMA_MODEL:
            self.db.del_model(model_name)

    @_logger
    def reset(self):
        self.assistant.reset()

    @_logger
    def close(self):
        self.db.close()