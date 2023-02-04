from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import logging
from chatterbot.trainers import ListTrainer
import re
TWITTER = {
      "CONSUMER_KEY": "my-twitter-consumer-key",
      "CONSUMER_SECRET": "my-twitter-consumer-secret",
      "ACCESS_TOKEN": "my-access-token",
      "ACCESS_TOKEN_SECRET": "my-access-token-secret"
  }
class Chatter():
    def __init__(self):
        self.bot=ChatBot(
            'Default Response Example Bot',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'default_response': 'I am sorry, but I do not understand.',
                    'maximum_similarity_threshold': 0.65
                }
            ]
        )

        trainer = ChatterBotCorpusTrainer(self.bot)
        trainer.train(
            'chatterbot.corpus.english'
        )
        res=[]
        f = open("cor.txt")
        lines = f.readlines()
        for k in lines:
            now=re.split(r"[\n\t]", k)
            for j in now:
                sentences = re.split(r"([.!?])", j)
                sentences.append("")
                sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
                if len(sentences)==1:
                    continue
                res.append(sentences[0])
        trainer=ListTrainer(self.bot)
        trainer.train(res)
        f.close()


    def r(self, s):
        return self.bot.get_response(s).text
