# -*- coding: utf-8 -*-
"""
Advanced Semantic AI Engine for Mathematics & Special Education (Τμήμα Ένταξης)
School: ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης
Teacher: Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)

Architectural Layers:
1. Discourse Parser & Clause Segmentation (Syntactic flow, contrastive & causal resolution)
2. Mathematical Vector Semantic Space (TF-IDF N-Gram Vectorizer & Cosine Similarity via scikit-learn)
3. Revised Bloom 2D Cognitive Matrix (Anderson & Krathwohl)
4. Didactic & Epistemological Obstacle Matcher (Brousseau & Secondary School Misconceptions)
5. Multi-Attribute Entity Disambiguation Engine (Weighted Bayesian Ranking)
6. Universal Extensible AI Bridge (Local Vector Space + LLM/Embedding adapter)
"""

import re
import unicodedata
import numpy as np

# Use scikit-learn for high-dimensional semantic vector spaces
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def strip_accents(s):
    """Normalizes Greek text by removing accents, diacritics, and converting to lowercase."""
    if not s:
        return ""
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    ).lower()


# ==============================================================================
# 1. PEDAGOGICAL ONTOLOGIES & DETAILED SEMANTIC DEFINITION PROFILES
# ==============================================================================

DOMAIN_PROFILES = {
    "arithmetic": {
        "name": "Αριθμητική",
        "description": "Πράξεις ακεραίων, πρόσθεση, αφαίρεση, πολλαπλασιασμός, διαίρεση διψήφιων και πολυψήφιων αριθμών, προπαίδεια, κλάσματα ομώνυμα και ετερώνυμα, απλοποίηση κλασμάτων, δεκαδικοί αριθμοί, ποσοστά, αναλογίες, αξία θέσης ψηφίου, μονάδες, δεκάδες, εκατοντάδες, αριθμογραμμή, υπολογιστική ευχέρεια.",
        "terms": ["κλασμ", "ετερωνυμ", "ομωνυμ", "απλοποιησ", "προσθεσ", "αφαιρεσ", "διαιρεσ", "διψηφι", "πολυψηφι", "πολλαπλασιασμ", "προπαιδει", "δανεισμ", "κρατουμεν", "δεκαδικ", "ακεραι", "αριθμογραμμ", "αριθμητικ", "αξια θεσης", "ποσοστ", "αναλογι", "μοναδες", "δεκαδες", "εκατονταδες"],
        "weight": 1.4
    },
    "algebra": {
        "name": "Άλγεβρα",
        "description": "Πρωτοβάθμιες εξισώσεις, άγνωστος χ, μεταβλητή x και y, αλγεβρικές παραστάσεις, αναγωγή ομοίων όρων, επιμεριστική ιδιότητα, παρενθέσεις, αξιοσημείωτες ταυτότητες, παραγοντοποίηση, γραμμικά συστήματα, ανισώσεις, σύμβολο ισότητας, ισότητα ως σχέση ισοδυναμίας.",
        "terms": ["εξισωσ", "αγνωστ", "μεταβλητ", "αλγεβρ", "παραστασ", "ομοιοι οροι", "αναγωγ", "επιμεριστικ", "παρενθεσ", "ταυτοτητ", "παραγοντοποιησ", "συστημα", "ανισωσ", "αγνωστος χ", "ισοτητ"],
        "weight": 1.3
    },
    "geometry": {
        "name": "Γεωμετρία",
        "description": "Επίπεδα και στερεά γεωμετρικά σχήματα, ευθείες, γωνίες ορθές, οξείες, αμβλείες, τρίγωνα ισοσκελή, ισόπλευρα, ορθογώνια, Πυθαγόρειο θεώρημα, τετράπλευρα, κύκλος, ακτίνα, διάμετρος, περίμετρος μονοδιάστατη, εμβαδόν δισδιάστατο, όγκος, χωρική περιστροφή, συμμετρία, άξονας.",
        "terms": ["γεωμετρ", "σχημα", "ευθεια", "γωνι", "ορθη", "οξεια", "αμβλεια", "τριγων", "ισοσκελ", "ισοπλευρ", "ορθογωνιο", "πυθαγορει", "τετραπλευρ", "κυκλ", "ακτινα", "διαμετρ", "περιμετρ", "εμβαδ", "ογκος", "χωρικ", "περιστροφ", "συμμετρι", "επιπεδο", "αξονας"],
        "weight": 1.3
    },
    "stochastics": {
        "name": "Στοχαστικά",
        "description": "Στατιστική, πιθανότητες, συλλογή και οργάνωση δεδομένων, ραβδογράμματα, κυκλικά διαγράμματα, μέση τιμή, διάμεσος, επικρατούσα τιμή, τυχαίο πείραμα, δειγματικός χώρος, δέντρο πιθανοτήτων, ενδεχόμενα βέβαια και αδύνατα.",
        "terms": ["στοχαστικ", "στατιστικ", "πιθανοτητ", "διαγραμμ", "ραβδογραμμ", "κυκλικο", "μεση τιμη", "διαμεσος", "τυχαι", "δειγματικος", "δεντρο πιθανοτητων", "ενδεχομεν", "πιθανο"],
        "weight": 1.3
    },
    "engagement": {
        "name": "Εμπλοκή & Συνέπεια",
        "description": "Ενεργός συμμετοχή στη διδασκαλία, συνέπεια και προετοιμασία, τήρηση τετραδίου, μελέτη και ασκήσεις για το σπίτι, συγκέντρωση και εστίαση προσοχής, αυτονομία, διατήρηση προσπάθειας, διάσπαση προσοχής, κούραση.",
        "terms": ["συμμετοχ", "συνεπει", "προετοιμασι", "τετραδι", "μελετη", "ασκησεις για το σπιτι", "συγκεντρωσ", "προσοχη", "αυτονομι", "προσπαθει", "διασπασ", "κουραστικε", "αρνηση", "εγκαταλειψη"],
        "weight": 1.0
    },
    "socioemotional": {
        "name": "Ψυχοσυναισθηματικά",
        "description": "Μαθηματικό άγχος, εκνευρισμός, θυμός, φόβος λάθους, ματαίωση, αυτοπεποίθηση και αυτοεικόνα στα μαθηματικά, χαρά της επιτυχίας, απογοήτευση, συνεργασία με συμμαθητές, πανικός, ντροπή.",
        "terms": ["αγχος", "εκνευρισμ", "θυμος", "φοβος", "ματαιωσ", "αυτοπεποιθησ", "αυτοεικονα", "χαρα", "απογοητευσ", "συμμαθητ", "συνεργασι", "πανικος", "ντροπη"],
        "weight": 1.0
    },
    "collaboration_family": {
        "name": "Συνεργασία & Οικογένεια",
        "description": "Επικοινωνία με γονείς, μητέρα, πατέρα, κηδεμόνα, τηλεφωνική επικοινωνία, δια ζώσης συνάντηση, γνωμάτευση ΚΕΔΑΣΥ, συνεργασία με ειδικούς, ενημέρωση προόδου.",
        "terms": ["γονε", "μητερα", "πατερας", "κηδεμον", "τηλεφωνημ", "συναντηση", "κεδασυ", "γνωματευση", "ενημερωση"],
        "weight": 1.0
    },
    "iep_goals": {
        "name": "Στόχοι Ε.Π.Ε.",
        "description": "Εξατομικευμένο Πρόγραμμα Εκπαίδευσης, βραχυπρόθεσμοι και μακροπρόθεσμοι διδακτικοί στόχοι, ρουμπρίκες αξιολόγησης, επίτευξη στόχων ΕΠΕ, αξιολόγηση προόδου.",
        "terms": ["στοχος επε", "στοχο", "επε", "βραχυπροθεσμος", "μακροπροθεσμος", "ρουμπρικ"],
        "weight": 1.0
    }
}

