import sqlite3
import csv
import shutil
from datetime import datetime
import os

# Inställningar
DB_NAMN = "bibliotek.db"
KATEGORIER = ["Skönlitteratur", "Facklitteratur", "Biografi", "Övrigt", "Lyrik", "Dramatik", "Filosofi", "Teologi", "Matlagning", "Barn"]

# Färger för terminalen
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def initiera_databas():
    """Skapar databasen och tabellerna om de inte finns."""
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bocker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titel TEXT NOT NULL,
            forfattare TEXT NOT NULL,
            kategori TEXT,
            tryckaar INTEGER,
            forlag TEXT,
            thumbnail TEXT
        )
    ''')
    
    # Check if new columns exist, if not add them (migration for existing databases)
    cursor.execute("PRAGMA table_info(bocker)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'tryckaar' not in columns:
        cursor.execute('ALTER TABLE bocker ADD COLUMN tryckaar INTEGER')
    if 'forlag' not in columns:
        cursor.execute('ALTER TABLE bocker ADD COLUMN forlag TEXT')
    if 'thumbnail' not in columns:
        cursor.execute('ALTER TABLE bocker ADD COLUMN thumbnail TEXT')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referenser (
            bok_id INTEGER,
            ref_id INTEGER,
            PRIMARY KEY (bok_id, ref_id),
            FOREIGN KEY (bok_id) REFERENCES bocker(id) ON DELETE CASCADE,
            FOREIGN KEY (ref_id) REFERENCES bocker(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
def backup_databas():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    source_db = 'bibliotek.db'
    backup_db = f'backups/bibliotek_backup_{timestamp}.db'
    
    try:
        # Skapa anslutning till källan
        src = sqlite3.connect(source_db)
        # Skapa anslutning till backup-filen
        dst = sqlite3.connect(backup_db)
        
        # Använd SQLites inbyggda backup-API
        with dst:
            src.backup(dst)
        
        dst.close()
        src.close()
        print(f"Backup sparad: {backup_db}")
    except Exception as e:
        print(f"Backup misslyckades: {e}")

def hämta_referens_titlar(bok_id):
    """Hjälpfunktion för att visa länkade titlar i terminalen."""
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b.titel FROM bocker b
        JOIN referenser r ON b.id = r.ref_id
        WHERE r.bok_id = ?
    ''', (bok_id,))
    titlar = [rad[0] for rad in cursor.fetchall()]
    conn.close()
    return ", ".join(titlar) if titlar else "-"

def välj_kategori():
    print("\nTillgängliga kategorier:")
    for i, kat in enumerate(KATEGORIER):
        print(f"{i + 1}. {kat}")
    while True:
        val = input("Välj kategori (nummer): ")
        if val.isdigit() and 0 < int(val) <= len(KATEGORIER):
            return KATEGORIER[int(val) - 1]
        print(f"{RED}Ogiltigt val.{END}")


def validera_tryckaar(tryckaar_str):
    """Validerar att tryckår är ett 4-siffrigt heltal mellan 1000 och nuvarande år."""
    if not tryckaar_str.strip():  # Tom sträng är OK (optional)
        return None
    
    current_year = datetime.now().year
    try:
        year = int(tryckaar_str)
        if 1000 <= year <= current_year:
            return year
        else:
            print(f"{RED}Tryckår måste vara mellan 1000 och {current_year}.{END}")
            return False
    except ValueError:
        print(f"{RED}Tryckår måste vara ett heltal.{END}")
        return False

def hantera_thumbnail(thumbnail_path):
    """Hanterar thumbnail-filen genom att kopiera den till thumbnails-mappen."""
    if not thumbnail_path.strip():
        return "thumbnails/placeholder.svg"  # Default placeholder
    
    if not os.path.exists(thumbnail_path):
        print(f"{RED}Filen {thumbnail_path} finns inte.{END}")
        return None
    
    # Skapa unikt filnamn baserat på timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(thumbnail_path)[1]
    new_filename = f"thumb_{timestamp}{file_extension}"
    new_path = os.path.join("thumbnails", new_filename)
    
    try:
        shutil.copy2(thumbnail_path, new_path)
        print(f"{GREEN}Thumbnail sparad som {new_path}{END}")
        return new_path
    except Exception as e:
        print(f"{RED}Fel vid kopiering av thumbnail: {e}{END}")
        return None

# --- MENYFUNKTIONER (1-11) ---

