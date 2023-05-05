import threading
import time

from TF.TfModel import Status
from Client.client_send_thread import SendingThread


class TrainingThread(threading.Thread):
    def __init__(self, host, port, client_instance):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.client_instance = client_instance

    def train(self):
        """
        Simulate ML training process
        """
        while True:
            if self.client_instance.model.status == Status.IDLE:
                self.client_instance.model.preprocess_data(self.client_instance.dataset_path)
                self.client_instance.model.train_model()

                if self.client_instance.model.status != Status.COMPLETE:
                    self.send_model_weights()
            elif self.client_instance.model.status == Status.WAITING_FOR_UPDATES:
                print("[Status]: WAITING_FOR_UPDATES")
                time.sleep(3)
            elif self.client_instance.model.status == Status.COMPLETE:
                print("\n[Status]: **COMPLETE**")
                break

    def check_local_state(self):
        epoch = self.client_instance.model.check_current_progress()
        weights = self.client_instance.model.check_current_weights()
        loss, accuracy = self.client_instance.model.check_current_performance()

        return epoch, weights, loss, accuracy

    def send_model_weights(self):
        model_weights = self.client_instance.model.check_current_weights()
        # send_socket_msg(self.server_socket, 'updated_weights', model_weights)

        send_thread = SendingThread(self.host, self.port, self.client_instance, "update_weights", model_weights)
        send_thread.start()

        # print("[Log] Client sent updated weights")

    def run(self):
        self.train()
        # self.client_instance.initialize_snapshot()
