# Multiple Instructions Format Guide

This guide explains the different ways to organize multiple ETABS instructions for UFO's RAG system.

---

## Quick Answer

**Current UFO JSON Loader:** One instruction per file (recommended)

**Multiple Instructions:** Create separate `.json` files, all in the same folder

**Indexing:** Point the learner tool to the folder containing all files

---

## Approach 1: One Instruction Per File (Recommended)

This is the **standard approach** that works out-of-the-box with UFO.

### File Structure

```
C:\ETABS_UFO_Docs\
├── 01_create_new_model.json
├── 02_define_concrete_material.json
├── 03_define_steel_material.json
├── 04_define_column_section.json
├── 05_define_beam_section.json
└── ...
```

### Each File Contains ONE Task

**File: `01_create_new_model.json`**
```json
{
  "request": "How to create a new ETABS model?",
  "guidance": [
    "Click on the 'File' menu in the top menu bar",
    "Select 'New Model' from the dropdown",
    "Choose the model template (e.g., Grid Only)",
    "Click 'OK' to create the model"
  ]
}
```

**File: `02_define_concrete_material.json`**
```json
{
  "request": "How to define a concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu",
    "Select 'Materials'",
    "Click 'Add New Material'",
    "Select 'Concrete' from dropdown",
    "Enter material properties",
    "Click 'OK' to save"
  ]
}
```

### Indexing Multiple Files

```powershell
# Point to the folder containing ALL your JSON files
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

**What happens:**
- Learner scans the entire `C:\ETABS_UFO_Docs` folder
- Finds all `.json` files (including subfolders)
- Loads each file as a separate document
- Creates a single FAISS index containing all instructions
- UFO can retrieve any of these instructions at runtime

### Advantages
✅ Easy to manage individual files
✅ Easy to add/remove specific instructions
✅ Clear organization with descriptive filenames
✅ Works out-of-the-box (no code modifications)
✅ Easy to version control (git tracks individual files)
✅ Can organize into subfolders by category

### Example with Subfolders

```
C:\ETABS_UFO_Docs\
├── modeling\
│   ├── 01_create_model.json
│   ├── 02_define_materials.json
│   └── 03_define_sections.json
├── analysis\
│   ├── 10_define_loads.json
│   ├── 11_run_analysis.json
│   └── 12_view_results.json
└── design\
    ├── 20_run_concrete_design.json
    └── 21_run_steel_design.json
```

Indexer will find all JSON files recursively:
```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

---

## Approach 2: Multiple Instructions in One File (Array Format)

If you want to put multiple instructions in a single JSON file, you need to use an **array structure**.

### Array Format

**File: `etabs_instructions.json`**
```json
[
  {
    "request": "How to create a new ETABS model?",
    "guidance": [
      "Click on the 'File' menu",
      "Select 'New Model'",
      "Choose template",
      "Click 'OK'"
    ]
  },
  {
    "request": "How to define a concrete material?",
    "guidance": [
      "Click on the 'Define' menu",
      "Select 'Materials'",
      "Click 'Add New Material'",
      "Select 'Concrete'",
      "Enter properties",
      "Click 'OK'"
    ]
  },
  {
    "request": "How to define a column section?",
    "guidance": [
      "Click on the 'Define' menu",
      "Select 'Frame Sections' → 'Add Rectangular'",
      "Enter section name",
      "Set dimensions",
      "Click 'OK'"
    ]
  }
]
```

### ⚠️ Important: Requires Custom Loader

The **current UFO JSON loader does not support array format**. You would need to create a custom loader.

### Custom Loader for Array Format

**File: `learner/etabs_array_loader.py`**
```python
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
from typing import Dict, List
from langchain.docstore.document import Document
from . import basic


class ETABSArrayLoader(basic.BasicDocumentLoader):
    """
    JSON loader that supports array format with multiple instructions per file.
    """

    def __init__(self, directory: str = None):
        super().__init__()
        self.extensions = ".json"
        self.directory = directory

    @staticmethod
    def load_json_document(file: str) -> List[Dict]:
        """
        Load JSON document(s) from file.
        Supports both single object and array of objects.
        """
        with open(file, "r") as f:
            try:
                data = json.load(f)
                # If it's a single object, wrap in list
                if isinstance(data, dict):
                    return [data]
                # If it's already a list, return as-is
                elif isinstance(data, list):
                    return data
                else:
                    return []
            except json.JSONDecodeError:
                return []

    def construct_document(self):
        """
        Construct langchain documents from JSON files.
        Each request-guidance pair becomes a separate document.
        """
        documents = []

        for file in self.load_file_name():
            # Load file (may contain single object or array)
            items = self.load_json_document(file)

            # Process each item
            for item in items:
                request = item.get("request", "")
                guidance_steps = item.get("guidance", [])
                guidance = "\n".join([step for step in guidance_steps if step])

                metadata = {
                    "title": request,
                    "summary": request,
                    "text": guidance,
                    "source_file": file
                }

                doc = Document(page_content=request, metadata=metadata)
                documents.append(doc)

        return documents
```

