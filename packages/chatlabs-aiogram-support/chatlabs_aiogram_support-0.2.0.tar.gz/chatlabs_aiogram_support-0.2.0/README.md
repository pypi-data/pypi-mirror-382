# ChatLabs Aiogram Support

## Установка

`pip install chatlabs-aiogram-support`

Необходимые переменные окружения:
- `BACKEND_SCHEMA`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `BACKEND_SUPPORT_PATH`

Добавление роутера поддержки в диспетчер:
```python
from aiogram import Dispatcher
import support

dp = Dispatcher()

dp.include_router(support.dialog_router)
```

Добавление кнопки поддержки в окно:
```python
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
import support

Dialog(
    ...,
    Window(
        ...,
        Start(
            text=Const('Поддержка'),
            id='support',
            state=support.main_state,
        ),
        ...,
    ),
    ...,
)
```

Альтернативный вариант:
```python
from aiogram_dialog import Dialog, Window
import support

Dialog(
    ...,
    Window(
        ...,
        support.SupportStartButton,
        ...,
    ),
    ...,
)
```
