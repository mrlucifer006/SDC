# Development Guide

Welcome to **The Siege of the Five Gates CTF** project! This guide will help you set up and run the platform locally for development.

## Prerequisites
Before you start, ensure you have the following installed on your machine:
- **Python 3.8+** (for the FastAPI backend)
- **Node.js 18+ & npm** (for the React/Vite frontend)
- **PostgreSQL** (or a local database if you're not using Docker)
- **Judge0** (required for code execution evaluation, configurable via backend environment variables)

---

## 1. Running the Backend

The backend is built using FastAPI and SQLModel.

### Setup Virtual Environment
First, navigate to the project root and create a Python virtual environment:
```powershell
python -m venv venv
```

### Activate the Environment
* On Windows (Powershell):
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Install Dependencies
Install the required packages from `backend/requirements.txt`:
```powershell
pip install -r backend/requirements.txt
```

### Start the Server
Start the FastAPI server using Uvicorn with hot-reloading enabled:
```powershell
uvicorn backend.main:app --reload
```
*The backend will be available at: [http://localhost:8000](http://localhost:8000)*
*API Documentation (Swagger UI) is automatically available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

> [!NOTE]
> The database will automatically initialize and seed the 5 gates upon startup if the database is empty.

---

## 2. Running the Frontend

The frontend is a React application built with Vite and TailwindCSS.

### Navigate to the Frontend Directory
```powershell
cd frontend
```

### Install Dependencies
Install all Node.js dependencies using npm:
```powershell
npm install
```

### Start the Development Server
Run the Vite development server:
```powershell
npm run dev
```
*The frontend will be available at: [http://localhost:5173](http://localhost:5173)*

---

## 3. Testing the Application
1. Open your browser to `http://localhost:5173`.
2. Click **Login** and navigate to the **Register** page to create a new user account.
3. Authenticate with your new credentials.
4. Try solving **Gate of Caesar (Gate 1)** to verify Judge0 code execution is working properly.
5. To test Admin functionalities, you must set `is_admin=True` for your user in the database, then access the "Command Center" dashboard.
