from typing import List, Tuple
from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)


def make_row_keyboards(items: List[str]) -> ReplyKeyboardMarkup:
    """
    :param items:
    :return:
    """
    # Создаем основной список кнопок
    keyboard = [[KeyboardButton(text=item)] for item in items]
    # Добавляем последние две кнопки в одном ряду
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def make_row_inline_keyboards(items: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    """
    :param items:
    :return:
    """
    # Создаем список для хранения строк клавиатуры
    keyboard = []
    # Проходим по всем элементам словаря
    for key, value in items:
        # Создаем кнопку для каждого элемента
        button = InlineKeyboardButton(text=key, callback_data=value)
        # Добавляем кнопку в последнюю строку клавиатуры
        keyboard.append([button])
    # Возвращаем клавиатуру с созданными строками
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def make_row_inline_keyboards_url(items: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    """
    :param
    :return:
    """
    # Создаем список для хранения строк клавиатуры
    keyboard = []
    # Проходим по всем элементам словаря
    for key, value in items:
        # Создаем кнопку для каждого элемента
        button = InlineKeyboardButton(text=key, url=value)
        # Добавляем кнопку в последнюю строку клавиатуры
        keyboard.append([button])
    # Возвращаем клавиатуру с созданными строками
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def make_tasks_inline_keyboard(tasks: list, callback_data_name: str) -> InlineKeyboardMarkup:
    """
    Создает inline-клавиатуру из списка задач.
    Каждая кнопка содержит ID задачи и callback_data вида "task_<id>".

    :param tasks: список задач (объектов с атрибутом id)
    :param callback_data_name: префикс для callback_data, например "task"
    :return: InlineKeyboardMarkup
    """
    keyboard = []

    for task in tasks:
        task_id = task.id
        button = InlineKeyboardButton(text=f'Запрос #{task_id}', callback_data=f'{callback_data_name}_{task_id}')
        keyboard.append([button])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
