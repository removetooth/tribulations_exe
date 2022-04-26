import discord, ast, time
from itertools import chain

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
userdefault = {
    'tickets': 0,
    'lastTeam': None,
    'immune': False,
    'escaped': False,
    'vote': None
    }

team_ids = [
    959682463175696414, # Paypal Mafia
    960150245226995772, # Outcasts
    960177784641191987, # Starving Artists
    960260637106257920, # Raging Crack Addicts
    960996087244668948, # Femboy Association
    960381460240547860#,# Sceptile Fans :D
    #381951357470375936, # test role from testing server
    #967604532148305970
    ]
team_chan_ids = {
    team_ids[0]: 959682914944188467, # Paypal Mafia
    team_ids[1]: 960150552275197992, # Outcasts
    team_ids[2]: 960178086131949592, # Starving Artists
    team_ids[3]: 960265304443863120, # Raging Crack Addicts
    team_ids[4]: 960996278572040212, # Femboy Association
    team_ids[5]: 961005507408171019#,# Sceptile Fans :D
    #team_ids[6]: 967586316579667988,
    #team_ids[7]: 967586316579667988
    }
role_elim_id = 961755681432666202#967593430916153344
chan_prizes_id = 953328018506534965#967586316579667988
chan_bots_id = 953163427101167647
op_ids = [266389941423046657, 221992874886037504]
tribulations_id = 951647646102200320#373237751039918098
host_id = 221992874886037504#266389941423046657

prizes = ['nuke', 'eliminate', 'revive', 'immunity', 'sabotage', 'fraud', 'thief', 'escape', 'timeout', 'bias', 'swap']
# transfer is not treated internally as a shop item

helptext = """Use "exe (keyword)" to use a command.

help/commands/? - Show this dialog.
balance/bal - Check the number of tickets you have.
shop/prizes - Check the Prize Booth.
vote <number> - Cast a vote.

== Prize Booth commands ==
nuke <team> - Eliminate an entire team.
eliminate <user> - Eliminate another player.
revive <user> - Revive a teammate.
immunity - Give yourself voting immunity.
sabotage <team> - Sabotage a team and force them into last place.
fraud - Double your team's votes.
thief <user> - Steal a user during autobalance.
escape - Save yourself from the next challenge.
timeout <user> - Temporarily eliminate a single user.
bias <team> - Request espionage.
swap <user> - Ask to swap teams with another user.
transfer <(amount)/all> <user> - Transfer tickets to another user."""

helpop = """

== Admin commands ==
kill - Stop the bot.
refresh - Create user data that might not exist, and update user data that does. Recommended to use after manually assigning a team role.
setlastteam <user> <team> - Set the last team an eliminated member was on. Used for revivals."""

helphost = """

== Host commands ==
tickets <give/remove/set> <amount> <user or team> - Manage currency.
start - Mark the start of a challenge. Disables Escape Rope.
callvote <team> - Call a vote against a team. Ends the active challenge.
endvote - End the voting period. Eliminates the loser.
autobalance - Toggle the autobalance period on and off. Enables/disables Thief.
changeprize <item> <stock/cost/desc> <value> - Edit prizes.
toggleitem <item> - Toggle the ability to purchase a prize."""

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
    uid = str(user if type(user) in [int, str] else user.id)
    try:
        f = open('users/'+uid+'.txt', 'r')
        udata = ast.literal_eval(f.read())
        f.close()
        for i in userdefault:
            if not i in udata:
                udata[i] = userdefault[i]
        with open('users/'+uid+'.txt', 'w') as f:
            f.write(str(udata))
    except FileNotFoundError:
        with open('users/'+uid+'.txt', 'w') as f:
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

def getTeamMembers(team):
    if type(team) in [int, str]:
        team = getHome().get_role(int(team))
    return team.members if team else []

