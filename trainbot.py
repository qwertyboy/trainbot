import discord
import asyncio
from cmds import incrementStats, editPlayer, dumpStats
from config import Config
from db import createDB
from cmdparser import ParseMessage
from help import Help


# initialize help messages
help = Help()
# create a client
client = discord.Client()
# get the config information
config = Config()
for group in config.groups:
    print(group.name)
    print('\t' + str(group.cmds))
    print('\t' + str(group.roles))
    print('\t' + str(group.users))


@client.event
async def on_ready():
    print('Logged in as \"%s\" with ID %s' % (client.user.name, client.user.id))
    print('Connected servers:')
    for server in client.servers:
        print('\t%s (%s)' % (server.name, server.id))

        #print('\tRoles:')
        #for role in server.role_hierarchy:
        #    print('\t\t%s (%s)' % (role.name, role.id))

        #print('\tMembers:')
        #for member in server.members:
        #    print('\t\t%s (%s)' % (member.name, member.id))
    print('---------------------------------------------')

@client.event
async def on_message(message):
    # check if we should process messages for this channel
    msgChannel = message.channel.id
    if msgChannel == config.listenID or config.listenID == 'NONE':
        # check if this is a command for this bot
        if message.content.startswith(config.cmdPrefix):
            # send a typing message because why not
            await client.send_typing(message.channel)
            # parse the command
            cmd = ParseMessage(message)
            gameFileName = cmd.game + '_' + config.statsFileName

            print('\n[INFO] Command: %s' % cmd.command)
            print('[INFO] Arguments: %s' % cmd.args)

            # get invoking member
            msgAuthor = message.author
            # check permission for command
            permission = config.checkPermission(msgAuthor, cmd.command)

            if permission:
                # main command for adding win and lose information
                # syntax: !updategame game='game' winner='winner' losers='losers'
                if cmd.command == 'UPDATESTATS':
                    # make sure the required arguments were provided
                    if cmd.game == 'NONE' or cmd.winner == 'NONE' or cmd.losers == 'NONE':
                        # error message if game not specified
                        if cmd.game == 'NONE':
                            print('[ERROR] No game specified')
                            await client.send_message(message.channel, 'Error: No game specified.')
                        # error message if winner not specified
                        if cmd.winner == 'NONE':
                            print('[ERROR] No winner specified')
                            await client.send_message(message.channel, 'Error: No winner specified.')
                        #error message if losers not specified
                        if cmd.losers == 'NONE':
                            print('[ERROR] No losers specified')
                            await client.send_message(message.channel, 'Error: No losers specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)
                        print('[INFO] Winner: %s' % cmd.winner)
                        print('[INFO] Losers: %s' % cmd.losers)

                        # try updating the stats
                        status = incrementStats(message.channel, gameFileName, cmd.winner, cmd.losers)
                        await client.send_message(message.channel, status)
                        await client.send_message(message.channel, '<:trains:324019973607653378>')

                # command for adding a player to a database
                # syntax: !addplayer game='game' name='name'
                elif cmd.command == 'ADDPLAYER':
                    # make sure the required arguments were provided
                    if cmd.game == 'NONE' or cmd.name == 'NONE':
                        # error message if game not specified
                        if cmd.game == 'NONE':
                            print('[ERROR] No game specified')
                            await client.send_message(message.channel, 'Error: No game specified.')
                        # error message if player not specified
                        if cmd.name == 'NONE':
                            print('[ERROR] No player specified')
                            await client.send_message(message.channel, 'Error: No player specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)
                        print('[INFO] Player: %s' % cmd.name)

                        # add the player
                        status = editPlayer(message.channel, gameFileName, cmd.name, editType='ADD')
                        await client.send_message(message.channel, status)

                # command for removing a player from a database
                # syntax: !removeplayer game='game' name='name'
                elif cmd.command == 'REMOVEPLAYER':
                    # make sure the required arguments were provided
                    if cmd.game == 'NONE' or cmd.name == 'NONE':
                        # error message if game not specified
                        if cmd.game == 'NONE':
                            print('[ERROR] No game specified')
                            await client.send_message(message.channel, 'Error: No game specified.')
                        # error message if player not specified
                        if cmd.name == 'NONE':
                            print('[ERROR] No player specified')
                            await client.send_message(message.channel, 'Error: No player specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)
                        print('[INFO] Player: %s' % cmd.name)

                        # remove the player
                        status = editPlayer(message.channel, gameFileName, cmd.name, editType='REMOVE')
                        await client.send_message(message.channel, status)

                # command for setting a players win and loss stats
                # syntax: !setplayer game='game' name='name' wins='wins' losses='losses'
                elif cmd.command == 'SETPLAYER':
                    # make sure the required arguments were provided
                    if cmd.game == 'NONE' or cmd.name == 'NONE' or cmd.wins == 'NONE' or cmd.losses == 'NONE':
                        # error message if game not specified
                        if cmd.game == 'NONE':
                            print('[ERROR] No game specified')
                            await client.send_message(message.channel, 'Error: No game specified.')
                        # error message if player not specified
                        if cmd.name == 'NONE':
                            print('[ERROR] No player specified')
                            await client.send_message(message.channel, 'Error: No player specified.')
                        # error message if wins not specified
                        if cmd.wins == 'NONE':
                            print('[ERROR] No wins specified')
                            await client.send_message(message.channel, 'Error: No wins specified.')
                        # error message if losses not specified
                        if cmd.losses == 'NONE':
                            print('[ERROR] No losses specified')
                            await client.send_message(message.channel, 'Error: No losses specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)
                        print('[INFO] Player: %s' % cmd.name)

                        # update the players stats
                        status = editPlayer(message.channel, gameFileName, cmd.name, editType='EDIT', wins=cmd.wins, losses=cmd.losses)
                        await client.send_message(message.channel, status)

                # command for displaying game stats
                # syntax: !stats game='game' (optional) sort='sort'
                elif cmd.command == 'STATS':
                    # make sure the required arguments were provided
                    if cmd.game == 'NONE':
                        # error message if game not specified
                        if cmd.game == 'NONE':
                            print('[ERROR] No game specified')
                            await client.send_message(message.channel, 'Error: No game specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)
                        print('[INFO] Sorting Type: %s' % cmd.sort)

                        statsMsg = dumpStats(message.channel, gameFileName, sortType=cmd.sort)
                        await client.send_message(message.channel, statsMsg)

                elif cmd.command == 'GAMEHELP':
                    if cmd.nonKeyed == 'NONE':
                        # return default help message
                        helpMsg = help.helpMessage('LIST')
                    else:
                        # return a help message for the specified command
                        helpMsg = help.helpMessage(cmd.nonKeyed)
                    # send message
                    await client.send_message(message.channel, helpMsg)

                # command for creating a new game database
                # syntax: !addgame game
                elif cmd.command == 'ADDGAME':
                    # make sure the required arguments were provided
                    if cmd.nonKeyed == 'NONE':
                        print('[ERROR] No game specified')
                        await client.send_message(message.channel, 'Error: No game specified.')
                    else:
                        # print some info to terminal
                        print('[INFO] Game: %s' % cmd.game)

                        gameFileName = cmd.nonKeyed + '_' + config.statsFileName
                        if createDB(gameFileName):
                            print('[INFO] New database created')
                            await client.send_message(message.channel, 'New database created!')
                        else:
                            await client.send_message(message.channel, 'Error: Problem creating database')

            # failed permission check or game check
            else:
                if not permission:
                    print('[ERROR] %s does not have permission to use this command' % msgAuthor.name)
                    await client.send_message(message.channel, 'Error: You do not have permission to use that command')

client.run(config.botToken)
# https://discordapp.com/oauth2/authorize?client_id=bot_id&scope=bot&permissions=0
