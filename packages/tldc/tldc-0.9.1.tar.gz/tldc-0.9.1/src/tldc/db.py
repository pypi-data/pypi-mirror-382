import os
import sqlite3
from .constants import DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_SETTINGS

class DB:
    def __init__(self):
        confdir = os.environ["HOME"] + "/.config/tldc"
        os.makedirs(confdir, exist_ok=True)
        self.connection = sqlite3.connect(confdir + "/tldc.db")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
                                      CREATE TABLE IF NOT EXISTS config (key primary key, value);
                                      CREATE TABLE IF NOT EXISTS models (model_name primary key, provider, settings);
                                      CREATE TABLE IF NOT EXISTS contexts (context primary key, response_id);
                                      CREATE TABLE IF NOT EXISTS history (context, message);
                                      CREATE TABLE IF NOT EXISTS sync_status (path primary key, checksum, is_synced);
                                      """)
        self.connection.execute("REPLACE INTO models VALUES(:model_name, 'ollama', :settings)",
                                {"model_name": DEFAULT_OLLAMA_MODEL, "settings": DEFAULT_OLLAMA_SETTINGS})
        self.connection.commit()

    def close(self):
        self.connection.executescript("""
                                      VACUUM config;
                                      VACUUM models;
                                      VACUUM contexts;
                                      VACUUM history;
                                      VACUUM sync_status;
                                      """)
        self.connection.close()

    def get_history(self, context):
        return self.connection.execute("SELECT rowid, message FROM history WHERE context = :context",
                                       {"context": context})

    def add_history(self, context, message):
        self.connection.execute("INSERT INTO history VALUES(:context, :message)", {"context": context,
                                                                                   "message": message})
        self.connection.commit()

    def del_history(self, context):
        self.connection.execute("DELETE FROM history WHERE context = :context", {"context": context})
        self.connection.commit()

    def get_status(self, path):
        return self.connection.execute("SELECT checksum, is_synced FROM sync_status WHERE path = :path",
                                       {"path": path}).fetchone()

    def set_status(self, path, checksum, is_synced):
        self.connection.execute("REPLACE INTO sync_status VALUES(:path, :checksum, :is_synced)",
                                {"path": path, "checksum": checksum, "is_synced": is_synced})
        self.connection.commit()

    def reset_status(self, path):
        self.connection.execute("UPDATE sync_status SET is_synced = 0 WHERE path LIKE :path",
                                {"path": f"{path}/%"})
        self.connection.commit()

    def get_response_id(self, context):
        result = self.connection.execute("SELECT response_id FROM contexts WHERE context = :context",
                                         {"context": context}).fetchone()
        return result["response_id"] if result else None

    def set_response_id(self, context, response_id):
        self.connection.execute("REPLACE INTO contexts VALUES(:context, :response_id)",
                                {"context": context, "response_id": response_id})
        self.connection.commit()

    def reset_response_id(self, context):
        self.connection.execute("DELETE FROM contexts WHERE context = :context", {"context": context})
        self.connection.commit()

    def get_config_value(self, key):
        result = self.connection.execute("SELECT value FROM config WHERE key = :key",
                                         {"key": key}).fetchone()
        return result["value"] if result else None

    def set_config_value(self, key, value):
        self.connection.execute("REPLACE INTO config VALUES(:key, :value)",
                                {"key": key, "value": value})
        self.connection.commit()

    def get_models(self):
        return self.connection.execute("SELECT model_name, provider, settings FROM models")

    def get_model(self, model_name):
        return self.connection.execute("SELECT model_name, provider, settings FROM models WHERE model_name = :model_name", {"model_name": model_name}).fetchone()

    def add_model(self, model_name, provider, settings):
        self.connection.execute("REPLACE INTO models VALUES(:model_name, :provider, :settings)",
                                {"model_name": model_name, "provider": provider, "settings": settings})
        self.connection.commit()

    def del_model(self, model_name):
        self.connection.execute("DELETE FROM models WHERE model_name = :model_name",
                                {"model_name": model_name})
        self.connection.commit()