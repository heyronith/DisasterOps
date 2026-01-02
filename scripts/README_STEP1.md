# Step 1 Quick Start

## Setup

```bash
# Install dependencies
pip install -r requirements_step1.txt

# Create directory structure
mkdir -p data/raw/{ics_forms,cert,ready_gov,fema_other}
mkdir -p data/processed
mkdir -p data/metadata
```

## Download Core Documents

```bash
# Download priority 1 documents (ICS forms + Ready.gov basics)
python scripts/download_knowledge_base.py --phase core

# Download expanded set (includes priority 2)
python scripts/download_knowledge_base.py --phase expanded

# Download everything
python scripts/download_knowledge_base.py --phase all
```

## Manual Downloads Needed

Some documents (especially CERT manuals) may require manual navigation:

```bash
# See which documents need manual download
python scripts/download_knowledge_base.py --show-manual
```

## Verify Downloads

Check `data/raw/` directory:
- `ics_forms/` - ICS forms PDFs
- `ready_gov/` - Ready.gov guides
- `cert/` - CERT materials (after manual download)
- `fema_other/` - Other FEMA resources

Metadata is saved to `data/metadata/` as JSON files.

## Next Steps

After downloading documents:
1. Manually download CERT Participant Manual
2. Verify all PDFs open correctly
3. Move to Step 2: RAG Pipeline (chunking + embeddings)


