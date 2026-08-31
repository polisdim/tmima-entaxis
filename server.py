#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Logger & Student Portfolio Backend for Inclusion Class (Τμήμα Ένταξης)
School: ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης
Teacher: Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)
"""

import os
import sys
import json
import socket
import threading
import time
import zipfile
import io
import shutil
import webbrowser
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

import docx_generator
import excel_generator
import ai_analyzer

# Set working directory to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

APP_DIR = os.path.join(BASE_DIR, 'app') if (os.path.exists(os.path.join(BASE_DIR, 'app')) and os.path.exists(os.path.join(BASE_DIR, 'app', 'index.html'))) else BASE_DIR

DATA_DIR = os.path.join(BASE_DIR, 'data') if os.path.exists(os.path.join(BASE_DIR, 'data')) else BASE_DIR
os.makedirs(DATA_DIR, exist_ok=True)
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')
os.makedirs(BACKUPS_DIR, exist_ok=True)

STUDENTS_DIR = os.path.join(BASE_DIR, 'Μαθητές')
os.makedirs(STUDENTS_DIR, exist_ok=True)

CLASSES_DIR = os.path.join(BASE_DIR, 'Τμήματα')
os.makedirs(CLASSES_DIR, exist_ok=True)

STUDENTS_FILE = os.path.join(DATA_DIR, 'students.json') if os.path.exists(os.path.join(DATA_DIR, 'students.json')) else os.path.join(BASE_DIR, 'students.json')
OBSERVATIONS_FILE = os.path.join(DATA_DIR, 'observations.json') if os.path.exists(os.path.join(DATA_DIR, 'observations.json')) else os.path.join(BASE_DIR, 'observations.json')
CLASS_OBSERVATIONS_FILE = os.path.join(DATA_DIR, 'class_observations.json')
AUTH_FILE = os.path.join(DATA_DIR, 'auth.json') if os.path.exists(os.path.join(DATA_DIR, 'auth.json')) else os.path.join(BASE_DIR, 'auth.json')

CENTRAL_LOG_FILE = os.path.join(BASE_DIR, 'Ημερολόγιο_Συνεδριών_2026-2027.md')
CENTRAL_EXCEL_FILE = os.path.join(BASE_DIR, 'Ημερολόγιο_Συνεδριών_2026-2027.xlsx')
RESEARCH_JSON_FILE = os.path.join(BASE_DIR, 'Ερευνητικό_Dataset_ΤΕ.json')
RESEARCH_CSV_FILE = os.path.join(BASE_DIR, 'Ερευνητικό_Dataset_ΤΕ.csv')

# Safe Atomic File Writes
def safe_write_json(filepath, data):
    """Writes data to a temp file and atomically replaces destination to prevent corruption."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    temp_path = f"{filepath}.tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, filepath)

def safe_write_text(filepath, text):
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    temp_path = f"{filepath}.tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(temp_path, filepath)

# Rolling Daily Backup
def create_daily_backup():
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        backup_zip_path = os.path.join(BACKUPS_DIR, f"backup_{today_str}.zip")
        if not os.path.exists(backup_zip_path):
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, dirs, files in os.walk(DATA_DIR):
                    if 'backups' in root:
                        continue
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        z.write(full_p, rel_p)
            # Retain only last 7 backups
            backups = sorted([os.path.join(BACKUPS_DIR, f) for f in os.listdir(BACKUPS_DIR) if f.endswith('.zip')])
            while len(backups) > 7:
                os.remove(backups.pop(0))
    except Exception as e:
        print(f"[!] Backup warning: {e}")

