from .parsers import parse_yaml

class LambdaHandler(object):

    def __init__(self, config_file='automaton.yml'):
        if config_file:
            self.components = parse_yaml(config_file)
        else:
            self.components = []

    def __call__(self, event={}, context={}):
        for component in self.components:
            if component.enabled:
                component.run()