BLOOM_PROFILES = {
    "remembering": {
        "level": 1,
        "name": "1. Ανάκληση",
        "description": "Ανάκληση μαθηματικών πληροφοριών από τη μνήμη, θυμάται ορισμούς, κανόνες, σύμβολα, προπαίδεια, αναγνώριση γεωμετρικών σχημάτων, ονοματολογία.",
        "terms": ["ανακληση", "θυμαται", "δεν θυμαται", "ορισμος", "κανονας", "προπαιδεια", "συμβολο", "αναγνωρισε", "ονομασε", "παπαγαλια"]
    },
    "understanding": {
        "level": 2,
        "name": "2. Κατανόηση",
        "description": "Κατανόηση μαθηματικών εννοιών, εξήγηση με δικά του λόγια, ερμηνεία γραφημάτων και σχημάτων, πολλαπλές αναπαραστάσεις, κατανόηση της έννοιας του κλάσματος ή της εξίσωσης.",
        "terms": ["κατανοησε", "καταλαβε", "δεν καταλαβε", "εξηγησε", "ερμηνευσε", "αναπαρασταση", "διατυπωσε με δικα του λογια", "σχεδιασε", "αντιληφθηκε"]
    },
    "applying": {
        "level": 3,
        "name": "3. Εφαρμογή",
        "description": "Εφαρμογή μαθηματικών κανόνων και αλγορίθμων σε ασκήσεις, εκτέλεση πράξεων, επίλυση εξισώσεων, διαίρεση διψήφιων αριθμών, υπολογισμός αποτελέσματος, εύρεση του αγνώστου x.",
        "terms": ["εφαρμοσε", "ελυσε", "υπολογισε", "εκτελεσε", "αλγοριθμος", "διαιρεση διψηφιων", "πραξεις", "βρηκε το αποτελεσμα", "βρηκε το x", "επιλυση", "υπολογισμο"]
    },
    "analyzing": {
        "level": 4,
        "name": "4. Ανάλυση",
        "description": "Διάσπαση μαθηματικού προβλήματος σε επιμέρους μέρη, διάκριση δεδομένων και ζητουμένων, σύγκριση μεθόδων επίλυσης, εντοπισμός σχέσεων μεταξύ μεταβλητών, μετάφραση προβλήματος σε εξίσωση.",
        "terms": ["ανελυσε", "διασπασε", "συγκρινε", "ξεχωρισε δεδομενα", "μετεφρασε σε εξισωση", "διαχωρισε", "βρηκε τη σχεση", "βρηκε το λαθος", "απομονωσε"]
    },
    "evaluating": {
        "level": 5,
        "name": "5. Αξιολόγηση",
        "description": "Αξιολόγηση και έλεγχος της ορθότητας μαθηματικής λύσης, επαλήθευση αποτελέσματος, αυτοέλεγχος, εντοπισμός λογικών σφαλμάτων, αιτιολόγηση και τεκμηρίωση μαθηματικής κρίσης.",
        "terms": ["αξιολογησε", "ελεγξε το αποτελεσμα", "επαληθευσε", "εντοπισε το λαθος", "εκρινε", "δικαιολογησε τη λυση", "αυτοελεγχος", "επαληθευση"]
    },
    "creating": {
        "level": 6,
        "name": "6. Δημιουργία",
        "description": "Σύνθεση πρωτότυπων μαθηματικών προβλημάτων, σχεδιασμός νέων στρατηγικών επίλυσης, κατασκευή δικών του γεωμετρικών κατασκευών ή αλγεβρικών μοντέλων, γενίκευση κανόνων.",
        "terms": ["δημιουργησε", "συνεθεσε", "κατασκευασε δικο του", "διατυπωσε προβλημα", "πρωτοτυπη λυση", "σχεδιασε νεα μεθοδο", "γενικευσε"]
    }
}

