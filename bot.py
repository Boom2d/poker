import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.methods import DeleteWebhook
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from dealer import Dealer
from player import Player, Action

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
dealer = Dealer()
player_list = []
table_cards = []
msg_map = {}
main_msg = types.Message

start_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Join", callback_data="join")]])

main_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Leave", callback_data="leave")]]
)

round_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Check", callback_data="check"),
                      InlineKeyboardButton(text="Fold", callback_data="fold")]]
)


@dp.message(Command('info'))
async def info(message: types.Message):
    chat_id = message.chat.id
    await message.answer(f"Your chat ID is {chat_id}")


async def deal_table(message: types.Message):
    try:
        global table_cards

        if table_cards:
            if len(table_cards) >= 5:
                pass
            elif len(table_cards) >= 3:
                table_cards.append(dealer.deal_cards(1)[0])
        else:
            table_cards = dealer.deal_cards(3)
        await message.edit_text(gen_main_view_text(), reply_markup=main_kb)
    except Exception as e:
        await message.edit_text(f"Something goes wrong: {e}")


async def deal_hand(message: types.Message):
    try:
        global player_list
        user = message.from_user.first_name

        if any(player.name == user for player in player_list):
            await message.answer(f"{user} already in game")
        else:
            player = Player(user)
            player.id = message.from_user.id
            card = dealer.deal_cards(2)
            player.set_hand(card)
            player_list.append(player)

            if isinstance(message, CallbackQuery):
                message = message.message
            await message.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=main_kb)

            msg = await message.answer(f"{user}'s hand: ||{card}||", parse_mode='MarkdownV2', reply_markup=round_kb)
            msg_map[msg.message_id] = player.id
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


@dp.message(Command('players'))
async def players(message: types.Message):
    try:
        if not player_list:
            await message.answer("Player list is empty")
        else:
            output = ''
            for player in player_list:
                output = output + (f"{player.name} {player.id} {player.action.value}\n")
            await message.answer(output)
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


async def calc_cards(message: types.Message):
    try:
        global player_list
        global table_cards

        if player_list and table_cards:
            for player in player_list:
                if player.action != Action.FOLD:
                    print(f"{player.name}'s full hand:", player.hand + table_cards)
                    player.score, player.combination = dealer.calc_score(player.hand + table_cards);
                    print(f"{player.name}'s has combination: {player.combination} score: {player.score}")

            max_score = max(player_list, key=lambda player: player.score).score

            table_cards = []
            dealer.shuffle_deck()

            win_list = [player for player in player_list if player.score == max_score]
            output = ''
            for player in win_list:
                output = output + (f"{player.name} wins! combination: {player.combination} score: {player.score}\n")

            await message.edit_text(f"Table: [][][]", reply_markup=main_kb)
            await message.answer(output)
        else:
            await message.edit_text(f"{message.text}\n\nThe game has not started. Deal the cards", reply_markup=main_kb)
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


@dp.message(Command('game'))
async def game(message: types.Message):
    print(f"Game message {message}")
    global main_msg
    player_list = []
    main_msg = await message.answer(f"Table: [][][]", reply_markup=start_kb)


@dp.callback_query(lambda callback: callback.data == "join")
async def button_join(callback: CallbackQuery):
    if table_cards:
        await callback.answer('The game is in progress. Try when table is empty')
    else:
        await deal_hand(callback)
        await callback.answer('Joined the game')


@dp.callback_query(lambda callback: callback.data == "leave")
async def button_leave(callback: CallbackQuery):
    for player in player_list:
        if player.name == callback.from_user.first_name:
            player_list.remove(player)
            await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=start_kb)
            await callback.answer('You left the game')

@dp.callback_query(lambda callback: callback.data == "check")
async def button_check(callback: CallbackQuery):
    name = callback.from_user.first_name
    id = callback.from_user.id
    if is_authorized(callback.message.message_id, name):
        if any(player.id == callback.from_user.id and player.action != Action.FOLD for player in player_list):
            set_action_by_name(name, Action.CHECK)
            await process_round()
            await callback.answer(f'{callback.from_user.first_name} check')
        else:
            await callback.answer('You already submit fold')
    else:
        await callback.answer('You are not allowed to do this')


@dp.callback_query(lambda callback: callback.data == "fold")
async def button_fold(callback: CallbackQuery):
    name = callback.from_user.first_name
    if is_authorized(callback.message.message_id, name):
        set_action_by_name(name, Action.FOLD)
        await process_round()
        await callback.answer(f'{name} fold')
    else:
        await callback.answer('You are not allowed to do this')


def set_action_by_name(name, action):
    for player in player_list:
        if player.name == name and player.action != Action.FOLD:
            print(f"Set action {player.action.value} for {player.name}")
            player.set_action(action)
            print(f"Current action {player.action.value} for {player.name}")


def is_round_done():
    return not any(player.action == Action.NONE for player in player_list)


def gen_main_view_text():
    player_list_str = '\nPlayer list: \n'
    for player in player_list:
        player_list_str = player_list_str + f"{player_list.index(player)} {player.name} {player.action.value} {player.bank}\n"
    if table_cards:
        return f"Table: {table_cards}\n" + player_list_str
    else:
        return player_list_str


async def process_round():
    if is_round_done():
        for player in player_list:
            player.set_action(Action.NONE)
        if len(table_cards) == 5:
            await calc_cards(main_msg)
        else:
            await deal_table(main_msg)
    else:
        await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=main_kb)


def is_authorized(message_id, name):
    return any(msg_map[message_id] == player.id and player.name == name for player in player_list)


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    print("Ready to start")
    await dp.start_polling(bot)


if __name__ == "__main__":
    dealer.shuffle_deck()
    asyncio.run(main())
