from flask import Flask, render_template, redirect, url_for, request, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) #Oturum yönetimi için reastgele bir anahtar.

#PostgreSQL bağlantısı.
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="chat_db",
        user="postgres",
        password="4806",
        port='5432'
    )
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Bu fonksiyonu, uygulamanız başlatıldığında çağırabilirsiniz.
create_tables()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0] #Kullanıcı ID'sini oturumda sakla
            return redirect(url_for('chat'))
        else:
            return "Kullanıcı adı veya şifre yanlış!"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        # POST isteği ile mesaj gönderme
        message = request.form['message']  # Formdan gelen mesaj
        user_id = session['user_id']  # Oturum açan kullanıcı ID'si

        # Mesajı veritabanına ekleme
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (user_id, message) VALUES (%s, %s)",
                (user_id, message)
            )
        conn.commit()

        # Mesaj gönderildikten sonra tekrar chat sayfasına yönlendir
        return redirect(url_for('chat'))

    # GET isteği ile mesajları alıp chat sayfasına gönderme
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT messages.id, users.username, messages.message, messages.timestamp
            FROM messages
            INNER JOIN users ON messages.user_id = users.id
            ORDER BY messages.timestamp ASC
            """
        )
        messages = cur.fetchall()

    conn.close()
    return render_template('chat.html', messages=messages)




@app.route('/logout')
def logout():
    session.pop('user_id', None) #Kullanıcıyı çıkart
    return redirect(url_for('login')) #Giriş sayfasına yönlendir.

if __name__ == '__main__':
    app.run(debug=True)