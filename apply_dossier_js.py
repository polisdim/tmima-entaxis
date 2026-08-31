# -*- coding: utf-8 -*-
with open("app/index.html", "r", encoding="utf-8") as f:
    html = f.read()

dossier_js = """
    // =========================================================================
    // MASTER STUDENT DOSSIER & GRID MANAGEMENT
    // =========================================================================
    let currentGradeFilter = 'ALL';
    let currentDossierIepTargets = [];

    function calculateStudentAge(birthDateStr) {
      if (!birthDateStr) return '';
      try {
        const bDate = new Date(birthDateStr);
        if (isNaN(bDate.getTime())) return '';
        const today = new Date();
        let age = today.getFullYear() - bDate.getFullYear();
        const m = today.getMonth() - bDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < bDate.getDate())) {
          age--;
        }
        return age > 0 ? `${age} ετών` : '';
      } catch (e) {
        return '';
      }
    }

    function filterStudentsByGrade(grade) {
      currentGradeFilter = grade;
      ['all', 'a', 'b', 'c'].forEach(g => {
        const btn = document.getElementById(`filter-grade-${g}`);
        if (btn) {
          const match = (g === 'all' && grade === 'ALL') || (g === 'a' && grade === 'Α') || (g === 'b' && grade === 'Β') || (g === 'c' && grade === 'Γ');
          btn.className = match
            ? 'px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-cyan text-slate-950 transition-all shadow-sm'
            : 'px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-brand-border transition-all';
        }
      });
      renderStudentsGrid();
    }

    function renderStudentsGrid() {
      const grid = document.getElementById('students-cards-grid');
      if (!grid) return;
      grid.innerHTML = '';

      const searchInput = document.getElementById('student-search-input');
      const q = searchInput ? searchInput.value.trim().toLowerCase() : '';

      let list = (appData.students || []).slice();

      if (currentGradeFilter !== 'ALL') {
        list = list.filter(s => {
          const g = (s.grade || '') + (s.class_section || '');
          return g.includes(currentGradeFilter);
        });
      }

      if (q) {
        list = list.filter(s => {
          const full = `${s.name || ''} ${s.surname || ''} ${s.grade || ''} ${s.class_section || ''} ${s.diagnosis || ''}`.toLowerCase();
          return full.includes(q);
        });
      }

      if (list.length === 0) {
        grid.innerHTML = `
          <div class="col-span-full py-12 text-center text-slate-500 bg-brand-card border border-brand-border rounded-xl">
            <span class="text-3xl block mb-2">🔍</span>
            <p class="text-sm font-semibold">Δεν βρέθηκαν μαθητές με τα επιλεγμένα κριτήρια.</p>
          </div>`;
        return;
      }

      list.forEach(st => {
        const full_name = `${st.name || ''} ${st.surname || ''}`.trim();
        const ageStr = calculateStudentAge(st.birth_date);
        const father = st.parent_father || {};
        const mother = st.parent_mother || {};
        const mprof = st.math_profile || {};
        const diag = st.diagnosis_info || {};
        const anxiety = mprof.math_anxiety || 'Μέτριο';
        const isBoy = (st.gender || 'Αγόρι') === 'Αγόρι';

        const anxietyBadge = anxiety === 'Χαμηλό'
          ? '<span class="px-2 py-0.5 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-800 text-[11px] font-bold">🟢 Χαμηλό Άγχος</span>'
          : anxiety === 'Υψηλό'
          ? '<span class="px-2 py-0.5 rounded-md bg-rose-950 text-rose-300 border border-rose-800 text-[11px] font-bold">🔴 Υψηλό Άγχος</span>'
          : '<span class="px-2 py-0.5 rounded-md bg-amber-950 text-amber-300 border border-amber-800 text-[11px] font-bold">🟡 Μέτριο Άγχος</span>';

        const stObs = (appData.observations || []).filter(o => o.student_id === st.id);
        const covTotal = (st.coverage && st.coverage.total) || 0;

        grid.innerHTML += `
          <div class="bg-brand-card border border-brand-border hover:border-slate-700 rounded-2xl p-4 sm:p-5 space-y-4 transition-all shadow-sm flex flex-col justify-between">
            
            <!-- Top Row: Avatar & Basic Info -->
            <div class="space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-2xl ${isBoy ? 'bg-cyan-950/80 border-cyan-800/80 text-cyan-300' : 'bg-purple-950/80 border-purple-800/80 text-purple-300'} border text-2xl flex items-center justify-center shadow-inner flex-shrink-0">
                    ${isBoy ? '👦' : '👧'}
                  </div>
                  <div>
                    <h3 class="text-base font-bold text-white leading-tight flex items-center gap-1.5 flex-wrap">
                      <span>${full_name}</span>
                      <span class="text-xs px-2 py-0.5 rounded bg-slate-900 text-cyan-300 border border-slate-700 font-normal">${st.grade || ''} ${st.class_section ? `(${st.class_section})` : ''}</span>
                    </h3>
                    <p class="text-[11px] text-slate-400 mt-0.5">
                      ${st.gender || ''} ${ageStr ? `• ${ageStr}` : ''} ${st.registration_no ? `• Α.Μ: ${st.registration_no}` : ''}
                    </p>
                  </div>
                </div>

                <div class="bg-slate-900 border border-brand-border rounded-xl px-2.5 py-1.5 text-center flex-shrink-0">
                  <span class="text-[10px] text-slate-400 block font-semibold">Πληρότητα</span>
                  <span class="text-sm font-bold text-brand-cyan">${covTotal}%</span>
                </div>
              </div>

              <!-- Diagnosis Row -->
              <div class="p-2.5 rounded-xl bg-slate-950/80 border border-brand-border text-xs space-y-1">
                <div class="flex items-center justify-between text-[11px] text-slate-400 font-semibold">
                  <span class="flex items-center gap-1">🏥 <span>${diag.authority || 'ΚΕΔΑΣΥ Ξάνθης'}</span> ${diag.protocol_no ? `<span class="text-slate-500 font-mono">(${diag.protocol_no})</span>` : ''}</span>
                </div>
                <p class="text-slate-200 font-medium text-[11px] line-clamp-1">${diag.diagnosis_type || st.diagnosis || 'Ειδική Μαθησιακή Δυσκολία'}</p>
              </div>

              <!-- Parents Contact Grid -->
              <div class="grid grid-cols-2 gap-2 text-[11px]">
                <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                  <span class="text-slate-400 block text-[10px] font-semibold">👨 Πατέρας:</span>
                  <span class="text-white font-medium block truncate">${father.name || '-'}</span>
                  ${father.phone ? `<a href="tel:${father.phone}" class="text-cyan-400 hover:underline font-mono text-[10px]">📞 ${father.phone}</a>` : '<span class="text-slate-500 text-[10px]">-</span>'}
                </div>
                <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                  <span class="text-slate-400 block text-[10px] font-semibold">👩 Μητέρα:</span>
                  <span class="text-white font-medium block truncate">${mother.name || '-'}</span>
                  ${mother.phone ? `<a href="tel:${mother.phone}" class="text-cyan-400 hover:underline font-mono text-[10px]">📞 ${mother.phone}</a>` : '<span class="text-slate-500 text-[10px]">-</span>'}
                </div>
              </div>

              <!-- Math Profile & Anxiety Badges -->
              <div class="flex items-center justify-between gap-2 flex-wrap pt-1">
                <div class="flex items-center gap-1.5 flex-wrap">
                  ${anxietyBadge}
                  <span class="px-2 py-0.5 rounded-md bg-purple-950/60 text-purple-300 border border-purple-800 text-[11px] font-semibold">🧠 ${mprof.learning_style || 'Οπτικό'}</span>
                </div>
                <span class="text-[11px] text-slate-400 font-mono font-semibold">${stObs.length} καταγραφές</span>
              </div>
            </div>

            <!-- Card Bottom Action Buttons -->
            <div class="pt-3 border-t border-brand-border flex items-center justify-between gap-2">
              <button onclick="openStudentDossier('${st.id}')" class="flex-1 py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-300 font-bold text-xs border border-cyan-800/60 flex items-center justify-center gap-1.5 transition-all active:scale-95 shadow-sm">
                ✏️ Πλήρης Καρτέλα
              </button>
              <button onclick="openCognitiveDrawer('${st.id}')" class="py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold text-xs border border-brand-border flex items-center gap-1 transition-all active:scale-95">
                📊 Bloom
              </button>
              <button onclick="downloadDocxForStudent('${st.id}')" class="py-2 px-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold text-xs border border-brand-border flex items-center gap-1 transition-all active:scale-95" title="Εξαγωγή Word">
                📄
              </button>
            </div>

          </div>`;
      });
    }

    function openStudentDossier(stId) {
      const modal = document.getElementById('modal-student-dossier');
      if (!modal) return;

      const isNew = stId === 'new' || !stId;
      const st = isNew ? null : (appData.students || []).find(s => s.id === stId);

      // Reset & set values
      document.getElementById('dos-id').value = isNew ? '' : st.id;
      document.getElementById('dos-name').value = st ? (st.name || '') : '';
      document.getElementById('dos-surname').value = st ? (st.surname || '') : '';
      document.getElementById('dos-gender').value = st ? (st.gender || 'Αγόρι') : 'Αγόρι';
      document.getElementById('dos-birthdate').value = st ? (st.birth_date || '') : '';
      document.getElementById('dos-grade').value = st ? (st.grade || "Β' Γυμνασίου") : "Β' Γυμνασίου";
      document.getElementById('dos-section').value = st ? (st.class_section || '') : '';
      document.getElementById('dos-regno').value = st ? (st.registration_no || '') : '';

      const father = (st && st.parent_father) || {};
      document.getElementById('dos-father-name').value = father.name || '';
      document.getElementById('dos-father-phone').value = father.phone || '';

      const mother = (st && st.parent_mother) || {};
      document.getElementById('dos-mother-name').value = mother.name || '';
      document.getElementById('dos-mother-phone').value = mother.phone || '';

      const contact = (st && st.contact) || {};
      document.getElementById('dos-address').value = contact.address || '';
      document.getElementById('dos-email').value = contact.email || '';
      document.getElementById('dos-family-notes').value = contact.family_notes || '';

      const diag = (st && st.diagnosis_info) || {};
      document.getElementById('dos-diag-authority').value = diag.authority || 'ΚΕΔΑΣΥ Ξάνθης';
      document.getElementById('dos-diag-protocol').value = diag.protocol_no || '';
      document.getElementById('dos-diag-type').value = diag.diagnosis_type || (st ? st.diagnosis : '') || '';
      document.getElementById('dos-diag-history').value = diag.support_history || '';
      document.getElementById('dos-notes').value = st ? (st.notes || '') : '';

      const mprof = (st && st.math_profile) || {};
      document.getElementById('dos-math-anxiety').value = mprof.math_anxiety || 'Μέτριο';
      document.getElementById('dos-learning-style').value = mprof.learning_style || 'Οπτικό / Πολυαισθητηριακό';
      document.getElementById('dos-math-strengths').value = mprof.strengths || '';
      document.getElementById('dos-math-weaknesses').value = mprof.weaknesses || '';
      document.getElementById('dos-math-strategies').value = mprof.effective_strategies || '';

      const psprof = (st && st.psychosocial_profile) || {};
      document.getElementById('dos-self-concept').value = psprof.self_concept || '';
      document.getElementById('dos-attention-focus').value = psprof.attention_focus || '';
      document.getElementById('dos-social-interaction').value = psprof.social_interaction || '';

      // Title & badges
      const titleEl = document.getElementById('dos-modal-title');
      const badgeEl = document.getElementById('dos-header-badge');
      const avatarEl = document.getElementById('dos-avatar-badge');

      if (isNew) {
        if (titleEl) titleEl.innerText = 'Νέα Καρτέλα Μαθητή';
        if (badgeEl) badgeEl.innerText = 'Νέα Εγγραφή';
        if (avatarEl) avatarEl.innerText = '➕';
        currentDossierIepTargets = [];
      } else {
        if (titleEl) titleEl.innerText = `${st.name} ${st.surname || ''}`.trim();
        if (badgeEl) badgeEl.innerText = `${st.grade || ''} ${st.class_section || ''}`;
        if (avatarEl) avatarEl.innerText = (st.gender === 'Κορίτσι') ? '👧' : '👦';
        currentDossierIepTargets = (st.iep_targets || []).slice();
      }

      updateCalculatedAgeDisplay();
      renderDossierIepTargetsList();
      switchDossierSubTab(1);
      modal.classList.remove('hidden');
    }

    function closeStudentDossier() {
      const modal = document.getElementById('modal-student-dossier');
      if (modal) modal.classList.add('hidden');
    }

    function switchDossierSubTab(tabNum) {
      for (let i = 1; i <= 4; i++) {
        const view = document.getElementById(`dossier-subtab-view-${i}`);
        const btn = document.getElementById(`dossier-tab-${i}`);
        if (view) {
          if (i === tabNum) view.classList.remove('hidden');
          else view.classList.add('hidden');
        }
        if (btn) {
          btn.className = (i === tabNum)
            ? 'px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-cyan text-slate-950 transition-all whitespace-nowrap shadow-sm'
            : 'px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:bg-slate-800 border border-brand-border transition-all whitespace-nowrap';
        }
      }
    }

    function updateCalculatedAgeDisplay() {
      const bDateVal = document.getElementById('dos-birthdate').value;
      const ageDisp = document.getElementById('dos-age-display');
      if (ageDisp) {
        const age = calculateStudentAge(bDateVal);
        ageDisp.innerText = age ? `Ηλικία: ${age}` : '';
      }
    }

    function renderDossierIepTargetsList() {
      const c = document.getElementById('dos-iep-targets-container');
      if (!c) return;
      c.innerHTML = '';
      if (currentDossierIepTargets.length === 0) {
        c.innerHTML = '<p class="text-xs text-slate-500 italic p-2">Δεν έχουν προστεθεί ακόμη στόχοι Ε.Π.Ε.</p>';
        return;
      }
      currentDossierIepTargets.forEach((t, idx) => {
        const statusColor = t.status === 'Εμπεδώθηκε' ? 'text-emerald-300 border-emerald-700 bg-emerald-950/60'
          : t.status === 'Επιτεύχθηκε' ? 'text-cyan-300 border-cyan-700 bg-cyan-950/60'
          : 'text-amber-300 border-amber-700 bg-amber-950/60';

        c.innerHTML += `
          <div class="p-2.5 rounded-xl bg-slate-950 border border-brand-border flex items-center justify-between gap-2 text-xs">
            <div class="flex items-center gap-2 flex-1">
              <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-cyan-300 font-bold text-[10px] flex-shrink-0">${t.area || 'Μαθηματικά'}</span>
              <span class="text-slate-200">${t.target}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <button type="button" onclick="toggleIepTargetStatus(${idx})" class="px-2 py-1 rounded-lg border font-bold text-[11px] ${statusColor} hover:scale-105 transition-all">
                ${t.status || 'Σε εξέλιξη'}
              </button>
              <button type="button" onclick="removeIepTargetFromDossier(${idx})" class="text-slate-500 hover:text-rose-400 p-1 text-xs">✕</button>
            </div>
          </div>`;
      });
    }

    function addIepTargetToDossier() {
      const areaEl = document.getElementById('dos-new-target-area');
      const textEl = document.getElementById('dos-new-target-text');
      const text = textEl ? textEl.value.trim() : '';
      if (!text) return;
      currentDossierIepTargets.push({
        id: 't_' + Date.now(),
        area: areaEl ? areaEl.value : 'Μαθηματικά',
        target: text,
        status: 'Σε εξέλιξη'
      });
      if (textEl) textEl.value = '';
      renderDossierIepTargetsList();
    }

    function removeIepTargetFromDossier(idx) {
      currentDossierIepTargets.splice(idx, 1);
      renderDossierIepTargetsList();
    }

    function toggleIepTargetStatus(idx) {
      const t = currentDossierIepTargets[idx];
      if (!t) return;
      const order = ['Σε εξέλιξη', 'Επιτεύχθηκε', 'Εμπεδώθηκε'];
      const curIdx = order.indexOf(t.status || 'Σε εξέλιξη');
      t.status = order[(curIdx + 1) % order.length];
      renderDossierIepTargetsList();
    }

    async function saveStudentDossier() {
      const id = document.getElementById('dos-id').value;
      const name = document.getElementById('dos-name').value.trim();
      if (!name) {
        alert('Παρακαλώ συμπληρώστε το όνομα του/της μαθητή/τριας.');
        switchDossierSubTab(1);
        return;
      }

      const existingSt = id ? (appData.students || []).find(s => s.id === id) : null;

      const payload = {
        id: id || ('st_' + Date.now()),
        name: name,
        surname: document.getElementById('dos-surname').value.trim(),
        code: (existingSt && existingSt.code) || ('S0' + ((appData.students || []).length + 1)),
        gender: document.getElementById('dos-gender').value,
        birth_date: document.getElementById('dos-birthdate').value,
        grade: document.getElementById('dos-grade').value,
        class_section: document.getElementById('dos-section').value.trim(),
        registration_no: document.getElementById('dos-regno').value.trim(),
        parent_father: {
          name: document.getElementById('dos-father-name').value.trim(),
          phone: document.getElementById('dos-father-phone').value.trim()
        },
        parent_mother: {
          name: document.getElementById('dos-mother-name').value.trim(),
          phone: document.getElementById('dos-mother-phone').value.trim()
        },
        contact: {
          address: document.getElementById('dos-address').value.trim(),
          email: document.getElementById('dos-email').value.trim(),
          family_notes: document.getElementById('dos-family-notes').value.trim()
        },
        diagnosis_info: {
          authority: document.getElementById('dos-diag-authority').value.trim(),
          protocol_no: document.getElementById('dos-diag-protocol').value.trim(),
          diagnosis_type: document.getElementById('dos-diag-type').value.trim(),
          support_history: document.getElementById('dos-diag-history').value.trim()
        },
        diagnosis: document.getElementById('dos-diag-type').value.trim(),
        notes: document.getElementById('dos-notes').value.trim(),
        math_profile: {
          math_anxiety: document.getElementById('dos-math-anxiety').value,
          learning_style: document.getElementById('dos-learning-style').value,
          strengths: document.getElementById('dos-math-strengths').value.trim(),
          weaknesses: document.getElementById('dos-math-weaknesses').value.trim(),
          effective_strategies: document.getElementById('dos-math-strategies').value.trim()
        },
        psychosocial_profile: {
          self_concept: document.getElementById('dos-self-concept').value.trim(),
          attention_focus: document.getElementById('dos-attention-focus').value.trim(),
          social_interaction: document.getElementById('dos-social-interaction').value.trim()
        },
        iep_targets: currentDossierIepTargets,
        coverage: (existingSt && existingSt.coverage) || { arithmetic: 10, algebra: 10, geometry: 10, stochastics: 10, total: 10 },
        created_at: (existingSt && existingSt.created_at) || new Date().toISOString()
      };

      await authFetch('/api/student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      closeStudentDossier();
      await loadData();
      alert(`Η καρτέλα του/της ${payload.name} αποθηκεύτηκε επιτυχώς!`);
    }

    function openCognitiveDrawer(stId) {
      selectStudent(stId);
      const drawer = document.getElementById('cognitive-bloom-drawer');
      const st = (appData.students || []).find(s => s.id === stId);
      if (drawer && st) {
        document.getElementById('cog-student-name').innerText = `Γνωστική Χαρτογράφηση: ${st.name} ${st.surname || ''}`.trim();
        drawer.classList.remove('hidden');
        drawer.scrollIntoView({ behavior: 'smooth' });
      }
    }

    function closeCognitiveDrawer() {
      const drawer = document.getElementById('cognitive-bloom-drawer');
      if (drawer) drawer.classList.add('hidden');
    }

    function downloadDocxForStudent(stId) {
      window.location.href = `/api/export_docx?student_id=${stId}&doc_type=1_initial`;
    }

    function downloadCurrentDossierDocx() {
      const id = document.getElementById('dos-id').value;
      if (!id) {
        alert('Παρακαλώ αποθηκεύστε πρώτα την καρτέλα του μαθητή.');
        return;
      }
      downloadDocxForStudent(id);
    }
"""

# Insert dossier_js before function renderStudents()
html = html.replace("function renderStudents() {", dossier_js + "\n    function renderStudents() {\n      renderStudentsGrid();")

with open("app/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Injected master dossier JS into index.html successfully!")
