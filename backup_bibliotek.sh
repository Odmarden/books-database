#!/bin/bash

# Inställningar
DB_PATH="/var/www/bokdatabas/bibliotek.db"
BACKUP_DIR="/var/www/bokdatabas/backups"
DATE=$(date +%Y-%m-%d_%H%M%S)

# Skapa backup-mapp om den inte finns
mkdir -p $BACKUP_DIR

# Skapa en säker backup med sqlite3-verktyget
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/bibliotek_$DATE.db'"

# Sätt rättigheter så wwwrun kan läsa dem om det behövs
chown :wwwrun $BACKUP_DIR/bibliotek_$DATE.db
chmod 640 $BACKUP_DIR/bibliotek_$DATE.db

# Ta bort backuper äldre än 30 dagar
find $BACKUP_DIR -type f -name "*.db" -mtime +30 -delete

echo "Backup klar: bibliotek_$DATE.db"
