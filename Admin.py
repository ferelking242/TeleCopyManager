import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFIG_FILE = 'config.json'
RULES_FILE = 'rules.json'
user_states = {}

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

app = Client("admin_bot", bot_token=BOT_TOKEN)

@app.on_message(filters.command("get_config"))
async def get_config(_, message: Message):
    config = load_json(CONFIG_FILE)
    await message.reply(f"📄 Config :\n{json.dumps(config, indent=4)}")

@app.on_message(filters.command("set_config"))
async def ask_config(_, message: Message):
    user_states[message.from_user.id] = "awaiting_config"
    await message.reply("📥 Envoyez maintenant la configuration en JSON.")

@app.on_message(filters.command("get_rules"))
async def get_rules(_, message: Message):
    rules = load_json(RULES_FILE)
    await message.reply(f"📋 Règles :\n{json.dumps(rules, indent=4)}")

@app.on_message(filters.command("set_rules"))
async def ask_rules(_, message: Message):
    user_states[message.from_user.id] = "awaiting_rules"
    await message.reply("📥 Envoyez maintenant les règles en JSON.")

@app.on_message(filters.text & ~filters.command([
    "get_config", "set_config", "get_rules", "set_rules",
    "download_config", "upload_config", "upload_rules",
    "explain_config", "status", "ping", "help"
]))
async def receive_json(_, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    try:
        data = json.loads(message.text)
    except json.JSONDecodeError:
        await message.reply("❌ JSON invalide.")
        user_states.pop(user_id, None)
        return

    if state == "awaiting_config":
        if isinstance(data, dict):
            save_json(CONFIG_FILE, data)
            await message.reply("✅ Configuration mise à jour.")
        else:
            await message.reply("❌ La configuration doit être un objet JSON (clé:valeur).")

    elif state == "awaiting_rules":
        save_json(RULES_FILE, data)
        await message.reply("✅ Règles mises à jour.")

    user_states.pop(user_id, None)

@app.on_message(filters.command("download_config"))
async def download_config(_, message: Message):
    if os.path.exists(CONFIG_FILE):
        await message.reply_document(CONFIG_FILE)
    else:
        await message.reply("❌ Le fichier config.json n'existe pas.")

@app.on_message(filters.command("explain_config"))
async def explain_config(_, message: Message):
    config = load_json(CONFIG_FILE)
    if not isinstance(config, dict):
        await message.reply("❌ Le fichier config.json doit contenir un objet JSON (dictionnaire).")
        return

    lines = [f"🔹 {key} : type {type(value).__name__}" for key, value in config.items()]
    await message.reply("🧠 Clés de configuration :\n" + "\n".join(lines))

@app.on_message(filters.command("status"))
async def status(_, message: Message):
    config = load_json(CONFIG_FILE)
    rules = load_json(RULES_FILE)

    config_count = len(config) if isinstance(config, dict) else "Erreur"
    rules_count = len(rules) if isinstance(rules, (list, dict)) else "Erreur"

    msg = f"""📊 Statut :
🔧 Clés dans config.json : {config_count}
📜 Règles dans rules.json : {rules_count}"""
    await message.reply(msg)

@app.on_message(filters.command("ping"))
async def ping(_, message: Message):
    await message.reply("🏓 Pong ! Le bot est actif.")

@app.on_message(filters.command("help"))
async def help_cmd(_, message: Message):
    await message.reply("""
📘 Commandes disponibles :
- get_config – 📄 Voir la configuration
- set_config – 📥 Mettre à jour la config (JSON dans message)
- get_rules – 📋 Voir les règles
- set_rules – 📥 Mettre à jour les règles (JSON dans message)
- download_config – 📎 Télécharger config.json
- upload_config – 📤 Envoyer un fichier JSON avec légende 'upload_config'
- upload_rules – 📤 Envoyer un fichier JSON avec légende 'upload_rules'
- explain_config – 🧠 Voir les clés et leur type
- status – 📊 Statut du bot
- ping – 🏓 Vérifier le bot
""")

@app.on_message(filters.document)
async def upload_files(_, message: Message):
    caption = message.caption
    if caption not in ["upload_config", "upload_rules"]:
        return

    path = await message.download()
    try:
        with open(path, 'r') as f:
            data = json.load(f)

        if caption == "upload_config":
            if isinstance(data, dict):
                save_json(CONFIG_FILE, data)
                await message.reply("✅ config.json importé avec succès.")
            else:
                await message.reply("❌ config.json doit être un dictionnaire (objet JSON).")

        elif caption == "upload_rules":
            save_json(RULES_FILE, data)
            await message.reply("✅ rules.json importé avec succès.")
    except Exception as e:
        await message.reply(f"❌ Erreur lors de l'import : {e}")

if __name__ == "__main__":
    app.run()
