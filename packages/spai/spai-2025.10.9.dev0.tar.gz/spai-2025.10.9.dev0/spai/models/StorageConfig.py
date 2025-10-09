from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class StorageConfig(BaseModel):
    type: str
    name: str


class LocalStorageConfig(StorageConfig):
    path: str

    @field_validator("type")
    @classmethod
    def type_must_be_local(cls, v):
        if not v == "local":
            raise ValueError("type must be local")
        return v

    @model_validator(mode='before')
    @classmethod
    def set_path_from_name_if_not_provided(cls, data):
        # Handle both dict and other input types
        if isinstance(data, dict):
            # If path is not provided or is None, set it to name
            if 'path' not in data or data.get('path') is None:
                if 'name' in data and data['name'] is not None:
                    data['path'] = data['name']
        return data


class S3StorageCredentials(BaseModel):
    url: str
    access_key: str
    secret_key: str
    bucket: str
    region: Optional[str] = (
        None  # en local no hace falta, además afecta a la conexión segura o no
    )


class S3StorageConfig(StorageConfig):
    credentials: Optional[S3StorageCredentials] = None

    @field_validator("type")
    @classmethod
    def type_must_be_s3(cls, v):
        if not v == "s3":
            raise ValueError("type must be s3")
        return v
