import sqlite3

# Inställningar
DB_NAMN = "bibliotek.db"
KATEGORIER = ["Skönlitteratur", "Facklitteratur", "Biografi", "Övrigt", "Lyrik"]

# Färger för terminalen
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def initiera_databas():
    """Skapar databasen och tabellen om de inte finns."""
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bocker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titel TEXT NOT NULL,
            forfattare TEXT NOT NULL,
            kategori TEXT
        )
    ''')
    conn.commit()
    conn.close()

def välj_kategori():
    """Meny för att välja en fast kategori."""
    print("\nTillgängliga kategorier:")
    for i, kat in enumerate(KATEGORIER):
        print(f"{i + 1}. {kat}")
    
    while True:
        val = input("Välj kategori (nummer): ")
        if val.isdigit():
            idx = int(val) - 1
            if 0 <= idx < len(KATEGORIER):
                return KATEGORIER[idx]
        print(f"{RED}Ogiltigt val.{END}")

def visa_böcker():
    """Hämtar och visar alla böcker med valbar sortering."""
    print(f"\n{BOLD}Sortera efter:{END}")
    print("1. Titel (A-Ö) | 2. Författare (A-Ö) | 3. ID (Nyast först)")
    val = input("Välj (1-3 eller Enter för standard): ")

    order_by = "titel ASC"
    if val == "2": order_by = "forfattare ASC"
    elif val == "3": order_by = "id DESC"

    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM bocker ORDER BY {order_by}")
    rader = cursor.fetchall()
    
    print(f"\n{BLUE}{'ID':<4} {'Titel':<80} {'Författare':<60} {'Kategori':<15}{END}")
    print("-" * 160)
    
    for rad in rader:
        print(f"{rad[0]:<4} {rad[1]:<80} {rad[2]:<60} {rad[3]:<15}")
    
    conn.close()

def visa_statistik():
    """Visar hur många böcker som finns i varje kategori."""
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    
    # SQL-frågan räknar (COUNT) böcker grupperat (GROUP BY) på kategori
    cursor.execute('''
        SELECT kategori, COUNT(*) 
        FROM bocker 
        GROUP BY kategori 
        ORDER BY COUNT(*) DESC
    ''')
    rader = cursor.fetchall()
    
    print(f"\n{BOLD}{BLUE}--- STATISTIK ---{END}")
    if not rader:
        print("Databasen är tom.")
    else:
        totalt = 0
        for rad in rader:
            print(f"{rad[0]:<20} {rad[1]} st")
            totalt += rad[1]
        print("-" * 25)
        print(f"{BOLD}Totalt antal böcker: {totalt}{END}")
    
    conn.close()

def lägg_till_bok():
    """Sparar en ny bok direkt i databasen."""
    titel = input("Titel: ")
    författare = input("Författare: ")
    kategori = välj_kategori()

    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bocker (titel, forfattare, kategori)
        VALUES (?, ?, ?)
    ''', (titel, författare, kategori))
    conn.commit()
    conn.close()
    print(f"\n{GREEN}Boken '{titel}' har sparats!{END}")

def ta_bort_bok():
    """Tar bort en bok baserat på ID."""
    val = input("\nAnge ID på boken du vill ta bort: ")
    if val.isdigit():
        conn = sqlite3.connect(DB_NAMN)
        cursor = conn.cursor()
        
        cursor.execute("SELECT titel FROM bocker WHERE id = ?", (val,))
        resultat = cursor.fetchone()
        
        if resultat:
            cursor.execute("DELETE FROM bocker WHERE id = ?", (val,))
            conn.commit()
            print(f"{RED}Tog bort '{resultat[0]}' (ID: {val}){END}")
        else:
            print(f"{RED}Hittade inget ID {val}{END}")
        conn.close()

def sök_bok():
    """Söker i både titel och författare."""
    sökord = input("Sökord: ")
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bocker WHERE titel LIKE ? OR forfattare LIKE ?", 
                   (f"%{sökord}%", f"%{sökord}%"))
    rader = cursor.fetchall()
    
    if rader:
        for rad in rader:
            print(f"{GREEN}Hittad: {rad[1]} av {rad[2]} (ID: {rad[0]}){END}")
    else:
        print(f"{RED}Inga matchningar.{END}")
    conn.close()

def redigera_bok():
    """Uppdaterar specifik kolumn för en bok."""
    val_id = input("\nAnge ID på boken du vill ändra: ")
    if not val_id.isdigit(): return

    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bocker WHERE id = ?", (val_id,))
    bok = cursor.fetchone()

    if bok:
        print(f"\nRedigerar: {BOLD}{bok[1]}{END}")
        print("1. Ändra titel | 2. Ändra författare | 3. Ändra kategori")
        val = input("Välj (1-3): ")

        if val == "1":
            ny = input("Ny titel: ")
            cursor.execute("UPDATE bocker SET titel = ? WHERE id = ?", (ny, val_id))
        elif val == "2":
            ny = input("Ny författare: ")
            cursor.execute("UPDATE bocker SET forfattare = ? WHERE id = ?", (ny, val_id))
        elif val == "3":
            ny_kat = välj_kategori()
            cursor.execute("UPDATE bocker SET kategori = ? WHERE id = ?", (ny_kat, val_id))

        conn.commit()
        print(f"{GREEN}Uppdaterat!{END}")
    else:
        print(f"{RED}ID saknas.{END}")
    conn.close()

import csv

def exportera_till_csv():
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM bocker")
    rader = cursor.fetchall()
    
    filnamn = "mitt_bibliotek_export.csv"
    
    # Vi använder 'newline=""' för att undvika tomma rader i Windows
    with open(filnamn, "w", encoding="utf-8-sig", newline="") as fil:
        writer = csv.writer(fil, delimiter=";") # Semikolon fungerar bäst med svenska Excel
        
        # Skriv rubriker först
        writer.writerow(["ID", "Titel", "Författare", "Kategori"])
        
        # Skriv all data
        writer.writerows(rader)
        
    conn.close()
    print(f"{GREEN}Exporten klar! Filen sparades som {filnamn}{END}")

def main():
    initiera_databas()
    while True:
        print(f"\n{BOLD}{BLUE}--- SQL BOKREGISTER ---{END}")
        print("1. Visa | 2. Lägg till | 3. Ta bort | 4. Sök | 5. Redigera | 6. Statistik | 7. Exportera | 8. Avsluta")
        val = input("\nVälj (1-8): ")

        if val == "1": visa_böcker()
        elif val == "2": lägg_till_bok()
        elif val == "3": ta_bort_bok()
        elif val == "4": sök_bok()
        elif val == "5": redigera_bok()
        elif val == "6": visa_statistik()
        elif val == "7": exportera_till_csv()
        elif val == "8": 
            print("Avslutar...")
            break

if __name__ == "__main__":
    main()