def visa_böcker():
    print(f"\n{BOLD}Sortera efter: 1. Titel | 2. Författare | 3. ID (Nyast) | 4. Tryckår{END}")
    val = input("Välj: ")
    order = "titel ASC"
    if val == "2": order = "forfattare ASC"
    elif val == "3": order = "id DESC"
    elif val == "4": order = "tryckaar DESC NULLS LAST"

    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM bocker ORDER BY {order}")
    rader = cursor.fetchall()
    
    print(f"\n{BLUE}{'ID':<4} {'Titel':<25} {'Författare':<20} {'År':<6} {'Förlag':<15} {'Kategori':<12} {'Referenser'}{END}")
    print("-" * 120)
    for rad in rader:
        # Hantera den nya datastrukturen: id, titel, forfattare, kategori, tryckaar, forlag, thumbnail
        id_val = rad[0]
        titel = rad[1][:23] if rad[1] else ""
        forfattare = rad[2][:18] if rad[2] else ""
        kategori = rad[3][:10] if rad[3] else ""
        tryckaar = str(rad[4]) if rad[4] else ""
        forlag = rad[5][:13] if rad[5] else ""
        refs = hämta_referens_titlar(id_val)
        
        print(f"{id_val:<4} {titel:<25} {forfattare:<20} {tryckaar:<6} {forlag:<15} {kategori:<12} {refs}")
    conn.close()


def lägg_till_bok():
    titel = input("Titel: ")
    forfattare = input("Författare: ")
    kategori = välj_kategori()
    
    # Hantera tryckår
    tryckaar = None
    while True:
        tryckaar_input = input("Tryckår (valfritt, tryck Enter för att hoppa över): ")
        if not tryckaar_input.strip():  # Tom input - hoppa över
            break
        validation_result = validera_tryckaar(tryckaar_input)
        if validation_result is not False:  # None eller giltigt år
            tryckaar = validation_result
            break
    
    # Hantera förlag
    forlag = input("Förlag (valfritt): ")
    if not forlag.strip():
        forlag = None
    
    # Hantera thumbnail
    thumbnail = None
    while True:
        thumbnail_input = input("Thumbnail-sökväg (valfritt, tryck Enter för standardbild): ")
        thumbnail_result = hantera_thumbnail(thumbnail_input)
        if thumbnail_result is not None:
            thumbnail = thumbnail_result
            break
        elif not thumbnail_input.strip():  # Tom input accepteras
            thumbnail = "thumbnails/placeholder.svg"
            break
        # Annars försök igen
    
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bocker (titel, forfattare, kategori, tryckaar, forlag, thumbnail) VALUES (?, ?, ?, ?, ?, ?)', 
                   (titel, forfattare, kategori, tryckaar, forlag, thumbnail))
    conn.commit()
    conn.close()
    print(f"{GREEN}Boken sparad!{END}")


def ta_bort_bok():
    val = input("\nAnge ID på boken du vill ta bort: ")
    if val.isdigit():
        conn = sqlite3.connect(DB_NAMN)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("SELECT titel FROM bocker WHERE id = ?", (val,))
        res = cursor.fetchone()
        if res:
            cursor.execute("DELETE FROM bocker WHERE id = ?", (val,))
            conn.commit()
            print(f"{RED}Tog bort '{res[0]}' och dess kopplingar.{END}")
        else:
            print(f"{RED}ID hittades inte.{END}")
        conn.close()

def sök_bok():
    sord = input("Sökord: ")
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bocker WHERE titel LIKE ? OR forfattare LIKE ?", (f"%{sord}%", f"%{sord}%"))
    rader = cursor.fetchall()
    if rader:
        for rad in rader:
            refs = hämta_referens_titlar(rad[0])
            print(f"{GREEN}Hittad: {rad[1]} av {rad[2]} (ID: {rad[0]}) - Ref: {refs}{END}")
    else:
        print(f"{RED}Inga matchningar.{END}")
    conn.close()

def redigera_bok():
    vid = input("\nAnge ID på boken du vill ändra: ")
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bocker WHERE id = ?", (vid,))
    bok = cursor.fetchone()
    if bok:
        print("1. Ändra titel | 2. Ändra författare | 3. Ändra kategori | 4. Ändra tryckår | 5. Ändra förlag | 6. Ändra thumbnail")
        val = input("Välj: ")
        if val == "1":
            cursor.execute("UPDATE bocker SET titel = ? WHERE id = ?", (input("Ny titel: "), vid))
        elif val == "2":
            cursor.execute("UPDATE bocker SET forfattare = ? WHERE id = ?", (input("Ny författare: "), vid))
        elif val == "3":
            cursor.execute("UPDATE bocker SET kategori = ? WHERE id = ?", (välj_kategori(), vid))
        elif val == "4":
            while True:
                tryckaar_input = input("Nytt tryckår (lämna tomt för att ta bort): ")
                if not tryckaar_input.strip():
                    cursor.execute("UPDATE bocker SET tryckaar = ? WHERE id = ?", (None, vid))
                    break
                validation_result = validera_tryckaar(tryckaar_input)
                if validation_result is not False:
                    cursor.execute("UPDATE bocker SET tryckaar = ? WHERE id = ?", (validation_result, vid))
                    break
        elif val == "5":
            forlag = input("Nytt förlag (lämna tomt för att ta bort): ")
            cursor.execute("UPDATE bocker SET forlag = ? WHERE id = ?", (forlag if forlag.strip() else None, vid))
        elif val == "6":
            while True:
                thumbnail_input = input("Ny thumbnail-sökväg (lämna tomt för standardbild): ")
                thumbnail_result = hantera_thumbnail(thumbnail_input)
                if thumbnail_result is not None:
                    cursor.execute("UPDATE bocker SET thumbnail = ? WHERE id = ?", (thumbnail_result, vid))
                    break
                elif not thumbnail_input.strip():
                    cursor.execute("UPDATE bocker SET thumbnail = ? WHERE id = ?", ("thumbnails/placeholder.svg", vid))
                    break
        conn.commit()
        print(f"{GREEN}Uppdaterat!{END}")
    conn.close()


