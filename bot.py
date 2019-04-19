import os
import discord
from maze import Maze

token = os.environ['token']
client = discord.Client()

maze_dict = {}

def as_code(text):
    return f'```{text}```'
    
@client.event
async def on_ready():
    print(f'logged on as {client.user}')
    
@client.event
async def on_message(msg):
    global maze_dict
    
    if not msg.content.startswith('🗺!'):
        return 
    
    print(msg.content)
    maze = Maze(13)
    msg = await msg.channel.send(as_code(maze.get_aisle_aa())+f'\n{maze.current_coord} / [10, 10]')
    maze_dict[msg.id] = maze
    for e in ('◀', '⬆', '▶', '⏫', '🗺'):
        await msg.add_reaction(e)
    
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user or not maze_dict.get(reaction.message.id) or reaction.emoji not in ('◀', '⬆', '▶', '⏫', '🗺'):
        print(reaction, user)
        print(user == client.user,not maze_dict.get(reaction.message.id),reaction.emoji not in ('◀', '⬆', '▶', '⏫', '🗺'))
        return 
    emoji = reaction.emoji
    maze = maze_dict[reaction.message.id]
    client.loop.create_task(reaction.remove(user))
    if emoji == '🗺':
        await reaction.message.channel.send(as_code(maze.get_map()))
    
    if emoji == '◀':
        maze.turn_l()
    elif emoji == '▶':
        maze.turn_r()
    elif emoji == '⬆':
        maze.move_forward()
    elif emoji == '⏫':
        maze.move_forward(maze.size)
    else:
        print(emoji)
    
    await reaction.message.edit(content = as_code(maze.get_aisle_aa())+f'\n{maze.current_coord} / [10, 10]')
    
client.run(token)
