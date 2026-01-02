# Step 1 PDF Processing Pipeline

## Setup

```bash
# Install dependencies
pip install -r requirements_step1.txt

# Or if using conda/virtualenv:
# pip install pdfplumber pandas jupyter
```

## Run the Pipeline

1. Open Jupyter notebook:
```bash
jupyter notebook step1_process_pdfs.ipynb
```

2. Run all cells (Cell → Run All)

The notebook will:
- Extract text from all PDFs in `Data/raw/`
- Identify document structure (sections, headers, pages)
- Generate citation IDs (format: `{source}_{doc_type}_{section}_{page}`)
- Save processed versions to `Data/processed/`
- Create citation index and metadata in `Data/metadata/`

## Output Structure

After processing, you'll have:

```
Data/
├── processed/          # JSON files with extracted text and structure
├── metadata/           # Citation index and document metadata
│   ├── citation_index.json       # Master citation lookup
│   └── processing_summary.json   # Statistics
```

## Citation Schema

Citations follow the format: `{source}_{doc_type}_{section}_{page}`

Examples:
- `fema_ics201_section1_p1`
- `cert_basic_training_manual_section2_p15`
- `ready_gov_are_you_ready_section3_p8`

## Next Steps

After processing completes, you're ready for **Step 2: RAG Pipeline** (chunking + embeddings)

