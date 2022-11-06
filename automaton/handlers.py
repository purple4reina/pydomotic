from .parsers import parse_yaml

class LambdaHandler(object):

    def __init__(self, config_file=None, s3=None):
        self.components = parse_yaml(config_file=config_file, s3=s3)

    def __call__(self, event={}, context={}):
        for component in self.components:
            if component.enabled:
                component.run()
