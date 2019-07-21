import discord
from discord.ext import commands
import json
import math
from datetime import datetime
import github
from github import Github
import logging
#ELO Algorithm taken from https://blog.mackie.io/the-elo-algorithm

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Open config file
with open("config.json") as f:
        configFile = json.load(f)

# Definitions
botToken = configFile['botToken']
filesToken = configFile['filesToken']
modID = int(configFile['modID'])

#In the case the bot files are hosted in a gist, functions getFile() and updateFile() also have the equivalent code for gists
"gistToken = configFile['gistToken']"
"gistClient = Github(gistToken)"
"gist = gistClient.get_gist(filesToken)"

bot = commands.Bot(command_prefix=(','), case_insensitive=True)

#Events:

@bot.event
async def on_ready():  # Prints when the bot is ready
	print('Bot is listo wacho')
	game = discord.Game("Use ,h for commands")
	await bot.change_presence(status=discord.Status.idle, activity=game)


#Functions:

def getFile(filename):    

    #Just a simpler way to open the files
    """gist = gistClient.get_gist(filesToken)
    f = (gist.files[filename].content)
    fJson = json.loads(f)"""
    
    filetype = ''
    boolean = False
    for i in filename:
        if i == '.':
            boolean = True
        if boolean:
            filetype += i

    with open(filename, 'r') as feed:
        f = feed
        if filetype == '.json':
            f = json.load(feed)
    return f

def updateFile(filename, data):
    #Just a simpler way to write on the files
    """gist.edit(description=gist.description,files={filename: github.InputFileContent(content=json.dumps(jsonData))},) #here "eloBOT" is the gist's name, can be changed for anything"""
    filetype = ''
    boolean = False
    for i in filename:
        if i == '.':
            boolean = True
        if boolean:
            filetype += i

    with open(filename, "w") as w:
        if filetype == '.json':
            json.dump(data,w)
        if filetype == '.txt':
            w.write(data)

def getAvgRank(members, gameAcronym, players):  # Gets the members of a team, the game acronym and the stats data, then it calculates the average rank of that team
    
    gameAcronym = gameAcronym.lower()
    rankList = []

    #Make the list of ranks
    for member in members:
        for i in players:
            if i['id'] == str(member.id):
                for game in i['games']:
                    if game['gameAcro'] == gameAcronym:
                        rankList.append(game['rank'])
    
    mean = 0
    count = 0
    
    #Calculates the average/mean rank
    for i in rankList:
        mean+=float(i)
        count+=1
    mean = mean/count
    return mean

def getMembers(str): # Makes a list of discord.Member's that are tagged in a message, message it's stored as string and tagged members are received as <@id>
    
    boolean = False
    members = []
    aux = ""
    for i in str:
        if i == ">":
            boolean = False
            members.append(int(aux))
            aux = ""
        if boolean:
            aux += i    
        if i == "@":
            boolean = True
    i = 0
    for member in members:
        members[i] = bot.get_user(member)
        i+=1
    return members

def check(member):  # Gets a discord id and checks if that id is already on the database, if not it will add it. Gotta add to make it add depending on the game acronym 
    playerid = member.id

    #Creates a string with the json format used, with default stats and blank id and playerName
    initialStats = json.loads('''
    {
        "id":"",
        "playerName":"",
        "games":
        [
            {"gameName":"Battlezone 98 Redux","gameAcro":"bzr","rank":"500","W":"0","T":"0","L":"0","TM":"0"},
            {"gameName":"Battlezone: Combat Commander","gameAcro":"bzcc","rank":"500","W":"0","T":"0","L":"0","TM":"0"}
        ]
    }''')

    playerid = str(playerid)
    print(f'checked id: {playerid} from user: {member.name}' )
    
    # Opens stats file, saves the data as a variable
    statsJson = getFile('stats.json')
    for i in statsJson['stats']['players']:  # Checks if the player id is in database, if it is then it returns
        if playerid == i['id']:
            return True

    #If players is not in the database it adds him
    initialStats['id'] = playerid
    initialStats['playerName'] = member.name
    statsJson['stats']['players'].append(initialStats)
    updateFile('stats.json',statsJson)

async def regStats(a, gameAcronym, membersA, membersB): # Gets the match result (win/tie), and appends the new stats file with the date and detail to the registry.json file

    gameAcronym = gameAcronym.lower()
    data = getFile('stats.json')
    players = data['stats']
    registry = getFile('registry.json')
    log = str(getFile('log.txt'))

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    newInput = json.loads('''
    {
        "date":"exampleDate",
        "detail":"detailExample",
        "stats":
        {
            "players":
            [
                {
                    "id":"exampleID",
                    "playerName":"exampleName",
                    "games":
                    [
                        {"gameName":"Battlezone 98 Redux","gameAcro":"bzr","rank":"500","W":"0","T":"0","L":"0","TM":"0"},
                        {"gameName":"Battlezone: Combat Commander","gameAcro":"bzcc","rank":"500","W":"0","T":"0","L":"0","TM":"0"}
                    ]
                }
            ]
        }
    }''')

    playerAAux = '''{"id":"","name":""}'''
    playerAAux = json.loads(playerAAux)
	
    playersA = '''[]'''
    playersA = json.loads(playersA)
    for playerA in membersA:
        playerAAux['id'] = playerA.id
        playerAAux['name'] = playerA.name
        playersA.append(playerAAux)
    
    playerBAux = '''{"id":"","name":""}'''
    playerBAux = json.loads(playerBAux)

    playersB = '''[]'''
    playersB = json.loads(playersB)
    for playerB in membersB:
        playerBAux['id'] = playerB.id
        playerBAux['name'] = playerB.name
        playersB.append(playerBAux)
    
    
    newInput['date'] = date
    newInput['detail'] = f"{playersA} {a} against {playersB} at {gameAcronym}"
    newInput['stats'] = players

    registry.append(newInput)
	
	#Sends the mod the new stats for backup
    msj = "\nNew Reg!:" + "\n\n" + f"{json.dumps(playersA)} {a} against {json.dumps(playersB)} at {gameAcronym}" + "\n\nStats:\n" + json.dumps(players)
    man = bot.get_user(modID)
    await man.send(msj)
    print(log)
    log += f"\n{playersA} {a} against {playersB} at {gameAcronym}"
    print(log)
	#Stores new registry
    updateFile('registry.json', registry)
    updateFile('log.txt',log)

    return

