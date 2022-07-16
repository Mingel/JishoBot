import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import urllib.request
import json
import tempfile
import os.path
import shutil


SEARCH_RESULTS_LIMIT_PER_PAGE = 5
JISHO_IN_KANA_ALONE_TEXT = "Usually written using kana alone"
TMP_FOLDER = os.path.join(tempfile.gettempdir(), 'discord_jisho_bot')

SEARCH_API_MAX_RESULTS = 10
TRANSLATE_API_MAX_RESULTS = 20

if not os.path.isdir(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.command(name='translate', description="Translation", brief="Translates a Japanese word to English", help='Translates a Japanese word to English\n[args...]:\t[(-page|-p) page_number]', aliases=['t'])
async def translate(ctx, query: str, *args):
    print(f"{ctx.message.author.name} wrote: {ctx.message.content}")
    if query is None:
        print('No arguments given!')
        return

    options = parse_translate_options(args)
    page = options['page']

    jisho_request_url = f"https://jisho.org/api/v1/search/words?keyword=\"{urllib.parse.quote(query)}\""
    print(f"Request: {jisho_request_url}")
    try:
        tmp_query_filepath = os.path.join(TMP_FOLDER, f"{query}.json")
        if os.path.exists(tmp_query_filepath):
            with open(tmp_query_filepath, "r", encoding='utf-8') as f:
                data = json.loads(f.read())
            print(f"Read from cache: {data}")
        else:
            with urllib.request.urlopen(jisho_request_url) as url:
                msg = url.read().decode()
                data = json.loads(msg)

                # Remove Wikipedia entries
                for datum in data['data']:
                    if isinstance(datum['attribution']['dbpedia'], str):
                        datum['senses'] = [sense for sense in datum['senses'] if "Wikipedia definition" not in sense['parts_of_speech']]

                if any([len(datum['senses']) == 0 for datum in data['data']]):
                    data['data'] = [datum for datum in data['data'] if len(datum['senses']) > 0]

                with open(tmp_query_filepath, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data))

            print(f"Received from jisho.org: {data}")
    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code}')
        return
    except urllib.error.URLError as e:
        print(f'URLError: {e.reason}')
        return

    embed = create_translation_embed(query, data, page_index=page)
    await ctx.channel.send(embed=embed)


@bot.command(name='search', description="Search", brief="Search for a word", help='Search for a word\n[args...]:\t[(-page|-p) page_number]', aliases=['s'])
async def search(ctx, query: str, *args):
    print(f"{ctx.message.author.name} wrote: {ctx.message.content}")
    if query is None:
        print('No arguments given!')
        return

    options = parse_translate_options(args)
    page = options['page']

    jisho_request_url = f"https://jisho.org/api/v1/search/words?keyword={urllib.parse.quote(query)}"
    print(f"Request: {jisho_request_url}")
    try:
        tmp_query_filepath = os.path.join(TMP_FOLDER, f"{query}.json")
        if os.path.exists(tmp_query_filepath):
            with open(tmp_query_filepath, "r", encoding='utf-8') as f:
                data = json.loads(f.read())
            print(f"Read from cache: {data}")
        else:
            with urllib.request.urlopen(jisho_request_url) as url:
                msg = url.read().decode()
                data = json.loads(msg)

                # Remove Wikipedia entries
                for datum in data['data']:
                    if isinstance(datum['attribution']['dbpedia'], str):
                        datum['senses'] = [sense for sense in datum['senses'] if "Wikipedia definition" not in sense['parts_of_speech']]

                if any([len(datum['senses']) == 0 for datum in data['data']]):
                    data['data'] = [datum for datum in data['data'] if len(datum['senses']) > 0]

                with open(tmp_query_filepath, "w", encoding="utf-8") as f:
                    f.write(json.dumps(data))

            print(f"Received from jisho.org: {data}")
    except urllib.error.HTTPError as e:
        print(f'HTTPError: {e.code}')
        return
    except urllib.error.URLError as e:
        print(f'URLError: {e.reason}')
        return

    embed = create_search_embed(query, data, page_index=page)
    await ctx.channel.send(embed=embed)


@bot.command(name='clearcache', help='Clears cache', aliases=['cc'])
async def clear_cache(ctx):
    try:
        shutil.rmtree(TMP_FOLDER)
        os.makedirs(TMP_FOLDER)
        print("Cache cleared!")
        await ctx.channel.send("Cache cleared!")
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        await ctx.channel.send("An error occurred!")


def parse_translate_options(options):
    page = 1 # default value

    option_index = 0
    while option_index < len(options):
        if options[option_index] in ["-p", "-page"]:
            if option_index + 1 < len(options) and options[option_index + 1].isdigit():
                page = int(options[option_index + 1])
            else:
                print("Missing argument!")
                return
            option_index = option_index + 2
    return {'page': page}

def parse_search_options(options):
    page = 1 # default value

    option_index = 0
    while option_index < len(options):
        if options[option_index] in ["-p", "-page"]:
            if option_index + 1 < len(options) and options[option_index + 1].isdigit():
                page = int(options[option_index + 1])
            else:
                print("Missing argument!")
                return
            option_index = option_index + 2
    return {'page': page}


