import discord, random, ast
from misc import *
from util import *

# == Transfer ==
async def cmdTRANSFER(message, args):
    # exe transfer (amount)/all user
    # this has gotten absolutely ridiculous

    # make sure there aren't any issues first
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return

    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return

    votingOpts = stateread('votingOpts')
    if message.author.id in votingOpts:
        await message.channel.send(embed=tEmbed('You are being voted on and cannot transfer tickets.', message.author))
        return

    # read args 3 and onwards as one string & initialize some stuff
    inStr = getTextArg(args, 3)
    targets = []
    cantTransferMsg = 'You cannot transfer tickets to one or more of these recipients.'
    
    # TODO: consider splitting some of this off into its own function
    # get users, if target is a list of recipients
    if ', ' in inStr:
        names = inStr.split(', ')
        for name in names:
            u = findUser(name)
            if type(u) == str:
                await message.channel.send(embed=tEmbed(u, message.author))
                return
            targets.append(u)
    
    # if not a list of recipients, figure out what the hell else it is
    else:
        u = findUser(inStr)
        if type(u) == str:
            team = findTeam(inStr)
            if type(team) == str:
                msg = 'Unable to find user or team with name "{0}. (get_user_named() is case sensitive!)".'.format(inStr)
                await message.channel.send(embed=tEmbed(msg, message.author))
                return
            targets = [i for i in getTeamMembers(team) if i.id != message.author.id] # exclude self from team targeting
        else:
            targets = [u]
            cantTransferMsg = 'You cannot transfer tickets to this person.' # should probably add a separate check for len(targets)

    # check if any of the targets cannot receive tickets
    for u in targets:  
        if u.id in [message.author.id, client.user.id] + votingOpts or not u in getAllParticipants():
            await message.channel.send(embed=tEmbed(cantTransferMsg, message.author))
            return
    
    # try to read the number of tickets to send
    tix = userread(message.author, 'tickets')
    if args[2] == 'all':
        amt = tix
    else:
        try:
            amt = int(args[2])
        except ValueError:
            await message.channel.send(embed=tEmbed('Please use a number or "all" for the amount.', message.author))
            return

        # for specific amounts, sanity check the number first
        if amt > tix:
            await message.channel.send(embed=tEmbed("You don't have that many tickets.", message.author))
            return
        elif amt < 0:
            await message.channel.send(embed=tEmbed("Nice try.", message.author))
            return
        elif amt == 0:
            await message.channel.send(embed=tEmbed("Don't waste my time.", message.author))
            return

    # ask user for confirmation
    addconf(['transfer', message.author.id, [u.id for u in targets], amt])
    text = '{num} tickets will be transferred to: {targets}\nDo you wish to proceed?\n\nexe confirm - Yes\nexe cancel - No'.format(
        num=amt,
        targets=', '.join([u.display_name for u in targets])
        )
    await sendConfMessage(message, text, msgOverride = True)

async def confTRANSFER(message, action):
    # format: ['transfer', invoker_id, [recipient_ids], amount]
    # make sure every recipient has a 'tickets' field in userdata
    [createDataIfNecessary(i) for i in action[2]]
    # deduct tickets from invoker
    invoke_amt = userread(action[1], 'tickets')
    invoke_amt -= action[3]
    userwrite(action[1], 'tickets', invoke_amt)
    # distribute tickets among all recipients
    distributeTickets(action[3], action[2])
    # generate and send an appropriate success message
    target_amt = userread(action[2][0], 'tickets') # leftover from only-one-person-at-a-time transfer
    if len(action[2]) <= 1:
        success_template = "== TRANSACTION SUCCESSFUL ==\n{invoker} sent {amt} tickets to {target}\n\nBalance after transfer:\n\n{invoker}: {i_amt} tickets\n{target}: {t_amt} tickets"
    else:
        success_template = "== TRANSACTION SUCCESSFUL ==\n{invoker} distributed {amt} tickets between: {targets}"
    names = [getHome().get_member(i).display_name for i in action[2]]
    success_msg = success_template.format(
        amt = action[3],
        invoker = getHome().get_member(action[1]).display_name,
        target = names[0],
        targets = ', '.join(names),
        i_amt = invoke_amt,
        t_amt = target_amt
        )
    await message.channel.send(embed=tEmbed(success_msg, message.author))
    await updateStatusBoard()

