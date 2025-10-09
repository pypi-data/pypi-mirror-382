"""Библиотека для взаимодействия с [API FlorestMessanger для ботов](https://florestmsgs-florestdev4185.amvera.io/api_docs)!"""
import requests, time
from typing import Any, Callable
from colorama import Fore, init
import asyncio, aiohttp

init()

class Message:
    def __init__(self, data: dict[str, str]):
        self.data = data
    @property
    def type_msg(self):
        """Тип сообщения. (text/другие)"""
        return self.data.get("type")
    @property
    def username(self):
        """Ник автора сообщения."""
        return self.data.get("username")
    @property
    def content(self):
        """Содержание сообщения. Если сообщение текстовое - его текстовое содержание, если это файл/гс - прямая ссылка на него."""
        return self.data.get("content")
    @property
    def mime_type(self):
        """Тип медиа. Если текстовое сообщение - равняется None."""
        return self.data.get("mime_type")
    @property
    def id(self):
        """ID сообщения."""
        if self.data.get("id"):
            return int(self.data.get("id"))
    @property
    def is_admin(self):
        """Является ли человек администратором в чате."""
        if not self.data.get('is_admin'):
            return False
        else:
            return bool(self.data.get('is_admin'))
    @property
    def is_bot(self):
        """Является ли пользователь ботом."""
        if not self.data.get('is_bot'):
            return False
        else:
            return bool(self.data.get('is_bot'))
    @property
    def url_ava(self):
        """Ссылка на аватарку пользователя."""
        url_builder = self.data.get('avatar_url', f'/avatar/{self.username}')
        return f'https://florestmsgs-florestdev4185.amvera.io{url_builder}'
    def download_ava(self):
        """Вернет аватарку пользователя в bytes."""
        try:
            return requests.get(self.url_ava).content
        except:
            return
    @property
    def reply_to(self):
        """Возвращает ID сообщения, на которое был сделан ответ со стороны пользователя.\nNone, если сообщение не является ответным на чужое."""
        if self.data.get("reply_to"):
            return int(self.data.get('reply_to'))
    
class Post:
    def __init__(self, post: dict[str, str]):
        self.post = post
    @property
    def title(self):
        """Заголовок поста."""
        return self.post.get('title')
    @property
    def description(self):
        """Описание поста."""
        return self.post.get("desc")
    @property
    def url(self):
        """Ссылка на пост."""
        return self.post.get("url")
    @property
    def author(self):
        """Ник автора поста."""
        return self.post.get('author')
    
class User:
    def __init__(self, data: str):
        self.data = data
    @property
    def username(self) -> str:
        """Ник пользователя."""
        return self.data
    
