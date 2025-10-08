from ..engine.database_engine import DatabaseEngine as DatabaseEngine
from ..logger.logging_ import logging as logging

class DatabaseChecker:
    @staticmethod
    async def metadata_to_database(source_metadata, engine_name, auto_create: bool = True): ...