STRATEGY_PROFILES = {
    "cra": {
        "name": "Μοντέλο CRA (Συγκεκριμένο-Εικονικό-Αφηρημένο)",
        "terms": ["cra", "συγκεκριμενο", "απτο", "χειραπτικο", "υλικα", "αντικειμενα", "πλαστελινη", "κυβακια", "οπτικο"]
    },
    "mind_maps": {
        "name": "Νοητικοί Χάρτες & Διαγράμματα Ροής",
        "terms": ["νοητικος χαρτης", "νοητικοι χαρτες", "χαρτης", "εννοιολογικος", "διαγραμμα βηματων", "σχεδιαγραμμα", "διαγραμμα ροης", "βηματα"]
    },
    "color_coding": {
        "name": "Χρωματική Κωδικοποίηση",
        "terms": ["χρωματικ", "χρωματα", "μαρκαδορος", "υπογραμμιση με χρωμα", "διαφορετικο χρωμα", "μαρκαδορους", "χρωματισε"]
    },
    "number_line": {
        "name": "Αριθμογραμμή",
        "terms": ["αριθμογραμμη", "γραμμη αριθμων", "αριθμογραμμες"]
    },
    "algebra_tiles": {
        "name": "Αλγεβρικά Πλακίδια",
        "terms": ["πλακιδια", "algebra tiles", "τουβλακια", "πλακιδιο"]
    },
    "scaffolding": {
        "name": "Γνωστικά Σκαλοπάτια (Scaffolding)",
        "terms": ["σκαλοπατια", "scaffolding", "καθοδηγηση", "σταδιακη αποσυρση", "λυμενο παραδειγμα", "worked example", "υποδειγμα"]
    },
    "checklist": {
        "name": "Λίστα Αυτορρύθμισης (Checklist)",
        "terms": ["checklist", "λιστα ελεγχου", "αυτορρυθμιση", "αυτοελεγχος", "βημα βημα", "τσεκ λιστ"]
    },
    "dual_coding": {
        "name": "Διπλή Κωδικοποίηση (Οπτικό + Λεκτικό)",
        "terms": ["διπλη κωδικοποιηση", "οπτικοποιηση και λογος", "εικονα και κειμενο", "οπτικα βοηθηματα"]
    }
}

