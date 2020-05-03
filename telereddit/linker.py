from telegram import InputMediaPhoto, InputMediaVideo, InputMediaDocument

from telereddit.config.config import (
    MAX_TRIES,
    EDIT_KEYBOARD,
    EDIT_FAILED_KEYBOARD,
    NO_EDIT_KEYBOARD,
    DELETE_KEYBOARD,
)
import telereddit.reddit as reddit
import telereddit.helpers as helpers
from telereddit.models.media import ContentType
from telereddit.models.exceptions import (
    SubredditError,
    TeleredditError,
    MediaTooBigError,
    PostSendError,
    PostEqualsMessageError,
)


class Linker:
    """ """

    @classmethod
    def set_bot(cls, bot):
        """

        Parameters
        ----------
        bot :
            

        Returns
        -------

        
        """
        cls.bot = bot

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.args = dict(
            chat_id=chat_id,
            parse_mode="Markdown",
            reply_markup=EDIT_KEYBOARD,
            disable_web_page_preview=True,
        )

    def get_args(self, override_dict={}):
        """

        Parameters
        ----------
        override_dict :
            (Default value = {})

        Returns
        -------

        
        """
        args = self.args.copy()
        args.update(override_dict)
        return args

    def send_random_post(self, subreddit):
        """

        Parameters
        ----------
        subreddit :
            

        Returns
        -------

        
        """
        for _ in range(MAX_TRIES):
            try:
                return self.send_post(helpers.get_random_post_url(subreddit))
            except TeleredditError as e:
                err = e
                if isinstance(e, SubredditError):
                    break
        return self._send_exception_message(err)

    def send_post_from_url(self, post_url):
        """

        Parameters
        ----------
        post_url :
            

        Returns
        -------

        
        """
        try:
            self.send_post(post_url, from_url=True)
        except TeleredditError as e:
            self._send_exception_message(e, keyboard=False)

    def send_post(self, post_url, from_url=False):
        """

        Parameters
        ----------
        post_url :
            
        from_url :
            (Default value = False)

        Returns
        -------

        
        """
        post = reddit.get_post(post_url)
        if post.media and post.media.size and post.media.size > 20000000:
            raise MediaTooBigError()

        args = self.get_args()
        if from_url:
            # if it is not a random post (e.g. shared via link) don't show the
            # edit custom keyboard
            args["reply_markup"] = NO_EDIT_KEYBOARD

        try:
            if post.get_type() == ContentType.TEXT:
                self.bot.sendMessage(text=post.get_msg(), **args)
            elif post.get_type() == ContentType.YOUTUBE:
                args["disable_web_page_preview"] = False
                self.bot.sendMessage(text=post.get_msg(), **args)
            elif post.get_type() == ContentType.GIF:
                self.bot.sendDocument(
                    document=post.media.url, caption=post.get_msg(), **args
                )
            elif post.get_type() == ContentType.VIDEO:
                self.bot.sendVideo(
                    video=post.media.url, caption=post.get_msg(), **args
                )
            elif post.get_type() == ContentType.PHOTO:
                self.bot.sendPhoto(
                    photo=post.media.url, caption=post.get_msg(), **args
                )

        except Exception:
            raise PostSendError(
                {"post_url": post.permalink, "media_url": post.media.url}
            )

    def edit_result(self, message):
        """Edits the given message with a new post from that subreddit, and edits the
        keyboard markup to give the user the ability to edit or confirm the message.

        Parameters
        ----------
        message :
            

        Returns
        -------

        
        """
        subreddit = helpers.get_subreddit_name(
            (message.caption or message.text) + "\n", True
        )
        if subreddit is None:
            return

        for _ in range(MAX_TRIES):
            try:
                return self.edit_random_post(message, subreddit)
            except TeleredditError:
                pass
        self.bot.editMessageReplyMarkup(
            self.chat_id, message.message_id, reply_markup=EDIT_FAILED_KEYBOARD
        )

    def edit_random_post(self, message, subreddit):
        """

        Parameters
        ----------
        message :
            
        subreddit :
            

        Returns
        -------

        
        """
        msg_is_text = message.caption is None
        post = reddit.get_post(helpers.get_random_post_url(subreddit))

        if (
            (msg_is_text and message.text_markdown == post.get_msg())
            or message.caption_markdown == post.get_msg()
            or (
                not msg_is_text
                and post.get_type() in [ContentType.TEXT, ContentType.YOUTUBE]
            )
        ):
            # if post is the same or message is not text and post is: retry
            raise PostEqualsMessageError()

        args = self.get_args({"message_id": message.message_id})
        try:
            if msg_is_text:
                if post.get_type() == ContentType.YOUTUBE:
                    args["disable_web_page_preview"] = False
                self.bot.editMessageText(post.get_msg(), **args)
            else:
                media_args = dict(
                    media=post.media.url,
                    caption=post.get_msg(),
                    parse_mode="Markdown",
                )
                if post.get_type() == ContentType.GIF:
                    media = InputMediaDocument(**media_args)
                elif post.get_type() == ContentType.VIDEO:
                    media = InputMediaVideo(**media_args)
                elif post.get_type() == ContentType.PHOTO:
                    media = InputMediaPhoto(**media_args)
                self.bot.editMessageMedia(media=media, **args)
            return
        except Exception:
            raise PostSendError(
                {"post_url": post.permalink, "media_url": post.media.url}
            )

    def _send_exception_message(self, e, keyboard=True):
        """Handles the errors created in post retrieval and sending.

        Parameters
        ----------
        e :
            
        keyboard :
            (Default value = True)

        Returns
        -------

        
        """
        args = dict(chat_id=self.chat_id, text=str(e), parse_mode="Markdown")
        if keyboard:
            args["reply_markup"] = DELETE_KEYBOARD
        self.bot.sendMessage(**args)
