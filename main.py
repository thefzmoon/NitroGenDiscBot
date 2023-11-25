import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.tasks import loop
# Un comment the line below if you would like to use this on repl.it 24/7
# from keep_alive import keep_alive
import colour
import os
import random
import string
import json

# Un comment the line below if you would like to use this on repl.it 24/7
# keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=';', intents=intents)

admin_role_id = Admin_role_id_here # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

custom_commands = {}


def is_admin(ctx):
    return discord.utils.get(ctx.author.roles, id=admin_role_id) is not None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='cmds')
async def commands_command(ctx):
    await ctx.send("My available commands are:\n"
                  ";avatar | Displays the avatar of the mentioned user or your own.\n"
                  ";gennitro | Generates UNCHECKED Nitro codes.\n")



@bot.command(name='staffcmds')
@commands.check(is_admin)
async def staffcommands_command(ctx):
    await ctx.send("My available administrative commands are:\n"
                  ";addcmd | Adds a custom command.\n"
                  ";editcmd | Edits a custom command.\n"
                  ";delcmd | Deletes a custom command.\n"
                  ";lock | Locks the channel you are in.\n"
                  ";unlock | Unlocks the channel you are in.\n"
                  ";echo | Echos the message you send.\n"
                  ";kick | Kicks a user from the discord\n"
                  ";ban | Bans a user from the discord\n"
                  ";unban | Unbans a user from the discord\n"
                  ";clear | Clears a specified amount of messages\n"
                  ";clearall | Clears all messages and recreates the channel\n")

@bot.command(name='customcmds')
@commands.check(is_admin)
async def list_custom_commands(ctx):
    if custom_commands:
        commands_list = "\n".join(f"{cmd}" for cmd in custom_commands)
        await ctx.send(f"Custom Commands:\n{commands_list}")
    else:
        await ctx.send("No custom commands available.")


try:
  with open('custom_commands.json', 'r') as file:
      custom_commands = json.load(file)
except FileNotFoundError:
  pass  

def save_commands():
  with open('custom_commands.json', 'w') as file:
      json.dump(custom_commands, file, indent=4)

@bot.command(name='addcmd')
@commands.check(is_admin)
async def add_command(ctx, cmd_name: str, *, cmd_text: str):
    custom_commands[cmd_name] = cmd_text
    save_commands()  
    await ctx.send(f"Command '{cmd_name}' added successfully!")

    async def dynamic_command(ctx, *args):
        await ctx.send(custom_commands.get(cmd_name, f"Command '{cmd_name}' not found."))

    bot.add_command(commands.Command(dynamic_command, name=cmd_name))

@bot.command(name='delcmd')
@commands.check(is_admin)
async def delete_command(ctx, cmd_name: str):
    if cmd_name in custom_commands:
        del custom_commands[cmd_name]
        bot.remove_command(cmd_name)  
        save_commands()  
        await ctx.send(f"Command '{cmd_name}' deleted successfully!")
    else:
        await ctx.send(f"Command '{cmd_name}' not found.")

@bot.command(name='editcmd')
@commands.check(is_admin)
async def edit_command(ctx, cmd_name: str, *, new_text: str):
    if cmd_name in custom_commands:
        custom_commands[cmd_name] = new_text
        save_commands()  
        await ctx.send(f"Command '{cmd_name}' edited successfully!")
    else:
        await ctx.send(f"Command '{cmd_name}' not found.")

@bot.command(name='lock')
@commands.check(is_admin)
async def lock_command(ctx):
    channel = ctx.channel
    staff_role = discord.utils.get(ctx.guild.roles, id=admin_role_id)

    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    if staff_role:
        await channel.set_permissions(staff_role, send_messages=True)

    await ctx.send(f"{channel.name} Locked 🔒")

@bot.command(name='unlock')
@commands.check(is_admin)
async def unlock_command(ctx):
    channel = ctx.channel

    await channel.set_permissions(ctx.guild.default_role, send_messages=None)

    await ctx.send(f"{channel.name} Unlocked 🔓")

@bot.command(name='echo')
@commands.check(is_admin)
async def echo_command(ctx, *, args):
    parts = args.split(' ', 1)
    if len(parts) >= 2 and parts[0].startswith('<#') and parts[0].endswith('>'):
        channel_id = int(parts[0][2:-1])
        target_channel = bot.get_channel(channel_id)
        if target_channel and isinstance(target_channel, discord.TextChannel):
            await target_channel.send(parts[1])
        else:
            await ctx.send(f"Invalid channel ID: {channel_id}")
    else:
        await ctx.send(args)

@bot.command(name='kick')
@commands.check(is_admin)
async def kick_command(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"{member.display_name} has been kicked.")

@bot.command(name='ban')
@commands.check(is_admin)
async def ban_command(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"{member.display_name} has been banned.")

@bot.command(name='unban')
@commands.check(is_admin)
async def unban_command(ctx, member_id: int):
    banned_users = await ctx.guild.bans()
    member_to_unban = discord.utils.get(banned_users, user_id=member_id)
    await ctx.guild.unban(member_to_unban.user)
    await ctx.send(f"{member_to_unban.user.name} has been unbanned.")

@bot.command(name='clear')
@commands.check(is_admin)
async def clear_command(ctx, amount: int):
    def is_pinned(m):
        return not m.pinned

    await ctx.message.delete()

    messages = await ctx.channel.purge(limit=amount, check=is_pinned)

    clrmsg = await ctx.send(f"Cleared {len(messages)} messages.")

    await asyncio.sleep(3)
    await clrmsg.delete()

@bot.command(name='clearall')
@commands.check(is_admin)
async def clearall_command(ctx):
    message = await ctx.send("Are you sure you want to clear all messages and recreate the channel? ✅❌")

    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Command timed out. Please run the command again.")
        return

    if str(reaction.emoji) == '❌':
        await ctx.send("Command terminated.")
    elif str(reaction.emoji) == '✅':
        channel_name = ctx.channel.name
        channel_position = ctx.channel.position
        channel_category = ctx.channel.category
        channel_overwrites = ctx.channel.overwrites

        await ctx.channel.delete()

        new_channel = await ctx.guild.create_text_channel(
            name=channel_name,
            category=channel_category,
        )
        await new_channel.edit(position=channel_position, overwrites=channel_overwrites)

        confirmation_message = await new_channel.send("Channel cleared and recreated.")

        await asyncio.sleep(5)
        await confirmation_message.delete()

@bot.command(name='avatar')
async def avatar_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    avatar_url = member.avatar.url
    await ctx.send(f"{avatar_url}")

@bot.command(name='gennitro')
# HERE 
async def generate_nitro_code(ctx, num: int = 1):
    if num < 1:
        await ctx.send("Please provide a valid positive number.")
        return

    if num > 25:
        nitro_codes = [generate_code() for _ in range(num)]
        file_content = "\n".join(nitro_codes)

        with open('nitro_codes.txt', 'w') as file:
            file.write(file_content)

        await ctx.send("Nitro codes generated. Here is the file:", file=discord.File('nitro_codes.txt'))
    else:
        nitro_codes = [generate_code() for _ in range(num)]
        formatted_codes = "\n".join(nitro_codes)
        await ctx.send(formatted_codes)

def generate_code():
    return f"https://discord.gift/{''.join(random.choices(string.ascii_letters + string.digits, k=16))}"

bot.run("Insert_Token_here")
