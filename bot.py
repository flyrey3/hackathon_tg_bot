import openai
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TELEGRAM_TOKEN = 'bot token'
OPENAI_API_KEY = 'openai api token '
greeting = 'Привет! Я бот, который может отвечать на твои вопросы с помощью ChatGPT. Просто отправь мне свой вопрос.'

openai.api_key = OPENAI_API_KEY

# Создаем объекты бота и диспетчера
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def wlc(message: types.Message):
    print("Получена команда start")
    await bot.send_message(message.from_user.id, greeting)


@dp.message_handler()
async def handle_all_messages(message: types.Message):
    print("Получено сообщение:", message.text)
    executing_message = await bot.send_message(message.chat.id, 'Выполняю...')
    completion_response = generate_openai_completion(
        message.text, message.chat.id)
    await bot.edit_message_text(text=completion_response, chat_id=message.from_user.id, message_id=executing_message.message_id)


def generate_openai_completion(prompt_text, chat_id):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0.4,
            max_tokens=4000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )

        if 'choices' in response and response['choices']:
            return response['choices'][0]['text']
        else:
            return "Извините, не удалось получить ответ от OpenAI."

    except openai.error.OpenAIError as e:
        if "length is" in str(e):
            return "Извините, ваш запрос слишком длинный. Пожалуйста, сформулируйте его более коротко."
        else:
            print(f"Ошибка при вызове API OpenAI: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."


@dp.message_handler()
async def handle_all_messages(message: types.Message):
    print("Получено сообщение:", message.text)
    completion_response = generate_openai_completion(message.text)
    await message.answer(completion_response)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
