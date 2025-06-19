import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv

# Ortam değişkenlerini yükle (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot ayarları
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Komutları tutmak için
commands_dict = {}

# Basit JSON veri tabanı (lowdb karşılığı)
DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": []}, f)

    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

db = load_db()

# Komutları ./commands klasöründen yükle
import importlib.util
import pathlib

commands_folder = pathlib.Path("./commands")
for command_file in commands_folder.glob("*.py"):
    spec = importlib.util.spec_from_file_location(command_file.stem, command_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if hasattr(mod, "data") and hasattr(mod, "execute"):
        # Slash komutu olarak ekle
        @tree.command(name=mod.data["name"], description=mod.data["description"])
        async def dynamic_command(interaction: discord.Interaction, mod=mod):
            await mod.execute(interaction, db)
            save_db(db)

        commands_dict[mod.data["name"]] = mod

# Slash command dinleyici
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command = commands_dict.get(interaction.data["name"])
        if not command:
            await interaction.response.send_message("Komut bulunamadı.", ephemeral=True)
            return
        try:
            await command.execute(interaction, db)
            save_db(db)
        except Exception as e:
            print(e)
            await interaction.response.send_message("Bir hata oluştu!", ephemeral=True)

# Bot açıldığında çalışacak
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Web Gamer Bot giriş yaptı: {bot.user}")

# Botu çalıştır
bot.run(TOKEN)
