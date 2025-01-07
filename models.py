from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import uuid
import os
from dbfread import DBF
import json
import pandas as pd

class WayTooBigException(Exception):
    pass



class AccessToken(Base):
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    call_count = Column(Integer, default=0)


DEFAULT_DATABASE = '324'
CAP = 100


class Catalog:
    def __init__(self, code):
        self.code = code
        self.chapters = []
        self.id = str(uuid.uuid4())

    def has_items(self):
        return any(chapter.tables for chapter in self.chapters)

    def json_repr(self):
        return {
            "code": self.code,
            "id": self.id,
        }

    def __str__(self):
        return f"{self.code}"

    def __repr__(self):
        return str(self)


class Chapter:
    def __init__(self, code, parent):
        self.code = code
        self.tables = []
        self.id = str(uuid.uuid4())
        self.parent = parent

    def json_repr(self):
        return {"name": self.code, "id": self.id, "parent": self.parent}

    def __str__(self):
        return f"{self.code}"

    def __repr__(self):
        return str(self)


class Table:
    def __init__(self, name, code, parent):
        self.name = name
        self.code = code
        self.items = []
        self.id = str(uuid.uuid4())
        self.parent = parent

    def json_repr(self):
        return {
            "symbol": self.code,
            "id": self.id,
            "opis": self.name,
            "parent": self.parent,
        }

    def __str__(self):
        return f"{self.code} {self.name}"

    def __repr__(self):
        return str(self)


class Item:
    def __init__(self, name, code, price, unit, parent):
        self.name = name
        self.code = code
        self.price = float(price.replace(",", "."))
        self.unit = unit
        self.id = str(uuid.uuid4())
        self.parent = parent

    def json_repr(self):
        return {
            "symbol": self.code,
            "katalog": "BCJ",
            "id": self.id,
            "cena": self.price,
            "jm": self.unit,
            "parent": self.parent,
            "opis": self.name,
        }

    def __str__(self):
        return f"{self.code} {self.name}"

    def __repr__(self):
        return str(self)


class DBFHandler:

    def parse_wki_dbf(self):
        pass

    def parse_bcj_dbf(self):
        database = DBF(self.bcj_dbf_file)

        catalogs = {}

        current_chapter = None
        current_table = None

        base_file_content = {"catalogs": [], "tables": [], "chapters": [], "items": []}

        for record in database:

            if record.get("CENA_SR"):
                if not current_table:
                    continue
                current_item = Item(
                    record.get("OPIS"),
                    record.get("SYMBOL"),
                    record.get("CENA_SR"),
                    record.get("JM_NAZWA"),
                    parent=current_table.id,
                )
                current_table.items.append(current_item)
                base_file_content["items"].append(current_item.json_repr())
            else:
                if current_table and current_table.items:
                    current_chapter.tables.append(current_table)

                symbol = record.get("SYMBOL").strip()
                if symbol[-1].isalpha() and symbol[-1].isupper():
                    catalog_symbol = record.get("KATALOG")
                else:
                    catalog_symbol = f"{record.get('KATALOG')} {symbol[0]}"

                if catalog_symbol not in catalogs.keys():
                    catalogs[catalog_symbol] = Catalog(catalog_symbol)
                    base_file_content["catalogs"].append(
                        catalogs[catalog_symbol].json_repr()
                    )
                    # temporary solutions for chapters
                    example_chapter = Chapter("01", catalogs[catalog_symbol].id)
                    base_file_content["chapters"].append(example_chapter.json_repr())
                    catalogs[catalog_symbol].chapters.append(example_chapter)
                    current_chapter = example_chapter

                current_table = Table(
                    record.get("NAZWA"), record.get("SYMBOL"), parent=current_chapter.id
                )
                base_file_content["tables"].append(current_table.json_repr())
        with open(self.bcj_json_file, "w") as f:
            json.dump(base_file_content, f)

    def check_files(self):
        if not os.path.exists(self.bcj_dbf_file) or not os.path.exists(
            self.wki_dbf_file
        ):
            raise FileNotFoundError("BCJ.DBF or WKI.DBF file not found")
        if not os.path.exists(self.bcj_json_file):
            self.parse_bcj_dbf()
        if not os.path.exists(self.wki_json_file):
            self.parse_wki_dbf()

    def __init__(self, dir_path):
        self.bcj_dbf_file = os.path.join(dir_path, "BCJ.DBF")
        self.bcj_json_file = os.path.join(dir_path, "BCJ.json")

        self.wki_dbf_file = os.path.join(dir_path, "WKI.DBF")
        self.wki_json_file = os.path.join(dir_path, "WKI.json")
        self.check_files()
        self.bcj_handler = BCJHandler(
            json.load(open(self.bcj_json_file))
            )


class BCJHandler:

    def __init__(self, json_file):
        self.json_file = json_file
        self.items_df = pd.DataFrame(self.json_file["items"])

    def search(self, catalog_id=None, chapter_id=None, table_id=None, phrase=None):
        if catalog_id:
            chapters = self.get_chapters(catalog_id)
            tables = []
            for chapter in chapters:
                tables += [table["id"] for table in self.get_tables(chapter["id"])]

            result = [
                item for item in self.json_file["items"] if item["parent"] in tables
            ]
            if phrase:
                result = [item for item in result if phrase in item["name"]]

        elif chapter_id:
            tables = [table["id"] for table in self.get_tables(chapter_id)]
            result = [
                item for item in self.json_file["items"] if item["parent"] in tables
            ]
            if phrase:
                result = [item for item in result if phrase in item["name"]]

        elif table_id:
            result = [
                item for item in self.json_file["items"] if item["parent"] == table_id
            ]
            if phrase:
                result = [item for item in result if phrase in item["name"]]
        else:
            raise WayTooBigException("You are trying to search in the whole database")

        if len(result) > CAP:
            raise WayTooBigException("Too many results")

        return result

    def get_catalogs(self):
        return self.json_file["catalogs"]

    def get_chapters(self, catalog_id):
        return [
            chapter
            for chapter in self.json_file["chapters"]
            if chapter["parent"] == catalog_id
        ]

    def get_tables(self, chapter_id):
        return [
            table for table in self.json_file["tables"] if table["parent"] == chapter_id
        ]

    def get_items(self, table_id):
        return [item for item in self.json_file["items"] if item["parent"] == table_id]

    def get_item_to_reprice(self, name):
        item = self.items_df[self.items_df["opis"] == name]
        if item.empty:
            return None
        return float(item['cena'])


class WKIHandler:
    def __init__(self, json_file):
        self.json_file = json_file