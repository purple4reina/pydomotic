import logging

logger = logging.getLogger(__name__)

class Component(object):

    def __init__(self, name, ifs, thens, elses, enabled=True):
        self.name = name or 'unknown'
        self.ifs = ifs
        self.thens = thens
        self.elses = elses
        self.enabled = enabled

    def run(self):
        logger.debug('running component %s', self.name)
        checked = True
        for trigger in self.ifs:
            logger.debug('checking trigger %s', trigger.name)
            if not trigger.check():
                logger.debug('trigger failed')
                checked = False
                break
            logger.debug('trigger passes')

        if checked:
            logger.debug('all triggers passed')
            exception = self._run_actions(self.thens)
        else:
            exception = self._run_actions(self.elses)

        if exception:
            raise exception

    def _run_actions(self, actions):
        exception = None
        for action in actions:
            logger.debug('running action %s', action.name)
            try:
                action.run()
            except Exception as e:
                logger.exception(f'failure running action {action.name}')
                exception = e
        return exception
