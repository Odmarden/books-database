import json
import sqlite3
import os

# Inställningar
JSON_FIL = "books.json"
DB_NAMN = "bibliotek.db"

def kör_konvertering():
    # 1. Kontrollera att JSON-filen finns
    if not os.path.exists(JSON_FIL):
        print(f"Fel: Hittade inte {JSON_FIL}")
        return

    # 2. Översättningsmall (Gammal: Ny)
    kategori_karta = {
        "Skönlitteratur inrikes": "Skönlitteratur",
        "Skönlitteratur utrikes": "Skönlitteratur",
        "Facklitteratur": "Facklitteratur",
        "Övrigt": "Övrigt"
    }

    try:
        with open(JSON_FIL, "r", encoding="utf-8") as fil:
            gamla_böcker = json.load(fil)

        conn = sqlite3.connect(DB_NAMN)
        cursor = conn.cursor()

        # Rensa tabellen först om du vill börja helt rent (valfritt)
        # cursor.execute("DELETE FROM bocker")

        antal = 0
        for bok in gamla_böcker:
            # Hanterar både stort och litet T/F från din tidigare JSON-resa
            titel = bok.get('Titel') or bok.get('titel')
            författare = bok.get('Författare') or bok.get('författare')
            gammal_kat = bok.get('kategori', 'Övrigt')
            
            # Här sker själva konverteringen av kategorin
            ny_kat = kategori_karta.get(gammal_kat, "Övrigt")

            if titel and författare:
                cursor.execute('''
                    INSERT INTO bocker (titel, forfattare, kategori)
                    VALUES (?, ?, ?)
                ''', (titel, författare, ny_kat))
                antal += 1

        conn.commit()
        conn.close()
        print(f"Succé! {antal} böcker har flyttats och kategorierna har städats.")

    except Exception as e:
        print(f"Något gick fel: {e}")

if __name__ == "__main__":
    kör_konvertering()