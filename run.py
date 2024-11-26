import os
import requests
import asyncio
import discord
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()  # Load environment variables from .env file

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

url = "https://verbier4vallees.ch/en/shop/product/available-dates-times?activity_id=410650"

async def check_tickets():
    last_check_time = datetime.now()
    tickets_found_last_hour = False

    while True:
        try:
            # Make the request with verify=False to ignore SSL certificate checks
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes

            data = response.json()
            tickets_found = False

            for date, availability in data["availabilityByDate"].items():
                if availability["available"] > 0:
                    tickets_found = True
                    tickets_found_last_hour = True
                    message = f"Ski tickets are available for {date}! Book now: {url}"
                    await send_discord_message(message)

            if not tickets_found:
                print("No tickets found in this check.")

            # Check if an hour has passed
            if datetime.now() - last_check_time >= timedelta(hours=1):
                if not tickets_found_last_hour:
                    await send_discord_message("No tickets found in the last hour.")
                # Reset the timer and the flag
                last_check_time = datetime.now()
                tickets_found_last_hour = False

            await asyncio.sleep(60)  # Check every 60 seconds

        except requests.exceptions.RequestException as e:
            print(f"Error checking tickets: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error

async def send_discord_message(message):
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(message)
        await client.close()

    await client.start(DISCORD_TOKEN)

# Run the check_tickets function
asyncio.run(check_tickets())
