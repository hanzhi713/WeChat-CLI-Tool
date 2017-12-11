from threading import Thread


class Process(Thread):

    def __init__(self, target=None, args=()):
        super(self.__class__, self).__init__()
        self.target = target
        self.args = args
        self.stopped = False

    def run(self):
        sub_thread = Thread(target=self.target, args=self.args)
        sub_thread.setDaemon(True)
        sub_thread.start()
        while (not self.stopped) and sub_thread.is_alive():
            sub_thread.join(0.5)

    def terminate(self):
        self.stopped = True