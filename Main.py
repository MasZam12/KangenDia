from flask import Flask, render_template, request, redirect, url_for, flash
import os
from database.db import create_connection
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def calculate_cf(user_cf, expert_cf):
    return user_cf * expert_cf

def combine_cf(cf_old, cf_new):
    return cf_old + cf_new * (1 - cf_old)

def get_user_cf(choice):
    return {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8, 6: 1.0}.get(choice, 0.0)

def load_knowledge_base_from_file():
    knowledge_base = {}
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "knowledge_bases.txt"))
    print(f"Mencoba memuat file knowledge base dari path: {file_path}")
    try:
        with open(file_path, 'r') as file:
            penyakit_code = None
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("P"):
                    penyakit_code, penyakit_name = line.split(" - ")
                    knowledge_base[penyakit_code] = {'name': penyakit_name, 'symptoms': {}}
                elif line.startswith("G"):
                    gejala_code, rest = line.split(": ")
                    gejala_name, weight = rest.split(" - ")
                    knowledge_base[penyakit_code]['symptoms'][gejala_code] = {'name': gejala_name, 'weight': float(weight)}
        print("Knowledge base berhasil dimuat.")
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan. Pastikan file berada di direktori 'data' dan bernama 'knowledge_bases.txt'.")
    except Exception as e:
        print("Terjadi error saat membaca knowledge base:", e)
    return knowledge_base

def diagnose(gejala_user, knowledge_base):
    hasil_diagnosis = []
    for penyakit_code, penyakit_data in knowledge_base.items():
        cf_combine = 0.0
        match_found = False
        for gejala_code, expert_cf in penyakit_data['symptoms'].items():
            user_cf = gejala_user.get(gejala_code, 0.0)
            if user_cf > 0:
                match_found = True
                cf_current = calculate_cf(user_cf, expert_cf['weight'])
                cf_combine = combine_cf(cf_combine, cf_current)
        if match_found:
            hasil_diagnosis.append((penyakit_data['name'], cf_combine))
    hasil_diagnosis.sort(key=lambda x: x[1], reverse=True)
    return hasil_diagnosis

def process_user_input(form_data):
    gejala_user = {}
    for symptom_code in form_data:
        user_input = int(form_data[symptom_code])
        gejala_user[symptom_code] = get_user_cf(user_input)
    return gejala_user

@app.route('/')
def start():
    return render_template('tampilan.html')

@app.route('/diagnosa')
def index():
    knowledge_base = load_knowledge_base_from_file()
    if not knowledge_base:
        return "Error: File knowledge base tidak ditemukan atau kosong."
    symptoms = {}
    for penyakit_data in knowledge_base.values():
        for gejala_code, gejala_data in penyakit_data['symptoms'].items():
            if gejala_code not in symptoms:
                symptoms[gejala_code] = gejala_data['name']
    return render_template('index.html', symptoms=symptoms)

@app.route('/diagnose', methods=['POST'])
def diagnose_route():
    knowledge_base = load_knowledge_base_from_file()
    if not knowledge_base:
        return "Error: Tidak dapat memuat knowledge base."
    gejala_user = process_user_input(request.form)
    hasil_diagnosis = diagnose(gejala_user, knowledge_base)
    hasil_diagnosis_filtered = [diagnosis for diagnosis in hasil_diagnosis if diagnosis[1] > 0]
    return render_template('result.html', diagnosis_results=hasil_diagnosis_filtered)

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO user (Nama_User, Email_User, No_User, Password_User) VALUES (%s, %s, %s, %s)", 
                        (username, email, phone, password))
            connection.commit()
            flash('Sign Up Successful!', 'success')
            return redirect(url_for('sign_in'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM user WHERE Email_User = %s AND Password_User = %s", (email, password))
            user = cursor.fetchone()
            if user:
                flash('Sign In Successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'danger')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            connection.close()
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)
