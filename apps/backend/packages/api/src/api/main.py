from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api.reservations import router as reservation_router
from api.api.room_types import router as room_type_router


def create_app() -> FastAPI:
    app = FastAPI(title="HRS API", version="0.1.0")

    # デモ用フロントエンド(別オリジンのSPA)からの呼び出しを許可する。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(reservation_router)
    app.include_router(room_type_router)

    return app


app = create_app()
