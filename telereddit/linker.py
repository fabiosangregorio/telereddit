"""Linker class which handles all telereddit requests."""

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
from telereddit.exceptions import (
    SubredditError,
    TeleredditError,
    MediaTooBigError,
    PostSendError,
    PostEqualsMessageError,
)


class Linker:
    """
    Handle a single telereddit request.

    Gets instanciated at every telereddit request. (new message, messsage
    callback, etc.)

    Attributes
    ----------
    bot : Bot
        python-telegram-bot's Bot instance: initialized by `set_bot()`.
    chat_id : Int
        Telegram's chat id to which to send the message.
    args : dict
        Args to construct the Telegram message.

    """

    @classmethod
    def set_bot(cls, bot):
        """
        Set the python-telegram-bot's Bot instance for the Linker object.

        This should be set only once, at the package startup.

        .. note:: This needs to be set before starting the bot loop.

        Parameters
        ----------
        bot : Bot
            The bot instance provided by python-telegram-bot

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
        Get the args parameters potentially overriding some of them.

        Parameters
        ----------
        override_dict : dict
            (Default value = {})

            Args to override, with key as argument key and value as override
            value.

        Returns
        -------
        `args`
        
        """
        args = self.args.copy()
        args.update(override_dict)
        return args

    def send_random_post(self, subreddit):
        """
        Send a random post to the chat from the given subreddit.

        Potentially catch Telereddit exceptions.

        Parameters
        ----------
        subreddit : str
            Valid subreddit name.

            .. note:: This should be a r/ prefixed subreddit name.
        
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
        Try to send the reddit post relative to post_url to the chat.

        Potentially catch Telereddit exceptions.

        Parameters
        ----------
        post_url : str
            Reddit share link of the post.

        """
        try:
            self.send_post(post_url, from_url=True)
        except TeleredditError as e:
            self._send_exception_message(e, keyboard=False)

    def send_post(self, post_url, from_url=False):
        """
        Send the reddit post relative to post_url to the chat.

        This is the core functionality of Linker.

        Parameters
        ----------
        post_url : str
            Reddit share link of the post.
            
        from_url : Boolean
            (Default value = False)

            Indicates whether the post url has been received from the chat or
            from the random post.
        
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
        """
        Edit the given message with a new post from that subreddit.
        
        Edit the keyboard markup to give the user the ability to edit or confirm
        the message.

        Parameters
        ----------
        message : Message
            python-telegram-bot's instance of the Telegram message.
        
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
        Edit the current Telegram message with another random Reddit post.

        Parameters
        ----------
        message : Message
            python-telegram-bot's instance of the Telegram message.
            
        subreddit : str
            Subreddit from which to retrieve the random post.

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
        """
        Send the exception text as a Telegram message to notify the user.

        Parameters
        ----------
        e : Exception
            Error to send as a message.
        keyboard : Boolean
            (Default value = True)
            Whether to add the delete button as a keyboard to the message.

        """
        args = dict(chat_id=self.chat_id, text=str(e), parse_mode="Markdown")
        if keyboard:
            args["reply_markup"] = DELETE_KEYBOARD
        self.bot.sendMessage(**args)
