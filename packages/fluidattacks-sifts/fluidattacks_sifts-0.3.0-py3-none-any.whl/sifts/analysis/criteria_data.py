import requests
import yaml

from sifts.config.settings import YAML_PATH_REQUIREMENTS, YAML_PATH_VULNERABILITIES

if not YAML_PATH_VULNERABILITIES.exists():
    response = requests.get(
        (
            "https://raw.githubusercontent.com/fluidattacks/universe"
            "/2bc45ef13abe49d58f7f78baefa8f8676601e2a7/defines/src/vulnerabilities/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_VULNERABILITIES.write_text(response.text)

if not YAML_PATH_REQUIREMENTS.exists():
    response = requests.get(
        (
            "https://raw.githubusercontent.com/fluidattacks/universe"
            "/2bc45ef13abe49d58f7f78baefa8f8676601e2a7/defines/src/requirements/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_REQUIREMENTS.write_text(response.text)

try:
    DEFINES_VULNERABILITIES: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(
        YAML_PATH_VULNERABILITIES.read_text(),
    )
except yaml.YAMLError:
    # The local file may be corrupted (e.g. HTML error page). Re-download it and try again.
    response = requests.get(
        (
            "https://raw.githubusercontent.com/fluidattacks/universe"
            "/2bc45ef13abe49d58f7f78baefa8f8676601e2a7/defines/src/vulnerabilities/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_VULNERABILITIES.write_text(response.text)
    DEFINES_VULNERABILITIES = yaml.safe_load(response.text)

try:
    DEFINES_REQUIREMENTS: dict[str, dict[str, dict[str, str]]] = yaml.safe_load(
        YAML_PATH_REQUIREMENTS.read_text(),
    )
except yaml.YAMLError:
    response = requests.get(
        (
            "https://raw.githubusercontent.com/fluidattacks/universe"
            "/2bc45ef13abe49d58f7f78baefa8f8676601e2a7/defines/src/requirements/data.yaml"
        ),
        timeout=30,
    )
    YAML_PATH_REQUIREMENTS.write_text(response.text)
    DEFINES_REQUIREMENTS = yaml.safe_load(response.text)
