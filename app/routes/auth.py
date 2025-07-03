from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.user_data import load_users, save_users
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

# ⛩️ Root redirect ke login
@auth.route('/')
def home():
    return redirect(url_for('auth.login'))

# 🔐 Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        if not username.strip() or not password.strip():
            flash('Username atau Password tidak boleh kosong!')
            return redirect(url_for('auth.login'))

        if username in users and check_password_hash(users[username]['password'], password):
            session['user'] = username
            session['display_name'] = users[username]['display_name']
            session['role'] = users[username]['role']
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Username atau password salah oi!')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# 📝 Register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        display_name = request.form['username']  # atau nanti bisa field sendiri

        if not username.strip() or not password.strip():
            flash('Username atau password tidak boleh kosong')
            return redirect(url_for('auth.register'))

        if username in users:
            flash('Username sudah dipakai!')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        users[username] = {
            'password': hashed_password,
            'display_name': display_name,
            'role': 'user'
        }

        save_users(users)
        flash('Berhasil daftar! Ayo login.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# 🏠 Dashboard (user/admin)
@auth.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', nama=session['display_name'])
    flash('Silakan login pek!')
    return redirect(url_for('auth.login'))

# ⚙️ Admin Panel
@auth.route('/admin')
def admin_panel():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Akses ditolak, kamu bukan admin!')
        return redirect(url_for('auth.login'))

    users = load_users()
    return render_template('admin_panel.html', users=users)

# ❌ Hapus user
@auth.route('/admin/delete/<username>', methods=['POST'])
def delete_user(username):
    if 'user' not in session or session.get('role') != 'admin':
        flash('Lu bukan admin bro.')
        return redirect(url_for('auth.login'))

    users = load_users()
    if username in users:
        if username != session['user']:
            del users[username]
            save_users(users)
            flash(f'User "{username}" berhasil dihapus!')
        else:
            flash('Gak bisa hapus akun sendiri 😅')

    return redirect(url_for('auth.admin_panel'))

# ✏️ Edit user
@auth.route('/admin/edit/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if 'user' not in session or session.get('role') != 'admin':
        flash('Lu bukan admin!')
        return redirect(url_for('auth.login'))

    users = load_users()

    if username not in users:
        flash('User tidak ditemukan!')
        return redirect(url_for('auth.admin_panel'))

    if request.method == 'POST':
        display_name = request.form['display_name']
        role = request.form['role']

        if not display_name.strip() or role not in ['admin', 'user']:
            flash('Data tidak valid!')
            return redirect(url_for('auth.edit_user', username=username))

        users[username]['display_name'] = display_name
        users[username]['role'] = role
        save_users(users)

        flash(f'User {username} berhasil diupdate!')
        return redirect(url_for('auth.admin_panel'))

    return render_template('edit_user.html', username=username, data=users[username])

# ➕ Tambah user
@auth.route('/admin/add', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Lu bukan admin!')
        return redirect(url_for('auth.login'))

    users = load_users()

    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        display_name = request.form['display_name']
        role = request.form['role']

        if username in users:
            flash('Username sudah ada!')
            return redirect(url_for('auth.add_user'))

        if not username.strip() or not password.strip() or role not in ['admin', 'user']:
            flash('Data tidak valid!')
            return redirect(url_for('auth.add_user'))

        users[username] = {
            'password': generate_password_hash(password),
            'display_name': display_name,
            'role': role
        }

        save_users(users)
        flash(f'User {username} berhasil ditambahkan!')
        return redirect(url_for('auth.admin_panel'))

    return render_template('add_user.html')

# 🚪 Logout
@auth.route('/logout')
def logout():
    session.clear()
    flash('Kamu sudah keluar!')
    return redirect(url_for('auth.login'))