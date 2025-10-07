from typing import Union


from telegram import InlineKeyboardMarkup


from telegram_bot_discussion.button.button import Button
from telegram_bot_discussion.button.coder_interface import CoderInterface


def change_button_at_keyboard(
    where: InlineKeyboardMarkup,
    change_from_button: Button,
    change_to_button: Union[Button, None],
    coder: CoderInterface,
) -> InlineKeyboardMarkup:
    """Help function for find and change button in `InlineKeyboardMarkup` to other button or delete it, if other button is `None`."""
    reply_markup_inline_keyboard = list(map(list, where.inline_keyboard))
    was_change = False
    row_id_decrement = 0
    new_reply_markup_inline_keyboard = []
    for row_id, reply_markup_buttons_row in enumerate(reply_markup_inline_keyboard):
        new_reply_markup_inline_keyboard[row_id - row_id_decrement] = []
        for _, reply_markup_button in enumerate(reply_markup_buttons_row):
            if change_from_button.equals(
                reply_markup_button,
                coder,
            ):
                # reply_markup_inline_keyboard[row_id-row_id_decrement][column_id-column_id_decrement] = (
                #     change_to_button.as_button(coder)
                # )
                was_change = True
                if change_to_button:
                    new_reply_markup_inline_keyboard[row_id].append(change_to_button)
            else:
                new_reply_markup_inline_keyboard[row_id].append(change_from_button)
        if len(new_reply_markup_inline_keyboard[row_id - row_id_decrement]) == 0:
            row_id_decrement += 1
    if was_change:
        return InlineKeyboardMarkup(new_reply_markup_inline_keyboard)
    return where  # None
