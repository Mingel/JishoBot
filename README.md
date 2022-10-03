# JishoBot

JishoBot is a basic Discord bot made in Python, which uses the [jisho.org API](https://jisho.org/forum/54fefc1f6e73340b1f160000-is-there-any-kind-of-search-api) and allows you to look up English/Japanese translations.

![image](https://user-images.githubusercontent.com/46728839/193692829-1e5c5b7b-c67f-4f89-83f8-8d30d9203f17.png)

## Build
The bot is built with [Python](https://www.python.org/). It has been tested with Python 3.7+.

To run the bot, it is required to use a Discord bot token to set up the bot. To receive a token, do the following:
1. Go to the Applications tab in the Discord Developer portal (click [here](https://discord.com/developers/applications)). You are required to login to your Discord account.
2. Click **New Application**, insert a name for the bot, then click **Create**.
3. On the left, click **Bot** and in the Build-A-Bot section on the right, click **Add Bot** and after that, **Yes, do it!**.
4. Press **Click to Reveal Token**. Now the token is visible and can be copied.

**DO NOT SHARE THE TOKEN.**

Inside the root folder, a file named `.env` must be created. You can use the given `.env.template` file. Insert the discord token inside the `.env` file: `DISCORD_TOKEN=<your token>`.

Make sure that the required packages are installed: 
```
pip install -r requirements.txt
```

To run the bot: 
```
python bot.py
```
Or if you have Python 2 and 3 installed:
```
python3 bot.py
```

## Commands

Basic:

1.
```
-s <query> [-p <page>] [-d]
```
Search for results with the given query. Note that jisho.org will also look for results where the latin letters are converted to kana.
If your query is longer than one word, you can wrap the query with quotation marks (e.g. `"to eat"`).

2.
```
-t <query> [-p <page>] [-d]
```
Search for results with the given query. The query will not be converted to kana if it only contains latin letters.
If your query is longer than one word, you can wrap the query with quotation marks.

Extra parameters:
```
[-d]: Show more information about results, e.g. frequency, JLPT level and many more.

[-p <page>]: Go to a specified page.
```

## Credits
Thanks to the team from [jisho.org](https://jisho.org/) for making this possible!

Jisho.org uses several data sources, which can be found at jisho.org's [About Page](https://jisho.org/about).