def visa_statistik():
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('SELECT kategori, COUNT(*) FROM bocker GROUP BY kategori ORDER BY COUNT(*) DESC')
    rader = cursor.fetchall()
    print(f"\n{BOLD}--- STATISTIK ---{END}")
    for rad in rader:
        print(f"{rad[0]:<20} {rad[1]} st")
    conn.close()

def exportera_till_csv():
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bocker")
    rader = cursor.fetchall()
    with open("bibliotek_export.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["ID", "Titel", "Författare", "Kategori", "Tryckår", "Förlag", "Thumbnail"])
        writer.writerows(rader)
    conn.close()
    print(f"{GREEN}Export klar till 'bibliotek_export.csv'{END}")


def koppla_bocker():
    id1, id2 = input("ID för bok 1: "), input("ID för bok 2: ")
    if id1.isdigit() and id2.isdigit():
        conn = sqlite3.connect(DB_NAMN)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO referenser VALUES (?, ?)", (id1, id2))
            cursor.execute("INSERT INTO referenser VALUES (?, ?)", (id2, id1))
            conn.commit()
            print(f"{GREEN}Böckerna är nu länkade!{END}")
        except:
            print(f"{RED}Kunde inte länka. Kontrollera att ID:n finns och inte redan är länkade.{END}")
        conn.close()

def ta_bort_koppling():
    """Borttagning med KONTROLLFRÅGA"""
    id1, id2 = input("ID 1: "), input("ID 2: ")
    if id1.isdigit() and id2.isdigit():
        conn = sqlite3.connect(DB_NAMN)
        cursor = conn.cursor()
        cursor.execute("SELECT id, titel FROM bocker WHERE id IN (?, ?)", (id1, id2))
        böcker = dict(cursor.fetchall())
        
        if len(böcker) == 2:
            print(f"\n{BOLD}Vill du ta bort länken mellan:{END}")
            print(f"'{böcker[int(id1)]}' och '{böcker[int(id2)]}'?")
            if input("Bekräfta med 'j': ").lower() == 'j':
                cursor.execute("DELETE FROM referenser WHERE (bok_id=? AND ref_id=?) OR (bok_id=? AND ref_id=?)", (id1, id2, id2, id1))
                conn.commit()
                print(f"{GREEN}Kopplingen raderad.{END}")
            else:
                print("Åtgärden avbruten.")
        else:
            print(f"{RED}Kunde inte hitta båda ID-numren.{END}")
        conn.close()

def visa_alla_kopplingar():
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT b1.titel, b2.titel FROM referenser r
        JOIN bocker b1 ON r.bok_id = b1.id
        JOIN bocker b2 ON r.ref_id = b2.id
        WHERE r.bok_id < r.ref_id
    ''')
    rader = cursor.fetchall()
    print(f"\n{BOLD}--- EXISTERANDE KORSREFERENSER ---{END}")
    if not rader: print("Inga kopplingar hittades.")
    for rad in rader:
        print(f"{rad[0]} <---> {rad[1]}")
    conn.close()

# --- MAIN ---

def main():
    initiera_databas()
    while True:
        print(f"\n{BOLD}{BLUE}--- SQL BOKREGISTER ---{END}")
        print("1. Visa | 2. Lägg till | 3. Ta bort bok | 4. Sök | 5. Redigera")
        print("6. Statistik | 7. Exportera | 8. Länka (Ref) | 9. Ta bort länk | 10. Visa länkar | 11. Avsluta")
        val = input("\nVälj (1-11): ")

        if val == "1": visa_böcker()
        elif val == "2": lägg_till_bok()
        elif val == "3": ta_bort_bok()
        elif val == "4": sök_bok()
        elif val == "5": redigera_bok()
        elif val == "6": visa_statistik()
        elif val == "7": exportera_till_csv()
        elif val == "8": koppla_bocker()
        elif val == "9": ta_bort_koppling()
        elif val == "10": visa_alla_kopplingar()
        elif val == "11": break

if __name__ == "__main__":
    main()
