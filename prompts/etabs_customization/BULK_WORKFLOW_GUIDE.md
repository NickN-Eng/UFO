# Bulk JSON Workflow - Quick Reference

This is the fastest way to create ETABS documentation for UFO. Generate everything at once, then automatically split into individual files.

---

## Complete Workflow

### Step 1: Generate Bulk JSON

Use the prompt from [bulk_json_generator_prompt.md](bulk_json_generator_prompt.md) with Claude/GPT-4.

**Expected output structure:**
```json
{
  "application": "ETABS",
  "version": "v20+",
  "instructions": [
    {
      "task_id": "01",
      "category": "modeling",
      "request": "How to create a new ETABS model?",
      "guidance": ["step 1", "step 2", "..."]
    },
    {
      "task_id": "02",
      "category": "materials",
      "request": "How to define a concrete material?",
      "guidance": ["step 1", "step 2", "..."]
    }
  ]
}
```

**Save as:** `etabs_bulk_instructions.json`

### Step 2: Split into Individual Files

```powershell
# Basic usage
python split_json_instructions.py etabs_bulk_instructions.json C:\ETABS_UFO_Docs

# With options
python split_json_instructions.py etabs_bulk_instructions.json C:\ETABS_UFO_Docs --organize
```

**Output:**
```
C:\ETABS_UFO_Docs\
├── 01_create_new_etabs_model.json
├── 02_define_concrete_material.json
├── 03_define_steel_material.json
└── ...
```

### Step 3: Create FAISS Index

```powershell
cd C:\Users\nniem\source\repos\UFO
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

### Step 4: Enable RAG in Config

Edit `ufo/config/config.yaml`:
```yaml
RAG_OFFLINE_DOCS: True
RAG_OFFLINE_DOCS_RETRIEVED_TOPK: 2
```

### Step 5: Test with UFO

```powershell
python -m ufo -r "create a new ETABS model"
```

---

## Script Options

### Basic Usage
```powershell
python split_json_instructions.py <input_file> <output_folder>
```

### With Task ID Prefix (Default)
```powershell
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs
```
**Output:** `01_create_model.json`, `02_define_material.json`

### Without Task ID Prefix
```powershell
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs --no-prefix
```
**Output:** `create_model.json`, `define_material.json`

### Organized by Category
```powershell
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs --organize
```
**Output:**
```
C:\ETABS_UFO_Docs\
├── modeling\
│   ├── 01_create_model.json
│   └── 07_draw_elements.json
├── materials\
│   ├── 02_define_concrete.json
│   └── 03_define_steel.json
└── loads\
    └── 08_define_loads.json
```

---

## Example: Complete Run

### Input File: `etabs_bulk_instructions.json`
```json
{
  "application": "ETABS",
  "version": "v20+",
  "instructions": [
    {
      "task_id": "01",
      "category": "modeling",
      "request": "How to create a new ETABS model?",
      "guidance": [
        "Click on the 'File' menu",
        "Select 'New Model'",
        "Choose template",
        "Click 'OK'"
      ]
    },
    {
      "task_id": "02",
      "category": "materials",
      "request": "How to define a concrete material in ETABS?",
      "guidance": [
        "Click on the 'Define' menu",
        "Select 'Materials'",
        "Click 'Add New Material'",
        "Select 'Concrete'",
        "Enter properties",
        "Click 'OK'"
      ]
    }
  ]
}
```

### Run Script
```powershell
PS C:\Users\nniem\source\repos\UFO> python split_json_instructions.py etabs_bulk_instructions.json C:\ETABS_UFO_Docs

Reading bulk JSON file: etabs_bulk_instructions.json
Found 2 instructions to process
Output folder: C:\ETABS_UFO_Docs
  ✓ Created: 01_create_new_etabs_model.json
  ✓ Created: 02_define_concrete_material_in_etabs.json

============================================================
SUMMARY
============================================================
Total instructions: 2
Files created: 2
Files skipped: 0
Output location: C:\ETABS_UFO_Docs

✓ Successfully created files:
  - 01_create_new_etabs_model.json
  - 02_define_concrete_material_in_etabs.json

============================================================
Next steps:
============================================================
1. Review the created files in: C:\ETABS_UFO_Docs
2. Create FAISS index:
   python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
3. Test with UFO:
   python -m ufo -r "your ETABS task here"
