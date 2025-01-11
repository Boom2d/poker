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
player_map: dict[str, Player] = {}
msg_map: dict[str, types.Message] = {}
table_cards = []
main_msg = types.Message
is_game_in_progress = False
big_blind = 20
bid = big_blind
blind_pos = 0
bank = 0

start_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Join", callback_data="join")]])
main_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Leave", callback_data="leave")]])


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
            player.hand = dealer.deal_cards(2)
        else:
            print(f'Show existing hand')

        if isinstance(message, CallbackQuery):
            message = message.message
        msg = await message.answer(f"{player.name}'s hand: ||{player.hand}||", parse_mode='MarkdownV2')
        player.id = message.from_user.id
        msg_map[player.id] = msg
        print(f'msg_map {msg_map}')

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
    player_map[user].pos = len(player_map.keys()) - 1


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
    try:
        if player_map and table_cards:
            fold_output = ''
            for player in player_map.values():
                print(f"{player.name}'s action: {player.action}")
                if player.action != Action.FOLD:
                    print(f"{player.name}'s full hand:", player.hand + table_cards)
                    player.score, player.combination = dealer.calc_score(player.hand + table_cards);
                    print(f"{player.name}'s has combination: {player.combination} score: {player.score}")
                else:
                    fold_output = fold_output + f"\n{player.name} fold =(\n"

            max_score = max(player_map.values(), key=lambda player: player.score).score

            win_list = [player for player in player_map.values() if player.score == max_score and player.score > 0]

            output = ''
            for player in win_list:
                #gain = bank / len(win_list)
                #player.bank = player.bank + gain # 1000.0
                output = output + (
                    f"{player.name} wins! combination: {player.combination} score: {player.score} got $\n")

            await message.edit_text(f"{welcom_msg}", reply_markup=main_kb)
            await message.answer(output + fold_output)
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
        dealer.shuffle_deck()
        is_game_in_progress = True
        main_msg = await message.answer(f"{welcom_msg}", reply_markup=start_kb)


@dp.message(Command('stop'))
async def game(message: types.Message):
    global is_game_in_progress
    global main_msg

    is_game_in_progress = False
    await main_msg.edit_text('The game has stopped', reply_markup=start_kb)


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
        await game_flow()


@dp.callback_query(lambda callback: callback.data == "leave")
async def button_leave(callback: CallbackQuery):
    del player_map[callback.from_user.first_name]
    await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=start_kb)
    await callback.answer('You left the game')


@dp.callback_query(lambda callback: callback.data == "call")
async def button_call(callback: CallbackQuery):
    await do_turn(callback, Action.CALL)


@dp.callback_query(lambda callback: callback.data == "raise")
async def button_raise(callback: CallbackQuery):
    await do_turn(callback, Action.RAISE)


@dp.callback_query(lambda callback: callback.data == "check")
async def button_check(callback: CallbackQuery):
    await do_turn(callback, Action.CHECK)


@dp.callback_query(lambda callback: callback.data == "fold")
async def button_fold(callback: CallbackQuery):
    await do_turn(callback, Action.FOLD)


async def show_button(person_id: str, button_list: []):
    msg = msg_map[person_id]
    round_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button, callback_data=button.lower()) for button in button_list]])
    print(f'Show_button msg.text: {msg.text}')
    await msg.edit_text(msg.text + "\nYour turn", parse_mode='MarkdownV2', reply_markup=round_kb)


async def do_turn(callback: CallbackQuery, action: Action):
    name = callback.from_user.first_name
    if is_authorized(callback.message.message_id, name):
        if (player_map[name].action != action):
            player_map[name].action = action
            print(f"Set action {action.value} for {name}")
            print('Turn off buttons')

            main_view = gen_main_view_text()
            if main_msg.text != main_view:
                await main_msg.edit_text(main_view, parse_mode='MarkdownV2', reply_markup=main_kb)

            msg = callback.message.text.replace('\nYour turn', '')
            if msg != callback.message.text:
                print(f'New msg: {msg} Callback text: {callback.message.text}')
                await callback.message.edit_text(msg, parse_mode='MarkdownV2',
                                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[[]]))
            await callback.answer(f'{name} {action.value}')
    else:
        print(f'You are not allowed to do this: {name} {callback.message.message_id}')
        await callback.answer('You are not allowed to do this')


def gen_main_view_text():
    player_map_str = '\nPlayer list: \n'
    for player in player_map.values():
        player_map_str = player_map_str + f": {player.name} {player.action.value} {player.bank}\n"
    if table_cards:
        return f"Table: {table_cards}\n" + player_map_str
    else:
        return player_map_str


def is_authorized(message_id, name):
    return any(msg_map[player.id].message_id == message_id and player.name == name for player in player_map.values())


async def game_flow():
    global table_cards
    global bank
    global bid

    while is_game_in_progress:
        play_order = list(player.pos for player in player_map.values())
        play_order = play_order[blind_pos:] + play_order[:blind_pos]
        print(f'Order list: {play_order}')
        player_list = sorted(player_map.values(), key=lambda item: play_order.index(item.pos))
        print(f'Player order: {player_list}')
        print(f'Player order: {player_list[blind_pos].bank}')

        player_list[blind_pos].bank = player_list[blind_pos].bank - bid
        player_list[blind_pos].bid = bid
        await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=main_kb)

        # round
        print(f'Round condition {all([player.action == Action.NONE for player in player_list])}')
        while all([player.action == Action.NONE for player in player_list]):
            for player in player_list:
                if player != Action.FOLD:
                    print(f"Round deal: {player}")
                    if player.bid == bid:
                        print("Check phase")
                        await show_button(player.id, ['Check', 'Raise', 'Fold'])
                    else:
                        print("Call phase")
                        await show_button(player.id, ['Call', 'Raise', 'Fold'])
                    while player.action == Action.NONE:
                        print(f"Waiting for turn {player.name}")
                        await asyncio.sleep(2)
                        switch_action(player)
                else:
                    print(f"Skip the turn. {name} has fold")

            bank = + bid
            if len(table_cards) == 5:
                await calc_cards(main_msg)
                print(f'Result view: {gen_main_view_text()}')
                await main_msg.edit_text(gen_main_view_text() + "\nNext round will in 15sec", parse_mode='MarkdownV2',
                                         reply_markup=main_kb)
                await asyncio.sleep(15)
                reset_table()

                for player in player_map.values():
                    deal_hand(msg_map[player.id], player)
            else:
                for player in player_list:
                    player.set_action(Action.NONE)
                await deal_table(main_msg)
                await main_msg.edit_text(gen_main_view_text(), parse_mode='MarkdownV2', reply_markup=main_kb)


def reset_table():
    dealer.shuffle_deck()
    bid = big_blind
    table_cards = []
    for player in player_map.values():
        player.score = 0
        player.bid = 0
        player.hand = 0
        player.action = Action.NONE


def switch_action(player: Player):
    global bid

    match player.action:
        case Action.CHECK:
            pass
        case Action.CALL:
            player.bid = player.bank - (bid - player.bid)
        case Action.RAISE:
            player.bid = player.bid - (bid * 2 - player.bid)
            bid = bid * 2
        case Action.FOLD:
            player.bid = 0
        case _:
            return "Invalid action"


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    print("Ready to start")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
