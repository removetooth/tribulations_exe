import discord

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

userdefault = {
    'tickets': 0,
    'lastTeam': None,
    'vote': None
    }
statedefault = {
    'shop': {
        'nuke': [1, 1100, 'Nuclear Bomb. Eliminate an entire team.', 0],
        'eliminate': [3, 520, 'Member Elimination. Eliminate another member of your choosing.', 0],
        'revive': [3, 420, 'Team Member Revival. Revive a fallen team member.', 0],
        'immunity': [3, 220, 'Immunity. Survive a round of elimination voting and have it passed onto 2nd-to-last place.', 0],
        'sabotage': [1, 200, 'Sabotage. Disallow a team from competing in any challenge of your choice, netting them an automatic last place.', 0],
        'fraud': [3, 150, "Voter Fraud. Buy the ability to have your team's votes doubled when voting to eliminate.", 0],
        'thief': [-1, 130, 'Thief. In the event of the host announcing an auto-balance, you can "buy" any player of your choice, as long as your team has below 4 members', 0],
        'escape': [4, 120, 'Escape Rope. Exempt yourself from one challenge and be barred from elimination and prizes. Cannot be used past the start time of the challenge.', 0],
        'timeout': [4, 90, 'For one challenge, you can choose to have a member from another team be eliminated.', 0],
        'peek': [3, 65, "Team Peek. Allow a teammate to see inside another team's channel for one challenge.", 0],
        'bias': [5, 40, 'Host bias. I will explain to you with a tinge of vagueness about the current actions of any team of your choice.', 0],
        'transfer': [-1, 0, 'Ticket Transfer. Transfer an allotted amount of tickets to another player with no extra cost.', 0],
        'swap': [-1, 0, 'Swap. As long as the two players consent, you can swap teams with no extra charge. Not usable during the process of voting for elimination.', 0]},
    'swap_requests': [],
    'use_confirmations': [],
    'frauds': [],
    'peekers': [],
    'timeouts': [],
    'immunities': [],
    'escape': [],
    'sabotage': None,
    'challengeActive': False,
    'autobalance': False,
    'votingActive': False,
    'votingOpts': [],
    'lastVote': None,
    'bannedItems': [],
    'statusChannel': 0,
    'statusMessage': 0
    }

team_ids = [
    959682463175696414, # Paypal Mafia
    960150245226995772, # Outcasts
    960177784641191987, # Starving Artists
    960260637106257920, # Raging Crack Addicts
    960996087244668948, # Femboy Association
    960381460240547860  # Sceptile Fans :D
    ]
team_chan_ids = {
    team_ids[0]: 959682914944188467, # Paypal Mafia
    team_ids[1]: 960150552275197992, # Outcasts
    team_ids[2]: 960178086131949592, # Starving Artists
    team_ids[3]: 960265304443863120, # Raging Crack Addicts
    team_ids[4]: 960996278572040212, # Femboy Association
    team_ids[5]: 961005507408171019  # Sceptile Fans :D
    }
role_elim_id = 961755681432666202 # ID of Eliminated role
chan_prizes_id = 953328018506534965 # ID of Prize Booth channel
chan_bots_id = 953163427101167647 # ID of bots channel (currently unused)
op_ids = [266389941423046657, 221992874886037504] # IDs of people who can use admin commands
tribulations_id = 951647646102200320 # ID of the Tribulations server
host_id = 221992874886037504 # ID of the host

prizes = list(statedefault['shop'])

helptext = """Use "exe (keyword)" to use a command.

help/commands/? - Show this dialog.
balance/bal [user] - Check your (or another user's) ticket balance.
shop/prizes - Check the Prize Booth.
vote <number> - Cast a vote. This can be used in DMs.

== Prize Booth commands ==
All of these commands can only be used in the prize booth and bot channels.
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
transfer <(amount)/all> <user, list of users, or team> - Transfer tickets to another user."""

helpop = """

== Admin commands ==
kill - Stop the bot.
refresh - Create user data that might not exist, and update user data that does. Recommended to use after manually assigning a team role.
setlastteam <user> <team> - Set the last team an eliminated member was on. Used for revivals.
ping [channel id] - Ping. Optionally respond in channel with given ID. Half-intended to help set up the status board.
status <message/channel> <id> - Set the IDs for the status board message and channel.
genstatus - Edit the status board with updated information."""

helphost = """

== Host commands ==
tickets <give/remove/set> <amount> <user or team> - Manage currency.
start - Mark the start of a challenge. Disables Escape Rope.
callvote <team> - Call a vote against a team. Ends the active challenge.
endvote - End the voting period. Eliminates the loser.
autobalance - Toggle the autobalance period on and off. Enables/disables Thief.
changeprize <item> <stock/cost/raiseby/desc> <value> - Edit prizes. -1 stock is infinite use.
toggleitem <item> - Toggle the ability to purchase a prize.
tally - Check the current vote tally."""

monologue = "You goddamn madman."
# i thought a copypasta would be funny but i think this comes off as too serious so it's unused for now
"""... Fine.

Congratulations. You've used the one nuke of the game on your own team. Was it worth it?

Did you think this through? Did you communicate with your team?

Or did you sit back as the people who trusted you with eleven hundred tickets begged you not to push the button, heartlessly reveling in their terror?

What did you hope to gain from this? Freedom? Sweet release for you and your comrades?
Or was it a sick, twisted sense of joy?
Did you think it would be funny to remove your entire team from the game, only to turn around and tell them it's a joke?

Either way, you're at the mercy of your former teammates now.

I can only pray that you made the right decision."""

vote_instructions = "Vote in DMs using exe vote (number)."#"Vote using the reactions below, or with exe vote (number), if those don't work. exe vote can also be used in DMs."
