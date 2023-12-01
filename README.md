# Blog

[![License MIT](https://img.shields.io/badge/licence-MIT-green)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/-SQLite-464646?style=flat-square&logo=SQLite)](https://www.sqlite.org/index.html)

## Информация о проекте
Небольшая социальная сеть для публикации личных блогов. На сайте пользователь может авторизоваться и публиковать свои посты.



## Инструкция по запуску проекта
1. Склонируйте проект «Blogicum» себе на компьютер.
2. Создайте  virtual environment для папки с проектом: 

   - Linux/macOS
    
    ```bash
    python3 -m venv venv
    ```
    
- Windows
    
    ```python
    python -m venv venv
    ```

3. Активируйте виртуального окружения

- Linux/macOS
    
    ```bash
    source venv/bin/activate
    ```
    
- Windows
    
    ```bash
    source venv/Scripts/activate
    ```
4. Все дальнейшие команды в терминале надо выполнять с активированным виртуальным окружением.

Обновите pip:

```bash
python -m pip install --upgrade pip
```

5. Установите зависимостей из файла *requirements.txt*:
команда в терминале **pip install -r requirements.txt** (Windows).

```bash
pip install -r requirements.txt
```

6. Применете миграцию

    
В директории с файлом manage.py выполните команду: 

```bash
python manage.py migrate
```

7. загрузите фикстуры из файла db.json (или со своей фикстуры с аналогичной структурой таблиц)

    
В директории с файлом manage.py выполните команду: 

```bash
python manage.py loaddata db.json
```

8. Запустите проект в dev-режиме

    
В директории с файлом manage.py выполните команду: 

```bash
python manage.py runserver
```

В ответ Django сообщит, что сервер запущен и проект доступен по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). 