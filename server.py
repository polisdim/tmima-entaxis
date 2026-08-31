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
import webbrowser
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

import docx_generator
import ai_analyzer

# Set working directory to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, 'data')
STUDENTS_DIR = os.path.join(BASE_DIR, 'Μαθητές')
APP_DIR = os.path.join(BASE_DIR, 'app')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STUDENTS_DIR, exist_ok=True)
os.makedirs(APP_DIR, exist_ok=True)

STUDENTS_FILE = os.path.join(DATA_DIR, 'students.json')
OBSERVATIONS_FILE = os.path.join(DATA_DIR, 'observations.json')
CENTRAL_LOG_FILE = os.path.join(BASE_DIR, 'Ημερολόγιο_Συνεδριών_2026-2027.md')
RESEARCH_JSON_FILE = os.path.join(BASE_DIR, 'Ερευνητικό_Dataset_ΤΕ.json')
RESEARCH_CSV_FILE = os.path.join(BASE_DIR, 'Ερευνητικό_Dataset_ΤΕ.csv')

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
        {"id": "iep_goals", "name": "Στόχοι Ε.Π.Ε.", "color": "#f97316", "icon": "🎯", "desc": "Βραχυπρόθεσμοι & μακροπρόθεσμοι στόχοι, ρουμπρίκες"}
    ],
    "bloom_levels": [
        {"id": "remembering", "level": 1, "name": "1. Ανάκληση", "desc": "Ανάκληση ορισμών, κανόνων, προπαίδειας, συμβόλων, γεγονότων"},
        {"id": "understanding", "level": 2, "name": "2. Κατανόηση", "desc": "Ερμηνεία, εξήγηση με δικά του λόγια, διαγραμματική αναπαράσταση"},
        {"id": "applying", "level": 3, "name": "3. Εφαρμογή", "desc": "Εκτέλεση αλγορίθμου, επίλυση ασκήσεων, εφαρμογή μεθόδου"},
        {"id": "analyzing", "level": 4, "name": "4. Ανάλυση", "desc": "Διάσπαση προβλήματος, διάκριση δεδομένων/ζητουμένων, σχέσεις"},
        {"id": "evaluating", "level": 5, "name": "5. Αξιολόγηση", "desc": "Έλεγχος λογικότητας αποτελέσματος, εντοπισμός σφάλματος, επιλογή στρατηγικής"},
        {"id": "creating", "level": 6, "name": "6. Δημιουργία", "desc": "Κατασκευή δικού του προβλήματος, γενίκευση, πρωτότυπη σύνθεση"}
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
    "obstacles": [
        {"domain": "arithmetic", "name": "Διαίρεση & Διαχείριση Μηδενός"},
        {"domain": "arithmetic", "name": "Κλάσματα (Σύγχυση Αριθμητή/Παρονομαστή)"},
        {"domain": "arithmetic", "name": "Δανεισμός / Κρατούμενο στην Αφαίρεση"},
        {"domain": "arithmetic", "name": "Αριθμητική Αίσθηση (Subitizing / Μέγεθος)"},
        {"domain": "algebra", "name": "Σφάλμα του Ίσον (= ως πράξη)"},
        {"domain": "algebra", "name": "Μεταβλητή (x ως ετικέτα αντί ποσότητας)"},
        {"domain": "algebra", "name": "Κανόνες Προσήμων & Παρενθέσεων"},
        {"domain": "algebra", "name": "Μετάφραση Λεκτικού σε Εξίσωση"},
        {"domain": "geometry", "name": "Σύγχυση Περιμέτρου (1D) και Εμβαδού (2D)"},
        {"domain": "geometry", "name": "Χωρική Περιστροφή & Μη-τυπικός Προσανατολισμός"},
        {"domain": "geometry", "name": "Αποκωδικοποίηση Γεωμετρικών Συμβόλων"},
        {"domain": "stochastics", "name": "Παραδρομή του Τζογαδόρου (Τυχαιότητα)"},
        {"domain": "stochastics", "name": "Παρερμηνεία Αξόνων & Κλίμακας Διαγραμμάτων"},
        {"domain": "stochastics", "name": "Σύγχυση Μέσης Τιμής και Διαμέσου"},
        {"domain": "engagement", "name": "Διάσπαση Προσοχής / Κόπωση"},
        {"domain": "engagement", "name": "Ελλιπής Προετοιμασία / Απώλεια Τετραδίου"},
        {"domain": "socioemotional", "name": "Μαθηματικό Άγχος / Φόβος Λάθους"},
        {"domain": "socioemotional", "name": "Χαμηλή Ανοχή στη Ματαίωση"}
    ]
}

