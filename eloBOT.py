import discord
from discord.ext import commands
import random
import json
import math
#ELO Algorithm taken from https://blog.mackie.io/the-elo-algorithm

client = commands.Bot(command_prefix = (','))

#Prints when the bot is ready

@client.event
async def on_ready():
    print('Bot is listo wacho')


#gets a discord id and checks if that id is already on the database, if not it will add it
     
def check(playerid):
   
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
    
    feed = open('players.json', "r")        #Opens file, saves the data as a variable and closes it
    players = json.load(feed) 
    feed.close()
    
    for i in players:                       #Checks if the player id is in database, if it is it returns
        if playerid == i['id']:
            return True

    with open('players.json', 'w') as w:    #
        initialstats["id"] = playerid        
        players.append(initialstats)
        json.dump(players,w)
        w.close()

def elo(Ra, Rb, S):
   
    k=100.    
    n=100.
    nR = Ra + k * (S - 1/(1+math.pow(10.0,-(Ra-Rb)/n)))
    return nR

def sendStats(memberID,memberNick):
    with open('players.json') as f:
        players = json.load(f)
    
        for i in players:
            if str(memberID) == i['id']:
            
                r = i['Rank']
                w = i['Wins']
                l = i['Loses']
                t = i['Ties']
                m = i['Total Matches']
                i = i['id']

                #return f'Player: <@{i}>\nRank: {round(float(r),3)}\nWins: {w}\nLoses: {l}\nTies: {t}\nMatches: {m}'
    embed = discord.Embed(
        title = f'{memberNick}\'s Stats:',
        description = f'\nRank: {round(float(r),3)}\nWins: {w}\nLoses: {l}\nTies: {t}\nMatches: {m}',
        colour = discord.Colour.green()
    )
    
    return embed

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency*1000)}ms')

@client.command()
async def stats(ctx, member: discord.Member):
    
    check(member.id)
    await ctx.send(embed = sendStats(member.id,member.display_name))
  
@client.command()
async def win(ctx, loser: discord.Member):
    print(f'{ctx.author} won against {loser}')
    check(ctx.author.id)
    check(loser.id)
    winnerID = str(ctx.author.id)
    loserID = str(loser.id)
    Rw = 0.0
    Rl = 0.0
    feed = open('players.json')
    players = json.load(feed)
    feed.close()

    #get the actual Ranks
    for i in players:
        if winnerID == i['id']:
            Rw = float(i['Rank'])
        if loserID == i['id']:
            Rl = float(i['Rank'])
            
    #new Ranks calculation
    Rwaux = elo(Rw,Rl,1)
    Rlaux = elo(Rl,Rw,0)
    Rw = Rwaux
    Rl = Rlaux
    
    #change Ranks
    for i in players:

        if winnerID == i['id']:
            i['Rank'] = str(Rw)
            aux = int(i['Wins'])
            i['Wins'] = str(aux+1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux+1)           
            
            
        if loserID == i['id']:
            i['Rank'] = str(Rl)
            aux = int(i['Loses'])
            i['Loses'] = str(aux+1)
            aux = int(i['Total Matches'])
            i['Total Matches'] = str(aux+1)
    
    #save new data
    with open('players.json','w') as w:
        json.dump(players,w)
        w.close()
    #send new stats
    await ctx.send(embed = sendStats(ctx.author.id,ctx.author.display_name))
    await ctx.send(embed = sendStats(loser.id,loser.display_name))

client.run('')
