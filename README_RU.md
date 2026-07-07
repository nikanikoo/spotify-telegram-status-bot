<div align="center">
  <img width="464" height="238" alt="image" src="https://github.com/user-attachments/assets/e412408b-f534-4ee3-b940-64dbd8873867" />
  <h1>Spotify to Telegram Status Bot</h1>
  <p><b>Скрипт на Python для трансляции проигрываемого трека Spotify в сообщение Telegram-канала в реальном времени.</b></p>
  <div>
	  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
	  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-red.svg?style=flat-square"></a>
  </div>
</div>

---

[EN](README.md)

**Spotify to Telegram Status Bot** — это легковесный Python-скрипт, транслирующий ваше текущее воспроизведение из Spotify в сообщение Telegram-канала и обновляющий его в реальном времени с прогресс-баром, временем воспроизведения и прямой ссылкой на трек.

> [!NOTE]
> При первом запуске бот автоматически отправит сообщение в указанный канал, получит его ID, сохранит его в конфигурацию `.env` и будет обновлять его каждые несколько секунд.

## 🚀 Возможности

- **Обновление в реальном времени**: Автоматически синхронизирует состояние воспроизведения и прогресс.
- **Интерактивный прогресс-бар**: Наглядно отображает положение воспроизведения трека.
- **Прямые ссылки**: Названия треков оформлены в виде кликабельных ссылок на Spotify.
- **Локализация**: Легкое переключение языка (`en` / `ru`) через конфигурацию в `.env` благодаря подгрузке данных из внешних JSON-файлов в `/locales`.

---

## 🛠 Установка и настройка

### Шаг 1. Создание Telegram-бота
1. Найдите бота **@BotFather** в Telegram и отправьте команду `/newbot`.
2. Скопируйте полученный **API Token**.
3. Создайте Telegram-канал (или используйте существующий) и добавьте бота в него в качестве **Администратора** с правами на публикацию и редактирование сообщений.
4. Скопируйте идентификатор канала (например, публичный юзернейм `@my_channel` или числовой ID `-1001234567890`).

### Шаг 2. Создание Spotify Developer App
1. Перейдите на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) и войдите в систему.
2. Нажмите **Create App** и заполните поля:
   - **App name**: Например, `Telegram Status Bot`
   - **Redirect URIs**: Вставьте строго этот адрес: `http://localhost:8888/callback`
3. Сохраните изменения, зайдите в **Settings** приложения и скопируйте **Client ID** и **Client Secret**.

### Шаг 3. Установка проекта
1. Склонируйте репозиторий или перейдите в папку с проектом.
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # Для Windows:
   .\venv\Scripts\activate
   # Для macOS/Linux:
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Скопируйте шаблон `.env.example` в рабочий файл `.env`:
   ```bash
   # Для macOS/Linux/Git Bash:
   cp .env.example .env
   # Для Windows PowerShell:
   Copy-Item .env.example .env
   ```
5. Откройте файл `.env` и заполните обязательные параметры:
   - `TELEGRAM_BOT_TOKEN`: Токен вашего Telegram-бота.
   - `TELEGRAM_CHANNEL_ID`: Юзернейм или ID канала.
   - `SPOTIFY_CLIENT_ID`: Client ID вашего приложения в Spotify.
   - `SPOTIFY_CLIENT_SECRET`: Client Secret вашего приложения в Spotify.
   - `LANGUAGE`: Задайте нужный язык — `ru` (русский) или `en` (английский).

   *Примечание: Оставьте `TELEGRAM_MESSAGE_ID` и `SPOTIFY_REFRESH_TOKEN` пустыми. Скрипт заполнит их самостоятельно.*

---

## 🔑 Авторизация в Spotify
Запустите скрипт авторизации:
```bash
python auth.py
```
Скрипт автоматически откроет вкладку в браузере. Войдите в Spotify (если требуется) и подтвердите права доступа, нажав **Authorize (Принять)**. После этого токен `SPOTIFY_REFRESH_TOKEN` будет сохранен в ваш файл `.env`.

---

## 📈 Запуск статус-бота
Запустите службу обновления статуса:
```bash
python main.py
```
Бот опубликует первое сообщение, запишет его ID в параметр `TELEGRAM_MESSAGE_ID` внутри `.env` и начнет отслеживать музыку, обновляя пост в реальном времени.

> [!TIP]
> Закрепите статусное сообщение в вашем канале, чтобы подписчики всегда могли видеть, что у вас играет в данный момент!

---

## 📄 Лицензия
Этот проект распространяется под лицензией [MIT](LICENSE).
