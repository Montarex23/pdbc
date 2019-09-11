import sys
import os
import json
import traceback
import discord
from discord import Embed
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
	print(cmd)
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
		'Embed': Embed,
		'commands': commands,
		'__import__': __import__
	}
	exec(compile(parsed, filename="<ast>", mode="exec"), env)
	result = (await eval(f"{fn_name}()", env))

@bot.event
async def on_ready():
    print(f'{lang[lang["lang"]]["loggedmsg"]} {bot.user.name} - {bot.user.id}')

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
		cmdscript = cmdscript + f"""\nargs = {message.content.split(' ')}"""
		cmdscript = cmdscript + f"\nmsgchannel = message.channel"
		for line in cmdscriptjson:
			if line.lower().startswith(".send:"):
				if line[6:].startswith('%') and line[6:].endswith('%'):
					cmdscript = cmdscript + f"\nbotmsg = await msgchannel.send({line[6:][1:len(line[6:]) - 1]})"
				else:
					cmdscript = cmdscript + f"\nbotmsg = await msgchannel.send('{line[6:]}')"
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
			elif line.lower().startswith('.args:'):
				argsline = []
				if " = " in line[6:]:
					argsline = line[6:].split(" = ")
				elif "= " in line[6:]:
					argsline = line[6:].split("= ")
				elif " =" in line[6:]:
					argsline = line[6:].split(" =")
				elif "=" in line[6:]:
					argsline = line[6:].split("=")
				else:
					nothing = 1
				if not argsline == []:
					if argsline[1].endswith('-'):
						number = f"{argsline[1].strip('-')}:len(args)"
					else:
						number = int(argsline[1])
					name = argsline[0]
					cmdscript = cmdscript + f"""\n{name} = args[{str(number)}]
if type({name}) == list:
	{name} = ' '.join({name})"""
			elif line.lower().startswith('.setchannel:'):
				if line[12:].strip(' ').lower() == "cmd":
					msgchannel = "message.channel"
				elif line[12:].startswith('%') and line[12:].endswith('%'):
					msgchannel = f"bot.get_channel(int({line[12:][1:len(line[12:]) - 1]}))"
				else:
					msgchannel = f"bot.get_channel(int({line[12:][1:len(line[12:]) - 1]}))"
				cmdscript = cmdscript + f"\nmsgchannel = {msgchannel}"
			elif line.lower().startswith('.clearmentions:'):
				if line[15:].startswith('%') and line[15:].endswith('%'):
					cmdscript = cmdscript + f"\n{line[15:][1:len(line[15:]) - 1]} = discord.utils.escape_mentions({line[15:][1:len(line[15:]) - 1]})"
			elif line.lower().startswith('.embed:'):
				cmdscript = cmdscript + f"\nembed = Embed(title='{line[7:]}')"
			elif line.lower().startswith('.embedfield:'):
				cmdscript = cmdscript + f"\nembed.add_field(name='{line[12:].split(',,,')[0]}', value='{line[12:].split(',,,')[1]}', inline=False)"
			elif line.lower().startswith('.embedfooter:'):
				cmdscript = cmdscript + f"\nembed.set_footer(text='{line[13:]}')"
			elif line.lower().startswith('.sendembed'):
				cmdscript = cmdscript + f"\nawait msgchannel.send(embed=embed)"
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
