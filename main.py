from fastapi import FastAPI, WebSocket
from database import Base, engine, SessionLocal
from models import Ticket
from ai import process_message
import json

app = FastAPI()

# Create DB tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Server running 🚀"}


# 💬 WebSocket Chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)

            message = data.get("message")

            if not message:
                await websocket.send_text(json.dumps({"error": "Message required"}))
                continue

            # 🧠 AI processing
            ai_result = process_message(message)

            # 🎫 Ticket creation if needed
            if ai_result["escalate"]:
                ticket = Ticket(
                    user_message=message,
                    category=ai_result["category"],
                    severity=ai_result["severity"]
                )
                db.add(ticket)
                db.commit()
                db.refresh(ticket)

                response = {
                    "response": ai_result["response"],
                    "ticket_id": ticket.id,
                    "category": ai_result["category"],
                    "severity": ai_result["severity"]
                }
            else:
                response = ai_result

            await websocket.send_text(json.dumps(response))

    except:
        db.close()
