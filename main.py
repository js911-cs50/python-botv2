import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import random
import sqlite3
import asyncio
from datetime import datetime, timedelta
import requests

message_count_lock = asyncio.Lock()
message_count = 0


my_secret = os.environ['TOKENN']


pokemon_caught = {}
money_raid_counters = {
    "Aerodactyl": "Kyogre-Primal, Magnezone",
    "Aurorus": "Any fighting type (Lucario, Mewtwo, medicham)",
    "Blissey": "Any fighting type (Lucario, Mewtwo, medicham)",
    "Skarmory": "Magnezone",
    "Virizion": "Salamence (other flying types may work)",
    "Appletun": "Abomasnow, Kyurem",
    "Flapple": "Abomasnow, Kyurem",
    "Heracross": "Salamence (other flying types may work)",
    "Volcarona": "Tyranitar",
    "Chesnaught": "Salamence",
    "Charizard": "Tyranitar",
    "Venusaur": "Salamence",
    "Coalossal": "Kyogre-Primal",
    "Vileplume": "Salamence",
    "Arboliva": "Salamence",
    "Gyarados": "Bellibolt, Magnezone",
    "Tyranitar": "Lucario, Medicham",
}

mega_raid = ["Diancie-Mega", "Groudon-Primal", "Heracross-Mega", "Kangaskhan-Mega", "Kyogre-Primal", "Latias-Mega",
             "Latios-Mega", "Lucario-Mega", "Mawile-Mega", "Medicham-Mega", "Metagross-Mega", "Mewtwo-Mega-X",
             "Mewtwo-Mega-Y", "Pidgeot-Mega", "Pinsir-Mega", "Rayquaza-Mega", "Salamence-Mega", "Sceptile-Mega",
             "Tyranitar-Mega"]

cool_raid = ["Articuno", "Articuno-Galar", "Azelf", "Blacephalon", "Buzzwole", "Calyrex", "Celebi", "Celesteela",
             "Cobalion", "Cosmog", "Cosmoem", "Cresselia", "Darkrai", "Dialga", "Diancie", "Entei", "Eternatus",
             "Genesect", "Giratina", "Giratina-Origin", "Glastrier", "Groudon", "Guzzlord", "Heatran", "Ho-Oh", "Hoopa",
             "Jirachi", "Kartana", "Keldeo", "Keldeo-Resolute", "Kyogre", "Kyurem", "Landorus", "Latias", "Latios",
             "Lugia", "Lunala", "Melmetal", "Meltan", "Meloetta", "Mesprit", "Mew", "Mewtwo", "Moltres",
             "Moltres-Galar", "Naganadel", "Necrozma", "Nihilego", "Palkia", "Pheromosa", "Poipole", "Raikou",
             "Rayquaza", "Regice", "Regidrago", "Regieleki", "Regigigas", "Regirock", "Registeel", "Reshiram",
             "Shaymin", "Shaymin-Sky", "Solgaleo", "Spectrier", "Stakataka", "Suicune", "Terrakion", "Thundurus",
             "Tornadus", "Type:Null", "Uxie", "Victini", "Virizion", "Volcanion", "Xerneas", "Xurkitree", "Yveltal",
             "Zacian", "Zamazenta", "Zapdos", "Zapdos-Galar", "Zarude", "Zekrom", "Zeraora", "Zygarde", "Miraidon",
             "Deoxys-Speed", "Koraidon"]


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        print(f"We have logged in as {client.user}")
        print(discord.__version__)
        if not self.synced:
            await tree.sync()
            self.synced = True


client = aclient()
tree = app_commands.CommandTree(client)


# /ping to run the command
@tree.command(name="ping", description="Ping ms")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {str(round(client.latency * 1000))}ms")


