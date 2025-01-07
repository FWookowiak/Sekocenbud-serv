import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


#katalog
def test_get_katalog_success():
    response = client.get("/katalog/uid_example/sid_example")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_katalog_invalid_params():
    response = client.get("/katalog/uid_example")
    assert response.status_code == 404

#rozdział
def test_get_rozdzial_success():
    response = client.get("/rozdzial/uid_example/sid_example/catalog_id_example")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_rozdzial_missing_params():
    response = client.get("/rozdzial/uid_example/sid_example")
    assert response.status_code == 404

#tablica
def test_get_tablica_success():
    response = client.get("/tablica/uid_example/sid_example/chapter_id_example")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_tablica_missing_params():
    response = client.get("/tablica/uid_example/sid_example")
    assert response.status_code == 404

#pozycja
def test_get_pozycja_success():
    response = client.get("/pozycja/uid_example/sid_example/table_id_example")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pozycja_missing_params():
    response = client.get("/pozycja/uid_example/sid_example")
    assert response.status_code == 404
