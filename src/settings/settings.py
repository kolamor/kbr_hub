import json
import os
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, validator
import yaml

__all__ = ('load_config', 'Config')


def load_config(config_file=None):
    default_file = Path(__file__).parent / 'config.yaml'
    with open(default_file, 'r') as f:
        config = yaml.safe_load(f)
    cf_dict = {}
    if config_file:
        cf_dict = yaml.safe_load(config_file)
    config.update(**cf_dict)
    env = Config()
    # load env
    for key, val in env.dict().items():
        if val:
            config.update({key: val})
    config = Config.parse_obj(config)
    print(config)
    return config


class Config(BaseModel):
    APP_NAME: Optional[str] = Field(default=os.environ.get('APP_NAME'))
    LOG_LEVEL: Optional[str] = Field(default=os.environ.get('LOG_LEVEL'))
    AUTH_SECRET_KEY: Optional[str] = Field(default=os.environ.get('AUTH_SECRET_KEY'))
    # psql
    POSTGRESQL_DSN: Optional[str] = Field(default=os.environ.get('POSTGRESQL_DSN'))
    POSTGRESQL_DSN_OPTIONS: Optional[dict] = Field(default=os.environ.get('POSTGRESQL_DSN_OPTIONS'))
    POSTGRESQL_ENGINE_PRE: Optional[bool] = Field(default=os.environ.get('POSTGRESQL_ENGINE_PRE'))

    @validator('POSTGRESQL_DSN_OPTIONS', 'RABBITMQ_OTHER_SETTINGS', 'RABBITMQ_OTHER_SETTINGS', pre=True,
               check_fields=False)
    def parse_to_dict(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
