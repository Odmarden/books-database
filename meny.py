import json
import os

filnamn = "personer.json"

def ladda_data():
    if os.path.exists(filnamn):
        with open(filnamn, "r", encoding="utf-8") as fil:
            return json.load(fil)
        
    return []

def spara_data(lista):
    with open(filnamn, "w", encoding="utf-8") as fil:
        json.dump(lista, fil, indent=4, ensure_ascii=False)

personer = ladda_data()

try:

    while True:
        print("\n--- HUVUDMENY ---")
        print("1. Visa alla personer")
        print("2. Lägg till en person")
        print("3. Ta bort person")
        print("4. Sök efter person")
        print("5. Avsluta")

        val = input("\nVälj ett alternativ (1-5): ")

        if val == "1":
            print("\n--- ALLA REGISTRERADE ---")
            if not personer:
                print("Listan är tom")
            for i, p in enumerate(personer):
                print(f"{i}. {p['namn']} ({p['ålder']} år)")

        elif val == "2":
            namn = input("Namn: ")
            while True:
                år_text = input("Födelseår: ")
                try:
                    år = int(år_text)
                    personer.append({"namn": namn, "ålder": 2025 - år})
                    spara_data(personer)
                    print(f"{namn} harlagts till!")
                    break
                except ValueError:
                    print("Använd siffror för år.")

        elif val == "3":
            if not personer:
                print("Ingen att ta bort.")
                continue
            for i, p in enumerate(personer):
                print(f"{i}. {p['namn']}")

            val_ta_bort = input("Vilket nummer vill du ta bort? ")
            if val_ta_bort.isdigit():
                idx = int(val_ta_bort)
                if 0 <= idx < len(personer):
                    borttagen = personer.pop(idx)
                    spara_data(personer)
                    print(f"Tog bort {borttagen['namn']}.")
                else:
                    print("Ogiltigt nummer.")

        elif val == "4":
            sökord = input("Skriv namnet du letar efter: ").lower()
            hittade_personer = []

            for p in personer:
                if sökord in p['namn'].lower():
                    hittade_personer.append(p)

            print("\n--- SÖKRESULTAT ---")
            if hittade_personer:
                for p in hittade_personer:
                    print(f"- {p['namn']} ({p['ålder']} år)")
            else:
                print("Ingen matchning hittades.")

        elif val == "5":
            print("Hejdå!")
            break

        else:
            print("Ogiltigt val, försök igen.")

except KeyboardInterrupt:
    print("\nProgrammet avslutades med Ctrl+C. Hejdå!")