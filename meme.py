import os
import requests
import logging
import discord
import asyncio
import threading
from discord.ext import commands, tasks
from flask import Flask
from dotenv import load_dotenv
from bsvlib import Wallet
from datetime import datetime, timedelta
from io import BytesIO
from zipfile import ZipFile
from collections import defaultdict

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
logging.info("Loading environment variables")
load_dotenv()

# Retrieve the bot token and wallet information from environment variables
bot_token = os.getenv("DISCORD_TOKEN")
private_key_wif = os.getenv("WALLET_PRIVATE_KEY")
winning_channel_id = int(os.getenv("WINNING_CHANNEL_ID"))
private_channel_id = int(os.getenv("PRIVATE_CHANNEL_ID"))

# Debugging: Print tokens to confirm they are loaded correctly
logging.info(f"Bot token loaded: {bool(bot_token)}")
logging.info(f"Private key loaded: {bool(private_key_wif)}")
logging.info(f"Winning channel ID: {winning_channel_id}")
logging.info(f"Private channel ID: {private_channel_id}")

app = Flask(__name__)

# Define intents for the bot
intents = discord.Intents.default()
intents.messages = True  # To receive messages
intents.guilds = True  # Access to guild events
intents.message_content = True  # Required to access message content under new API rules
intents.reactions = True  # Required to track reactions

bot = commands.Bot(command_prefix="/", intents=intents)

# Meme submission dictionary to track submissions and reactions
meme_submissions = {}
user_badges = {}
total_sats_earned = {}

# Dictionary to store emoji submissions
emoji_submissions = defaultdict(list)

# Dictionary to store the count of approved emojis per user
approved_emojis_count = defaultdict(int)

def award_badge(user_id, badge):
    if user_id not in user_badges:
        user_badges[user_id] = []
    if badge not in user_badges[user_id]:
        user_badges[user_id].append(badge)
        logging.info(f"Awarded badge '{badge}' to user ID {user_id}")
        return badge
    return None

@bot.command(name="memelord", help="Submit a meme and get 10 reactions to win 10000 sats.")
async def memelord(ctx):
    author_tag = str(ctx.author)  # This includes the username and discriminator
    logging.info(f"Command '/memelord' invoked by {author_tag} (ID: {ctx.author.id})")

    # Prompt the user to upload an image
    await ctx.send("Please upload an image to submit your meme.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0

    # Wait for the user to upload an image
    try:
        message = await bot.wait_for('message', check=check, timeout=60)
        logging.info(f"Image uploaded by {author_tag} (ID: {ctx.author.id})")
    except asyncio.TimeoutError:
        logging.warning(f"Image upload timeout for user {author_tag} (ID: {ctx.author.id})")
        await ctx.send("You took too long to upload an image. Please try again.")
        return

    attachment = message.attachments[0]
    if not (attachment.filename.endswith(".png") or attachment.filename.endswith(".jpg") or 
            attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".gif")):
        logging.warning(f"Invalid file type uploaded by {author_tag} (ID: {ctx.author.id})")
        await ctx.send("Please upload a valid image file (png, jpg, jpeg, gif).")
        return

    meme_submissions[message.id] = {
        "user_id": ctx.author.id,
        "username": ctx.author.name,  # Only use the username without discriminator
        "reactions": set(),  # Use a set to track unique users who reacted
        "reaction_count": 0,  # To track total reaction count for simulation
        "attachment_url": attachment.url,
        "submission_time": datetime.now(),
    }
    logging.info(f"Meme submitted by {ctx.author.name} (ID: {ctx.author.id}). Message ID: {message.id}")
    await ctx.send(f"Meme submitted by {ctx.author.mention}. Get 10 reactions to stack 10000 sats!")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    message = reaction.message
    if message.id not in meme_submissions:
        return

    submission = meme_submissions[message.id]
    if user.id not in submission["reactions"]:
        submission["reactions"].add(user.id)
        submission["reaction_count"] += 1
        reactions = submission["reaction_count"]
        logging.info(f"Reaction added to meme: {submission['attachment_url']} by user {user} (ID: {user.id}). Total reactions: {reactions}")

        if reactions >= 10:
            await process_payout(message, submission)

