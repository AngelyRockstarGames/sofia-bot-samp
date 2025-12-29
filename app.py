import discord
import os
from discord.ext import commands
from samp_client.client import SampClient
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SAMP_IP = os.getenv('SAMP_IP', '144.217.64.5')
SAMP_PORT = int(os.getenv('SAMP_PORT', 6135))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def update_presence():
    try:
        with SampClient(address=SAMP_IP, port=SAMP_PORT) as client:
            info = client.get_server_info()
            players_online = info.players
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=f"Jugadores ({players_online})"
            )
            await bot.change_presence(activity=activity)
    except:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Jugadores (0)"
        )
        await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
    print(f'Bot conectado: {bot.user}')
    
    await update_presence()
    
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error sincronizando: {e}")

@bot.command(name='users')
async def samp_users(ctx):
    await ctx.send("Consultando usuarios del servidor SA-MP...")
    
    try:
        with SampClient(address=SAMP_IP, port=SAMP_PORT) as client:
            info = client.get_server_info()
            players_online = info.players
            max_players = info.max_players
            server_name = info.hostname
            
            await update_presence()
            
            embed = discord.Embed(
                title=f"Usuarios en: {server_name}",
                color=0x3498db
            )
            
            embed.add_field(name="Dirección", value=f"`{SAMP_IP}:{SAMP_PORT}`", inline=False)
            
            if players_online > 0:
                try:
                    player_list = client.get_players()
                    
                    if player_list and len(player_list) > 0:
                        player_names = [player.name for player in player_list[:10]]
                        players_text = "\n".join([f"• {name}" for name in player_names])
                        
                        if len(player_list) > 10:
                            players_text += f"\n\n*... y {len(player_list) - 10} más*"
                        
                        embed.add_field(
                            name=f"Jugadores Conectados ({players_online}/{max_players})",
                            value=players_text,
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name=f"Jugadores Conectados ({players_online}/{max_players})",
                            value=f"Hay {players_online} jugador(es) conectado(s)",
                            inline=False
                        )
                except:
                    embed.add_field(
                        name=f"Jugadores Conectados ({players_online}/{max_players})",
                        value=f"Hay {players_online} jugador(es) conectado(s)",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="Jugadores Conectados",
                    value="No hay usuarios en el servidor",
                    inline=False
                )
            
            embed.add_field(
                name="Capacidad",
                value=f"Máximo: {max_players} jugadores",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
    except Exception as e:
        print(f"Error: {e}")
        
        await update_presence()
        
        embed_error = discord.Embed(
            title="Error de Conexión",
            description="No se pudo conectar al servidor SA-MP.",
            color=0xFF0000
        )
        embed_error.add_field(
            name="Posibles causas", 
            value=f"Servidor apagado\nIP/Puerto incorrecto\nFirewall bloqueando", 
            inline=False
        )
        
        await ctx.send(embed=embed_error)

@bot.tree.command(name="users", description="Muestra los usuarios conectados al servidor SA-MP")
async def slash_samp_users(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        with SampClient(address=SAMP_IP, port=SAMP_PORT) as client:
            info = client.get_server_info()
            players_online = info.players
            max_players = info.max_players
            server_name = info.hostname
            
            await update_presence()
            
            embed = discord.Embed(
                title=f"Usuarios en: {server_name}",
                color=0x2ecc71
            )
            
            embed.add_field(name="Servidor", value=f"`{SAMP_IP}:{SAMP_PORT}`", inline=False)
            
            if players_online > 0:
                try:
                    player_list = client.get_players()
                    
                    if player_list and len(player_list) > 0:
                        player_names = [player.name for player in player_list[:10]]
                        players_text = "\n".join([f"• {name}" for name in player_names])
                        
                        if len(player_list) > 10:
                            players_text += f"\n\n*... y {len(player_list) - 10} más*"
                        
                        embed.add_field(
                            name=f"Conectados ({players_online}/{max_players})",
                            value=players_text,
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name=f"Conectados ({players_online}/{max_players})",
                            value=f"{players_online} jugador(es) activo(s)",
                            inline=False
                        )
                except:
                    embed.add_field(
                        name=f"Conectados ({players_online}/{max_players})",
                        value=f"{players_online} jugador(es) activo(s)",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="Jugadores Conectados",
                    value="No hay usuarios en el servidor",
                    inline=False
                )
            
            embed.add_field(
                name="Límite",
                value=f"Máximo: {max_players} jugadores",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        print(f"Error: {e}")
        
        await update_presence()
        
        embed_error = discord.Embed(
            title="Conexión fallida",
            description="No se pudo obtener información del servidor.",
            color=0xFF0000
        )
        
        await interaction.followup.send(embed=embed_error)

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN no encontrado en .env")
    else:
        bot.run(TOKEN)
