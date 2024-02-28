# make sure that espeak is install on your system
# sudo apt install espeak

import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')

# Shows all tts voices installed on you system
for i in voices:
    print(i)
    print(i.id)

engine.setProperty('voice', 'german')
engine.setProperty('rate', 170)

engine.say('was ist das für eine roboter stimme')

engine.runAndWait()