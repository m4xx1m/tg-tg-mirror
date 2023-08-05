import contextlib
import os
import asyncio
import logging
import telethon
from telethon.tl.types import MessageMediaGeoLive, MessageMediaWebPage

DISALLOWED_FILE_TYPES = (MessageMediaGeoLive, MessageMediaWebPage)


logger = logging.getLogger("app")
logger.setLevel("INFO")
logging.basicConfig(format="%(asctime)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d - %(message)s")


class Handlers:
    def __init__(self, client: telethon.TelegramClient, to_chat: int):
        self.client = client
        self.to_chat = to_chat

    async def album_handler(self, event: telethon.events.album.Album.Event):
        await self._process(event.messages)

    async def single_handler(self, event: telethon.events.NewMessage.Event):
        if event.message.grouped_id:
            return
        await self._process([event.message])

    async def _process(self, messages: list[telethon.types.Message]):
        logger.info(f"processing message {messages[0].id}")
        text = ""
        entities = None
        link_preview = False

        for message in messages:
            if message.message:
                text = message.message
                entities = message.entities
                if message.media and isinstance(message.media, MessageMediaWebPage):
                    link_preview = True
                break

        files = []
        for message in messages:
            if isinstance(message.media, DISALLOWED_FILE_TYPES):
                continue
            files.append(message.media)

        match len(files):
            case 1:
                files = files[0]
            case 0:
                files = None

        if not text and not files:
            return

        await self.client.send_message(
            entity=self.to_chat,
            message=text,
            file=files,
            formatting_entities=entities,
            link_preview=link_preview
        )


async def main():
    if not (bot_token := os.getenv("BOT_TOKEN", None)):
        raise ValueError("BOT_TOKEN is not set")

    if not (from_chat := os.getenv("FROM", None)):
        raise ValueError("FROM is not set")

    if not (to_chat := os.getenv("TO", None)):
        raise ValueError("TO is not set")

    from_chat, to_chat = int(from_chat), int(to_chat)

    client = telethon.TelegramClient("bot", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e")
    await client.start(bot_token=bot_token)
    me = await client.get_me()
    logger.info(f"signed in as @{me.username} (id {me.id})")

    handlers = Handlers(client=client, to_chat=to_chat)
    client.add_event_handler(handlers.album_handler, telethon.events.Album(chats=[from_chat]))
    client.add_event_handler(handlers.single_handler, telethon.events.NewMessage(chats=[from_chat]))

    logger.info("starting polling")
    await client.disconnected

if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