# Initial taxonomy & domains
TAXONOMY = {
    "domains": [
        {"id": "arithmetic", "name": "Αριθμητική", "color": "#38bdf8", "icon": "🔢", "desc": "Αριθμητική αίσθηση, πράξεις, κλάσματα, δεκαδικοί, προπαίδεια"},
        {"id": "algebra", "name": "Άλγεβρα", "color": "#a855f7", "icon": "📐", "desc": "Σύμβολα, μεταβλητές x, εξισώσεις, αναγωγή όρων, ιδιότητες"},
        {"id": "geometry", "name": "Γεωμετρία", "color": "#34d399", "icon": "📏", "desc": "Σχήματα, περίμετρος, εμβαδόν, χωρική αντίληψη, Πυθαγόρειο"},
        {"id": "stochastics", "name": "Στοχαστικά", "color": "#f59e0b", "icon": "📊", "desc": "Διαγράμματα, στατιστική, μέση τιμή, πιθανότητες, τυχαιότητα"},
        {"id": "engagement", "name": "Εμπλοκή & Συνέπεια", "color": "#ec4899", "icon": "⏱️", "desc": "Συνέπεια, προετοιμασία, συγκέντρωση, αυτενέργεια, μελέτη"},
        {"id": "socioemotional", "name": "Ψυχοσυναισθηματικά", "color": "#6366f1", "icon": "🧠", "desc": "Αυτοεικόνα, άγχος, ματαίωση, κίνητρα, κοινωνικές σχέσεις"},
        {"id": "collaboration_family", "name": "Συνεργασία & Οικογένεια", "color": "#14b8a6", "icon": "🤝", "desc": "Δυαδική σχέση εκπαιδευτικού-μαθητή, γονείς, ΚΕΔΑΣΥ"},
        {"id": "iep_goals", "name": "Στόχοι Ε.Π.Ε.", "color": "#f97316", "icon": "🎯", "desc": "Βραχυπρόθεσμοι & μακροπρόθεσμοι στόχοι, ρουμπρίκες 4 επιπέδων"}
    ],
    "bloom_levels": [
        {"id": "remembering", "level": 1, "name": "1. Ανάκληση", "desc": "Ανάκληση ορισμών, κανόνων, προπαίδειας, συμβόλων, γεγονότων"},
        {"id": "understanding", "level": 2, "name": "2. Κατανόηση", "desc": "Ερμηνεία, εξήγηση με δικά του λόγια, διαγραμματική αναπαράσταση"},
        {"id": "applying", "level": 3, "name": "3. Εφαρμογή", "desc": "Εκτέλεση αλγορίθμου, επίλυση ασκήσεων, εφαρμογή μεθόδου"},
        {"id": "analyzing", "level": 4, "name": "4. Ανάλυση", "desc": "Διάσπαση προβλήματος, διάκριση δεδομένων/ζητουμένων, σχέσεις"},
        {"id": "evaluating", "level": 5, "name": "5. Αξιολόγηση", "desc": "Έλεγχος λογικότητας αποτελέσματος, εντοπισμός σφάλματος, επιλογή στρατηγικής"},
        {"id": "creating", "level": 6, "name": "6. Δημιουργία", "desc": "Κατασκευή δικού του προβλήματος, γενίκευση, πρωτότυπη σύνθεση"}
    ],
    "duval_registers": [
        {"id": "verbal", "name": "Λεκτική / Φυσική Γλώσσα", "icon": "🗣️"},
        {"id": "symbolic", "name": "Συμβολική / Αλγεβρική", "icon": "🔢"},
        {"id": "visual", "name": "Γραφική / Οπτική", "icon": "📐"},
        {"id": "manipulative", "name": "Απτική / Εποπτική (CRA)", "icon": "🧩"}
    ],
    "strategies": [
        {"id": "cra", "name": "Μοντέλο CRA", "desc": "Συγκεκριμένο -> Εικονικό -> Αφηρημένο"},
        {"id": "mind_maps", "name": "Νοητικοί Χάρτες", "desc": "Εννοιολογική χαρτογράφηση, διάγραμμα βημάτων"},
        {"id": "color_coding", "name": "Χρωματική Κωδικοποίηση", "desc": "Διάκριση προσήμων, αγνώστων, όρων με χρώμα"},
        {"id": "number_line", "name": "Αριθμογραμμή", "desc": "Οπτικοποίηση πράξεων και τάξης μεγέθους"},
        {"id": "algebra_tiles", "name": "Αλγεβρικά Πλακίδια", "desc": "Απτή/εικονική αναπαράσταση εξισώσεων"},
        {"id": "scaffolding", "name": "Γνωστικά Σκαλοπάτια (Scaffolding)", "desc": "Λυμένα παραδείγματα με σταδιακή απόσυρση"},
        {"id": "checklist", "name": "Λίστες Αυτορρύθμισης", "desc": "Βήμα-βήμα έλεγχος σκέψης και επαλήθευση"},
        {"id": "dual_coding", "name": "Διπλή Κωδικοποίηση", "desc": "Συνδυασμός λεκτικής & οπτικής πληροφορίας"},
        {"id": "other", "name": "Άλλη Τεχνική", "desc": "Εξατομικευμένη τεχνική παρέμβασης"}
    ],
    "outcomes": [
        {"id": "positive", "code": "+", "name": "Υψηλή Επιτυχία / Θετικό", "color": "#4ade80", "weight": 1.0},
        {"id": "partial", "code": "~", "name": "Μερική Επιτυχία / Με Βοήθεια", "color": "#facc15", "weight": 0.5},
        {"id": "negative", "code": "-", "name": "Δυσκολία / Ανεπαρκές", "color": "#f87171", "weight": 0.0}
    ],
    "rubric_levels": [
        {"level": 1, "name": "1. Αρχικό (Novice)", "desc": "Εκτέλεση μόνο με πλήρη και συνεχή καθοδήγηση."},
        {"level": 2, "name": "2. Αναδυόμενο (Emerging)", "desc": "Εκτέλεση με μερική υποστήριξη / hints."},
        {"level": 3, "name": "3. Ικανό (Proficient)", "desc": "Αυτόνομη επίλυση σε οικείο πλαίσιο."},
        {"level": 4, "name": "4. Γενικευμένο (Mastered)", "desc": "Πλήρης αυτονομία και εφαρμογή σε νέα προβλήματα."}
    ],
    "obstacles": [
        {"domain": "arithmetic", "name": "Διαίρεση & Διαχείριση Μηδενός", "type": "Επιστημολογικό"},
        {"domain": "arithmetic", "name": "Κλάσματα (Σύγχυση Αριθμητή/Παρονομαστή)", "type": "Επιστημολογικό"},
        {"domain": "arithmetic", "name": "Δανεισμός / Κρατούμενο στην Αφαίρεση", "type": "Διδακτικό"},
        {"domain": "arithmetic", "name": "Αριθμητική Αίσθηση (Subitizing / Μέγεθος)", "type": "Οντογενετικό"},
        {"domain": "algebra", "name": "Σφάλμα του Ίσον (= ως πράξη)", "type": "Διδακτικό"},
        {"domain": "algebra", "name": "Μεταβλητή (x ως ετικέτα αντί ποσότητας)", "type": "Επιστημολογικό"},
        {"domain": "algebra", "name": "Κανόνες Προσήμων & Παρενθέσεων", "type": "Διδακτικό"},
        {"domain": "algebra", "name": "Μετάφραση Λεκτικού σε Εξίσωση", "type": "Επιστημολογικό"},
        {"domain": "geometry", "name": "Σύγχυση Περιμέτρου (1D) και Εμβαδού (2D)", "type": "Οντογενετικό"},
        {"domain": "geometry", "name": "Χωρική Περιστροφή & Μη-τυπικός Προσανατολισμός", "type": "Οντογενετικό"},
        {"domain": "geometry", "name": "Αποκωδικοποίηση Γεωμετρικών Συμβόλων", "type": "Διδακτικό"},
        {"domain": "stochastics", "name": "Παραδρομή του Τζογαδόρου (Τυχαιότητα)", "type": "Επιστημολογικό"},
        {"domain": "stochastics", "name": "Παρερμηνεία Αξόνων & Κλίμακας Διαγραμμάτων", "type": "Διδακτικό"},
        {"domain": "stochastics", "name": "Σύγχυση Μέσης Τιμής και Διαμέσου", "type": "Επιστημολογικό"},
        {"domain": "engagement", "name": "Διάσπαση Προσοχής / Κόπωση", "type": "Οντογενετικό"},
        {"domain": "engagement", "name": "Ελλιπής Προετοιμασία / Απώλεια Τετραδίου", "type": "Συνήθεια"},
        {"domain": "socioemotional", "name": "Μαθηματικό Άγχος / Φόβος Λάθους", "type": "Ψυχοσυναισθηματικό"},
        {"domain": "socioemotional", "name": "Ρήξη Διδακτικού Συμβολαίου (Αναμονή Επιβεβαίωσης)", "type": "Διδακτικό Συμβόλαιο"}
    ]
}

