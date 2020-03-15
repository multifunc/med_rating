# -*- coding: utf-8 -*-

import logging
from pathlib import Path
from typing import List, Dict, Optional

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


def write_report_to_file(file: Path, user: Dict, tasks: List[Dict]) -> bool:
    """
    Создает файл отчета и заполняет данными о пользователе из словаря и
    возращет результат об успешном(ошибочном) создания файла
    :param file: полное имя файла отчета
    :param user: словарь данных по пользовател для которого формируем отчет
    :param tasks: список задач пользователя
    :return: при успешном формировании файл отчета возвращает True иначе False
    """
    pass


def create_report(user: Dict, tasks: List[Dict]):
    """
    Формирует файл отчета по пользователю
    :param user: информация о пользователе
    :param tasks: список задач пользовотеля
    """


def group_tasks_by_user(users: List[Dict], tasks: List[Dict]) -> Dict:
    """
    Функция группирует списки задач по ключу userId
    :param users: список словарей пользователей
    :param tasks: список словарей задач
    :return: в случае успешной обработки полученных данных возращается словарь
    """


def get_users_from_api(users_api_url: str) -> Optional[List[Dict]]:
    """
    Функция отправляет запрос на API для получения json словаря со списком данных пользователей
    :return: при успешном запросе возвращается json словарь со списком пользователей, иначе возвращает None
    """


def get_tasks_from_api(tasks_api_url: str) -> Optional[List[Dict]]:
    """
    Функция отправляет запрос на API для получения json словаря со списком заданий
    :return: при успешном запросе возвращается json словарь со списком заданий, иначе возвращает None
    """


if __name__ == '__main__':
    main()