async def process_payout(message, submission):
    username = submission["username"]
    user_id = submission["user_id"]
    logging.info(f"Processing payout for user {username} (ID: {user_id})")
    user_address = fetch_user_address(username)
    if user_address:
        # Handle payout logic here using the unchanged payment process
        tx_id = send_sats(private_key_wif, user_address, 10000)

        # Update total sats earned
        if user_id not in total_sats_earned:
            total_sats_earned[user_id] = 0
        total_sats_earned[user_id] += 10000
        logging.info(f"User {username} (ID: {user_id}) earned 10000 sats. Total sats: {total_sats_earned[user_id]}")

        # Award badges for earning sats
        new_badges = []
        additional_sats = 0
        if total_sats_earned[user_id] >= 100000 and "Memelord" not in user_badges.get(user_id, []):
            award_badge(user_id, "Memelord")
            additional_sats = 100000
            new_badges.append("Memelord")
        elif total_sats_earned[user_id] >= 50000 and "Based Memer" not in user_badges.get(user_id, []):
            award_badge(user_id, "Based Memer")
            additional_sats = 50000
            new_badges.append("Based Memer")
        elif total_sats_earned[user_id] == 10000 and "Normie Badge" not in user_badges.get(user_id, []):
            award_badge(user_id, "Normie Badge")
            new_badges.append("Normie Badge")

        embed = discord.Embed(
            title="🎉 Based! 🎉",
            description=f"Your meme got 10 reactions, {username}! You win 10000 sats!",
            color=discord.Color.green()
        )
        embed.add_field(name="Transaction ID", value=tx_id, inline=False)
        embed.add_field(name="Total Sats Earned", value=total_sats_earned[user_id], inline=False)
        if new_badges:
            badge_msg = f"You have also earned the following badge(s): {', '.join(new_badges)}"
            embed.add_field(name="New Badges", value=badge_msg, inline=False)
            if additional_sats > 0:
                tx_id_bonus = send_sats(private_key_wif, user_address, additional_sats)
                total_sats_earned[user_id] += additional_sats
                embed.add_field(name="Bonus Transaction ID", value=tx_id_bonus, inline=False)
                badge_msg += f" and an additional {additional_sats} sats bonus!"

        await message.channel.send(embed=embed)

        # Post the winning meme to the specified channel
        winning_channel = bot.get_channel(winning_channel_id)
        if winning_channel:
            embed = discord.Embed(
                title="This meme has been approved by 1Sat Society",
                description="Pump our bags!",
                color=discord.Color.blue()
            )
            embed.set_image(url=submission['attachment_url'])
            await winning_channel.send(embed=embed)
        logging.info(f"Winning meme posted to channel ID {winning_channel_id}")

@bot.command(name="badges", help="Displays your earned badges and total sats earned.")
async def show_badges(ctx):
    user_id = ctx.author.id
    author_tag = str(ctx.author)
    logging.info(f"Command '/badges' invoked by {author_tag} (ID: {ctx.author.id})")
    user_badges_list = user_badges.get(user_id, [])
    total_sats = total_sats_earned.get(user_id, 0)

    embed = discord.Embed(title="🏅 Meme Badge 🏅", color=discord.Color.orange())
    for badge in user_badges_list:
        embed.add_field(name=badge, value="\u200b", inline=False)
    embed.add_field(name="Total Sats Earned", value=total_sats, inline=False)

    await ctx.send(embed=embed)
    logging.info(f"Displayed badges for user {author_tag} (ID: {ctx.author.id})")

@tasks.loop(minutes=1)
async def check_expired_submissions():
    now = datetime.now()
    expired_submissions = [msg_id for msg_id, sub in meme_submissions.items() if now - sub["submission_time"] > timedelta(hours=24)]
    for msg_id in expired_submissions:
        del meme_submissions[msg_id]
        logging.info(f"Meme with ID {msg_id} has expired and has been removed from tracking.")

