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

## AI Operations Assistant

Dispatchers can ask plain-English questions about current deliveries
(e.g. "which orders need attention?") and get a short answer generated
from the live order data in the database — it only uses what's actually
in the DB, it won't make things up.

Set these in your `.env` (get a key at https://platform.openai.com/api-keys):

OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

Example questions:
- Which deliveries need attention?
- Which driver has the highest workload?
- Summarize today's deliveries.
- Which orders have been in transit the longest?
- Are there any cancelled deliveries?
- What should the dispatcher prioritize next?

If `OPENAI_API_KEY` is missing, or the key has no quota left, the
assistant card shows a friendly error instead of crashing — the rest
of the dashboard keeps working normally.