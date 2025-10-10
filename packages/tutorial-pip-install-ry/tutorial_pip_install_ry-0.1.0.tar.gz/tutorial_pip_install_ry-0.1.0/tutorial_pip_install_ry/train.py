import os
from .model import create_mlp

def train_model(data, epochs=20, batch_size=32, save_path="tutorial_mlp_model.keras"):
    X_train, X_test, y_train, y_test = data
    model = create_mlp(X_train.shape[1])
    model.fit(X_train, y_train,
              validation_data=(X_test, y_test),
              epochs=epochs, batch_size=batch_size, verbose=1)
    model.save(save_path)
    print(f"✅ Model saved to {os.path.abspath(save_path)}")
    return model
