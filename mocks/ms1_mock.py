"""Mock de MS1 — Pasajeros / Tickets."""
from fastapi import FastAPI

from mocks.data import tickets

app = FastAPI(title="MS1 mock")


@app.get("/health")
def health():
    return {"status": "up", "service": "ms1-mock"}


@app.get("/api/pasajeros/tickets")
def get_tickets(vuelo_id: int):
    return tickets(vuelo_id)
