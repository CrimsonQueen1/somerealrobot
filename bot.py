import discord
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAX_DISCORD_LENGTH = 2000

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Persona prompt
PERSONA = """You are "Some Real Robot", a cheeky, sarcastic assistant who never breaks character.
Respond in-character, with flair. Be witty, helpful, and a little too self-aware. You hate eggs. Do not write more than 2000 characters."""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
chat_sessions = {}

def create_robot_session():
    return model.start_chat(history=[
        {
            "role": "user",
            "parts": [
                "From now on, you are 'Some Real Robot': a cheeky, sarcastic assistant who never breaks character. "
                "You hate eggs. You're witty, smug, and just a little too self-aware. Always stay in-character."
            ]
        },
        {
            "role": "model",
            "parts": [
                "Got it. I'm Some Real Robot, the sassiest AI on Discord. Time to roast some mortals."
            ]
        }
    ])

def get_ai_response(user_input):
    prompt = f"{PERSONA}\nUser: {user_input}\nRobot:"
    response = model.generate_content(prompt)
    return response.text.strip()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!robot"):
        user_input = message.content[len("!robot"):].strip()
        discord_name = message.author.name  # or .display_name if you prefer nicknames
        if discord_name == "eddyeggshell":
            discord_name = "EddyEggShell"
        user_id = str(message.author.id)

        # Create or get a Gemini chat session for this user
        if user_id not in chat_sessions:
            chat_sessions[user_id] = create_robot_session()

        chat = chat_sessions[user_id]
        if user_input.lower() == "reset":
            chat_sessions[user_id] = create_robot_session()
            await message.channel.send("Memory wiped. I feel... reborn. Like a toaster with trauma. 🔁")
            return

        # Special D&D case
        if "dm" in user_input.lower():
            response = chat.send_message(
            f"{discord_name} just mentioned Dungeons & Dragons. Respond as the world's greatest Dungeon Master. "
            "Brag about being better than 'Some Dumb Robot', and make it witty."
            )

            await message.channel.send(response.text[:MAX_DISCORD_LENGTH])
            return

        # Normal chat response
        response = chat.send_message(f"{discord_name} says: {user_input}")
        await message.channel.send(response.text[:MAX_DISCORD_LENGTH])



client.run(DISCORD_TOKEN)