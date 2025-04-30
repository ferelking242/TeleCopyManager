from pyrogram import Client
import asyncio

api_id = 23636020
api_hash = "22b5c8faf8e35cfd5833aad8374eb652"

# Canaux
source_channel = "ferelking1"
target_channel = "ferelking2"

app = Client("session_copie", api_id=api_id, api_hash=api_hash)

async def copier_anciens_messages():
    async with app:
        messages = []
        async for message in app.get_chat_history(source_channel):
            messages.append(message)

        # Inverser la liste pour copier du plus ancien au plus récent
        messages.reverse()

        for message in messages:
            try:
                await app.copy_message(
                    chat_id=target_channel,
                    from_chat_id=source_channel,
                    message_id=message.id
                )
                print(f"✔️ Copié : {message.id}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Erreur {message.id} : {e}")

app.run(copier_anciens_messages())
