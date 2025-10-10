import yaml

class YAMLParser:
    def parse(self, data):
        return yaml.safe_load(data)
