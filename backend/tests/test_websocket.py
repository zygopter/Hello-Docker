import json
from fastapi.testclient import TestClient

def test_websocket_crud_events(client: TestClient):
    # 1) Open a WebSocket connection
    with client.websocket_connect("/ws/users") as ws:
        # 2) CREATE
        create_payload = {
            "firstname": "Marine",
            "lastname": "Chamoux",
            "nickname": "Marin",
            "email": "marin@gmail.com"
        }
        res = client.post("/users/", json=create_payload)
        assert res.status_code == 200
        created = res.json()
        # Receive the "create" event
        msg = ws.receive_json()
        assert msg["action"] == "create"
        assert msg["user"] == created

        # 3) UPDATE
        update_payload = {
            "firstname": "Robert",
            "lastname": "Chamoux",
            "nickname": "Rob",
            "email": "rob@gmail.com"
        }
        res = client.put(f"/users/{created['id']}", json=update_payload)
        assert res.status_code == 200
        updated = res.json()
        # Receive the "update" event
        msg = ws.receive_json()
        assert msg["action"] == "update"
        assert msg["user"] == updated

        # 4) DELETE
        res = client.delete(f"/users/{created['id']}")
        assert res.status_code == 200
        # Receive the "delete" event
        msg = ws.receive_json()
        assert msg["action"] == "delete"
        assert msg["user_id"] == created["id"]