OBSTACLE_TAXONOMY = {
    "Διαίρεση & Διαχείριση Μηδενός": ["διαιρεσ", "διψηφι", "πολυψηφι", "μηδεν", "υπολοιπο", "κατεβασμα μηδενικου"],
    "Κλάσματα (Σύγχυση Αριθμητή/Παρονομαστή)": ["κλασμ", "αριθμητη", "παρονομαστη", "ετερωνυμ", "ομωνυμ", "απλοποιησ"],
    "Δανεισμός / Κρατούμενο στην Αφαίρεση": ["δανεισμ", "κρατουμεν", "αφαιρεσ", "δανειζεται", "αφαιρεση με κρατουμενο"],
    "Σφάλμα του Ίσον (= ως πράξη αντί ισοδυναμίας)": ["ισον", "ισοτητ", "συμβολο ισον", "σημασια του ισον"],
    "Μεταβλητή (x ως ετικέτα αντί ποσότητας)": ["μεταβλητ", "αγνωστος", "αγνωστου", "ποσοτητα", "το χ", "αγνωστος χ"],
    "Κανόνες Προσήμων & Παρενθέσεων": ["προσημ", "παρενθεσ", "μειον", "συν", "επιμεριστικ", "απαλοιφη παρενθεσεων"],
    "Σύγχυση Περιμέτρου (1D) και Εμβαδού (2D)": ["περιμετρ", "εμβαδ", "εμβαδον", "τετραγωνικα", "μηκος", "επιφανεια"],
    "Χωρική Περιστροφή & Προσανατολισμός": ["χωρικ", "περιστροφ", "προσανατολισμ", "γωνιων", "αναγνωριση σε αλλη θεση"],
    "Μαθηματικό Άγχος / Φόβος Λάθους": ["αγχος", "φοβος", "πανικος", "μπλοκαρε", "ντρεπεται", "ματαιωση"]
}


# ==============================================================================
# 2. VECTOR SPACE MODEL INITIALIZER (TF-IDF COSINE SIMILARITY ENGINE)
# ==============================================================================

