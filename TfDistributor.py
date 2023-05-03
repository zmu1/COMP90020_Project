import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, Average


class TfDistributor:
    def __init__(self):
        self.latest_model_weights = None
        self.collected_weights = []

        self.total_clients = None

    def set_total_clients(self, num):
        self.total_clients = num

    def check_collected_num(self):
        return len(self.collected_weights)

    def collect_model_weights(self, weights):
        self.collected_weights.append(weights)

        collected_num = self.check_collected_num()
        print("Successfully collected model weights, existing weights count:", collected_num)
        # print(weights)

        if collected_num == self.total_clients:
            print("All client models have been collected, ready to merge...")
        else:
            print("Models collected: {}, waiting for other {} clients"
                  .format(collected_num, self.total_clients - collected_num))

    # def get_base_model(self):
    #     model = Sequential([
    #         Dense(input_dim=30, units=128, activation="relu"),
    #         Dense(units=64, activation="relu"),
    #         Dropout(0.2),
    #         Dense(units=32, activation="relu"),
    #         Dropout(0.2),
    #         Dense(units=16, activation="relu"),
    #         Dropout(0.2),
    #         Dense(units=1, activation="sigmoid")])
    #     return model

    def integrate_model_weights(self):
        # collected_models = []
        # for weights in self.collected_weights:
        #     model = self.get_base_model()
        #     model.set_weights(weights)
        #     collected_models.append(model)

        merged_weights = Average()(self.collected_weights)
        self.latest_model_weights = merged_weights

        # updated_model = self.get_base_model()
        # updated_model.set_weights(merged_weights)

        print("Merged model weights:", merged_weights)

        return self.latest_model_weights
