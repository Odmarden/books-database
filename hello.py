import json 

import os

filnamn = "personer.json"
personer = []

if os.path.exists(filnamn):
    with open(filnamn, "r", encoding="utf-8") as fil:
        personer = json.load(fil)
    print(f"Hittade {len(personer)} tidigare registrerade personer.\n")

else:
    print("Ingen tidigare fil hittades. startar en ny lista.\n")

while True:
    antal_text = input("Hur många personer vill du registrera? ")
    try:
        antal = int(antal_text)
        if antal > 0:
            break
        else:
            print("Du måste registrera minst 1 person.")
    except ValueError:
        print("Ogiltigt svar. Skriv ett antal med siffror.")


for i in range(antal):
    print(f"\n--- Person {i+1} ---")
    namn = input("Namn: ")

    while True:
        år_text = input("Födelseår: ")
        try:
            år = int(år_text)
            ålder = 2025 - år
            break
        except ValueError:
            print("Skriv år med siffror!")

    ny_person = {"namn": namn, "ålder": ålder}
    personer.append(ny_person)

if personer:
    print("\n--- Nuvarande personer ---")
    for i, p in enumerate(personer):
        print(f"{i}: {p['namn']}")

    val = input("\nVill du ta bort någon? Skriv siffran, annars tryck Enter: ")
    if val.isdigit(): 
        index = int(val)
        if 0 <= index < len(personer):
            borttagen = personer.pop(index)
            print(f"Tog bort {borttagen['namn']}.")
        else:
            print("Felaktigt nummer.")    


with open("personer.json", "w", encoding="utf-8") as fil:
    json.dump(personer, fil, indent=4, ensure_ascii=False)
 
print("\nKvar i listan:", [p['namn'] for p in personer])

print("\nRegistrering klar! Här är listan:")

for p in personer:
    status = "myndig" if p['ålder'] >= 18 else "inte myndig"
    print(f"{p['namn']} är {p['ålder']} år gammal och är {status}.")
5
