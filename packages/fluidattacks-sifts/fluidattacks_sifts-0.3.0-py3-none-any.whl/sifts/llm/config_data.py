from pathlib import Path

import yaml

from sifts.llm.types import ModelParameters

model_path = Path(__file__).parent.parent / "static" / "model_parameters.yaml"

with Path(model_path).open() as reader:
    MODEL_PARAMETERS: ModelParameters = yaml.safe_load(reader.read())

TOP_FINDINGS = MODEL_PARAMETERS["top_findings"]
