import discord, ast, random
from itertools import chain
from misc import *

def userwrite(user, tag, value):
    # write directly to user data
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
    # read directly from user data
    with open('users/'+str(user if type(user) == int else user.id)+'.txt', 'r') as f:
        return ast.literal_eval(f.read())[tag]

def createDataIfNecessary(user):
    # create & update data for a user
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
    # i am stupid
    f = open(path,'w')
    f.write(content)
    f.close()

def quickread(path):
    # just return the contents of a file without having to open, read, and close every time
    try:
        f = open(path,'r')
        content = f.read()
        f.close()
    except:
        content = ""
    return content

def statewrite(tag, value):
    # write directly to the game state
    state = ast.literal_eval(quickread('state.txt'))
    state[tag] = value
    quickwrite('state.txt', str(state))

def stateread(tag):
    # read directly from the game state
    return ast.literal_eval(quickread('state.txt'))[tag]

def getHome():
    # return tribulations as a Guild
    return client.get_guild(tribulations_id)

def getStatusMsg():
    # return an editable PartialMessage that has the game status on it, if any
    msg_id = stateread('statusMessage')
    chan_id = stateread('statusChannel')
    if chan_id == 0 or msg_id == 0:
        return None
    return client.get_channel(chan_id).get_partial_message(msg_id)

def getAllParticipants(eliminated = False):
    # returns a list of all participating members (and, optionally, eliminated members)
    tribulations = getHome()
    ids = team_ids + ([role_elim_id] if eliminated else [])
    teams = [tribulations.get_role(i).members for i in ids if tribulations.get_role(i)]
    users = list(chain(*teams))
    return users

def getTeamMembers(team):
    # returns all Members of a team
    if type(team) in [int, str]:
        team = getHome().get_role(int(team))
    return team.members if team else []

def getStatus():
    # return a string with the status of each team
    result = []
    for tid in team_ids:
        team = getHome().get_role(tid)
        if not team:
            continue
        elim = getHome().get_role(role_elim_id)
        members = team.members
        ticket_counts = [userread(i, 'tickets') for i in members]
        members_text = ["{0} - Active, {1} tickets".format(members[i].mention, ticket_counts[i]) for i in range(len(members))]
        elim_text = ["~~{0} - Eliminated~~".format(i.mention) for i in elim.members if userread(i, 'lastTeam') == tid]
        roster_text = '\n'.join(members_text + elim_text)
        result.append("__**{0}**__\n{1}\n**Ticket total:** {2}".format(team.name.upper(), roster_text, sum(ticket_counts)))
    return '\n\n'.join(result) + '\n'

def tEmbed(text, author = None, colorOverride = None):
    # return a command-line-stylized Embed. yes, it could look better. THIS IS INTENTIONAL.
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
    # add a pending confirmation to the game state.
    # pending confirmations are generally lists, like so
    # ["action name", (user id), (extra argument 1), (extra argument 2)...]
    confs = stateread("use_confirmations")
    confs.append(conf)
    statewrite("use_confirmations", confs)

def gethasconfu(user):
    # check if a user has any pending confirmations
    conf = stateread("use_confirmations")
    existing = [i for i in conf if i[1] == (user if type(user) == int else user.id)]
    return len(existing) > 0

def getconfu(user):
    # get all pending confirmations for a user
    conf = stateread("use_confirmations")
    existing = [i for i in conf if i[1] == (user if type(user) == int else user.id)]
    return existing

def transact(user, item):
    # deduct an item's price from a user's ticket balance,
    # then remove 1 from that item's stock if it's finite.
    # separated into its own function to make exe confirm
    # easier to read and write for.
    item = item.lower()
    shop = stateread('shop')
    uid = user if type(user) == int else user.id
    amt = userread(uid, 'tickets')
    if shop[item][0] > 0:
        shop[item][0] -= 1
    amt -= shop[item][1]
    shop[item][1] += shop[item][3]
    statewrite('shop', shop)
    userwrite(uid, 'tickets', amt)

