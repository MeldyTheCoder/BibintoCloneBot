from models.database import DatabaseAdapter
from models.repr import ReprModel


class BaseModel(ReprModel):
    def __init__(self, database_adapter: DatabaseAdapter, **options):
        self._database_adapter: DatabaseAdapter = database_adapter
        self._set_attributes(**options)

    def _set_attributes(self, **options):
        for key, val in options.items():
            setattr(self, f"_{self.__class__.__name__}__{key}", val)