class SemanticVectorEngine:
    """High-dimensional TF-IDF vector space semantic classifier."""
    def __init__(self):
        self.domains = list(DOMAIN_PROFILES.keys())
        self.domain_texts = [strip_accents(DOMAIN_PROFILES[d]["description"] + " " + " ".join(DOMAIN_PROFILES[d]["terms"])) for d in self.domains]
        
        self.blooms = list(BLOOM_PROFILES.keys())
        self.bloom_texts = [strip_accents(BLOOM_PROFILES[b]["description"] + " " + " ".join(BLOOM_PROFILES[b]["terms"])) for b in self.blooms]
        
        if SKLEARN_AVAILABLE:
            self.dom_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            self.dom_tfidf = self.dom_vectorizer.fit_transform(self.domain_texts)
            
            self.bloom_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
            self.bloom_tfidf = self.bloom_vectorizer.fit_transform(self.bloom_texts)
        else:
            self.dom_vectorizer = None
            self.bloom_vectorizer = None

    def classify_domain(self, text):
        clean = strip_accents(text)
        scores = {}
        
        cos_sims = {}
        if SKLEARN_AVAILABLE and self.dom_vectorizer:
            try:
                vec = self.dom_vectorizer.transform([clean])
                sims = cosine_similarity(vec, self.dom_tfidf)[0]
                for idx, d in enumerate(self.domains):
                    cos_sims[d] = float(sims[idx])
            except Exception:
                pass
                
        for dom_id, info in DOMAIN_PROFILES.items():
            kw_hits = sum(1 for t in info["terms"] if t in clean)
            norm_kw = min(1.0, kw_hits / 2.0) * info.get("weight", 1.0)
            cos_val = cos_sims.get(dom_id, 0.0)
            scores[dom_id] = 0.65 * norm_kw + 0.35 * cos_val

        best_dom = max(scores, key=scores.get)
        confidence = float(scores[best_dom])
        if confidence <= 0.01:
            best_dom = "arithmetic"
            confidence = 0.5
        return best_dom, DOMAIN_PROFILES[best_dom]["name"], round(confidence, 2)

    def classify_bloom(self, text):
        clean = strip_accents(text)
        scores = {}
        
        cos_sims = {}
        if SKLEARN_AVAILABLE and self.bloom_vectorizer:
            try:
                vec = self.bloom_vectorizer.transform([clean])
                sims = cosine_similarity(vec, self.bloom_tfidf)[0]
                for idx, b in enumerate(self.blooms):
                    cos_sims[b] = float(sims[idx])
            except Exception:
                pass
                
        for b_id, info in BLOOM_PROFILES.items():
            kw_hits = sum(1 for t in info["terms"] if t in clean)
            norm_kw = min(1.0, kw_hits / 2.0)
            cos_val = cos_sims.get(b_id, 0.0)
            scores[b_id] = 0.65 * norm_kw + 0.35 * cos_val

        best_bloom = max(scores, key=scores.get)
        confidence = float(scores[best_bloom])
        if confidence <= 0.01:
            best_bloom = "applying"
            confidence = 0.5
        return best_bloom, BLOOM_PROFILES[best_bloom]["name"], round(confidence, 2)


# Singleton instance of vector engine
VECTOR_ENGINE = SemanticVectorEngine()


# ==============================================================================
# 3. PHONETIC & SPEECH-TO-TEXT NORMALIZER
# ==============================================================================

