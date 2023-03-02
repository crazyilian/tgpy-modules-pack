"""
    name: yes_no_answers
    needs:
      config_loader: 0.0.0
      tg_name: 0.0.0
    once: false
    origin: tgpy://module/yes_no_answers
    priority: 29
    save_locals: true
    description: react when someone answers to "yes", "no", etc. with rhyme in target chats
"""
import telethon

handle_yes_no_chats = set()
really_handling_yes_no_chats = set()


class YesNoAnswers:
    def __init__(self):
        self.config = ModuleConfig('yes_no_answers', default_dict={'chats': []})
        self.telethon_handlers = set()
        self.chats = set()
        self.add(*self.config.chats)

    def __save_chats(self):
        self.config.chats = list(self.chats)

    def add(self, *chats):
        """add new chats to handle yes no answers"""
        self.chats.update(chats)
        self.__save_chats()
        new_chats = [chat for chat in chats if chat not in self.telethon_handlers]
        if not new_chats:
            return
        self.telethon_handlers.update(new_chats)

        @client.on(telethon.events.NewMessage(chats=new_chats))
        async def handle_yes_no_answer(event):
            if event.chat_id not in self.chats:
                return
            SUFFIXES = {
                "да": "да",
                "нет": "ет",
                "ладно": "дно"
            }
            for word, suffix in SUFFIXES.items():
                if not event.text.lower().endswith(suffix):
                    continue
                orig = await event.get_reply_message()
                if orig and orig.text.lower().split()[-1:] == [word]:
                    await event.reply("Ловко парировал(а) " + get_name(event.sender))
                    break

    def remove(self, *chats):
        """remove chat handlers"""
        self.chats.difference_update(chats)
        self.__save_chats()

    async def get(self):
        """get current handling chats"""
        for chat in self.chats:
            print(chat, ':', get_name(await client.get_entity(chat)))


yes_no_answers = YesNoAnswers()

__all__ = ['yes_no_answers']
