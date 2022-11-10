import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import db

bot = Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await db.add_user(message.from_user.id)
    telegram_id = message.from_user.id
    await bot.send_message(telegram_id, "Welcome in my ToDo app!")


@dp.message_handler(commands=['add_task'])
async def process_add_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = (await db.get_user_state(telegram_id))[0]
    if user_state == 'main':
        await db.set_user_state(telegram_id, 'add_task_0')
        await bot.send_message(telegram_id, "Enter title for your task")


@dp.message_handler(commands=['remove_task'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = (await db.get_user_state(telegram_id))[0]
    if user_state == 'main':
        await db.set_user_state(telegram_id, 'remove_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task that you want to remove.")


@dp.message_handler(commands=['mark'])
async def process_mark_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = (await db.get_user_state(telegram_id))[0]
    if user_state == 'main':
        await db.set_user_state(telegram_id, 'mark_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task you want to mark as completed.")


@dp.message_handler(commands=['task_detail'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    user_state = (await db.get_user_state(telegram_id))[0]
    if user_state == 'main':
        await db.set_user_state(telegram_id, 'detail_task_0')
        await bot.send_message(telegram_id, "Enter task_id for task you want to know details.")


@dp.message_handler(commands=['list_tasks'])
async def process_remove_task_command(message: types.Message):
    telegram_id = message.from_user.id
    await db.set_user_state(message.from_user.id, 'main')
    tasks = await db.list_user_tasks(telegram_id=telegram_id)
    res = "Tasks:\nID | Title"
    for task in tasks:
        res += f"\n{task[0]} {task[1]}"
        res += (" ✅" if task[4] else " ❌")
    await bot.send_message(telegram_id, res)


async def add_task_title(msg, telegram_id):
    task_id = await db.add_task(title=msg.text, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'add_task_1')
    await db.set_draft_task_id(telegram_id, tuple(task_id)[0])
    await bot.send_message(telegram_id, "Enter description or send 'skip' word to skip this step.")


async def add_task_description(msg, telegram_id):
    if msg.text != 'skip':
        task_id = (await db.get_draft_task_id(telegram_id=telegram_id))[0]
        await db.update_task(description=msg.text, task_id=task_id, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'add_task_2')
    await bot.send_message(telegram_id, "Send me an help image or send 'skip' word to skip this step.")


async def add_task_img(msg, telegram_id):
    if msg.text != 'skip':
        task_id = (await db.get_draft_task_id(telegram_id=telegram_id))[0]
        await msg.photo[-1].download(destination_file=f'images/{task_id}')
        with open(f'images/{task_id}', 'rb') as f:
            content = f.read()
        os.remove(f"images/{task_id}")
        await db.update_task(image_blob=content, task_id=task_id, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'main')
    await bot.send_message(telegram_id, "Successfully added task!")


async def remove_task(msg, telegram_id):
    task_id = msg.text
    await db.delete_user_task(task_id=task_id, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'main')
    await bot.send_message(telegram_id, "Task successfully removed")


async def mark_task(msg, telegram_id):
    task_id = msg.text
    await db.mark_as_completed(task_id=task_id, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'main')
    await bot.send_message(telegram_id, "Task successfully marked as completed ✅")


async def detail_task(msg, telegram_id):
    task_id = msg.text
    task = await db.get_task(task_id=task_id, telegram_id=telegram_id)
    await db.set_user_state(telegram_id, 'main')
    res = f"ID: {task[0]}\nTitle: {task[1]}\nDescription: {task[2]}\nCompleted: "
    res += ("✅" if task[4] else "❌")
    await bot.send_message(telegram_id, res)
    if task[3]:
        await bot.send_photo(telegram_id, task[3])


async def main_state(msg, telegram_id):
    await bot.send_message(telegram_id, f"{msg.text} is not a command!")


@dp.message_handler(content_types=['text', 'photo'])
async def echo_message(message: types.Message):
    telegram_id = message.from_user.id
    user_state = (await db.get_user_state(telegram_id))[0]

    routes = {
        "main": main_state,
        "add_task_0": add_task_title,
        "add_task_1": add_task_description,
        "add_task_2": add_task_img,
        "remove_task_0": remove_task,
        "mark_task_0": mark_task,
        "detail_task_0": detail_task
    }
    await routes[user_state](message, telegram_id)


if __name__ == '__main__':
    # db.create_tables()
    executor.start_polling(dp)
