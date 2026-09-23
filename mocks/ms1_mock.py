"""Mock de MS1 — Pasajeros / Tickets."""
from fastapi import FastAPI

from mocks.data import tickets

app = FastAPI(title="MS1 mock")


@app.get("/health")
def health():
    return {"status": "up", "service": "ms1-mock"}


# MS1 real (Guillermo) sirve /tickets en la raíz. El prefix /api/pasajeros/
# lo agrega el nginx del API Gateway para llamadas externas.
@app.get("/tickets")
def get_tickets(vuelo_id: int):
    return tickets(vuelo_id)
