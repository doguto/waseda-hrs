from fastapi import FastAPI

from api.api.reservations import router as reservation_router


def create_app() -> FastAPI:
    app = FastAPI(title="HRS API", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(reservation_router)

    return app


app = create_app()