@tree.command(name="hello", description="Says Hello", guild=discord.Object(id=625780431035564082))
async def hello(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(f"Hello! {user.mention}")


@tree.command(name="start", description="Start the bot")
async def start(interaction: discord.Interaction):
    # Check if user is None
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')  # Make sure to use quotes for the database name
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM main WHERE member_id = ?",
                   (user.id,))
    result = cursor.fetchone()
    if result is None:
        sql = "INSERT INTO main(member_id, wallet, bank, fishing_rod, pokemon) VALUES(?,?,?,?,?)"
        val = (user.id, 500, 0, 0, None)
        cursor.execute(sql, val)
        db.commit()
        embed = discord.Embed(title=f"{user.name}'s account has been created")
    else:
        embed = discord.Embed(title=f"{user.name} account already exists")
    await interaction.response.send_message(embed=embed)
    cursor.close()
    db.close()

@tree.command(name="catch", description="Catch the pokemon")
async def guess(interaction: discord.Interaction, pokemon_name: str):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}'
    response = requests.get(url)
    pokemon_data = response.json()

    if pokemon_data['name'] == pokemon_name:
        user_pokemon = pokemon_caught.get(interaction.user.id, [])
        user_pokemon.append(pokemon_name)
        pokemon_caught[interaction.user.id] = user_pokemon

        user = interaction.user
        try:
            db = sqlite3.connect('bank.sqlite')
            cursor = db.cursor()

            # Check for user record (assuming user_id is a column in "main")
            cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
            result = cursor.fetchone()

            if result:
                # Insert Pokemon data if user record exists
                cursor.execute("INSERT INTO pokemon VALUES (?, ?)", (user.id, pokemon_name))
            else:
                # Handle case where user record is missing (optional)
                print(f"User with ID {user.id} not found in main table")

            db.commit()

        except sqlite3.Error as err:
            print(f"Database error: {err}")

        finally:
            db.close()

        await interaction.response.send_message(f'Congratulations {interaction.user.name}, you caught a {pokemon_name}!')
    else:
        await interaction.response.send_message(f'Oh no! The wild {pokemon_name} escaped!')

    global spawned_pokemon
    spawned_pokemon = None

@tree.command(name="create_pokemon_table", description="Create a pokemon table in the database")
async def create_pokemon_table(interaction: discord.Interaction):
    db = sqlite3.connect('bank.sqlite')  # Make sure to use quotes for the database name
    cursor = db.cursor()

    # Create table
    cursor.execute('''CREATE TABLE IF NOT EXISTS pokemon
                     (user_id text, pokemon_name text)''')

    # Save (commit) the changes
    db.commit()

    # Close the connection
    cursor.close()
    db.close()

    await interaction.response.send_message('Pokemon table created in the database.')



@tree.command(name="pokemon", description="Shows your pokemon")
async def pokemon(interaction: discord.Interaction):
    user = interaction.user
    try:
        db = sqlite3.connect('bank.sqlite')
        cursor = db.cursor()

        cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("SELECT pokemon_name FROM pokemon WHERE user_id = ?", (user.id,))
            pokemon = cursor.fetchall()
            if pokemon:
                embed = discord.Embed(title="Your Pokemon")
                for poke in pokemon:
                    the_poke = f"{poke[0]}"
                    embed.add_field(name=f"{the_poke}", value=f"{the_poke}", inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("You haven't caught any Pokemon yet!")

    except sqlite3.Error as err:
        print(f"Database error: {err}")
    finally:
        db.close()
        cursor.close()
@client.event
async def on_message(msg):
    if msg.channel.id == 650165688941412382 and msg.author != client.user:
        global message_count

        async with message_count_lock:
            message_count += 1

            if message_count >= 5:  # Spawn a Pokémon every 5 messages
                message_count = 0

                pokemon_id = random.randint(1, 1025)  # Choose a random Pokémon from the first 151
                url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}'
                response = requests.get(url)
                pokemon = response.json()

                global spawned_pokemon
                spawned_pokemon = pokemon['name']
                pokemon_image_url = pokemon['sprites']['front_default']
                embed = discord.Embed(title=f"A wild {spawned_pokemon} has appeared!")
                embed.set_image(url=pokemon_image_url)
                await msg.channel.send(embed=embed)

keep_alive()
client.run(my_secret)
