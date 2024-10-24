from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Ganti dengan secret key Anda
csrf = CSRFProtect(app)

class SymptomForm(FlaskForm):
    SYMPTOM_CHOICES = [
        ('1', 'Tidak Yakin (0.0)'),
        ('2', 'Hampir Mungkin (0.2)'),
        ('3', 'Mungkin (0.4)'),
        ('4', 'Cukup Yakin (0.6)'),
        ('5', 'Yakin (0.8)'),
        ('6', 'Sangat Yakin (1.0)')
    ]

    G01 = SelectField('Nyeri Dada', choices=SYMPTOM_CHOICES)
    G02 = SelectField('Keringat Dingin', choices=SYMPTOM_CHOICES)
    G03 = SelectField('Nyeri Ulu Hati', choices=SYMPTOM_CHOICES)
    G04 = SelectField('Penurunan Kesadaran', choices=SYMPTOM_CHOICES)
    G05 = SelectField('Denyut Nadi Lemah', choices=SYMPTOM_CHOICES)
    G06 = SelectField('Sesak Nafas', choices=SYMPTOM_CHOICES)
    G09 = SelectField('Kaki Bengkak', choices=SYMPTOM_CHOICES)
    G10 = SelectField('Perut Membesar', choices=SYMPTOM_CHOICES)
    G11 = SelectField('Sesak Saat Malam Hari', choices=SYMPTOM_CHOICES)
    G12 = SelectField('Posisi Tidur 2 Bantal', choices=SYMPTOM_CHOICES)
    G13 = SelectField('Berdebar', choices=SYMPTOM_CHOICES)
    G14 = SelectField('Batuk Berdarah', choices=SYMPTOM_CHOICES)
    G17 = SelectField('Mudah Lelah', choices=SYMPTOM_CHOICES)
    G18 = SelectField('Bibir Membiru', choices=SYMPTOM_CHOICES)
    G20 = SelectField('Infeksi Saluran Nafas Berulang', choices=SYMPTOM_CHOICES)
    G22 = SelectField('Nyeri pada Tangan/Kaki', choices=SYMPTOM_CHOICES)
    G23 = SelectField('Kaki/Tangan Memerah', choices=SYMPTOM_CHOICES)

# Knowledge Base
knowledge_base = {
    'P01': {
        'name': 'Jantung Koroner',
        'symptoms': {
            'G01': {'name': 'Nyeri Dada', 'weight': 0.8},
            'G02': {'name': 'Keringat Dingin', 'weight': 0.6},
            'G03': {'name': 'Nyeri Ulu Hati', 'weight': 0.4},
            'G04': {'name': 'Penurunan Kesadaran', 'weight': 0.6},
            'G05': {'name': 'Denyut Nadi Lemah', 'weight': 0.6},
            'G06': {'name': 'Sesak Nafas', 'weight': 0.4}
        }
    },
    'P02': {
        'name': 'Gagal Jantung Kongestif',
        'symptoms': {
            'G06': {'name': 'Sesak Nafas', 'weight': 0.8},
            'G09': {'name': 'Kaki Bengkak', 'weight': 0.6},
            'G10': {'name': 'Perut Membesar', 'weight': 0.4},
            'G11': {'name': 'Sesak Saat Malam Hari', 'weight': 0.6},
            'G12': {'name': 'Posisi Tidur 2 Bantal', 'weight': 0.8}
        }
    },
    'P03': {
        'name': 'Katup Jantung',
        'symptoms': {
            'G13': {'name': 'Berdebar', 'weight': 0.4},
            'G14': {'name': 'Batuk Berdarah', 'weight': 0.4},
            'G06': {'name': 'Sesak Nafas', 'weight': 0.6}
        }
    },
    'P04': {
        'name': 'Aritmia',
        'symptoms': {
            'G13': {'name': 'Berdebar', 'weight': 0.8},
            'G07': {'name': 'Pusing', 'weight': 0.4}
        }
    },
    'P05': {
        'name': 'Jantung Bawaan',
        'symptoms': {
            'G18': {'name': 'Bibir Membiru', 'weight': 0.8},
            'G17': {'name': 'Mudah Lelah', 'weight': 0.6},
            'G20': {'name': 'Infeksi Saluran Nafas Berulang', 'weight': 0.6}
        }
    },
    'P06': {
        'name': 'Pembuluh Darah',
        'symptoms': {
            'G09': {'name': 'Kaki Bengkak', 'weight': 0.6},
            'G22': {'name': 'Nyeri pada Tangan/Kaki', 'weight': 0.6},
            'G23': {'name': 'Kaki/Tangan Memerah', 'weight': 0.8}
        }
    }
}

# Certainty Factor Calculation
def calculate_cf(user_symptoms, disease_symptoms):
    cf = 0
    for symptom_code, user_cf in user_symptoms.items():
        if symptom_code in disease_symptoms:
            expert_cf = disease_symptoms[symptom_code]['weight']
            combined_cf = user_cf * expert_cf
            cf = cf + combined_cf * (1 - cf)
    return cf

# Backward Chaining
def backward_chaining(user_symptoms):
    results = {}
    for disease_code, disease_info in knowledge_base.items():
        cf = calculate_cf(user_symptoms, disease_info['symptoms'])
        if cf > 0:
            results[disease_info['name']] = round(cf * 100, 2)  # Convert to percentage
    return results

@app.route('/')
def index():
    return render_template('tampilan.html')

@app.route('/diagnosa/', methods=['GET', 'POST'])
def diagnosis():
    form = SymptomForm()
    print(f"CSRF Token: {form.csrf_token.data}")
    diagnosis_results = {}

    if request.method == 'POST' and form.validate_on_submit():
        # Get symptoms from the form
        user_symptoms = {}
        confidence_levels = {
            '1': 0.0, '2': 0.2, '3': 0.4, '4': 0.6, '5': 0.8, '6': 1.0
        }

        for field, value in form.data.items():
            if value and value in confidence_levels:
                user_symptoms[field] = confidence_levels[value]

        # Diagnose using backward chaining
        diagnosis_results = backward_chaining(user_symptoms)

    # Sort results
    sorted_diagnosis = sorted(diagnosis_results.items(), key=lambda x: x[1], reverse=True)

    return render_template('diagnosa.html', form=form, diagnosis_results=sorted_diagnosis)

if __name__ == '__main__':
    app.run(debug=True)
