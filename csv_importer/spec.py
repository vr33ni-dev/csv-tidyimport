import yaml


def load_spec(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