def init_default_data():
    if not os.path.exists(STUDENTS_FILE):
        default_students = [
            {
                "id": "st_1",
                "name": "Μιχαέλα",
                "code": "S01",
                "gender": "Κορίτσι",
                "grade": "Β' Γυμνασίου",
                "class_section": "Β1",
                "diagnosis": "Ειδική Μαθησιακή Δυσκολία (Δυσαριθμησία & Δυσλεξία) - Γνωμάτευση ΚΕΔΑΣΥ Ξάνθης",
                "hours_per_week": 4,
                "notes": "Ιδιαίτερα συνεργάσιμη. Βοηθάται σημαντικά από οπτικά βοηθήματα και αναπαραστάσεις.",
                "created_at": "2026-08-31T10:00:00",
                "iep_targets": [
                    {"id": "t1", "area": "Αριθμητική", "target": "Αυτοματοποίηση πράξεων κλασμάτων (ετερώνυμα)", "status": "Σε εξέλιξη"},
                    {"id": "t2", "area": "Άλγεβρα", "target": "Επίλυση πρωτοβάθμιων εξισώσεων ax+b=c με χρωματική κωδικοποίηση", "status": "Σε εξέλιξη"},
                    {"id": "t3", "area": "Γεωμετρία", "target": "Διάκριση περιμέτρου και εμβαδού σε ορθογώνια και τρίγωνα", "status": "Σε εξέλιξη"},
                    {"id": "t4", "area": "Συμπεριφορά", "target": "Ενίσχυση αυτοπεποίθησης και μείωση μαθηματικού άγχους", "status": "Επιτεύχθηκε"}
                ],
                "coverage": {
                    "arithmetic": 65,
                    "algebra": 80,
                    "geometry": 45,
                    "stochastics": 30,
                    "engagement": 90,
                    "socioemotional": 85,
                    "collaboration_family": 70,
                    "iep_goals": 75,
                    "total": 67
                }
            },
            {
                "id": "st_2",
                "name": "Νίκος",
                "code": "S02",
                "gender": "Αγόρι",
                "grade": "Α' Γυμνασίου",
                "class_section": "Α2",
                "diagnosis": "ΔΕΠ-Υ (Διάσπαση Προσοχής) & Δυσκολίες στην Υπολογιστική Ευχέρεια",
                "hours_per_week": 3,
                "notes": "Υψηλή ενέργεια. Χρειάζεται μικρά διαλείμματα, λίστες ελέγχου (checklists) και άμεση επιβράβευση.",
                "created_at": "2026-08-31T10:30:00",
                "iep_targets": [
                    {"id": "t1", "area": "Αριθμητική", "target": "Κατάκτηση προπαίδειας και πράξεων ακεραίων με αριθμογραμμή", "status": "Σε εξέλιξη"},
                    {"id": "t2", "area": "Εμπλοκή", "target": "Διατήρηση προσοχής για 20 συνεχόμενα λεπτά με αυτορρύθμιση", "status": "Σε εξέλιξη"}
                ],
                "coverage": {
                    "arithmetic": 70,
                    "algebra": 40,
                    "geometry": 50,
                    "stochastics": 20,
                    "engagement": 85,
                    "socioemotional": 75,
                    "collaboration_family": 80,
                    "iep_goals": 60,
                    "total": 60
                }
            }
        ]
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_students, f, ensure_ascii=False, indent=2)

    if not os.path.exists(OBSERVATIONS_FILE):
        default_observations = [
            {
                "id": "obs_1",
                "student_id": "st_1",
                "student_name": "Μιχαέλα",
                "timestamp": "2026-08-31T11:15:00",
                "domain_id": "arithmetic",
                "domain_name": "Αριθμητική",
                "bloom_id": "applying",
                "bloom_name": "3. Εφαρμογή",
                "strategy_id": "color_coding",
                "strategy_name": "Χρωματική Κωδικοποίηση",
                "technique": "Χρωματική διάκριση αριθμητή (μπλε) και παρονομαστή (κόκκινο)",
                "outcome_id": "positive",
                "outcome_code": "+",
                "outcome_name": "Υψηλή Επιτυχία / Θετικό",
                "obstacle": "Κλάσματα (Σύγχυση Αριθμητή/Παρονομαστή)",
                "raw_text": "Η Μιχαέλα κατανόησε άμεσα την πρόσθεση ομωνύμων κλασμάτων όταν χρησιμοποιήσαμε χρωματική κωδικοποίηση για τον αριθμητή και τον παρονομαστή.",
                "notes": "Η τεχνική λειτούργησε άριστα. Επόμενο βήμα τα ετερώνυμα."
            },
            {
                "id": "obs_2",
                "student_id": "st_1",
                "student_name": "Μιχαέλα",
                "timestamp": "2026-08-31T11:45:00",
                "domain_id": "algebra",
                "domain_name": "Άλγεβρα",
                "bloom_id": "understanding",
                "bloom_name": "2. Κατανόηση",
                "strategy_id": "mind_maps",
                "strategy_name": "Νοητικοί Χάρτες",
                "technique": "Διάγραμμα ροής βημάτων επίλυσης πρωτοβάθμιας εξίσωσης",
                "outcome_id": "positive",
                "outcome_code": "+",
                "outcome_name": "Υψηλή Επιτυχία / Θετικό",
                "obstacle": "Σφάλμα του Ίσον (= ως πράξη)",
                "raw_text": "Ο νοητικός χάρτης βημάτων βοήθησε τη Μιχαέλα να ξεπεράσει τη σύγχυση του συμβόλου ίσον στην εξίσωση.",
                "notes": "Ανέκτησε αυτοπεποίθηση στη μετάβαση όρων."
            }
        ]
        with open(OBSERVATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_observations, f, ensure_ascii=False, indent=2)

