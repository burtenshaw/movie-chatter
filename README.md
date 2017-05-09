# Dependencies 

* [Chatterbot](https://github.com/gunthercox/ChatterBot)
* [Chatterbot Corpus](https://github.com/gunthercox/chatterbot-corpus)
* [IMDBpy](http://imdbpy.sourceforge.net/)

# Installation

* Install dependencies
* Clone this directory

# Usage

```bash
python chatter.py
```

So far the bot has two scripted roles:

```
User: I want to watch something
Bot: What's your favorite film? Maybe we can find something similar.
User: the godfather         
Bot: Do you mean The Godfather directed by Francis Ford Coppola?
User: yes
Bot: How about Scarface?
---
User: what's it about
Bot: Do you know Scarface?
User: yes
Bot: Something you might not know is ...
When Scarface (1983) was re-released in theaters in 2003, the studio wanted Brian De Palma to change the soundtrack so that rap songs inspired by the movie could be used. De Palma refused.
---

```

# Training

Using [Chatterbot Corpus](https://github.com/gunthercox/chatterbot-corpus) the bot can be trained on conversation scripts.

``` python
from chatterbot.trainers import ChatterBotCorpusTrainer

chatterbot = ChatBot("Training Example")
chatterbot.set_trainer(ChatterBotCorpusTrainer)

chatterbot.train(
    "chatterbot.corpus.english"
)
```
