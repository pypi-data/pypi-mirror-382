from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mlflow_experiment_name: str
    mlflow_experiment_path: str
    mlflow_artifact_path: str
    mlflow_tracking_uri: str

    databricks_host: str
    databricks_token: str

    model_config = SettingsConfigDict(extra="allow", env_file=find_dotenv())


settings = Settings()