def create_translation_embed(query, data, page_index=1):
    if len(data['data']) == 0:
        return discord.Embed(
            title=f"Translations of {query}",
            url=f"https://jisho.org/search/\"{urllib.parse.quote(query)}\"",
            description="No results found!",
            color=discord.Color.green())

    if page_index is None:
        page_index = 1

    embed = discord.Embed(
        title=f"Translations of {query}",
        url=f"https://jisho.org/search/\"{urllib.parse.quote(query)}\"",
        description=f"{len(data['data'])}{'+' if len(data['data']) >= TRANSLATE_API_MAX_RESULTS else ''} result{'s' if len(data['data']) > 1 else ''} found:",
        color=discord.Color.green())

    max_visible_results_on_page = min(len(data['data']) - ((page_index - 1) * SEARCH_RESULTS_LIMIT_PER_PAGE), SEARCH_RESULTS_LIMIT_PER_PAGE)
    is_only_one_page = (len(data['data']) - 1) // SEARCH_RESULTS_LIMIT_PER_PAGE == 0
    for i in range((page_index - 1) * SEARCH_RESULTS_LIMIT_PER_PAGE, (page_index - 1) * SEARCH_RESULTS_LIMIT_PER_PAGE + max_visible_results_on_page):
        result = data['data'][i]

        if 'word' in result['japanese'][0]:
            japanese_word = result['japanese'][0]['word']
            reading = result['japanese'][0]['reading']
        else:
            japanese_word = result['japanese'][0]['reading']
            reading = None

        english_definitions = [f"{index + 1}.\t{', '.join(sense['english_definitions'])}"
                               if len(result['senses']) > 1
                               else f"  \t{', '.join(sense['english_definitions'])}"
                               for index, sense in
                               enumerate(result['senses'])]
        additional_info = None

        if JISHO_IN_KANA_ALONE_TEXT in result['senses'][0]['tags']:
            additional_info = "*Usually in Kana alone*"

        if len(data['data']) == 1:
            embed_name = f"{japanese_word}"
        else:
            embed_name = f"{i + 1}. {japanese_word}"
        embed_value_intro = '\n'.join(filter(None, [f"{japanese_word} {'[{0}]'.format(reading) if reading is not None else ''}", additional_info]))
        embed_value_results = '\n'.join(english_definitions)
        embed_value = f"```{embed_value_intro}\n{embed_value_results}```"
        if i < max_visible_results_on_page - 1:
            embed_value += '\n\u200B'
        embed.add_field(name=embed_name, value=embed_value,
                        inline=False)

    if is_only_one_page:
        embed.set_footer(text=f"Retrieved from jisho.org")
    else:
        embed.set_footer(text=f"Page {page_index}/{((len(data['data']) - 1) // SEARCH_RESULTS_LIMIT_PER_PAGE) + 1}\nRetrieved from jisho.org")
    return embed

def create_search_embed(query, data, page_index=1):
    if len(data['data']) == 0:
        return discord.Embed(
            title=f"Searching for {query}",
            url=f"https://jisho.org/search/{urllib.parse.quote(query)}",
            description="No results found!",
            color=discord.Color.green())

    if page_index is None:
        page_index = 1

    embed = discord.Embed(
        title=f"Searching for {query}",
        url=f"https://jisho.org/search/{urllib.parse.quote(query)}",
        description=f"{len(data['data'])}{'+' if len(data['data']) >= SEARCH_API_MAX_RESULTS else ''} result{'s' if len(data['data']) > 1 else ''} found:",
        color=discord.Color.green())

    limit_per_page = min(len(data['data']), SEARCH_RESULTS_LIMIT_PER_PAGE)
    is_only_one_page = (len(data['data']) - 1) // SEARCH_RESULTS_LIMIT_PER_PAGE == 0
    for i in range((page_index - 1) * SEARCH_RESULTS_LIMIT_PER_PAGE, (page_index - 1) * SEARCH_RESULTS_LIMIT_PER_PAGE + limit_per_page):
        result = data['data'][i]

        if 'word' in result['japanese'][0]:
            japanese_word = result['japanese'][0]['word']
            reading = result['japanese'][0]['reading']
        else:
            japanese_word = result['japanese'][0]['reading']
            reading = None

        english_definitions = [f"{index + 1}.\t{', '.join(sense['english_definitions'])}"
                               if len(result['senses']) > 1
                               else f"  \t{', '.join(sense['english_definitions'])}"
                               for index, sense in
                               enumerate(result['senses'])]
        additional_info = None

        if JISHO_IN_KANA_ALONE_TEXT in result['senses'][0]['tags']:
            additional_info = "*Usually in Kana alone*"

        if len(data['data']) == 1:
            embed_name = f"{japanese_word}"
        else:
            embed_name = f"{i + 1}. {japanese_word}"
        embed_value_intro = '\n'.join(filter(None, [f"{japanese_word} {'[{0}]'.format(reading) if reading is not None else ''}", additional_info]))
        embed_value_results = '\n'.join(english_definitions)
        embed_value = f"```{embed_value_intro}\n{embed_value_results}```"
        if i < limit_per_page - 1:
            embed_value += '\n\u200B'
        embed.add_field(name=embed_name, value=embed_value,
                        inline=False)

    if is_only_one_page:
        embed.set_footer(text=f"Retrieved from jisho.org")
    else:
        embed.set_footer(text=f"Page {page_index}/{((len(data['data']) - 1) // SEARCH_RESULTS_LIMIT_PER_PAGE) + 1}\nRetrieved from jisho.org")
    return embed

bot.run(TOKEN)