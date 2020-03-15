# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from json import JSONDecodeError
from typing import List, Dict, Optional

import requests
from requests import RequestException
from jsonschema import validate, ValidationError, SchemaError

from schemas import USERS, TASKS

ROOT_DIR = Path(__name__).parent
REPORT_DIR = ROOT_DIR.joinpath("tasks")

USERS_API_URL = "https://json.medrating.org/users"
TASKS_API_URL = "https://json.medrating.org/todos"

DATETIME_FMT = "%d.%m.%Y %H:%M"

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = ROOT_DIR / 'task.log'

logger = logging.getLogger("medrating")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(FORMATTER)
logger.addHandler(file_handler)


def main():
    """
    Запуск генерации отчётов по заданиям пользователей
    """
    logger.info("Start")

    if not REPORT_DIR.exists():
        REPORT_DIR.mkdir()

    users = get_users_from_api(USERS_API_URL)
    if users is None:
        logger.warning("Повторите попытку позже, не удалось получить список пользователей!")
        return

    tasks = get_tasks_from_api(TASKS_API_URL)
    if tasks is None:
        logger.warning("Повторите попытку позже, не удалось получить список заданий!")
        return

    users_tasks: dict = group_tasks_by_user(users, tasks)
    for user_id in users_tasks.keys():
        create_report(users_tasks[user_id]['user'], users_tasks[user_id]['tasks'])

    logger.info("Success")


def str_shortener(string: str, max_len: int = 50, placeholder: str = '...') -> str:
    """
    Сокращает строку до `max_len` символов
    :param string: строка
    :param max_len: максимальная длина строки
    :param placeholder: строка для замены символов выше `max_len`
    :return: возращает строку, если длина не превышает `max_len` иначе возращает сокращенную строку
    """
    if len(string) > max_len:
        return string[:max_len] + placeholder
    return string


def write_report_to_file(file: Path, user: Dict, tasks: List[Dict]) -> bool:
    """
    Создает файл отчета и заполняет данными о пользователе из словаря и
    возращет результат об успешном(ошибочном) создания файла
    :param file: полное имя файла отчета
    :param user: словарь данных по пользовател для которого формируем отчет
    :param tasks: список задач пользователя
    :return: при успешном формировании файл отчета возвращает True иначе False
    """
    success = True
    try:
        with file.open('w', encoding='utf-8') as f:
            report_heading: str = (
                f"{user['name']} <{user['email']}> "
                f"{datetime.now().strftime(DATETIME_FMT)}\n"
                f"{user['username']}\n\n"

            )
            f.write(report_heading)
            f.write("Завершённые задачи:\n")

            first_remaining_task_index: Optional[int] = None
            for index, task in enumerate(tasks):
                if task['completed']:
                    f.write(str_shortener(task['title']) + "\n")
                else:
                    first_remaining_task_index = index
                    break

            f.write("\nОставшиеся задачи:\n")
            if first_remaining_task_index:
                for task in tasks[first_remaining_task_index:]:
                    f.write(str_shortener(task['title']) + "\n")
    except (OSError, KeyError, IndexError, ValueError) as e:
        logger.exception(f"Ошибка при записи данных в файл: <{e}>.")
        success = False

    return success


def get_report_datetime(file: Path) -> Optional[datetime]:
    """
    Возвращает дату генерации файла отчёта, хранящуюся в его 1-й строке
    :param file: полный путь к файлу отчёта
    :return: дата формирования отчёта
    """
    report_date = None
    try:
        with file.open('r', encoding='utf-8') as f:
            first_line = f.readlines(1)[0]

        if first_line:
            try:
                raw_date: str = first_line.split(">")[1].strip()
                report_date = datetime.strptime(raw_date, DATETIME_FMT)
            except (IndexError, ValueError) as e:
                if isinstance(e, IndexError):
                    logger.exception("Ошибка в первой строке, не удалось извлечь дату отчета!")
                else:
                    logger.exception("Ошибка в первой строке, не удалось преобразовать дату отчета!")
    except OSError:
        logger.exception("Ошибка, не удалось открыть файл, для прочтения!")
    return report_date


