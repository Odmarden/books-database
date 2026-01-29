import json
import os

FILNAMN = "books.json"
KATEGORIER = ["Skönlitteratur inrikes", "Skönlitteratur utrikes", "Facklitteratur", "Övrigt"]
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
            print("Varning: Filen 'books.json' är skadad. Startar med tom lista.")
            return []
    return []

def spara_data(lista):
    with open(FILNAMN, "w", encoding="utf-8") as fil:
        json.dump(lista, fil, indent=4, ensure_ascii=False)

def visa_böcker(lista):
    print(f"\n{'ID':<4} {'titel':<80} {'författare':<60} {'Kategori':<30}")
    print("-" * 174)
    for p in lista:
        bok_id = p.get('id', '??')
        kat = p.get('kategori', 'Ospecad')
        print(f"{bok_id:<4} {p['titel']:<80} {p['författare']:<60} {kat:<30}")

def filtrera_kategori(lista):
    # Använd välj_kategori() istället för input().capitalize()
    kategori = välj_kategori()
    matchningar = [p for p in lista if p.get('kategori') == kategori]

    if matchningar:
        visa_böcker(matchningar)
    else:
        print(f"Hittade inga böcker i kategorin '{kategori}'.")

def lägg_till_bok(lista):
    titel = input("titel: ")
    kategori = välj_kategori()
    författare = input("författare: ")

    if not lista:
        nästa_id = 1
    else:
        nästa_id = max(p['id'] for p in lista) + 1

    ny_bok = {
        "id": nästa_id,
        "titel": titel,
        "författare": författare,
        "kategori": kategori
    }

    lista.append(ny_bok)
    spara_data(lista)
    print(f"{GREEN}{titel} har lagts till med ID: {nästa_id}!{END}")
            

def ta_bort_bok(lista):
    visa_böcker(lista)
    if not lista: return

    val = input("\nSkriv ID på den bok du vill ta bort: ")
    if val.isdigit():
        id_att_ta_bort = int(val)
        
        bok_att_radera = None
        for p in lista:
            if p['id'] == id_att_ta_bort:
                bok_att_radera = p
                break
        
        if bok_att_radera:
            lista.remove(bok_att_radera)
            spara_data(lista)
            # .get('titel', 'Okänd titel') hämtar titeln, 
# men om den saknas (KeyError) skriver den 'Okänd titel' istället.
            print(f"Tog bort {bok_att_radera.get('titel', 'Okänd titel')} (ID: {id_att_ta_bort}).")
        else:
            print("{RED}Hittade ingen bok med det ID-numret.{END}")

def sök_bok(lista):
    sökord = input("Sök efter titel: ").lower()
    resultat = [p for p in lista if sökord in p['titel'].lower()]

    print("\n--- SÖKRESULTAT ---")
    if resultat:
        for p in resultat:
            print(f"- {p['titel']} {p['författare']}")
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

def sortera_böcker(lista):
    print("\nSorteras efter:")
    print("1. Titel (A-Ö)")
    print("2. Författare (A-Ö)")
    print("3. Kategori (A-Ö)")
    val = input("Välj (1-3): ")

    if val == "1":
        lista.sort(key=lambda p: p['titel'].lower())
        print("Listan har sorterats efter titel.")

    elif val == "2":
        lista.sort(key=lambda p: p['författare'])
        print("Listan har sorterats efter författare.")

    elif val == "3":
        lista.sort(key=lambda p: p['kategori'])
        print("Listan har sorterats efter kategori.")

    spara_data(lista)

def redigera_bok(lista):
    visa_böcker(lista)
    val = input("\nAnge ID på den bok du vill ändra (eller Enter för att avbryta): ")
    
    if not val.isdigit():
        return

    val_id = int(val)
    bok = None
    
    # Hitta rätt bok i listan
    for p in lista:
        if p.get('id') == val_id:
            bok = p
            break
            
    if bok:
        print(f"\nRedigerar {bok['titel']}")
        print("1. Ändra titel")
        print("2. Ändra författare")
        print("3. Ändra kategori")
        val_typ = input("Vad vill du ändra? (1-3): ")

        if val_typ == "1":
            ny_titel = input(f"Ny titel (nuvarande: {bok['titel']}): ")
            if ny_titel:
                bok['titel'] = ny_titel
        
        elif val_typ == "2":
            ny_författare= input(f"Ny författare (nuvarande: {bok['författare']}): ")
            if ny_författare:
                bok['författare'] = ny_författare
        
        elif val_typ == "3":
            print(f"Nuvarande kategori: {bok.get('kategori', 'Ospecad')}")
            ny_kat = välj_kategori()
            bok['kategori'] = ny_kat
            spara_data(lista)
            print("Kategorin har uppdaterats!")

        spara_data(lista)
        print("Uppdateringen sparad!")
    else:
        print("Hittade ingen bok med det ID-numret.")

def main():
    böcker = ladda_data()

    try:
        while True:
            print("\n--- HUVUDMENY ---")
            print("1. Visa alla | 2. Lägg till | 3. Ta bort | 4. Sök | 5. Filtrera | 6. Sortera | 7. Redigera | 8. Avsluta")
            val = input("\nVälj (1-8): ")

            if val == "1":
                visa_böcker(böcker)
            elif val == "2":
                lägg_till_bok(böcker)
            elif val == "3":
                ta_bort_bok(böcker)
            elif val == "4":
                sök_bok(böcker)
            elif val == "5":
                filtrera_kategori(böcker)
            elif val == "6":
                sortera_böcker(böcker)
            elif val == "7":
                redigera_bok(böcker)
            elif val == "8":
                print("Hejdå!")
                break
            else:
                print("Ogiltigt val.")

    except KeyboardInterrupt:
        print("\nProgrammet avslutat.")

if __name__ == "__main__":
    main()