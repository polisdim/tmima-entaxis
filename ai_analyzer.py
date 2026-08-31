# -*- coding: utf-8 -*-
"""
Advanced Semantic AI Engine for Mathematics & Special Education (Τμήμα Ένταξης)
School: ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης
Teacher: Δημήτριος Πολυχρόνης (ΠΕ03.ΕΑΕ)

Architectural Layers:
1. Discourse Parser & Clause Segmentation (Syntactic flow, contrastive & causal resolution)
2. Mathematical Vector Semantic Space (TF-IDF N-Gram Vectorizer & Cosine Similarity via scikit-learn)
3. Revised Bloom 2D Cognitive Matrix (Anderson & Krathwohl)
4. Duval Semiotic Representation Registers (Verbal, Symbolic, Visual, Manipulative & Transitions)
5. Didactic & Epistemological Obstacle Matcher (Brousseau: Epistemological, Didactic, Ontogenetic, Didactic Contract)
6. Scaffolding Recommender Engine (Actionable pedagogical strategies for PE03.EAE)
7. Multi-Attribute Entity & Target Disambiguation (Individual, Group of 2-3 Students, Class/Section)
"""

import re
import unicodedata

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

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
        "description": "Μαθηματικό άγχος, εκνευρισμός, θυμός, φόβος λάθους, ματαίωση, αυτοπεποίθηση και αυτοεικόνα στα μαθηματικά, χαρά της επιτυχίας, απογοήτευση, συνεργασία στο Τμήμα Ένταξης, πανικός, ντροπή.",
        "terms": ["αγχος", "εκνευρισμ", "θυμος", "φοβος", "ματαιωσ", "αυτοπεποιθησ", "αυτοεικονα", "χαρα", "απογοητευσ", "συμμαθητ", "συνεργασι", "πανικος", "ντροπη"],
        "weight": 1.0
    },
    "collaboration_family": {
        "name": "Συνεργασία & Οικογένεια",
        "description": "Επικοινωνία με γονείς, μητέρα, πατέρα, κηδεμόνα, τηλεφωνική επικοινωνία, δια ζώσης συνάντηση, γνωμάτευση ΚΕΔΑΣΥ, συνεργασία με ειδικούς, ενημέρωση προόδου στο Τμήμα Ένταξης.",
        "terms": ["γονε", "μητερα", "πατερας", "κηδεμον", "τηλεφωνημ", "συναντηση", "κεδασυ", "γνωματευση", "ενημερωση"],
        "weight": 1.0
    },
    "iep_goals": {
        "name": "Στόχοι Ε.Π.Ε.",
        "description": "Εξατομικευμένο Πρόγραμμα Εκπαίδευσης, βραχυπρόθεσμοι και μακροπρόθεσμοι διδακτικοί στόχοι, ρουμπρίκες αξιολόγησης 4 επιπέδων, επίτευξη στόχων ΕΠΕ, αξιολόγηση προόδου.",
        "terms": ["στοχος επε", "στοχο", "επε", "βραχυπροθεσμος", "μακροπροθεσμος", "ρουμπρικ", "σταθμη", "ρουμπρικα 4 επιπεδων"],
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

# ------------------------------------------------------------------------------
# DUVAL SEMIOTIC REGISTERS (Ημιωτικές Αναπαραστάσεις Raymond Duval)
# ------------------------------------------------------------------------------
DUVAL_REGISTERS = {
    "verbal": {
        "name": "Λεκτική / Φυσική Γλώσσα",
        "icon": "🗣️",
        "description": "Εκφώνηση προβλήματος, λεκτική διατύπωση κανόνων, διάκριση δεδομένων και ζητουμένων.",
        "terms": ["λεκτικ", "εκφωνηση", "περιγραφη", "προβλημα με λογια", "διατυπωση", "με λογια"]
    },
    "symbolic": {
        "name": "Συμβολική / Αλγεβρική",
        "icon": "🔢",
        "description": "Αριθμητικά σύμβολα, πράξεις, μεταβλητές x/y, εξισώσεις, κλασματική γραφή.",
        "terms": ["συμβολικ", "αλγεβρικ", "εξισωση", "συμβολα", "μεταβλητη x", "τυπος", "αριθμητικη γραφη"]
    },
    "visual": {
        "name": "Γραφική / Οπτική",
        "icon": "📐",
        "description": "Γεωμετρικά σχήματα, διαγράμματα, γραφικές παραστάσεις, άξονες, εικονική απεικόνιση.",
        "terms": ["γραφικ", "οπτικ", "σχημα", "διαγραμμα", "ραβδογραμμα", "γεωμετρικο", "εικονα", "καρτεσιανοι αξονες"]
    },
    "manipulative": {
        "name": "Απτική / Εποπτική (CRA)",
        "icon": "🧩",
        "description": "Χειραπτικό υλικό, αριθμογραμμή, αλγεβρικά πλακίδια, κύβοι Dienes, απτά αντικείμενα.",
        "terms": ["απτικ", "εποπτικ", "χειραπτικ", "αριθμογραμμη", "πλακιδια", "υλικα", "τουβλακια", "κυβακια", "πλαστελινη", "cra"]
    }
}

# ------------------------------------------------------------------------------
# BROUSSEAU OBSTACLE TYPES & MISCONCEPTIONS
# ------------------------------------------------------------------------------
BROUSSEAU_OBSTACLES = {
    "Διαίρεση & Διαχείριση Μηδενός": {
        "type": "epistemological",
        "type_name": "Επιστημολογικό",
        "terms": ["διαιρεσ", "διψηφι", "πολυψηφι", "μηδεν", "υπολοιπο", "κατεβασμα μηδενικου"],
        "desc": "Επιστημολογική δυσκολία με τη δυαδική φύση του μηδενός και τον αλγόριθμο της διαίρεσης."
    },
    "Κλάσματα (Σύγχυση Αριθμητή/Παρονομαστή)": {
        "type": "epistemological",
        "type_name": "Επιστημολογικό",
        "terms": ["κλασμ", "αριθμητη", "παρονομαστη", "ετερωνυμ", "ομωνυμ", "απλοποιησ"],
        "desc": "Επιστημολογική σύγκρουση φυσικών αριθμών με τον ρητό αριθμό ως λόγο μέρους-όλου."
    },
    "Δανεισμός / Κρατούμενο στην Αφαίρεση": {
        "type": "didactic",
        "type_name": "Διδακτικό",
        "terms": ["δανεισμ", "κρατουμεν", "αφαιρεσ", "δανειζεται", "αφαιρεση με κρατουμενο"],
        "desc": "Διδακτικό εμπόδιο από μηχανιστική εκτέλεση αλγορίθμου χωρίς κατανόηση δεκαδικής αξίας θέσης."
    },
    "Σφάλμα του Ίσον (= ως πράξη αντί ισοδυναμίας)": {
        "type": "didactic",
        "type_name": "Διδακτικό",
        "terms": ["ισον", "ισοτητ", "συμβολο ισον", "σημασια του ισον"],
        "desc": "Διδακτικό εμπόδιο όπου το σύμβολο = εκλαμβάνεται ως εντολή 'υπολόγισε' αντί για σχέση ισορροπίας."
    },
    "Μεταβλητή (x ως ετικέτα αντί ποσότητας)": {
        "type": "epistemological",
        "type_name": "Επιστημολογικό",
        "terms": ["μεταβλητ", "αγνωστος", "αγνωστου", "ποσοτητα", "το χ", "αγνωστος χ"],
        "desc": "Επιστημολογικό άλμα από τη συγκεκριμένη αριθμητική τιμή στη γενικευμένη μεταβλητή ποσότητα."
    },
    "Κανόνες Προσήμων & Παρενθέσεων": {
        "type": "didactic",
        "type_name": "Διδακτικό",
        "terms": ["προσημ", "παρενθεσ", "μειον", "συν", "επιμεριστικ", "απαλοιφη παρενθεσεων"],
        "desc": "Σύγχυση μεταξύ του προσήμου ως πράξης (αφαίρεση) και ως ιδιότητας του ρητού αριθμού."
    },
    "Σύγχυση Περιμέτρου (1D) και Εμβαδού (2D)": {
        "type": "ontogenetic",
        "type_name": "Οντογενετικό",
        "terms": ["περιμετρ", "εμβαδ", "εμβαδον", "τετραγωνικα", "μηκος", "επιφανεια"],
        "desc": "Οντογενετική/χωρική δυσκολία διάκρισης μονοδιάστατης γραμμικής μέτρησης και δισδιάστατης επιφάνειας."
    },
    "Χωρική Περιστροφή & Προσανατολισμός": {
        "type": "ontogenetic",
        "type_name": "Οντογενετικό",
        "terms": ["χωρικ", "περιστροφ", "προσανατολισμ", "γωνιων", "αναγνωριση σε αλλη θεση"],
        "desc": "Δυσκολία αναγνώρισης γεωμετρικών σχημάτων όταν αλλάζει ο τυπικός οριζόντιος προσανατολισμός."
    },
    "Ρήξη Διδακτικού Συμβολαίου (Αναμονή Επιβεβαίωσης)": {
        "type": "didactic_contract",
        "type_name": "Ρήξη Διδακτικού Συμβολαίου",
        "terms": ["περιμενει να του πω", "αναμονη επιβεβαιωσης", "δεν παιρνει πρωτοβουλια", "ρωταει αν ειναι σωστο", "εξαρτηση"],
        "desc": "Παθητική στάση του μαθητή που μεταθέτει την ευθύνη ελέγχου και μαθηματικής κρίσης στον εκπαιδευτικό."
    },
    "Μαθηματικό Άγχος / Φόβος Λάθους": {
        "type": "ontogenetic",
        "type_name": "Ψυχοσυναισθηματικό / Άγχος",
        "terms": ["αγχος", "φοβος", "πανικος", "μπλοκαρε", "ντρεπεται", "ματαιωση", "απογοητευση"],
        "desc": "Συναισθηματικό μπλοκάρισμα και φόβος έκθεσης που υπερφορτώνει τη μνήμη εργασίας."
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


VECTOR_ENGINE = SemanticVectorEngine()


# ==============================================================================
# 3. SPEECH NORMALIZER & DISAMBIGUATION (INDIVIDUAL, GROUP, CLASS)
# ==============================================================================

def normalize_speech_text(text):
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


def resolve_targets(raw_text, students, current_student_id=None):
    """
    Identifies target scope from speech/text:
    - 'class': If text mentions specific class section (e.g. 'στο Β1', 'στο τμημα Α2', 'ολη η ταξη')
    - 'group': If text mentions multiple students (e.g. 'ο Νικος και η Μιχαελα')
    - 'individual': Single student
    """
    if not students:
        return {'target_type': 'individual', 'students': [], 'class_section': None}
    
    raw_text = normalize_speech_text(raw_text)
    clean = strip_accents(raw_text)
    
    # 1. Check for Class section mention
    class_match = re.search(r'\b(στο\s+τμημα|στο|στην\s+ταξη|ταξη|τμημα)\s*([α-γ][1-3]|[α-γ]\s*[1-3])\b', clean)
    section_direct = re.search(r'\b([α-γ][1-3])\b', clean)
    
    detected_section = None
    if class_match:
        detected_section = class_match.group(2).replace(' ', '').upper()
    elif 'ολη η ταξη' in clean or 'στο τμημα' in clean:
        if section_direct:
            detected_section = section_direct.group(1).upper()

    # 2. Check for Multiple Students
    matched_students = []
    for st in students:
        st_name = strip_accents(st.get('name', ''))
        first_stem = st_name[:3] if len(st_name) >= 3 else st_name
        if st_name and (re.search(r'\b' + re.escape(st_name) + r'\b', clean) or re.search(r'\b' + re.escape(first_stem) + r'[α-ω]*\b', clean)):
            if st not in matched_students:
                matched_students.append(st)

    if detected_section and len(matched_students) == 0:
        return {
            'target_type': 'class',
            'students': [s for s in students if s.get('class_section', '').upper() == detected_section],
            'class_section': detected_section
        }
    elif len(matched_students) >= 2:
        return {
            'target_type': 'group',
            'students': matched_students,
            'class_section': matched_students[0].get('class_section')
        }
    elif len(matched_students) == 1:
        return {
            'target_type': 'individual',
            'students': matched_students,
            'class_section': matched_students[0].get('class_section')
        }
    else:
        # Fallback to current student or first student
        fallback = next((s for s in students if s['id'] == current_student_id), students[0])
        return {
            'target_type': 'individual',
            'students': [fallback],
            'class_section': fallback.get('class_section')
        }


def resolve_student_entity(raw_text, students, current_student_id=None):
    res = resolve_targets(raw_text, students, current_student_id)
    if res['students']:
        return res['students'][0]
    return students[0] if students else None


# ==============================================================================
# 4. DUVAL REGISTERS & BROUSSEAU OBSTACLE CLASSIFIER
# ==============================================================================

def classify_duval_register(raw_text):
    """Classifies the primary semiotic register according to Duval (1995)."""
    clean = strip_accents(raw_text)
    scores = {}
    for reg_id, info in DUVAL_REGISTERS.items():
        hits = sum(1 for t in info["terms"] if t in clean)
        scores[reg_id] = hits
    
    best_reg = max(scores, key=scores.get)
    if scores[best_reg] == 0:
        # default to symbolic for math if nothing else
        best_reg = "symbolic"
    return best_reg, DUVAL_REGISTERS[best_reg]["name"], DUVAL_REGISTERS[best_reg]["icon"]


def classify_brousseau_obstacle(raw_text):
    """Detects specific obstacle and categorizes it under Brousseau's typology."""
    clean = strip_accents(raw_text)
    for obst_name, info in BROUSSEAU_OBSTACLES.items():
        if any(t in clean for t in info["terms"]):
            return obst_name, info["type"], info["type_name"]
    return "", "none", "-"


# ==============================================================================
# 5. SCAFFOLDING RECOMMENDER ENGINE
# ==============================================================================

def recommend_scaffolding(domain_id, obstacle_name, bloom_level=3, duval_reg="symbolic"):
    """
    Returns 2-3 tailored didactic scaffolding interventions based on detected 
    obstacle, domain, and Duval register.
    """
    recs = []
    
    # Obstacle-specific scaffolding
    if "Κλάσματα" in obstacle_name:
        recs.append("🧩 Χρήση χειραπτικών κλασματικών ράβδων ή κυκλικών πιτών (CRA - Επίπεδο Συγκεκριμένου).")
        recs.append("🎨 Χρωματική κωδικοποίηση: πράσινο στον αριθμητή (μέρη που παίρνουμε), κόκκινο στον παρονομαστή (ίσα μέρη συνόλου).")
        recs.append("📏 Τοποθέτηση κλασμάτων σε αριθμογραμμή από το 0 έως το 1 για εννοιολόγηση μεγέθους.")
    elif "Διαίρεση" in obstacle_name or "Μηδενός" in obstacle_name:
        recs.append("📝 Λίστα αυτορρύθμισης 4 βημάτων: 1. Διαιρώ, 2. Πολλαπλασιάζω, 3. Αφαιρώ, 4. Κατεβάζω.")
        recs.append("🧮 Αναπαράσταση με πλακίδια δεκάδων/μονάδων για οπτικοποίηση της διαδικασίας 'μοιρασιάς'.")
    elif "Ίσον" in obstacle_name or "Εξίσωση" in obstacle_name or "Μεταβλητή" in obstacle_name:
        recs.append("⚖️ Αναπαράσταση εξίσωσης με ζυγαριά ισορροπίας δύο δίσκων (ισοδυναμία μελών).")
        recs.append("🟩 Χρήση Αλγεβρικών Πλακιδίων (Algebra Tiles): πράσινα πλακίδια για το x, κίτρινα/κόκκινα για αριθμούς.")
        recs.append("🔍 Αντικατάσταση του x με 'κουτάκι μυστηρίου' [ ? ] πριν την εισαγωγή του συμβόλου.")
    elif "Προσήμων" in obstacle_name:
        recs.append("🚶 Κίνηση πάνω στην οριζόντια αριθμογραμμή (δεξιά = θετικά/κέρδος, αριστερά = αρνητικά/ζημία).")
        recs.append("🔴🔵 Δίχρωμα πιόνια (μπλε για θετικά, κόκκινα για αρνητικά με κανόνα μηδενικού ζεύγους).")
    elif "Περιμέτρου" in obstacle_name or "Εμβαδού" in obstacle_name:
        recs.append("🧶 Απτική διάκριση: Σπάγκος για την περίμετρο (μήκος γύρω-γύρω) vs. Κάλυψη με τετραγωνάκια Post-it για το εμβαδόν.")
        recs.append("📐 Επισήμανση μονάδων μέτρησης: cm (1D διάσταση) vs. cm² (2D τετραγωνάκια).")
    elif "Άγχος" in obstacle_name or "Ρήξη" in obstacle_name:
        recs.append("🤝 Μοντέλο 'Εγώ κάνω - Εμείς κάνουμε - Εσύ κάνεις' (Gradual Release of Responsibility).")
        recs.append("📋 Παροχή λυμένου υποδείγματος (Worked Example) με κενά μόνο στα τελικά βήματα.")
        recs.append("🌟 Αποδοχή του λάθους ως 'εργαλείο μάθησης' και αποσυμπίεση χρόνου.")
    else:
        # Domain fallback
        if domain_id == "algebra":
            recs.append("🎨 Χρωματική κωδικοποίηση όμοιων όρων (κυκλώστε με ίδιο χρώμα τα x, με άλλο τους αριθμούς).")
            recs.append("📋 Λίστα βημάτων επίλυσης πρωτοβάθμιας εξίσωσης με παραδείγματα.")
        elif domain_id == "geometry":
            recs.append("🖐️ Χρήση διαφανειών και φυσική περιστροφή του σχήματος στο θρανίο.")
            recs.append("💻 Δυναμική εξερεύνηση στο Geogebra μέσω του Tablet.")
        else:
            recs.append("🪜 Διάσπαση του προβλήματος σε 2 απλούστερα υπο-ερωτήματα.")
            recs.append("🗣️ Ενθάρρυνση για λεκτική εξήγηση της σκέψης (Think-Aloud Protocol).")

    return recs[:3]


# ==============================================================================
# 6. DISCOURSE & CONTRAST CLAUSE RESOLVER
# ==============================================================================

def resolve_outcome_and_consequence(raw_text):
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
# 7. MASTER AI OBSERVATION ANALYZER & ENRICHER
# ==============================================================================

def analyze_observation_text(raw_text, students=None, current_student_id=None):
    raw_text = normalize_speech_text(raw_text)
    clean = strip_accents(raw_text)
    
    # 1. Target and Entity Resolution
    target_info = resolve_targets(raw_text, students, current_student_id)
    matched_student = target_info['students'][0] if target_info['students'] else None
    
    # 2. Vector Semantic Domain & Bloom
    best_domain_id, best_domain_name, dom_conf = VECTOR_ENGINE.classify_domain(raw_text)
    best_bloom_id, best_bloom_name, bloom_conf = VECTOR_ENGINE.classify_bloom(raw_text)

    # 3. Duval Register
    duval_reg, duval_name, duval_icon = classify_duval_register(raw_text)

    # 4. Brousseau Obstacle
    obst_name, obst_type, obst_type_name = classify_brousseau_obstacle(raw_text)

    # 5. Teaching Strategy
    best_strat_id = "other"
    best_strat_name = "Εξατομικευμένη Παρέμβαση"
    for strat_id, info in STRATEGY_PROFILES.items():
        if any(t in clean for t in info["terms"]):
            best_strat_id = strat_id
            best_strat_name = info["name"]
            break

    # 6. Scaffolding Recommendations
    bloom_num = BLOOM_PROFILES.get(best_bloom_id, {}).get("level", 3)
    scaffolding_recs = recommend_scaffolding(best_domain_id, obst_name, bloom_num, duval_reg)

    # 7. Outcome
    outcome_id, outcome_code, outcome_name = resolve_outcome_and_consequence(raw_text)

    return {
        "target_type": target_info['target_type'],
        "class_section": target_info.get('class_section'),
        "student": matched_student,
        "students": target_info['students'],
        "student_id": matched_student.get("id") if matched_student else "st_1",
        "student_name": matched_student.get("name") if matched_student else "Μαθητής",
        "domain_id": best_domain_id,
        "domain_name": best_domain_name,
        "domain_confidence": round(dom_conf, 2),
        "bloom_id": best_bloom_id,
        "bloom_name": best_bloom_name,
        "bloom_confidence": round(bloom_conf, 2),
        "duval_register": duval_reg,
        "duval_name": duval_name,
        "duval_icon": duval_icon,
        "obstacle": obst_name,
        "obstacle_type": obst_type,
        "obstacle_type_name": obst_type_name,
        "strategy_id": best_strat_id,
        "strategy_name": best_strat_name,
        "scaffolding_recommendations": scaffolding_recs,
        "outcome_id": outcome_id,
        "outcome_code": outcome_code,
        "outcome_name": outcome_name,
        "raw_text": raw_text
    }


def enrich_observation_payload(payload, students=None):
    raw_text = payload.get("raw_text", "")
    if not raw_text:
        return payload
    
    current_st_id = payload.get("student_id")
    analyzed = analyze_observation_text(raw_text, students=students, current_student_id=current_st_id)
    
    for k in ["domain_id", "domain_name", "bloom_id", "bloom_name", "strategy_id", "strategy_name", 
              "obstacle", "obstacle_type", "obstacle_type_name", "duval_register", "duval_name", "duval_icon",
              "outcome_id", "outcome_code", "outcome_name", "target_type"]:
        if not payload.get(k) or payload.get(k) in ["-", "", "undefined"]:
            if k in analyzed:
                payload[k] = analyzed[k]

    if "scaffolding_recommendations" not in payload and analyzed.get("scaffolding_recommendations"):
        payload["scaffolding_recommendations"] = analyzed["scaffolding_recommendations"]

    if not payload.get("student_id") or payload.get("student_id") == "undefined":
        payload["student_id"] = analyzed["student_id"]
        payload["student_name"] = analyzed["student_name"]
    elif students:
        st = next((s for s in students if s['id'] == payload['student_id']), None)
        if st:
            payload["student_name"] = st["name"]

    return payload
