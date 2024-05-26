import discord
import os
from keep_alive import keep_alive
from discord import app_commands
import random
import sqlite3
import asyncio
from datetime import datetime, timedelta
import requests

my_secret = os.environ['TOKENN']


pokemon_caught = []
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


class MyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label='My Button')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('Button was clicked!')


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
        sql = "INSERT INTO main(member_id, wallet, bank, fishing_rod) VALUES(?,?,?,?)"
        val = (user.id, 500, 0, 0)
        cursor.execute(sql, val)
        db.commit()
        embed = discord.Embed(title=f"{user.name}'s account has been created")
    else:
        embed = discord.Embed(title=f"{user.name} account already exists")
    await interaction.response.send_message(embed=embed)
    cursor.close()
    db.close()


@tree.command(name="balance", description="Shows your balance")
async def balance(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        embed = discord.Embed(title=f"{user.name}'s Balance")
        embed.set_author(name=user.name)
        embed.add_field(name="Wallet", value=f"${result[1]:,}", inline=False)
        embed.add_field(name="Bank", value=f"${result[2]:,}", inline=False)
        embed.add_field(name="Fishing Rod", value=f"{result[3]:,}", inline=False)
        embed.set_footer(text="Bot made by Ghost")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up.")
    cursor.close()
    db.close()


@tree.command(name="delete", description="Deletes your account")
async def delete(interaction: discord.Interaction, user: discord.Member):
    user = interaction.user
    if user.id == 624308731672264704:
        db = sqlite3.connect('bank.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
        result = cursor.fetchone()
        if result:
            embed = discord.Embed(title=f"{user.name}'s account has been deleted")
            embed.set_author(name=user.name)
            embed.set_footer(text="aw")
            await interaction.response.send_message(embed=embed)
            sql = "DELETE FROM main WHERE member_id = ?"
            val = (user.id,)
            cursor.execute(sql, val)
            db.commit()
            db.close()
            cursor.close()


@discord.app_commands.checks.cooldown(1, 15)
@tree.command(name="beg", description="Beg for money")
async def beg(interaction: discord.Interaction):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        if random.randint(1, 3) == 3:
            embed = discord.Embed(title=f"{user.name} begged and got nothing")
            await interaction.response.send_message(embed=embed)
        else:
            amount = random.randint(1, 100)
            embed = discord.Embed(title=f"{user.name} begged and got ${amount:,}")
            await interaction.response.send_message(embed=embed)
            cursor.execute("UPDATE main SET wallet = wallet + ? WHERE member_id = ?", (amount, user.id))
            db.commit()
            cursor.close()
            db.close()
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up.")


@beg.error  # Tell the user when they've got a cooldown
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


@discord.app_commands.checks.cooldown(1, 3)
@tree.command(name="deposit", description="Deposit money into your bank")
async def deposit(interaction: discord.Interaction, amount: int):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        if amount > result[1]:
            await interaction.response.send_message(f"{user.name} does not have enough money to deposit ${amount:,}")
        else:
            cursor.execute("UPDATE main SET bank = bank + ? WHERE member_id = ?", (amount, user.id))
            cursor.execute("UPDATE main SET wallet = wallet - ? WHERE member_id = ?", (amount, user.id))
            db.commit()
            embed = discord.Embed(title=f"{user.name} deposited ${amount:,} into their bank")
            await interaction.response.send_message(embed=embed)
            cursor.close()
            db.close()
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up.")


@deposit.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)


@tree.command(name="users", description="temp update")
async def users(interaction: discord.Interaction):
    user = interaction.user
    if user.id == 624308731672264704:
        db = sqlite3.connect('bank.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM main")
        result = cursor.fetchall()
        embed = discord.Embed(title="Users")
        for user in result:
            user_name = f"<@{user[0]}>"
            embed.add_field(name=f"{user_name}", value=f"{user[1]:,}", inline=True)
        await interaction.response.send_message(embed=embed)
        cursor.close()
        db.close()
    else:
        await interaction.response.send_message(f"{user.name} does not have permission to use this command.")


@tree.command(name="shop", description="Shows the shop")
async def shop(interaction: discord.Interaction):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        embed = discord.Embed(title="Shop")
        embed.add_field(name="1. Fishing Rod", value="Cost: 500 coins", inline=False)
        embed.add_field(name="2. Hunting Rifle", value="Cost: 1000 coins", inline=False)
        embed.add_field(name="3. Pickaxe", value="Cost: 1500 coins", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up")


@tree.command(name="buy", description="Buy an item from the shop")
async def buy(interaction: discord.Interaction, item: int):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        if item == 1:
            if result[1] >= 500:
                cursor.execute("UPDATE main SET wallet = wallet - 500 WHERE member_id = ?", (user.id,))
                cursor.execute("UPDATE main SET fishing_rod = fishing_rod + 1 WHERE member_id = ?", (user.id,))
                db.commit()
                await interaction.response.send_message(f"{user.name} bought a fishing rod for 500 coins")
            else:
                await interaction.response.send_message(f"{user.name} does not have enough money")


@tree.command(name="add", description="Adds a column to the database")
async def add(interaction: discord.Interaction, column_name: str, format_type: str):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        if user.id == 624308731672264704:
            cursor.execute(f"ALTER TABLE main ADD COLUMN {column_name} {format_type}")
            db.commit()
            await interaction.response.send_message(f"{column_name} added to the database")
            cursor.close()
            db.close()
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up")


@tree.command(name="give", description="Gives money to a user")
async def give(interaction: discord.Interaction, user: discord.User, amount: int):
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    giver = interaction.user
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (giver.id,))
    giver_result = cursor.fetchone()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    user_result = cursor.fetchone()
    if giver_result and user_result:
        if giver_result[1] >= amount:
            cursor.execute("UPDATE main SET wallet = wallet + ? WHERE member_id = ?", (amount, user.id))
            cursor.execute("UPDATE main SET wallet = wallet - ? WHERE member_id = ?", (amount, giver.id))
            db.commit()
            await interaction.response.send_message(f"{giver.name} gave {user.name} {amount} coins")
            cursor.close()
            db.close()
        else:
            await interaction.response.send_message(f"{giver.name} does not have enough money")
    else:
        await interaction.response.send_message(f"One of the users does not have an account set up")


@tree.command(name="withdraw", description="Withdraws money from the bank")
async def withdraw(interaction: discord.Interaction, amount: int):
    user = interaction.user
    db = sqlite3.connect('bank.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM main WHERE member_id = ?", (user.id,))
    result = cursor.fetchone()
    if result:
        if result[1] >= amount:
            cursor.execute("UPDATE main SET wallet = wallet + ? WHERE member_id = ?", (amount, user.id))
            cursor.execute("UPDATE main SET bank = bank - ? WHERE member_id = ?", (amount, user.id))
            db.commit()
            await interaction.response.send_message(f"{user.name} withdrew {amount}")
            cursor.close()
            db.close()
        else:
            await interaction.response.send_message(f"{user.name} does not have enough money in the bank")
    else:
        await interaction.response.send_message(f"{user.name} does not have an account set up")


# @tree.command(name="remind", description="Reminds a user to do something")
# async def remind(interaction: discord.Interaction, user: discord.User, time: str, *, message: str):
#     # Parse the time string into a datetime object
#     # This assumes that the time string is in the format "HH:MM:SS"
#     hours, minutes, seconds = map(int, time.split(':'))
#     now = datetime.now()
#     reminder_time = now + timedelta(hours=hours, minutes=minutes, seconds=seconds)
#
#     # Calculate the delay in seconds
#     delay = (reminder_time - now).total_seconds()
#     await interaction.response.send_message(
#         f"Reminder set for {user.name} in {hours}h, {minutes}mins, {seconds}s for {message}")
#
#     # Wait for the specified amount of time
#     await asyncio.sleep(delay)
#
#     # Send the reminder
#     await interaction.channel.send(f"{user.mention}, reminder for {message}")


@tree.command(name="guess", description="Guess button for money")
async def guess(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(MyButton())
    await interaction.response.send_message('Guess the correct button for money', view=view)


@tree.command(name="catch", description="Catch the pokemon")
async def guess(interaction: discord.Interaction):
    name = interaction.data['options'][0]['value']
    url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    response = requests.get(url)
    pokemon = response.json()
    if pokemon['name'] == name:  # If the Pokémon name is correct
        user_pokemon = pokemon_caught.get(interaction.user.id, [])
        user_pokemon.append(name)
        pokemon_caught[interaction.user.id] = user_pokemon
        await interaction.response.send_message(f'Congratulations {interaction.user.name}, you caught a {name}!')
    else:
        await interaction.response.send_message(f'Oh no! The wild {name} escaped!')

@client.event
async def on_message(msg):
    if msg.channel.id == 799655169008467968 and msg.author != client.user:
        embed = msg.embeds[0]
        if "New raid" in embed.description:
            _, pokemon = embed.description.split("defeat ")
            pokemon = pokemon.replace("?", "")
            pokemon = pokemon.replace("**", "")
            if pokemon in money_raid_counters:
                await msg.channel.send(
                    f"<@&625783594966843403>  {pokemon} Potential money raid! Try: {money_raid_counters[pokemon]}")
            elif pokemon in cool_raid or pokemon.__contains__("Arceus"):
                await msg.channel.send(f"<@&625783594966843403> {pokemon} get pinged")
            else:
                await msg.channel.send(f"{pokemon} not added")
        elif "New Mega Raid" in embed.description:
            _, pokemon = embed.description.split("defeat ")
            pokemon = pokemon.replace("?", "")
            pokemon = pokemon.replace("**", "")
            if pokemon in mega_raid:
                await msg.channel.send(f"<@&625783594966843403> {pokemon} get pinged")
        else:
            pass
    if msg.channel.id == 650165688941412382 and msg.author != client.user:
        global message_count
        if msg.author == client.user:
            return

        message_count += 1

        if message_count >= 5:  # Spawn a Pokémon every 5 messages
            message_count = 0
            pokemon_id = random.randint(1, 151)  # Choose a random Pokémon from the first 151
            url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}'
            response = requests.get(url)
            pokemon = response.json()
            pokemon_name = pokemon['name']
            pokemon_image_url = pokemon['sprites']['front_default']
            embed = discord.Embed(title=f"A wild {pokemon_name} has appeared!")
            embed.set_image(url=pokemon_image_url)

keep_alive()
client.run(my_secret)
