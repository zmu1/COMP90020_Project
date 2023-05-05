import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from keras.callbacks import LambdaCallback, Callback

############### Preprocessing ##################

data = pd.read_csv('../ml/credit_batch_1.csv')

current_epoch = 0
current_weights = None
current_loss = None
current_accuracy = None

# Split dataset
X = data.drop(['isFraud'], axis=1)
y = data['isFraud']

# Standardization
scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
X_train, y_train = SMOTE(random_state=75).fit_resample(X_train, y_train)


############### Define TF Model ##################

# Define TF Model Layers - DNN
def init_model():
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


# Add training callbacks
def update_current_epoch():
    global current_epoch
    current_epoch += 1


def update_current_weights():
    global current_weights
    current_weights = model.layers[0].get_weights()


def update_current_performance(loss, accuracy):
    global current_loss, current_accuracy
    current_loss = loss
    current_accuracy = accuracy


class CustomCallback(Callback):
    def on_epoch_end(self, batch, logs=None):
        update_current_epoch()
        update_current_weights()
        update_current_performance(logs['loss'], logs['accuracy'])


model = init_model()
model.compile(loss='binary_crossentropy', optimizer='adam', metrics='accuracy')

############### Training TF Model ##################

# Model Training
X_train = np.asarray(X_train).astype(np.float32)
y_train = np.asarray(y_train).astype(np.float32)

X_test = np.asarray(X_test).astype(np.float32)
y_test = np.asarray(y_test).astype(np.float32)

model.fit(X_train, y_train, epochs=50, batch_size=100, callbacks=[CustomCallback()])

############### Model Evaluation ##################
# Model Evaluation
model.evaluate(X_test, y_test)


# Check Local States
def check_local_state():
    print("Current epoch:", current_epoch)
    print("Current weights:", current_weights)
    print("Current loss: {}, accuracy: {}".format(current_loss, current_accuracy))


check_local_state()
