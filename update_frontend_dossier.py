# -*- coding: utf-8 -*-
import re

with open("app/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update navigation tab text to "Καρτέλες Μαθητών"
html = html.replace(
    '''        <button onclick="switchTab('students')" id="tab-students" class="touch-btn text-xs sm:text-sm font-semibold rounded-lg text-slate-300 hover:bg-slate-800 border border-brand-border">
          Μαθητές
        </button>''',
    '''        <button onclick="switchTab('students')" id="tab-students" class="touch-btn text-xs sm:text-sm font-semibold rounded-lg text-slate-300 hover:bg-slate-800 border border-brand-border">
          👤 Καρτέλες Μαθητών
        </button>'''
)

# 2. Replace view-students section
new_view_students = """    <!-- ========================================== -->
    <!-- TAB 2: MASTER STUDENT DOSSIERS VIEW        -->
    <!-- ========================================== -->
    <section id="view-students" class="space-y-4 hidden">
      
      <!-- Top Control & Filter Bar -->
      <div class="flex flex-wrap items-center justify-between gap-3 bg-brand-card border border-brand-border rounded-xl p-3 shadow-sm">
        <div class="flex items-center gap-1.5 flex-wrap" id="grade-filter-buttons">
          <button onclick="filterStudentsByGrade('ALL')" id="filter-grade-all" class="px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-cyan text-slate-950 transition-all">Όλοι οι Μαθητές</button>
          <button onclick="filterStudentsByGrade('Α')" id="filter-grade-a" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-brand-border transition-all">Α' Γυμνασίου</button>
          <button onclick="filterStudentsByGrade('Β')" id="filter-grade-b" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-brand-border transition-all">Β' Γυμνασίου</button>
          <button onclick="filterStudentsByGrade('Γ')" id="filter-grade-c" class="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-brand-border transition-all">Γ' Γυμνασίου</button>
        </div>

        <div class="flex items-center gap-2 flex-1 sm:flex-none justify-end">
          <input type="text" id="student-search-input" oninput="renderStudentsGrid()" placeholder="🔍 Αναζήτηση μαθητή..."
                 class="bg-slate-900 border border-brand-border rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none focus:ring-1 focus:ring-cyan-500 w-full sm:w-48">
          <button onclick="openStudentDossier('new')" class="touch-btn bg-brand-cyan hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-lg shadow-sm whitespace-nowrap">
            + Νέα Καρτέλα
          </button>
        </div>
      </div>

      <!-- Master Students Cards Grid -->
      <div id="students-cards-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4"></div>

      <!-- Cognitive / Bloom Inspector Drawer (Appears when clicking Inspect on a student) -->
      <div id="cognitive-bloom-drawer" class="bg-brand-card border border-brand-border rounded-xl p-5 space-y-4 shadow-lg hidden">
        <div class="flex items-center justify-between pb-3 border-b border-brand-border">
          <div class="flex items-center gap-2">
            <span class="text-lg">📊</span>
            <div>
              <h3 id="cog-student-name" class="text-sm font-bold text-white">Γνωστική Χαρτογράφηση</h3>
              <p class="text-[11px] text-slate-400">Επίπεδα Bloom (1-5) & Πληρότητα ανά Τομέα Μαθηματικών</p>
            </div>
          </div>
          <button onclick="closeCognitiveDrawer()" class="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-900 border border-slate-800">✕ Κλείσιμο</button>
        </div>
        <div id="coverage-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"></div>
        <div id="domain-detail-card" class="bg-slate-900 border border-cyan-800/60 rounded-xl p-4 text-xs space-y-3 hidden transition-all shadow-lg"></div>
      </div>

    </section>"""

# Replace the view-students section
html = re.sub(r'<!-- ===+\s+-->\s+<!-- TAB 2: STUDENTS VIEW\s+-->\s+<!-- ===+\s+-->\s+<section id="view-students".*?</section>', new_view_students, html, flags=re.DOTALL)

with open("app/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated view-students section in index.html!")
