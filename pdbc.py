import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import json
import subprocess
import os

if "PBot" not in os.listdir(os.getcwd()):
    os.makedirs("PBot")
    wd = os.getcwd() + "/PBot"
    os.chdir(wd)
    os.makedirs("Cogs")
    variables_file = open("variables.json", "w")
    variables_file.write("{}")
    variables_file.close()
    config_file = open("config.json", "w")
    config_file.write('{"language":"en"}')
    config_file.close()
    cmdsinfo_file = open("cmdsinfo.json", "w")
    cmdsinfo_file.write('{}')
    cmdsinfo_file.close()
    languages_file = open("languages.json", "w")
    languages_file.write('''{
    "en": {
        "editbot":"Edit Bot",
        "options":"Options",
        "warning":"Warning!",
        "msgboxlang":"You must restart the app"
    },
    "pl": {
        "editbot":"Edytuj Bota",
        "options":"Ustawienia",
        "warning":"Uwaga!",
        "msgboxlang":"Musisz uruchomić ponownie aplikację"
    }
}''')
    languages_file.close()
else:
    os.chdir(os.getcwd() + "/PBot")
with open("config.json", "r") as config_file:
    config = json.load(config_file)
    lg = config["language"]
with open("languages.json", "r+") as languages_file:
    lang = json.load(languages_file)
with open("cmdsinfo.json", "r+") as cmdsinfo_file:
    cmdsinfo = json.load(cmdsinfo_file)
    
LARGE_FONT= ("Verdana", 12)

def editjson(file, key, value):
    with open(file + ".json", "r+") as openedfile:
        data = json.loads(openedfile.read())
        data[key] = value
        openedfile.seek(0)
        json.dump(data, openedfile)
        openedfile.close()
    if key == "language":
         messagebox.showwarning(lang[value]["warning"], lang[value]["msgboxlang"])

         
class Main(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, BotEditor, OptionsPage, CommandEditor):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
        menubar = frame.menubar()
        self.configure(menu=menubar)

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        controller.title("Python Discord Bot Creator")
        controller.geometry("700x500")
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack()

        button = tk.Button(self, text=lang[lg]["editbot"], command=lambda: controller.show_frame(BotEditor))
        button.pack()

        button2 = tk.Button(self, text=lang[lg]["options"], command=lambda: controller.show_frame(OptionsPage))
        button2.pack()

    def menubar(self):
        self.menu = tk.Menu(self) 
        cascade = tk.Menu(self.menu)
        self.menu.add_cascade(label="Program", menu = cascade)        
        cascade.add_command(label = "opcja 1", command=lambda: print("xD"))
        cascade.add_command(label = "opcja 2", command=lambda: print("xD"))       
        cascade2 = tk.Menu(cascade, tearoff = 0)
        cascade.add_cascade(label = "Podmenu", menu = cascade2)       
        cascade2.add_radiobutton(label = "opcja 1", command=lambda: print("xD"))
        cascade2.add_radiobutton(label = "opcja 2", command=lambda: print("xD"))
        cascade2.add_separator()
        cascade2.add_checkbutton(label = "opcja 3", command=lambda: print("xD"))
        return self.menu


class BotEditor(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Bot", font=LARGE_FONT).grid(row=0)

        cwd = os.getcwd()
        os.chdir(cwd + "/Cogs")
        i = 0
        for file in os.listdir(os.getcwd()):
            if str(file).endswith('.py'):
                i = i + 1
        os.chdir(cwd)
        
        label1 = tk.Label(self, text=f"Komendy: {i}").grid(row=1)

        label2 = tk.Label(self, text="Token: ").grid(row=2, column=0)
        entry = tk.Entry(self, show="*", width=50).grid(row=2, column=1)

        button1 = tk.Button(self, text="Run bot", command=lambda: os.system(f"{os.getcwd()}PBot/main.py")).grid(row=3)

        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage)).grid(row=4)

        button2 = tk.Button(self, text="Nowa Komenda", command=lambda: controller.show_frame(CommandEditor)).grid(row=5)

    def menubar(self):
        self.menu = tk.Menu(self) 
        cmdsmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Komendy", menu = cmdsmenu)
        cwd = os.getcwd()
        for cmd in os.listdir(cwd + "/Cogs"):
            if str(cmd).endswith(".py"):
                cmdsmenu.add_command(label = str(cmd).split('.')[0], command=lambda: print("xD"))
        os.chdir(cwd)
        cmdsmenu.add_separator()
        cmdsmenu.add_command(label = "Nowa komenda", command=lambda: Main.show_frame(self, CommandEditor))       
        return self.menu



class OptionsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=lang[lg]["options"], font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()

        rb_var = tk.StringVar()
        rb_female = tk.Radiobutton(self, variable = rb_var, value = "en", text = "English", command=lambda: editjson("config", "language", "en"))
        rb_male = tk.Radiobutton(self, variable = rb_var, value = "pl", text = "Polski", command=lambda: editjson("config", "language", "pl"))
        rb_var.set(config["language"])
        
        rb_female.pack()
        rb_male.pack()

    def menubar(self):
        self.menu = tk.Menu(self) 
        cascade = tk.Menu(self.menu)
        self.menu.add_cascade(label="Program", menu = cascade)        
        cascade.add_command(label = "opcja 1", command=lambda: print("xD"))
        cascade.add_command(label = "opcja 2", command=lambda: print("xD"))       
        cascade2 = tk.Menu(cascade, tearoff = 0)
        cascade.add_cascade(label = "Podmenu", menu = cascade2)       
        cascade2.add_radiobutton(label = "opcja 1", command=lambda: print("xD"))
        cascade2.add_radiobutton(label = "opcja 2", command=lambda: print("xD"))
        cascade2.add_separator()
        cascade2.add_checkbutton(label = "opcja 3", command=lambda: print("xD"))
        return self.menu


class CommandEditor(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label0 = tk.Label(self, text="Command Editor", font=LARGE_FONT).grid(row=0, column=1)
        label = tk.Label(self, text="Nazwa komendy:").grid(row=1, column=0)
        cmdname = tk.Entry(self, width=40)
        cmdname.grid(row=2, column=0)

        label = tk.Label(self, text="Output komendy:").grid(row=3, column=0)
        textbox = tk.Text(self, width = 80, height = 30)
        textbox.grid(row=4, column=0)
        
        label2 = tk.Label(self, text="* - Opcjonalne\nAkcje:").grid(row=1, column=2)
        self.treeview = ttk.Treeview(self)

        send = ["Wysyła wiadomośc", "tekst - Tekst wiadomości"]
        self.add_values(send, ".send:tekst")
        createChannel = ["Tworzy kanał", "typ - voice/text", "nazwa - nazwa kanału"]
        self.add_values(createChannel, ".createChannel:typ, nazwa")
        script = ["! DLA ZAAWANSOWANYCH !", "Dodaje linijke do kodu komendy","linijka - linijka do dodania do kodu"]
        self.add_values(script, ".script:linijka")

        
        self.sb_treeview = tk.Scrollbar(self)
        self.treeview.config(yscrollcommand = self.sb_treeview.set)
        self.sb_treeview.config(command = self.treeview.yview)
        self.sb_treeview.place(in_ = self.treeview, relx = 1., y = 0, relheight = 1.)
        self.treeview.grid(row=2, column=2, rowspan=3)

        ok = tk.Button(self, text="Create", width=20, command=lambda:CommandEditor.create(self, cmdname.get(), textbox.get("1.0","end")))
        ok.grid(row=5, column=1)

    def add_values(self, values, name):
        value = self.treeview.insert("", 'end', name, text = name)
        for i in values:
            self.treeview.insert(value, 'end', i, text = i)
    def add_items(self, iid, values):
        for i in values:
            self.treeview.insert(iid, 'end', i, text = i, anchor = Tkinter.W)

    def create(self, cmdname, output):
            
        output = output.split('''
''')
        cmdscript = ""
        for line in output:
            if line.startswith('.'):
                if line.lower().startswith('.send:'):
                    cmdscript = cmdscript + f"\n        await ctx.send('{line[6:]}')"
                elif line.lower().startswith('.createchannel:'):
                    toscript = line[15:]
                    if ", " in toscript:
                        toscript = toscript.split(', ')
                    elif "," in toscript:
                        toscript = toscript.split(',')
                    else:
                        return
                    cmdscript = cmdscript + f"\n        await ctx.message.guild.create_{toscript[0]}_channel('{toscript[1]}')"
                elif line.lower().startswith('.script:'):
                    cmdscript = cmdscript + f"\n        {line[8:]}"
                    
        cmdscript = f'''import discord
from discord.ext import commands


class {cmdname}Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="{cmdname}")
    async def {cmdname}cmd(self, ctx, *args):
        {cmdscript}

def setup(bot):
    bot.add_cog({cmdname}Cog(bot))'''

        cwd = os.getcwd()
        os.chdir(cwd + "/Cogs")
        with open(f"{cmdname}.py", "w", encoding='utf-8') as newcmdfile:
            newcmdfile.write(cmdscript)
            newcmdfile.close()
        os.chdir(cwd)
        
    def menubar(self):
        self.menu = tk.Menu(self) 
        cascade = tk.Menu(self.menu)
        self.menu.add_cascade(label="Program", menu = cascade)
        cascade.add_command(label = "opcja 1", command=lambda: print("xD"))
        cascade.add_command(label = "opcja 2", command=lambda: print("xD"))       
        cascade2 = tk.Menu(cascade, tearoff = 0)
        cascade.add_cascade(label = "Podmenu", menu = cascade2)       
        cascade2.add_radiobutton(label = "opcja 1", command=lambda: print("xD"))
        cascade2.add_radiobutton(label = "opcja 2", command=lambda: print("xD"))
        cascade2.add_separator()
        cascade2.add_checkbutton(label = "opcja 3", command=lambda: print("xD"))
        return self.menu



app = Main()
app.mainloop()
