from pydantic import BaseModel
from typing import Dict, Any


class DBConfigs(BaseModel):
    """
    Configurations related to database connection.
    """

    db_uri: str
    pool_size: int | None = 10
    max_overflow: int | None = 20
    pool_timeout: int | None = 30
    pool_recycle: int | None = 1800
    other_engine_configs: Dict[str, Any] | None = None
