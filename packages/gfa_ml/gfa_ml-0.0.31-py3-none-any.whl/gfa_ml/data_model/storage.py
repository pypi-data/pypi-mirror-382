from pydantic import BaseModel, Field

from gfa_ml.lib.utils import load_yaml
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


class BlobItemList(BaseModel):
    folders: list[str] = Field(..., description="List of folder paths")
    files: list[str] = Field(..., description="List of file paths")


class AzureBlobConfig(BaseModel):
    connection_string: str = Field(
        ..., description="Azure Blob Storage connection string"
    )
    container_name: str = Field(..., description="Name of the blob container")

    @classmethod
    def from_yaml(cls, file_path: str):
        config_data = load_yaml(file_path)
        return cls(**config_data)
