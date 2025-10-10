from typing import Any
from aiogram.types import BufferedInputFile
from aiogram_renderer.thumbnail import Thumbnail
from aiogram_renderer.widgets.text import Text, Area
from aiogram_renderer.widgets.widget import Widget


class FileBytes(Widget):
    __slots__ = ("file_name", "bytes_name", "thumbnail", "media_caption")

    # Укажите caption если хотите видеть в MediaGroup под каждым фото описание
    # В случае отправки File отдельно используйте виджеты Text, Multi
    def __init__(self, file_name: str, bytes_name: str, thumbnail: Thumbnail = None,
                 media_caption: str | Text = None, show_on: str = None):
        """
        Виджет для отправки байтов файла, так как не хранится в памяти - отобразить окно можно будет только один раз
        :param file_name: имя файла
        :param bytes_name: имя поля в file_bytes, где хранятся байты
        :param thumbnail: объект превью Thumbnail
        :param media_caption: описание файла для MediaGroup
        :param show_on: фильтр видимости
        """
        super().__init__(show_on=show_on)
        self.file_name = file_name
        self.bytes_name = bytes_name
        self.thumbnail = thumbnail
        self.media_caption = media_caption

    async def assemble(self, data: dict[str, Any], **kwargs) -> tuple[Any, Any, Any]:
        if not (await self.is_show_on(data)):
            return None, "", None

        file_name = self.file_name

        if isinstance(self.media_caption, (Text, Area)):
            caption_text = await self.media_caption.assemble(data)
        else:
            caption_text = self.media_caption

        # Форматируем по data, если там заданы ключи {key}
        for key, value in data.items():
            # Подставляем значения в имя файла
            if '{' + key + '}' in file_name:
                file_name = file_name.replace('{' + key + '}', str(value))
            # Подставляем значения в описание файла
            if isinstance(caption_text, str) and (caption_text != ""):
                if '{' + key + '}' in caption_text:
                    caption_text = caption_text.replace('{' + key + '}', str(value))

        if self.thumbnail is not None:
            thumbnail_obj = await self.thumbnail.assemble(data=data, kwargs=kwargs)
        else:
            thumbnail_obj = None

        return BufferedInputFile(file=kwargs["file_bytes"][self.bytes_name], filename=file_name), caption_text, thumbnail_obj


class VideoBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, thumbnail: Thumbnail = None, media_caption: str | Text = None,
                 show_on: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name, thumbnail=thumbnail,
                         media_caption=media_caption, show_on=show_on)


class PhotoBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, media_caption: str | Text = None, show_on: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name,
                         media_caption=media_caption, show_on=show_on)


class AudioBytes(FileBytes):
    __slots__ = ()

    def __init__(self, file_name: str, bytes_name: str, thumbnail: Thumbnail = None, media_caption: str | Text = None,
                 show_on: str = None):
        super().__init__(file_name=file_name, bytes_name=bytes_name, thumbnail=thumbnail,
                         media_caption=media_caption, show_on=show_on)
