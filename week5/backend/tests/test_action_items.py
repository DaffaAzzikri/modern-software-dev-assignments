def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_complete_action_item_not_found(client):
    """PUT /action-items/{id}/complete dengan ID yang tidak ada harus mengembalikan 404."""
    r = client.put("/action-items/99999/complete")
    assert r.status_code == 404
    assert r.json()["detail"] == "Action item not found"


def test_create_action_item_missing_description(client):
    """POST /action-items/ tanpa field 'description' harus mengembalikan 422."""
    r = client.post("/action-items/", json={})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

def test_list_items_filter_completed_false(client):
    """GET /action-items/?completed=false returns only incomplete items."""
    id1 = client.post("/action-items/", json={"description": "Pending"}).json()["id"]
    id2 = client.post("/action-items/", json={"description": "Done"}).json()["id"]
    client.put(f"/action-items/{id2}/complete")

    r = client.get("/action-items/?completed=false")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == id1
    assert data[0]["completed"] is False


def test_list_items_filter_completed_true(client):
    """GET /action-items/?completed=true returns only completed items."""
    id1 = client.post("/action-items/", json={"description": "Pending"}).json()["id"]
    id2 = client.post("/action-items/", json={"description": "Done"}).json()["id"]
    client.put(f"/action-items/{id2}/complete")

    r = client.get("/action-items/?completed=true")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == id2
    assert data[0]["completed"] is True


def test_list_items_no_filter_returns_all(client):
    """GET /action-items/ without a filter returns all items regardless of status."""
    client.post("/action-items/", json={"description": "Task A"})
    id2 = client.post("/action-items/", json={"description": "Task B"}).json()["id"]
    client.put(f"/action-items/{id2}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ---------------------------------------------------------------------------
# Bulk-complete tests
# ---------------------------------------------------------------------------

def test_bulk_complete_success(client):
    """POST /action-items/bulk-complete marks all supplied IDs as completed."""
    id1 = client.post("/action-items/", json={"description": "Task 1"}).json()["id"]
    id2 = client.post("/action-items/", json={"description": "Task 2"}).json()["id"]

    r = client.post("/action-items/bulk-complete", json={"ids": [id1, id2]})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert all(item["completed"] is True for item in data)
    returned_ids = {item["id"] for item in data}
    assert returned_ids == {id1, id2}


def test_bulk_complete_empty_ids_returns_400(client):
    """POST /action-items/bulk-complete with an empty list returns 400."""
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 400
    assert r.json()["detail"] == "No IDs provided"


def test_bulk_complete_missing_body_field_returns_422(client):
    """POST /action-items/bulk-complete without the 'ids' field returns 422."""
    r = client.post("/action-items/bulk-complete", json={})
    assert r.status_code == 422


def test_bulk_complete_not_found_returns_404(client):
    """POST /action-items/bulk-complete with a non-existent ID returns 404."""
    r = client.post("/action-items/bulk-complete", json={"ids": [99999]})
    assert r.status_code == 404
    assert "99999" in r.json()["detail"]


def test_bulk_complete_partial_not_found_rolls_back(client):
    """If one ID is missing the entire transaction is rolled back.

    The valid item that was processed before the missing ID must remain
    incomplete after the request returns 404.
    """
    id1 = client.post("/action-items/", json={"description": "Real task"}).json()["id"]

    r = client.post("/action-items/bulk-complete", json={"ids": [id1, 99999]})
    assert r.status_code == 404

    # A fresh GET must show id1 is still incomplete (rollback was effective)
    r = client.get("/action-items/?completed=false")
    assert r.status_code == 200
    pending_ids = [item["id"] for item in r.json()]
    assert id1 in pending_ids
