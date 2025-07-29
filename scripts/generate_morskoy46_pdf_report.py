import os
import pandas as pd
from fpdf import FPDF  # fpdf2
from datetime import datetime

# Font path for Unicode support
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts', 'dejavu-fonts-ttf-2.37')
FONT_PATH = os.path.join(FONT_DIR, 'ttf', 'DejaVuSans.ttf')

# --- CONFIGURABLE PATHS ---
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, '../data/processed/Morskoy46')
ENRICHED_CSV = os.path.join(DATA_DIR, 'gosuslugi_seized_fuzzy_matches_enriched_Morskoy46.csv')
DAMAGE_CSV = os.path.join(ROOT, '../data/processed/damage_assessment_clean_en.csv')
MEDIA_METADATA_CSV = os.path.join(DATA_DIR, 'telegram_media_metadata.csv')
REFERENCE_IMG_DIR = os.path.join(DATA_DIR, 'telegram_images_sorted/building_facade_reference/46_only')
HISTORICAL_IMG_DIR = os.path.join(DATA_DIR, 'telegram_images_sorted/building_facade_reference/historical')
OUTPUT_PDF = os.path.join(DATA_DIR, 'Morskoy46_evidence_report.pdf')

# --- LOAD DATA ---
def safe_load_csv(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

enriched_df = safe_load_csv(ENRICHED_CSV)
damage_df = safe_load_csv(DAMAGE_CSV)
media_df = safe_load_csv(MEDIA_METADATA_CSV)

# --- PDF GENERATION ---
class PDF(FPDF):
    def header(self):
        self.set_font('DejaVu', 'B', 16)
        self.cell(0, 10, 'Morskoy 46 Forensic Evidence Report', ln=True, align='C')
        self.set_font('DejaVu', '', 10)
        self.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True, align='C')
        self.ln(5)
    def chapter_title(self, title):
        self.set_font('DejaVu', 'B', 13)
        self.cell(0, 8, title, ln=True, align='L')
        self.ln(2)
    def chapter_body(self, text):
        self.set_font('DejaVu', '', 11)
        self.multi_cell(0, 7, text)
        self.ln(2)
    def add_image(self, img_path, caption=None, w=100):
        if os.path.exists(img_path):
            self.image(img_path, w=w)
            if caption:
                self.set_font('DejaVu', 'I', 9)
                self.cell(0, 6, caption, ln=True, align='C')
            self.ln(2)

pdf = PDF()
pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
pdf.add_font('DejaVu', 'B', FONT_PATH, uni=True)
pdf.add_font('DejaVu', 'I', FONT_PATH, uni=True)
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# --- SUMMARY SECTION ---
pdf.chapter_title('1. Overview and Context')
pdf.chapter_body('''This report aggregates all available forensic, administrative, and visual evidence for Morskoy 46 (Mariupol). It integrates occupation administration records, damage assessment, Telegram media, and curated visual documentation. All data is normalized and cross-referenced to support forensic mapping, machine learning, and evidence-based reporting.\n\nSources: occupation decrees, seized property tables, Telegram chat images, curated historical imagery, and damage assessment databases.''')

# --- ENRICHED DATA SUMMARY ---
pdf.chapter_title('2. Seized Properties & Administrative Data')
if not enriched_df.empty:
    preview = enriched_df.head(10).to_string(index=False)
    pdf.chapter_body(f'First 10 rows (see CSV for full data):\n{preview}')
else:
    pdf.chapter_body('No enriched seized property data found.')

# --- DAMAGE ASSESSMENT SUMMARY ---
pdf.chapter_title('3. Damage Assessment Extract')
if not damage_df.empty:
    preview = damage_df.head(10).to_string(index=False)
    pdf.chapter_body(f'First 10 rows (see CSV for full data):\n{preview}')
else:
    pdf.chapter_body('No damage assessment data found.')

# --- TELEGRAM MEDIA SUMMARY ---
pdf.chapter_title('4. Telegram Media Metadata')
if not media_df.empty:
    preview = media_df.head(10).to_string(index=False)
    pdf.chapter_body(f'First 10 rows (see CSV for full data):\n{preview}')
else:
    pdf.chapter_body('No Telegram media metadata found.')

# --- CURATED IMAGE GALLERY ---
pdf.chapter_title('5. Curated Visual Evidence (Reference)')
img_paths = []
if os.path.isdir(REFERENCE_IMG_DIR):
    img_paths += [os.path.join(REFERENCE_IMG_DIR, f) for f in os.listdir(REFERENCE_IMG_DIR) if f.lower().endswith('.jpg')]
if os.path.isdir(HISTORICAL_IMG_DIR):
    img_paths += [os.path.join(HISTORICAL_IMG_DIR, f) for f in os.listdir(HISTORICAL_IMG_DIR) if f.lower().endswith('.jpg')]
img_paths = img_paths[:6]  # Limit for PDF size
for img_path in img_paths:
    pdf.add_image(img_path, caption=os.path.basename(img_path))

pdf.chapter_title('6. Notes & Analytical Context')
pdf.chapter_body('''- All data sources are cross-referenced and normalized for forensic traceability.\n- Administrative violence is executed through routine municipal procedures; see project notes for critical theory context.\n- For full data, see accompanying CSVs and scripts.\n- Contact: project maintainer for further queries or collaboration.''')

pdf.output(OUTPUT_PDF)
print(f"PDF report generated: {OUTPUT_PDF}")