def calculate_student_coverage(student_id):
    with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
        observations = json.load(f)
    
    student_obs = [o for o in observations if o.get('student_id') == student_id]
    domains = ["arithmetic", "algebra", "geometry", "stochastics", "engagement", "socioemotional", "collaboration_family", "iep_goals"]
    coverage = {}
    
    for d in domains:
        obs_d = [o for o in student_obs if o.get('domain_id') == d]
        if not obs_d:
            coverage[d] = 10
        else:
            bloom_count = len(set(o.get('bloom_id') for o in obs_d if o.get('bloom_id')))
            count = len(obs_d)
            pct = min(100, 25 + (count * 15) + (bloom_count * 10))
            coverage[d] = pct
            
    total_pct = int(sum(coverage.values()) / len(domains))
    coverage["total"] = total_pct
    return coverage

def get_student_dir(student):
    """
    Returns the hierarchical directory path for a student based on their class/grade.
    E.g. 'Μαθητές/Α_Γυμνασίου/Νίκος' or 'Μαθητές/Β_Γυμνασίου/Μιχαέλα'
    """
    st_name = student.get('name', 'Μαθητής')
    grade_str = str(student.get('grade', '')).strip()
    section_str = str(student.get('class_section', '')).strip().upper()
    
    if section_str.startswith(('Α', 'A')) or grade_str.startswith(('Α', 'A', "Α'", "A'")):
        grade_folder = "Α_Γυμνασίου"
    elif section_str.startswith(('Β', 'B')) or grade_str.startswith(('Β', 'B', "Β'", "B'")):
        grade_folder = "Β_Γυμνασίου"
    elif section_str.startswith(('Γ', 'C')) or grade_str.startswith(('Γ', 'C', "Γ'", "C'")):
        grade_folder = "Γ_Γυμνασίου"
    else:
        grade_folder = "Γενικό_Αρχείο_Μαθητών"
        
    st_dir = os.path.join(STUDENTS_DIR, grade_folder, st_name)
    os.makedirs(st_dir, exist_ok=True)
    return st_dir

