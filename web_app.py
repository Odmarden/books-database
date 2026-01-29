from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAMN = "bibliotek.db"

HTML_MALL = '''
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mitt bibliotek</title>
    <style>
        :root {
            --primary: #2c3e50; --accent: #3498db; --bg: #f4f7f6;
            --text: #333; --ref-bg: #fff9c4; --ref-text: #f57f17;
        }
        body { font-family: sans-serif; background: var(--bg); display: flex; flex-direction: column; align-items: center; padding: 20px; }
        .container { max-width: 800px; width: 100%; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .search-box { display: flex; gap: 10px; margin-bottom: 30px; }
        input { flex-grow: 1; padding: 12px; border: 2px solid #ddd; border-radius: 6px; }
        button { background: var(--accent); color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .book-card { border-bottom: 1px solid #eee; padding: 20px 0; }
        .book-header { display: flex; justify-content: space-between; }
        .tag { background: #e1f5fe; color: #0277bd; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; }
        
        /* Klickbara referenser */
        .references { margin-top: 10px; font-size: 0.85em; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .ref-link {
            background: var(--ref-bg);
            color: var(--ref-text);
            padding: 2px 10px;
            border-radius: 4px;
            text-decoration: none;
            border: 1px solid #fff176;
            transition: transform 0.1s;
        }
        .ref-link:hover { background: #fff176; transform: scale(1.05); }
        .ref-label { font-weight: bold; color: #888; font-size: 0.75em; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="container">
        <h1><a href="/" style="text-decoration:none; color:inherit;">📚 Mitt Bibliotek</a></h1>

               
        <form class="search-box" method="GET" action="/">
            <input type="text" name="sok" placeholder="Sök titel eller författare..." value="{{ sokord }}">
            <button type="submit">Sök</button>
        </form>

        <div class="results">
            {% for rad in rader %}
            <div class="book-card">
                <div class="book-header">
                    <div class="book-info">
                        <h3 id="book-{{ rad[0] }}">{{ rad[1] }}</h3>
                        <p>av {{ rad[2] }}</p>
                    </div>
                    <a href="/?sok={{ rad[3] }}" class="tag" style="text-decoration:none;">{{ rad[3] }}</a>
                </div>
                
                {% if rad[4] %}
                <div class="references">
                    <span class="ref-label">Relaterat:</span>
                    {% for ref_data in rad[4].split('||') %}
                        {# ref_data ser ut som "ID:Titel" #}
                        {% set parts = ref_data.split(':', 1) %}
                        <a href="/?sok={{ parts[1] }}" class="ref-link">{{ parts[1] }}</a>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    sokord = request.args.get('sok', '')
    conn = sqlite3.connect(DB_NAMN)
    cursor = conn.cursor()
    
    # Vi använder '||' som separator mellan olika böcker och ':' mellan ID och Titel
    sql = '''
        SELECT b.id, b.titel, b.forfattare, b.kategori, 
        (SELECT GROUP_CONCAT(b2.id || ':' || b2.titel, '||') 
         FROM referenser r 
         JOIN bocker b2 ON r.ref_id = b2.id 
         WHERE r.bok_id = b.id) as relaterat
        FROM bocker b
        WHERE b.titel LIKE ? OR b.forfattare LIKE ? OR b.kategori LIKE ?
        ORDER BY b.titel ASC
    '''
    
    cursor.execute(sql, (f"%{sokord}%", f"%{sokord}%", f"%{sokord}%"))
    rader = cursor.fetchall()
    conn.close()
    
    return render_template_string(HTML_MALL, rader=rader, sokord=sokord)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)