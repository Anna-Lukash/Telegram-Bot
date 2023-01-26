from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from json import dumps
from json import loads
from json import load
import config

questions = load(open("questions.json", "r", encoding="utf-8"))
is_in_progress = False
bot = Bot(token=config.TOKEN) #Ваш токен
dp = Dispatcher(bot=bot)
'''1. Delete all decorators and add dp.register....
2. Add dictionary'''
#Transfer to keyboard file
def compose_markup(question: int):
    km = InlineKeyboardMarkup(row_width=4)
    for i in range(len(questions[question]["variants"])):
        cd = {
            "question": question,
            "answer": i
        }
        km.insert(InlineKeyboardButton(questions[question]["variants"][i], callback_data=dumps(cd)))
    return km

# Handler for checking test answers 
@dp.callback_query_handler(lambda c: True)
async def answer_handler(callback: CallbackQuery):
    data = loads(callback.data)
    q = data["question"]
    is_correct = questions[q]["correct_answer"] - 1 == data["answer"]
    passed = 0
    is_in_progress = True
    if is_correct:
        passed += 1
    if q + 1 > len(questions) - 1:
        reset(callback.from_user.id)
        await bot.delete_message(callback.from_user.id, msg)
        await bot.send_message(
            callback.from_user.id,
            f"Ви пройшли тестування\\! \n✅ Правильних відповідей\\: *{passed} з {len(questions)}*\\.", parse_mode="MarkdownV2"
        )
        return
    await bot.edit_message_text(
        questions[q + 1]["text"],
        callback.from_user.id,
        reply_markup=compose_markup(q + 1),
        parse_mode="MarkdownV2"
    )


@dp.message_handler(commands=["test"])
async def go_handler(message: Message):
    if is_in_progress:
        await bot.send_message(message.from_user.id, "🚫 Ви не можете почати тест, тому що *ви вже його проходите*\\.", parse_mode="MarkdownV2")
        return
    else:
        await bot.send_message(
        message.from_user.id,
        questions[0]["text"],
        reply_markup=compose_markup(0),
        parse_mode="MarkdownV2"
    )


@dp.message_handler(commands=["finish"])
async def quit_handler(message: Message):
    if not is_in_progress:
        await bot.send_message(message.from_user.id, "❗️Ви ще *не почали тест*\\.", parse_mode="MarkdownV2")
        return
    await bot.send_message(message.from_user.id, "✅ Ви *закінчили тест*\\.", parse_mode="MarkdownV2")
    
# START, change from message_handler to callback_query_handler 
@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("Запрошуємо тебе пройти невеликий тест на приблизне визначення рівня англійської\\. \n\n📝 Тест складається з 20 питань різної складності, які в основному перевіряють вашу граматику і лексику\\. \n\nСаме тому тест НЕ Є 100% відображенням вашого рівня англійської\\. \nРеді\\? Стеді\\? Гоу\\!🏃‍♀️\n\n*Почати тест* \\- /test\n*Закінчити тест* \\- /finish", parse_mode="MarkdownV2")



def main() -> None:
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main()


