import discord, ast, time
from itertools import chain

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
userdefault = {
    'tickets': 0,
    'lastTeam': None,
    'immune': False,
    'escaped': False
    }

team_ids = [
    959682463175696414, # Paypal Mafia
    960150245226995772, # Outcasts
    960177784641191987, # Starving Artists
    960260637106257920, # Raging Crack Addicts
    960996087244668948, # Femboy Association
    960381460240547860,# Sceptile Fans :D
    381951357470375936, # test role from testing server
    967604532148305970
    ]
team_chan_ids = {
    team_ids[0]: 959682914944188467, # Paypal Mafia
    team_ids[1]: 960150552275197992, # Outcasts
    team_ids[2]: 960178086131949592, # Starving Artists
    team_ids[3]: 960265304443863120, # Raging Crack Addicts
    team_ids[4]: 960996278572040212, # Femboy Association
    team_ids[5]: 961005507408171019,  # Sceptile Fans :D
    team_ids[7]: 967586316579667988
    }
role_elim_id = 967593430916153344#961755681432666202
chan_prizes_id = 953328018506534965
chan_bots_id = 953163427101167647
op_ids = [266389941423046657, 221992874886037504]
tribulations_id = 373237751039918098#951647646102200320
host_id = 266389941423046657#221992874886037504

helptext = """Use "exe (keyword)" to use a command.

help/commands/? - Show this dialog.
balance/bal - Check the number of tickets you have.
shop/prizes - Check the Prize Booth.

== Prize Booth commands ==
nuke/bomb <team name> - Eliminate an entire team.
eliminate <user> - Eliminate another player.
revive <user> - Revive a teammate.
immunity - Give yourself voting immunity.
sabotage <team name> - Sabotage a team and force them into last place.
fraud - Double your team's votes.
thief <user> - Steal a user during autobalance.
escape - Save yourself from the next challenge.
timeout <user> - Temporarily eliminate a single user.
bias <team name> - Request espionage.
swap <user> - Ask to swap teams with another user.
transfer <user> <amount/all> - Transfer tickets to another user."""

helpop = """

== Admin commands ==
refresh - Create user data that might not exist, and update user data that does. Recommended to use after manually assigning a team role.
tickets <give/remove/set> <user or team> <amount> - Manage currency.
"""

monologue = "You goddamn madman."
"""... Fine.

Congratulations. You've used the one nuke of the game on your own team. Was it worth it?

Did you think this through? Did you communicate with your team?

Or did you sit back as the people who trusted you with eleven hundred tickets begged you not to push the button, heartlessly reveling in their terror?

What did you hope to gain from this? Freedom? Sweet release for you and your comrades?
Or was it a sick, twisted sense of joy?
Did you think it would be funny to remove your entire team from the game, only to turn around and tell them it's a joke?

Either way, you're at the mercy of your former teammates now.

I can only pray that you made the right decision."""

def userwrite(user, tag, value):
    try:
        f = open('users/'+str(user if type(user) == int else user.id)+'.txt', 'r')
        d = ast.literal_eval(f.read())
        f.close()
    except FileNotFoundError:
        d = userdefault

    d[tag] = value
    f = open('users/'+str(user if type(user) == int else user.id)+'.txt', 'w')
    f.write(str(d))
    f.close()

def userread(user, tag):
    with open('users/'+str(user if type(user) == int else user.id)+'.txt', 'r') as f:
        return ast.literal_eval(f.read())[tag]

def createDataIfNecessary(user):
    try:
        f = open('users/'+str(user if type(user) == int else user.id)+'.txt', 'r')
        f.close()
    except FileNotFoundError:
        with open('users/'+str(user if type(user) == int else user.id)+'.txt', 'w') as f:
            f.write(str(userdefault))

def quickwrite(path, content):
    f = open(path,'w')
    f.write(content)
    f.close()

def quickread(path):
    try:
        f = open(path,'r')
        content = f.read()
        f.close()
    except:
        content = ""
    return content

def statewrite(tag, value):
    state = ast.literal_eval(quickread('state.txt'))
    state[tag] = value
    quickwrite('state.txt', str(state))

def stateread(tag):
    return ast.literal_eval(quickread('state.txt'))[tag]

def getHome():
    return client.get_guild(tribulations_id)