def rollover(file: Path, username: str):
    """
    Переименовывает файл, добавляя в суффикс дату создания файла, хранящуюся в первой строке
    :param file: путь к файлу
    :param username: имя пользователя
    :return: (путь к переименованному файлу, флаг успеха операции)
    """
    original_file: Path = Path(file)
    success: bool = False
    renamed_file: Optional[Path] = None
    try:
        report_date = get_report_datetime(file)
        if report_date:
            renamed_file = REPORT_DIR.joinpath(username + report_date.strftime("_%Y-%m-%dT%H:%M") + '.txt')
            original_file.rename(renamed_file)
            success = True
    except OSError:
        logger.exception("Ошибка при переименовании файлов отчета.")

    return renamed_file, success


def create_report(user: Dict, tasks: List[Dict]):
    """
    Формирует файл отчета по пользователю
    :param user: информация о пользователе
    :param tasks: список задач пользовотеля
    """
    try:
        username: str = user['username']
        report_file: Path = REPORT_DIR.joinpath(username + '.txt')

        rollback_allowed: bool = False
        renamed_file: Optional[Path] = None
        if report_file.exists():
            renamed_file, rollback_allowed = rollover(report_file, username)

        if not write_report_to_file(report_file, user, tasks):
            if rollback_allowed and renamed_file:
                renamed_file.rename(report_file)
    except OSError as e:
        logger.exception(f"Ошибка при формировании отчета для пользователя {user['username']}: {e}")


def group_tasks_by_user(users: List[Dict], tasks: List[Dict]) -> Dict:
    """
    Группирует списки задач по ключу userId
    :param users: список словарей пользователей
    :param tasks: список словарей задач
    :return: словарь пользователей и сгруппированных и отсортированных задач пользователе (сначала идут выполненные)
    """
    users.sort(key=itemgetter('id'))

    # выполненные задачи в разрезе пользователя будут будут идти первыми
    tasks.sort(key=lambda task: (task['userId'], not task['completed']))
    users_tasks = {
        user['id']: {
            "user": user,
            "tasks": []
        }
        for user in users
    }
    for user_id, task_group in groupby(tasks, key=itemgetter('userId')):
        if user_id in users_tasks.keys():
            users_tasks[user_id]['tasks'] = list(task_group)
    return users_tasks


def get_users_from_api(users_api_url: str) -> Optional[List[Dict]]:
    """
    Функция отправляет запрос на API для получения json словаря со списком данных пользователей
    :return: при успешном запросе возвращается json словарь со списком пользователей, иначе возвращает None
    """
    try:
        response = requests.get(users_api_url)
        users = response.json()
        validate(users, schema=USERS)
        return users
    except (RequestException, JSONDecodeError, ValidationError, SchemaError) as e:
        if isinstance(e, RequestException):
            logger.exception(f"Ошибка при получение данных: <{e}>!")
        elif isinstance(e, JSONDecodeError):
            logger.exception(f"Ошибка при парсинге json - ответа от сервера: <{e}>.")
        elif isinstance(e, (ValidationError, SchemaError)):
            logger.exception(f"Ошибка валидации списка пользователей по схеме USERS: {e}")


def get_tasks_from_api(tasks_api_url: str) -> Optional[List[Dict]]:
    """
    Функция отправляет запрос на API для получения json словаря со списком заданий
    :return: при успешном запросе возвращается json словарь со списком заданий, иначе возвращает None
    """
    try:
        response = requests.get(tasks_api_url)
        tasks = response.json()
        validate(tasks, schema=TASKS)
        return tasks
    except (RequestException, JSONDecodeError, ValidationError, SchemaError) as e:
        if isinstance(e, RequestException):
            logger.exception(f"Ошибка при получение данных: <{e}>!")
        elif isinstance(e, JSONDecodeError):
            logger.exception(f"Ошибка при парсинге json - ответа от сервера: <{e}>.")
        elif isinstance(e, (ValidationError, SchemaError)):
            logger.exception(f"Ошибка валидации списка задач по схеме TASKS: {e}")


if __name__ == '__main__':
    main()