============================================================
```

### Output Files

**File: `C:\ETABS_UFO_Docs\01_create_new_etabs_model.json`**
```json
{
  "request": "How to create a new ETABS model?",
  "guidance": [
    "Click on the 'File' menu",
    "Select 'New Model'",
    "Choose template",
    "Click 'OK'"
  ]
}
```

**File: `C:\ETABS_UFO_Docs\02_define_concrete_material_in_etabs.json`**
```json
{
  "request": "How to define a concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu",
    "Select 'Materials'",
    "Click 'Add New Material'",
    "Select 'Concrete'",
    "Enter properties",
    "Click 'OK'"
  ]
}
```

---

## Filename Generation

The script automatically generates clean filenames from the request text:

| Request | Generated Filename |
|---------|-------------------|
| "How to create a new ETABS model?" | `01_create_new_etabs_model.json` |
| "How to define a concrete material in ETABS?" | `02_define_concrete_material_in_etabs.json` |
| "How to run structural analysis?" | `10_run_structural_analysis.json` |

**Rules:**
- Removes "How to" prefix
- Converts to lowercase
- Replaces spaces with underscores
- Removes special characters
- Prefixes with task_id (if enabled)
- Limits length to 50 characters

---

## Error Handling

### Invalid JSON Syntax
```
ERROR: Invalid JSON in file: Expecting ',' delimiter: line 10 column 5 (char 234)
```
**Solution:** Validate and fix JSON using a JSON validator

### Missing Required Fields
```
ERROR: Invalid bulk JSON structure: Instruction 3 missing required field: guidance
```
**Solution:** Ensure all instructions have task_id, request, and guidance fields

### File Already Exists
```
⚠️  SKIPPED (already exists): 01_create_new_etabs_model.json
```
**Solution:** Delete existing files or rename them if you want to regenerate

---

## Tips

### ✅ DO:
- Validate your bulk JSON before running the script
- Review the output files after splitting
- Use task_id prefix for better organization (default behavior)
- Start with 10-15 instructions, then expand

### ❌ DON'T:
- Skip validation of the bulk JSON
- Run script multiple times without checking output
- Use duplicate task_ids
- Forget to specify the output folder

---

## Validation Before Splitting

Check your bulk JSON is valid:

### PowerShell
```powershell
Get-Content etabs_bulk_instructions.json | ConvertFrom-Json
```

### Python
```python
import json
with open('etabs_bulk_instructions.json') as f:
    data = json.load(f)
    print(f"Found {len(data['instructions'])} instructions")
```

### Online Validators
- https://jsonlint.com/
- https://jsonformatter.org/

---

## Advanced: Batch Processing

Generate multiple sets of instructions:

### Bulk Set 1: Core Modeling (10 tasks)
```powershell
python split_json_instructions.py etabs_modeling.json C:\ETABS_UFO_Docs\01_modeling
```

### Bulk Set 2: Analysis (10 tasks)
```powershell
python split_json_instructions.py etabs_analysis.json C:\ETABS_UFO_Docs\02_analysis --organize
```

### Bulk Set 3: Design (10 tasks)
```powershell
python split_json_instructions.py etabs_design.json C:\ETABS_UFO_Docs\03_design --organize
```

### Index All at Once
```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

---

## Troubleshooting

### Script Not Found
```
python: can't open file 'split_json_instructions.py'
```
**Solution:** Make sure you're in the UFO root directory where the script is located

### Permission Denied
```
PermissionError: [Errno 13] Permission denied: 'C:\ETABS_UFO_Docs\01_create_model.json'
```
**Solution:** Close any programs that might have the file open, or run PowerShell as Administrator

### Empty Output Folder
```
Files created: 0
```
**Solution:** Check that your bulk JSON has the correct structure with "instructions" array

---

## Summary

**Workflow:**
1. ✍️ Use AI prompt → Generate bulk JSON
2. ✂️ Run split script → Create individual files
3. 📚 Run learner → Create FAISS index
4. ⚙️ Enable RAG → Edit config.yaml
5. 🚀 Test UFO → Verify it works

**Time Savings:**
- Without script: ~20 minutes to create 10 files manually
- With script: ~5 minutes (generate bulk + split)
- **Savings: 75% faster!**

**Command Summary:**
```powershell
# Split
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs

# Index
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# Test
python -m ufo -r "create a new ETABS model"
```

Done! 🎉