def tEmbed(text, author = None, colorOverride = None):
    if author:
        author = author if type(author) == int else author.id
    embed = discord.Embed(
        color = colorOverride if colorOverride else 0x00ff00,
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

def transact(user, item):
    shop = stateread('shop')
    uid = user if type(user) == int else user.id
    amt = userread(uid, 'tickets')
    if shop[item][0] > 0:
        shop[item][0] -= 1
    amt -= shop[item][1]
    statewrite('shop', shop)
    userwrite(uid, 'tickets', amt)

def findUser(arg):
    if arg.startswith('<@') and not arg.startswith('<@&'):
        return getHome().get_member(int(arg.lstrip('<@').strip('>')))
    elif arg.startswith('<@!'):
        return getHome().get_member(int(arg.lstrip('<@!').strip('>')))
    else:
        user = getHome().get_member_named(arg)
        if user:
            return user
        else:
            return 'Unable to find user named ' + arg

def findTeam(arg):
    if arg.startswith('<@&'):
        return getHome().get_role(int(arg.lstrip('<@&').strip('>')))
    matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == arg.lower()]
    if len(matches) <= 0:
        return '"'+teamName+'" does not match the name of any participating teams.'
    return matches[0]

def getTextArg(args, start):
    return ' '.join([args[i] for i in range(start,len(args))])


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    game = discord.Game("exe help")
    await client.change_presence(status=discord.Status.online, activity=game)

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
            if message.author.id == host_id:
                helpmsg = helpmsg + helphost
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
            # exe transfer (amount)/all user
            createDataIfNecessary(message.author)
            name = getTextArg(args, 3)
            u = findUser(name)
            if type(u) == str:
                await message.channel.send(embed=tEmbed(u, message.author))
                return
            if not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot transfer tickets.', message.author))
                return
            if u.id == message.author.id or u.id == client.user.id or not u in getAllParticipants():
                await message.channel.send(embed=tEmbed('You cannot transfer tickets to this person.', message.author))
                return
            tix = userread(message.author, 'tickets')
            if args[2] == 'all':
                amt = tix
            else:
                try:
                    amt = int(args[2])
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
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            addconf(['transfer', message.author.id, u.id, amt])
            embed = tEmbed('Transfer {num} tickets to {target}?\nexe confirm - Yes\nexe cancel - No'.format(num=amt,target=u.display_name), message.author)
            await message.channel.send(embed=embed)
            
            
        # === PRIZE BOOTH COMMANDS: ===
        
        elif args[1].lower() in prizes and message.channel.id == chan_prizes_id:
            
            if message.author.id in stateread('escape') or not message.author in getAllParticipants():
                await message.channel.send(embed=tEmbed('You are not in the game and cannot purchase this item.', message.author))
                return
            amt = userread(message.author, 'tickets')
            shop = stateread('shop')
            bans = stateread('bannedItems')
            if args[1].lower() in bans:
                await message.channel.send(embed=tEmbed("{0} has been manually disabled.".format(args[1].upper()), message.author))
                return
            if amt < shop[args[1].lower()][1]:
                await message.channel.send(embed=tEmbed("You don't have enough tickets for this prize.", message.author))
                return
            if shop[args[1].lower()][0] == 0:
                await message.channel.send(embed=tEmbed("This prize is out of stock.", message.author))
                return
            if gethasconfu(message.author):
                await message.channel.send(embed=tEmbed('You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(message.author)]), message.author))
                return
            msgOverride = False
            colorOverride = None
            

            if args[1].lower() == 'nuke':
                teamName = getTextArg(args, 2)
                team = findTeam(teamName)
                if type(team) == str:
                    await message.channel.send(embed=tEmbed(team, message.author))
                    return
                msgOverride = True
                if team in message.author.roles:
                    msg = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nWARNING: YOU ARE ABOUT TO NUKE YOUR OWN GODDAMN TEAM.\n\nCONTINUING MAY HAVE VERY UNDESIRABLE CONSEQUENCES.\nARE YOU SURE YOU WANT TO CONTINUE?\n\nexe confirm - yes\nexe cancel - NO NO NO NO NO NO NO"
                    colorOverride = 0xff0000
                    addconf(['friendlynuke', message.author.id, team.id])
                else:
                    msg = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nYou have targeted: {team}\n\nContinuing will eliminate this entire team for {cost} tickets.\nDo you want to continue?\n\nexe confirm - Yes\nexe cancel - No".format(team=team.name, cost=shop['nuke'][1])
                    addconf(['nuke', message.author.id, team.id])

          
            elif args[1].lower() == 'eliminate':
                name = getTextArg(args, 2)
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
                if u.id == message.author.id or not u in getAllParticipants():
                    await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
                    return
                addconf(['eliminate', message.author.id, u.id])
                msg = "You have chosen to eliminate {target}.".format(target=u.display_name)
            

            elif args[1].lower() == 'revive':
                name = getTextArg(args, 2)
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
                if u.id == message.author.id or not(u in getAllParticipants(eliminated=True)) or userread(u.id, 'lastTeam') != userread(message.author, 'lastTeam'):
                    await message.channel.send(embed=tEmbed("You can't revive that person.", message.author))
                    return
                addconf(['revive', message.author.id, u.id])
                msg = "You have chosen to revive {target}.".format(target=u.display_name)
                

            elif args[1].lower() == 'peek':
                teamName = getTextArg(args, 2)
                team = findTeam(teamName)
                if type(team) == str:
                    await message.channel.send(embed=tEmbed(team, message.author))
                    return
                if team.id == userread(message.author, 'lastTeam'):
                    await message.channel.send(embed=tEmbed("You cannot peek your own team.", message.author))
                    return
                peekers = stateread('peekers')
                if message.author.id in [i[0] for i in peekers]:
                    await message.channel.send(embed=tEmbed("You are already peeking another team's channel!", message.author))
                    return
                addconf(['peek', message.author.id, team_chan_ids[team.id]])
                msg = "You have chosen to peek {target}'s team channel.".format(target=team.name)


            elif args[1].lower() == 'timeout':
                name = getTextArg(args, 2)
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
                if u.id == message.author.id or not u in getAllParticipants():
                    await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
                    return
                addconf(['timeout', message.author.id, u.id])
                msg = "You have chosen to temporarily eliminate {target}.".format(target=u.display_name)
                

            elif args[1].lower() == 'sabotage':
                teamName = getTextArg(args, 2)
                team = findTeam(teamName)
                if type(team) == str:
                    await message.channel.send(embed=tEmbed(team, message.author))
                    return
                if team.id == userread(message.author, 'lastTeam'):
                    await message.channel.send(embed=tEmbed("You cannot sabotage your own team.", message.author))
                    return
                sabotage = stateread('sabotage')
                if sabotage:
                    await message.channel.send(embed=tEmbed("A team has already been sabotaged!", message.author))
                    return
                addconf(['sabotage', message.author.id, team.id])
                msg = "You have chosen to sabotage {target}.".format(target=team.name)
                

            elif args[1].lower() == 'bias':
                teamName = getTextArg(args, 2)
                team = findTeam(teamName)
                if type(team) == str:
                    await message.channel.send(embed=tEmbed(team, message.author))
                    return
                if team.id == userread(message.author, 'lastTeam'):
                    await message.channel.send(embed=tEmbed("You cannot request bias against your own team.", message.author))
                    return
                addconf(['bias', message.author.id, team.id])
                msg = "You have chosen to request insider info on {target} from the host.".format(target=team.name)
                

            elif args[1].lower() == 'fraud':
                team = userread(message.author, 'lastTeam')
                frauds = stateread('frauds')
                if team in frauds:
                    await message.channel.send(embed=tEmbed("Your team has already rigged the vote for this challenge.", message.author))
                    return
                addconf(['fraud', message.author.id])
                msg = "You and your team have chosen to shamelessly engage in election fraud."
                

            elif args[1].lower() == 'escape':
                active = stateread('challengeActive') or stateread('voteActive')
                escapes = stateread('escape')
                if active:
                    await message.channel.send(embed=tEmbed("Escape Rope cannot be used while a challenge or vote is ongoing.", message.author))
                    return
                if message.author.id in escapes: # possibly unnecessary
                    await message.channel.send(embed=tEmbed("You've already used Escape Rope for this challenge.", message.author))
                    return
                addconf(['escape', message.author.id])
                msg = "You have chosen to escape from the next challenge. You will be barred from prizes during this time."
                

            elif args[1].lower() == 'thief':
                ab = stateread('autobalance')
                if not ab:
                    await message.channel.send(embed=tEmbed("You cannot use Thief outside of autobalance.", message.author))
                    return
                userTeam = userread(message.author, "lastTeam")
                members = getTeamMembers(userTeam)
                if len(members) >= 4:
                    await message.channel.send(embed=tEmbed("Your team already has 4 members!", message.author))
                    return
                name = getTextArg(args, 2)
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
                targetTeam = userread(u, "lastTeam")
                if targetTeam == userTeam:
                    await message.channel.send(embed=tEmbed("That person is already on your team!", message.author))
                    return
                addconf(['thief', message.author.id, u.id])
                msg = "You have chosen to steal {0} for your own team.".format(u.display_name)


            elif args[1].lower() == 'swap':
                swap = stateread('swap_requests')
                existing = [i for i in swap if i[0] == message.author.id]
                if len(existing) > 0:
                    await message.channel.send(embed=tEmbed("You already have an open swap request.", message.author))
                    return
                name = getTextArg(args, 2)
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
                userTeam = userread(message.author, "lastTeam")
                targetTeam = userread(u, "lastTeam")
                if u.id == message.author.id or userTeam == targetTeam or not u in getAllParticipants():
                    await message.channel.send(embed=tEmbed("You can't swap with that person.", message.author))
                    return
                msgOverride = True
                swaps = stateread('swap_requests')
                swaps.append([message.author.id, u.id])
                statewrite('swap_requests', swaps)
                if not u in message.mentions:
                    await message.channel.send(u.mention)
                msg = "{0} has requested to swap teams with {1}.\n\nexe accept - Swap teams\nexe deny - Don't swap\n\nexe cancel - Cancel request".format(message.author.display_name, u.display_name)

            elif args[1].lower() == 'immunity':
                immunities = stateread('immunities')
                if message.author.id in immunities:
                    await message.channel.send(embed=tEmbed("You are already immune.", message.author))
                    return
                addconf(['immunity', message.author.id])
                msg = "You have chosen to give yourself immunity to the next vote."                
                

            if not msgOverride:
                msg = msg + "\n\nThis will cost {cost} tickets.\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(cost=shop[args[1]][1])
            await message.channel.send(embed=tEmbed(msg, message.author, colorOverride=colorOverride))
        
                
        # === END OF PRIZE COMMANDS ===
        
        elif args[1].lower() == 'accept':
            swap = stateread('swap_requests')
            requests = [swap.pop(i) for i in range(len(swap)-1,-1,-1) if swap[i][1] == message.author.id]
            request = requests[0] if len(requests) > 0 else None
            statewrite('swap_requests', swap)
            if request == None:
                return
            role0 = getHome().get_role(userread(request[0], 'lastTeam'))
            role1 = getHome().get_role(userread(request[1], 'lastTeam'))
            u0 = getHome().get_member(request[0])
            u1 = getHome().get_member(request[1])
            await u0.add_roles(role1)
            await u0.remove_roles(role0)
            await u1.add_roles(role0)
            await u1.remove_roles(role1)
            userwrite(u0, 'lastTeam', role1.id)
            userwrite(u1, 'lastTeam', role0.id)
            transact(u1, 'swap')
            msg = "Swap request accepted.\n\n{u0} is now on {r1}.\n{u1} is now on {r0}.".format(u0=u0.display_name, u1=u1.display_name, r0=role0, r1=role1)
            await message.channel.send(embed=tEmbed(msg, message.author))
            

        elif args[1].lower() == 'deny':
            swap = stateread('swap_requests')
            existing = [swap.pop(i) for i in range(len(swap)-1,-1,-1) if swap[i][1] == message.author.id]
            statewrite('swap_requests', swap)
            if len(existing) > 0:
                await message.channel.send(embed=tEmbed("Swap request denied.", message.author))
        

        elif args[1].lower() == 'cancel':
            conf = stateread('use_confirmations')
            existing = [conf.pop(i) for i in range(len(conf)-1,-1,-1) if conf[i][1] == message.author.id]
            statewrite('use_confirmations', conf)
            
            swap = stateread('swap_requests')
            existing_swap = [swap.pop(i) for i in range(len(swap)-1,-1,-1) if swap[i][0] == message.author.id]
            statewrite('swap_requests', swap)
            
            if len(existing) > 0 or len(existing_swap) > 0:
                await message.channel.send(embed=tEmbed("Action cancelled.", message.author))
                

        elif args[1].lower() == 'confirm':
            conf = stateread('use_confirmations')
            actions = [conf.pop(i) for i in range(len(conf)-1,-1,-1) if conf[i][1] == message.author.id]
            action = actions[0] if len(actions) > 0 else None
            statewrite('use_confirmations', conf)

            if action == None:
                return

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
                transact(message.author, 'nuke')
                for u in getTeamMembers(action[2]):
                    await u.add_roles(getHome().get_role(role_elim_id))
                    await u.remove_roles(getHome().get_role(action[2]))
                    userwrite(u, 'lastTeam', action[2])
                await message.channel.send(embed=tEmbed("Now we are all sons of bitches.", message.author))

            if action[0] == 'friendlynuke':
                addconf(['nukemyownteamforrealsies', action[1], action[2]])
                finalwarning = "ARE YOU *ABSOLUTELY, 100% SURE* YOU WANT TO DO THIS?\n\nexe confirm - PLEASE\nexe cancel - DO NOT."
                await message.channel.send(embed=tEmbed(finalwarning, message.author, colorOverride=0xffa500))

            if action[0] == 'nukemyownteamforrealsies':
                transact(message.author, 'nuke')
                for u in getTeamMembers(action[2]):
                    await u.add_roles(getHome().get_role(role_elim_id))
                    await u.remove_roles(getHome().get_role(action[2]))
                    userwrite(u, 'lastTeam', action[2])
                await message.channel.send(embed=tEmbed(monologue, message.author))

            if action[0] == 'eliminate':
                transact(message.author, 'eliminate')
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(role_elim_id))
                await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0}.".format(u.display_name), message.author))

            if action[0] == 'revive':
                transact(message.author, 'revive')
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(userread(u, 'lastTeam')))
                await u.remove_roles(getHome().get_role(role_elim_id))
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nWelcome back, {0}!".format(u.display_name), message.author))

            if action[0] == 'peek':
                transact(message.author, 'peek')
                channel = getHome().get_channel(action[2])
                await channel.set_permissions(message.author, read_messages=True, send_messages=False, add_reactions=False)
                peekers = stateread('peekers')
                peekers.append([action[1], action[2]])
                statewrite('peekers', peekers)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have special eyes.", message.author))

            if action[0] == 'timeout':
                transact(message.author, 'timeout')
                u = getHome().get_member(action[2])
                await u.add_roles(getHome().get_role(role_elim_id))
                await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
                timeouts = stateread('timeouts')
                timeouts.append(u.id)
                statewrite('timeouts', timeouts)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0} for this challenge.".format(u.display_name), message.author))

            if action[0] == 'sabotage':
                transact(message.author, 'sabotage')
                role = getHome().get_role(action[2])
                statewrite('sabotage', action[2])
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\n{0} can no longer participate in this challenge, and automatically loses.".format(role.name), message.author))

            if action[0] == 'bias':
                transact(message.author, 'bias')
                role = getHome().get_role(action[2])
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou are the favorite team. For now.", message.author))
                await client.get_user(host_id).send(str(message.author) + " used Bias and requests info on " + role.name + ".")

            if action[0] == 'fraud':
                transact(message.author, 'fraud')
                frauds = stateread('frauds')
                frauds.append(userread(message.author, 'lastTeam'))
                statewrite('frauds', frauds)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou suddenly feel like your vote matters. Like, a lot.", message.author))

            if action[0] == 'escape':
                transact(message.author, 'escape')
                escape = stateread('escape')
                escape.append(message.author.id)
                statewrite('escape', escape)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou will not be part of the next challenge.", message.author))

            if action[0] == 'thief':
                transact(message.author, 'thief')
                u = getHome().get_member(action[2])
                role = getHome().get_role(userread(message.author, 'lastTeam'))
                await u.add_roles(role)
                await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
                userwrite(u, 'lastTeam', role.id)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\n{target} has been abducted by {team}!".format(target=u.display_name, team=role.name), message.author))

            if action[0] == 'immunity':
                transact(message.author, 'immunity')
                immunities = stateread('immunities')
                immunities.append(message.author.id)
                statewrite('immunities', immunities)
                await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou feel invincible. Whether or not you are is another matter entirely...", message.author))


        # === HOST/ADMIN COMMANDS ===

        elif args[1].lower() == 'start' and message.author.id == host_id:
            statewrite('challengeActive', True)
            await message.channel.send("Challenge started. Escape Rope can no longer be used.")
                
        # change this to voting later
        elif args[1].lower() == 'callvote' and message.author.id == host_id:
            teamName = getTextArg(args, 2)
            sabotage = stateread('sabotage')
            losers = getHome().get_role(sabotage) if sabotage else findTeam(teamName)
            if type(losers) == str:
                await message.channel.send(embed=tEmbed(losers, message.author))
                return            
            statewrite('sabotage', None)
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

            await message.channel.send("Challenge ended. {msg} {team}.".format(
                msg = "Due to sabotage, the vote automatically goes against" if sabotage else "The host has called a vote against",
                team=losers.name))
            
            escapes = stateread('escape')
            immunities = stateread('immunities')
            losingTeamMembers = [i for i in getTeamMembers(losers) if not(i in escapes or i in immunities)]
            statewrite('votingActive', True)
            statewrite('votingOpts', [i.id for i in losingTeamMembers])

            for tid in team_ids:
                channel = getHome().get_channel(team_chan_ids[tid])
                if channel == None:
                    continue
                msg = "You must cast out one of your own.\n\nTime to choose." if tid == losers.id \
                      else "Voting time!\nChoose a contestant to eliminate."
                embed = tEmbed(msg)
                block = '\n'.join(['`{0}` - {1}'.format(i+1, losingTeamMembers[i].mention) for i in range(len(losingTeamMembers))])
                embed.add_field(name='Chopping Block', value=block)
                embed.set_footer(text="Vote using the reactions below or with exe vote (number).")
                poll = await channel.send(embed=embed)
                [await poll.add_reaction(str(i+1)+'\N{COMBINING ENCLOSING KEYCAP}') for i in range(len(losingTeamMembers))]
                

        elif args[1].lower() == 'endvote' and message.author.id == host_id:
            tally = {i: 0 for i in stateread('votingOpts')}
            frauds = stateread('frauds')
            immunities = stateread('immunities')
            for tid in team_ids:
                for member in getTeamMembers(tid):
                    vote = userread(member, 'vote')
                    if not vote:
                        continue
                    if vote == member.id:
                        voteNum = 3
                    elif member.id in tally:
                        voteNum = 2
                    else:
                        voteNum = 1
                    if tid in frauds:
                        voteNum = voteNum * 2
                    tally[vote] = tally[vote] + voteNum
            highest = 0
            loser = 0
            second = 0
            for i in tally:
                if tally[i] >= highest:
                    second = loser
                    loser = i
                    highest = tally[i]
                if tally[i] >= second and tally[i] < highest:
                    second = i
            isLoserImmune = loser in immunities
            statewrite('votingActive', False)
            statewrite('votingOpts', [])
            statewrite('lastVote', [loser, second])
            statewrite('escape', [])
            statewrite('frauds', [])
            statewrite('immunities', [])
            u = getHome().get_member(loser if not isLoserImmune else second)
            for i in team_ids:
                for j in getTeamMembers(i):
                    userwrite(j, 'vote', None)
                    userwrite(j, "lastTeam", i)
            text_tally = '\n'.join(['<@{user}>: {votes} votes'.format(user=i, votes=tally[i]) for i in tally])
            embed = discord.Embed(title='Final Tally', description = text_tally, color = 0x00ff00)
            extra_comments = "" if not isLoserImmune else "\n<@{0}>'s vote immmunity deflects the loss to <@{1}>.\n".format(loser, second)
            await u.add_roles(getHome().get_role(role_elim_id))
            await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
            await message.channel.send("The vote has ended.\n"+extra_comments+"\n{0} is no more.".format(u.mention), embed=embed)
        

        elif args[1].lower() == 'autobalance' and message.author.id == host_id:
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


        elif args[1].lower() == 'kill' and message.author.id in op_ids:
            await message.channel.send('stopping')
            await client.close()
            

        elif args[1].lower() == 'tickets' and message.author.id == host_id:
            # exe tickets give/remove/set amount user/team
            resp = {
                'give': 'Granted {num} tickets to {subject}.',
                'remove': 'Took {num} tickets from {subject}.',
                'set': "Set {subject}'s ticket balance to {num}."
                }
            name = getTextArg(args, 4)
            u = findUser(name)
            if not type(u) == str:
                createDataIfNecessary(u)
                tickets = userread(u, 'tickets')
                if args[2] == 'give':
                    tickets += int(args[3])
                elif args[2] == 'remove':
                    tickets -= int(args[3])
                elif args[2] == 'set':
                    tickets = int(args[3])
                userwrite(u, 'tickets', tickets)
                await message.channel.send(resp[args[2]].format(num=args[3], subject=u.display_name))
            else:
                team = findTeam(name)
                if type(team) == str:
                    await message.channel.send("Unable to find user or team with name " + args[4])
                    return
                members = getTeamMembers(team)
                for member in members:
                    createDataIfNecessary(member)
                    tickets = userread(member, 'tickets')
                    if args[2] == 'give':
                        tickets += int(args[3])
                    elif args[2] == 'remove':
                        tickets -= int(args[3])
                    elif args[2] == 'set':
                        await message.channel.send("You probably shouldn't do that. (TODO: add a confirmation dialog)")
                        return
                    userwrite(member, 'tickets', tickets)
                    await message.channel.send(resp[args[2]].format(num=args[3], subject=team.name))
                    

        elif args[1].lower() == 'setlastteam' and message.author.id in op_ids:
            u = findUser(args[2])
            teamName = getTextArg(args,3)
            team = findTeam(teamName)
            if type(u) == str or type(team) == str:
                await message.channel.send("Invalid user or team name.")
                return
            userwrite(u, 'lastTeam', team.id)
            await message.channel.send('Set last team of user {0} to {1}'.format(u.display_name, team.name))
            

        elif args[1].lower() == 'changeprize' and message.author.id == host_id:
            shop = stateread('shop')
            args[2] = args[2].lower()
            if args[3] == 'stock':
                shop[args[2]][0] = int(args[4])
            elif args[3] == 'cost':
                shop[args[2]][1] = int(args[4])
            elif args[3] == 'desc':
                shop[args[2]][2] = getTextArg(args,4)
            else:
                await message.channel.send('invalid operation')
                return
            statewrite('shop', shop)
            await message.channel.send('item {0} updated'.format(args[3]))


        elif args[1].lower() == 'toggleitem' and message.author.id == host_id:
            bans = stateread('bannedItems')
            args[2] = args[2].lower()
            if args[2] in bans:
                bans.remove(args[2])
                await message.channel.send('Item {0} can now be bought.'.format(args[2].upper()))
            else:
                bans.append(args[2])
                await message.channel.send('Item {0} can no longer be bought.'.format(args[2].upper()))
            statewrite('bannedItems', bans)


        elif args[1].lower() == 'vote' and stateread('votingActive') and message.author in getAllParticipants() and int(args[2]) <= len(stateread("votingOpts")):
            index = int(args[2])-1
            vote = userread(message.author, 'vote')
            opts = stateread('votingOpts')
            target = getHome().get_member(opts[index])
            feedback = ('You have changed your vote to {0}.' if vote else 'You have voted for {0}.').format(target.display_name)
            userwrite(message.author, 'vote', opts[index])
            await message.author.send(feedback)
            
            
                            
        #await message.channel.send("ack")
                    
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    
    if reaction.message.author == client.user and \
       len(reaction.message.embeds) == 1 and \
       stateread('votingActive') and \
       reaction.message.embeds[0].footer.text == "Vote using the reactions below or with exe vote (number)." \
       and reaction.count >= 1 \
       and user in getAllParticipants() \
       and int(reaction.emoji[0]) <= len(stateread("votingOpts")):
        index = int(reaction.emoji[0])-1
        vote = userread(user, 'vote')
        opts = stateread('votingOpts')
        target = getHome().get_member(opts[index])
        feedback = ('You have changed your vote to {0}.' if vote else 'You have voted for {0}.').format(target.display_name)
        userwrite(user, 'vote', opts[index])
        await user.send(feedback)
        #await reaction.message.channel.send('ack')
        

client.run('OTY3NDk3MzgxNTA1NTYwNjI2.YmRKJg.XfGDs0p99d6jHZ3QK3EPSgODiX0')
    