def init_default_data():
    if not os.path.exists(STUDENTS_FILE):
        default_students = [
            {
                "id": "st_1",
                "name": "Μιχαέλα",
                "surname": "Παπαδοπούλου",
                "code": "S01",
                "gender": "Κορίτσι",
                "birth_date": "2012-05-14",
                "grade": "Β' Γυμνασίου",
                "class_section": "Β1",
                "registration_no": "4521",
                "parent_father": {"name": "Ιωάννης Παπαδόπουλος", "phone": "6971234567"},
                "parent_mother": {"name": "Ελένη Παπαδοπούλου", "phone": "6987654321"},
                "contact": {"address": "Ξάνθη", "email": "papadopoulou_fam@example.com", "family_notes": "Τακτική επικοινωνία με τους γονείς."},
                "diagnosis_info": {"authority": "ΚΕΔΑΣΥ Ξάνθης", "protocol_no": "284/12-04-2024", "diagnosis_type": "Ειδική Μαθησιακή Δυσκολία (Δυσαριθμησία & Δυσλεξία)", "support_history": "2ο έτος φοίτησης στο Τμήμα Ένταξης"},
                "math_profile": {
                    "strengths": "Εξαιρετική οπτική αντίληψη, αγάπη για τα γεωμετρικά σχήματα, δεξιότητα στη χρήση του tablet.",
                    "weaknesses": "Δυσκολία στις πράξεις με κλάσματα (ετερώνυμα) και στην αλγεβρική μετατροπή εκφωνήσεων.",
                    "math_anxiety": "Μέτριο",
                    "learning_style": "Οπτικό / Πολυαισθητηριακό",
                    "effective_strategies": "Χρήση αριθμογραμμής, οπτικοποιημένα βήματα (scaffolding), χρωματική κωδικοποίηση προσήμων."
                },
                "psychosocial_profile": {
                    "self_concept": "Ευγενική και πρόθυμη, αποκτά αυτοπεποίθηση με την επιβεβαίωση.",
                    "attention_focus": "Διατηρεί σταθερή εστίαση προσοχής για 25-30 λεπτά.",
                    "social_interaction": "Εξαιρετική κοινωνική αλληλεπίδραση στο Τμήμα Ένταξης."
                },
                "iep_targets": [
                    {"id": "t1", "area": "Αριθμητική", "target": "Αυτοματοποίηση πράξεων κλασμάτων (ετερώνυμα) με εποπτικό υλικό", "rubric_level": 2, "status": "Σε εξέλιξη"},
                    {"id": "t2", "area": "Άλγεβρα", "target": "Επίλυση πρωτοβάθμιων εξισώσεων ax+b=c με χρωματική κωδικοποίηση", "rubric_level": 2, "status": "Σε εξέλιξη"},
                    {"id": "t3", "area": "Γεωμετρία", "target": "Διάκριση περιμέτρου και εμβαδού σε ορθογώνια και τρίγωνα", "rubric_level": 3, "status": "Σε εξέλιξη"},
                    {"id": "t4", "area": "Συμπεριφορά", "target": "Ενίσχυση αυτοπεποίθησης και μείωση μαθηματικού άγχους", "rubric_level": 4, "status": "Επιτεύχθηκε"}
                ],
                "coverage": {"arithmetic": 65, "algebra": 50, "geometry": 80, "stochastics": 40, "total": 62}
            }
        ]
        safe_write_json(STUDENTS_FILE, default_students)

    if not os.path.exists(OBSERVATIONS_FILE):
        default_obs = []
        safe_write_json(OBSERVATIONS_FILE, default_obs)

    if not os.path.exists(CLASS_OBSERVATIONS_FILE):
        safe_write_json(CLASS_OBSERVATIONS_FILE, [])

    if not os.path.exists(AUTH_FILE):
        safe_write_json(AUTH_FILE, {'pin': '2026', 'updated_at': datetime.now().isoformat()})

    create_daily_backup()

def calculate_student_coverage(student_id):
    if not os.path.exists(OBSERVATIONS_FILE):
        return {"arithmetic": 0, "algebra": 0, "geometry": 0, "stochastics": 0, "total": 0}
    with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
        obs = json.load(f)
    st_obs = [o for o in obs if o.get('student_id') == student_id]
    
    domains = ["arithmetic", "algebra", "geometry", "stochastics"]
    counts = {d: 0 for d in domains}
    for o in st_obs:
        d = o.get('domain_id')
        if d in counts:
            counts[d] += 1
            
    cov = {}
    total_score = 0
    for d in domains:
        score = min(100, counts[d] * 20)
        cov[d] = score
        total_score += score
    cov['total'] = round(total_score / len(domains)) if domains else 0
    return cov

def get_student_dir(student):
    st_name = student.get('name', 'Μαθητής').strip()
    st_surname = student.get('surname', '').strip()
    folder_name = f"{st_name}_{st_surname}".strip('_')
    st_dir = os.path.join(STUDENTS_DIR, folder_name)
    os.makedirs(st_dir, exist_ok=True)
    return st_dir

