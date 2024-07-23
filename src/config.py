import os
from omegaconf import OmegaConf
from hydra import initialize, compose


with initialize(version_base="1.2", config_path="../config/"):
    cfg = compose(config_name="config")

if cfg.model.type == "azure":
    env_key = "AZURE_OPENAI_API_KEY"

elif cfg.model.type == "openai":
    env_key = "OPENAI_API_KEY"

elif cfg.model.type == "anthropic":
    env_key = "ANTHROPIC_API_KEY"

elif cfg.model.type == "google":
    env_key = "GOOGLE_API_KEY"


os.environ[env_key] = cfg.model.api_key
model_type = cfg.model.type
model_args = OmegaConf.to_object(cfg.model.args)
