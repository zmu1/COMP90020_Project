class ClientState:
    def __init__(self, client):
        # Client config
        self.host = client.host
        self.port = client.port

        # Client local dataset
        self.dataset_path = client.dataset_path

        # Client local tensorflow model
        self.model = client.model

    def check(self):
        print(self.host, self.port)
        print(self.dataset_path)

    def check_model(self):
        print("[Snapshot] Current epoch:", self.model.current_epoch)
        print("[Snapshot] Current loss:", self.model.current_loss)
        print("[Snapshot] Current accuracy:", self.model.current_accuracy)
        # print("[Snapshot] Current weights:", self.model.current_weights)

