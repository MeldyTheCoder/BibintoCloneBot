from models.base import BaseModel

class PhotoModel(BaseModel):
    __photo_id: str = ''

    @property
    def photo_id(self):
        return self.__photo_id

    @property
    def get_photo(self):
        return lambda bot: (await bot.get_file(self.__photo_id))