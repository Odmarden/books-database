import json
import os

FILNAMN = "personer.json"
KATEGORIER = ["Familj", "Vän", "Jobb", "Övrigt"]
# Färgkoder
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m' # Denna nollställer färgen

def ladda_data():
    if os.path.exists(FILNAMN):
        try:
            with open(FILNAMN, "r", encoding="utf-8") as fil:
                return json.load(fil)
        except json.JSONDecodeError:
            print("Varning: Filen 'personer.json' är skadad. Startar med tom lista.")
            return []
    return []

def spara_data(lista):
    with open(FILNAMN, "w", encoding="utf-8") as fil:
        json.dump(lista, fil, indent=4, ensure_ascii=False)

def visa_personer(lista):
    print(f"\n{'ID':<4} {'Namn':<20} {'Ålder':<8} {'kategori':<15}")
    print("-" * 50)
    for p in lista:
        person_id = p.get('id', '??')
        kat = p.get('kategori', 'Ospecad')
        print(f"{person_id:<4} {p['namn']:<20} {p['ålder']:<8} {kat:<15}")

def filtrera_kategori(lista):
    # Använd välj_kategori() istället för input().capitalize()
    kategori = välj_kategori()
    matchningar = [p for p in lista if p.get('kategori') == kategori]

    if matchningar:
        visa_personer(matchningar)
    else:
        print(f"Hittade inga personer i kategorin '{kategori}'.")

def lägg_till_person(lista):
    namn = input("namn: ")
#    kat_input = input("Kategori (t ex familj, vän, jobb): ").capitalize()
    kategori = välj_kategori()

    if not lista:
        nästa_id = 1
    else:
        nästa_id = max(p['id'] for p in lista) + 1

    while True:
        år_text = input("Födelseår: ")
        try:
            år = int(år_text)
            ålder = 2025 - år
            ny_person = {
                "id": nästa_id,
                "namn": namn,
                "ålder": ålder,
                "kategori": kategori
            }

            lista.append(ny_person)
            spara_data(lista)
            print(f"{GREEN}{namn} har lagts till med ID: {nästa_id}!{END}")
            break
        except ValueError:
            print("{RED}Använd siffror för år.{END}")

def ta_bort_person(lista):
    visa_personer(lista)
    if not lista: return

    val = input("\nSkriv ID på den person du vill ta bort: ")
    if val.isdigit():
        id_att_ta_bort = int(val)
        
        person_att_radera = None
        for p in lista:
            if p['id'] == id_att_ta_bort:
                person_att_radera = p
                break
        
        if person_att_radera:
            lista.remove(person_att_radera)
            spara_data(lista)
            print(f"Tog bort {person_att_radera['namn']} (ID: {id_att_ta_bort}).")
        else:
            print("{RED}Hittade ingen person med det ID-numret.{END}")

def sök_person(lista):
    sökord = input("Sök efter namn: ").lower()
    resultat = [p for p in lista if sökord in p['namn'].lower()]

    print("\n--- SÖKRESULTAT ---")
    if resultat:
        for p in resultat:
            print(f"- {p['namn']} ({p['ålder']} år)")
    else:
        print("{RED}Ingen matchning hittades.{END}")

def välj_kategori():
    print("\nTillgängliga kategorier:")
    for i, kat in enumerate(KATEGORIER):
        print(f"{i + 1}. {kat}")
    
    while True:
        val = input("Välj kategori (nummer): ")
        if val.isdigit():
            idx = int(val) - 1
            if 0 <= idx < len(KATEGORIER):
                return KATEGORIER[idx]
        print(f"{RED}Ogiltigt val. Välj en siffra mellan 1 och {len(KATEGORIER)}.{END}")

def sortera_personer(lista):
    print("\nSorteras efter:")
    print("1. Namn (A-Ö)")
    print("2. Ålder (Yngst först)")
    print("3. Kategori (A-Ö)")
    val = input("Välj (1-3): ")

    if val == "1":
        lista.sort(key=lambda p: p['namn'].lower())
        print("Listan har sorterats efter namn.")

    elif val == "2":
        lista.sort(key=lambda p: p['ålder'])
        print("Listan har sorterats efter ålder.")

    elif val == "3":
        lista.sort(key=lambda p: p['kategori'])
        print("Listan har sorterats efter kategori.")

    spara_data(lista)

def redigera_person(lista):
    visa_personer(lista)
    val = input("\nAnge ID på den person du vill ändra (eller Enter för att avbryta): ")
    
    if not val.isdigit():
        return

    val_id = int(val)
    person = None
    
    # Hitta rätt person i listan
    for p in lista:
        if p.get('id') == val_id:
            person = p
            break
            
    if person:
        print(f"\nRedigerar {person['namn']}")
        print("1. Ändra namn")
        print("2. Ändra ålder")
        print("3. Ändra kategori")
        val_typ = input("Vad vill du ändra? (1-3): ")

        if val_typ == "1":
            nytt_namn = input(f"Nytt namn (nuvarande: {person['namn']}): ")
            if nytt_namn:
                person['namn'] = nytt_namn
        
        elif val_typ == "2":
            nytt_år = input("Nytt födelseår: ")
            if nytt_år.isdigit():
                person['ålder'] = 2025 - int(nytt_år)
        
        elif val_typ == "3":
            print(f"Nuvarande kategori: {person.get('kategori', 'Ospecad')}")
            ny_kat = välj_kategori()
            person['kategori'] = ny_kat
            spara_data(lista)
            print("Kategorin har uppdaterats!")

        spara_data(lista)
        print("Uppdateringen sparad!")
    else:
        print("Hittade ingen person med det ID-numret.")

def main():
    personer = ladda_data()

    try:
        while True:
            print("\n--- HUVUDMENY ---")
            print("1. Visa alla | 2. Lägg till | 3. Ta bort | 4. Sök | 5. Filtrera | 6. Sortera | 7. Redigera | 8. Avsluta")
            val = input("\nVälj (1-8): ")

            if val == "1":
                visa_personer(personer)
            elif val == "2":
                lägg_till_person(personer)
            elif val == "3":
                ta_bort_person(personer)
            elif val == "4":
                sök_person(personer)
            elif val == "5":
                filtrera_kategori(personer)
            elif val == "6":
                sortera_personer(personer)
            elif val == "7":
                redigera_person(personer)
            elif val == "8":
                print("Hejdå!")
                break
            else:
                print("Ogiltigt val.")

    except KeyboardInterrupt:
        print("\nProgrammet avslutat.")

if __name__ == "__main__":
    main()