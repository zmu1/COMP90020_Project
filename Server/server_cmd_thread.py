import threading
from Server.server_send_thread import SendingThread


class CommandThread(threading.Thread):
    def __init__(self, send_port, server_instance):
        threading.Thread.__init__(self, daemon=True)
        self.send_port = send_port
        self.server_instance = server_instance

    def send_command(self, command, content, to_all=True):
        if to_all:
            for worker_ip in self.server_instance.worker_list:
                send_thread = SendingThread(worker_ip, self.send_port, self.server_instance, command, content)
                send_thread.start()
                send_thread.join()

    def handle_user_command(self):
        while True:
            user_input = input()

            if user_input == 'snapshot':
                print("\n[User command]: snapshot")
                self.send_command("marker", "Record your local state")

            elif user_input == 'finish':
                print("\n[User command]: stop training")
                self.send_command(user_input, "Stop Training")

            else:
                print("\n[User command]: Unrecognised user command")

    def run(self):
        self.handle_user_command()
