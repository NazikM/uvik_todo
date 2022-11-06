import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import db

bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    db.add_user(message.from_user.id)
    telegram_id = message.from_user.id
    await bot.send_message(telegram_id, "Welcome in my ToDo app!")


@dp.message_handler(commands=['add_task'])
async def process_add_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = db.get_user_state(telegram_id)
    if user_state == 'main':
        db.set_user_state(telegram_id, 'add_task_0')
        await bot.send_message(telegram_id, "Enter title for your task")


@dp.message_handler(commands=['remove_task'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = db.get_user_state(telegram_id)
    if user_state == 'main':
        db.set_user_state(telegram_id, 'remove_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task that you want to remove.")


@dp.message_handler(commands=['mark'])
async def process_mark_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = db.get_user_state(telegram_id)
    if user_state == 'main':
        db.set_user_state(telegram_id, 'mark_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task you want to mark as completed.")


@dp.message_handler(commands=['task_detail'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = db.get_user_state(telegram_id)
    if user_state == 'main':
        db.set_user_state(telegram_id, 'detail_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task you want to know details.")


@dp.message_handler(commands=['list_tasks'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    db.set_user_state(message.from_user.id, 'main')
    tasks = db.list_user_tasks(telegram_id=telegram_id)
    res = "Tasks:\nID | Title"
    for task in tasks:
        res += f"\n{task[0]} {task[1]}"
        res += (" ✅" if task[4] else " ❌")
    await bot.send_message(telegram_id, res)


@dp.message_handler(content_types=['text', 'photo'])
async def echo_message(message: types.Message):
    telegram_id = message.from_user.id
    user_state = db.get_user_state(telegram_id)
    if user_state == 'main':
        await message.reply("Please enter command.")
    elif user_state == 'add_task_0':
        task_id = db.add_task(title=message.text, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'add_task_1')
        db.set_draft_task_id(telegram_id, task_id)
        await bot.send_message(telegram_id, "Enter description or send 'skip' word to skip this step.")
    elif user_state == 'add_task_1':
        if message.text != 'skip':
            task_id = db.get_draft_task_id(telegram_id=telegram_id)
            db.update_task(description=message.text, task_id=task_id, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'add_task_2')
        await bot.send_message(telegram_id, "Send me an help image or send 'skip' word to skip this step.")
    elif user_state == 'add_task_2':
        if message.text != 'skip':
            task_id = db.get_draft_task_id(telegram_id=telegram_id)
            await message.photo[-1].download(destination_file=f'images/{task_id}')
            with open(f'images/{task_id}', 'rb') as f:
                content = f.read()
            os.remove(f"images/{task_id}")
            db.update_task(image_blob=content, task_id=task_id, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'main')
        await bot.send_message(telegram_id, "Successfully added task!")

    elif user_state == 'remove_task_0':
        task_id = db.get_draft_task_id(telegram_id=telegram_id)
        db.delete_user_task(task_id=task_id, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'main')
        await bot.send_message(telegram_id, "Task successfully removed")

    elif user_state == 'mark_task_0':
        task_id = db.get_draft_task_id(telegram_id=telegram_id)
        db.mark_as_completed(task_id=task_id, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'main')
        await bot.send_message(telegram_id, "Task successfully marked as completed ✅")

    elif user_state == 'detail_task_0':
        task_id = db.get_draft_task_id(telegram_id=telegram_id)
        task = db.get_task(task_id=task_id, telegram_id=telegram_id)
        db.set_user_state(telegram_id, 'main')
        res = f"ID: {task[0]}\nTitle: {task[1]}\nDescription: {task[2]}\nCompleted: "
        res += ("✅" if task[4] else "❌")
        await bot.send_message(telegram_id, res)
        await bot.send_photo(telegram_id, task[3])
    # await bot.send_message(message.from_user.id, message.text)


if __name__ == '__main__':
    db.create_tables()
    executor.start_polling(dp)
