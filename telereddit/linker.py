import traceback

from telegram import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from sentry_sdk import capture_exception
from config.config import MAX_TRIES, EDIT_KEYBOARD, EDIT_FAILED_KEYBOARD, NO_EDIT_KEYBOARD

import reddit
import helpers

from status import OkStatus, KoStatus

from media import ContentType


class Linker:
    @classmethod
    def set_bot(cls, bot):
        cls.bot = bot

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def send_random_posts(self, text, num_posts=None):
        subreddits = helpers.get_subreddit_names(text)[0:num_posts]
        for subreddit in subreddits:
            for _ in range(MAX_TRIES):
                status = self.send_post(helpers.get_random_post_url(subreddit))
                if status.ok:
                    break
            if not status.ok:
                self._send_exception_message(status.err_msg)

    def send_post_from_url(self, post_url):
        status = self.send_post(post_url)
        if not status.ok:
            self._send_exception_message(status.err_msg, keyboard=False)

    def send_post(self, post_url):
        status = reddit.get_post(post_url)
        if not status.ok:
            if status.err_code == 'not_found':
                self.bot.sendMessage(self.chat_id, status.err_msg)
                return OkStatus()
            else:
                return status

        post = status.data
        if post.media and post.media.size and post.media.size > 20000000:
            return KoStatus("I'm sorry, media is too big to be sent.")

        # if it is not a random post (e.g. shared via link) don't show the
        # edit custom keyboard
        args = dict(chat_id=self.chat_id,
                    reply_markup=NO_EDIT_KEYBOARD if post_url else EDIT_KEYBOARD,
                    disable_web_page_preview=True,
                    parse_mode='MarkdownV2')
        try:
            if post.get_type() == ContentType.TEXT:
                self.bot.sendMessage(text=post.get_msg(), **args)
            elif post.get_type() == ContentType.YOUTUBE:
                args["disable_web_page_preview"] = False
                self.bot.sendMessage(text=post.get_msg(), **args)
            elif post.get_type() == ContentType.GIF:
                self.bot.sendDocument(document=post.media.url, caption=post.get_msg(), **args)
            elif post.get_type() == ContentType.VIDEO:
                self.bot.sendVideo(video=post.media.url, caption=post.get_msg(), **args)
            elif post.get_type() == ContentType.PHOTO:
                self.bot.sendPhoto(photo=post.media.url, caption=post.get_msg(), **args)

        except Exception as e:
            capture_exception(e)
            traceback.print_exc()
            return KoStatus("I'm sorry, there has been an error in sending the post.")

        return OkStatus()

    def edit_result(self, update):
        '''
        Edits the given message with a new post from that subreddit, and edits the
        keyboard markup to give the user the ability to edit or confirm the message.
        '''
        message = update.effective_message
        message_id = message.message_id
        text = (message.caption or message.text) + '\n'
        subreddit = helpers.get_subreddit_name(text, True)
        if subreddit is None:
            return

        tries = 0
        while tries < MAX_TRIES:
            status = reddit.get_post(subreddit)
            if not status.ok:
                continue

            post = status.data
            msg_is_text = message.caption is None

            if ((msg_is_text and message.text_markdown == post.get_msg())
               or message.caption_markdown == post.get_msg()):
                tries += 1
                continue  # if post is the same retry

            if not msg_is_text and post.get_type() in [ContentType.TEXT, ContentType.YOUTUBE]:
                tries += 1
                continue  # if message is not text and post is retry

            args = dict(chat_id=self.chat_id,
                        message_id=message_id,
                        parse_mode='MarkdownV2',
                        reply_markup=EDIT_KEYBOARD,
                        disable_web_page_preview=True)

            if msg_is_text:
                if post.get_type() == ContentType.TEXT:
                    self.bot.editMessageText(post.get_msg(), **args)
                elif post.get_type() == ContentType.YOUTUBE:
                    self.bot.editMessageText(post.get_msg(), reply_markup=EDIT_KEYBOARD, **args)
            else:
                media_args = dict(media=post.media.url, caption=post.get_msg(), parse_mode='MarkdownV2')
                if post.get_type() == ContentType.GIF:
                    media = InputMediaDocument(**media_args)
                elif post.get_type() == ContentType.VIDEO:
                    media = InputMediaVideo(**media_args)
                elif post.get_type() == ContentType.PHOTO:
                    media = InputMediaPhoto(**media_args)
                self.bot.editMessageMedia(media=media, **args)

            break

        if tries >= MAX_TRIES:
            self.bot.editMessageReplyMarkup(self.chat_id, message_id,
                                            reply_markup=EDIT_FAILED_KEYBOARD)

    def _send_exception_message(self, msg, keyboard=True):
        '''Handles the errors created in post retrieval and sending.'''
        if keyboard:
            self.bot.sendMessage(self.chat_id, msg, 'MarkdownV2', reply_markup=NO_EDIT_KEYBOARD)
        else:
            self.bot.sendMessage(self.chat_id, msg, 'MarkdownV2')
