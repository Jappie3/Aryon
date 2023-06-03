import yaml

with open("src/config.yaml", "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
