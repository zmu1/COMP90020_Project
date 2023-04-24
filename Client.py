from client import client_comm_thread
import time


class Client:
    def __init__(self):
        self.foo_var = 0
        self.comm_thread = client_comm_thread.ClientCommThread()

    def train(self):
        for i in range(60):
            self.foo_var += 1
            print(self.foo_var)

            # Pass value to the comm Thread
            self.comm_thread.foo_var = self.foo_var
            time.sleep(1)

    def run(self):
        self.comm_thread.start()
        self.train()


client = Client()
client.run()
