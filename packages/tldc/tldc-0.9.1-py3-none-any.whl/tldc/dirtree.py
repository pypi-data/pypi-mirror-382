from pathlib import Path
from hashlib import md5
import os
import sys
from .constants import DIRTREE_EXCLUDE
from .constants import DIRTREE_EXCLUDE_ANYWHERE
from .constants import DIRTREE_MAXFILES
from .db import DB
from .logger import logger

class DirTree:
    def __init__(self, cwd, db: DB):
        self.cwd = cwd
        self.db = db
        self.path = Path(cwd)
        self.files = []
        self.statuses = {}
        for p in self.path.glob("*"):
            if self.check_path(p):
                if not p.is_dir():
                    self.files.append(str(p))
                    self._filecount_check()
                else:
                    for subp in p.glob("**/*"):
                        if not subp.is_dir() and self.check_path(subp):
                            self.files.append(str(subp))
                            self._filecount_check()
        for p in self.files:
            self.refresh(p)

    def _filecount_check(self):
        if len(self.files) > DIRTREE_MAXFILES:
            raise ValueError("1000 files and counting. Are we really doing this?")

    def get_files(self):
        logger("Getting file list")
        result = []
        for fullp in self.files:
            result.append({"path": self._to_relative(fullp), "is_synced": self.statuses[fullp]})
        return result

    def read_file(self, p):
        fullp = self._from_relative(p)
        if fullp.find(f"{self.cwd}/") == 0 and fullp.find(f"{self.cwd}/.git/") == -1:
            logger(f"Reading {fullp}")
            file = open(fullp, "r")
            data = file.read()
            file.close()
            self.mark_synced(p)
            return data
        else:
            raise PermissionError(f"AI tried to read {fullp}, access denied.")

    def write_file(self, p, data):
        fullp = self._from_relative(p)
        if fullp.find(f"{self.cwd}/") == 0 and fullp.find(f"{self.cwd}/.git/") == -1:
            logger(f"Writing {fullp}")
            dirp = str(Path(fullp).parent)
            os.makedirs(dirp, exist_ok=True)
            file = open(fullp, "w")
            file.write(data)
            file.close()
            self.mark_synced(p)
        else:
            raise PermissionError(f"AI tried to write {fullp}, access denied.")

    def mark_synced(self, p):
        fullp = self._from_relative(p)
        checksum = md5(open(fullp, "rb").read()).hexdigest()
        self.db.set_status(fullp, checksum, 1)
        self.statuses[fullp] = 1

    def _to_relative(self, fullp):
        return str(Path(fullp).relative_to(self.cwd))

    def _from_relative(self, p):
        return str(Path(f"{self.cwd}/{p}").resolve())

    def refresh(self, fullp):
        status = self.db.get_status(fullp)
        checksum = md5(open(fullp, "rb").read()).hexdigest()
        is_synced = 1 if status and status["checksum"] == checksum and status["is_synced"] == 1 else 0
        self.db.set_status(fullp, checksum, is_synced)
        self.statuses[fullp] = is_synced

    def reset(self):
        self.db.reset_status(self.cwd)

    def check_path(self, p):
        if str(p)[len(self.cwd)+1:] in DIRTREE_EXCLUDE:
            return False
        for subp in str(p).split("/"):
            if subp[subp.rfind("/")+1:] in DIRTREE_EXCLUDE_ANYWHERE:
                return False
        return True