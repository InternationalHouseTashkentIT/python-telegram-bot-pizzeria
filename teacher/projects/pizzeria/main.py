import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import user

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

token = "6128693331:AAHX8Pf-jv2krN9XnAtqCPPdostQjAJ0x2c"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение с тремя прикрепленными кнопками."""

    # Инициализируем пользователя если это необходимо.
    user.init_user(update.effective_user.username)

    keyboard = [
        [
            InlineKeyboardButton("Меню", callback_data="to_menu_page"),
            InlineKeyboardButton("Корзина", callback_data="to_basket_page"),
        ],
        # [InlineKeyboardButton("Опция 3", callback_data="3")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Пожалуйста выбери", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries должны быть обязательно отвечены, даже если уведомление пользователю не требуется отправлять.
    # Некоторые клиенты могут испытывать проблемы в противном случае. См. https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    user_name = update.effective_user.username

    if query.data == "to_menu_page":
        markup = user.generate_menu_markup(user_name)
        await query.edit_message_text(text="Вы перешли в меню:", reply_markup=markup)

    elif query.data == "to_basket_page":
        await query.edit_message_text(text="Вы перешли в корзину")

    elif "to_product_" in query.data:
        # Обрезаем строку - получаем id продукта
        product_id = query.data[11:]
        data = user.generate_product_markup_data(user_name, product_id)

        await query.edit_message_text(text=data["message"],
            reply_markup=data["markup"],
            parse_mode="html"
        )

    elif "order_product_" in query.data:
        # Обрезаем строку - получаем id продукта
        product_id = query.data[14:]

        # Добавляем товар в корзину
        user.add_product_to_basket(user_name, product_id)

        # Генерируем ответ о заказанном товаре
        data = user.generate_order_markup_data(user_name, product_id)

        await query.edit_message_text(text=data["message"], reply_markup=data["markup"], parse_mode="html")

    else:
        await query.edit_message_text(text=f"Ваш ответ: {query.data}")

app = ApplicationBuilder().token(token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()

