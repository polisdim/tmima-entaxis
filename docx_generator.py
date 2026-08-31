#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word (.docx) Document Generator for Inclusion Class (Τμήμα Ένταξης)
Populates official school templates based on live student data, Bloom levels,
interventions, and IEP goals.
School: ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης
Teacher: Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)
"""

import os
import copy
import docx
from datetime import datetime

TEMPLATES_BASE_DIR = r"c:\Users\polis\OneDrive - Democritus University of Thrace\Υλικά\ΕΑΕ\Ένταξη"

def get_template_file(template_filename, gender="Κορίτσι"):
    """Finds the template file in gender-specific folder with fallback."""
    folder_name = "0. Αγόρι" if (gender and "Αγόρι" in gender) else "0. Κορίτσι"
    path = os.path.join(TEMPLATES_BASE_DIR, folder_name, template_filename)
    
    if os.path.exists(path):
        return path
    
    # Fallback to 0. Αγόρι
    fallback_path = os.path.join(TEMPLATES_BASE_DIR, "0. Αγόρι", template_filename)
    if os.path.exists(fallback_path):
        return fallback_path
        
    # Fallback to 0. Κορίτσι
    fallback_path2 = os.path.join(TEMPLATES_BASE_DIR, "0. Κορίτσι", template_filename)
    if os.path.exists(fallback_path2):
        return fallback_path2

    raise FileNotFoundError(f"Template '{template_filename}' not found in templates directory.")

def generate_iep_docx(student, observations, output_dir):
    """Generates the official IEP (.docx) document using the user's template (3. ΕΠΕ.docx)."""
    gender = student.get('gender', 'Κορίτσι')
    tmpl_path = get_template_file("3. ΕΠΩΝΥΜΟ ΟΝΟΜΑ ΕΠΕ.docx", gender)
    doc = docx.Document(tmpl_path)
    
    # 1. Fill Table 0 (Student Details)
    if len(doc.tables) > 0:
        t0 = doc.tables[0]
        parts = student.get('name', '').split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        if len(t0.rows) > 1 and len(t0.rows[1].cells) > 3:
            t0.rows[1].cells[1].text = first_name
            t0.rows[1].cells[3].text = last_name or student.get('name', '')
        
        if len(t0.rows) > 2 and len(t0.rows[2].cells) > 3:
            t0.rows[2].cells[1].text = f"{student.get('grade', '')} {student.get('class_section', '')}".strip()
            t0.rows[2].cells[3].text = "2026-2027"
        
        if len(t0.rows) > 3 and len(t0.rows[3].cells) > 3:
            t0.rows[3].cells[1].text = student.get('diagnosis', 'Ειδική Μαθησιακή Δυσκολία')
            t0.rows[3].cells[3].text = "2026-2027"

    # Filter observations for this student
    st_id = student.get('id')
    st_obs = [o for o in observations if o.get('student_id') == st_id or o.get('student_name') == student.get('name')]
    math_obs = [o for o in st_obs if o.get('domain_id') in ['arithmetic', 'algebra', 'geometry', 'stochastics']]
    
    # 2. Iterate paragraphs and enrich math adaptations
    for p in doc.paragraphs:
        txt = p.text.strip()
        if "Στην Άλγεβρα:" in txt:
            alg_obs = [o for o in math_obs if o.get('domain_id') == 'algebra']
            alg_desc = alg_obs[0].get('raw_text', '') if alg_obs else "Χρήση χρωματικής κωδικοποίησης και νοητικών χαρτών βημάτων για την επίλυση εξισώσεων."
            p.text = f"Στην Άλγεβρα: {alg_desc}"
        elif "Στη Γεωμετρία:" in txt:
            geom_obs = [o for o in math_obs if o.get('domain_id') == 'geometry']
            geom_desc = geom_obs[0].get('raw_text', '') if geom_obs else "Διαχωρισμός περιμέτρου και εμβαδού με χρήση απτών οπτικών αναπαραστάσεων και σχημάτων."
            p.text = f"Στη Γεωμετρία: {geom_desc}"

    os.makedirs(output_dir, exist_ok=True)
    st_clean_name = student.get('name', 'Μαθητής').replace(' ', '_')
    out_filename = f"2_ΕΠΕ_{st_clean_name}_2026-2027.docx"
    out_path = os.path.join(output_dir, out_filename)
    doc.save(out_path)
    return out_path