def sync_markdown_and_docx_files():
    """Generates and syncs student Markdown and Word (.docx) files grouped by grade."""
    with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
        students = json.load(f)
    with open(OBSERVATIONS_FILE, 'r', encoding='utf-8') as f:
        observations = json.load(f)

    # 1. Update Student Folders (Markdown & Docx) grouped by grade
    for st in students:
        st_name = st['name']
        st_dir = get_student_dir(st)
        
        st_obs = [o for o in observations if o.get('student_id') == st['id'] or o.get('student_name') == st_name]
        
        # 1.1 Profile Markdown
        profile_md = f"""# Καρτέλα Μαθητή: {st['name']} ({st.get('code', 'S00')})
**Τάξη / Τμήμα:** {st.get('grade', '')} {st.get('class_section', '')}  
**Φύλο:** {st.get('gender', '')}  
**Εβδομαδιαίες Ώρες Τ.Ε.:** {st.get('hours_per_week', 3)}  
**Διάγνωση / ΕΕΑ:** {st.get('diagnosis', 'Εκκρεμεί')}  
**Ημερομηνία Εγγραφής:** {st.get('created_at', '')[:10]}  

---

## Α. Γενικό Προφίλ & Παρατηρήσεις
{st.get('notes', 'Δεν έχουν καταχωρηθεί γενικές σημειώσεις.')}

---

## Β. Πληρότητα Χαρτογράφησης Μαθησιακού Προφίλ (Coverage %)
* **Συνολική Πληρότητα:** {st.get('coverage', {}).get('total', 0)}%
* **Αριθμητική:** {st.get('coverage', {}).get('arithmetic', 0)}%
* **Άλγεβρα:** {st.get('coverage', {}).get('algebra', 0)}%
* **Γεωμετρία:** {st.get('coverage', {}).get('geometry', 0)}%
* **Στοχαστικά:** {st.get('coverage', {}).get('stochastics', 0)}%
* **Μαθησιακή Εμπλοκή & Συνέπεια:** {st.get('coverage', {}).get('engagement', 0)}%
* **Ψυχοσυναισθηματικός Τομέας:** {st.get('coverage', {}).get('socioemotional', 0)}%
* **Συνεργασία & Οικογένεια:** {st.get('coverage', {}).get('collaboration_family', 0)}%
* **Στόχοι Ε.Π.Ε.:** {st.get('coverage', {}).get('iep_goals', 0)}%

---
*Τελευταία ενημέρωση αρχείου: {datetime.now().strftime('%d/%m/%Y %H:%M')}*
"""
        with open(os.path.join(st_dir, '1_Στοιχεία_και_Προφίλ.md'), 'w', encoding='utf-8') as f:
            f.write(profile_md)

        # 1.2 Math Profile & Bloom Markdown
        math_domains = ["arithmetic", "algebra", "geometry", "stochastics"]
        math_obs = [o for o in st_obs if o.get('domain_id') in math_domains]
        
        math_md = f"""# Μαθηματικό Προφίλ & Ταξινομία Bloom: {st['name']}
**Σχολικό Έτος:** 2026-2027  
**Εκπαιδευτικός:** Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)  

---

## Ιστορικό Μαθηματικών Παρεμβάσεων ανά Τομέα

| Ημερομηνία | Τομέας | Επίπεδο Bloom | Στρατηγική / Τεχνική | Αποτέλεσμα | Ειδικό Εμπόδιο | Σημείωση |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
"""
        for o in sorted(math_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            math_md += f"| {dt} | {o.get('domain_name','')} | {o.get('bloom_name','')} | {o.get('strategy_name','')}: {o.get('technique','')} | [{o.get('outcome_code','+')}] | {o.get('obstacle','-')} | {o.get('raw_text','')} |\n"
            
        math_md += f"\n---\n*Σύνολο καταγεγραμμένων μαθηματικών συμβάντων: {len(math_obs)}*\n"
        with open(os.path.join(st_dir, '2_Μαθηματικό_Προφίλ_Bloom.md'), 'w', encoding='utf-8') as f:
            f.write(math_md)

        # 1.3 Behavioral & Engagement Markdown
        eng_obs = [o for o in st_obs if o.get('domain_id') == 'engagement']
        eng_md = f"""# Μαθησιακή Εμπλοκή, Συνέπεια & Προετοιμασία: {st['name']}
**Τομείς Εστίασης:** Συνέπεια, Προετοιμασία τετραδίων/υλικών, Συγκέντρωση, Αυτορρύθμιση.

---

## Καταγραφές Εμπλοκής

| Ημερομηνία | Περιγραφή Παρατήρησης | Αποτέλεσμα | Σημείωση Εκπαιδευτικού |
| :--- | :--- | :---: | :--- |
"""
        for o in sorted(eng_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            eng_md += f"| {dt} | {o.get('raw_text','')} | [{o.get('outcome_code','+')}] | {o.get('notes','')} |\n"
        with open(os.path.join(st_dir, '3_Συμπεριφορά_και_Εμπλοκή.md'), 'w', encoding='utf-8') as f:
            f.write(eng_md)

        # 1.4 Socioemotional Markdown
        soc_obs = [o for o in st_obs if o.get('domain_id') in ['socioemotional', 'collaboration_family']]
        soc_md = f"""# Κοινωνικοσυναισθηματικό Προφίλ & Συνεργασία: {st['name']}
**Τομείς Εστίασης:** Αυτοεικόνα, Μαθηματικό Άγχος, Σχέσεις με συνομηλίκους, Συνεργασία με γονείς & φορείς.

---

## Καταγραφές & Κρίσιμα Συμβάντα

| Ημερομηνία | Θεματική | Περιγραφή Συμβάντος | Αποτέλεσμα |
| :--- | :--- | :--- | :---: |
"""
        for o in sorted(soc_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            soc_md += f"| {dt} | {o.get('domain_name','')} | {o.get('raw_text','')} | [{o.get('outcome_code','+')}] |\n"
        with open(os.path.join(st_dir, '4_Κοινωνικοσυναισθηματικά.md'), 'w', encoding='utf-8') as f:
            f.write(soc_md)

        # 1.5 IEP Goals & Rubrics Markdown
        targets = st.get('iep_targets', [])
        iep_md = f"""# Εξατομικευμένο Πρόγραμμα Εκπαίδευσης (Ε.Π.Ε.) & Ρουμπρίκες: {st['name']}
**Σχολικό Έτος:** 2026-2027  
**Επιτροπή Διεπιστημονικής Υποστήριξης (ΕΔΥ) / Τμήμα Ένταξης**  

---

## Στοχοθεσία Ε.Π.Ε. (Βραχυπρόθεσμοι & Μακροπρόθεσμοι Στόχοι)

| Α/Α | Τομέας | Διατύπωση Στόχου | Κατάσταση |
| :---: | :--- | :--- | :---: |
"""
        for idx, t in enumerate(targets, 1):
            iep_md += f"| {idx} | {t.get('area','')} | {t.get('target','')} | **{t.get('status','Σε εξέλιξη')}** |\n"
        with open(os.path.join(st_dir, '5_Στόχοι_ΕΠΕ_και_Ρουμπρίκες.md'), 'w', encoding='utf-8') as f:
            f.write(iep_md)

        # 1.6 Full Student Observation Log
        st_log_md = f"""# Ημερολόγιο Παρατηρήσεων & Διδακτικών Συμβάντων: {st['name']}

| Ημερομηνία & Ώρα | Τομέας | Bloom | Στρατηγική | Αποτέλεσμα | Περιγραφή |
| :--- | :--- | :--- | :--- | :---: | :--- |
"""
        for o in sorted(st_obs, key=lambda x: x.get('timestamp', ''), reverse=True):
            dt = o.get('timestamp', '')[:16].replace('T', ' ')
            st_log_md += f"| {dt} | {o.get('domain_name','')} | {o.get('bloom_name','')} | {o.get('strategy_name','')} | [{o.get('outcome_code','+')}] | {o.get('raw_text','')} |\n"
        with open(os.path.join(st_dir, 'Ημερολόγιο_Παρατηρήσεων.md'), 'w', encoding='utf-8') as f:
            f.write(st_log_md)

        # 1.7 AUTO-GENERATE OFFICIAL WORD (.DOCX) DOCUMENTS
        try:
            docx_generator.generate_iep_docx(st, observations, st_dir)
            docx_generator.generate_initial_assessment_docx(st, observations, st_dir)
            docx_generator.generate_rubrics_docx(st, observations, st_dir)
            docx_generator.generate_final_evaluation_docx(st, observations, st_dir)
        except Exception as e:
            print(f"[!] Warning generating docx for {st_name}: {e}")

    # 2. Update Central Session Log
    central_md = f"""# Ημερολόγιο Συνεδριών Τμήματος Ένταξης (2026-2027)
**Σχολική Μονάδα:** ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης  
**Εκπαιδευτικός:** Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)  
**Πλαίσιο:** Ειδική Διδακτική Μαθηματικών & Ολόπλευρη Παρέμβαση  

---

## Συγκεντρωτική Ροή Παρατηρήσεων ({len(observations)} εγγραφές)

| Ημ/νία & Ώρα | Μαθητής | Θεματικός Τομέας | Επίπεδο Bloom | Στρατηγική / Τεχνική | Αποτέλεσμα | Σημείωση / Περιγραφή Παρατήρησης |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""
    for o in sorted(observations, key=lambda x: x.get('timestamp', ''), reverse=True):
        dt = o.get('timestamp', '')[:16].replace('T', ' ')
        strat = o.get('strategy_name', '')
        if o.get('technique'):
            strat += f" ({o.get('technique')})"
        central_md += f"| {dt} | **{o.get('student_name','')}** | {o.get('domain_name','')} | {o.get('bloom_name','-')} | {strat} | **[{o.get('outcome_code','+')}]** | {o.get('raw_text','')} |\n"

    central_md += f"\n---\n*Τελευταία αυτόματη ενημέρωση: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n"
    with open(CENTRAL_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(central_md)

    # 3. Update Research Dataset
    with open(RESEARCH_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(observations, f, ensure_ascii=False, indent=2)

    with open(RESEARCH_CSV_FILE, 'w', encoding='utf-8-sig') as f:
        f.write("id,student_id,student_code,student_name,timestamp,domain_id,domain_name,bloom_id,bloom_name,strategy_id,strategy_name,technique,outcome_id,outcome_code,obstacle,raw_text\n")
        student_code_map = {s['id']: s.get('code', s['name']) for s in students}
        for o in observations:
            s_code = student_code_map.get(o.get('student_id'), 'S00')
            clean_text = o.get('raw_text', '').replace('"', '""').replace('\n', ' ')
            clean_tech = o.get('technique', '').replace('"', '""')
            clean_obst = o.get('obstacle', '').replace('"', '""')
            f.write(f'"{o.get("id")}","{o.get("student_id")}","{s_code}","{o.get("student_name")}","{o.get("timestamp")}","{o.get("domain_id")}","{o.get("domain_name")}","{o.get("bloom_id","")}","{o.get("bloom_name","")}","{o.get("strategy_id","")}","{o.get("strategy_name","")}","{clean_tech}","{o.get("outcome_id")}","{o.get("outcome_code")}","{clean_obst}","{clean_text}"\n')

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
    with open(AUTH_FILE, 'w', encoding='utf-8') as f:
        json.dump({'pin': str(new_pin).strip(), 'updated_at': datetime.now().isoformat()}, f, indent=2)

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

        if path == '/api/auth/check':
            is_auth = is_client_authenticated(self, query)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"authenticated": is_auth}).encode('utf-8'))
            return

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
            
            for st in students:
                st['coverage'] = calculate_student_coverage(st['id'])

            response_data = {
                "students": students,
                "observations": observations,
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

            st_name = student.get('name', 'Μαθητής')
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

            # Auto-enrich with AI
            if payload.get('raw_text'):
                payload = ai_analyzer.enrich_observation_payload(payload, students=students)

            obs_id = payload.get('id') or f"obs_{int(datetime.now().timestamp() * 1000)}"
            payload['id'] = obs_id
            if not payload.get('timestamp'):
                payload['timestamp'] = datetime.now().isoformat()

            existing_idx = next((i for i, o in enumerate(observations) if o.get('id') == obs_id), -1)
            if existing_idx >= 0:
                observations[existing_idx] = payload
            else:
                observations.insert(0, payload)

            with open(OBSERVATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(observations, f, ensure_ascii=False, indent=2)

            if payload.get('student_id'):
                for st in students:
                    if st['id'] == payload['student_id']:
                        st['coverage'] = calculate_student_coverage(st['id'])
                with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(students, f, ensure_ascii=False, indent=2)

            sync_markdown_and_docx_files()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "observation": payload}, ensure_ascii=False).encode('utf-8'))
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

            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(students, f, ensure_ascii=False, indent=2)

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

            with open(OBSERVATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(observations, f, ensure_ascii=False, indent=2)

            if payload.get('student_id'):
                for st in students:
                    if st['id'] == payload['student_id']:
                        st['coverage'] = calculate_student_coverage(st['id'])
                with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(students, f, ensure_ascii=False, indent=2)

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
            with open(OBSERVATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(observations, f, ensure_ascii=False, indent=2)

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
    print("  ΕΞΥΠΝΟΣ ΒΟΗΘΟΣ & ΚΑΡΤΕΛΑ ΜΑΘΗΤΗ ΤΜΗΜΑΤΟΣ ΕΝΤΑΞΗΣ")
    print("  ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης - Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)")
    print("=" * 70)
    print(f"[*] Τοπική πρόσβαση από αυτόν τον Υπολογιστή: http://localhost:{port}")
    print(f"[*] Άμεση πρόσβαση από το Xiaomi Pad 6 (Tablet): http://{local_ip}:{port}")
    print("=" * 70)
    print("[+] Τα έγγραφα Word (.docx), Markdown και Dataset συγχρονίζονται αυτόματα.")
    
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