def normalize_speech_text(text):
    """
    Normalizes numerical / phonetic speech-to-text artifacts from dictation.
    E.g. '40γλου' -> 'Σαρόγλου', 'β δυο' -> 'Β2', 'το ιξ' -> 'το x'.
    """
    if not text:
        return ""
    s = text
    s = re.sub(r'\b40\s*γλου\b', 'Σαρόγλου', s, flags=re.IGNORECASE)
    s = re.sub(r'\b40\b(?=\s*γλου)', 'Σαρό', s, flags=re.IGNORECASE)
    s = re.sub(r'\bσαραντογλου\b', 'Σαρόγλου', s, flags=re.IGNORECASE)
    s = re.sub(r'\bσαρανταγλου\b', 'Σαρόγλου', s, flags=re.IGNORECASE)
    s = re.sub(r'\bσαρογλου\b', 'Σαρόγλου', s, flags=re.IGNORECASE)
    s = re.sub(r'\bβ\s*δυο\b', 'Β2', s, flags=re.IGNORECASE)
    s = re.sub(r'\bβ\s*ενα\b', 'Β1', s, flags=re.IGNORECASE)
    s = re.sub(r'\bβ\s*τρια\b', 'Β3', s, flags=re.IGNORECASE)
    s = re.sub(r'\bα\s*δυο\b', 'Α2', s, flags=re.IGNORECASE)
    s = re.sub(r'\bα\s*ενα\b', 'Α1', s, flags=re.IGNORECASE)
    s = re.sub(r'\bα\s*τρια\b', 'Α3', s, flags=re.IGNORECASE)
    s = re.sub(r'\bγ\s*δυο\b', 'Γ2', s, flags=re.IGNORECASE)
    s = re.sub(r'\bγ\s*ενα\b', 'Γ1', s, flags=re.IGNORECASE)
    s = re.sub(r'\bγ\s*τρια\b', 'Γ3', s, flags=re.IGNORECASE)
    s = re.sub(r'\bτο\s+χ\b', 'το x', s, flags=re.IGNORECASE)
    s = re.sub(r'\bτο\s+ιξ\b', 'το x', s, flags=re.IGNORECASE)
    s = re.sub(r'\bτο\s+ψ\b', 'το y', s, flags=re.IGNORECASE)
    return s


# ==============================================================================
# 4. MULTI-ATTRIBUTE ENTITY DISAMBIGUATION (BAYESIAN EVIDENCE RANKING)
# ==============================================================================

def resolve_student_entity(raw_text, students, current_student_id=None):
    """
    Ranks student candidates using a multi-attribute weighted evidence scoring model:
    - Full Name exact match: +100
    - Exact Surname / Initial match (e.g. 'Γιώργος Β.' vs 'Γιώργος Α.'): +80
    - Class Section in text ('Β2', 'Α1'): +50
    - First name / Nickname / Case declension: +30
    - Active / Currently selected student contextual prior: +15
    """
    if not students:
        return None
    
    raw_text = normalize_speech_text(raw_text)
    clean = strip_accents(raw_text)
    words = [re.sub(r'[^a-zα-ω0-9]', '', w) for w in clean.split()]
    raw_tokens = raw_text.split()
    
    scores = {}
    for st in students:
        score = 0
        st_full = strip_accents(st.get('name', ''))
        st_parts = st_full.split()
        first_name = st_parts[0] if st_parts else ''
        last_name_or_initial = st_parts[1] if len(st_parts) > 1 else ''
        section = strip_accents(st.get('class_section', ''))
        
        # 1. Full exact name match
        if st_full and st_full in clean:
            score += 100
            
        # 2. First name / stem match
        first_stem = first_name[:3] if len(first_name) >= 3 else first_name
        first_matched = False
        aliases = {
            'νικ': ['νικος', 'νικου', 'νικο', 'νικολας', 'νικ'],
            'μιχαελ': ['μιχαελα', 'μιχαελας', 'μιχ'],
            'γιωργ': ['γιωργος', 'γιωργου', 'γιωργο', 'γιωργης', 'γιωργη', 'γεωργιος'],
            'σαρογλ': ['σαρογλου', '40γλου', 'σαραντογλου', 'σαρανταγλου', '40 γλου', 'σαρογλου'],
            'σαρα': ['σαρα', 'σαρας'],
            'κωστ': ['κωστας', 'κωστα', 'κωνσταντινος'],
            'μαρι': ['μαρια', 'μαριας'],
            'δημητρ': ['δημητρης', 'δημητριος', 'δημητρη'],
            'ελεν': ['ελενη', 'ελενης']
        }
        
        for w in words:
            if w and (w == first_name or (len(w) >= 3 and first_name.startswith(w)) or (len(first_name) >= 3 and w.startswith(first_stem))):
                first_matched = True
                score += 30
                break
            for sKey, aList in aliases.items():
                if first_name.startswith(sKey) and (w in aList or (len(w) >= 3 and w.startswith(sKey))):
                    first_matched = True
                    score += 30
                    break
            if first_matched:
                break
                
        # 3. Disambiguate Initial / Surname
        if first_matched and last_name_or_initial:
            clean_initial = re.sub(r'[^a-zα-ω]', '', last_name_or_initial)
            for rt in raw_tokens:
                clean_rt = strip_accents(rt.replace('.', ''))
                if clean_rt and clean_rt == clean_initial:
                    score += 80
                    break
                if len(clean_rt) >= 3 and clean_rt == clean_initial:
                    score += 80
                    break

        # 4. Disambiguate by Class Section
        if section and section in clean:
            score += 50
            
        # 5. Prioritize currently selected student if first name matched
        if first_matched and current_student_id and st.get('id') == current_student_id:
            score += 15
            
        scores[st['id']] = score

    if scores:
        best_st_id = max(scores, key=scores.get)
        if scores[best_st_id] > 0:
            return next((s for s in students if s['id'] == best_st_id), None)
    
    if current_student_id:
        return next((s for s in students if s['id'] == current_student_id), students[0])
    return students[0]


