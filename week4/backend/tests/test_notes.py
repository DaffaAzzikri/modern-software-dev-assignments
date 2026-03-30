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


def test_get_note_by_id(client):
    # Create a note first
    payload = {"title": "Get Note Test", "content": "Testing get by ID"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    created_note = r.json()
    note_id = created_note["id"]

    # Get the note by ID
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert note["id"] == note_id
    assert note["title"] == "Get Note Test"
    assert note["content"] == "Testing get by ID"


def test_get_note_not_found(client):
    # Try to get a note that doesn't exist
    r = client.get("/notes/9999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()