def sync_markdown_and_docx_files():
    """Generates all student Markdown portfolios, DOCX files, class logs, and the central Excel spreadsheet."""
    if not os.path.exists(STUDENTS_FILE) or not os.path.exists(OBSERVATIONS_FILE):
        return

    with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
        students = json.load(f)
    with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
        observations = json.load(f)

    # 1. Update Each Student's Folder
    for st in students:
        st_dir = get_student_dir(st)
        st_obs = [o for o in observations if o.get('student_id') == st['id'] or o.get('student_name') == st.get('name')]

        father = st.get('parent_father', {})
        mother = st.get('parent_mother', {})
        contact = st.get('contact', {})
        diag = st.get('diagnosis_info', {})
        mprof = st.get('math_profile', {})
        psprof = st.get('psychosocial_profile', {})

        # 1.1 Profile Markdown
        profile_md = f"""# Καρτέλα Μαθητή/τριας: {st.get('name', '')} {st.get('surname', '')}
**Σχολική Μονάδα:** ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης  
**Τμήμα Ένταξης (Τ.Ε.)** | Σχολικό Έτος 2026-2027  
**Εκπαιδευτικός Ε.Α.Ε.:** Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)  

---

## 1. Δημογραφικά Στοιχεία & Επικοινωνία
* **Ονοματεπώνυμο:** {st.get('name', '')} {st.get('surname', '')}
* **Κωδικός Ερευνητικού Dataset:** `{st.get('code', 'S00')}`
* **Τάξη / Τμήμα:** {st.get('grade', '')} {st.get('class_section', '')} (Α.Μ: {st.get('registration_no', '-')})
* **Ημερομηνία Γέννησης / Φύλο:** {st.get('birth_date', '-')} | {st.get('gender', '-')}
* **Στοιχεία Πατέρα:** {father.get('name', '-')} (Τηλ: {father.get('phone', '-')})
* **Στοιχεία Μητέρας:** {mother.get('name', '-')} (Τηλ: {mother.get('phone', '-')})
* **Διεύθυνση / Email:** {contact.get('address', '-')} | {contact.get('email', '-')}

---

## 2. Διαγνωστικό Ιστορικό & Γνωμάτευση ΚΕΔΑΣΥ
* **Φορέας Διάγνωσης:** {diag.get('authority', 'ΚΕΔΑΣΥ Ξάνθης')}
* **Αρ. & Ημ/νία Πρωτοκόλλου:** {diag.get('protocol_no', '-')}
* **Είδος Ειδικών Εκπαιδευτικών Αναγκών:** {diag.get('diagnosis_type', st.get('diagnosis', 'Ειδική Μαθησιακή Δυσκολία'))}
* **Ιστορικό Υποστήριξης στο Τ.Ε.:** {diag.get('support_history', 'Φοίτηση στο Τμήμα Ένταξης')}

---

## 3. Μαθησιακό & Γνωστικό Προφίλ στα Μαθηματικά
* **Μαθηματικό Άγχος:** {mprof.get('math_anxiety', 'Μέτριο')}
* **Δυνατά Σημεία:** {mprof.get('strengths', '-')}
* **Κύρια Εμπόδια:** {mprof.get('weaknesses', '-')}
* **Προτιμώμενο Μαθησιακό Στυλ:** {mprof.get('learning_style', 'Οπτικό / Πολυαισθητηριακό')}
* **Αποτελεσματικές Διδακτικές Στρατηγικές:** {mprof.get('effective_strategies', '-')}

---

## 4. Ψυχοκοινωνικό Προφίλ & Συμπεριφορά
* **Αυτοαντίληψη & Αυτοπεποίθηση:** {psprof.get('self_concept', '-')}
* **Εστίαση & Διάρκεια Προσοχής:** {psprof.get('attention_focus', '-')}
* **Κοινωνική Αλληλεπίδραση στο Τ.Ε.:** {psprof.get('social_interaction', '-')}

---
*Τελευταία ενημέρωση αρχείου: {datetime.now().strftime('%d/%m/%Y %H:%M')}*
"""
        safe_write_text(os.path.join(st_dir, '1_Στοιχεία_και_Προφίλ.md'), profile_md)

        # 1.2 Math Profile & Bloom
        math_domains = ["arithmetic", "algebra", "geometry", "stochastics"]
        math_obs = [o for o in st_obs if o.get('domain_id') in math_domains]
        
        math_md = f"""# Μαθηματικό Προφίλ, Duval & Bloom: {st['name']}
**Σχολικό Έτος:** 2026-2027 | Τμήμα Ένταξης - ΔΗΜ.Ω.Σ. Ξάνθης  

| Ημερομηνία | Τομέας | Bloom | Αναπαράσταση (Duval) | Στρατηγική / Τεχνική | Αποτέλεσμα | Εμπόδιο | Σημείωση |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
"""
        for o in sorted(math_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            duval = o.get('duval_name', o.get('duval_register', '-'))
            math_md += f"| {dt} | {o.get('domain_name','')} | {o.get('bloom_name','')} | {duval} | {o.get('strategy_name','')}: {o.get('technique','')} | [{o.get('outcome_code','+')}] | {o.get('obstacle','-')} | {o.get('raw_text','')} |\n"
            
        math_md += f"\n---\n*Σύνολο καταγεγραμμένων μαθηματικών συμβάντων: {len(math_obs)}*\n"
        safe_write_text(os.path.join(st_dir, '2_Μαθηματικό_Προφίλ_Bloom.md'), math_md)

        # 1.3 IEP Goals & 4-Level Rubric Markdown
        targets = st.get('iep_targets', [])
        rubric_map = {1: "1. Αρχικό (Πλήρης καθοδήγηση)", 2: "2. Αναδυόμενο (Μερική βοήθεια)", 3: "3. Ικανό (Αυτόνομη επίλυση)", 4: "4. Γενικευμένο (Πλήρης κατάκτηση)"}
        iep_md = f"""# Ε.Π.Ε. & Ρουμπρίκα 4 Επιπέδων: {st['name']}
**Σχολικό Έτος:** 2026-2027 | Τμήμα Ένταξης

| Α/Α | Τομέας | Διατύπωση Στόχου Ε.Π.Ε. | Στάθμη Ρουμπρίκας (1-4) | Κατάσταση |
| :---: | :--- | :--- | :--- | :---: |
"""
        for idx, t in enumerate(targets, 1):
            r_lvl = t.get('rubric_level', 2)
            r_label = rubric_map.get(r_lvl, f"Επίπεδο {r_lvl}")
            iep_md += f"| {idx} | {t.get('area','')} | {t.get('target','')} | **{r_label}** | {t.get('status','Σε εξέλιξη')} |\n"
        safe_write_text(os.path.join(st_dir, '5_Στόχοι_ΕΠΕ_και_Ρουμπρίκες.md'), iep_md)

        # 1.4 Observation Log Markdown
        st_log_md = f"""# Ημερολόγιο Παρατηρήσεων Τ.Ε.: {st['name']}

| Ημερομηνία & Ώρα | Τύπος | Τομέας | Bloom | Στρατηγική | Αποτέλεσμα | Περιγραφή |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""
        for o in sorted(st_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            ttype = o.get('target_type', 'individual')
            ttype_label = 'Ατομική' if ttype == 'individual' else ('Ομάδα' if ttype == 'group' else 'Τμήμα')
            st_log_md += f"| {dt} | {ttype_label} | {o.get('domain_name','')} | {o.get('bloom_name','')} | {o.get('strategy_name','')} | [{o.get('outcome_code','+')}] | {o.get('raw_text','')} |\n"
        safe_write_text(os.path.join(st_dir, 'Ημερολόγιο_Παρατηρήσεων.md'), st_log_md)

        # 1.5 Word (.docx) generation
        try:
            docx_generator.generate_iep_docx(st, observations, st_dir)
            docx_generator.generate_initial_assessment_docx(st, observations, st_dir)
            docx_generator.generate_rubrics_docx(st, observations, st_dir)
            docx_generator.generate_final_evaluation_docx(st, observations, st_dir)
        except Exception as e:
            print(f"[!] Warning generating docx for {st.get('name')}: {e}")

    # 2. Central Markdown Session Log
    central_md = f"""# Ημερολόγιο Συνεδριών Τμήματος Ένταξης (2026-2027)
**Σχολική Μονάδα:** ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης  
**Εκπαιδευτικός Ε.Α.Ε.:** Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)  

