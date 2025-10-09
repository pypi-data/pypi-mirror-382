import json
import os
import sqlite3
import stat
from pathlib import Path
from typing import Union

from xxhash import xxh32 as xh

default_path = Path("./temp.db")


class Cache:
    # BUF_SIZE is totally arbitrary
    BUF_SIZE = 65536  # default 64kb chunks

    def __init__(self, path: Path = default_path, table: str = "cachehash"):
        self.db_path = path
        self.db = sqlite3.connect(path)

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.db.row_factory = dict_factory
        self.cur = self.db.cursor()
        self.table_name = table
        self.query("make_table")

    def is_regular_file(self, path: Path):
        """
        Checks if the given path is a regular file (not a socket, directory, etc.).
        Args:
            path: The path to check.
        Returns:
            True if the path is a regular file, False otherwise.
        """
        try:
            mode = os.stat(path).st_mode
            return stat.S_ISREG(mode)
        except FileNotFoundError:
            return False

    def query(self, file_name: str, parameters=None, query: Union[str, None] = None):
        cur_path = Path(__file__).parent.resolve().absolute()
        path = Path(f"{cur_path}/sql/{file_name}.sql")
        if query:
            query = query.replace("<table_name>", f'"{self.table_name}"')
            if parameters is not None:
                return self.cur.execute(query, parameters)
            else:
                return self.cur.execute(query)
        else:
            with open(path, "r") as f:
                query = f.read()
                query = query.replace("<table_name>", f'"{self.table_name}"')
                if parameters is not None:
                    return self.cur.execute(query, parameters)
                else:
                    return self.cur.execute(query)

    def hash_file(self, fp: Path) -> str:
        h = xh()
        if not self.is_regular_file(fp):
            return "Error: " + str(fp.absolute()) + "- Unhashable file type"
        with open(fp, "rb") as f:
            while True:
                data = f.read(self.BUF_SIZE)
                if not data:
                    break
                h.update(data)
        return h.hexdigest()

    def hash_directory(self, directory: Path) -> str:
        h = xh()
        # Walk through directory in a sorted manner for consistency
        for root, dirs, files in sorted(os.walk(directory)):
            # Hash directory names
            for d in sorted(dirs):
                dir_path = Path(root) / d
                # Add directory name and metadata to hash
                h.update(str(dir_path.relative_to(directory)).encode())
                h.update(str(dir_path.stat().st_mtime).encode())

            # Hash files
            for f in sorted(files):
                file_path = Path(root) / f
                # Add file path, size, and modification time to hash
                h.update(str(file_path.relative_to(directory)).encode())
                stat = file_path.stat()
                h.update(str(stat.st_size).encode())
                h.update(str(stat.st_mtime).encode())
                # Also include file content hash
                h.update(self.hash_file(file_path).encode())

        return h.hexdigest()

    def get_hash(self, path: Path) -> str:
        if path.is_file():
            return self.hash_file(path)
        elif path.is_dir():
            return self.hash_directory(path)
        else:
            raise ValueError(f"{path} is neither a file nor a directory")

    def get(
        self, file_path: Union[str, Path]
    ) -> Union[str, list, dict, int, float, None]:
        fp: str
        if type(file_path) is str:
            fp = file_path
            file_path = Path(file_path)
        else:
            fp = str(file_path)

        if not file_path.exists():
            raise ValueError(f"{file_path} does not exist")

        hash = self.get_hash(file_path)
        row = self.query(
            "get_record_hash_key",
            {"hash": hash, "key": fp},
        ).fetchone()

        if row is None:
            return None
        else:
            return json.loads(row["val"])

    def get_by_hash(
        self, file_path: Union[str, Path]
    ) -> Union[str, list, dict, int, float, None]:
        fp: str
        if type(file_path) is str:
            fp = file_path
            file_path = Path(file_path)
        else:
            fp = str(file_path)

        if not file_path.exists():
            raise ValueError(f"{file_path} does not exist")

        hash = self.get_hash(file_path)
        row = self.query(
            "get_record",
            {"hash": hash},
        ).fetchone()

        if row is None:
            return None
        else:
            return json.loads(row["val"])

    def set(
        self,
        file_path: Union[str, Path],
        values: Union[str, list, dict, int, float, None],
        append: bool = False,
    ):
        fp: str
        if isinstance(file_path, str):
            fp = file_path
            file_path = Path(file_path)
        elif isinstance(file_path, Path):
            fp = str(file_path)
        else:
            raise ValueError("Invalid file_path")

        if not file_path.exists():
            raise ValueError(f"{file_path} does not exist")

        values = json.dumps(values)

        hash = self.get_hash(file_path)
        existing_record = self.query(
            "get_record_hash_key",
            {"hash": hash, "key": fp},
        ).fetchone()
        if existing_record is not None and append is False:
            v = existing_record["val"]
            if v != values:
                self.query(
                    "update_record",
                    {
                        "key": fp,
                        "hash": hash,
                        "value": values,
                    },
                )
        else:
            self.query(
                "insert_record",
                {
                    "key": fp,
                    "hash": hash,
                    "value": values,
                },
            )
        self.db.commit()