class Bot:
    def __init__(self, token: str, username: str, prefix: str = 'test!', proxies: dict[str, str] = None, raise_on_status_code: bool = False):
        """Класс для взаимодействия с ботами FlorestMessanger. Документация: https://florestmsgs-florestdev4185.amvera.io/api_docs\ntoken: токен бота. Создать бота и получить токен: https://florestmsgs-florestdev4185.amvera.io/your_bots\nusername: ник бота, чтобы он не реагировал на свои же сообщения.\nprefix: префикс команд. К примеру, `!`\nproxies: прокси для запросов. Необязательно.\nraise_on_status_code: производить ошибку при получении HTTP кода типов 400, 500, 401 и др. Хорошо для debug."""
        self.token = token
        self.proxies = proxies
        self.raise_on_status_code = raise_on_status_code
        self.username = username
        start = requests.get("https://florestmsgs-florestdev4185.amvera.io/api/bot/get_messages", headers={"X-Bot-Token":self.token}, proxies=self.proxies)
        if start.status_code != 200:
            if self.raise_on_status_code:
                print(f'{Fore.RED}Fucking exception! Stopping the polling..')
                raise Exception(f"ОШИБКА! КОД: {start.status_code}. JSON: {start.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
        self.start_messages = start.json().get("messages")
        self.command_handlers = []
        self.prefix = prefix
    def add_command(self, name: str) -> Callable:
        """Декоратор для добавления команды.
        Пример: @bot.add_command('hello') def func(message): ..."""
        def decorator(func: Callable[[Message], None]):
            self.command_handlers.append({'name': self.prefix + name, 'func': func})
            return func
        return decorator

    def get_users(self) -> list[User]:
        """Функция для получения списка пользователей на данный момент."""
        r = requests.get("https://florestmsgs-florestdev4185.amvera.io/api/bot/get_users", proxies=self.proxies, headers={"X-Bot-Token":self.token})
        if r.status_code != 200:
            if self.raise_on_status_code:
                raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            else:
                return []
        else:
            _ = []
            for u in r.json()["usernames"]:
                _.append(User(u))
            return _
    def send_message(self, text: str) -> bool:
        """Отправка текстового сообщения.\ntext: текст сообщения."""
        r = requests.post("https://florestmsgs-florestdev4185.amvera.io/api/bot/send_message", params={"content":text}, proxies=self.proxies, headers={"X-Bot-Token":self.token})
        if r.status_code != 200:
            if self.raise_on_status_code:
                raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            else:
                return False
        else:
            return True
    def send_media(self, media: Any) -> str:
        """Отправка медиа в чат любого типа. Видео, фото, файлы любых разрешений до 500 МБ.\nmedia: base64/bytes/buffer (к примеру, `open()`)\nВозвращает ссылку на отправленное медиа."""
        r = requests.post("https://florestmsgs-florestdev4185.amvera.io/api/bot/send_media", headers={"X-Bot-Token":self.token}, files={"file":media}, proxies=self.proxies)
        if r.status_code != 200:
            if self.raise_on_status_code:
                raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            else:
                return False
        else:
            return r.json().get("url")
    def send_dm(self, username: str, content: str) -> bool:
        """Отправка личных сообщений пользователям для передачи чувствительных данных.\nusername: ник пользователя для отправки ЛС.\ncontent: что ему над написать?\n`True` при успешной отправке. `False` при отсутствии пользователя в сети, или при неправильном токене."""
        r = requests.post("https://florestmsgs-florestdev4185.amvera.io/api/bot/send_dm", params={"username":username, "content":content}, proxies=self.proxies, headers={"X-Bot-Token":self.token})
        if r.status_code != 200:
            if self.raise_on_status_code:
                raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            else:
                return False
        else:
            return True
    def send_reply(self, message, content: str) -> bool:
        """Функция для ответа на чужое сообщение в мессенджере.\nmessage: экземпляр класса "Message", или ID сообщения (int).\ncontent: сообщение; как надо ответить на запрос.\nВозвращает True/False."""
        if isinstance(message, int):
            r = requests.post("https://florestmsgs-florestdev4185.amvera.io/api/bot/send_reply", params={"reply_to":message, "content":content}, proxies=self.proxies, headers={"X-Bot-Token":self.token})
            if r.status_code != 200:
                if self.raise_on_status_code:
                    raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                else:
                    return False
            else:
                return True
        elif isinstance(message, Message):
            r = requests.post("https://florestmsgs-florestdev4185.amvera.io/api/bot/send_reply", params={"reply_to":message.id, "content":content}, proxies=self.proxies, headers={"X-Bot-Token":self.token})
            if r.status_code != 200:
                if self.raise_on_status_code:
                    raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                else:
                    return False
            else:
                return True
        else:
            raise Exception(f'Неизвестный тип данных в аргументе message. Только класс Message и int!')
    def get_blogs(self) -> list[Post]:
        """Список постов с `/blogs`."""
        r = requests.get("https://florestmsgs-florestdev4185.amvera.io/api/bot/get_blogs", headers={"X-Bot-Token":self.token}, proxies=self.proxies)
        if r.status_code != 200:
            if self.raise_on_status_code:
                raise Exception(f"ОШИБКА! КОД: {r.status_code}. JSON: {r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            else:
                return []
        else:
            posts = []
            for i in r.json().get("blogs"):
                posts.append(Post(i))
            return posts
    def run(self):
        """Функция для старта бота. Ничего более."""
        print(f'{Fore.YELLOW}STARTING OF POLLING FROM FLORESTMESSANGER\'S API!')
        while True:
            new_req = requests.get("https://florestmsgs-florestdev4185.amvera.io/api/bot/get_messages", headers={"X-Bot-Token": self.token}, proxies=self.proxies)
            if new_req.status_code != 200:
                if self.raise_on_status_code:
                    print(f'{Fore.RED}Fucking exception! Stopping the polling..')
                    raise Exception(f"ОШИБКА! КОД: {new_req.status_code}. JSON: {new_req.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
            _ = new_req.json().get("messages")
            for i in _:
                if i in self.start_messages:
                    pass
                else:
                    if i.get("username") != self.username:
                        for handler in self.command_handlers:
                            if i.get("content") and i.get("content").startswith(handler.get('name')):
                                handler["func"](Message(i))
                    self.start_messages.append(i)
            time.sleep(1)

class AsyncBot:
    def __init__(self, token: str, username: str, prefix: str = 'test!', proxies: dict[str, str] = None, raise_on_status_code: bool = False):
        """Класс для взаимодействия с ботами FlorestMessanger. Документация: https://florestmsgs-florestdev4185.amvera.io/api_docs\ntoken: токен бота. Создать бота и получить токен: https://florestmsgs-florestdev4185.amvera.io/your_bots\nusername: ник бота, чтобы он не реагировал на свои же сообщения.\nprefix: префикс команд. К примеру, `!`\nproxies: прокси для запросов. Необязательно.\nraise_on_status_code: производить ошибку при получении HTTP кода типов 400, 500, 401 и др. Хорошо для debug."""
        self.token = token
        self.proxies = proxies
        self.raise_on_status_code = raise_on_status_code
        self.username = username
        start = requests.get("https://florestmsgs-florestdev4185.amvera.io/api/bot/get_messages", headers={"X-Bot-Token":self.token}, proxies=self.proxies)
        if start.status_code != 200:
            if self.raise_on_status_code:
                print(f'{Fore.RED}Fucking exception! Stopping the polling..')
                raise Exception(f"ОШИБКА! КОД: {start.status_code}. JSON: {start.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
        self.start_messages = start.json().get("messages")
        self.command_handlers = []
        self.prefix = prefix
    def add_command(self, name: str) -> Callable:
        """Декоратор для добавления команды.
        Пример: @bot.add_command('hello') def func(message): ..."""
        def decorator(func: Callable[[Message], None]):
            self.command_handlers.append({'name': self.prefix + name, 'func': func})
            return func
        return decorator
    async def get_users(self) -> list[User]:
        """Асинхронная функция для получения списка пользователей."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/get_users"
        headers = {"X-Bot-Token": self.token}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, proxy=self.proxies, headers=headers) as r:
                    if r.status != 200:
                        if self.raise_on_status_code:
                            raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                        else:
                            return []
                    else:
                        data = await r.json()
                        users = [User(u) for u in data["usernames"]]
                        return users
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return []

    async def send_message(self, text: str) -> bool:
        """Асинхронная отправка текстового сообщения."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/send_message"
        params = {"content": text}
        headers = {"X-Bot-Token": self.token}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, proxy=self.proxies, headers=headers) as r:
                    if r.status != 200:
                        if self.raise_on_status_code:
                            raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                        else:
                            return False
                    else:
                        return True
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return False


    async def send_media(self, media: Any) -> str:
        """Асинхронная отправка медиа в чат любого типа.\nВозвращает ссылку на отправленное медиа."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/send_media"
        headers = {"X-Bot-Token": self.token}


        try:
            async with aiohttp.ClientSession() as session:
                 data = aiohttp.FormData()
                 data.add_field('file', media)
                 async with session.post(url, headers=headers, data=data, proxy=self.proxies) as r:
                    if r.status != 200:
                        if self.raise_on_status_code:
                            raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                        else:
                            return False
                    else:
                        j = await r.json()
                        return j.get("url")
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return False
    
    async def send_dm(self, username: str, content: str) -> bool:
        """Отправка личных сообщений пользователям для передачи чувствительных данных.\nusername: ник пользователя для отправки ЛС.\ncontent: что ему над написать?\n`True` при успешной отправке. `False` при отсутствии пользователя в сети, или при неправильном токене."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/send_dm"
        params = {"username":username, "content":content}
        headers = {"X-Bot-Token": self.token}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, proxy=self.proxies, headers=headers) as r:
                    if r.status != 200:
                        if self.raise_on_status_code:
                            raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                        else:
                            return False
                    else:
                        return True
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return False

    async def send_reply(self, message, content: str) -> bool:
        """Функция для ответа на чужое сообщение в мессенджере.\nmessage: экземпляр класса "Message", или ID сообщения (int).\ncontent: сообщение; как надо ответить на запрос.\nВозвращает True/False."""
        if isinstance(message, int):
            url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/send_reply"
            params = {"reply_to":message, "content":content}
            headers = {"X-Bot-Token": self.token}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, params=params, proxy=self.proxies, headers=headers) as r:
                        if r.status != 200:
                            if self.raise_on_status_code:
                                raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                            else:
                                return False
                        else:
                            return True
            except aiohttp.ClientError as e:
                print(f"Ошибка клиента aiohttp: {e}")
                return False
        elif isinstance(message, Message):
            url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/send_reply"
            params = {"reply_to":message.id, "content":content}
            headers = {"X-Bot-Token": self.token}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, params=params, proxy=self.proxies, headers=headers) as r:
                        if r.status != 200:
                            if self.raise_on_status_code:
                                raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                            else:
                                return False
                        else:
                            return True
            except aiohttp.ClientError as e:
                print(f"Ошибка клиента aiohttp: {e}")
                return False
        else:
            raise Exception(f'Неизвестный тип данных в аргументе message. Только класс Message и int!')

    async def get_blogs(self) -> list[Post]:
        """Асинхронный список постов с `/blogs`."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/get_blogs"
        headers = {"X-Bot-Token": self.token}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, proxy=self.proxies) as r:
                    if r.status != 200:
                        if self.raise_on_status_code:
                            raise Exception(f"ОШИБКА! КОД: {r.status}. JSON: {await r.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                        else:
                            return []
                    else:
                        data = await r.json()
                        posts = [Post(i) for i in data.get("blogs", [])]
                        return posts
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return []


    async def _process_message(self, message_data):
        """Асинхронная обработка одного сообщения."""
        if message_data in self.start_messages:
            return  # Пропустить, если сообщение уже обработано

        if message_data.get("username") != self.username:  # Используем username
            for handler in self.command_handlers:
                content = message_data.get("content")
                if content and content.startswith(handler.get('name')):
                    await handler["func"](Message(message_data))

        self.start_messages.append(message_data)


    async def polling(self):
        """Асинхронная функция для опроса API и получения новых сообщений."""
        url = f"https://florestmsgs-florestdev4185.amvera.io/api/bot/get_messages"
        headers = {"X-Bot-Token": self.token}

        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    try:  # Добавлено для перехвата ошибок aiohttp внутри цикла
                        async with session.get(url, headers=headers, proxy=self.proxies) as response:
                            if response.status != 200:
                                if self.raise_on_status_code:
                                    print(f'{Fore.RED}Fucking exception! Stopping the polling..')
                                    raise Exception(f"ОШИБКА! КОД: {response.status}. JSON: {await response.json()}. ПРОВЕРЬТЕ ТОКЕН И ПРАВИЛЬНОСТЬ УКАЗАННЫХ ПАРАМЕТРОВ!!!")
                                else:
                                    print(f'{Fore.RED}API Error: {response.status}')
                                    await asyncio.sleep(1) # ждем 1 сек
                                    continue # переходим к следующей итерации цикла
                            data = await response.json()
                            messages = data.get("messages", [])  # Используем get() с значением по умолчанию

                            tasks = [self._process_message(message) for message in messages]
                            await asyncio.gather(*tasks) # одновременный запуск корутин
                    except aiohttp.ClientError as e:
                        print(f"aiohttp error during polling: {e}")
                        await asyncio.sleep(5) #  увеличиваем время ожидания в случае ошибки
                    except Exception as e:
                         print(f"Unexpected error during polling: {e}")
                         await asyncio.sleep(5)

                    await asyncio.sleep(1)  # Задержка перед следующим запросом
        except Exception as e: # общий обработчик ошибок
            print(f"Global error in polling loop: {e}")



    def run(self):
        """Функция для старта бота."""
        print(f'{Fore.YELLOW}STARTING OF POLLING FROM FLORESTMESSANGER\'S API!')
        asyncio.run(self.polling())