def generate_initial_assessment_docx(student, observations, output_dir):
    """Generates the Initial Assessment (.docx) document (2. ΑΑ.docx)."""
    gender = student.get('gender', 'Κορίτσι')
    tmpl_path = get_template_file("2. ΕΠΩΝΥΜΟ ΟΝΟΜΑ ΑΑ.docx", gender)
    doc = docx.Document(tmpl_path)
    
    if len(doc.tables) > 0:
        t0 = doc.tables[0]
        parts = student.get('name', '').split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        if len(t0.rows) > 1 and len(t0.rows[1].cells) > 5:
            t0.rows[1].cells[1].text = first_name
            t0.rows[1].cells[5].text = last_name or student.get('name', '')
        if len(t0.rows) > 2 and len(t0.rows[2].cells) > 3:
            t0.rows[2].cells[1].text = student.get('grade', "Β' Γυμνασίου")
            t0.rows[2].cells[3].text = student.get('class_section', "Β1")
        if len(t0.rows) > 3 and len(t0.rows[3].cells) > 6:
            t0.rows[3].cells[1].text = student.get('diagnosis', 'Ειδική Μαθησιακή Δυσκολία')
            t0.rows[3].cells[6].text = "2026-2027"

    os.makedirs(output_dir, exist_ok=True)
    st_clean_name = student.get('name', 'Μαθητής').replace(' ', '_')
    out_filename = f"1_Αρχική_Αξιολόγηση_{st_clean_name}.docx"
    out_path = os.path.join(output_dir, out_filename)
    doc.save(out_path)
    return out_path

def generate_rubrics_docx(student, observations, output_dir):
    """Generates the Mid-Year Evaluation / Rubrics (.docx) document (4. ΑΞΙΟΛΟΓΗΣΗ.docx)."""
    gender = student.get('gender', 'Κορίτσι')
    tmpl_path = get_template_file("4. ΕΠΩΝΥΜΟ ΟΝΟΜΑ ΑΞΙΟΛΟΓΗΣΗ.docx", gender)
    doc = docx.Document(tmpl_path)
    
    for t in doc.tables:
        if len(t.rows) > 1:
            parts = student.get('name', '').split(' ', 1)
            if len(t.rows[1].cells) > 1:
                t.rows[1].cells[1].text = parts[0]
            if len(t.rows[1].cells) > 4:
                t.rows[1].cells[4].text = parts[1] if len(parts) > 1 else ''

    os.makedirs(output_dir, exist_ok=True)
    st_clean_name = student.get('name', 'Μαθητής').replace(' ', '_')
    out_filename = f"3_Ενδιάμεση_Αξιολόγηση_{st_clean_name}.docx"
    out_path = os.path.join(output_dir, out_filename)
    doc.save(out_path)
    return out_path

def generate_final_evaluation_docx(student, observations, output_dir):
    """Generates the Final Summative Evaluation Report (.docx) document (6. ΤΑ.docx)."""
    gender = student.get('gender', 'Κορίτσι')
    tmpl_path = get_template_file("6. ΕΠΩΝΥΜΟ ΟΝΟΜΑ ΤΑ.docx", gender)
    doc = docx.Document(tmpl_path)
    
    if len(doc.tables) > 0:
        t0 = doc.tables[0]
        parts = student.get('name', '').split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        
        if len(t0.rows) > 1 and len(t0.rows[1].cells) > 5:
            t0.rows[1].cells[1].text = first_name
            t0.rows[1].cells[5].text = last_name or student.get('name', '')
        if len(t0.rows) > 2 and len(t0.rows[2].cells) > 3:
            t0.rows[2].cells[1].text = student.get('grade', "Β' Γυμνασίου")
            t0.rows[2].cells[3].text = student.get('class_section', "Β1")
        if len(t0.rows) > 3 and len(t0.rows[3].cells) > 6:
            t0.rows[3].cells[1].text = student.get('diagnosis', 'Ειδική Μαθησιακή Δυσκολία')
            t0.rows[3].cells[6].text = "2026-2027"

    os.makedirs(output_dir, exist_ok=True)
    st_clean_name = student.get('name', 'Μαθητής').replace(' ', '_')
    out_filename = f"4_Τελική_Έκθεση_{st_clean_name}.docx"
    out_path = os.path.join(output_dir, out_filename)
    doc.save(out_path)
    return out_path
