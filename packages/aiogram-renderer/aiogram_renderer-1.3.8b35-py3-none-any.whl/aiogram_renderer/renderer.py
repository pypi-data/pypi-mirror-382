from datetime import datetime, timedelta
from typing import Any
from aiogram.client.default import Default
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument, Update
from .bot_mode import BotModes
from aiogram_renderer.components.enums import RenderMode
from .widgets.inline.panel import DynamicPanel
from .widgets.media.bytes import FileBytes, AudioBytes, VideoBytes, PhotoBytes
from .widgets.media.file_id import FileID, PhotoID, VideoID, AudioID
from .widgets.media.path import File, Audio, Video, Photo
from .widgets.media.url import AudioUrl, PhotoUrl, VideoUrl, FileUrl
from .window import Window, Alert


class Renderer:
    __slots__ = ('event', 'bot', 'windows', 'fsm', 'bot_modes', 'progress_updates')

    def __init__(self, event: Update, windows: list[Window], fsm: FSMContext = None, bot_modes: BotModes = None):
        self.event = event
        self.bot = event.bot
        self.windows = windows
        self.fsm = fsm
        self.bot_modes = bot_modes
        self.progress_updates = {}

    async def __sync_modes(self, fsm_data: dict[str, Any]) -> dict[str, Any]:
        """
        Метод для синхронизации режимов бота, все режимы проверяются на валидность
        :param fsm_data: FSM данные пользователя
        :return:
        """
        # Синхронизируем режимы (если режимы в боте не указаны мы убираем их из fsm)
        if (self.bot_modes is None) and ("__modes__" in fsm_data):
            fsm_data.pop("__modes__")
        elif (self.bot_modes is None) and ("__modes__" not in fsm_data):
            pass
        # В другом случае синхронизируем их
        else:
            fsm_data = await self.bot_modes.sync_modes(fsm_data)
        return fsm_data

    @staticmethod
    async def __sync_dpanels(fsm_data: dict[str, Any], data: dict[str, Any], window: Window) -> Any:
        """
        Метод для синхронизации данных динамических групп виджетов DynamicPanel с данными,
        переданными в метод render
        :param fsm_data: FSM данные пользователя
        :param data: данные переданные в render
        :param window: объект Window
        :return:
        """
        # Синхронизируем данные DynamicPanel (создаем поле __dpanels__ и помещаем туда новые данные DynamicPanel)
        for widget in window._widgets:
            if isinstance(widget, DynamicPanel):
                if "__dpanels__" not in fsm_data.keys():
                    fsm_data["__dpanels__"] = {}
                if data is not None:
                    if widget.name in data.keys():
                        fsm_data["__dpanels__"][widget.name] = data[widget.name]
        return fsm_data

    async def __sync_data(self, window: Window, data: dict) -> tuple[Any, dict[str, Any]]:
        """
        Метод для синхронизации данных переданных в метод render и FSM данных пользователя,
        синхронизируются данные окна, режимы и другие данные для специальных виджетов
        :param window: объект Window
        :param data: данные переданные в renderer
        :return:
        """
        fsm_data = await self.fsm.get_data()

        # В стейтах бота данные окон хранятся в fsm, в следующем формате
        # Словарь со стейтами окон задается в порядке их открытия, в каждом из них содержатся данные окна
        # '__windows__': {'State.step1': {'btn_text': 'default'...}, 'State.step2': {'btn_text': 'default2'...}...}
        state = window._state.state

        # Если окна есть в fsm
        if "__windows__" in fsm_data.keys():
            # Если окно присутствует в fsm и есть data, то выполняем merge, заменяя и дополняя данные
            if (state in fsm_data["__windows__"]) and (data is not None):
                fsm_data["__windows__"][state] |= data
            # Если окна нет в fsm и есть data, то сохраняем окно с заданной data
            elif (state not in fsm_data["__windows__"]) and (data is not None):
                fsm_data["__windows__"][state] = data
            # Если окна нет в fsm и нет data, то сохраняем окно с пустым data
            elif (state not in fsm_data["__windows__"]) and (data is None):
                fsm_data["__windows__"][state] = {}

        # Если окна нет в fsm, то создаем словарь __windows__ и добавляем туда окно с данными
        else:
            fsm_data["__windows__"] = {state: data} if data is not None else {state: {}}

        window_data = fsm_data["__windows__"][state]

        # Синхронизируем режимы
        fsm_data = await self.__sync_modes(fsm_data)

        # Синхронизируем DynamicPanel виджеты
        fsm_data = await self.__sync_dpanels(fsm_data=fsm_data, data=data, window=window)

        # Перезаписываем fsm
        await self.fsm.set_data(fsm_data)

        return window_data, fsm_data

    async def __get_window_by_state(self, state: str) -> Window | None:
        """
        Функция для получения объекта окна по FSM State, окна задаются в configure_renderer
        :param state: FSM State
        :return:
        """
        for i, window in enumerate(self.windows, start=1):
            if window._state == state:
                return window
            assert i != len(self.windows), ValueError("Окно не за задано в конфигурации")
        return None

    async def _switch_dynamic_panel_page(self, name: str, page: int):
        """
        Метод для переключения страницы группы - виджета DynamicPanel
        :param name: название группы, задается в виджете
        :param page: страница, на которую надо переключить
        """
        fsm_data = await self.fsm.get_data()
        # Устанавливаем новую активную страницу в группе
        fsm_data["__dpanels__"][name]["page"] = page
        await self.fsm.set_data(fsm_data)

    async def get_window_data(self, window: str | Window) -> dict[str, Any]:
        """
        Метод для получения данных окна из FSM
        :param window: параметр State.state или объект Alert | Window
        """
        # Проверяем есть ли стейт в заданных окнах
        if isinstance(window, str):
            window = await self.__get_window_by_state(window)

        # Форматируем имя параметра окна
        fsm_data = await self.fsm.get_data()
        w_param_name = window._state.state.replace(".", ":")
        return fsm_data["__windows__"][w_param_name]

    async def set_window_data(self, window: str | Window, data: dict[str, Any]) -> None:
        """
        Метод для перезаписи данных окна из FSM
        :param window: параметр State.state или объект Alert | Window
        :param data: новые данные окна
        """
        # Проверяем есть ли стейт в заданных окнах
        if isinstance(window, str):
            window = await self.__get_window_by_state(window)

        # Форматируем имя параметра окна
        w_param_name = window._state.state.replace(".", ":")
        await self.fsm.update_data({"__windows__": {w_param_name: data}})

    async def update_progress(self, window: str | Alert | Window, name: str, percent: float, event: Update = None,
                              data: dict[str, Any] = None, chat_id: int = None, message_id: int = None,
                              interval: float = 0.5) -> Message | None | TelegramBadRequest:
        """
        Метод для обновления прогресс бара, не рекомендуется ставить интервал ниже 0.5, исходя из ограничений
        EditMessageText Telegram.
        :param window: параметр State.state или объект Alert | Window
        :param name: название прогресс бара, указано в виджете
        :param percent: новый процент для прогресс бара
        :param event: Update бота
        :param data: данные окна
        :param chat_id: id чата
        :param message_id: id сообщения
        :param interval: интервал обновления в секундах, если функция будет вызвана раньше она не выполнится
        :return:
        """

        # Первым в приоритете event объект
        if event is not None:
            try:
                message_id = event.message_id
                chat_id = event.chat_id
            except:
                message_id = event.message.message_id
                chat_id = event.message.chat.id
        else:
            if (message_id is None) or (chat_id is None):
                raise ValueError("Нужно указать оба параметра: message_id, chat_id")

        # Если передан стейт, находим по нему нужное окно
        if not isinstance(window, (Alert, Window)):
            window = await self.__get_window_by_state(state=window)

        # Если название прогресс бара не указано в Renderer добавляем
        if name not in self.progress_updates:
            self.progress_updates[name] = datetime.now()

        # Если последнее обновление прогресс бара задано в Renderer задаем новую границу для него
        elif datetime.now() > (self.progress_updates[name] + timedelta(seconds=interval)):
            self.progress_updates[name] = datetime.now() + timedelta(seconds=interval)

        # Если таймер еще не закончился и вызов не попал в интервал, выходим из функции
        else:
            return

        # Указываем новый процент для параметра с прогресс баром
        data[name] = percent

        # Пересобираем текст сообщения с обновленным прогресс баром
        file, new_text, keyboard = await window.assemble(data=data, modes={}, dpanels={})

        try:
            return await self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text,
                                                    reply_markup=keyboard)
        except TelegramBadRequest as e:
            if "message to edit not found" in str(e):
                return await self.bot.send_message(chat_id=chat_id, text=new_text, reply_markup=keyboard)
            else:
                return e

    async def __render_media(self, file: File | FileBytes | FileUrl | FileID, data: dict[str, Any], text: str,
                             chat_id: int, message_id: int = None, mode: str = RenderMode.ANSWER,
                             reply_markup: Any = None, file_bytes: dict[str, bytes] = None) -> Message | None:
        """
        Метод рендеринга сообщения с медиа файлом
        :param file: виджет с файлом
        :param data: данные окна
        :param chat_id: id чата
        :param data: данные для передачи в окно
        :param message_id: id сообщения
        :param mode: режим рендеринга
        :param file_bytes: словарь с байтами файл(а|ов)
        :return:
        """
        # По умолчанию берем тот текст, что задан в виджетах окна, media_caption будет использоваться для
        # медиа групп
        file_obj, caption_text, thumbnail = await file.assemble(data=data, file_bytes=file_bytes)
        message = None

        if mode == RenderMode.EDIT or mode == RenderMode.EDIT_OR_ANSWER:
            if isinstance(file, (Photo, PhotoBytes, PhotoUrl, PhotoID)):
                input_media = InputMediaPhoto(media=file_obj, caption=text)
            elif isinstance(file, (Video, VideoBytes, VideoUrl, VideoID)):
                input_media = InputMediaVideo(media=file_obj, caption=text, supports_streaming=True,
                                              thumbnail=thumbnail)
            elif isinstance(file, (Audio, AudioBytes, AudioUrl, AudioID)):
                input_media = InputMediaAudio(media=file_obj, caption=text)
            else:
                input_media = InputMediaDocument(media=file_obj, caption=text, thumbnail=thumbnail)
            try:
                message = await self.bot.edit_message_media(chat_id=chat_id, message_id=message_id,
                                                            reply_markup=reply_markup, media=input_media)
                return message

            # Если нет медиафайла пропускаем ошибку
            except Exception:
                if mode == RenderMode.EDIT:
                    return message

        # Если режим DELETE_AND_SEND - удаляем сообщение
        if mode == RenderMode.DELETE_AND_SEND:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)

        # Если режим не REPLY - удаляем id REPLY сообщения
        if mode != RenderMode.REPLY:
            message_id = None

        # В режимах ANSWER, REPLY, EDIT_OR_ANSWER - отправляем сообщение с media
        if isinstance(file, (Photo, PhotoBytes, PhotoUrl, PhotoID)):
            message = await self.bot.send_photo(chat_id=chat_id, photo=file_obj, caption=text,
                                                reply_to_message_id=message_id, reply_markup=reply_markup)
        elif isinstance(file, (Video, VideoBytes, VideoUrl, VideoID)):
            message = await self.bot.send_video(chat_id=chat_id, video=file_obj, caption=text,
                                                supports_streaming=True, reply_to_message_id=message_id,
                                                reply_markup=reply_markup, thumbnail=thumbnail)
        elif isinstance(file, (Audio, AudioBytes, AudioUrl, AudioID)):
            message = await self.bot.send_audio(chat_id=chat_id, audio=file_obj, caption=text, thumbnail=thumbnail,
                                                reply_to_message_id=message_id, reply_markup=reply_markup)
        else:
            message = await self.bot.send_document(chat_id=chat_id, document=file_obj, caption=text,
                                                   reply_to_message_id=message_id,
                                                   reply_markup=reply_markup, thumbnail=thumbnail)

        return message

    async def render(self,
                     window: str | Alert | Window,
                     event: Update = None,
                     chat_id: int = None,
                     message_id: int = None,
                     data: dict[str, Any] = None,
                     mode: str = RenderMode.ANSWER,
                     parse_mode: str = Default("parse_mode"),
                     file_bytes: dict[str, bytes] = None) -> tuple[Message | None, Window]:
        """
        Основной метод для преобразования окна в сообщение Telegram
        :param window: параметр State.state или объект Alert | Window
        :param event: Update бота
        :param chat_id: id чата
        :param data: данные для передачи в окно
        :param message_id: id сообщения
        :param mode: режим рендеринга
        :param parse_mode: режим парсинга
        :param file_bytes: словарь с байтами файл(а|ов)
        :return:
        """

        # Первым в приоритете event объекта Renderer
        if (event is None) and (chat_id is None) and (message_id is None):
            try:
                message_id = self.event.message.message_id
                chat_id = self.event.message.chat.id
            except:
                message_id = self.event.callback_query.message.message_id
                chat_id = self.event.callback_query.message.chat.id

        # Вторым в приоритете идет event, указанный в renderer
        elif event is not None:
            if isinstance(event, Message):
                message_id = event.message_id
                chat_id = event.chat.id
            else:
                message_id = event.message.message_id
                chat_id = event.message.chat.id

        # Третьим идут message_id и chat_id
        else:
            if (chat_id is None) and (mode == RenderMode.ANSWER):
                raise ValueError("Для отправки сообщения нужно указать chat_id")
            elif (chat_id is not None) and (mode == RenderMode.ANSWER):
                pass
            elif (chat_id is None) or (message_id is None):
                raise ValueError("Нужно указать оба параметра: message_id, chat_id")

        if message_id is None:
            assert mode != RenderMode.REPLY, ValueError("message_id обязателен в REPLY режиме")
            assert mode != RenderMode.DELETE_AND_SEND, ValueError("message_id обязателен в режиме DELETE_AND_SEND")

        if isinstance(window, Alert):
            fsm_data = await self.fsm.get_data()
            # Синхронизируем режимы
            fsm_data = await self.__sync_modes(fsm_data=fsm_data)
            await self.fsm.set_data(fsm_data)
            window_data = data if data is not None else {}
        else:
            # Если передали Window берем state из него
            if isinstance(window, Window):
                state = window._state
            else:
                state = window
                window = await self.__get_window_by_state(state=state)

            await self.fsm.set_state(state=state)

            # Синхронизируем данные окна
            window_data, fsm_data = await self.__sync_data(window=window, data=data)

        # Собираем и форматируем клавиатуру и текст
        modes = fsm_data["__modes__"] if "__modes__" in fsm_data else {}
        dpanels = fsm_data["__dpanels__"] if "__dpanels__" in fsm_data else {}
        file, text, reply_markup = await window.assemble(data=window_data, modes=modes, dpanels=dpanels)
        # Проверяем прикреплен ли файл к окну
        if file is not None:
            return await self.__render_media(file=file, data=window_data, text=text, reply_markup=reply_markup,
                                             chat_id=chat_id, message_id=message_id,
                                             mode=mode, file_bytes=file_bytes), window

        # Елси не прикреплен, выбираем тип отправки сообщения
        if mode == RenderMode.REPLY:
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode, reply_to_message_id=message_id,
                                                  disable_web_page_preview=window.disable_web_page_preview)

        elif mode == RenderMode.DELETE_AND_SEND:
            try:
                await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except TelegramBadRequest:
                pass
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode,
                                                  disable_web_page_preview=window.disable_web_page_preview)

        elif mode == RenderMode.EDIT:
            message = await self.bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id,
                                                       reply_markup=reply_markup, parse_mode=parse_mode,
                                                       disable_web_page_preview=window.disable_web_page_preview)

        elif mode == RenderMode.EDIT_OR_ANSWER:
            try:
                message = await self.bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id,
                                                           reply_markup=reply_markup, parse_mode=parse_mode,
                                                           disable_web_page_preview=window.disable_web_page_preview)
            except:
                message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                      parse_mode=parse_mode,
                                                      disable_web_page_preview=window.disable_web_page_preview)

        # RenderMode.ANSWER в других случаях
        else:
            message = await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup,
                                                  parse_mode=parse_mode,
                                                  disable_web_page_preview=window.disable_web_page_preview)

        return message, window

    async def answer(self, window: str | Alert | Window, event: Update = None, chat_id: int = None,
                     data: dict[str, Any] = None, parse_mode: ParseMode = Default("parse_mode"),
                     file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, event=event, chat_id=chat_id, message_id=None,
                                 parse_mode=parse_mode, mode=RenderMode.ANSWER,
                                 data=data, file_bytes=file_bytes)

    async def edit(self, window: str | Alert | Window, event: Update = None, chat_id: int = None,
                   message_id: int = None, data: dict[str, Any] = None, parse_mode: ParseMode = Default("parse_mode"),
                   file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, event=event, chat_id=chat_id, message_id=message_id,
                                 parse_mode=parse_mode, mode=RenderMode.EDIT, data=data, file_bytes=file_bytes)

    async def edit_or_answer(self, window: str | Alert | Window, event: Update = None, chat_id: int = None,
                             message_id: int = None, data: dict[str, Any] = None,
                             parse_mode: ParseMode = Default("parse_mode"),
                             file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, event=event, chat_id=chat_id, message_id=message_id,
                                 parse_mode=parse_mode, mode=RenderMode.EDIT_OR_ANSWER, data=data, file_bytes=file_bytes)

    async def delete_and_send(self, window: str | Alert | Window, event: Update = None, chat_id: int = None,
                              message_id: int = None, data: dict[str, Any] = None,
                              parse_mode: ParseMode = Default("parse_mode"),
                              file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, event=event, chat_id=chat_id, message_id=message_id,
                                 parse_mode=parse_mode, mode=RenderMode.DELETE_AND_SEND,
                                 data=data, file_bytes=file_bytes)

    async def reply(self, window: str | Alert | Window, event: Update = None, chat_id: int = None,
                    message_id: int = None, data: dict[str, Any] = None, parse_mode: ParseMode = Default("parse_mode"),
                    file_bytes: dict[str, bytes] = None) -> tuple[Message, Window]:
        return await self.render(window=window, event=event, chat_id=chat_id, message_id=message_id,
                                 parse_mode=parse_mode, mode=RenderMode.REPLY, data=data, file_bytes=file_bytes)
