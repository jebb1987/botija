import discord
from discord.ext import commands
from fuzzywuzzy import process  # Para manejar errores tipográficos

# Habilitar los intents necesarios
intents = discord.Intents.default()
intents.reactions = True  # Habilitar intents de reacciones

# Crear el bot con los intents configurados
bot = commands.Bot(command_prefix=".", intents=intents, case_insensitive=True)

# Diccionario para almacenar los grupos
grupos = {}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def create(ctx, nombre_grupo: str):
    """
    Crea un nuevo grupo con el nombre especificado.
    """
    # Crear el mensaje inicial del grupo
    mensaje = f"**Grupo: {nombre_grupo}**\n"
    mensaje += "1. ⚔️ BK: (vacío)\n"
    mensaje += "2. ⚔️ BK: (vacío)\n"
    mensaje += "3. 🐴 DL: (vacío)\n"
    mensaje += "4. 🐴 DL: (vacío)\n"
    mensaje += "5. 🏹 ELF: (vacío)\n"
    mensaje += "6. 🏹 ELF: (vacío)\n"
    mensaje += "7. 🧙‍♂️ SM: (vacío)\n"
    mensaje += "8. 🧙‍♂️ SM: (vacío)\n"

    # Enviar el mensaje y añadir reacciones
    msg = await ctx.send(mensaje)
    for emoji in ["⚔️", "🐴", "🏹", "🧙‍♂️"]:
        await msg.add_reaction(emoji)

    # Guardar el mensaje en el diccionario de grupos
    grupos[msg.id] = {
        "nombre": nombre_grupo,
        "miembros": {emoji: [] for emoji in ["⚔️", "🐴", "🏹", "🧙‍♂️"]}
    }

@bot.event
async def on_reaction_add(reaction, user):
    """
    Maneja las reacciones para unirse a un grupo.
    """
    # Verificar si la reacción es en un mensaje de grupo y que no sea el propio bot
    if reaction.message.id in grupos and not user.bot:
        grupo = grupos[reaction.message.id]
        emoji = reaction.emoji

        # Verificar si el usuario ya está registrado en cualquier grupo activo
        for mensaje_id, datos_grupo in grupos.items():
            for miembros in datos_grupo["miembros"].values():
                if user.name in miembros and mensaje_id != reaction.message.id:
                    # Eliminar la reacción ya que el usuario ya está en otro grupo
                    await reaction.message.remove_reaction(emoji, user)
                    await user.send(f"⚠️ No puedes unirte a '{grupo['nombre']}' porque ya estás en otro grupo activo.")
                    return

        # Buscar si el usuario ya reaccionó en otro puesto válido del grupo actual
        for react in reaction.message.reactions:
            if user in await react.users().flatten() and react.emoji != emoji and react.emoji in grupo["miembros"]:
                # Eliminar la reacción anterior del usuario
                await reaction.message.remove_reaction(react.emoji, user)

                # Quitar el nombre del usuario del rol anterior
                if user.name in grupo["miembros"][react.emoji]:
                    grupo["miembros"][react.emoji].remove(user.name)

        # Verificar si hay espacio disponible en el rol correspondiente
        if len(grupo["miembros"][emoji]) >= 2:
            # Eliminar la reacción porque ya no hay espacio disponible
            await reaction.message.remove_reaction(emoji, user)
            await user.send(f"⚠️ El puesto para '{emoji}' está lleno. No puedes unirte.")
            return

        # Agregar al usuario si no está ya en la lista del emoji actual
        if user.name not in grupo["miembros"][emoji]:
            grupo["miembros"][emoji].append(user.name)

            # Limitar la cantidad de miembros mostrados a 2 por rol
            miembros_bk = grupo["miembros"]["⚔️"][:2]
            miembros_dl = grupo["miembros"]["🐴"][:2]
            miembros_elf = grupo["miembros"]["🏹"][:2]
            miembros_sm = grupo["miembros"]["🧙‍♂️"][:2]

            # Actualizar el mensaje con los nuevos miembros
            mensaje = f"**Grupo: {grupo['nombre']}**\n"
            mensaje += f"1. ⚔️ BK: {miembros_bk[0] if len(miembros_bk) > 0 else '(vacío)'}\n"
            mensaje += f"2. ⚔️ BK: {miembros_bk[1] if len(miembros_bk) > 1 else '(vacío)'}\n"
            mensaje += f"3. 🐴 DL: {miembros_dl[0] if len(miembros_dl) > 0 else '(vacío)'}\n"
            mensaje += f"4. 🐴 DL: {miembros_dl[1] if len(miembros_dl) > 1 else '(vacío)'}\n"
            mensaje += f"5. 🏹 ELF: {miembros_elf[0] if len(miembros_elf) > 0 else '(vacío)'}\n"
            mensaje += f"6. 🏹 ELF: {miembros_elf[1] if len(miembros_elf) > 1 else '(vacío)'}\n"
            mensaje += f"7. 🧙‍♂️ SM: {miembros_sm[0] if len(miembros_sm) > 0 else '(vacío)'}\n"
            mensaje += f"8. 🧙‍♂️ SM: {miembros_sm[1] if len(miembros_sm) > 1 else '(vacío)'}\n"

            await reaction.message.edit(content=mensaje)

@bot.command(name="close")
async def close_group(ctx, group_name: str):
    """
    Cierra un grupo existente.
    """
    # Buscar el grupo por nombre usando fuzzy matching
    nombres_grupos = [grupo["nombre"] for grupo in grupos.values()]
    mejor_coincidencia, puntaje = process.extractOne(group_name, nombres_grupos)

    # Si la coincidencia es buena (puntaje > 70), usar ese nombre
    if puntaje > 70:
        for mensaje_id, grupo in grupos.items():
            if grupo["nombre"] == mejor_coincidencia:
                await ctx.send(f"🗑️ Grupo '{mejor_coincidencia}' eliminado correctamente.")
                del grupos[mensaje_id]
                return
    else:
        await ctx.send(f"⚠️ No se encontró ningún grupo con el nombre '{group_name}'.")

@bot.command(name="list")
async def list_groups(ctx):
    """
    Muestra una lista de los grupos activos.
    """
    if grupos:
        # Si hay grupos activos, mostrar sus nombres
        mensaje = "**Grupos Activos:**\n"
        for grupo in grupos.values():
            mensaje += f"- {grupo['nombre']}\n"
        await ctx.send(mensaje)
    else:
        # Si no hay grupos activos
        await ctx.send("⚠️ No hay grupos activos en este momento.")

# Ejecutar el bot
bot.run('MTM0NTA3NTczNTMyODU4NzgwNw.GgbLer.a_Zy2MuHc69lT1oq6BX9krqMgAelzYb88nmW5U')
