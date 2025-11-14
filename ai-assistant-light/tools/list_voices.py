# tools/list_voices.py
import pyttsx3
e = pyttsx3.init()
for v in e.getProperty("voices"):
    print("ID:", v.id)
    print("Name:", getattr(v, "name", ""))
    print("Langs:", getattr(v, "languages", ""))
    print("-"*40)
