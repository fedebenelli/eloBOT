import discord
from discord.ext import commands
import json
import math
from datetime import datetime
import keep_alive
import github
from github import Github
#ELO Algorithm taken from https://blog.mackie.io/the-elo-algorithm


#open config file
with open("config.json") as f:
        configFile = json.load(f)

#definitions
botToken = configFile['botToken']
gistToken = configFile['gistToken']
filesToken = configFile['filesToken']
modID = configFile['modID']

gistClient = Github(gistToken)
gist = gistClient.get_gist(filesToken)

bot = commands.Bot(command_prefix=(','))

#Events:

@bot.event
async def on_ready():  # Prints when the bot is ready
	print('Bot is listo wacho')
	game = discord.Game("Use ,h for commands")
	await bot.change_presence(status=discord.Status.idle, activity=game)


#Functions:

def getFile(filename):
    gist = gistClient.get_gist(statsToken)
    stats = (gist.files[filename].content)
    statsJson = json.loads(stats)
    return statsJson

def updateFile(filename,jsonData):
    gist.edit(description="eloBOT",files={filename: github.InputFileContent(content=json.dumps(jsonData))},) #here "eloBOT" is the gist's name, can be changed for anything 

def check(member):  # Gets a discord id and checks if that id is already on the database, if not it will add it. Gotta fix it to make it add depending on the game acronym 
    playerid = member.id
    initialStats = json.loads('''
    {"id":"",
    "playerName":"",
    "games":[
        {"gameName":"Battlezone 98 Redux","gameAcro":"bzr","rank":"500","W":"0","T":"0","TM":"0"},
        {"gameName":"Battlezone: Combat Commander","gameAcro":"bzcc","rank":"500","W":"0","T":"0","TM":"0"}]}''')

    playerid = str(playerid)
    print(f'checked id: {playerid} from user: {member.name}' )
    
    # Opens file, saves the data as a variable
    statsJson = getFile('stats.json')
    for i in statsJson['stats']['players']:  # Checks if the player id is in database, if it is it returns
        if playerid == i['id']:
            return True

    #If players is not in the database it adds him
    initialStats['id'] = playerid
    initialStats['playerName'] = member.name
    statsJson['stats']['players'].append(initialStats)
    updateFile('stats.json',statsJson)

async def regStats(a, gameAcronym, playerA, playerB):

	#Gets actual stats, registry and date, then updates the registry

    data = getFile('stats.json')
    players = data['stats']
    registry = getFile('registry.json')

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    newInput = json.loads('''
    {"date":"exampleDate",
    "detail":"detailExample",
    "stats":{
        "players":[
            {"id":"exampleID","playerName":"exampleName",
            "games":[
                {"gameName":"Battlezone 98 Redux","gameAcro":"bzr","rank":"500","W":"0","T":"0","TM":"0"},
                {"gameName":"Battlezone: Combat Commander","gameAcro":"bzcc","rank":"500","W":"0","T":"0","TM":"0"}]}]}}''')
	
    newInput['date'] = date
    newInput['detail'] = f"{playerA.name} {a} against {playerB.name} at {gameAcronym}"
    newInput['stats'] = players
	
    registry.append(newInput)
	
	#Sends Ruther the new stats for backup
    msj = f"{playerA.name} {a} against {playerB.name} at {gameAcronym}"+str(players)
    man = bot.get_user(RutherID)
    await man.send(msj)

	#Stores new registry
    updateFile('registry.json', registry)
    return

def elo(Ra, Rb, S):  # Calculates new ELO rank

    k = 100.
    n = 100.
    nR = Ra + k * (S - 1 / (1 + math.pow(10.0, -(Ra - Rb) / n)))
    return nR

def sendStats(member, gameAcronym):
    
    memberID = member.id
    memberNick = member.display_name
    statsJson = getFile('stats.json')

    if gameAcronym != "all":
        for i in statsJson['stats']['players']:
            if str(memberID) == i['id']:
                for game in i['games']:
                    if game['gameAcro'] == gameAcronym:
                        r = game['rank']
                        w = game['W']
                        t = game['T']
                        tm = game['TM']
                        gameName = game['gameName']
                        break
        #Embed design
        name = f'{memberNick}\'s {gameName} Stats:'
        avatar = str(member.avatar_url)
        data = f'```\nRank:{round(float(r),3):->10}\nWins:{w:->10}\nTies:{t:->10}\nMatches:{tm:->7}```'
        
        embed = discord.Embed(colour=discord.Colour.green())
        embed.set_thumbnail(url=avatar)
        embed.add_field(name=name, value=data, inline=True)
    
    else:
        avatar = str(member.avatar_url)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.set_thumbnail(url=avatar)

        for i in statsJson['stats']['players']:
            if str(memberID) == i['id']:
                for game in i['games']:
                        r = game['rank']
                        w = game['W']
                        t = game['T']
                        tm = game['TM']
                        gameName = game['gameName']

                        name = f'{memberNick}\'s {gameName} Stats:'                        
                        data = f'```\nRank:{round(float(r),3):->10}\nWins:{w:->10}\nTies:{t:->10}\nMatches:{tm:->7}```'
                        embed.add_field(name=name, value=data, inline=True)      

    return embed