def deltaelo(memberA, teamBrank, gameAcronym,S, players):  # Calculates delta on ELO rank
    gameAcronym = gameAcronym.lower()
    RA = 0.

    # Get the actual rank of memberA
    for i in players:   
        if str(memberA.id) == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    RA = float(game['rank'])

    #Calculation of delta elo
    k = 100.
    n = 100.
    deltaRank = k * (S - 1 / (1 + math.pow(10.0, -(RA - teamBrank) / n)))
    return deltaRank

def changeelo(memberA, deltaRank, gameAcronym, cond, players):
    
    gameAcronym = gameAcronym.lower()
    #change Ranks    
    for i in players:
        if str(memberA.id) == i['id']:
            for game in i['games']:
                if game['gameAcro'] == gameAcronym:
                    newRank = float(game['rank']) + deltaRank
                    game['rank'] = newRank
                    aux = int(game[cond])
                    game[cond] = str(aux + 1)
                    aux = int(game['TM'])
                    game['TM'] = str(aux + 1)

    stats = getFile('stats.json')
    stats['stats']['players'] = players
    
    #save new data    
    updateFile('stats.json', stats)
    
def sendStats(member, gameAcronym):

    gameAcronym = gameAcronym.lower()
    memberID = member.id
    memberNick = member.display_name
    statsJson = getFile('stats.json')
    gameName = ''
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
    string = '''

        `,ping`: Returns bot\'s ping.
        `,stats <gamename> @player`: Gives tagged player elo stats.
        `,ranked <gamecondition> <gamename>`: Will ask for another message, where the user tags all the players of team 1 and then all the players of team 2.
        gamecondition can be "win" or "tie".
        `,veto`: Sends a veto request to the bot\'s managers.
        
        \n\n'''
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
    gameAcronym = gameAcronym.lower()
    check(member)
    await ctx.send(embed=sendStats(member,gameAcronym))

@bot.command()
async def ranked(ctx, cond, gameAcronym):  # Takes current message author's and tagged user's stats, checks them and calculates new ones and dumps in file
    
    #  Defines variables for later
    gameAcronym = gameAcronym.lower()
    SA = 0.5
    SB = 0.5
    strA = ""
    strB = ""
    deltaA = 0
    deltaB = 0
    teamA = ""
    teamB = ""

    # Gets the actual stats from the file
    stats = getFile('stats.json')
    players = stats['stats']['players']

    if cond == "win":
        SA = 1
        SB = 0
        strA = "W"
        strB = "L"
        teamA = "Winners"
        teamB = "Losers"
    if cond == "tie":
        SA = 0.5
        SB = 0.5
        strA = "T"
        strB = "T"
        teamA = "Team 1"
        teamB = "Team 2"

    # Gets the member's input of players and saves them as a variable (list)
    await ctx.send(f"Input the {teamA}:")
    msj = await bot.wait_for('message')
    membersA = getMembers(msj.content)

    await ctx.send(f"Input the {teamB}:")
    msj = await bot.wait_for('message')
    membersB = getMembers(msj.content)

    # Checks if there ain't any repeated players on both teams
    """
    if ctx.author in membersB:

    for member in membersA:
        if member in membersB:
            await ctx.send('One player can\'t be on both teams, try again >:(')
            return"""

    async with ctx.typing():
        for member in membersA:
            check(member)
        for member in membersB:
            check(member)
        print(len(membersA))
        print(len(membersB))
        # Calculates Avg Rank of each team
        teamArank = getAvgRank(membersA,gameAcronym,players) * len(membersA)/len(membersB)
        teamBrank = getAvgRank(membersB,gameAcronym,players) * len(membersB)/len(membersA)

        # Calculates the new variation of rank (delta) based on actual stats and updates
        for memberA in membersA:
            for memberB in membersB:
                deltaA = deltaelo(memberA, teamBrank, gameAcronym, SA, players)
                changeelo(memberA, deltaA, gameAcronym, strA, players)

        for memberB in membersB:
            for memberA in membersA:
                deltaB = deltaelo(memberB, teamArank, gameAcronym, SB, players)
                changeelo(memberB, deltaB, gameAcronym, strB, players)
        await regStats(cond, gameAcronym, membersA, membersB)

        # Send new stats        
        await ctx.send(f"{teamA}:")
        for memberA in membersA:
            await ctx.send(embed=sendStats(memberA, gameAcronym))
        await ctx.send(f"{teamB}:")
        for memberB in membersB:
            await ctx.send(embed=sendStats(memberB, gameAcronym))
    print('Ranked!')

    

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

""" WIP
@bot.command()
@commands.has_permissions(administrator=True) 
async def mod(ctx, member: discord.Member):
    """
    
bot.run(botToken)
