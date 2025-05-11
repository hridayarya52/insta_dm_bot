from instagrapi import Client
from transformers import pipeline
from gtts import gTTS
from pydub import AudioSegment
import os
import time
import random

USERNAME = "your_username"
PASSWORD = "your_password"

cl = Client()

if os.path.exists("settings.json"):
    cl.load_settings("settings.json")

try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("settings.json")
except Exception as e:
    print("Login failed, check credentials or 2FA code:", e)
    exit()

generator = pipeline("text-generation", model="ai-forever/rugpt3small_based_on_gpt2")

keyword_responses = {
    "hello": "Hello jaan 😘, kya haal hai?",
    "kya kar rahi ho": "Bas aapke baare me soch rahi hoon ❤️",
    "tum kaun ho": "Main tumhari AI wali crush hoon 😚"
}

def greet_user(username):
    return f"Namaste {username}, main hoon tumhari flirty AI bot ❤️"

def generate_voice(text, filename="voice.mp3"):
    tts = gTTS(text=text, lang='hi')
    tts.save(filename)
    sound = AudioSegment.from_mp3(filename)
    sound.export("voice.aac", format="aac")
    return "voice.aac"

def get_random_image():
    img_dir = "images"
    return os.path.join(img_dir, random.choice(os.listdir(img_dir)))

last_checked = {}

while True:
    threads = cl.direct_threads()
    for thread in threads:
        if not thread.messages:
            continue

        message = thread.messages[0]
        user_id = message.user_id
        username = cl.user_info(user_id).username
        msg_id = message.id
        text = message.text.strip().lower()

        if msg_id == last_checked.get(thread.id):
            continue

        print(f"{username}: {text}")
        last_checked[thread.id] = msg_id

        response = None
        for keyword in keyword_responses:
            if keyword in text:
                response = keyword_responses[keyword]
                break

        if not response:
            prompt = f"एक लड़की से ऐसे बात करो जैसे वो शरमिली हो {text}"
            ai_reply = generator(prompt, max_length=50, do_sample=True)[0]["generated_text"]
            response = ai_reply.split(":")[-1].strip()

        greeting = greet_user(username)
        cl.direct_send(greeting, [user_id])
        cl.direct_send(response, [user_id])
        voice_file = generate_voice(response)
        cl.direct_send_voice(voice_file, [user_id])
        image_path = get_random_image()
        cl.direct_send_photo(image_path, [user_id])

    time.sleep(10)
