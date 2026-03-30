def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"

def test_notes_pagination_and_sorting(client):
    # Setup: Create 5 distinct notes
    notes_data = [
        {"title": "Alpha Note", "content": "Content alpha"},
        {"title": "Beta Note", "content": "Content beta"},
        {"title": "Charlie Note", "content": "Content charlie"},
        {"title": "Delta Note", "content": "Content delta"},
        {"title": "Echo Note", "content": "Content echo"},
    ]
    
    created_notes = []
    for data in notes_data:
        r = client.post("/notes/", json=data)
        assert r.status_code == 201, r.text
        created_notes.append(r.json())
    
    # Test limit & skip: Page 1 (limit=2, skip=0)
    r = client.get("/notes/", params={"limit": 2, "skip": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 2, "Page 1 should have exactly 2 items"
    page1_ids = {note["id"] for note in page1}
    
    # Test limit & skip: Page 2 (limit=2, skip=2)
    r = client.get("/notes/", params={"limit": 2, "skip": 2})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 2, "Page 2 should have exactly 2 items"
    page2_ids = {note["id"] for note in page2}
    
    # Verify pages have different items
    assert page1_ids.isdisjoint(page2_ids), "Page 1 and Page 2 should have different items"
    
    # Test sorting by id ascending
    r = client.get("/notes/", params={"sort": "id", "limit": 100})
    assert r.status_code == 200
    sorted_asc = r.json()
    asc_ids = [note["id"] for note in sorted_asc]
    assert asc_ids == sorted(asc_ids), "IDs should be sorted in ascending order"
    
    # Test sorting by id descending
    r = client.get("/notes/", params={"sort": "-id", "limit": 100})
    assert r.status_code == 200
    sorted_desc = r.json()
    desc_ids = [note["id"] for note in sorted_desc]
    assert desc_ids == sorted(desc_ids, reverse=True), "IDs should be sorted in descending order"
    
    # Test sorting by title ascending
    r = client.get("/notes/", params={"sort": "title", "limit": 100})
    assert r.status_code == 200
    sorted_by_title_asc = r.json()
    titles_asc = [note["title"] for note in sorted_by_title_asc]
    assert titles_asc == sorted(titles_asc), "Titles should be sorted in ascending order"
    
    # Test sorting by title descending
    r = client.get("/notes/", params={"sort": "-title", "limit": 100})
    assert r.status_code == 200
    sorted_by_title_desc = r.json()
    titles_desc = [note["title"] for note in sorted_by_title_desc]
    assert titles_desc == sorted(titles_desc, reverse=True), "Titles should be sorted in descending order"
