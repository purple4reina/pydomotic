from .parsers import parse_yaml

class LambdaHandler(object):

    def __init__(self, config_file='automaton.yml'):
        self.components = parse_yaml(config_file)

    def __call__(self, event={}, context={}):
        for component in self.components:
            if component.enabled:
                component.run()
