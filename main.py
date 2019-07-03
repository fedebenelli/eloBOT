import discord
from discord.ext import commands
import json
import math
from datetime import datetime
import keep_alive
import json_store_client
#ELO Algorithm taken from https://blog.mackie.io/the-elo-algorithm


#open config file
with open("config.json") as f:
        configFile = json.load(f)

#definitions

jsonToken = configFile['jsonToken']	
botToken = configFile['botToken']
jsonClient = json_store_client.Client(jsonToken)

bot = commands.Bot(command_prefix=(','))
RutherID = 168437285908512768


#Events:

@bot.event
async def on_ready():  # Prints when the bot is ready
	print('Bot is listo wacho')
	game = discord.Game("Use ,h for commands")
	await bot.change_presence(status=discord.Status.idle, activity=game)


#Functions:
"""WIP
@bot.event
async def role(member):
    # Opens file, saves the data as a variable and closes it
    feed = open('players.json', "r")
    players = json.load(feed)
    feed.close()
    for i in players:
        if str(member.id) == i['id']:
            #if float(i['Rank']) < 500:
            role = discord.utils.get(member.guild.roles, name='1')
            print()
            await member.add_roles(role)
            #role1 = discord.utils.get(member.guild.roles, name='1')
            role2 = discord.utils.get(member.guild.roles, name='2')
            role3 = discord.utils.get(member.guild.roles, name='3')
            await member.remove_roles(role2, role3)
            print()"""


def check(member):  # Gets a discord id and checks if that id is already on the database, if not it will add it
    playerid = member.id
    initialstats = json.loads('''{
    "id": "",
    "Rank": "500",
    "Wins": "0",                        
    "Loses": "0",
    "Ties": "0",
    "Total Matches": "0"
    }''')

    playerid = str(playerid)
    print(f'checked id: {playerid}')

    # Opens file, saves the data as a variable and closes it
    players = jsonClient.retrieve('stats')

    for i in players:  # Checks if the player id is in database, if it is it returns
        if playerid == i['id']:
            return True

    #If players is not in the database it adds him
    initialstats["id"] = playerid
    players.append(initialstats)
    jsonClient.store("stats", players)


async def regStats(a, playerA, playerB):

	#Gets actual stats, registry and date, then updates the registry
	players = jsonClient.retrieve('stats')
	registry = jsonClient.retrieve('registry')    
	now = datetime.now()
	date = now.strftime("%d/%m/%Y %H:%M:%S")
	registry.append(date)
	registry.append(f"{playerA.name} {a} against {playerB.name}")
	registry.append(players)
	
	#Sends Ruther the new stats for backup
	msj = f"{playerA.name} {a} against {playerB.name}"+str(players)
	man = bot.get_user(RutherID)
	await man.send(msj)

	#Stores new registry
	jsonClient.store('registry',registry)
	return


def elo(Ra, Rb, S):  # Calculates new ELO rank

    k = 100.
    n = 100.
    nR = Ra + k * (S - 1 / (1 + math.pow(10.0, -(Ra - Rb) / n)))
    return nR


def sendStats(member):

    memberID = member.id
    memberNick = member.display_name
    players = jsonClient.retrieve('stats')
    for i in players:
        if str(memberID) == i['id']:
            r = i['Rank']
            w = i['Wins']
            l = i['Loses']
            t = i['Ties']
            m = i['Total Matches']
            i = i['id']

    name = f'{memberNick}\'s Stats:'
    avatar = str(member.avatar_url)
    data = f'```\nRank:{round(float(r),3):->10}\nWins:{w:->10}\nLoses:{l:->9}\nTies:{t:->10}\nMatches:{m:->7}```'

    embed = discord.Embed(colour=discord.Colour.green())
    embed.set_thumbnail(url=avatar)
    embed.add_field(name=name, value=data, inline=True)

    return embed

#Commands:

