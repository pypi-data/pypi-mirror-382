from tensorflow import keras
from tensorflow.keras import layers

def create_mlp(input_dim, hidden_units=64):
    model = keras.Sequential([
        layers.Dense(hidden_units, activation="relu", input_shape=(input_dim,)),
        layers.Dense(hidden_units, activation="relu"),
        layers.Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model