---

## Συγκεντρωτική Ροή Παρεμβάσεων ({len(observations)} εγγραφές)

| Ημ/νία & Ώρα | Τύπος | Μαθητής / Τμήμα | Τομέας | Bloom | Duval | Στρατηγική | Αποτέλεσμα | Περιγραφή |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""
    for o in sorted(observations, key=lambda x: x.get('timestamp', ''), reverse=True):
        dt = o.get('timestamp', '')[:16].replace('T', ' ')
        ttype = o.get('target_type', 'individual')
        tt_lbl = 'Ατομική' if ttype == 'individual' else ('Ομάδα Τ.Ε.' if ttype == 'group' else 'Τμήμα')
        duval = o.get('duval_name', o.get('duval_register', '-'))
        strat = o.get('strategy_name', '')
        if o.get('technique'):
            strat += f" ({o.get('technique')})"
        central_md += f"| {dt} | {tt_lbl} | **{o.get('student_name','')}** | {o.get('domain_name','')} | {o.get('bloom_name','-')} | {duval} | {strat} | **[{o.get('outcome_code','+')}]** | {o.get('raw_text','')} |\n"

    central_md += f"\n---\n*Τελευταία αυτόματη ενημέρωση: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n"
    safe_write_text(CENTRAL_LOG_FILE, central_md)

    # 3. Central Excel Session Log (.xlsx)
    try:
        excel_generator.generate_sessions_excel(observations, students, CENTRAL_EXCEL_FILE)
    except Exception as e:
        print(f"[!] Warning generating Excel sessions log: {e}")

    # 4. Update Research Datasets (JSON & CSV)
    safe_write_json(RESEARCH_JSON_FILE, observations)

    csv_header = "id,target_type,student_id,student_code,student_name,class_section,timestamp,domain_id,domain_name,bloom_id,bloom_name,duval_register,duval_name,strategy_id,strategy_name,technique,outcome_id,outcome_code,obstacle,obstacle_type,raw_text\n"
    student_code_map = {s['id']: s.get('code', s['name']) for s in students}
    student_sec_map = {s['id']: s.get('class_section', '') for s in students}
    csv_rows = [csv_header]
    for o in observations:
        s_id = o.get('student_id', '')
        s_code = student_code_map.get(s_id, 'S00')
        s_sec = o.get('class_section') or student_sec_map.get(s_id, '')
        clean_text = str(o.get('raw_text', '')).replace('"', '""').replace('\n', ' ')
        clean_tech = str(o.get('technique', '')).replace('"', '""')
        clean_obst = str(o.get('obstacle', '')).replace('"', '""')
        ttype = o.get('target_type', 'individual')
        row_str = f'"{o.get("id")}","{ttype}","{s_id}","{s_code}","{o.get("student_name")}","{s_sec}","{o.get("timestamp")}","{o.get("domain_id")}","{o.get("domain_name")}","{o.get("bloom_id","")}","{o.get("bloom_name","")}","{o.get("duval_register","")}","{o.get("duval_name","")}","{o.get("strategy_id","")}","{o.get("strategy_name","")}","{clean_tech}","{o.get("outcome_id")}","{o.get("outcome_code")}","{clean_obst}","{o.get("obstacle_type","")}","{clean_text}"\n'
        csv_rows.append(row_str)
    safe_write_text(RESEARCH_CSV_FILE, "".join(csv_rows))

    # 5. Update Class / Section Markdown Logs
    if os.path.exists(CLASS_OBSERVATIONS_FILE):
        with open(CLASS_OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
            class_obs = json.load(f)
        sections = set([s.get('class_section') for s in students if s.get('class_section')] + [co.get('class_section') for co in class_obs if co.get('class_section')])
        for sec in sections:
            if not sec:
                continue
            sec_obs = [co for co in class_obs if co.get('class_section') == sec]
            sec_md = f"""# Ημερολόγιο Διδασκαλίας Τμήματος Τ.Ε.: {sec}
**Σχολικό Έτος:** 2026-2027 | ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης  
**Εκπαιδευτικός Ε.Α.Ε.:** Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)  

---

## Καταγραφές Συνεδριών Τμήματος ({len(sec_obs)} εγγραφές)

| Ημερομηνία & Ώρα | Τομέας | Στρατηγική / Εμπόδιο | Αποτέλεσμα | Περιγραφή Συνεδρίας Τμήματος |
| :--- | :--- | :--- | :---: | :--- |
"""
            for co in sorted(sec_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
                dt = co.get('timestamp', '')[:16].replace('T', ' ')
                sec_md += f"| {dt} | {co.get('domain_name','-')} | {co.get('strategy_name','-')} / {co.get('obstacle','-')} | [{co.get('outcome_code','+')}] | {co.get('raw_text','')} |\n"
            safe_write_text(os.path.join(CLASSES_DIR, f"{sec}_Ημερολόγιο.md"), sec_md)

import secrets

AUTH_FILE = os.path.join(DATA_DIR, 'auth.json')
ACTIVE_SESSIONS = {}
FAILED_ATTEMPTS = {}

def get_auth_pin():
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('pin', '2026')
        except Exception:
            pass
    return '2026'

def set_auth_pin(new_pin):
    safe_write_json(AUTH_FILE, {'pin': str(new_pin).strip(), 'updated_at': datetime.now().isoformat()})

def is_client_authenticated(handler, query=None):
    auth_header = handler.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    elif query and 'token' in query:
        token = query['token'][0]
    
    if token and token in ACTIVE_SESSIONS:
        ACTIVE_SESSIONS[token]['last_seen'] = datetime.now().isoformat()
        return True
    return False

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class InclusionAppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=APP_DIR, **kwargs)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        query = urllib.parse.parse_qs(url.query)

        # Static assets
        if path == '/' or path == '/index.html':
            index_path = os.path.join(APP_DIR, 'index.html')
            if not os.path.exists(index_path):
                index_path = os.path.join(BASE_DIR, 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                return

        if path in ['/manifest.json', '/sw.js']:
            f_path = os.path.join(APP_DIR, path.lstrip('/'))
            if not os.path.exists(f_path):
                f_path = os.path.join(BASE_DIR, path.lstrip('/'))
            if os.path.exists(f_path):
                with open(f_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                mtype = 'application/manifest+json' if path.endswith('.json') else 'application/javascript'
                self.send_header('Content-Type', f'{mtype}; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
                return

        if path == '/api/auth/check':
            is_auth = is_client_authenticated(self, query)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"authenticated": is_auth}).encode('utf-8'))
            return

        # Protect all other API routes
        if path.startswith('/api/') and not path.startswith('/api/auth/'):
            if not is_client_authenticated(self, query):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Απαιτείται σύνδεση με PIN"}).encode('utf-8'))
                return

        if path == '/api/data':
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                observations = json.load(f)
            
            class_obs = []
            if os.path.exists(CLASS_OBSERVATIONS_FILE):
                with open(CLASS_OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                    class_obs = json.load(f)
            
            for st in students:
                st['coverage'] = calculate_student_coverage(st['id'])

            response_data = {
                "students": students,
                "observations": observations,
                "class_observations": class_obs,
                "taxonomy": TAXONOMY,
                "server_info": {
                    "local_ip": get_local_ip(),
                    "port": self.server.server_address[1],
                    "timestamp": datetime.now().isoformat()
                }
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/classes':
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            sections = {}
            for st in students:
                sec = st.get('class_section') or st.get('grade', 'Γενική')
                if sec not in sections:
                    sections[sec] = {"section": sec, "grade": st.get('grade', ''), "students": []}
                sections[sec]["students"].append({"id": st['id'], "name": st.get('name', ''), "surname": st.get('surname', '')})
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(list(sections.values()), ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/export_excel':
            sync_markdown_and_docx_files()
            if os.path.exists(CENTRAL_EXCEL_FILE):
                with open(CENTRAL_EXCEL_FILE, 'rb') as f:
                    excel_bytes = f.read()
                filename = os.path.basename(CENTRAL_EXCEL_FILE)
                quoted_filename = urllib.parse.quote(filename)
                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                self.send_header('Content-Disposition', f"attachment; filename*=UTF-8''{quoted_filename}")
                self.send_header('Content-Length', str(len(excel_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(excel_bytes)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        elif path == '/api/export_all_zip':
            sync_markdown_and_docx_files()
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
                # Add central files
                if os.path.exists(CENTRAL_EXCEL_FILE):
                    z.write(CENTRAL_EXCEL_FILE, os.path.basename(CENTRAL_EXCEL_FILE))
                if os.path.exists(CENTRAL_LOG_FILE):
                    z.write(CENTRAL_LOG_FILE, os.path.basename(CENTRAL_LOG_FILE))
                if os.path.exists(RESEARCH_CSV_FILE):
                    z.write(RESEARCH_CSV_FILE, os.path.basename(RESEARCH_CSV_FILE))
                if os.path.exists(RESEARCH_JSON_FILE):
                    z.write(RESEARCH_JSON_FILE, os.path.basename(RESEARCH_JSON_FILE))
                
                # Add student portfolios
                for root, dirs, files in os.walk(STUDENTS_DIR):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        z.write(full_p, rel_p)

                # Add class logs
                for root, dirs, files in os.walk(CLASSES_DIR):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        z.write(full_p, rel_p)

            zip_bytes = zip_buffer.getvalue()
            filename = f"Χαρτοφυλάκιο_ΤΕ_Ξάνθης_{datetime.now().strftime('%Y%m%d')}.zip"
            quoted_filename = urllib.parse.quote(filename)
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f"attachment; filename*=UTF-8''{quoted_filename}")
            self.send_header('Content-Length', str(len(zip_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(zip_bytes)
            return

        elif path == '/api/backup/download':
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, dirs, files in os.walk(DATA_DIR):
                    if 'backups' in root:
                        continue
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, BASE_DIR)
                        z.write(full_p, rel_p)
            zip_bytes = zip_buffer.getvalue()
            filename = f"Backup_TE_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            quoted_filename = urllib.parse.quote(filename)
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f"attachment; filename*=UTF-8''{quoted_filename}")
            self.send_header('Content-Length', str(len(zip_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(zip_bytes)
            return

        elif path == '/api/export_docx':
            student_id = query.get('student_id', [''])[0]
            doc_type = query.get('doc_type', ['iep'])[0]
            
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                observations = json.load(f)

            student = next((s for s in students if s['id'] == student_id), None)
            if not student:
                self.send_response(404)
                self.end_headers()
                return

            st_dir = get_student_dir(student)
            try:
                if doc_type == 'iep':
                    doc_path = docx_generator.generate_iep_docx(student, observations, st_dir)
                elif doc_type == 'aa':
                    doc_path = docx_generator.generate_initial_assessment_docx(student, observations, st_dir)
                elif doc_type == 'rubrics':
                    doc_path = docx_generator.generate_rubrics_docx(student, observations, st_dir)
                elif doc_type == 'ta':
                    doc_path = docx_generator.generate_final_evaluation_docx(student, observations, st_dir)
                else:
                    doc_path = docx_generator.generate_iep_docx(student, observations, st_dir)

                with open(doc_path, 'rb') as f:
                    file_bytes = f.read()

                filename = os.path.basename(doc_path)
                quoted_filename = urllib.parse.quote(filename)

                self.send_response(200)
                self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                self.send_header('Content-Disposition', f"attachment; filename*=UTF-8''{quoted_filename}")
                self.send_header('Content-Length', str(len(file_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(file_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
                return

        return super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == '/api/auth/login':
            client_ip = self.client_address[0]
            pin = str(payload.get('pin', '')).strip()
            now_ts = datetime.now().timestamp()
            fail_info = FAILED_ATTEMPTS.get(client_ip, {'count': 0, 'last_failed': 0})
            if fail_info['count'] >= 5 and (now_ts - fail_info['last_failed']) < 300:
                self.send_response(429)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Πάρα πολλές αποτυχημένες προσπάθειες. Δοκιμάστε ξανά σε 5 λεπτά."}).encode('utf-8'))
                return

            correct_pin = get_auth_pin()
            if pin == correct_pin:
                token = secrets.token_hex(24)
                ACTIVE_SESSIONS[token] = {
                    'created_at': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat(),
                    'ip': client_ip
                }
                if client_ip in FAILED_ATTEMPTS:
                    del FAILED_ATTEMPTS[client_ip]
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "token": token}).encode('utf-8'))
                return
            else:
                FAILED_ATTEMPTS[client_ip] = {
                    'count': fail_info['count'] + 1,
                    'last_failed': now_ts
                }
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Λάθος PIN ασφαλείας."}).encode('utf-8'))
                return

        if path == '/api/auth/change_pin':
            if not is_client_authenticated(self):
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Unauthorized"}).encode('utf-8'))
                return
            old_pin = str(payload.get('old_pin', '')).strip()
            new_pin = str(payload.get('new_pin', '')).strip()
            if old_pin != get_auth_pin():
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Το παλιό PIN δεν είναι σωστό."}).encode('utf-8'))
                return
            if len(new_pin) < 4:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Το νέο PIN πρέπει να έχει τουλάχιστον 4 ψηφία."}).encode('utf-8'))
                return
            set_auth_pin(new_pin)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "message": "Το PIN ενημερώθηκε επιτυχώς."}).encode('utf-8'))
            return

        # Protect all other POST APIs
        if path.startswith('/api/') and not is_client_authenticated(self):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "Απαιτείται σύνδεση με PIN"}).encode('utf-8'))
            return

        if path == '/api/ai_analyze':
            text = payload.get('text', '')
            current_st_id = payload.get('current_student_id')
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
            analysis = ai_analyzer.analyze_observation_text(text, students, current_st_id)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(analysis, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/observation':
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                observations = json.load(f)
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)

            raw_text = payload.get('raw_text', '')
            target_type = payload.get('target_type', 'individual')
            student_ids = payload.get('student_ids', [])
            class_section = payload.get('class_section')

            # Auto-enrich with AI
            if raw_text:
                enriched = ai_analyzer.analyze_observation_text(raw_text, students=students)
                for k in ["domain_id", "domain_name", "bloom_id", "bloom_name", "strategy_id", "strategy_name", 
                          "obstacle", "obstacle_type", "obstacle_type_name", "duval_register", "duval_name", "duval_icon",
                          "outcome_id", "outcome_code", "outcome_name"]:
                    if not payload.get(k) or payload.get(k) in ["-", "", "undefined"]:
                        if k in enriched:
                            payload[k] = enriched[k]
                if not target_type or target_type == 'individual':
                    target_type = enriched.get('target_type', 'individual')
                    payload['target_type'] = target_type

            # Case 1: Class-level observation
            if target_type == 'class' or (class_section and not payload.get('student_id') and not student_ids):
                class_obs_list = []
                if os.path.exists(CLASS_OBSERVATIONS_FILE):
                    with open(CLASS_OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                        class_obs_list = json.load(f)
                
                c_id = payload.get('id') or f"cobs_{int(datetime.now().timestamp() * 1000)}"
                payload['id'] = c_id
                payload['target_type'] = 'class'
                payload['class_section'] = class_section or payload.get('class_section', 'Γενική')
                if not payload.get('timestamp'):
                    payload['timestamp'] = datetime.now().isoformat()
                
                class_obs_list.insert(0, payload)
                safe_write_json(CLASS_OBSERVATIONS_FILE, class_obs_list)
                sync_markdown_and_docx_files()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "observation": payload, "type": "class"}, ensure_ascii=False).encode('utf-8'))
                return

            # Case 2: Multi-student Group observation
            created_entries = []
            if target_type == 'group' and len(student_ids) > 1:
                group_id = f"grp_{int(datetime.now().timestamp())}"
                for s_id in student_ids:
                    st_obj = next((s for s in students if s['id'] == s_id), None)
                    single_item = copy.deepcopy(payload)
                    single_item['id'] = f"obs_{int(datetime.now().timestamp() * 1000)}_{s_id}"
                    single_item['student_id'] = s_id
                    single_item['student_name'] = st_obj.get('name', 'Μαθητής') if st_obj else 'Μαθητής'
                    single_item['class_section'] = st_obj.get('class_section', '') if st_obj else ''
                    single_item['target_type'] = 'group'
                    single_item['group_id'] = group_id
                    if not single_item.get('timestamp'):
                        single_item['timestamp'] = datetime.now().isoformat()
                    observations.insert(0, single_item)
                    created_entries.append(single_item)
            else:
                # Single Student observation
                obs_id = payload.get('id') or f"obs_{int(datetime.now().timestamp() * 1000)}"
                payload['id'] = obs_id
                payload['target_type'] = 'individual'
                if not payload.get('timestamp'):
                    payload['timestamp'] = datetime.now().isoformat()
                
                st_id = payload.get('student_id')
                if st_id:
                    st_obj = next((s for s in students if s['id'] == st_id), None)
                    if st_obj:
                        payload['student_name'] = st_obj.get('name', '')
                        payload['class_section'] = st_obj.get('class_section', '')
                
                existing_idx = next((i for i, o in enumerate(observations) if o.get('id') == obs_id), -1)
                if existing_idx >= 0:
                    observations[existing_idx] = payload
                else:
                    observations.insert(0, payload)
                created_entries.append(payload)

            safe_write_json(OBSERVATIONS_FILE, observations)

            # Update student coverage
            for st in students:
                st['coverage'] = calculate_student_coverage(st['id'])
            safe_write_json(STUDENTS_FILE, students)

            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "observations": created_entries}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/student/iep_rubric_update':
            student_id = payload.get('student_id')
            target_id = payload.get('target_id')
            rubric_level = int(payload.get('rubric_level', 2))
            status = payload.get('status')
            
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)

            student = next((s for s in students if s['id'] == student_id), None)
            if not student:
                self.send_response(404)
                self.end_headers()
                return

            targets = student.get('iep_targets', [])
            target = next((t for t in targets if t.get('id') == target_id), None)
            if target:
                target['rubric_level'] = rubric_level
                target['rubric_updated_at'] = datetime.now().isoformat()
                if status:
                    target['status'] = status
                elif rubric_level == 4:
                    target['status'] = "Επιτεύχθηκε"
                elif rubric_level >= 2:
                    target['status'] = "Σε εξέλιξη"
                else:
                    target['status'] = "Αρχικό στάδιο"

            safe_write_json(STUDENTS_FILE, students)
            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "target": target, "student": student}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/student':
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)

            st_id = payload.get('id') or f"st_{len(students) + 1}"
            payload['id'] = st_id
            if not payload.get('created_at'):
                payload['created_at'] = datetime.now().isoformat()

            existing_idx = next((i for i, s in enumerate(students) if s.get('id') == st_id), -1)
            if existing_idx >= 0:
                students[existing_idx] = payload
            else:
                students.append(payload)

            safe_write_json(STUDENTS_FILE, students)
            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "student": payload}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/edit_observation':
            obs_id = payload.get('id')
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                observations = json.load(f)
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)

            if payload.get('raw_text'):
                enriched = ai_analyzer.enrich_observation_payload(payload, students=students)
                payload.update(enriched)

            existing_idx = next((i for i, o in enumerate(observations) if o.get('id') == obs_id), -1)
            if existing_idx >= 0:
                original_ts = observations[existing_idx].get('timestamp')
                payload['timestamp'] = original_ts if original_ts else (payload.get('timestamp') or datetime.now().isoformat())
                payload['updated_at'] = datetime.now().isoformat()
                observations[existing_idx] = payload
            else:
                payload['id'] = obs_id or f"obs_{int(datetime.now().timestamp()*1000)}"
                if not payload.get('timestamp'):
                    payload['timestamp'] = datetime.now().isoformat()
                observations.append(payload)

            safe_write_json(OBSERVATIONS_FILE, observations)
            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "observation": payload}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/delete_observation':
            obs_id = payload.get('id')
            with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
                observations = json.load(f)
            
            observations = [o for o in observations if o.get('id') != obs_id]
            safe_write_json(OBSERVATIONS_FILE, observations)
            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def auto_open_browser(port):
    time.sleep(0.6)
    url = f"http://localhost:{port}"
    try:
        webbrowser.open(url)
    except Exception:
        pass

