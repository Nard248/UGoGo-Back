import websocket
import threading
import json


def on_message(ws, message):
    message_content = json.loads(message)["content"]
    print("Received:", message_content)


def on_open(ws):
    def run():
        while True:
            msg = input("Enter message: ").strip()
            if not msg:
                continue
            payload = {"content": msg}
            ws.send(json.dumps(payload))
    threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    my_user_id = input("Enter YOUR user ID: ").strip()
    other_user_id = input("Enter OTHER user's ID: ").strip()

    # Match your actual routing.py pattern
    url = f"ws://127.0.0.1:8000/ws/chat/dm/user/{other_user_id}/?user_id={my_user_id}"
    print(f"Connecting to {url}")

    ws = websocket.WebSocketApp(url, on_message=on_message)
    ws.on_open = on_open
    ws.run_forever()
