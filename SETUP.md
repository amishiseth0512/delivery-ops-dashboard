## What this is

A delivery ops dashboard I built to learn full-stack development. 
Dispatchers can create orders, assign them to drivers, and reassign 
them if needed. Drivers log in and see only their own orders and 
update the status as they go. Stack: React + TypeScript frontend, 
Python FastAPI backend, PostgreSQL.

## Running locally

You'll need Python 3.9+, Node.js, and PostgreSQL installed.

**Backend:**

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload


**Frontend:**

cd frontend
npm install
npm run dev


Open http://localhost:5173 — log in as a dispatcher to manage all 
orders, or as a driver to see your assigned ones.

**Tests:**
pytest tests/