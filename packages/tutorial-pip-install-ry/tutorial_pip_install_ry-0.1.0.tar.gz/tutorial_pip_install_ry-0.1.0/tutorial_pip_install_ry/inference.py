import numpy as np
from tensorflow import keras

def inference(x, model_path="tutorial_mlp_model.keras"):
    model = keras.models.load_model(model_path)
    x = np.array(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    y_pred = model.predict(x)
    return y_pred.flatten().tolist()
