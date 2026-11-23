"""Write the OpenAPI spec to stdout, for generating the typed frontend client.

Usage: uv run python -m app.export_openapi > ../frontend/openapi.json
"""

import json
import sys

from app.main import create_app


def main() -> None:
    spec = create_app().openapi()
    json.dump(spec, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
