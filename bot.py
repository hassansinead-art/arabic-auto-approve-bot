import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    ContextTypes,
)

# بوت موافقة تلقائية فقط.
# لا يحتوي هذا البرنامج على أي دالة لإرسال رسائل خاصة للأعضاء.

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def approve_join_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    request = update.chat_join_request
    if request is None:
        return

    target_channel = os.getenv("CHANNEL_ID", "").strip()

    # إذا حُددت قناة بعينها، تجاهل الطلبات القادمة من أي محادثة أخرى.
    if target_channel and str(request.chat.id) != target_channel:
        return

    try:
        await context.bot.approve_chat_join_request(
            chat_id=request.chat.id,
            user_id=request.from_user.id,
        )
        logger.info(
            "تمت الموافقة على طلب انضمام. channel_id=%s user_id=%s",
            request.chat.id,
            request.from_user.id,
        )
    except Exception:
        # تسجيل الخطأ فقط، دون إرسال أي رسالة للمستخدم.
        logger.exception(
            "تعذرت الموافقة على الطلب. channel_id=%s user_id=%s",
            request.chat.id,
            request.from_user.id,
        )


def main() -> None:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("يرجى ضبط متغير البيئة BOT_TOKEN.")

    app = Application.builder().token(token).build()
    app.add_handler(ChatJoinRequestHandler(approve_join_request))

    logger.info("بدأ بوت الموافقة التلقائية. لا تُرسل رسائل خاصة.")
    app.run_polling(
        allowed_updates=["chat_join_request"],
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()
