class Component(object):

    def __init__(self, ifs=None, thens=None, elses=None, enabled=True):
        self.ifs = ifs or []
        self.thens = thens or []
        self.elses = elses or []
        self.enabled = enabled

    def run(self):
        checked = True
        for trigger in self.ifs:
            if not trigger.check():
                checked = False
                break
        if checked:
            for action in self.thens:
                action.run()
        else:
            for action in self.elses:
                action.run()

    def __str__(self):
        return (f'<Component ifs={self.ifs} thens={self.thens} '
                f'elses={self.elses} enabled={self.enabled}>')
    __repr__ = __str__
