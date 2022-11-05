import logging

logger = logging.getLogger(__name__)

class Component(object):

    def __init__(self, name=None, ifs=None, thens=None, elses=None, enabled=True):
        self.name = name or 'unknown'
        self.ifs = ifs or []
        self.thens = thens or []
        self.elses = elses or []
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
            for action in self.thens:
                logger.debug('running action %s', action.name)
                action.run()
        else:
            for action in self.elses:
                logger.debug('running action %s', action.name)
                action.run()
