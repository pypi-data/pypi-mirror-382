import os
from pathlib import Path

from platformdirs import user_data_dir

DATA_DIR = user_data_dir("sifts", ensure_exists=True)


FI_AWS_OPENSEARCH_HOST = os.environ.get("AWS_OPENSEARCH_HOST", "https://localhost:9200")


FI_AWS_REGION_NAME = "us-east-1"


FI_ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")


YAML_PATH_VULNERABILITIES = Path(DATA_DIR, "vulnerabilities.yaml")
YAML_PATH_REQUIREMENTS = Path(DATA_DIR, "requirements.yaml")
