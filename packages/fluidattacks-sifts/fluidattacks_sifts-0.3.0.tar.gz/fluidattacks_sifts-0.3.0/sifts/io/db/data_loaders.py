import json
from pathlib import Path

typology_path = Path(__file__).parent.parent.parent / "static" / "typology_embedding.json"
with Path(typology_path).open() as f:
    KNN_DATA: dict[str, list[list[float]]] = json.load(f)
