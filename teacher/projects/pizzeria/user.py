"""Модуль для работы с файлами пользователя"""
import os
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

def init_user(username: str):
    """
    Инициализирует папку пользователя и все необходимые файлы
    
    :param username: Уникальное имя пользователя в Telegram
    :return: None
    """

    # Получение пути к текущей директории скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # формируем корректную директорию
    target_dir = os.path.join(current_dir, "users", username)

    # Создаем личную папку пользователя если это необходимо
    if os.path.exists(target_dir):
        print(f"Папка пользователя {username} существует.")
    else:
        os.mkdir(target_dir)
        print(f"Папка пользователя {username} создана.")

        # Создаем файл для хранения корзины
        fp = open(f"{target_dir}/basket.json", "w")
        json.dump({}, fp)
        fp.close()
        print("Корзина создана.")

        # Создаем папку для заказов
        os.mkdir(f"{target_dir}/orders")
        print("Папка для заказов создана.")

def read_goods():
    # Получение пути к текущей директории скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))

    fp = open(f"{current_dir}/goods.json", "r")
    goods = json.load(fp)
    fp.close()
    return goods


def generate_menu_markup(user_id: str):
    """
    Функция генерирует кнопки для товаров из меню.
    """
    keyboard = []

    goods = read_goods()

    for product_id in goods:
        product_name = goods[product_id]["name"]
        keyboard.append( [InlineKeyboardButton(product_name, callback_data=f"to_product_{product_id}")] )

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def generate_product_markup_data(user_id: str, product_id: str):
    """
    Функция генерирует разметку для товара.
    """

    goods = read_goods()

    product_name = goods[product_id]["name"]
    product_description = goods[product_id]["description"]
    product_price = goods[product_id]["price"]

    message = f"<b>{product_name}</b>\n\n{product_description}\n\n<b>Цена</b>: {product_price}"

    goods_count = calculate_all_basket_goods(user_id)

    keyboard = [
        [InlineKeyboardButton(f"Заказать", callback_data=f"order_product_{product_id}")],
        [InlineKeyboardButton("Вернуться в Меню", callback_data="to_menu_page")],
        [InlineKeyboardButton(f"Перейти к Корзине (Всего товаров:{goods_count})", callback_data="to_basket_page")]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    return {
        "message": message,
        "markup": markup
    }


def generate_order_markup_data(user_id: str, product_id: str):
    """
    Функция генерирует разметку для ответа о заказанном товаре.
    """

    goods = read_goods()

    product_name = goods[product_id]["name"]
    product_price = goods[product_id]["price"]

    message = "Вы заказали " + product_name + " по цене " + str(product_price)

    goods_count = calculate_all_basket_goods(user_id)

    keyboard = [
        [InlineKeyboardButton(f"Заказать повторно", callback_data=f"order_product_{product_id}")],
        [InlineKeyboardButton("Вернуться в Меню", callback_data="to_menu_page")],
        [InlineKeyboardButton(f"Перейти к Корзине (Всего товаров: {goods_count})", callback_data="to_basket_page")]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    return {
        "message": message,
        "markup": markup
    }


def read_user_basket(user_id: str):
    # Получение пути к текущей директории скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # формируем корректную директорию
    target_dir = os.path.join(current_dir, "users", user_id)

    fp = open(f"{target_dir}/basket.json", "r")
    user_basket = json.load(fp)
    fp.close()

    return user_basket

def calculate_all_basket_goods(user_id: str):
    user_basket = read_user_basket(user_id)

    goods_count = 0

    for product_id in user_basket:
        goods_count += user_basket[product_id]

    return goods_count


def add_product_to_basket(user_id: str, product_id: str):
    user_basket = read_user_basket(user_id)

    # Получение пути к текущей директории скрипта
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # формируем корректную директорию
    target_dir = os.path.join(current_dir, "users", user_id)

    user_basket[product_id] = (user_basket.get(product_id) or 0) + 1

    fp = open(f"{target_dir}/basket.json", "w")
    json.dump(user_basket, fp)
    fp.close()
    print(f"Пользователь {user_id} добавил в корзину {product_id}")
