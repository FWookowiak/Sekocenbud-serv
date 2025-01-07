from fastapi import FastAPI, HTTPException, APIRouter, Query
from typing import List, Optional
from models import DBFHandler
import os

app = FastAPI()

router = APIRouter()

@router.get("/katalog", response_model=List[List[str]])
def get_katalog(sekocenbud_db: str = Query(..., description="Database version to use")):
    dbf_handler = DBFHandler(os.path.join("DBF", sekocenbud_db))
    result = [[item["code"], item["id"]] for item in dbf_handler.bcj_handler.get_catalogs()]
    return result

@router.get("/rozdzial/{id_katalogu}")
def get_rozdzial(
    id_katalogu: str,
    sekocenbud_db: str = Query(..., description="Nazwa DBF (np. 220)"),
):
    database = os.path.join("DBF", sekocenbud_db)
    dbf_handler = DBFHandler(database)
    bcj_handler = dbf_handler.bcj_handler
    result = bcj_handler.get_chapters(id_katalogu)

    return result

@router.get("/tablica/{id_rozdzialu}")
def get_tablica(
    id_rozdzialu: str,
    sekocenbud_db: str = Query(..., description="Nazwa DBF (np. 220)"),
):
    database = os.path.join("DBF", sekocenbud_db)
    dbf_handler = DBFHandler(database)
    bcj_handler = dbf_handler.bcj_handler
    result = bcj_handler.get_tables(id_rozdzialu)

    return result

@router.get("/pozycja/{id_tablicy}")
def get_pozycja(
    id_tablicy: str,
    sekocenbud_db: str = Query(..., description="Nazwa DBF (np. 220)"),
):
    database = os.path.join("DBF", sekocenbud_db)
    dbf_handler = DBFHandler(database)
    bcj_handler = dbf_handler.bcj_handler
    result = bcj_handler.get_items(id_tablicy)

    return result