### Register Custom Loader

**File: `learner/indexer.py`** (modify line ~18-21)
```python
from learner import etabs_array_loader  # Add this import

_doc_loader_mapper = {
    "xml": xml_loader.XMLLoader,
    "json": json_loader.JsonLoader,
    "etabs_array": etabs_array_loader.ETABSArrayLoader,  # Add this line
}
```

### Use Custom Loader

```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format etabs_array
```

### Advantages of Array Format
✅ All instructions in one place
✅ Easier to review all at once
✅ Simpler file management (fewer files)

### Disadvantages
❌ Requires custom loader code
❌ Harder to manage individual instructions
❌ Harder to track changes in version control
❌ One syntax error breaks all instructions
❌ Harder to organize by category

---

## Approach 3: Hybrid - Grouped by Category

A practical middle ground: **one file per category** with multiple related instructions.

### File Structure

```
C:\ETABS_UFO_Docs\
├── materials.json          (all material-related tasks)
├── sections.json           (all section-related tasks)
├── loads.json              (all load-related tasks)
└── analysis.json           (all analysis tasks)
```

### Example: Materials File

**File: `materials.json`**
```json
[
  {
    "request": "How to define a new concrete material in ETABS?",
    "guidance": [
      "Click on the 'Define' menu",
      "Select 'Materials'",
      "Click 'Add New Material'",
      "Select 'Concrete' from Material Type dropdown",
      "Enter material name",
      "Enter compressive strength fc",
      "Click 'OK' to save",
      "Click 'OK' to close dialog"
    ]
  },
  {
    "request": "How to modify an existing material in ETABS?",
    "guidance": [
      "Click on the 'Define' menu",
      "Select 'Materials'",
      "Select the material from the list",
      "Click 'Modify/Show Material'",
      "Edit the properties as needed",
      "Click 'OK' to save changes",
      "Click 'OK' to close dialog"
    ]
  },
  {
    "request": "How to delete a material in ETABS?",
    "guidance": [
      "Click on the 'Define' menu",
      "Select 'Materials'",
      "Select the material to delete from the list",
      "Click 'Delete Material' button",
      "Confirm deletion if prompted",
      "Click 'OK' to close dialog"
    ]
  }
]
```

**Requires:** Custom array loader (see Approach 2)

---

## Comparison Table

| Aspect | One File Per Task | Array Format | Grouped by Category |
|--------|------------------|--------------|---------------------|
| **Setup** | ✅ No code changes | ❌ Custom loader needed | ❌ Custom loader needed |
| **File Management** | Many files | One file | Few files |
| **Organization** | ✅ Very clear | ⚠️ Can get cluttered | ✅ Good balance |
| **Version Control** | ✅ Easy to track | ❌ Hard to see individual changes | ⚠️ Medium |
| **Error Impact** | Isolated per file | All instructions fail | Category fails |
| **Updates** | ✅ Edit one file | Edit large file | Edit medium file |
| **Recommended For** | Most users | Small datasets | Medium datasets |

---

## Recommended Workflow

### For Most Users (10-50 instructions)
**Use Approach 1: One file per task**

```
C:\ETABS_UFO_Docs\
├── 01_create_model.json
├── 02_define_concrete.json
├── 03_define_steel.json
└── ...
```

**Why:** Works out-of-the-box, easy to manage, clear organization.

### For Larger Projects (50+ instructions)
**Use Approach 1 with subfolders**

```
C:\ETABS_UFO_Docs\
├── 01_modeling\
│   ├── 01_create_model.json
│   ├── 02_materials.json
│   └── 03_sections.json
├── 02_analysis\
│   ├── 10_loads.json
│   └── 11_run_analysis.json
└── 03_design\
    └── 20_concrete_design.json
```

