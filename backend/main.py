import os
from typing import Optional, List
from fastapi import FastAPI, Depends
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect

from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env (facultatif)
load_dotenv()

# Chaîne de connexion à PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle de table
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)

# # Création automatique de la table si nécessaire
# Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            await connection.send_json(message)

manager = ConnectionManager()

app = FastAPI()


origins = [
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # ou ["*"] pour tout autoriser (pas recommandé en prod)
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE…
    allow_headers=["*"],          # Content-Type, Authorization…
)

# Schémas Pydantic
class MessageIn(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: int
    content: str

# Point d'entrée POST
@app.post("/messages/", response_model=MessageOut)
def create_message(msg: MessageIn):
    db = SessionLocal()
    db_msg = Message(content=msg.content)
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    db.close()
    return MessageOut(id=db_msg.id, content=db_msg.content)

# Point d'entrée GET
@app.get("/messages/{message_id}", response_model=MessageOut)
def read_message(message_id: int):
    db = SessionLocal()
    db_msg = db.query(Message).get(message_id)
    db.close()
    return MessageOut(id=db_msg.id, content=db_msg.content)

# --- Modèle SQLAlchemy pour User ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)

# Créez la table (si elle n’existe pas déjà)
Base.metadata.create_all(bind=engine)

# --- Schémas Pydantic ---
class UserIn(BaseModel):
    firstname: str
    lastname: str
    nickname: Optional[str] = None
    email: EmailStr

class UserOut(UserIn):
    id: int

# --- Endpoints CRUD Users ---

@app.websocket("/ws/users")
async def websocket_users(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # On attend simplement que le client reste connecté
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    await manager.broadcast({
        "action": "create",
        "user": {"id": db_user.id, "firstname": db_user.firstname, "lastname": db_user.lastname, "nickname": db_user.nickname, "email": db_user.email}
    })
    db.close()
    return db_user

@app.get("/users/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    db.close()
    return users

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user_in: UserIn, db: Session = Depends(get_db)):
    # Récupère l'utilisateur existant
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Applique les modifications
    for field, value in user_in.dict().items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    # Diffusion de l'événement
    await manager.broadcast({
        "action": "update",
        "user": {
            "id": db_user.id,
            "firstname": db_user.firstname,
            "lastname": db_user.lastname,
            "nickname": db_user.nickname,
            "email": db_user.email
        }
    })
    return db_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    # Diffusion de l'événement
    await manager.broadcast({
        "action": "delete",
        "user_id": user_id
    })
    return {"ok": True}
