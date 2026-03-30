def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_get_note_not_found(client):
    """GET /notes/{id} dengan ID yang tidak ada harus mengembalikan 404."""
    r = client.get("/notes/99999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_create_note_missing_required_field(client):
    """POST /notes/ tanpa field 'title' harus mengembalikan 422 Unprocessable Entity."""
    r = client.post("/notes/", json={"content": "No title provided"})
    assert r.status_code == 422