def findUser(arg):
    # try to find a user in Tribulations based on string input
    # returns str with error message if failed, discord.Member if successful
    if arg.startswith('<@') and not arg.startswith('<@&'):
        return getHome().get_member(int(arg.lstrip('<@').strip('>')))
    elif arg.startswith('<@!'):
        return getHome().get_member(int(arg.lstrip('<@!').strip('>')))
    else:
        user = getHome().get_member_named(arg)
        if user:
            return user
        else:
            return 'Unable to find user named "' + arg + '". (get_member_named() is case sensitive!)'

def findTeam(arg):
    # find team by name or reference
    # returns str with error message if failed, discord.Role if successful
    if arg.startswith('<@&'):
        return getHome().get_role(int(arg.lstrip('<@&').strip('>')))
    matches = [getHome().get_role(i) for i in team_ids if getHome().get_role(i) and getHome().get_role(i).name.lower() == arg.lower()]
    if len(matches) <= 0:
        return '"'+arg+'" does not match the name of any participating teams.'
    return matches[0]

def getTextArg(args, start):
    # get text with spaces from a specific argument onwards
    return ' '.join([args[i] for i in range(start,len(args))])

def distributeTickets(amt, users):
    # distribute amt tickets as evenly as possible between a list of users.
    # CRACKPOT IDEA
    # calculate number of tickets modulo number of users
    rem = amt % len(users)
    # subtract the remainder from the amount and divide by number of users
    base = (amt - rem) / len(users)
    # choose rem amount of users at random to get 1 more ticket than base
    # (also make a copy of the list so we don't actually modify the list that was passed in)
    users_editsafe = users.copy()
    extras = [users_editsafe.pop(random.randint(0, len(users)-1)) for i in range(rem)] # (this automatically separates them)
    for u in extras:
        tickets = userread(u, "tickets")
        tickets += int(base + 1)
        userwrite(u, "tickets", tickets)
    # give base amount of tickets to everyone else
    for u in users_editsafe:
        tickets = userread(u, "tickets")
        tickets += int(base)
        userwrite(u, "tickets", tickets)

def checkPurchaseErrors(user, prize, ignoreConf = False):
    # checks if a prize can be purchased based on the user and the prize in question.
    # returns a str with the error message if there is a problem, None if there are no issues.
    uid = user if type(user) == int else user.id
    if uid in stateread('escape') or not uid in [i.id for i in getAllParticipants()]:
        return 'You are not in the game.'
    createDataIfNecessary(uid)
    amt = userread(uid, 'tickets')
    shop = stateread('shop')
    bans = stateread('bannedItems')
    if prize.lower() in bans:
        return "{0} has been manually disabled.".format(prize.upper())
    if amt < shop[prize.lower()][1]:
        return "You don't have enough tickets for this prize."
    if shop[prize.lower()][0] == 0:
        return "This prize is out of stock."
    if gethasconfu(uid) and not ignoreConf:
        return 'You must first confirm or cancel: ' + ', '.join([i[0].upper() for i in getconfu(uid)])
    return None

async def updateStatusBoard():
    msg = getStatusMsg()
    if msg:
        await msg.edit(content=getStatus())

async def sendConfMessage(message, text, msgOverride = False, colorOverride = 0x00ff00):
    # lotta broken references here so i'm gonna fix it the stupid way
    shop = stateread('shop')
    args = message.content.split(' ')
    args = [i for i in args if not i == '']
    msg = text
    if not msgOverride:
        msg = msg + "\n\nThis will cost {cost} tickets.{stock}\nDo you wish to continue?\nexe confirm - Yes\nexe cancel - No".format(
            cost=shop[args[1]][1],
            stock="\n{0} of this item will remain.".format(shop[args[1]][0]) if shop[args[1]][0] > 0 else ""
            )
    await message.channel.send(embed=tEmbed(msg, message.author, colorOverride=colorOverride))