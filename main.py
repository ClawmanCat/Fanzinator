import telegram
from telegram.ext import Updater, CommandHandler

import fanzo_builder as builder
import stickerpack as stickerpack
import conversation_add_fanzlet as add_fanzlet
from serialized_dict import serialized_dict

import os
import traceback
import hashlib


with open(os.path.join('assets', 'token.txt'), 'r') as token_file:
    token = token_file.read()

updater = Updater(token = token, use_context = True)



image_hashes = serialized_dict('./assets/image_hashes.json')


def add_command(dispatcher, name, command, pass_args = True):
    handler = CommandHandler(name, command, pass_args = pass_args)
    dispatcher.add_handler(handler)


def add_conversation(dispatcher, handler):
    dispatcher.add_handler(handler)


def command_build_image_common(update, context, make_image_fn):
    try:
        arg_hash  = hashlib.md5(' '.join(context.args).encode('utf8')).hexdigest()
        dest_path = f'./assets/hs_{arg_hash}.png'

        if not os.path.exists(dest_path):
            img = make_image_fn(context.args)
            img.save(dest_path)

        with open(dest_path, 'rb') as handle:
            image_id = update.message.reply_photo(handle).photo[-1].get_file().file_id
            image_hashes.insert(str(image_id), arg_hash)
    except BaseException as e:
        print(f'Error: { str(e) }')
        print(traceback.format_exc())

        update.message.reply_text(f'Error: { str(e) }')


def command_fanzinate(update, context):
    command_build_image_common(update, context, builder.make_fanzination)


def command_sofa_fanzinate(update, context):
    command_build_image_common(update, context, builder.make_sofa_fanzination)


def command_get_hash(update, context):
    arg_hash = hashlib.md5(' '.join(context.args).encode('utf8')).hexdigest()
    update.message.reply_text(f'Result will be hashed as: {arg_hash}')


def command_list_fanzlets(update, context):
    result = []
    for img_path in os.listdir('./assets'):
        name, ext = os.path.splitext(os.path.basename(img_path))
        if not name[0:2] == 'hs' and ext == '.png': result.append(name)

    update.message.reply_text('The following fanzlets are available to fanzinate: ' + ', '.join(result))


def command_make_sticker(update, context):
    if update.message.reply_to_message is None or update.message.reply_to_message.photo is None:
        update.message.reply_text('Please reply to a message from the bot containing a fanzlet when using this command.')
        return

    image_id = update.message.reply_to_message.photo[-1].get_file().file_id
    if not image_hashes.contains(str(image_id)):
        update.message.reply_text('Please reply to a message from the bot containing a fanzlet when using this command.')
        return

    image_hash = image_hashes.get(str(image_id))

    try:
        sticker = stickerpack.make_sticker(update, updater.bot, f'./assets/hs_{image_hash}.png')
        update.message.reply_sticker(sticker)
    except BaseException as e:
        print(f'Error: {str(e)}')
        print(traceback.format_exc())

        update.message.reply_text(f'Error: {str(e)}')


def main():
    dispatcher = updater.dispatcher

    add_command(dispatcher, 'fanzinate',      command_fanzinate)
    add_command(dispatcher, 'sofanate',       command_sofa_fanzinate)
    add_command(dispatcher, 'list_fanzlets',  command_list_fanzlets)
    add_command(dispatcher, 'make_stickling', command_make_sticker)
    add_command(dispatcher, 'hash_of',        command_get_hash)
    add_conversation(dispatcher, add_fanzlet.make_handler())

    updater.start_polling()


if __name__ == '__main__': main()