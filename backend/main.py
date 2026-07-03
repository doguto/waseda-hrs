from fastapi import FastAPI

from routers import cancellation, checkin, checkout, inquiry, reservation

app = FastAPI(title="HRS Backend")

app.include_router(reservation.router)
app.include_router(inquiry.router)
app.include_router(checkin.router)
app.include_router(checkout.router)
app.include_router(cancellation.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
