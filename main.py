import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
)
from scraper.database import DatabaseManager
from scraper.divar_scraper import DivarScraper
from modules.neighborhood_selector import select_neighborhoods
from notifier.telegram_notifier import TelegramNotifier
from utils.logger import logger
from utils.metrics import PROCESSED_USERS, start_metrics_server
from config import Config
from modules.filters_handler import handle_filters

# 🔥 تنظیمات لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

db_manager = DatabaseManager()
notifier = TelegramNotifier()

# 📌 مراحل مکالمه
SELECT_AD_TYPE, SELECT_NEIGHBORHOODS, FILTERS, CHANGE_FILTERS = range(4)

# ✅ استارت و دریافت شماره تماس
async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[KeyboardButton("📞 ارسال شماره تماس", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("سلام! لطفاً شماره‌تماس خود را ارسال کنید.", reply_markup=reply_markup)
    return ConversationHandler.END

# ✅ دریافت شماره و تایید شهر (تهران)
async def contact_received(update: Update, context: CallbackContext) -> int:
    contact = update.message.contact
    chat_id = update.message.chat.id
    name = update.message.from_user.full_name
    phone_number = contact.phone_number

    await db_manager.add_user(chat_id, name, phone_number)
    await update.message.reply_text(f"✅ شماره شما دریافت شد: {phone_number}")
    await update.message.reply_text("🏙 **شهر شما: تهران** ✅ (قابل تغییر نیست)")
    
    # پرسش درباره نوع آگهی
    await update.message.reply_text("❓ لطفاً **نوع آگهی** را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup([
        ["🏡 فروش"], ["🏠 رهن و اجاره"]
    ], resize_keyboard=True))
    return SELECT_AD_TYPE

# ✅ دریافت نوع آگهی
async def select_ad_type(update: Update, context: CallbackContext) -> int:
    context.user_data["ad_type"] = update.message.text
    await update.message.reply_text("📍 لطفاً حداکثر ۳ محله‌ی مورد نظر خود را انتخاب کنید.")
    return SELECT_NEIGHBORHOODS

# ✅ دریافت و ذخیره محله‌ها
async def neighborhoods_handler(update: Update, context: CallbackContext) -> int:
    neighborhoods = select_neighborhoods(update.message.text)
    if not neighborhoods:
        await update.message.reply_text("❌ هیچ محله‌ای یافت نشد. لطفاً دوباره امتحان کنید.")
        return SELECT_NEIGHBORHOODS

    context.user_data['neighborhoods'] = neighborhoods
    await update.message.reply_text(f"✅ محله‌های انتخاب‌شده: {', '.join(neighborhoods)}")

    # انتقال به دریافت فیلترها
    return await handle_filters(update, context)

# ✅ تنظیمات (امکان تغییر فیلترها)
async def settings(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("⚙️ کدام فیلتر را می‌خواهید تغییر دهید؟", reply_markup=ReplyKeyboardMarkup([
        ["📍 تغییر محله‌ها"], ["📏 تغییر متراژ"], ["🛏 تغییر تعداد خواب"], 
        ["💰 تغییر قیمت"], ["🔙 بازگشت به منو"]
    ], resize_keyboard=True))
    return CHANGE_FILTERS

# ✅ هندلر تغییر فیلتر
async def change_filters(update: Update, context: CallbackContext) -> int:
    choice = update.message.text
    if choice == "🔙 بازگشت به منو":
        return ConversationHandler.END

    await update.message.reply_text("❓ ابتدا بگویید که به دنبال **فروش** هستید یا **رهن و اجاره**؟",
                                    reply_markup=ReplyKeyboardMarkup([["فروش"], ["رهن و اجاره"]], resize_keyboard=True))
    context.user_data["change_filter"] = choice
    return FILTERS

# ✅ اجرای ربات
def main():
    app = Application.builder().token(Config.TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_AD_TYPE: [MessageHandler(filters.TEXT, select_ad_type)],
            SELECT_NEIGHBORHOODS: [MessageHandler(filters.TEXT, neighborhoods_handler)],
            FILTERS: [MessageHandler(filters.TEXT, handle_filters)],
            CHANGE_FILTERS: [MessageHandler(filters.TEXT, change_filters)]
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
