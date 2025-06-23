# hello-docker

A minimal **full-stack** example project:

* **Frontend**: React (TypeScript) + Vite
* **Backend**: FastAPI (Python)
* **Database**: PostgreSQL (local, via Docker Compose)
* **Real-time updates**: WebSockets for CRUD events on the `users` table

---

## 🚀 Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v4+)
* [Node.js](https://nodejs.org/) (v18+) & [npm](https://www.npmjs.com/) (or [pnpm](https://pnpm.io/))

---

## 📥 Installation (from scratch)

1. **Clone this repository**

   ```bash
   git clone git@github.com:zygopter/Hello-Docker.git
   cd Hello-Docker
   ```

2. **Start the entire stack**

   ```bash
   docker-compose up --build
   ```

   * PostgreSQL → port **5432**
   * FastAPI → port **8000**, Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)
   * Vite (React) → port **4173**, UI at [http://localhost:4173](http://localhost:4173)

3. **(Optional) Frontend local development**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The frontend will connect to the API using `VITE_API_URL` defined in `frontend/.env`.

---

## 🛠️ Environment Variables

* **backend/.env**

  ```dotenv
  DATABASE_URL=postgresql://user:password@db:5432/hello_db
  ```

* **frontend/.env**

  ```dotenv
  VITE_API_URL=http://localhost:8000
  VITE_WS_URL=ws://localhost:8000/ws/users
  ```

Docker Compose will automatically load `backend/.env` if you add:

```yaml
services:
  backend:
    env_file:
      - ./backend/.env
```

---

## 🔧 Project Structure

```
hello-docker/
├─ backend/
│  ├─ Dockerfile
│  ├─ main.py
│  ├─ requirements.txt
│  ├─ requirements-dev.txt
│  └─ tests/             ← Pytest suite (uses in-memory SQLite)
├─ frontend/
│  ├─ Dockerfile
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  ├─ public/
│  └─ src/
│     ├─ App.tsx
│     ├─ types.ts
│     └─ components/
│        └─ Users.tsx
├─ docker-compose.yml
├─ .gitignore
└─ README.md
```

---

## 🧪 Running Backend Tests

The backend tests use an in-memory SQLite database to avoid affecting your local Postgres.

```bash
cd backend
export PYTHONPATH="$PWD"
pytest -q
```

---

## 🎉 Usage

* **Create / Read / Update / Delete** users via the REST API or the React UI.
* Watch the table update in real time using WebSockets.

---

## 📄 License

MIT © [Marine Chamoux](https://github.com/zygopter)
