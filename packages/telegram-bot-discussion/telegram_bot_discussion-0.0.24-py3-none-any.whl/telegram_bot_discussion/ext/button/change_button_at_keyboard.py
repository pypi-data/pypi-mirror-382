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
    new_reply_markup_inline_keyboard = []
    for row_id, reply_markup_buttons_row in enumerate(reply_markup_inline_keyboard):
        new_row = []
        for _, reply_markup_button in enumerate(reply_markup_buttons_row):
            if change_from_button.equals(
                reply_markup_button,
                coder,
            ):
                was_change = True
                if change_to_button:
                    new_row.append(change_to_button)
            else:
                new_row.append(reply_markup_button)
        if len(new_row) > 0:
            new_reply_markup_inline_keyboard.append(new_row)
    if was_change:
        return InlineKeyboardMarkup(new_reply_markup_inline_keyboard)
    return where  # None
