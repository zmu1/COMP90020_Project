import pandas as pd
import numpy as np
from enum import Enum

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from keras.callbacks import LambdaCallback

class Status(Enum):
    IDLE = 0
    TRAINING = 1
    WAITING_FOR_UPDATES = 2
    TRAINED = 3

class TfModel:
    def __init__(self):
        # Initialise local value
        self.current_epoch = 0
        self.current_weights = None
        self.current_loss = None
        self.current_accuracy = None

        # Initialise training status
        self.status = Status.IDLE

        # Init dataset
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None

        # Init model
        self.model = self.init_model()

    def preprocess_data(self, file_name):
        data = pd.read_csv(file_name)

        # Split dataset
        X = data.drop(['isFraud'], axis=1)
        y = data['isFraud']

        # Standardization
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
        X_train, y_train = SMOTE(random_state=75).fit_resample(X_train, y_train)

        # Convert types for tensorflow
        self.X_train = np.asarray(X_train).astype(np.float32)
        self.y_train = np.asarray(y_train).astype(np.float32)
        self.X_test = np.asarray(X_test).astype(np.float32)
        self.y_test = np.asarray(y_test).astype(np.float32)

    def init_model(self):
        model = Sequential([
            Dense(input_dim=30, units=128, activation="relu"),
            Dense(units=64, activation="relu"),
            Dropout(0.2),
            Dense(units=32, activation="relu"),
            Dropout(0.2),
            Dense(units=16, activation="relu"),
            Dropout(0.2),
            Dense(units=1, activation="sigmoid")])

        return model

    def train_model(self):
        reset_epoch_callback = LambdaCallback(on_train_begin=lambda batch: self.update_current_epoch(reset=True))
        update_epoch_callback = LambdaCallback(on_epoch_end=lambda batch, logs: self.update_current_epoch())
        update_weights_callback = LambdaCallback(on_epoch_end=lambda batch, logs: self.update_current_weights())
        update_performance_callback = LambdaCallback(
            on_epoch_end=lambda batch, logs: self.update_current_performance(logs['loss'], logs['accuracy']))

        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics='accuracy')

        if self.current_weights is not None:
            self.model.set_weights(self.current_weights)
            print("Train use updated weights")

        self.model.fit(self.X_train, self.y_train, epochs=50, batch_size=100, callbacks=[reset_epoch_callback,
                                                                                          update_epoch_callback,
                                                                                          update_weights_callback,
                                                                                          update_performance_callback])
        # Finish current round of training
        # Waiting for updated model weights
        self.status = Status.WAITING_FOR_UPDATES

    def update_current_epoch(self, reset=False):
        if reset:
            self.current_epoch = 0
        else:
            self.current_epoch += 1

    def update_current_weights(self):
        self.current_weights = self.model.get_weights()

    def update_current_performance(self, loss, accuracy):
        self.current_loss = loss
        self.current_accuracy = accuracy

    def check_current_progress(self):
        return self.current_epoch

    def check_current_weights(self):
        return self.current_weights

    def check_current_performance(self):
        return self.current_loss, self.current_accuracy

    def receive_updated_weights(self, updated_weights):
        self.current_weights = updated_weights
        print("Received updated weights")
