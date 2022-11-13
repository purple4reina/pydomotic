import logging
import time

from .exceptions import AutomatonComponentRunError
from .parsers import parse_yaml

logger = logging.getLogger(__name__)

class LambdaHandler(object):

    def __init__(self, config_file=None, s3=None):
        self.components = parse_yaml(config_file=config_file, s3=s3)

    def __call__(self, event={}, context={}):
        components, failed = [c for c in self.components if c.enabled], []
        attempts = 3

        while components and attempts:
            attempts -= 1
            for component in components:
                try:
                    component.run()
                except Exception as e:
                    logger.exception(
                        f'failure running component {component.name}, '
                        f'{attempts} remaining attempts')
                    failed.append(component)

            if failed and attempts:
                time.sleep(0.25)
            components, failed = failed, []

        if components:
            raise AutomatonComponentRunError(
                    f'one or more components failed after 3 attempts: '
                    f'{", ".join(c.name for c in components)}')
