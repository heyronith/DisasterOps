"""
Organize downloaded knowledge base files into proper directory structure
"""

import os
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SOURCE_DIR = BASE_DIR / "Data"
TARGET_DIR = BASE_DIR / "data"

# Create directory structure
RAW_DIR = TARGET_DIR / "raw"
ICS_FORMS_DIR = RAW_DIR / "ics_forms"
CERT_DIR = RAW_DIR / "cert"
READY_GOV_DIR = RAW_DIR / "ready_gov"
FEMA_OTHER_DIR = RAW_DIR / "fema_other"
PROCESSED_DIR = TARGET_DIR / "processed"
METADATA_DIR = TARGET_DIR / "metadata"

# Create all directories
for dir_path in [RAW_DIR, ICS_FORMS_DIR, CERT_DIR, READY_GOV_DIR, FEMA_OTHER_DIR, PROCESSED_DIR, METADATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# File categorization rules
ICS_FORMS_KEYWORDS = ["ics form", "ics_training_reference_guide", "nims ics forms booklet"]
CERT_KEYWORDS = ["cert", "Cert"]
READY_GOV_KEYWORDS = ["are-you-ready", "ready-gov", "caregivers", "tornado", "Wildfire", "Hurricane", "Floood", "Earthquake"]
FEMA_OTHER_KEYWORDS = ["nims", "NRF", "is-"]

def normalize_filename(filename: str) -> str:
    """Normalize filenames (remove special chars, standardize case)"""
    # Keep the original for now, but clean up common issues
    filename = filename.replace(" ", "_").replace(",", "").replace("(", "").replace(")", "")
    filename = filename.replace("__", "_")
    return filename

def organize_files():
    """Organize files from Data/ to data/raw/ structure"""
    
    if not SOURCE_DIR.exists():
        print(f"❌ Source directory {SOURCE_DIR} does not exist!")
        return
    
    moved_files = {
        "ics_forms": [],
        "cert": [],
        "ready_gov": [],
        "fema_other": []
    }
    
    # Process all files and directories in Data/
    for item in SOURCE_DIR.iterdir():
        item_name_lower = item.name.lower()
        
        # Skip if it's a directory we'll handle separately
        if item.is_dir() and item_name_lower.startswith("is-"):
            # Move IS course directories to fema_other
            dest = FEMA_OTHER_DIR / item.name
            print(f"📁 Moving directory: {item.name} -> {dest}")
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(item), str(dest))
            moved_files["fema_other"].append(item.name)
            continue
        
        if item.is_file():
            # Determine category
            category = None
            dest_dir = None
            
            # Check ICS Forms
            if any(keyword.lower() in item_name_lower for keyword in ICS_FORMS_KEYWORDS):
                category = "ics_forms"
                dest_dir = ICS_FORMS_DIR
                # Normalize ICS form filenames
                new_name = item.name.lower().replace(" ", "_").replace(",", "").replace("(", "").replace(")", "")
                new_name = new_name.replace("__", "_")
                dest = dest_dir / new_name
            # Check CERT
            elif any(keyword.lower() in item_name_lower for keyword in CERT_KEYWORDS):
                category = "cert"
                dest_dir = CERT_DIR
                # Fix typo in filename
                new_name = item.name.replace("Brasic", "Basic").replace("Manuak", "Manual")
                new_name = new_name.replace(" ", "_").lower()
                dest = dest_dir / new_name
            # Check Ready.gov
            elif any(keyword.lower() in item_name_lower for keyword in READY_GOV_KEYWORDS):
                category = "ready_gov"
                dest_dir = READY_GOV_DIR
                new_name = item.name.replace(" ", "_").lower()
                dest = dest_dir / new_name
            # Check FEMA Other (NIMS, NRF)
            elif any(keyword.lower() in item_name_lower for keyword in FEMA_OTHER_KEYWORDS):
                category = "fema_other"
                dest_dir = FEMA_OTHER_DIR
                new_name = item.name.replace(" ", "_").lower()
                dest = dest_dir / new_name
            else:
                print(f"⚠️  Unclassified file: {item.name} (moving to fema_other)")
                category = "fema_other"
                dest_dir = FEMA_OTHER_DIR
                new_name = item.name.replace(" ", "_").lower()
                dest = dest_dir / new_name
            
            # Move file
            if dest.exists():
                print(f"⚠️  File already exists, skipping: {dest.name}")
            else:
                print(f"📄 Moving: {item.name} -> {dest}")
                shutil.move(str(item), str(dest))
                moved_files[category].append(dest.name)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Organization Summary")
    print("="*60)
    for category, files in moved_files.items():
        print(f"\n{category.upper()}: {len(files)} files")
        for f in sorted(files)[:10]:  # Show first 10
            print(f"  ✅ {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
    
    print(f"\n✅ Files organized successfully!")
    print(f"📁 Source: {SOURCE_DIR}")
    print(f"📁 Destination: {RAW_DIR}")

if __name__ == "__main__":
    organize_files()

