"""Generate the OpenAPI schema JSON file from the FastAPI app definition."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402


def generate_openapi_schema(output_path: Path) -> None:
    schema = app.openapi()
    output_path.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"OpenAPI schema written to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "openapi.json",
        help="Output file path (default: backend/openapi.json)",
    )
    args = parser.parse_args()
    generate_openapi_schema(args.output)


if __name__ == "__main__":
    main()
