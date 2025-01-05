import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.methods import DeleteWebhook
from aiogram.filters import Command

from dealer import Dealer
from player import Player


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
dealer = Dealer()
player_list = []
table_cards = []

@dp.message(Command('info'))
async def info(message: types.Message):
    chat_id = message.chat.id
    await message.answer(f"Your chat ID is {chat_id}")


@dp.message(Command('table'))
async def deal_table(message: types.Message):
    try:
        global table_cards

        if not table_cards:
            table_cards = dealer.deal_cards(5)
            await message.answer(f"Table: {table_cards}")
        else:
            await message.answer(f"Table: {table_cards}")
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


@dp.message(Command('hand'))
async def deal_hand(message: types.Message):
    try:
        global player_list
        user = message.from_user.first_name

        if any(player.name == user for player in player_list):
            await message.answer(f"{user} already in game")
        else:
            player = Player(user)
            card = dealer.deal_cards(2)
            player.set_hand(card)
            player_list.append(player)
            await message.answer(f"{user}'s hand: ||{card}||", parse_mode='MarkdownV2')
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


@dp.message(Command('players'))
async def deal_hand(message: types.Message):
    try:
        if not player_list:
            await message.answer("Player list is empty")
        else:
            output = ''
            for player in player_list:
                output = output + (f"{player.name}\n")
            await message.answer(output)
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


@dp.message(Command('check'))
async def calc_cards(message: types.Message):
    try:
        global player_list
        global table_cards

        if player_list and table_cards:
            for player in player_list:
                print(f"{player.name}'s full hand:", player.hand + table_cards)
                player.score, player.combination = dealer.calc_score(player.hand + table_cards);
                print(f"{player.name}'s has combination: {player.combination} score: {player.score}")

            max_score = max(player_list, key=lambda player: player.score).score
            win_list = [player for player in player_list if player.score == max_score]
            output = ''
            for player in win_list:
                output = output + (f"{player.name} wins! combination: {player.combination} score: {player.score}\n")
            await message.answer(output)

            player_list = []
            table_cards = []
            dealer.shuffle_deck()

        else:
            await message.answer(f"The game has not started. Deal the cards")
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")

@dp.message(Command('clean'))
async def delete_bot_messages(message: types.Message):
    chat_id = message.chat.id
    updates = await bot.get_updates()

    for update in updates:
        if update.message and update.message.from_user.is_bot and update.message.chat.id == chat_id:
            try:
                print(f"Delete message {update.message.message_id}")
                await bot.delete_message(chat_id, update.message.message_id)
            except Exception as e:
                print(f"Failed to delete message {update.message.message_id}: {e}")

    await message.answer("All bot messages have been deleted!")

@dp.message(Command('debug'))
async def debug(message: types.Message):
    message.message_id

    resp = await message.edit_text()
    print(f"Resp: {resp}")


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    print("Ready to start")
    await dp.start_polling(bot)


if __name__ == "__main__":
    dealer.shuffle_deck()
    asyncio.run(main())
