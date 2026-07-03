# hotelware-backend

FastAPI で実装されたホテル予約システムのバックエンドAPI。

## セットアップ

```bash
uv sync
```

## 開発サーバー起動

```bash
uv run uvicorn main:app --reload
```

起動後、以下でOpenAPI/Swagger UIを確認できます。

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## OpenAPIスキーマの生成

サーバーを起動せずに `openapi.json` を生成できます。

```bash
uv run python scripts/generate_openapi.py
```

出力先を変更する場合は `-o` オプションを指定します。

```bash
uv run python scripts/generate_openapi.py -o path/to/output.json
```
