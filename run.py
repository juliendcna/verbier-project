import requests
import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

url = "https://verbier4vallees.ch/en/shop/product/available-dates-times?activity_id=410650"

async def check_tickets():
    while True:
        try:
            # Make the request with verify=False to ignore SSL certificate checks
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes

            data = response.json()

            for date, availability in data["availabilityByDate"].items():
                if availability["available"] > 0:
                    message = f"Ski tickets are available for {date}! Book now: {url}"
                    await send_discord_message(message)

            await asyncio.sleep(3600)  # Check every hour (adjust as needed)

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

if __name__ == "__main__":
    asyncio.run(check_tickets())
