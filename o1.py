import discord
from discord import app_commands
import datetime

# Kullanıcı verilerini geçici olarak bellekte saklamak için
user_data = {}

# Botu başlatmak için gerekli intent'ler
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Slash komutu: /oyun-sec
@tree.command(name="oyun-sec", description="Bir oyun seç ve süreci başlat.")
@app_commands.describe(oyun="Oynamak istediğin oyunu seç")
@app_commands.choices(oyun=[
    app_commands.Choice(name="Valorant", value="valorant"),
    app_commands.Choice(name="Minecraft", value="minecraft"),
    app_commands.Choice(name="LoL", value="lol")
])
async def oyun_sec(interaction: discord.Interaction, oyun: app_commands.Choice[str]):
    user_id = str(interaction.user.id)

    # Kullanıcı zaten bir oyun başlattıysa
    if user_id in user_data:
        await interaction.response.send_message("Zaten bir oyun süreci başlattınız.", ephemeral=True)
        return

    # Yeni kullanıcı için veri kaydı oluştur
    user_data[user_id] = {
        "oyun": oyun.value,
        "baslangic": datetime.datetime.now(),
        "durum": "online"
    }

    await interaction.response.send_message(
        f"{oyun.name} oyunu seçildi! 2 günlük çevrim içi süreciniz başladı.",
        ephemeral=True
    )

# Bot hazır olduğunda komutları Discord'a yükle
@bot.event
async def on_ready():
    await tree.sync()
    print(f'{bot.user} olarak giriş yapıldı.')

# Botu başlat
bot.run("TOKEN")
