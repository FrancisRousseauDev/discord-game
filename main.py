import os
import asyncio
import discord
from discord.ext import commands
from consumables import consumables
import random

TOKEN = 'OTEzMzU0NTkyNDE3MzcwMTMy.YZ9RwA.PPpxHHTgEDNfmhKNYosqBy2mwrQ'
bot = commands.Bot(command_prefix='!')
client = discord.Client()
isGameStarted = False
isGameCreated = False
gameIsFinished = False
joinedUsers = []

currentUser = ''
index = 0

weapons = ['Banana', 'Apple', 'Frozen burrito']


def getAllChannels(Client):
    text_channel_list = []
    for guild in client.guilds:
        text_channel_list = guild.text_channels
    return text_channel_list


@client.event
async def on_ready():

    print(consumables)
    print(f'{client.user} has connected to Discord!')
    await help()


async def help():
    welcomeMessage = f"Welcome to the Colosseum bot!\n" \
                     "**Commands**\n" \
                     "```>>start : will start the game\n" \
                     ">>new : will create a new game\n" \
                     ">>end : will stop the game\n" \
                     ">>users : will show all joined users\n" \
                     ">>join : will add a user to the game (min 2)\n" \
                     ">>clear : will clear the whole channel\n```"
    await getAllChannels(client)[0].send(welcomeMessage)

def getCurrentUser():
    for user in joinedUsers:
        if user['author'] == currentUser:
            return user

def getAllUsersExceptCurrent():
    list = []
    for user in joinedUsers:
        #if user['authors'] != currentUser:
        list.append(user)

    parsedList = []
    for user in list:
        parsedList.append(user['author'])

    return parsedList

def getItemsOfUser(parsed):
    global currentUser

    if parsed:
        for user in joinedUsers:
            print(user['author'])
            print(currentUser)
            if user['author'] == currentUser:
                allItems = []
                for item in user['items']:
                    allItems.append(item['name'])
                return allItems
    else:
        for user in joinedUsers:
            print(user['author'])
            print(currentUser)
            if user['author'] == currentUser:
                return user['items']


def addItemOfUser(weapon):
    print(weapon)
    global currentUser
    for user in joinedUsers:
        if user['author'] == currentUser:
            user['items'].append(weapon)

def getMessage(type):
    if type == 1:
        return f"<@{currentUser.id}> it is your turn\n" + \
               f"**Items**\n" + \
               str(getItemsOfUser(True)) + \
               f"\n**Options**\n"\
               + "```1) will search for new items \n"\
               + "2) will fight someone \n```"

    if type == 2:
        consumable = random.choice(consumables)
        addItemOfUser(consumable)
        return str(currentUser) + " you have found " + consumable['name']

    if type == 3:
        return f"<@{currentUser.id}> timed out\n"


    if type == 4:
        return f"You have chosen to attack someone: \n" \
               f"**Items**\n" + \
               str(getItemsOfUser(True))

    if type == 5:
        return f"<@{currentUser.id}> is dead."

    if type == 6:
        print(getAllUsersExceptCurrent())
        return f"Choose the person to attack: \n" \
               f"**Persons**\n" + \
               str(getAllUsersExceptCurrent())




async def clear(ctx):
    await ctx.channel.purge(limit=None)