@bot.event
async def on_ready():
    check_expired_submissions.start()
    logging.info("Bot is ready and check_expired_submissions task has started.")

# Fetch user BitcoinSV address from a web service
def fetch_user_address(username):
    logging.info(f"Fetching BSV address for username: {username}")
    try:
        response = requests.get('https://1satsociety.com/show_users')
        response.raise_for_status()

        # Parse the response content, handling <br> tags by replacing them with newlines
        content = response.text.replace("<br>", "\n")
        users = content.splitlines()

        for user in users:
            if user.startswith(f"Username: {username}, BSV Address:"):
                address_info = user.split(", BSV Address: ")[1].split(",")[0]
                if address_info != "Not set":
                    logging.info(f"Address retrieved for username {username}: {address_info}")
                    return address_info
        logging.info(f"No address found for username {username}")
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve user addresses: {e}")
    return None

# Function to send sats using bsvlib
def send_sats(private_key_wif, to_address, amount_sats):
    logging.info(f"Preparing to send {amount_sats} sats to {to_address}")
    try:
        outputs = [(to_address, amount_sats)]
        wallet = Wallet([private_key_wif])
        tx = wallet.create_transaction(outputs=outputs)
        result = tx.broadcast()
        logging.info(f"Transaction successful: {result}")
        return result.data
    except Exception as e:
        logging.error(f"Failed to send transaction: {str(e)}")
        return None

@bot.command(name="submitemojis", help="Submit a zip file containing emojis.")
async def submitemojis(ctx):
    author_tag = str(ctx.author)  # This includes the username and discriminator
    logging.info(f"Command '/submitemojis' invoked by {author_tag} (ID: {ctx.author.id})")

    if len(ctx.message.attachments) != 1 or not ctx.message.attachments[0].filename.endswith('.zip'):
        await ctx.send("Please upload a single zip file with your command.")
        return

    attachment = ctx.message.attachments[0]
    response = await attachment.read()
    zip_file = BytesIO(response)

    try:
        with ZipFile(zip_file) as zip:
            for zip_entry in zip.infolist():
                # Ignore unsupported files like __MACOSX directory and hidden files
                if zip_entry.filename.startswith('__MACOSX') or zip_entry.filename.startswith('.'):
                    continue
                if zip_entry.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    emoji_submissions[ctx.author.id].append((zip_entry.filename, zip.read(zip_entry.filename), ctx.channel.id))
        await ctx.send(f"Your emoji submission has been received, {ctx.author.mention}.")
        logging.info(f"Emoji submission received from {author_tag} (ID: {ctx.author.id})")

        # Send a message to the private admin channel
        private_channel = bot.get_channel(private_channel_id)
        if private_channel:
            await private_channel.send(
                f"New emoji submission from {ctx.author.mention}. Use /listemojis <@{ctx.author.id}> to review."
            )

    except Exception as e:
        logging.error(f"Failed to process zip file: {str(e)}")
        await ctx.send("Failed to process your zip file. Please ensure it contains valid image files.")