#Commands:

@bot.command()
async def h(ctx):

    embed = discord.Embed(colour=discord.Colour.green())
    string = '''`,ping`: Returns bot\'s ping.
        `,stats gamename @player`: Gives tagged player elo stats.
        `,win gamename @player`: Assigns new elo ranks based on that message\'s author is the match winner and tagged user the match playerB.
        `,tie gamename @player`: Assigns new elo ranks based to both players.
        `,veto`: Sends a veto request to the bot\'s managers.\n\n'''
    name = 'eloBOT commands\'s:'
    embed.add_field(name=name, value=string, inline=False)    
    string = '''    
    \nIn the case the you want to veto a result where you\'ve been tagged use `,veto` and they\'ll contact with you.
    \nIf an user wants to veto a match, the winner needs to provide a screenshot of the match\'s result. If no proof is given then the match never happened and the ranks will be restored to their last values, so make sure to always screenshot your ranked match results.'''
    name = 'Veto rules:'
    embed.add_field(name=name, value=string, inline=False)
    name = 'Notes:'
    string = '''`gamename` can be: `bzr` or `bzcc`. In the `stats` option you can also use `all` for showing stats in all games.'''
    embed.add_field(name=name, value=string, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):  # Sends Current bot's ping
    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')

@bot.command()
async def stats(ctx, gameAcronym, member: discord.Member):  # Checks tagged user's stats
    #await role(member)
    check(member)
    await ctx.send(embed=sendStats(member,gameAcronym))

@bot.command()
async def win(ctx, gameAcronym, playerB: discord.Member):  # Takes current message author's and tagged user's stats, checks them and calculates new ones and dumps in file

    if playerB == ctx.author:
        await ctx.send('Congratulations, you played yourself')
        return
    print(f'{ctx.author} won against {playerB}')
    check(ctx.author)
    check(playerB)

    playerAid = str(ctx.author.id)
    playerBid = str(playerB.id)
    Rw = 0.0
    Rl = 0.0
    
    stats = getFile('stats.json')
    players = stats['stats']['players']

    #get the actual Ranks
    for i in players:
        if playerAid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    Rw = float(game['rank'])
        if playerBid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    Rl = float(game['rank'])

    #new Ranks calculation
    Rwaux = elo(Rw, Rl, 1)
    Rlaux = elo(Rl, Rw, 0)
    Rw = Rwaux
    Rl = Rlaux

    #change Ranks
    for i in players:
        if playerAid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    game['rank'] = Rw
                    aux = int(game['W'])
                    game['W'] = str(aux + 1)
                    aux = int(game['TM'])
                    game['TM'] = str(aux + 1)

        if playerBid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    game['rank'] = Rl
                    aux = int(game['TM'])
                    game['TM'] = str(aux + 1)

    stats['stats']['players'] = players
    #save new data
    updateFile('stats.json', stats)
    #send new stats
    await ctx.send(embed=sendStats(ctx.author, gameAcronym))
    await ctx.send(embed=sendStats(playerB, gameAcronym))
    await regStats('won', gameAcronym, ctx.author, playerB)

@bot.command()
async def tie(ctx, gameAcronym, playerB: discord.Member):  # Takes current message author's and tagged user's stats,hecks them and calculates new ones and dumps in file

    if playerB == ctx.author:
        await ctx.send('Congratulations, you played yourself')
        return
    print(f'{ctx.author} won against {playerB}')
    check(ctx.author)
    check(playerB)

    playerAid = str(ctx.author.id)
    playerBid = str(playerB.id)
    RA = 0.0
    RB = 0.0
    
    stats = getFile('stats.json')
    players = stats['stats']['players']

    #get the actual Ranks
    for i in players:
        if playerAid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    RA = float(game['rank'])
        if playerBid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    RB = float(game['rank'])

    #new Ranks calculation
    RAaux = elo(RA, RB, 0.5)
    RBaux = elo(RB, RA, 0.5)
    RA = RAaux
    RB = RBaux

    #change Ranks
    for i in players:
        if playerAid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    game['rank'] = RA
                    aux = int(game['T'])
                    game['T'] = str(aux + 1)
                    aux = int(game['TM'])
                    game['TM'] = str(aux + 1)

        if playerBid == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    game['rank'] = RB
                    aux = int(game['T'])
                    game['T'] = str(aux + 1)
                    aux = int(game['TM'])
                    game['TM'] = str(aux + 1)

    stats['stats']['players'] = players
    #save new data
    updateFile('stats.json', stats)
    #send new stats
    await ctx.send(embed=sendStats(ctx.author, gameAcronym))
    await ctx.send(embed=sendStats(playerB, gameAcronym))
    await regStats('tied', gameAcronym, ctx.author, playerB)

@bot.command()
async def veto(ctx):

    man = bot.get_user(modID)
    name = ctx.author.name
    authorid = ctx.author.id
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    msj = f'Veto from:\n {name}, id:{authorid} at {date}'
    await man.send(msj)
    await ctx.send('Your veto request hast been sent.')


#keep_alive.keep_alive()
bot.run(botToken)
