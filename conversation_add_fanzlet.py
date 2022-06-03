from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters


class conversation_state:
    class state_tuple:
        def __init__(self):
            self.image_name = None
            self.image = None

    def __init__(self):
        self.storage = dict()

    def assure_exists(self, user):
        if not user in self.storage:
            self.storage[user] = conversation_state.state_tuple()

    def process_complete(self, user):
        state = self.storage[user]
        state.image.get_file().download(f'./assets/{state.image_name}.png')

    def add_name(self, user, name):
        self.assure_exists(user)
        self.storage[user].image_name = name

    def add_image(self, user, image):
        self.assure_exists(user)
        self.storage[user].image = image
        self.process_complete(user)

    def clear(self, user):
        self.assure_exists(user)
        del self.storage[user]

storage = conversation_state()


REQUIRE_NAME, REQUIRE_FILE = range(2)


def make_handler():
    return ConversationHandler(
        entry_points = [
            CommandHandler(
                'add_fanzlet',
                lambda u, c: (u.message.reply_text('What is the name of your fanzlet?'), REQUIRE_NAME)[1]
            )
        ],
        fallbacks = [
            CommandHandler(
                'cancel',
                lambda u, c: (
                    storage.clear(u.message.from_user.id),
                    u.message.reply_text('Nevermind then...'),
                    ConversationHandler.END
                )[2]
            )
        ],
        states = {
            REQUIRE_NAME: [ MessageHandler(
                Filters.text & ~Filters.command,
                lambda u, c: (
                    storage.add_name(u.message.from_user.id, u.message.text),
                    u.message.reply_text('Please send me your fanzlet as a PNG. Make sure to send it as a file so Telegram doesn\'t remove the transparency.'),
                    REQUIRE_FILE
                )[2]
            ) ],
            REQUIRE_FILE: [ MessageHandler(
                Filters.document.mime_type('image/png'),
                lambda u, c: (
                    storage.add_image(u.message.from_user.id, u.message.document),
                    u.message.reply_text('Fanzlet has been added. Counter-terrorists win.'),
                    ConversationHandler.END
                )[2]
            ) ]
        }
    )