import json, os
from flask import Flask, request, render_template, flash, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'jangan dikasih tahu' # buat enable flash

def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as file:
            return json.load(file)
    return {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/hallo/<name>')
def greet(name):
    return f'halo, {name.capitalize()}!'

@app.route('/umur/<int:usia>')
def umur(usia):
    return f'Wah udah {usia} tahun aja nih!'

@app.route('/form', methods = ['GET', 'POST'])
def form():
    if request.method == 'POST':
        nama = request.form['nama']
        if not nama.strip():
            flash('Nama tidak boleh kosong!')
            return redirect(url_for('form'))
        return f'Halo, {nama} data kamu sudah masuk!.'
    return render_template('form.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        # Validasi semua
        if not username.strip() or not password.strip():
            flash('Username atau Password tidak boleh kosong!')
            return redirect(url_for('login'))
        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            session['display_name'] = users[username]['display_name']
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah oi!') 
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        display_name = request.form['username']

        if not username.strip() or not password.strip():
            flash('Username atau password tidak boleh kosong')
            return redirect(url_for('register'))
    
        if username in users:
            flash('Username sudah dipakai!')
            return redirect(url_for('register'))
    
        hashed_password = generate_password_hash(password)
        users[username] = {
        'password': hashed_password,
        'display_name': display_name
        }

        save_users(users)
        flash('Berhasil daftar! Ayo login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', nama=session['user'])
    flash('Silakan login pek!')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Kamu sudah keluar!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)