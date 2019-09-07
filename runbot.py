import sys
import os
import json
import traceback
import discord
import ast
from discord.ext import commands

with open("languages.json", "r") as languages_file:
    lang = json.loads(languages_file.read())
    languages_file.close()

name = open('runbot.txt').read()

os.chdir(os.getcwd() + f"/{name}")

with open("config.json", "r") as config_file:
    config = json.loads(config_file.read())
    config_file.close()

with open("cmdsinfo.json", "r") as cmdsinfo_file:
    cmdsinfo = json.loads(cmdsinfo_file.read())
    cmdsinfo_file.close()
    
prefix = config["prefix"]

bot = commands.Bot(command_prefix=prefix, description='Description')

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

async def execfunc(bot, message, cmd):
	fn_name = "_eval_expr"
	cmd = cmd.strip("` ")
	cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
	body = f"async def {fn_name}():\n{cmd}"
	parsed = ast.parse(body)
	body = parsed.body[0].body
	insert_returns(body)
	env = {
		'bot': bot,
		'message': message,
		'discord': discord,
		'commands': commands,
		'__import__': __import__
	}
	exec(compile(parsed, filename="<ast>", mode="exec"), env)
	result = (await eval(f"{fn_name}()", env))

@bot.event
async def on_ready():
    print(f'{lang[config["language"]]["loggedmsg"]} {bot.user.name} - {bot.user.id}')

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	if not message.content.startswith(prefix):
		return
	if " " in message.content:
		cmd = message.content.split(" ")
	else:
		cmd = [message.content, ""]
	cmd[0] = cmd[0][1:]
	with open("cmdsinfo.json", "r") as cmdsinfo_file:
		cmdsinfo = json.loads(cmdsinfo_file.read())
		cmdsinfo_file.close()
	try:
		cmdscriptjson = cmdsinfo[cmd[0]]
		cmdscriptjson = cmdscriptjson.split("\n")
		cmdscript = ""
		for line in cmdscriptjson:
			if line.lower().startswith(".send"):
				cmdscript = cmdscript + f"""\nchannel = message.channel
botmsg = await channel.send('{line[6:]}')"""
			elif line.lower().startswith('.createchannel:'):
				toscript = line[15:]
				if ", " in toscript:
					toscript = toscript.split(', ')
				elif "," in toscript:
					toscript = toscript.split(',')
				else:
					return
				cmdscript = cmdscript + f"\nawait message.guild.create_{toscript[0]}_channel('{toscript[1]}')"
			elif line.lower().startswith('.script:'):
				cmdscript = cmdscript + f"\n{line[8:]}"
			elif line.lower().startswith('.deletemessage:'):
				msgtodel = line[15:]
				if msgtodel == "usermsg":
					scr = "await message.delete()"
				elif msgtodel == "botmsg":
					scr = "await botmsg.delete()"
				else:
					scr = f"await message.channel.get_message({msgtodel}).delete()"
				cmdscript = cmdscript + f"\n{scr}"
			elif line.lower().startswith('.log:'):
				cmdscript = cmdscript + f"\nprint('{line[5:]}')"
				cmdscript = cmdscript + f"\nopen('log.txt', 'a').write('''\n{line[5:]}''')"
			else:
				cmdscript = cmdscript + f"\n#{line}"
		await execfunc(bot, message, cmdscript)
	except KeyError:
		nothing = 1
	if message.content.lower().startswith(prefix + "pdbc addcmd ") and message.author.id == int(config["ownerid"]):
		newcmd = message.content[len(prefix) + 12:].split("""
""")
		cmdname = newcmd[0]
		newcmd.pop(0)
		newcmd = "\n".join(newcmd)
		with open("cmdsinfo.json", "w") as cmdsinfo_file:
			cmdsinfo[cmdname] = newcmd
			json.dump(cmdsinfo, cmdsinfo_file)
			cmdsinfo_file.close()
		await message.channel.send(f"Dodano komende `{cmdname}` :ok_hand:")


bot.run(config['token'], bot=True, reconnect=True)
