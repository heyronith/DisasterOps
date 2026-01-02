# Knowledge Base Organization Summary

**Date:** December 2024  
**Source:** `/Data/` folder  
**Destination:** `/data/raw/` (organized structure)

---

## Directory Structure

```
data/
├── raw/                          # Original PDFs as downloaded
│   ├── ics_forms/               # 21 files
│   ├── cert/                    # 1 file
│   ├── ready_gov/               # 7 files
│   └── fema_other/              # 4 PDFs + 3 IS course directories
├── processed/                   # (Reserved for cleaned, structured versions)
└── metadata/                    # (Reserved for citation IDs, document metadata)
```

---

## File Inventory

### ICS Forms (21 files)
Located in: `data/raw/ics_forms/`

**Core ICS Forms:**
- ✅ `ics_form_201_incident_briefing_v3.pdf`
- ✅ `ics_form_202_incident_objectives_v3.1.pdf`
- ✅ `ics_form_203_organization_assignment_list_v3.pdf`
- ✅ `ics_form_204_assignment_list_v3.1.pdf`
- ✅ `ics_form_205_incident_radio_communications_plan_v3.1.pdf`
- ✅ `ics_form_205a_communications_list_v3.pdf`
- ✅ `ics_form_206_medical_plan_v3.pdf`
- ✅ `ics_form_207_incident_organization_chart_v3.pdf`
- ✅ `ics_form_208_safety_message-plan_v3.1.pdf`
- ✅ `ics_form_209_incident_status_summary_v3.pdf`
- ✅ `ics_form_210_resource_status_change_v3.pdf`
- ✅ `ics_form_211_incident_check-in_list_v3.1.pdf`
- ✅ `ics_form_213_general_message_v3.pdf`
- ✅ `ics_form_214_activity_log_v3.1.pdf`
- ✅ `ics_form_215_operational_planning_worksheet_v3.pdf`
- ✅ `ics_form_215a_incident_action_plan_safety_analysis_v3.pdf`
- ✅ `ics_form_218_support_vehicle-equipment_inventory_v3.pdf`
- ✅ `ics_form_220_air_operations_summary_v3.pdf`
- ✅ `ics_form_221_demobilization_check-out_v3.1.pdf`

**Reference Materials:**
- ✅ `nims_ics_forms_booklet.v3.pdf` (Complete ICS forms booklet with instructions)
- ✅ `ics_training_reference_guide.pdf` (Comprehensive ICS training reference)

**Missing Forms:** ICS-212 (not typically used in standard operations)

---

### CERT Materials (1 file)
Located in: `data/raw/cert/`

- ✅ `cert_basic_training_manual.pdf`
  - **Original filename:** "Cert Brasic Training Manuak.pdf"
  - **Fixed:** Typo corrected (Brasic → Basic, Manuak → Manual)

---

### Ready.gov Guides (7 files)
Located in: `data/raw/ready_gov/`

**Core Preparedness Guides:**
- ✅ `are-you-ready-guide.pdf` (Comprehensive citizen preparedness guide)
- ✅ `ready-gov_caregivers-preparedness-guide.pdf`

**Disaster-Specific Guides:**
- ✅ `earthquake_hazard_guide.pdf`
- ✅ `floood_guide.pdf` (Note: original filename had typo "Floood")
- ✅ `hurricane_guide.pdf`
- ✅ `tornado_guide.pdf` (Fixed: was "tornadao guide.pdf", moved from fema_other)
- ✅ `wildfire_guide.pdf`

---

### FEMA Other Resources (4 PDFs + 3 IS Course Directories)
Located in: `data/raw/fema_other/`

**NIMS Documents:**
- ✅ `nims_doctrine.pdf`
- ✅ `nims-guideline-resource-management-preparedness.pdf`
- ✅ `nims-incident-complexity-guide.pdf`

**National Response Framework:**
- ✅ `nrf_finalapproved_2011028.pdf`

**FEMA Independent Study (IS) Courses:**
- ✅ `is-0100c_complete-course/` (IS-100: Introduction to ICS)
  - Student Manual (SM)
  - Instructor Guide (IG)
  - Visuals (PowerPoint)
  - Handouts
- ✅ `is-200c-complete-course/` (IS-200: ICS for Single Resources)
  - Student Manual (SM)
  - Instructor Guide (IG)
  - Visuals (PowerPoint)
  - Handouts
- ✅ `is-700b_complete/` (IS-700: NIMS Introduction)
  - Student Manual (SM)
  - Instructor Guide (IG)
  - Visuals (PowerPoint)
  - Handouts

---

## Total Count

- **PDF Files:** 49 total
  - ICS Forms: 21
  - CERT: 1
  - Ready.gov: 7
  - FEMA Other (PDFs): 4
  - FEMA IS Courses (PDFs within directories): 16+ (includes student manuals, instructor guides, handouts)
- **Total Directories:** 4 main categories + 3 IS course directories

---

## Filename Normalizations Applied

1. **ICS Forms:** Normalized to lowercase with underscores, removed parentheses and commas
   - Example: `ics form 201, incident briefing (v3).pdf` → `ics_form_201_incident_briefing_v3.pdf`

2. **CERT Manual:** Fixed typos in original filename
   - `Cert Brasic Training Manuak.pdf` → `cert_basic_training_manual.pdf`

3. **Ready.gov Guides:** Standardized to lowercase with underscores
   - Example: `Wildfire Guide.pdf` → `wildfire_guide.pdf`

4. **Tornado Guide:** Fixed typo and moved to correct category
   - `tornadao guide.pdf` (was in fema_other) → `tornado_guide.pdf` (moved to ready_gov)

---

## Next Steps

1. ✅ **Step 1 Complete:** Knowledge base downloaded and organized
2. ⏭️ **Step 2:** Extract text from PDFs (using pdfplumber, PyPDF2, or pdfminer)
3. ⏭️ **Step 3:** Structure documents (identify sections, headers, page breaks)
4. ⏭️ **Step 4:** Build citation index (map text chunks → source documents)
5. ⏭️ **Step 5:** Prepare for chunking (Step 2: RAG Pipeline)

---

## Notes

- All original files have been moved from `/Data/` to `/data/raw/`
- Directory structure follows the specification in `STEP1_KNOWLEDGE_BASE_GUIDE.md`
- Filenames have been normalized for consistency
- The `/data/processed/` and `/data/metadata/` directories are ready for Step 2