**Why:** Still uses standard loader, but organized by category.

### For Advanced Users
**Use Approach 3: Grouped array files with custom loader**

Only if you have specific requirements that make array format better for your workflow.

---

## Indexing Examples

### Example 1: All Files in One Folder

```powershell
# Structure:
# C:\ETABS_UFO_Docs\
# ├── 01_task.json
# ├── 02_task.json
# └── 03_task.json

python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

Result: All 3 tasks indexed

### Example 2: Files in Subfolders

```powershell
# Structure:
# C:\ETABS_UFO_Docs\
# ├── modeling\01_task.json
# ├── modeling\02_task.json
# └── analysis\10_task.json

python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

Result: All 3 tasks indexed (recursive search)

### Example 3: Incremental Additions

```powershell
# Initial indexing
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# Later, add more files to the folder
# Then re-index with --incremental flag
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json --incremental
```

Result: New files added to existing index

### Example 4: Array Format (Custom Loader)

```powershell
# Structure:
# C:\ETABS_UFO_Docs\
# └── all_tasks.json  (contains array of 10 tasks)

# After creating custom loader
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format etabs_array
```

Result: All 10 tasks from array indexed

---

## How UFO Retrieves Instructions

Regardless of file organization, **UFO's retrieval works the same way**:

1. **User makes request:** "create a concrete material in ETABS"

2. **UFO creates embedding** of the request using sentence transformers

3. **FAISS searches** through all indexed instructions

4. **Retrieves top-k most similar** based on semantic similarity

5. **Returns best matches** regardless of which file they came from

**Key Point:** File organization is for YOUR convenience - UFO sees all instructions as one unified knowledge base.

---

## Example: Complete Workflow

### Step 1: Create Instructions (One Per File)

**File: `01_create_model.json`**
```json
{
  "request": "How to create a new ETABS model?",
  "guidance": ["..."]
}
```

**File: `02_define_material.json`**
```json
{
  "request": "How to define a concrete material?",
  "guidance": ["..."]
}
```

**File: `03_define_section.json`**
```json
{
  "request": "How to define a column section?",
  "guidance": ["..."]
}
```

### Step 2: Index All Files

```powershell
cd C:\Users\nniem\source\repos\UFO
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

**Output:**
```
Processing C:\ETABS_UFO_Docs\01_create_model.json...
Processing C:\ETABS_UFO_Docs\02_define_material.json...
Processing C:\ETABS_UFO_Docs\03_define_section.json...
Creating embeddings...
Building FAISS index...
Saved to vectordb/docs/ETABS/
```

### Step 3: UFO Uses All Instructions

```powershell
python -m ufo -r "define a concrete material in ETABS"
```

**What happens:**
- UFO searches ALL 3 instructions (and any others you've added)
- Finds `02_define_material.json` is most relevant
- Uses that guidance to perform the task

---

## Best Practices

### ✅ DO:
- Start with one file per task (standard approach)
- Use descriptive filenames: `02_define_concrete_material.json`
- Organize into subfolders by category if you have many tasks
- Number files for logical ordering (01, 02, 03...)
- Keep each instruction focused on ONE task

### ❌ DON'T:
- Mix multiple unrelated tasks in one file
- Use array format unless you have a specific reason
- Create overly complex folder hierarchies
- Forget to re-index after adding new files

---

## FAQ

**Q: Can I have 100 separate JSON files?**
A: Yes! The indexer will process them all and create one unified index.

**Q: Do I need to merge files before indexing?**
A: No. Keep them separate. The indexer handles multiple files automatically.

**Q: What if I want to add more instructions later?**
A: Just add new JSON files and re-index with `--incremental` flag.

**Q: Can I mix both formats (single and array)?**
A: Not with the standard loader. Stick to one approach for consistency.

**Q: Which format does UFO recommend?**
A: One instruction per file (Approach 1) - it's the standard and works out-of-the-box.

---

## Summary

**Standard Approach (Recommended):**
- One instruction per JSON file
- Multiple files in same folder
- Index the folder containing all files
- No code modifications needed

**Command:**
```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

**Result:**
- All instructions indexed into single FAISS database
- UFO can retrieve any instruction based on semantic similarity
- Easy to manage and maintain

**Bottom Line:** Create separate JSON files for each task, put them all in one folder, and point the indexer to that folder. UFO will handle the rest!