# == Nuke ==
async def cmdNUKE(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    teamName = getTextArg(args, 2)
    team = findTeam(teamName)
    if type(team) == str:
        await message.channel.send(embed=tEmbed(team, message.author))
        return
    colorOverride = 0x00ff00
    if team in message.author.roles:
        text = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nWARNING: YOU ARE ABOUT TO NUKE YOUR OWN GODDAMN TEAM.\n\nCONTINUING MAY HAVE VERY UNDESIRABLE CONSEQUENCES.\nARE YOU SURE YOU WANT TO CONTINUE?\n\nexe confirm - yes\nexe cancel - NO NO NO NO NO NO NO"
        colorOverride = 0xff0000
        addconf(['friendlynuke', message.author.id, team.id])
    else:
        text = "/!\\ NUCLEAR WARHEAD ARMED /!\\\n\nYou have targeted: {team}\n\nContinuing will eliminate this entire team for {cost} tickets.\nDo you want to continue?\n\nexe confirm - Yes\nexe cancel - No".format(team=team.name, cost=shop['nuke'][1])
        addconf(['nuke', message.author.id, team.id])
    await sendConfMessage(message, text, msgOverride=True, colorOverride=colorOverride)

async def confNUKE(message, action):
    transact(message.author, 'nuke')
    ticketTotal = 0
    for u in getTeamMembers(action[2]):
        await u.add_roles(getHome().get_role(role_elim_id))
        await u.remove_roles(getHome().get_role(action[2]))
        userwrite(u, 'lastTeam', action[2])
        ticketTotal += userread('tickets')
        userwrite(u, 'tickets', 0)
    distributeTickets(ticketTotal, getAllParticipants())
    await message.channel.send(embed=tEmbed("Now we are all sons of bitches.", message.author))
    await updateStatusBoard()

async def confFRIENDLYNUKE(message, action):
    addconf(['nukemyownteamforrealsies', action[1], action[2]])
    finalwarning = "ARE YOU *ABSOLUTELY, 100% SURE* YOU WANT TO DO THIS?\n\nexe confirm - PLEASE\nexe cancel - DO NOT."
    await message.channel.send(embed=tEmbed(finalwarning, message.author, colorOverride=0xffa500))

async def confREALLYFRIENDLYNUKE(message, action):
    transact(message.author, 'nuke')
    ticketTotal = 0
    for u in getTeamMembers(action[2]):
        await u.add_roles(getHome().get_role(role_elim_id))
        await u.remove_roles(getHome().get_role(action[2]))
        userwrite(u, 'lastTeam', action[2])
        ticketTotal += userread('tickets')
        userwrite(u, 'tickets', 0)
    distributeTickets(ticketTotal, getAllParticipants())
    await message.channel.send(embed=tEmbed(monologue, message.author))
    await updateStatusBoard()

# == Eliminate ==
async def cmdELIMINATE(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    name = getTextArg(args, 2)
    u = findUser(name)
    if type(u) == str:
        await message.channel.send(embed=tEmbed(u, message.author))
        return
    if u.id == message.author.id or not u in getAllParticipants():
        await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
        return
    addconf(['eliminate', message.author.id, u.id])
    text = "You have chosen to eliminate {target}.".format(target=u.display_name)
    await sendConfMessage(message, text)

async def confELIMINATE(message, action):
    transact(message.author, 'eliminate')
    u = getHome().get_member(action[2])
    await u.add_roles(getHome().get_role(role_elim_id))
    await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
    distributeTickets(userread(u, 'tickets'), getAllParticipants())
    userwrite(u, 'tickets', 0)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0}.".format(u.display_name), message.author))
    await updateStatusBoard()
            
# == Revive ==
async def cmdREVIVE(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    name = getTextArg(args, 2)
    u = findUser(name)
    if type(u) == str:
        await message.channel.send(embed=tEmbed(u, message.author))
        return
    if u.id == message.author.id or not(u in getAllParticipants(eliminated=True)) or userread(u.id, 'lastTeam') != userread(message.author, 'lastTeam'):
        await message.channel.send(embed=tEmbed("You can't revive that person.", message.author))
        return
    addconf(['revive', message.author.id, u.id])
    text = "You have chosen to revive {target}.".format(target=u.display_name)
    await sendConfMessage(message, text)

async def confREVIVE(message, action):
    transact(message.author, 'revive')
    u = getHome().get_member(action[2])
    await u.add_roles(getHome().get_role(userread(u, 'lastTeam')))
    await u.remove_roles(getHome().get_role(role_elim_id))
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nWelcome back, {0}!".format(u.display_name), message.author))
    await updateStatusBoard()
                
# == Peek ==
async def cmdPEEK(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
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
    text = "You have chosen to peek {target}'s team channel.".format(target=team.name)
    await sendConfMessage(message, text)

async def confPEEK(message, action):
    transact(message.author, 'peek')
    channel = getHome().get_channel(action[2])
    await channel.set_permissions(message.author, read_messages=True, send_messages=False, add_reactions=False)
    peekers = stateread('peekers')
    peekers.append([action[1], action[2]])
    statewrite('peekers', peekers)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have special eyes.", message.author))
    await updateStatusBoard()

# == Timeout ==
async def cmdTIMEOUT(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    name = getTextArg(args, 2)
    u = findUser(name)
    if type(u) == str:
        await message.channel.send(embed=tEmbed(u, message.author))
        return
    if u.id == message.author.id or not u in getAllParticipants():
        await message.channel.send(embed=tEmbed("You can't eliminate that person.", message.author))
        return
    addconf(['timeout', message.author.id, u.id])
    text = "You have chosen to temporarily eliminate {target}.".format(target=u.display_name)
    await sendConfMessage(message, text)

async def confTIMEOUT(message, action):
    transact(message.author, 'timeout')
    u = getHome().get_member(action[2])
    await u.add_roles(getHome().get_role(role_elim_id))
    await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
    timeouts = stateread('timeouts')
    timeouts.append(u.id)
    statewrite('timeouts', timeouts)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou have eliminated {0} for this challenge.".format(u.display_name), message.author))
    await updateStatusBoard()
                
# == Sabotage ==
async def cmdSABOTAGE(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
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
    text = "You have chosen to sabotage {target}.".format(target=team.name)
    await sendConfMessage(message, text)

async def confSABOTAGE(message, action):
    transact(message.author, 'sabotage')
    role = getHome().get_role(action[2])
    statewrite('sabotage', action[2])
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\n{0} can no longer participate in this challenge, and automatically loses.".format(role.name), message.author))
    await updateStatusBoard()
                
# == Bias ==
async def cmdBIAS(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    teamName = getTextArg(args, 2)
    team = findTeam(teamName)
    if type(team) == str:
        await message.channel.send(embed=tEmbed(team, message.author))
        return
    if team.id == userread(message.author, 'lastTeam'):
        await message.channel.send(embed=tEmbed("You cannot request bias against your own team.", message.author))
        return
    addconf(['bias', message.author.id, team.id])
    text = "You have chosen to request insider info on {target} from the host.".format(target=team.name)
    await sendConfMessage(message, text)

async def confBIAS(message, action):
    transact(message.author, 'bias')
    role = getHome().get_role(action[2])
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou are the favorite team. For now.", message.author))
    await client.get_user(host_id).send(str(message.author) + " used Bias and requests info on " + role.name + ".")
    await updateStatusBoard()
                
# == Fraud ==
async def cmdFRAUD(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    team = userread(message.author, 'lastTeam')
    frauds = stateread('frauds')
    if team in frauds:
        await message.channel.send(embed=tEmbed("Your team has already rigged the vote for this challenge.", message.author))
        return
    addconf(['fraud', message.author.id])
    text = "You and your team have chosen to shamelessly engage in election fraud."
    await sendConfMessage(message, text)

async def confFRAUD(message, action):
    transact(message.author, 'fraud')
    frauds = stateread('frauds')
    frauds.append(userread(message.author, 'lastTeam'))
    statewrite('frauds', frauds)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou suddenly feel like your vote matters. Like, a lot.", message.author))
    await updateStatusBoard()
                
# == Escape ==
async def cmdESCAPE(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    active = stateread('challengeActive') or stateread('voteActive')
    escapes = stateread('escape')
    if active:
        await message.channel.send(embed=tEmbed("Escape Rope cannot be used while a challenge or vote is ongoing.", message.author))
        return
    if message.author.id in escapes: # possibly unnecessary
        await message.channel.send(embed=tEmbed("You've already used Escape Rope for this challenge.", message.author))
        return
    addconf(['escape', message.author.id])
    text = "You have chosen to escape from the next challenge. You will be barred from prizes during this time."
    await sendConfMessage(message, text)

async def confESCAPE(message, action):
    transact(message.author, 'escape')
    escape = stateread('escape')
    escape.append(message.author.id)
    statewrite('escape', escape)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou will not be part of the next challenge.", message.author))
    await updateStatusBoard()
                
# == Thief ==
async def cmdTHIEF(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
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
    text = "You have chosen to steal {0} for your own team.".format(u.display_name)
    await sendConfMessage(message, text)

async def confTHIEF(message, action):
    transact(message.author, 'thief')
    u = getHome().get_member(action[2])
    role = getHome().get_role(userread(message.author, 'lastTeam'))
    await u.add_roles(role)
    await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
    userwrite(u, 'lastTeam', role.id)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\n{target} has been abducted by {team}!".format(target=u.display_name, team=role.name), message.author))
    await updateStatusBoard()

# == Swap ==
async def cmdSWAP(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    swap = stateread('swap_requests')
    existing = [i for i in swap if i[0] == message.author.id]
    if stateread('votingActive'):
        await message.channel.send(embed=tEmbed("You can't swap right now.", message.author))
        return
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

# confSWAP does not exist- handled in cmdACCEPT and cmdDENY


async def cmdIMMUNITY(message, args):
    if not message.channel.id in [chan_prizes_id, chan_bots_id]:
        return
    err = checkPurchaseErrors(message.author, args[1].lower())
    if err:
        await message.channel.send(embed=tEmbed(err, message.author))
        return
    immunities = stateread('immunities')
    if message.author.id in immunities:
        await message.channel.send(embed=tEmbed("You are already immune.", message.author))
        return
    addconf(['immunity', message.author.id])
    msg = "You have chosen to give yourself immunity to the next vote."

async def confIMMUNITY(message, action):
    transact(message.author, 'immunity')
    immunities = stateread('immunities')
    immunities.append(message.author.id)
    statewrite('immunities', immunities)
    await message.channel.send(embed=tEmbed("== TRANSACTION SUCCESSFUL ==\n\nYou feel invincible. Whether or not you are is another matter entirely...", message.author))
    await updateStatusBoard()