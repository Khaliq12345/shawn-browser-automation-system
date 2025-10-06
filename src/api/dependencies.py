from fastapi import Depends
from src.utils.database import Database
from typing import Annotated

databaseDepends = Annotated[Database, Depends(Database)]
