import yaml


def load_yaml_file(file_path: str):
    with open(file_path, "r") as stream:
        return yaml.safe_load(stream)