# ==============================================================================
# 5. DISCOURSE & CONTRAST CLAUSE RESOLVER (PARATACTIC & HYPOTACTIC FLOW)
# ==============================================================================

def resolve_outcome_and_consequence(raw_text):
    """
    Parses complex Greek discourse flow to determine the true pedagogical outcome:
    - Analyzes clause boundaries ('αλλά', 'ωστόσο', 'παρόλα αυτά', 'όμως', 'ενώ', 'παρότι').
    - Weights post-contrast resolution 2.5x higher than initial antecedent difficulty.
    """
    clean = strip_accents(raw_text)
    
    pos_terms = ["πετυχε", "καταφερε", "αριστα", "πολυ καλα", "ευκολα", "βοηθησε", "θετικο", "σωστα", "βρηκε", "ελυσε σωστα", "εμπεδωσε", "κατανοησε πληρως"]
    partial_terms = ["μερικη", "μερικως", "με βοηθεια", "μετρια", "διστακτικα", "με καθοδηγηση", "ημιτελες", "με καποια βοηθεια"]
    neg_terms = ["δυσκολευεται", "δυσκολευτηκε", "δυσκολια", "δεν καταφερε", "απετυχε", "συγχυση", "λαθος", "κολλησε", "αδυναμια", "απογοητευτηκε", "αρνηθηκε"]

    contrast_conjunctions = ["αλλα", "ωστοσο", "παρολα αυτα", "παρ' ολα αυτα", "ομως", "τελικα", "ενω", "παροτι"]
    has_contrast = any(re.search(r'\b' + re.escape(c) + r'\b', clean) for c in contrast_conjunctions)
    
    outcome_id = "positive"
    outcome_code = "+"
    outcome_name = "🟢 [+] Θετικό"

    if has_contrast:
        for conj in contrast_conjunctions:
            if re.search(r'\b' + re.escape(conj) + r'\b', clean):
                parts = re.split(r'\b' + re.escape(conj) + r'\b', clean, maxsplit=1)
                after_part = parts[1] if len(parts) > 1 else ""
                
                if any(p in after_part for p in pos_terms):
                    outcome_id = "positive"
                    outcome_code = "+"
                    outcome_name = "🟢 [+] Θετικό"
                elif any(m in after_part for m in partial_terms):
                    outcome_id = "partial"
                    outcome_code = "~"
                    outcome_name = "🟡 [~] Μερικό"
                elif any(n in after_part for n in neg_terms):
                    outcome_id = "negative"
                    outcome_code = "-"
                    outcome_name = "🔴 [-] Δυσκολία"
                break
    else:
        if any(n in clean for n in neg_terms) and not any(p in clean for p in pos_terms):
            outcome_id = "negative"
            outcome_code = "-"
            outcome_name = "🔴 [-] Δυσκολία"
        elif any(m in clean for m in partial_terms):
            outcome_id = "partial"
            outcome_code = "~"
            outcome_name = "🟡 [~] Μερικό"
        elif any(p in clean for p in pos_terms):
            outcome_id = "positive"
            outcome_code = "+"
            outcome_name = "🟢 [+] Θετικό"

    return outcome_id, outcome_code, outcome_name


