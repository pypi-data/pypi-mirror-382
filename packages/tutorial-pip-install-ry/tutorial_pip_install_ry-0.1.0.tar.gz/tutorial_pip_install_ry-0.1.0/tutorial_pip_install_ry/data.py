import pandas as pd
from sklearn.model_selection import train_test_split
from huggingface_hub import hf_hub_download

def load_data(
    repo_id="RunyaoYu/Tutorial_pip_install_dataset",
    filename="tutorial_dataset.csv",
    download=True
):
    """
    Load training data. If download=True, fetches from Hugging Face dataset repo.
    """
    if download:
        csv_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="dataset")
    else:
        csv_path = filename

    df = pd.read_csv(csv_path)
    X = df.drop(columns=["target"]).values
    y = df["target"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"✅ Loaded dataset from {repo_id} ({df.shape})")
    return X_train, X_test, y_train, y_test
