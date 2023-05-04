import threading
import time


class TrainingThread(threading.Thread):
    def __init__(self, client_instance):
        threading.Thread.__init__(self)
        self.client_instance = client_instance

    def train(self):
        """
        Simulate ML training process
        """
        print("------Training Started------")

        while self.client_instance.foo_var < 5:
            self.client_instance.foo_var += 1
            print("------Training progress: {}------".format(self.client_instance.foo_var))

            time.sleep(1)

    def run(self):
        self.train()
        # self.client_instance.initialize_snapshot()
