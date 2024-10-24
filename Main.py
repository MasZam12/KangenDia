from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Fungsi untuk menghitung Certainty Factor (CF)
def calculate_cf(user_cf, expert_cf):
    return user_cf * expert_cf

def combine_cf(cf_old, cf_new):
    return cf_old + cf_new * (1 - cf_old)

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

# Halaman awal untuk tampilan pertama
@app.route('/')
def first_page():
    return render_template('tampilan.html')

# Halaman Utama untuk Form Gejala
@app.route('/diagnosa/')
def index():
    knowledge_base = load_knowledge_base_from_file('knowledge_base.txt')
    symptoms = {gejala_code: data['name'] for gejala_code, data in next(iter(knowledge_base.values()))['symptoms'].items()}
    return render_template('index.html', symptoms=symptoms)

# Proses diagnosa
@app.route('/diagnose', methods=['POST'])
def diagnose_route():
    knowledge_base = load_knowledge_base_from_file('knowledge_base.txt')
    gejala_user = {}

    for symptom_code in request.form:
        user_input = int(request.form[symptom_code])
        gejala_user[symptom_code] = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 0.8, 6: 1.0}.get(user_input, 0.0)

    hasil_diagnosis = diagnose(gejala_user, knowledge_base)
    return render_template('result.html', diagnosis_results=hasil_diagnosis)

if __name__ == '__main__':
    app.run(debug=True)