def run_server(port=8080):
    init_default_data()
    sync_markdown_and_docx_files()
    
    local_ip = get_local_ip()
    print("=" * 70)
    print("  ΕΞΥΠΝΟΣ ΒΟΗΘΟΣ & ΚΑΡΤΕΛΑ ΜΑΘΗΤΗ ΤΜΗΜΑΤΟΣ ΕΝΤΑΞΗΣ (Τ.Ε.)")
    print("  ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης - Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)")
    print("=" * 70)
    print(f"[*] Τοπική πρόσβαση από αυτόν τον Υπολογιστή: http://localhost:{port}")
    print(f"[*] Άμεση πρόσβαση από το Xiaomi Pad 6 (Tablet): http://{local_ip}:{port}")
    print("=" * 70)
    print("[+] Αυτόματος συγχρονισμός: Word (.docx), Excel (.xlsx), Markdown και Dataset.")
    print(f"[+] Κυλιόμενα αντίγραφα ασφαλείας (Backups) ενεργά στο: {BACKUPS_DIR}")
    
    server_address = ('', port)
    try:
        httpd = ThreadingHTTPServer(server_address, InclusionAppHandler)
        threading.Thread(target=auto_open_browser, args=(port,), daemon=True).start()
        httpd.serve_forever()
    except OSError as e:
        if port < 8090:
            run_server(port + 1)
        else:
            raise e

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
