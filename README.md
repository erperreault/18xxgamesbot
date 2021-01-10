18xx.games Bot - A friendly Discord chatbot
======================================================

On the back-end,
- this app starts at `server.py`
- add frameworks and packages in `requirements.txt`
- safely store app secrets in `.env`
- `start.sh` is required for Python 3

Currently, this bot only runs while the glitch is running.

Currently, this bot only responds to "hello". 

It thinks its name is hello!

[Discord features]
In the future this bot wants to learn how to: send reminders, 
clean up channels, automatically convert time
zones, and log finished game stats. 

An idea for the order we could deliver these features in is:
1. schedule games via chatbot command that takes game arguments
2. add time zones to game creation message
3. store games and attributes in data storage of some kind
4. schedule reminders and delete post after allotted time
:( run bot on server... actually glitch is fine nvm

Bonus:
* Users can add or remove(?) timezones
* Sweep confused user posts in game channels
* ping someone in discord if it's your turn

[Other features]
In the future this bot also wants to learn how to: scrape the
18xx.games website to see whose turn it is, collect play data 
across all other public games for company winrates, performance 
per OR, etc. Making a webpage to display the bot's log might be
helpful. Also host privately on old PC.

Remixed from 'flask-hello-world' by Kenneth Reitz