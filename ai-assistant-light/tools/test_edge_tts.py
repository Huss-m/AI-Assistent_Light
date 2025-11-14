# tools/test_edge_tts.py
import asyncio
import pygame
import time
import edge_tts

TEXT = "Hej! Jag heter AI-assistenten. Jag pratar svenska och det fungerar bra!"
VOICE = "sv-SE-MattiasNeural"
MP3_PATH = "test_svenska.mp3"

async def main():
    # Skapa och spara MP3-fil med svensk röst
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(MP3_PATH)
    print(f"✅ Ljudfil skapad: {MP3_PATH}")

    # Spela upp MP3 med pygame
    pygame.mixer.init()
    pygame.mixer.music.load(MP3_PATH)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
