from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'superhemlig_nyckel_byt_i_produktion'
DB_NAMN = "bibliotek.db"
THUMBNAIL_DIR = "thumbnails"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
KATEGORIER = ["Skönlitteratur", "Facklitteratur", "Biografi", "Övrigt", "Lyrik", "Dramatik", "Filosofi", "Teologi", "Matlagning", "Barn"]

def get_db_connection():
    conn = sqlite3.connect(DB_NAMN)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_upload(file):
    if file and allowed_file(file.filename):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
        filename = f"thumb_{timestamp}.{ext}"
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)
        filepath = os.path.join(THUMBNAIL_DIR, filename)
        file.save(filepath)
        return filepath
    return None

@app.route('/thumbnail/<path:filename>')
def thumbnail(filename):
    if filename.startswith('thumbnails/'):
        actual_filename = filename[11:]
    else:
        actual_filename = filename
    
    thumbnail_path = os.path.join('thumbnails', actual_filename)
    if os.path.exists(thumbnail_path):
        return send_from_directory('thumbnails', actual_filename)
    else:
        return send_from_directory('thumbnails', 'placeholder.svg')

@app.route('/')
def index():
    sokord = request.args.get('sok', '')
    kategori = request.args.get('kat', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = '''
        SELECT b.id, b.titel, b.forfattare, b.kategori, b.tryckaar, b.forlag, b.thumbnail,
        (SELECT GROUP_CONCAT(b2.id || ':' || b2.titel, '||') 
         FROM referenser r 
         JOIN bocker b2 ON r.ref_id = b2.id 
         WHERE r.bok_id = b.id) as relaterat
        FROM bocker b
        WHERE 1=1
    '''
    params = []
    
    if sokord:
        query += ' AND (b.titel LIKE ? OR b.forfattare LIKE ? OR b.forlag LIKE ? OR CAST(b.tryckaar AS TEXT) LIKE ?)'
        search_term = f"%{sokord}%"
        params.extend([search_term, search_term, search_term, search_term])
        
    if kategori:
        query += ' AND b.kategori = ?'
        params.append(kategori)
        
    query += ' ORDER BY b.id DESC'
    
    cursor.execute(query, params)
    rader = cursor.fetchall()
    conn.close()
    
    return render_template('index.html', rader=rader, sokord=sokord, vald_kat=kategori, kategorier=KATEGORIER)

@app.route('/add', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        titel = request.form['titel']
        forfattare = request.form['forfattare']
        kategori = request.form.get('kategori')
        tryckaar = request.form.get('tryckaar')
        forlag = request.form.get('forlag')
        
        thumbnail_path = 'thumbnails/placeholder.svg'
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file.filename != '':
                uploaded_path = handle_upload(file)
                if uploaded_path:
                    thumbnail_path = uploaded_path
                else:
                    flash('Ogiltigt filformat för bilden.', 'error')

        if not titel or not forfattare:
            flash('Titel och författare är obligatoriska fält!', 'error')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO bocker (titel, forfattare, kategori, tryckaar, forlag, thumbnail) VALUES (?, ?, ?, ?, ?, ?)',
                         (titel, forfattare, kategori, tryckaar if tryckaar else None, forlag if forlag else None, thumbnail_path))
            conn.commit()
            conn.close()
            flash('Boken lades till i biblioteket!', 'success')
            return redirect(url_for('index'))

    return render_template('add.html', kategorier=KATEGORIER)

@app.route('/edit/<int:bok_id>', methods=('GET', 'POST'))
def edit_book(bok_id):
    conn = get_db_connection()
    bok = conn.execute('SELECT * FROM bocker WHERE id = ?', (bok_id,)).fetchone()
    
    if bok is None:
        conn.close()
        flash('Boken hittades inte.', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        titel = request.form['titel']
        forfattare = request.form['forfattare']
        kategori = request.form.get('kategori')
        tryckaar = request.form.get('tryckaar')
        forlag = request.form.get('forlag')
        
        thumbnail_path = bok['thumbnail']
        if 'thumbnail' in request.files:
            file = request.files['thumbnail']
            if file.filename != '':
                uploaded_path = handle_upload(file)
                if uploaded_path:
                    thumbnail_path = uploaded_path
                else:
                    flash('Ogiltigt filformat för bilden.', 'error')

        if not titel or not forfattare:
            flash('Titel och författare är obligatoriska fält!', 'error')
        else:
            conn.execute('UPDATE bocker SET titel = ?, forfattare = ?, kategori = ?, tryckaar = ?, forlag = ?, thumbnail = ? WHERE id = ?',
                         (titel, forfattare, kategori, tryckaar if tryckaar else None, forlag if forlag else None, thumbnail_path, bok_id))
            conn.commit()
            conn.close()
            flash('Boken uppdaterades framgångsrikt!', 'success')
            return redirect(url_for('index'))
            
    conn.close()
    return render_template('edit.html', bok=bok, kategorier=KATEGORIER)

@app.route('/delete/<int:bok_id>', methods=('POST',))
def delete_book(bok_id):
    conn = get_db_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute('DELETE FROM bocker WHERE id = ?', (bok_id,))
    conn.commit()
    conn.close()
    flash('Boken har tagits bort.', 'success')
    return redirect(url_for('index'))

@app.route('/upload/<int:bok_id>', methods=['GET', 'POST'])
def upload_thumbnail(bok_id):
    conn = get_db_connection()
    bok = conn.execute("SELECT id, titel, forfattare, thumbnail FROM bocker WHERE id = ?", (bok_id,)).fetchone()
    
    if not bok:
        conn.close()
        flash('Boken hittades inte', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'thumbnail' not in request.files or request.files['thumbnail'].filename == '':
            flash('Ingen fil valdes.', 'error')
        else:
            file = request.files['thumbnail']
            uploaded_path = handle_upload(file)
            if uploaded_path:
                conn.execute("UPDATE bocker SET thumbnail = ? WHERE id = ?", (uploaded_path, bok_id))
                conn.commit()
                flash('Omslagsbild uppdaterad!', 'success')
                conn.close()
                return redirect(url_for('index'))
            else:
                flash('Otillåtet filformat. Tillåtna: jpg, jpeg, png, gif, webp.', 'error')
    
    conn.close()
    return render_template('upload.html', bok=bok)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