def getAllParticipants(eliminated = False):
    tribulations = getHome()
    ids = team_ids + ([role_elim_id] if eliminated else [])
    teams = [tribulations.get_role(i).members for i in ids if tribulations.get_role(i)]
    users = list(chain(*teams))
    return users

def getTeamMembers(idno):
    return getHome().get_role(int(idno)).members if getHome().get_role(int(idno)) else []

def tEmbed(text, author = None):
    if author:
        author = author if type(author) == int else author.id
    embed = discord.Embed(
        color = 0x00ff00,
        #title = (("tribulations/users/<@"+str(author)+">> ") if author else '') + "TRIBULATIONS.EXE",
        description = '```> {text}```'.format(text='\n> '.join(text.split('\n')))
    )
    if author:
        embed.set_footer(text="Requested by {0}".format(client.get_user(author)))
    return embed

def addconf(conf):
    confs = stateread("use_confirmations")
    confs.append(conf)
    statewrite("use_confirmations", confs)

def gethasconfu(user):
    conf = stateread("use_confirmations")
    existing = [i for i in conf if i[1] == (user if type(user) == int else user.id)]
    return len(existing) > 0

def getconfu(user):
    conf = stateread("use_confirmations")
    existing = [i for i in conf if i[1] == (user if type(user) == int else user.id)]
    return existing
    

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(client.user.mention) or \
       message.content.startswith("exe"):
        args = message.content.split(' ')
        args = [i for i in args if not i == '']

        if args[1].lower() in ['help', 'commands', '?']:
            helpmsg = helptext
            if message.author.id in op_ids:
                helpmsg = helpmsg + helpop
            await message.author.send(embed=tEmbed(helpmsg))
            await message.channel.send(embed=tEmbed("Command list sent to DMS.", message.author))
            
        
        elif args[1].lower() in ['shop', 'prizes']:
            shop = stateread('shop')
            shop_text = '\n'.join(['{item} [{cost} tickets - {stock}] - {desc}'.format(
                item=i.upper(),
                stock=(str(shop[i][0])+" in stock") if shop[i][0] >= 0 else "Infinite use",
                cost=shop[i][1],
                desc=shop[i][2]) for i in shop if shop[i][0] != 0])
            shop_msg = '== PRIZE CORNER ==\n\nUse "exe (item)" to select an item for purchase\n\n' + shop_text
            await message.author.send(embed=tEmbed(shop_msg))
            await message.channel.send(embed=tEmbed("Prize Corner listings have been sent to your DMS.", message.author))
            

        elif args[1].lower() in ['balance', 'bal']:
            createDataIfNecessary(message.author)
            if not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game.', message.author))
                return
            balance = userread(message.author, 'tickets')
            embed = tEmbed("CURRENT BALANCE: " + str(balance) + " TICKETS", message.author)
            await message.channel.send(embed=embed)
            

        elif args[1].lower() == 'transfer':
            createDataIfNecessary(message.author)
            if args[2].startswith('<@'):
                uid = int(args[2].lstrip('<@').strip('>'))
            else:
                user = getHome().get_member_named(args[2])
                if user:
                    uid = user.id
                else:
                    await message.channel.send(embed=tEmbed('Unable to find user with search term ' + args[2], message.author))
                    return
            if not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot transfer tickets.', message.author))
                return
            if uid == message.author.id or uid == client.user.id or not getHome().get_member(uid) in getAllParticipants():
                await message.channel.send(embed=tEmbed('You cannot transfer tickets to this person.', message.author))
                return
            tix = userread(message.author, 'tickets')
            if args[3] == 'all':
                amt = tix
            else:
                try:
                    amt = int(args[3])
                except ValueError:
                    await message.channel.send(embed=tEmbed('Please use a number or "all" for the amount.', message.author))
                    return
                if amt > tix:
                    await message.channel.send(embed=tEmbed("You don't have that many tickets.", message.author))
                    return
                elif amt < 0:
                    await message.channel.send(embed=tEmbed("Nice try.", message.author))
                    return
                elif amt == 0:
                    await message.channel.send(embed=tEmbed("Don't waste my time.", message.author))
                    return
            target = getHome().get_member(uid)
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            addconf(['transfer', message.author.id, uid, amt])
            embed = tEmbed('Transfer {num} tickets to {target}?\nexe confirm - Yes\nexe cancel - No'.format(num=amt,target=target.display_name), message.author)
            await message.channel.send(embed=embed)
            

        elif args[1].lower() in ['bomb', 'nuke']:
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['nuke'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['nuke'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            teamName = ' '.join([args[i] for i in range(2,len(args))])
            matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == teamName.lower()]
            if len(matches) > 0:
                team = matches[0]
                if gethasconfu(message.author):
                    await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                    return
                if team in message.author.roles:
                    msg = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nWARNING: YOU ARE ABOUT TO NUKE YOUR OWN GODDAMN TEAM.\n\nCONTINUING MAY HAVE VERY UNDESIRABLE CONSEQUENCES.\nARE YOU SURE YOU WANT TO CONTINUE?\n\nexe confirm - yes\nexe cancel - NO NO NO NO NO NO NO"
                    addconf(['friendlynuke', message.author.id, team.id])
                else:
                    msg = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nYou have targeted: {team}\n\nContinuing will eliminate this entire team for {cost} tickets.\nDo you want to continue?\n\nexe confirm - Yes\nexe cancel - No".format(team=team.name, cost=shop['nuke'][1])
                    addconf(['nuke', message.author.id, team.id])
                await message.channel.send(embed=tEmbed(msg, message.author))
            else:
                await message.channel.send(embed=tEmbed('"'+teamName+'" does not match the name of any participating teams.', message.author))

      
        elif args[1].lower() == 'eliminate':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['eliminate'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['eliminate'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            if args[2].startswith('<@'):
                uid = int(args[2].lstrip('<@').strip('>'))
            else:
                user = getHome().get_member_named(args[2])
                if user:
                    uid = user.id
                else:
                    await message.channel.send(embed=tEmbed('Unable to find user with search term ' + args[2], message.author))
                    return
            if uid == message.author.id or not getHome().get_member(uid) in getAllParticipants():
                await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
                return
            addconf(['eliminate', message.author.id, uid])
            msg = "You have chosen to eliminate {target} for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['eliminate'][1], target=getHome().get_member(uid).display_name)
            await message.channel.send(embed=tEmbed(msg, message.author))
        

        elif args[1].lower() == 'revive':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['revive'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['revive'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            if args[2].startswith('<@'):
                uid = int(args[2].lstrip('<@').strip('>'))
            else:
                user = getHome().get_member_named(args[2])
                if user:
                    uid = user.id
                else:
                    await message.channel.send(embed=tEmbed('Unable to find user with search term ' + args[2], message.author))
                    return
            if uid == message.author.id or not(getHome().get_member(uid) in getAllParticipants(True)) or userread(uid, 'lastTeam') != userread(message.author, 'lastTeam'):
                await message.channel.send(embed=tEmbed("You can't revive that person.", message.author))
                return
            addconf(['revive', message.author.id, uid])
            msg = "You have chosen to revive {target} for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['eliminate'][1], target=getHome().get_member(uid).display_name)
            await message.channel.send(embed=tEmbed(msg, message.author))
            

        elif args[1].lower() == 'peek':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['peek'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['peek'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            teamName = ' '.join([args[i] for i in range(2,len(args))])
            matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == teamName.lower()]
            if len(matches) <= 0:
                await message.channel.send(embed=tEmbed('"'+teamName+'" does not match the name of any participating teams.', message.author))
                return
            team = matches[0]
            if team.id == userread(message.author, 'lastTeam'):
                await message.channel.send(embed=tEmbed("You cannot peek your own team.", message.author))
                return
            peekers = stateread('peekers')
            if message.author.id in [i[0] for i in peekers]:
                await message.channel.send(embed=tEmbed("You are already peeking another team's channel!", message.author))
                return
            addconf(['peek', message.author.id, team_chan_ids[team.id]])
            msg = "You have chosen to peek {target}'s team channel for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['peek'][1], target=team.name)
            await message.channel.send(embed=tEmbed(msg, message.author))


        elif args[1].lower() == 'timeout':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['timeout'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['timeout'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            if args[2].startswith('<@'):
                uid = int(args[2].lstrip('<@').strip('>'))
            else:
                user = getHome().get_member_named(args[2])
                if user:
                    uid = user.id
                else:
                    await message.channel.send(embed=tEmbed('Unable to find user with search term ' + args[2], message.author))
                    return
            if uid == message.author.id or not getHome().get_member(uid) in getAllParticipants():
                await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
                return
            addconf(['timeout', message.author.id, uid])
            msg = "You have chosen to temporarily eliminate {target} for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['timeout'][1], target=getHome().get_member(uid).display_name)
            await message.channel.send(embed=tEmbed(msg, message.author))

        elif args[1].lower() == 'sabotage':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['sabotage'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['sabotage'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            teamName = ' '.join([args[i] for i in range(2,len(args))])
            matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == teamName.lower()]
            if len(matches) <= 0:
                await message.channel.send(embed=tEmbed('"'+teamName+'" does not match the name of any participating teams.', message.author))
                return
            team = matches[0]
            if team.id == userread(message.author, 'lastTeam'):
                await message.channel.send(embed=tEmbed("You cannot sabotage your own team.", message.author))
                return
            sabotage = stateread('sabotage')
            if sabotage:
                await message.channel.send(embed=tEmbed("A team has already been sabotaged!", message.author))
                return
            addconf(['sabotage', message.author.id, team.id])
            msg = "You have chosen to sabotage {target} for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['sabotage'][1], target=team.name)
            await message.channel.send(embed=tEmbed(msg, message.author))
            

        elif args[1].lower() == 'bias':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['bias'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['bias'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            teamName = ' '.join([args[i] for i in range(2,len(args))])
            matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == teamName.lower()]
            if len(matches) <= 0:
                await message.channel.send(embed=tEmbed('"'+teamName+'" does not match the name of any participating teams.', message.author))
                return
            team = matches[0]
            if team.id == userread(message.author, 'lastTeam'):
                await message.channel.send(embed=tEmbed("You cannot request bias against your own team.", message.author))
                return
            addconf(['bias', message.author.id, team.id])
            msg = "You have chosen to request insider info on {target} from the host for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['bias'][1], target=team.name)
            await message.channel.send(embed=tEmbed(msg, message.author))
            

        elif args[1].lower() == 'fraud':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['fraud'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['fraud'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            team = userread(message.author, 'lastTeam')
            frauds = stateread('frauds')
            if team in frauds:
                await message.channel.send(embed=tEmbed("Your team has already rigged the vote for this challenge.", message.author))
                return
            addconf(['fraud', message.author.id])
            msg = "You have chosen to shamelessly engage in election fraud for {cost} tickets.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['fraud'][1])
            await message.channel.send(embed=tEmbed(msg, message.author))
            

        elif args[1].lower() == 'escape':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            active = stateread('challengeActive')
            if active:
                await message.channel.send(embed=tEmbed("Escape Rope cannot be used while a challenge is ongoing.", message.author))
                return
            if amt < shop['escape'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['escape'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            addconf(['escape', message.author.id])
            msg = "You have chosen to escape from the next challenge for {cost} tickets.\nYou will be barred from prizes during this time.\n\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop['escape'][1])
            await message.channel.send(embed=tEmbed(msg, message.author))


        
        elif args[1].lower() == 'eliminate':
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            if amt < shop['eliminate'][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop['eliminate'][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            

        elif args[1].lower() == 'cancel':
            conf = stateread('use_confirmations')
            existing = [i for i in conf if i[1] == message.author.id]
            [conf.pop(i) for i in range(len(conf)-1,-1,-1) if conf[i][1] == message.author.id]
            statewrite('use_confirmations', conf)
            if len(existing) > 0:
                await message.channel.send(embed=tEmbed("Action cancelled.", message.author))
                

        elif args[1].lower() == 'confirm':
            conf = stateread('use_confirmations')
            actions = [conf.pop(i) for i in range(len(conf)-1,-1,-1) if conf[i][1] == message.author.id]
            action = actions[0] if len(actions) > 0 else None
            statewrite('use_confirmations', conf)

            if action[0] == 'transfer':
                createDataIfNecessary(action[2])
                invoke_amt = userread(action[1], 'tickets')
                target_amt = userread(action[2], 'tickets')
                invoke_amt -= action[3]
                target_amt += action[3]
                userwrite(action[1], 'tickets', invoke_amt)
                userwrite(action[2], 'tickets', target_amt)
                success_template = "== TRANSACTION SUCCESSFUL ==\n{invoker} sent {amt} tickets to {target}\n\nBalance after transfer:\n\n{invoker}: {i_amt} tickets\n{target}: {t_amt} tickets"
                success_msg = success_template.format(
                    amt = action[3],
                    invoker = getHome().get_member(action[1]).display_name,
                    target = getHome().get_member(action[2]).display_name,
                    i_amt = invoke_amt,
                    t_amt = target_amt
                    )
                await message.channel.send(embed=tEmbed(success_msg, message.author))

            if action[0] == 'nuke':
                for u in getTeamMembers(action[2]):
                    await u.add_roles(getHome().get_role(role_elim_id))
                    await u.remove_roles(getHome().get_role(action[2]))
                    userwrite(u, 'lastTeam', action[2])
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['nuke'][0] -= 1
                amt -= shop['nuke'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                await message.channel.send(embed=tEmbed("Now we are all sons of bitches.", message.author))

            if action[0] == 'friendlynuke':
                addconf(['nukemyownteamforrealsies', action[1], action[2]])
                finalwarning = "ARE YOU *ABSOLUTELY, 100% SURE* YOU WANT TO DO THIS?\n\nexe confirm - PLEASE\nexe cancel - DO NOT."
                await message.channel.send(embed=tEmbed(finalwarning, message.author))

            if action[0] == 'nukemyownteamforrealsies':
                for u in getTeamMembers(action[2]):
                    await u.add_roles(getHome().get_role(role_elim_id))
                    await u.remove_roles(getHome().get_role(action[2]))
                    userwrite(u, 'lastTeam', action[2])
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['nuke'][0] -= 1
                amt -= shop['nuke'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                await message.channel.send(embed=tEmbed(monologue, message.author))

            if action[0] == 'eliminate':
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(role_elim_id))
                await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['eliminate'][0] -= 1
                amt -= shop['eliminate'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0}.".format(u.display_name), message.author))

            if action[0] == 'revive':
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(userread(u, 'lastTeam')))
                await u.remove_roles(getHome().get_role(role_elim_id))
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['revive'][0] -= 1
                amt -= shop['revive'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nWelcome back, {0}!".format(u.display_name), message.author))

            if action[0] == 'peek':
                channel = getHome().get_channel(action[2])
                await channel.set_permissions(message.author, read_messages=True, send_messages=False, add_reactions=False)
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['peek'][0] -= 1
                amt -= shop['peek'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                peekers = stateread('peekers')
                peekers.append([action[1], action[2]])
                statewrite('peekers', peekers)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have special eyes.", message.author))

            if action[0] == 'timeout':
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(role_elim_id))
                await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['timeout'][0] -= 1
                amt -= shop['timeout'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                timeouts = stateread('timeouts')
                timeouts.append(u.id)
                statewrite('timeouts', timeouts)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0} for this challenge.".format(u.display_name), message.author))

            if action[0] == 'sabotage':
                role = getHome().get_role(action[2])
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['sabotage'][0] -= 1
                amt -= shop['sabotage'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                statewrite('sabotage', action[2])
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\n{0} can no longer participate in this challenge, and automatically loses.".format(role.name), message.author))

            if action[0] == 'bias':
                role = getHome().get_role(action[2])
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['bias'][0] -= 1
                amt -= shop['bias'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou are the favorite team. For now.", message.author))
                await client.get_user(host_id).send(str(message.author) + " used Bias and requests info on " + role.name + ".")

            if action[0] == 'fraud':
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['fraud'][0] -= 1
                amt -= shop['fraud'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                frauds = stateread('frauds')
                frauds.append(userread(message.author, 'lastTeam'))
                statewrite('frauds', frauds)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou suddenly feel like your vote matters. Like, a lot.", message.author))

            if action[0] == 'escape':
                shop = stateread('shop')
                amt = userread(message.author, 'tickets')
                shop['escape'][0] -= 1
                amt -= shop['escape'][1]
                statewrite('shop', shop)
                userwrite(message.author, 'tickets', amt)
                escape = stateread('escape')
                escape.append(message.author.id)
                statewrite('escape', escape)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou will not be part of the next challenge.", message.author))

        elif args[1].lower() == 'start' and int(message.author.id) in op_ids:#== host_id:
            statewrite('challengeActive', True)
            await message.channel.send("Challenge started. Escape Rope can no longer be used.")
                
        # change this to voting later
        elif args[1].lower() == 'callvote' and int(message.author.id) in op_ids:#== host_id:
            statewrite('challengeActive', False)
            peekers = stateread('peekers')
            
            for i in peekers:
                u = getHome().get_member(i[0])
                c = getHome().get_channel(i[1])
                await c.set_permissions(u, overwrite = None)
            statewrite('peekers', [])
            
            timeouts = stateread('timeouts')
            for i in timeouts:
                u = getHome().get_member(i)
                await u.add_roles(getHome().get_role(userread(u, 'lastTeam')))
                await u.remove_roles(getHome().get_role(role_elim_id))
            statewrite('timeouts', [])
            
            sabotage = stateread('sabotage')
            losers = getHome().get_role(sabotage if sabotage else int(args[2].lstrip("<@&").strip(">")))
            statewrite('sabotage', None)

            await message.channel.send("Challenge ended. {msg} {team}.".format(
                msg = "Due to sabotage, the vote automatically goes against" if sabotage else "The host has called a vote against",
                team=losers.name))

            # at some point you will need to do statewrite('escape', [])

        elif args[1].lower() == 'autobalance' and int(message.author.id) in op_ids:#== host_id:
            ab = stateread('autobalance')
            statewrite('autobalance', not(ab))
            await message.channel.send("Autobalance period has " + {False:"ended. THIEF can no longer be used.", True:"begun. THIEF can now be used."}[not(ab)])

        elif args[1].lower() == 'refresh' and message.author.id in op_ids:
            users = getAllParticipants(eliminated = True)
            [createDataIfNecessary(i) for i in users]
            for i in team_ids:
                for j in getTeamMembers(i):
                    userwrite(j, "lastTeam", i)
            await message.channel.send("data created & updated for all participants")
            

        elif args[1].lower() == 'tickets' and int(message.author.id) in op_ids:
            resp = {
                'give': 'Granted {num} tickets to {subject}.',
                'remove': 'Took {num} tickets from {subject}.',
                'set': "Set {subject}'s ticket balance to {num}."
                }
            if args[3].startswith("<@&"):
                members = getTeamMembers(args[3].lstrip("<@&").strip(">"))
                for member in members:
                    createDataIfNecessary(member.id)
                    tickets = userread(member.id, 'tickets')
                    if args[2] == 'give':
                        tickets += int(args[4])
                    elif args[2] == 'remove':
                        tickets -= int(args[4])
                    elif args[2] == 'set':
                        await message.channel.send("You probably shouldn't do that.")
                        return
                    userwrite(member.id, 'tickets', tickets)
                    await message.channel.send(resp[args[2]].format(num=args[4], subject=args[3]))
                    
            elif args[3].startswith("<@"):
                uid = int(args[3].lstrip("<@").strip(">"))
                createDataIfNecessary(uid)
                tickets = userread(uid, 'tickets')
                if args[2] == 'give':
                    tickets += int(args[4])
                elif args[2] == 'remove':
                    tickets -= int(args[4])
                elif args[2] == 'set':
                    tickets = int(args[4])
                userwrite(uid, 'tickets', tickets)
                await message.channel.send(resp[args[2]].format(num=args[4], subject=args[3]))
                
            else:
                target = getHome().get_member_named(args[3])
                if target:
                    createDataIfNecessary(target.id)
                    tickets = userread(target.id, 'tickets')
                    if args[2] == 'give':
                        tickets += int(args[4])
                    elif args[2] == 'remove':
                        tickets -= int(args[4])
                    elif args[2] == 'set':
                        tickets = int(args[4])
                    userwrite(target.id, 'tickets', tickets)
                    await message.channel.send(resp[args[2]].format(num=args[4], subject=target.mention))
                else:
                    await message.channel.send('Unable to find user with search term ' + args[3])
                    return
            
            
                        
                    
        #await message.channel.send("ack")
        
        

client.run('OTY3NDk3MzgxNTA1NTYwNjI2.YmRKJg.XfGDs0p99d6jHZ3QK3EPSgODiX0')
    