@bot.command()
async def h(ctx):
    embed = discord.Embed(colour=discord.Colour.green())

    string = '`,ping`: Returns bot\'s ping.\n`,stats @player`: Gives tagged player elo stats.\n`,win @player`: Assigns new elo ranks based on that message\'s author is the match winner and tagged user the match loser.\n`,tie @player`: Assigns new elo ranks based to both players.\n`,veto`: Sends a veto request to the bot\'s managers.'
    name = 'eloBOT commands\'s:'
    embed.add_field(name=name, value=string, inline=True)

    string = 'In the case the you want to veto a result where you\'ve been tagged use `,veto` and we\'ll contact with you.\nIf an user wants to veto a match, the winner needs to provide a screenshot of the match\'s result. If no proof is given then the match never happened and the ranks will be restored to their last values, so make sure to always screenshot your ranked match results.'
    name = 'Veto rules:'
    embed.add_field(name=name, value=string, inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):  # Sends Current bot's ping
    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')


@bot.command()
async def stats(ctx, member: discord.Member):  # Checks tagged user's stats
    #await role(member)
    check(member)
    await ctx.send(embed=sendStats(member))


@bot.command()
async def win(ctx, loser: discord.Member):  # Takes current message author's and tagged user's stats, checks them and calculates new ones and dumps in file

    if loser == ctx.author:
        await ctx.send('Congratulations, you played yourself')
        return
    print(f'{ctx.author} won against {loser}')
    check(ctx.author)
    check(loser)
    winnerID = str(ctx.author.id)
    loserID = str(loser.id)
    Rw = 0.0
    Rl = 0.0
    
    players = jsonClient.retrieve('stats')

    #get the actual Ranks
    for i in players:
        if winnerID == i['id']:
            Rw = float(i['Rank'])
        if loserID == i['id']:
            Rl = float(i['Rank'])

    #new Ranks calculation
    Rwaux = elo(Rw, Rl, 1)
    Rlaux = elo(Rl, Rw, 0)
    Rw = Rwaux
    Rl = Rlaux

    #change Ranks
    for i in players:

        if winnerID == i['id']:
            i['Rank'] = str(Rw)
            aux = int(i['Wins'])
            i['Wins'] = str(aux + 1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux + 1)

        if loserID == i['id']:
            i['Rank'] = str(Rl)
            aux = int(i['Loses'])
            i['Loses'] = str(aux + 1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux + 1)

    #save new data
    jsonClient.store('stats',players)
    #send new stats
    await ctx.send(embed=sendStats(ctx.author))
    await ctx.send(embed=sendStats(loser))
    await regStats('won', ctx.author, loser)


@bot.command()
async def tie(ctx, playerB: discord.Member):  # Takes current message author's and tagged user's stats,hecks them and calculates new ones and dumps in file
    if playerB == ctx.author:
        await ctx.send('Congratulations, you played yourself')
        return
    print(f'{ctx.author} tied with {playerB}')
    check(ctx.author)
    check(playerB)
    playerAid = str(ctx.author.id)
    playerBid = str(playerB.id)
    Rw = 0.0
    Rl = 0.0
    players = jsonClient.retrieve('stats')

    #get the actual Ranks
    for i in players:
        if playerAid == i['id']:
            Rw = float(i['Rank'])
        if playerBid == i['id']:
            Rl = float(i['Rank'])

    #new Ranks calculation
    Rwaux = elo(Rw, Rl, 0.5)
    Rlaux = elo(Rl, Rw, 0.5)
    Rw = Rwaux
    Rl = Rlaux

    #change Ranks
    for i in players:

        if playerAid == i['id']:
            i['Rank'] = str(Rw)
            aux = int(i['Ties'])
            i['Ties'] = str(aux + 1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux + 1)

        if playerBid == i['id']:
            i['Rank'] = str(Rl)
            aux = int(i['Ties'])
            i['Ties'] = str(aux + 1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux + 1)

    #save new data
    jsonClient.store('stats',players)

    #send new stats
    await ctx.send(embed=sendStats(ctx.author))
    await ctx.send(embed=sendStats(playerB))
    await regStats('tied', ctx.author, playerB)


@bot.command()
async def veto(ctx):

    man = bot.get_user(RutherID)
    name = ctx.author.name
    authorid = ctx.author.id
    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")
    msj = f'Veto from:\n {name}, id:{authorid} at {date}'
    await man.send(msj)
    await ctx.send('Your veto request hast been sent.')



keep_alive.keep_alive()
bot.run(botToken)