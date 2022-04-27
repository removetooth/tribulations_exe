# TRIBULATIONS.EXE
# Hastily thrown together in a weekend (& cleaned up later) by riff
# Made to automate aspects of the Tribulations gameshow

# Token goes in token.txt.

# To anyone reading in the future who might be reading
# back to previous commits and wondering why I made the
# choices I did, I never intended to show the code to
# anyone. Mistakes were made, lessons were learned.
# Lessons are still being learned.
# This is more or less just an exercise, after all.

# One of these days I'll learn how to use discord.ext.commands.
# Don't have the time today, though.

import discord, ast, random
from itertools import chain

import cmdlists
from misc import *
from util import *


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    try:
        foo = open('state.txt', 'r')
        foo.close()
    except:
        quickwrite('state.txt', str(statedefault))
    game = discord.Game("exe help")
    await client.change_presence(status=discord.Status.online, activity=game)
    await updateStatusBoard()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(client.user.mention) or \
       message.content.lower().startswith("exe"):
        args = message.content.split(' ')
        args = [i for i in args if not i == '']

        # TODO: TEMPORARY stand-in during cleanup. Get rid of if-else hell soon!
        if args[1] in cmdlists.cmdList:
            await cmdlists.cmdList[args[1]](message, args)


        elif args[1].lower() in ['help', 'commands', '?']:
            helpmsg = helptext
            if message.author.id == host_id:
                helpmsg = helpmsg + helphost
            if message.author.id in op_ids:
                helpmsg = helpmsg + helpop
            try:
                await message.author.send(embed=tEmbed(helpmsg))
            except discord.errors.Forbidden:
                await message.channel.send(embed=tEmbed("I can't seem to send you the command list. Do you have DMs disabled?", message.author))
            #await message.channel.send(embed=tEmbed("Command list sent to DMs.", message.author))
            
        
        elif args[1].lower() in ['shop', 'prizes']:
            shop = stateread('shop')
            shop_text = '\n'.join(['{item} [{cost} tickets - {stock}] - {desc}'.format(
                item=i.upper(),
                stock=(str(shop[i][0])+" in stock") if shop[i][0] >= 0 else "Infinite use",
                cost=shop[i][1],
                desc=shop[i][2]) for i in shop if shop[i][0] != 0])
            shop_msg = '== PRIZE CORNER ==\n\nUse "exe (item)" to select an item for purchase\n\n' + shop_text
            await message.author.send(embed=tEmbed(shop_msg))
            await message.channel.send(embed=tEmbed("Prize Corner listings have been sent to your DMs.", message.author))
            

        elif args[1].lower() in ['balance', 'bal']:
            u = message.author
            name = getTextArg(args, 2)
            if not name == '':
                u = findUser(name)
                if type(u) == str:
                    await message.channel.send(embed=tEmbed(u, message.author))
                    return
            if not u in getAllParticipants():
                msg = '{0} not in the game.'.format("You are" if u == message.author else "That user is")
                await message.channel.send(embed=tEmbed(msg, message.author))
                return
            createDataIfNecessary(u)
            balance = userread(u, 'tickets')
            embed = tEmbed("CURRENT BALANCE: " + str(balance) + " TICKETS", message.author)
            await message.channel.send(embed=embed)

        
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
            if action[0] in cmdlists.confList:
                await cmdlists.confList[action[0]](message, action)
                

        # === HOST/ADMIN COMMANDS ===

        elif args[1].lower() == 'start' and message.author.id == host_id:
            statewrite('challengeActive', True)
            await message.channel.send("Challenge started. Escape Rope can no longer be used.")
                
        
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
                embed.set_footer(text=vote_instructions)
                poll = await channel.send(embed=embed)
                # votes are supposed to be anonymous, so don't do reaction voting.
                #[await poll.add_reaction(str(i+1)+'\N{COMBINING ENCLOSING KEYCAP}') for i in range(len(losingTeamMembers))]
                

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
            for i in tally: # there are probably better ways to do this
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
            extra_comments = "" if not isLoserImmune else "\n<@{0}>'s vote immunity deflects the loss to <@{1}>.\n".format(loser, second)
            await u.add_roles(getHome().get_role(role_elim_id))
            await u.remove_roles(getHome().get_role(userread(u, 'lastTeam')))
            await message.channel.send("The vote has ended.\n"+extra_comments+"\n{0} is no more.\n".format(u.mention), embed=embed)
            distributeTickets(userread(u, 'tickets'), getAllParticipants())
            userwrite(u, 'tickets', 0)
            await updateStatusBoard()
        

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
            await updateStatusBoard()
            await message.channel.send("data created & updated for all participants")


        elif args[1].lower() == 'kill' and message.author.id in op_ids:
            await message.channel.send('stopping')
            await client.close()
            

        elif args[1].lower() == 'tickets':
            if not message.author.id == host_id:
                await message.channel.send(embed=tEmbed("\"tickets\" is only usable by the host to manage tickets.\nIf you're trying to transfer tickets, use \"transfer\" instead:\nexe transfer <(amount)/all> <user, list of users, or team>", message.author))
                return
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
            await updateStatusBoard()
                    

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
            args[3] = args[3].lower()
            if args[3] == 'stock':
                shop[args[2]][0] = int(args[4])
            elif args[3] == 'cost':
                shop[args[2]][1] = int(args[4])
            elif args[3] == 'desc':
                shop[args[2]][2] = getTextArg(args,4)
            elif args[3] == 'raiseby':
                shop[args[2]][3] = int(args[4])
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


        elif args[1].lower() == 'ping' and message.author.id in op_ids:
            # intended to help set up the status board
            dest = getTextArg(args, 2)
            chan = message.channel
            if dest.isdigit() and not dest == '':
                chan = client.get_channel(int(dest))
            await chan.send('pong')


        elif args[1].lower() == 'genstatus' and message.author.id in op_ids:
            await updateStatusBoard()


        elif args[1].lower() == 'status' and message.author.id in op_ids:
            if args[2] == 'message':
                statewrite('statusMessage', int(args[3]))
            elif args[2] == 'channel':
                statewrite('statusChannel', int(args[3]))
            else:
                await message.channel.send('invalid operation')
            await message.channel.send('status ' + args[2].lower() + ' id updated')


        elif args[1].lower() == 'tally' and message.author.id == host_id and stateread('votingActive'):
            tally = {i: 0 for i in stateread('votingOpts')}
            frauds = stateread('frauds')
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
            text_tally = '\n'.join(['<@{user}>: {votes} votes'.format(user=i, votes=tally[i]) for i in tally])
            embed = discord.Embed(title='Current Tally', description = text_tally, color = 0x00ff00)
            await message.author.send(embed=embed)


        elif args[1].lower() == 'vote' \
           and message.channel.type == 'private' \
           and stateread('votingActive') \
           and message.author in getAllParticipants() \
           and int(args[2]) <= len(stateread("votingOpts")):
            index = int(args[2])-1
            vote = userread(message.author, 'vote')
            opts = stateread('votingOpts')
            target = getHome().get_member(opts[index])
            feedback = ('You have changed your vote to {0}.' if vote else 'You have voted for {0}.').format(target.display_name)
            userwrite(message.author, 'vote', opts[index])
            await message.author.send(feedback)

            
                    
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return
    
    # votes are supposed to be anonymous, so no reaction voting for now.
    if False and \
        reaction.message.author == client.user and \
       len(reaction.message.embeds) == 1 and \
       stateread('votingActive') and \
       reaction.message.embeds[0].footer.text == vote_instructions \
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
        

client.run(quickread('token.txt'))
    
