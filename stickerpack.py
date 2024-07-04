import telegram.error
from telegram import error, StickerSet
from serialized_dict import serialized_dict


stickerpacks  = serialized_dict('./assets/stickerpacks.json') # User => Pack Count
sticker_limit = 120


def stickerpack_raw_name(update, bot, index):
    return f'fanzlets_{update.message.from_user.id}_{index}_by_{bot.username}'


def get_stickerpack(bot, raw_name):
    # bot.get_sticker_set(raw_name) is broken due to Telegram API changes.
    # Updating to a new version of python_telegram_bot would require rewriting the entire bot, as it has very thoroughly changed.
    # Instead, just make the API request manually.
    resp = bot._request.post(
        f"{bot.base_url}/getStickerSet",
        {
            "name": raw_name,
        },
    )

    resp['is_animated'] = False
    resp['is_video'] = False

    return StickerSet.de_json(resp, bot)
    # return bot.get_sticker_set(raw_name)


def is_stickerpack_full(bot, raw_name):
    return len(get_stickerpack(bot, raw_name).stickers) >= sticker_limit


def add_sticker_to_existing_pack(update, bot, raw_name, image):
    success = bot.add_sticker_to_set(
        update.message.from_user.id,
        raw_name,
        "🦊",
        png_sticker = image
    )

    if not success: raise RuntimeError('Failed to add sticker to pack.')
    return get_stickerpack(bot, raw_name).stickers[-1]


def make_stickerpack(update, bot, image, index):
    raw_name = stickerpack_raw_name(update, bot, index)
    display_name = f'{update.message.from_user.username}s Fanzlets {index}'

    try:
        success = bot.create_new_sticker_set(
            user_id     = update.message.from_user.id,
            name        = raw_name,
            title       = display_name,
            emojis      = "🦊",
            png_sticker = image
        )

        if not success: raise RuntimeError('Failed to create sticker pack.')

        stickerpacks.insert(str(update.message.from_user.id), str(index))
        return get_stickerpack(bot, raw_name)
    except telegram.error.BadRequest as e:
        if "peer_id_invalid" in e.message.lower():
            raise RuntimeError('You must start a DM session with the bot before it can create stickers in your name.')
        else: raise e


def add_sticker_for_user(update, bot, image):
    id = update.message.from_user.id

    has   = stickerpacks.contains(str(id))
    count = 0 if not has else int(stickerpacks.get(str(id)))
    full  = not has or is_stickerpack_full(bot, stickerpack_raw_name(update, bot, count))

    if full:
        pack = make_stickerpack(update, bot, image, count + 1)
        return pack.stickers[-1]
    else:
        return add_sticker_to_existing_pack(update, bot, stickerpack_raw_name(update, bot, count), image)


def make_sticker(update, bot, file):
    with open(file, 'rb') as handle:
        return add_sticker_for_user(update, bot, handle)