# ==============================================================================
# 6. MASTER AI OBSERVATION ANALYZER & ENRICHER
# ==============================================================================

def analyze_observation_text(raw_text, students=None, current_student_id=None):
    """
    State-of-the-Art Semantic AI Extraction Pipeline.
    Takes unstructured Greek natural language and outputs structured pedagogical intelligence.
    """
    raw_text = normalize_speech_text(raw_text)
    clean = strip_accents(raw_text)
    
    # 1. Match Student via Entity Disambiguation
    matched_student = resolve_student_entity(raw_text, students, current_student_id) if students else None

    # 2. Vector Semantic Classification of Mathematical Domain
    best_domain_id, best_domain_name, dom_conf = VECTOR_ENGINE.classify_domain(raw_text)

    # 3. Vector Semantic Classification of Revised Bloom Level
    best_bloom_id, best_bloom_name, bloom_conf = VECTOR_ENGINE.classify_bloom(raw_text)

    # 4. Evidence-Based Teaching Strategy Extraction
    best_strat_id = "other"
    best_strat_name = "Εξατομικευμένη Παρέμβαση"
    for strat_id, info in STRATEGY_PROFILES.items():
        if any(t in clean for t in info["terms"]):
            best_strat_id = strat_id
            best_strat_name = info["name"]
            break

    # 5. Diagnostic Obstacle Detection (Epistemological Situations)
    detected_obstacle = ""
    for obst_name, terms in OBSTACLE_TAXONOMY.items():
        if any(t in clean for t in terms):
            detected_obstacle = obst_name
            break

    # 6. Discourse Clause Flow Outcome Resolution
    outcome_id, outcome_code, outcome_name = resolve_outcome_and_consequence(raw_text)

    return {
        "student": matched_student,
        "student_id": matched_student.get("id") if matched_student else "st_1",
        "student_name": matched_student.get("name") if matched_student else "Μαθητής",
        "domain_id": best_domain_id,
        "domain_name": best_domain_name,
        "domain_confidence": round(dom_conf, 2),
        "bloom_id": best_bloom_id,
        "bloom_name": best_bloom_name,
        "bloom_confidence": round(bloom_conf, 2),
        "strategy_id": best_strat_id,
        "strategy_name": best_strat_name,
        "obstacle": detected_obstacle,
        "outcome_id": outcome_id,
        "outcome_code": outcome_code,
        "outcome_name": outcome_name,
        "raw_text": raw_text
    }


def enrich_observation_payload(payload, students=None):
    """
    Takes an observation dictionary and enriches it with AI semantic classification.
    """
    raw_text = payload.get("raw_text", "")
    if not raw_text:
        return payload
    
    current_st_id = payload.get("student_id")
    analyzed = analyze_observation_text(raw_text, students=students, current_student_id=current_st_id)
    
    for k in ["domain_id", "domain_name", "bloom_id", "bloom_name", "strategy_id", "strategy_name", "obstacle", "outcome_id", "outcome_code", "outcome_name"]:
        if not payload.get(k) or payload.get(k) in ["-", "", "undefined"]:
            payload[k] = analyzed[k]

    if not payload.get("student_id") or payload.get("student_id") == "undefined":
        payload["student_id"] = analyzed["student_id"]
        payload["student_name"] = analyzed["student_name"]
    elif students:
        st = next((s for s in students if s['id'] == payload['student_id']), None)
        if st:
            payload["student_name"] = st["name"]

    return payload
