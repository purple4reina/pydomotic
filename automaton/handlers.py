import collections
import logging
import time

from .exceptions import AutomatonComponentRunError, AutomatonWebhookError
from .parsers import parse_yaml, register_webhooks

logger = logging.getLogger(__name__)

class _Handler(object):

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

class LambdaHandler(_Handler):

    def __init__(self, config_file=None, s3=None):
        self.components = parse_yaml(config_file=config_file, s3=s3)

    def __call__(self, event={}, context={}):
        self.run_components(self.components)

class WebhookHandler(_Handler):

    forbidden_response = {
            'statusCode': 403,
            'errorMessage': 'forbidden',
    }
    not_found_response = {
            'statusCode': 404,
            'errorMessage': 'not found',
    }
    ok_response = {
            'statusCode': 200,
            'body': '{"status":"ok"}',
    }

    def __init__(self, config_file=None, s3=None, authorize=None):
        self.webhooks = register_webhooks(config_file=config_file, s3=s3)
        # TODO: test authorization
        self.authorize = authorize

    def __call__(self, event={}, context={}):
        # TODO: test __call__
        request = self.WebhookRequest.from_event(event)
        if self.authorize and not self.authorize(request.headers):
            return self.forbidden_response
        if request.method != 'POST':
            return self.not_found_response
        components = self.webhooks.get(request.path)
        if components is None:
            return self.not_found_response
        self.run_components(components)
        return self.ok_response

    class WebhookRequest(collections.namedtuple('Request',
            ('method', 'path', 'headers'))):

        @classmethod
        def from_event(cls, event):
            try:
                # TODO: test from_event
                http = event.get('requestContext', {}).get('http')
                return cls(
                        method=http.get('method'),
                        path=http.get('path'),
                        headers=event.get('headers'),
                )
            except Exception as e:
                raise AutomatonWebhookError('Unable to read request: '
                        f'[{e.__class__.__name__}] {e}')