@bot.command(name="approveemojis", help="Approve emojis submitted by a user.")
@commands.has_permissions(manage_emojis=True)
async def approveemojis(ctx, user: discord.User):
    author_tag = str(ctx.author)
    user_tag = str(user)
    logging.info(f"Command '/approveemojis' invoked by {author_tag} for user {user_tag} (ID: {user.id})")

    if user.id not in emoji_submissions:
        await ctx.send(f"No emoji submissions found for {user.mention}.")
        return

    submission_channel_id = emoji_submissions[user.id][0][2]
    submission_channel = bot.get_channel(submission_channel_id)
    approved_emojis = 0

    for filename, filedata, _ in emoji_submissions[user.id]:
        try:
            if len(filedata) > 256 * 1024:  # Check if file size is greater than 256 KB
                raise ValueError(f"File {filename} exceeds the size limit of 256 KB.")
            emoji = await ctx.guild.create_custom_emoji(name=filename.split('.')[0], image=filedata)
            await submission_channel.send(f"Emoji {emoji.name} approved and added to the server!")
            approved_emojis += 1
        except (discord.HTTPException, ValueError) as e:
            logging.error(f"Failed to create emoji {filename}: {str(e)}")
            await ctx.send(f"Failed to create emoji {filename}: {str(e)}")

    if approved_emojis > 0:
        # Update the approved emoji count
        approved_emojis_count[user.id] += approved_emojis
        await ctx.send(f"Approved {approved_emojis} emojis for {user.mention}.")
        del emoji_submissions[user.id]

        # Calculate total payout
        total_payout = approved_emojis_count[user.id] * 1500
        # Send payout
        tx_id = await payout_sats(user.id, total_payout)
        if tx_id:
            await submission_channel.send(f"{user.mention} has been paid {total_payout} sats. Transaction ID: {tx_id}")
            approved_emojis_count[user.id] = 0  # Reset count after successful payout
        else:
            await submission_channel.send(f"Failed to pay {user.mention} {total_payout} sats.")
    else:
        await ctx.send(f"Failed to approve any emojis for {user.mention}.")

@bot.command(name="listemojis", help="List submitted emojis for a user.")
@commands.has_permissions(manage_emojis=True)
async def listemojis(ctx, user: discord.User):
    author_tag = str(ctx.author)
    user_tag = str(user)
    logging.info(f"Command '/listemojis' invoked by {author_tag} for user {user_tag} (ID: {user.id})")

    if user.id not in emoji_submissions or not emoji_submissions[user.id]:
        await ctx.send(f"No emoji submissions found for {user.mention}.")
        return

    embed = discord.Embed(title=f"Submitted Emojis by {user}", color=discord.Color.blue())
    files = [discord.File(BytesIO(filedata), filename=filename) for filename, filedata, _ in emoji_submissions[user.id]]

    for filename, filedata, _ in emoji_submissions[user.id]:
        embed.add_field(name=filename, value="\u200b", inline=False)
        embed.set_image(url=f"attachment://{filename}")

    await ctx.send(embed=embed, files=files)

@bot.command(name="rejectemojis", help="Reject emojis submitted by a user.")
@commands.has_permissions(manage_emojis=True)
async def rejectemojis(ctx, user: discord.User):
    author_tag = str(ctx.author)
    user_tag = str(user)
    logging.info(f"Command '/rejectemojis' invoked by {author_tag} for user {user_tag} (ID: {user.id})")
    if user.id not in emoji_submissions:
        await ctx.send(f"No emoji submissions found for {user.mention}.")
        return

    submission_channel_id = emoji_submissions[user.id][0][2]
    submission_channel = bot.get_channel(submission_channel_id)

    await submission_channel.send(f"Your emoji submission has been rejected, {user.mention}.")
    del emoji_submissions[user.id]
    await ctx.send(f"Rejected emoji submission for {user.mention}.")

async def payout_sats(user_id, amount):
    user = await bot.fetch_user(user_id)  # Use fetch_user to ensure we get the user from the API
    if not user:
        logging.error(f"Failed to fetch user with ID {user_id}")
        return None

    username = user.name  # Only use the username part
    logging.info(f"Processing payout for user {username} (ID: {user_id})")
    user_address = fetch_user_address(username)
    if user_address:
        tx_id = send_sats(private_key_wif, user_address, amount)
        if tx_id:
            logging.info(f"User {username} (ID: {user_id}) earned {amount} sats. Transaction ID: {tx_id}")
            return tx_id
        else:
            logging.error(f"Transaction failed for user {username} (ID: {user_id})")
            return None
    else:
        logging.error(f"Failed to fetch BSV address for user {username} (ID: {user_id})")
        return None

if __name__ == "__main__":
    logging.info("Starting bot and Flask app")
    threading.Thread(target=lambda: app.run(port=5001)).start()
    bot.run(bot_token)
