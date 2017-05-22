# Dependencies

* [Chatterbot](https://github.com/gunthercox/ChatterBot)
* [Chatterbot Corpus](https://github.com/gunthercox/chatterbot-corpus)
* [IMDBpy](http://imdbpy.sourceforge.net/)

# Installation

* Install dependencies
* Clone this directory

# Usage

```bash
python chatter.py --mongodb <address>:<port>
```

Some example conversations:

```
---
Hi
Hello
---
How are you?
I am doing well.
---
I want to watch a comedy tonight
Okay, let me think.
Some movies in this genre are:
Forrest Gump , directed by Robert Zemeckis
La vita è bella , directed by Roberto Benigni
City Lights , directed by Charles Chaplin
Intouchables , directed by Olivier Nakache
Modern Times , directed by Charles Chaplin
Back to the Future , directed by Robert Zemeck
---
Can you explain what intouchables is about?
Do you know Intouchables?
---
no
In Paris, the aristocratic and intellectual Philippe is a quadriplegic millionaire who is interviewing candidates for the position of his carer, with his red-haired secretary Magalie. Out of the blue, the rude African Driss cuts the line of candidates and brings a document from the Social Security and asks Phillipe to sign it to prove that he is seeking a job position so he can receive his unemployment benefit. Philippe challenges Driss, offering him a trial period of one month to gain experience helping him. Then Driss can decide whether he would like to stay with him or not. Driss accepts the challenge and moves to the mansion, changing the boring life of Phillipe and his employees.
---
Is it any good?
The movie is rated 8.6/10.
So it should be really good!
---
Which actors play in it?
The most important actors are François Cluzet, Omar Sy, Anne Le Ny, Audrey Fleurot and Joséphine de Meaux
---
And what about city lights?
Do you know City Lights?
---
no, i don't
A tramp falls in love with a beautiful blind girl. Her family is in financial trouble. The tramp's on-and-off friendship with a wealthy man allows him to be the girl's benefactor and suitor.
---
is it based on a book?
City Lights was written, directed, produced, and starred in by the silent film-maker Charles Chaplin.
---
Do you have more information?    
Do you know City Lights?
---
Yes, now I do.
Something you might not know is ...
In 2008, this film was voted #1 on AFI's list over the ten best romantic comedies of all time.
---

```

```
---
Lets talk about movies
What's your favorite film? Maybe we can find something similar.
The godfather
Do you mean The Godfather directed by Francis Ford Coppola?
no
I'm sorry, please be more specific.
The godfather part 2
Do you mean The Godfather: Part II directed by Francis Ford Coppola?
yes
How about The Departed?
---
What is it about?
Do you know The Departed?
---
no
In South Boston, the state police force is waging war on Irish-American organized crime. Young undercover cop Billy Costigan is assigned to infiltrate the mob syndicate run by gangland chief Frank Costello. While Billy quickly gains Costello's confidence, Colin Sullivan, a hardened young criminal who has infiltrated the state police as an informer for the syndicate is rising to a position of power in the Special Investigation Unit. Each man becomes deeply consumed by their double lives, gathering information about the plans and counter-plans of the operations they have penetrated. But when it becomes clear to both the mob and the police that there is a mole in their midst, Billy and Colin are suddenly in danger of being caught and exposed to the enemy - and each must race to uncover the identity of the other man in time to save themselves. But is either willing to turn on their friends and comrades they've made during their long stints undercover?
---
And what about the godfather?
Do you know The Godfather?
---
yes
Something you might not know is ...
According to Alex Rocco, he originally auditioned for the role of Al Neri but Francis Ford Coppola insisted that he play Moe Greene instead. Rocco, an Italian-American, felt that he would not be able to play a person of Jewish descent. According to Rocco, Coppola told him "'The Italians do this,' and he punches his fingers up. 'And the Jews do this,' and his hand's extended, the palm flat. Greatest piece of direction I ever got. I've been playing Jews ever since."
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
