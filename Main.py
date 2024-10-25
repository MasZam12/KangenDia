from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Fungsi untuk menghitung Certainty Factor (CF)
def calculate_cf(user_cf, expert_cf):
    """Menghitung CF berdasarkan input user dan pakar."""
    return user_cf * expert_cf

def combine_cf(cf_old, cf_new):
    """Menggabungkan dua nilai CF."""
    return cf_old + cf_new * (1 - cf_old)

# Fungsi untuk mendapatkan nilai CF dari input user
def get_user_cf(choice):
    return {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8, 6: 1.0}.get(choice, 0.0)

# Fungsi untuk membaca knowledge base dari file
def load_knowledge_base_from_file(file_path):
    knowledge_base = {}
    try:
        with open(file_path, 'r') as file:
            penyakit_code = None
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("P"):  # Baris yang memulai kode penyakit
                    penyakit_code, penyakit_name = line.split(" - ")
                    knowledge_base[penyakit_code] = {'name': penyakit_name, 'symptoms': {}}
                elif line.startswith("G"):  # Baris yang memulai kode gejala
                    gejala_code, rest = line.split(": ")
                    gejala_name, weight = rest.split(" - ")
                    knowledge_base[penyakit_code]['symptoms'][gejala_code] = {'name': gejala_name, 'weight': float(weight)}
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan.")
    return knowledge_base

# Fungsi untuk melakukan diagnosa
def diagnose(gejala_user, knowledge_base):
    hasil_diagnosis = []
    for penyakit_code, penyakit_data in knowledge_base.items():
        cf_combine = 0.0
        for gejala, expert_cf in penyakit_data['symptoms'].items():
            user_cf = gejala_user.get(gejala, 0.0)
            cf_current = calculate_cf(user_cf, expert_cf['weight'])
            cf_combine = combine_cf(cf_combine, cf_current)
        hasil_diagnosis.append((penyakit_data['name'], cf_combine))
    hasil_diagnosis.sort(key=lambda x: x[1], reverse=True)
    return hasil_diagnosis

# Fungsi untuk memproses input user dari form
def process_user_input(form_data):
    gejala_user = {}
    for symptom_code in form_data:
        user_input = int(form_data[symptom_code])
        gejala_user[symptom_code] = get_user_cf(user_input)
    return gejala_user

@app.route('/')
def first_page():
    return render_template('tampilan.html')

@app.route('/diagnosa/')
def index():
    # Muat knowledge base dan kumpulkan semua gejala unik
    knowledge_base = load_knowledge_base_from_file("knowledge_base.txt")
    symptoms = {}
    for penyakit_data in knowledge_base.values():
        for gejala_code, gejala_data in penyakit_data['symptoms'].items():
            if gejala_code not in symptoms:
                symptoms[gejala_code] = gejala_data['name']
    return render_template('index.html', symptoms=symptoms)

@app.route('/diagnose', methods=['POST'])
def diagnose_route():
    knowledge_base = load_knowledge_base_from_file("knowledge_base.txt")
    gejala_user = process_user_input(request.form)

    hasil_diagnosis = diagnose(gejala_user, knowledge_base)
    hasil_diagnosis_filtered = [diagnosis for diagnosis in hasil_diagnosis if diagnosis[1] > 0]

    return render_template('result.html', diagnosis_results=hasil_diagnosis_filtered)

if __name__ == '__main__':
    app.run(debug=True)
