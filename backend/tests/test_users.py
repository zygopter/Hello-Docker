def test_create_and_get_user(client):
    # CREATE
    payload = {
        "firstname": "Alice",
        "lastname": "Dupont",
        "nickname": "Ali",
        "email": "alice@example.com"
    }
    res = client.post("/users/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["firstname"] == "Alice"

    # LIST
    res = client.get("/users/")
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 1

    # GET by ID
    res = client.get(f"/users/{data['id']}")
    assert res.status_code == 200
    assert res.json()["email"] == "alice@example.com"

def test_update_user(client):
    # UPDATE l'utilisateur 1
    update_payload = {
        "firstname": "Alice2",
        "lastname": "Dupont2",
        "nickname": "Al2",
        "email": "alice2@example.com"
    }
    res = client.put("/users/1", json=update_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["firstname"] == "Alice2"
    assert data["email"] == "alice2@example.com"

def test_delete_user(client):
    # DELETE l'utilisateur 1
    res = client.delete("/users/1")
    assert res.status_code == 200
    assert res.json() == {"ok": True}

    # Vérifier qu'il n'existe plus
    res = client.get("/users/1")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"
