import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.methods import DeleteWebhook
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from dealer import Dealer
from player import Player, Action

welcom_msg = 'Table: [][][]'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
dealer = Dealer()
player_map = {}
table_cards = []
msg_map = {}
main_msg = types.Message
is_game_in_progress = False
big_blind = 20
blind_pos = 0
bank = 0

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


async def deal_hand(message: types.Message, player: Player):
    try:
        if player.hand == []:
            print(f'Deal new hand for {player.name}')
            player.set_hand(dealer.deal_cards(2))

        if isinstance(message, CallbackQuery):
            message = message.message
        msg = await message.answer(f"{player.name}'s hand: ||{player.hand}||", parse_mode='MarkdownV2',
                                   reply_markup=round_kb)
        msg_map[msg.message_id] = player.id

    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


async def add_to_player_map(user: str, message: types.Message):
    """
    Adds a player to the player list if they are not already in the game.

    Args:
        user (str): The name of the user.
        message (types.Message): The message object from the user.

    """
    if len(player_map.keys()) > 8:
        await message.answer("Table is full")
        return
    if user in player_map.keys():
        await message.answer(f"{user} already in game")
        return

    player_map[user] = Player(user)


@dp.message(Command('hand'))
async def show_hand(message: types.Message):
    name = message.from_user.first_name
    try:
        await deal_hand(message, player_map[name])
    except KeyError:
        await message.answer(f"{name} is not found")

@dp.message(Command('players'))
async def players(message: types.Message):
    try:
        if not player_map:
            await message.answer("Player list is empty")
        else:
            output = ''
            for player in player_map.values():
                output = output + (f"{player.name} {player.id} {player.action.value}\n")
            await message.answer(output)
    except Exception as e:
        await message.answer(f"Something goes wrong: {e}")


async def calc_cards(message: types.Message):
    global table_cards

    try:
        if player_map and table_cards:
            for player in player_map.values():
                print(f"{player.name}'s action: {player.action}")
                if player.action != Action.FOLD:
                    print(f"{player.name}'s full hand:", player.hand + table_cards)
                    player.score, player.combination = dealer.calc_score(player.hand + table_cards);
                    print(f"{player.name}'s has combination: {player.combination} score: {player.score}")

            max_score = max(player_map.values(), key=lambda player: player.score).score

            win_list = [player for player in player_map.values() if player.score == max_score]

            output = ''
            for player in win_list:
                output = output + (f"{player.name} wins! combination: {player.combination} score: {player.score}\n")

            table_cards = []
            dealer.shuffle_deck()
            for player in player_map.values():
                player.hand = []
                player.score = 0

            await message.edit_text(f"{welcom_msg}", reply_markup=main_kb)
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
    global is_game_in_progress
    global main_msg

    if is_game_in_progress:
        main_msg = await message.answer(gen_main_view_text(), reply_markup=start_kb)
    else:
        player_map = {}
        is_game_in_progress = True
        main_msg = await message.answer(f"{welcom_msg}", reply_markup=start_kb)


@dp.callback_query(lambda callback: callback.data == "join")
async def button_join(callback: CallbackQuery):
    print(f'Callback: {callback}')
    if table_cards:
        await callback.answer('The game is in progress. Try when table is empty')
    else:
        user = callback.from_user.first_name
        await add_to_player_map(user=user, message=callback)
        await deal_hand(callback, player_map[user])
        await main_msg.edit_text(f"{welcom_msg} {gen_main_view_text()}", parse_mode='MarkdownV2', reply_markup=main_kb)
        await callback.answer('Joined the game')


@dp.callback_query(lambda callback: callback.data == "leave")
async def button_leave(callback: CallbackQuery):
    del player_map[callback.from_user.first_name]
    await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=start_kb)
    await callback.answer('You left the game')


@dp.callback_query(lambda callback: callback.data == "check")
async def button_check(callback: CallbackQuery):
    name = callback.from_user.first_name
    if is_authorized(callback.message.message_id, name):
        set_action_by_name(name, Action.CHECK)
        await process_round()
        await callback.answer(f'{name} check')
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
    player = player_map[name]
    if player.action != Action.FOLD:
        print(f"Set action {player.action.value} for {player.name}")
        player.set_action(action)
        print(f"Current action {player.action.value} for {player.name}")


def is_round_done():
    return not any(player.action == Action.NONE for player in player_map.values())


def gen_main_view_text():
    player_map_str = '\nPlayer list: \n'
    for player in player_map.values():
        player_map_str = player_map_str + f": {player.name} {player.action.value} {player.bank}\n"
    if table_cards:
        return f"Table: {table_cards}\n" + player_map_str
    else:
        return player_map_str


async def process_round():
    if is_round_done():
        global table_cards
        if len(table_cards) == 5:
            await calc_cards(main_msg)
        else:
            await deal_table(main_msg)
        for player in player_map.values():
            player.set_action(Action.NONE)
    else:
        await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=main_kb)

def is_authorized(message_id, name):
    return any(msg_map[message_id] == player.id and player.name == name for player in player_map.values())


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    print("Ready to start")
    await dp.start_polling(bot)


if __name__ == "__main__":
    dealer.shuffle_deck()
    asyncio.run(main())
