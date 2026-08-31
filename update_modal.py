# -*- coding: utf-8 -*-
with open("app/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace the old modal-new-student with modal-student-dossier
old_modal = """  <!-- MODAL: ADD STUDENT -->
  <div id="modal-new-student" class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4 hidden">
    <div class="bg-brand-card border border-brand-border rounded-xl max-w-sm w-full p-5 space-y-3 shadow-2xl">
      <h3 class="text-sm font-bold text-white">Νέος Μαθητής</h3>
      <input type="text" id="new-st-name" class="w-full bg-slate-900 border border-brand-border rounded p-2 text-xs text-white" placeholder="Όνομα (π.χ. Γιώργος)">
      <div class="grid grid-cols-2 gap-2">
        <select id="new-st-gender" class="bg-slate-900 border border-brand-border rounded p-2 text-xs text-white">
          <option value="Αγόρι">Αγόρι</option>
          <option value="Κορίτσι">Κορίτσι</option>
        </select>
        <input type="text" id="new-st-grade" class="bg-slate-900 border border-brand-border rounded p-2 text-xs text-white" placeholder="Τάξη (π.χ. Β1)">
      </div>
      <input type="text" id="new-st-diagnosis" class="w-full bg-slate-900 border border-brand-border rounded p-2 text-xs text-white" placeholder="Διάγνωση (π.χ. Δυσαριθμησία)">
      
      <div class="flex justify-end gap-2 pt-2">
        <button onclick="closeNewStudentModal()" class="touch-btn bg-slate-800 text-slate-300 rounded text-xs">Ακύρωση</button>
        <button onclick="saveNewStudent()" class="touch-btn bg-brand-cyan text-slate-950 font-bold rounded text-xs">Αποθήκευση</button>
      </div>
    </div>
  </div>"""

new_modal = """  <!-- ==================================================== -->
  <!-- MODAL: MASTER STUDENT DOSSIER (ΠΛΗΡΗΣ ΚΑΡΤΕΛΑ ΜΑΘΗΤΗ) -->
  <!-- ==================================================== -->
  <div id="modal-student-dossier" class="fixed inset-0 z-50 bg-black/85 flex items-center justify-center p-2 sm:p-4 hidden backdrop-blur-sm">
    <div class="bg-brand-card border border-brand-border rounded-2xl max-w-4xl w-full max-h-[94vh] flex flex-col shadow-2xl overflow-hidden">
      
      <!-- Modal Header -->
      <div class="p-4 sm:p-5 border-b border-brand-border bg-slate-900/90 flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div id="dos-avatar-badge" class="w-11 h-11 rounded-xl bg-cyan-950 border border-cyan-700/80 text-cyan-300 font-bold text-lg flex items-center justify-center shadow-inner">
            👤
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 id="dos-modal-title" class="text-base sm:text-lg font-bold text-white tracking-wide">Πλήρης Καρτέλα Μαθητή</h2>
              <span id="dos-header-badge" class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700"></span>
            </div>
            <p class="text-[11px] text-slate-400">Τμήμα Ένταξης | ΔΗΜ.Ω.Σ. Γυμνάσιο Ξάνθης</p>
          </div>
        </div>
        <button onclick="closeStudentDossier()" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm transition-all">✕</button>
      </div>

      <!-- Dossier Sub-Tabs Navigation -->
      <div class="flex items-center gap-1.5 px-4 sm:px-5 py-2.5 bg-slate-950 border-b border-brand-border overflow-x-auto custom-scroll">
        <button type="button" onclick="switchDossierSubTab(1)" id="dossier-tab-1" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-cyan text-slate-950 transition-all whitespace-nowrap shadow-sm">
          👤 1. Προσωπικά & Γονείς
        </button>
        <button type="button" onclick="switchDossierSubTab(2)" id="dossier-tab-2" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:bg-slate-800 border border-brand-border transition-all whitespace-nowrap">
          🏥 2. Διαγνωστικό ΚΕΔΑΣΥ
        </button>
        <button type="button" onclick="switchDossierSubTab(3)" id="dossier-tab-3" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:bg-slate-800 border border-brand-border transition-all whitespace-nowrap">
          📐 3. Μαθηματικό Προφίλ & Άγχος
        </button>
        <button type="button" onclick="switchDossierSubTab(4)" id="dossier-tab-4" class="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:bg-slate-800 border border-brand-border transition-all whitespace-nowrap">
          🧠 4. Ψυχοκοινωνικό & Στόχοι ΕΠΕ
        </button>
      </div>

      <!-- Modal Body (Scrollable Form) -->
      <form id="dossier-form" onsubmit="event.preventDefault(); saveStudentDossier();" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 custom-scroll">
        <input type="hidden" id="dos-id">

        <!-- SUB-TAB 1: ΠΡΟΣΩΠΙΚΑ & ΓΟΝΕΙΣ -->
        <div id="dossier-subtab-view-1" class="space-y-4">
          
          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <h4 class="text-xs font-bold text-cyan-400 tracking-wider">ΣΤΟΙΧΕΙΑ ΜΑΘΗΤΗ/ΤΡΙΑΣ</h4>
            
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Όνομα *</label>
                <input type="text" id="dos-name" required class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Μιχαέλα">
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Επώνυμο</label>
                <input type="text" id="dos-surname" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Παπαδοπούλου">
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Φύλο</label>
                <select id="dos-gender" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400">
                  <option value="Κορίτσι">Κορίτσι</option>
                  <option value="Αγόρι">Αγόρι</option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Ημ/νία Γέννησης</label>
                <input type="date" id="dos-birthdate" onchange="updateCalculatedAgeDisplay()" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400">
                <span id="dos-age-display" class="text-[10px] text-cyan-400 mt-0.5 block"></span>
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Τάξη</label>
                <select id="dos-grade" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400">
                  <option value="Α' Γυμνασίου">Α' Γυμνασίου</option>
                  <option value="Β' Γυμνασίου">Β' Γυμνασίου</option>
                  <option value="Γ' Γυμνασίου">Γ' Γυμνασίου</option>
                </select>
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Τμήμα</label>
                <input type="text" id="dos-section" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Β1">
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Αριθμός Μητρώου (Α.Μ.)</label>
                <input type="text" id="dos-regno" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. 4521">
              </div>
            </div>
          </div>

          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <h4 class="text-xs font-bold text-cyan-400 tracking-wider">ΣΤΟΙΧΕΙΑ ΓΟΝΕΩΝ & ΕΠΙΚΟΙΝΩΝΙΑ</h4>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="bg-slate-950/80 p-3 rounded-lg border border-brand-border space-y-2">
                <span class="text-xs font-bold text-slate-300 flex items-center gap-1">👨 Στοιχεία Πατέρα</span>
                <div>
                  <label class="block text-[10px] text-slate-400">Ονοματεπώνυμο</label>
                  <input type="text" id="dos-father-name" class="w-full bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Ιωάννης Παπαδόπουλος">
                </div>
                <div>
                  <label class="block text-[10px] text-slate-400">Τηλέφωνο Επικοινωνίας</label>
                  <input type="tel" id="dos-father-phone" class="w-full bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. 6971234567">
                </div>
              </div>

              <div class="bg-slate-950/80 p-3 rounded-lg border border-brand-border space-y-2">
                <span class="text-xs font-bold text-slate-300 flex items-center gap-1">👩 Στοιχεία Μητέρας</span>
                <div>
                  <label class="block text-[10px] text-slate-400">Ονοματεπώνυμο</label>
                  <input type="text" id="dos-mother-name" class="w-full bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Ελένη Παπαδοπούλου">
                </div>
                <div>
                  <label class="block text-[10px] text-slate-400">Τηλέφωνο Επικοινωνίας</label>
                  <input type="tel" id="dos-mother-phone" class="w-full bg-slate-900 border border-slate-800 rounded p-1.5 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. 6987654321">
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Διεύθυνση Κατοικίας</label>
                <input type="text" id="dos-address" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Ξάνθη">
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Email Επικοινωνίας</label>
                <input type="email" id="dos-email" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. parents@example.com">
              </div>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">Σημειώσεις Οικογενειακού Πλαισίου / Συνεργασίας</label>
              <textarea id="dos-family-notes" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="Σημειώσεις για την επικοινωνία με τους γονείς..."></textarea>
            </div>

          </div>

        </div>

        <!-- SUB-TAB 2: ΔΙΑΓΝΩΣΤΙΚΟ ΚΕΔΑΣΥ -->
        <div id="dossier-subtab-view-2" class="space-y-4 hidden">
          
          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <h4 class="text-xs font-bold text-cyan-400 tracking-wider">ΙΑΤΡΟΠΑΙΔΑΓΩΓΙΚΗ ΕΚΘΕΣΗ & ΓΝΩΜΑΤΕΥΣΗ</h4>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Φορέας Διάγνωσης</label>
                <input type="text" id="dos-diag-authority" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. ΚΕΔΑΣΥ Ξάνθης">
              </div>
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">Αριθμός & Ημ/νία Πρωτοκόλλου</label>
                <input type="text" id="dos-diag-protocol" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. 284/12-04-2024">
              </div>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">Είδος Ειδικών Εκπαιδευτικών Αναγκών / Διάγνωση *</label>
              <input type="text" id="dos-diag-type" required class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Ειδική Μαθησιακή Δυσκολία (Δυσαριθμησία & Δυσλεξία)">
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">Ιστορικό Εκπαιδευτικής Υποστήριξης</label>
              <input type="text" id="dos-diag-history" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. 2ο έτος φοίτησης στο Τμήμα Ένταξης, προηγούμενη στήριξη στο Δημοτικό">
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">Γενικές Παρατηρήσεις / Σημειώσεις Εκπαιδευτικού</label>
              <textarea id="dos-notes" rows="3" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="Γενικές παιδαγωγικές παρατηρήσεις για τον/την μαθητή/τρια..."></textarea>
            </div>
          </div>

        </div>

        <!-- SUB-TAB 3: ΜΑΘΗΣΙΑΚΟ ΠΡΟΦΙΛ & ΑΓΧΟΣ -->
        <div id="dossier-subtab-view-3" class="space-y-4 hidden">
          
          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <h4 class="text-xs font-bold text-cyan-400 tracking-wider">ΓΝΩΣΤΙΚΟ & ΜΑΘΗΣΙΑΚΟ ΠΡΟΦΙΛ ΣΤΑ ΜΑΘΗΜΑΤΙΚΑ</h4>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">📊 Επίπεδο Μαθηματικού Άγχους (Math Anxiety)</label>
                <select id="dos-math-anxiety" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400 font-bold">
                  <option value="Χαμηλό">🟢 Χαμηλό Άγχος (Άνετη συμμετοχή)</option>
                  <option value="Μέτριο" selected>🟡 Μέτριο Άγχος (Χρειάζεται ενθάρρυνση)</option>
                  <option value="Υψηλό">🔴 Υψηλό Άγχος (Άγχος επίδοσης / αποφυγή)</option>
                </select>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">🧠 Προτιμώμενο Μαθησιακό Στυλ</label>
                <select id="dos-learning-style" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400">
                  <option value="Οπτικό / Πολυαισθητηριακό">Οπτικό / Πολυαισθητηριακό</option>
                  <option value="Ακουστικό / Προφορικό">Ακουστικό / Προφορικό</option>
                  <option value="Κιναισθητικό / Απτικό">Κιναισθητικό / Απτικό (Χειραπτικό υλικό)</option>
                  <option value="Δομημένο / Βήμα-προς-Βήμα">Δομημένο / Βήμα-προς-Βήμα</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">✨ Δυνατά Σημεία στα Μαθηματικά (Strengths)</label>
              <textarea id="dos-math-strengths" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Εξαιρετική οπτική αντίληψη, αγάπη για τα γεωμετρικά σχήματα, δεξιότητα στο Geogebra..."></textarea>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">⚠️ Κύρια Εμπόδια & Τομείς Δυσκολίας (Target Weaknesses)</label>
              <textarea id="dos-math-weaknesses" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Δυσκολία στις πράξεις με κλάσματα, αυτοματοποίηση προπαίδειας, επίλυση εξισώσεων..."></textarea>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">🛠️ Αποτελεσματικές Διδακτικές Στρατηγικές & Προσαρμογές</label>
              <textarea id="dos-math-strategies" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="π.χ. Χρήση αριθμογραμμής, βήμα-προς-βήμα καθοδήγηση (scaffolding), χρωματική κωδικοποίηση προσήμων..."></textarea>
            </div>

          </div>

        </div>

        <!-- SUB-TAB 4: ΨΥΧΟΚΟΙΝΩΝΙΚΟ & ΣΤΟΧΟΙ ΕΠΕ -->
        <div id="dossier-subtab-view-4" class="space-y-4 hidden">
          
          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <h4 class="text-xs font-bold text-cyan-400 tracking-wider">ΨΥΧΟΚΟΙΝΩΝΙΚΟ ΠΡΟΦΙΛ & ΣΥΜΠΕΡΙΦΟΡΑ</h4>
            
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">🌟 Αυτοαντίληψη & Αυτοπεποίθηση</label>
                <textarea id="dos-self-concept" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="Στάση απέναντι στην προσπάθεια..."></textarea>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">⏳ Εστίαση & Διάρκεια Προσοχής</label>
                <textarea id="dos-attention-focus" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="Διάρκεια συγκέντρωσης..."></textarea>
              </div>

              <div>
                <label class="block text-[11px] font-semibold text-slate-300 mb-1">🤝 Κοινωνική Αλληλεπίδραση</label>
                <textarea id="dos-social-interaction" rows="2" class="w-full bg-slate-950 border border-brand-border rounded-lg p-2 text-xs text-white outline-none focus:border-cyan-400" placeholder="Συνεργασία στην ομάδα..."></textarea>
              </div>
            </div>
          </div>

          <!-- IEP TARGETS BUILDER -->
          <div class="bg-slate-900/60 border border-brand-border rounded-xl p-4 space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-cyan-400 tracking-wider">🎯 ΣΤΟΧΟΙ Ε.Π.Ε. 2026-2027</h4>
              <span class="text-[11px] text-slate-400">Εξατομικευμένη Στοχοθεσία</span>
            </div>

            <div class="flex gap-2">
              <select id="dos-new-target-area" class="bg-slate-950 border border-brand-border rounded-lg px-2 py-1.5 text-xs text-white w-36 flex-shrink-0">
                <option value="Αριθμητική">Αριθμητική</option>
                <option value="Άλγεβρα">Άλγεβρα</option>
                <option value="Γεωμετρία">Γεωμετρία</option>
                <option value="Στοχαστικά">Στοχαστικά</option>
                <option value="Εμπλοκή">Εμπλοκή</option>
                <option value="Μαθηματικό Προφίλ">Μαθηματικό Προφίλ</option>
              </select>
              <input type="text" id="dos-new-target-text" placeholder="Νέος διδακτικός στόχος Ε.Π.Ε...." class="flex-1 bg-slate-950 border border-brand-border rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-cyan-400">
              <button type="button" onclick="addIepTargetToDossier()" class="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs rounded-lg whitespace-nowrap">+ Προσθήκη</button>
            </div>

            <div id="dos-iep-targets-container" class="space-y-2 pt-1 max-h-48 overflow-y-auto custom-scroll"></div>
          </div>

        </div>

      </form>

      <!-- Modal Footer -->
      <div class="p-4 sm:p-5 border-t border-brand-border bg-slate-900/90 flex items-center justify-between gap-3">
        <div>
          <button type="button" id="dos-btn-export-docx" onclick="downloadCurrentDossierDocx()" class="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-800/80 text-xs font-semibold flex items-center gap-1.5 transition-all">
            📄 Εξαγωγή Word (.docx)
          </button>
        </div>
        <div class="flex items-center gap-2">
          <button type="button" onclick="closeStudentDossier()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-all">
            Ακύρωση
          </button>
          <button type="button" onclick="saveStudentDossier()" class="px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-black text-xs shadow-lg active:scale-95 transition-all">
            💾 Αποθήκευση Καρτέλας
          </button>
        </div>
      </div>

    </div>
  </div>"""

html = html.replace(old_modal, new_modal)

with open("app/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated modal-student-dossier in index.html!")
