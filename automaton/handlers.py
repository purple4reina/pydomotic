import collections
import logging
import time

from .exceptions import AutomatonComponentRunError
from .parsers import parse_yaml

logger = logging.getLogger(__name__)

class LambdaHandler(object):

    ok_response = {
            'statusCode': 200,
            'body': '{"status":"ok"}',
    }

    def __init__(self, config_file=None, s3=None):
        self.components, self.webhook_sensor = parse_yaml(
                config_file=config_file, s3=s3)

    def __call__(self, event={}, context={}):
        # TODO: test webhook triggers
        self.webhook_sensor.set_webhook_request(event)
        self.run_components(self.components)
        return self.ok_response

    def run_components(self, components):
        components, failed = [c for c in components if c.enabled], []
        attempts = 3

        while components and attempts:
            attempts -= 1
            for component in components:
                try:
                    component.run()
                except Exception:
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
