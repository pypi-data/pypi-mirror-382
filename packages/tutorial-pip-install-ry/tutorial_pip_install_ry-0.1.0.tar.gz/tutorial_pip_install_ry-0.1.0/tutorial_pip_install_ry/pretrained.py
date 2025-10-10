from huggingface_hub import hf_hub_download

def download_pretrained(
    repo_id="RunyaoYu/Tutorial_pip_install_model",
    filename="mymlp_model.keras"
):
    """
    Download pretrained MLP model from Hugging Face.
    """
    model_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type="model")
    print(f"✅ Pretrained model downloaded to {model_path}")
    return model_path