@client.event
async def on_message(message):
    global client
    print(message)
    global isGameStarted
    global isGameCreated
    global joinedUsers
    if message.content == '>>clear':
        await clear(message)
        await help()

    if message.content == '>>new':
        suggestEmbed = discord.Embed(colour=0xFF0000)
        suggestEmbed.set_author(name=f'Suggested by ', icon_url=f'{message.author.avatar_url}')
        suggestEmbed.add_field(name='New suggestion!', value=f'cool')
        await message.channel.send(embed=suggestEmbed)
        if isGameCreated:
            await message.channel.send(f"<@{message.author.id}>, there is a game created already.")
        else:
            isGameCreated = True
            await message.channel.send('Game created!')

    if message.content == '>>users':
        parsedUsers = []
        for user in joinedUsers:
            parsedUsers.append(f"<@{user['author'].id}>")
        await message.channel.send(f"List of all joined users: \n{', '.join(parsedUsers)}")

    if message.content == '>>help':
        await help()

    if message.content == '>>start':
        if isGameStarted:
            await message.channel.send(f"<@{message.author.id}>, there is a game busy already.")
        elif not isGameCreated:
            await message.channel.send(f"<@{message.author.id}>, there is no game created yet")
        elif len(joinedUsers) == 0:
            await message.channel.send(f"<@{message.author.id}>, there are no people joined yet")
        elif isGameCreated and not isGameStarted:
            isGameStarted = True
            await startGame(message)

    if message.content == '>>join':
        if not isGameCreated:
            await message.channel.send(f"<@{message.author.id}>, game is not joinable. There is no game created yet!")
        else:
            print(message.author)
            if any(d['author'] == message.author for d in joinedUsers):
                await message.channel.send(f"Sorry, you joined the game already...")
            else:
                joinedUsers.append({
                    "author": message.author,
                    "health": 100,
                    "items": []
                })
                print(joinedUsers)
                parsedUsers = []
                await message.channel.send(f"Game is joined by: <@{message.author.id}>")
                for user in joinedUsers:
                    print(user)
                    parsedUsers.append(f"<@{user['author'].id}>")
                await message.channel.send(f"List of all joined users: \n{', '.join(parsedUsers)}")

    if message.content == '>>end':
        isGameStarted = False
        isGameCreated = False
        joinedUsers = []
        await message.channel.send('Game ended!')

    print('message', message)
    if message.author == client.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    if message.content == '99!':
        response = brooklyn_99_quotes[0]
        await message.channel.send(response)


async def startGame(message):
    global index
    while not gameIsFinished:
        for play in joinedUsers:
            reaction = await askQuestion(message.channel)
            if reaction:
                if str(reaction) == '⬅️':
                    await message.channel.send(getMessage(2))
                    await asyncio.sleep(2)
                elif str(reaction) == '➡️':
                    await useItem(message.channel)


            else:
                print('OTHERR')
def check(reaction, user):
    return user == currentUser

async def useItem(channel):
    message = await channel.send(getMessage(4))
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
        items = getItemsOfUser(False)
        print(items)
        if str(reaction) == '⬅️':
            item = items[0]
            await choosePersonToAttack(channel, item)
        elif str(reaction) == '➡️':
            item = items[1]
            await choosePersonToAttack(channel, item)
    except asyncio.TimeoutError:
        if isGameStarted:
            await channel.send(getMessage(3))

async def choosePersonToAttack(channel, item):
    message = await channel.send(getMessage(6))
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
        user = getCurrentUser()
        if str(reaction) == '⬅️':
            await addDamageOrHealth(channel, item)
        elif str(reaction) == '➡️':
            await addDamageOrHealth(channel, item)
    except asyncio.TimeoutError:
        if isGameStarted:
            await channel.send(getMessage(3))

def getUserByID(id):
    for user in joinedUsers:
        if user.id == id:
            return user


async def addDamageOrHealth(channel, item):
    global currentUser
    user = getCurrentUser()
    itemHealth = random.randint(int(item['max']), int(item['min']))
    userHealth = int(user['health'])
    user['health'] = itemHealth + userHealth
    if user['health'] < 0:
        print('user dead')
        joinedUsers.remove(user)
        await channel.send(getMessage(5))
    else:
        print('user dead')
        await channel.send(f"Users health dropped from {userHealth} to: {user['health']}")



async def askQuestion(channel):
    global currentUser
    global index

    try:
        print(index, len(joinedUsers))
        if len(joinedUsers) + 100 > index and len(joinedUsers) != index:
            currentUser = joinedUsers[index]['author']
            message = await channel.send(getMessage(1))
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            index += 1
            reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
            return reaction
        elif len(joinedUsers) == index:
            index = 0
            return None
        else:
            index += 1
            await channel.send("everyone played")
            return None

    except asyncio.TimeoutError:
        if isGameStarted:
            await channel.send(getMessage(3))



@bot.command(name='list')
async def paginate(ctx, arg):
    await ctx.send(arg)


client.run(TOKEN)
