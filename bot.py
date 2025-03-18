import discord
from discord.ext import commands
from fuzzywuzzy import process
import json

# Cargar el token desde config.json
with open('config.json', 'r') as file:
    config = json.load(file)

intents = discord.Intents.default()
intents.reactions = True
bot = commands.Bot(command_prefix=".", intents=intents, case_insensitive=True)

grupos = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def create(ctx, nombre_grupo: str):
    mensaje = f"**Grupo: {nombre_grupo}**\n"
    mensaje += "1. ⚔️ BK: (vacío)\n2. ⚔️ BK: (vacío)\n3. 🐴 DL: (vacío)\n4. 🐴 DL: (vacío)\n"
    mensaje += "5. 🏹 ELF: (vacío)\n6. 🏹 ELF: (vacío)\n7. 🧙‍♂️ SM: (vacío)\n8. 🧙‍♂️ SM: (vacío)\n"

    msg = await ctx.send(mensaje)
    for emoji in ["⚔️", "🐴", "🏹", "🧙‍♂️"]:
        await msg.add_reaction(emoji)

    grupos[msg.id] = {
        "nombre": nombre_grupo,
        "miembros": {emoji: [] for emoji in ["⚔️", "🐴", "🏹", "🧙‍♂️"]}
    }

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.id in grupos and not user.bot:
        grupo = grupos[reaction.message.id]
        emoji = reaction.emoji

        for mensaje_id, datos_grupo in grupos.items():
            for miembros in datos_grupo["miembros"].values():
                if user.name in miembros and mensaje_id != reaction.message.id:
                    await reaction.message.remove_reaction(emoji, user)
                    await user.send(f"⚠️ No puedes unirte a '{grupo['nombre']}' porque ya estás en otro grupo activo.")
                    return

        if len(grupo["miembros"][emoji]) < 2 and user.name not in grupo["miembros"][emoji]:
            grupo["miembros"][emoji].append(user.name)
            await actualizar_mensaje_grupo(reaction.message, grupo)

async def actualizar_mensaje_grupo(mensaje, grupo):
    contenido = f"**Grupo: {grupo['nombre']}**\n"
    roles = ["⚔️ BK", "🐴 DL", "🏹 ELF", "🧙‍♂️ SM"]
    contador = 1

    for emoji, miembros in grupo["miembros"].items():
        for i in range(2):
            miembro = miembros[i] if i < len(miembros) else "(vacío)"
            contenido += f"{contador}. {emoji} {roles[contador // 2]}: {miembro}\n"
            contador += 1

    await mensaje.edit(content=contenido)

bot.run(config["TOKEN"])
