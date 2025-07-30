#!/usr/bin/env python3
# src/scrape_telegram_channel.py

import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import asyncio
import pandas as pd

# --- Configuration ---
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

SOURCES_FILE = 'sources.csv'
OUTPUT_IMAGE_DIR = 'data/scraped_telegram_images/'
OUTPUT_CSV_FILE = 'output/telegram_scrape_results.csv'

async def main():
    channel_name = "morskoy_46"
    all_results = []

    async with TelegramClient('mariupol_session', API_ID, API_HASH) as client:
        print(f"\nScraping channel: @{channel_name}")

        async for message in client.iter_messages(channel_name):
            meta = {
                'file_path': None,
                'media_type': None,
                'message_id': message.id,
                'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                'sender_id': message.sender_id,
                'caption': message.text,
                'message_link': f"https://t.me/{channel_name}/{message.id}",
                'file_size': None,
                'mime_type': None
            }
            # Images/photos
            if message.photo:
                filename = f"{message.date.strftime('%Y-%m-%d')}_{message.id}.jpg"
                filepath = os.path.join('/Users/alexeykovalev/Desktop/urbicide_project/data/processed/Morskoy46/telegram_images_raw/', filename)
                if not os.path.exists(filepath):
                    await message.download_media(file=filepath)
                meta['file_path'] = filepath
                meta['media_type'] = 'photo'
            # Videos
            elif message.video:
                filename = f"{message.date.strftime('%Y-%m-%d')}_{message.id}.mp4"
                filepath = os.path.join('/Users/alexeykovalev/Desktop/urbicide_project/data/processed/Morskoy46/telegram_videos_raw/', filename)
                if not os.path.exists(filepath):
                    await message.download_media(file=filepath)
                meta['file_path'] = filepath
                meta['media_type'] = 'video'
            # Documents (PDFs, DOCX, etc.)
            elif message.document:
                ext = message.document.mime_type.split('/')[-1] if message.document.mime_type else 'bin'
                filename = f"{message.date.strftime('%Y-%m-%d')}_{message.id}.{ext}"
                filepath = os.path.join('/Users/alexeykovalev/Desktop/urbicide_project/data/processed/Morskoy46/telegram_docs_raw/', filename)
                if not os.path.exists(filepath):
                    await message.download_media(file=filepath)
                meta['file_path'] = filepath
                meta['media_type'] = 'document'
                meta['file_size'] = message.document.size
                meta['mime_type'] = message.document.mime_type
            if meta['file_path']:
                all_results.append(meta)

    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('/Users/alexeykovalev/Desktop/urbicide_project/data/processed/Morskoy46/telegram_media_metadata.csv', index=False, encoding='utf-8-sig')
        print(f"\nScraping complete. {len(all_results)} files saved. Metadata in telegram_media_metadata.csv")
    else:
        print("\nScraping complete. No media files found.")

if __name__ == "__main__":
    if not all([API_ID, API_HASH, PHONE_NUMBER]):
        print("Error: API_ID, API_HASH, or PHONE_NUMBER not found in .env file.")
        print("Please create a .env file with your Telegram credentials.")
    else:
        asyncio.run(main())