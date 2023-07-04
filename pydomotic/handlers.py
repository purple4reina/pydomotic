import logging
import time
import traceback

from .exceptions import PyDomoticComponentRunError
from .parsers import parse_yaml

logger = logging.getLogger(__name__)

class Handler(object):

    def __init__(self, config_file=None):
        self.components, _ = parse_yaml(config_file=config_file)

    def __call__(self):
        self.run_components()

    def run_components(self):
        components, failed = [c for c in self.components if c.enabled], []
        attempts = 3

        while components and attempts:
            attempts -= 1
            for component in components:
                try:
                    component.run()
                except Exception:
                    exc = ''.join(traceback.format_exc())
                    logger.error(
                        f'failure running component {component.name}, '
                        f'{attempts} remaining attempts\n{exc}')
                    failed.append(component)

            if failed and attempts:
                time.sleep(0.25)
            components, failed = failed, []

        if components:
            raise PyDomoticComponentRunError(
                    f'one or more components failed after 3 attempts: '
                    f'{", ".join(c.name for c in components)}')

class LambdaHandler(Handler):

    ok_response = {
            'statusCode': 200,
            'body': '{"status":"ok"}',
    }

    def __init__(self, config_file=None, s3=None):
        self.components, context = parse_yaml(config_file=config_file, s3=s3)
        self.webhook_sensor = context.webhook_sensor

    def __call__(self, event, context):
        # TODO: test webhook triggers
        self.webhook_sensor.set_webhook_request(event)
        self.run_components()
        return self.ok_response

class CommandLineHandler(Handler):

    def __init__(self):
        args = self.parse_args()
        super().__init__(config_file=args.config_file)

    def parse_args(self):
        import argparse
        parser = argparse.ArgumentParser(
                prog='python -m pydomotic',
                description='run pydomotic components',
        )
        parser.add_argument(
                '-c', '--config-file',
                help=('path to config file, will default to pydomotic.yaml '
                        'if no other config setting is found'),
        )
        return parser.parse_args()
