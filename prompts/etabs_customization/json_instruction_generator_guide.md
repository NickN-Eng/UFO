# JSON Instruction Generator Guide for ETABS

This guide helps you create high-quality JSON documentation files for UFO's RAG system. Use this to systematically document ETABS workflows.

---

## Quick Reference

**Target Format:**
```json
{
  "request": "How to [accomplish task]?",
  "guidance": [
    "Step 1: Action to take",
    "Step 2: Next action",
    "..."
  ]
}
```

**Detail Level:** Enough for someone who knows ETABS basics but needs guidance on the specific workflow.

**How Many:** Start with 10 core tasks, then expand incrementally.

---

## Prompt Template for AI-Assisted Generation

Use this prompt with Claude, GPT-4, or similar to generate JSON documentation:

```
I need to create JSON documentation for UFO (UI-Focused Agent) to automate ETABS tasks.

TASK: [Describe the ETABS task you want to document]

FORMAT REQUIREMENTS:
{
  "request": "Natural language description of what the user wants to accomplish",
  "guidance": [
    "List of step-by-step instructions",
    "Each step should be one clear action",
    "Include menu paths, dialog names, and button labels"
  ]
}

DETAIL LEVEL GUIDELINES:
- Include exact menu names (e.g., "Define" menu, not just "menu")
- Specify dialog names when they appear (e.g., "Define Materials dialog")
- Name specific buttons (e.g., "OK", "Add New Material", "Cancel")
- Mention field names for data entry (e.g., "Material Name field")
- Include intermediate steps like waiting for dialogs to appear
- Assume user knows ETABS basics but needs this specific workflow

EXAMPLE FOR REFERENCE:
{
  "request": "How to define a new concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "Select 'Materials' from the dropdown menu",
    "Click the 'Add New Material' button in the Materials dialog",
    "Select 'Concrete' from the Material Type dropdown",
    "Enter a name for the material in the Material Name field",
    "Enter the compressive strength fc value",
    "Click 'OK' to save the material",
    "Click 'OK' again to close the Materials dialog"
  ]
}

TASK DESCRIPTION:
[Your specific ETABS task here - be as detailed as needed about what you want to accomplish]

Please generate the JSON documentation following these requirements.
```

---

## How to Create Multiple Instructions Efficiently

### Method 1: Batch Generation with AI

Create a list of tasks first, then generate documentation for each:

```
I need to create JSON documentation for 10 ETABS tasks. I'll provide the task list, and for each task, generate JSON documentation following this format:

{
  "request": "Natural language description",
  "guidance": ["step-by-step instructions"]
}

TASKS TO DOCUMENT:
1. Create a new ETABS model
2. Define a concrete material
3. Define a steel material
4. Create a rectangular column section
5. Create a beam section
6. Define grid system
7. Draw frame elements (columns and beams)
8. Define load cases
9. Assign loads to structural elements
10. Run structural analysis

For each task, provide:
- Clear request description
- Detailed step-by-step guidance
- Exact menu paths and button names
- Dialog names when they appear

Start with Task 1.
```

Then iterate through each task, or ask the AI to generate all at once if the tasks are simple enough.

### Method 2: Manual Documentation Workflow

**Step-by-step process:**

1. **Open ETABS** and prepare to perform the task
2. **Open a text editor** (VSCode, Notepad++, etc.) with a JSON template
3. **Perform the task** while taking notes:
   - Every menu you click
   - Every dialog that opens
   - Every button you press
   - Every field you fill in
4. **Write down the steps** immediately after (memory is fresh)
5. **Convert to JSON** using the template
6. **Validate JSON syntax** (VSCode will highlight errors)
7. **Save with descriptive name** (e.g., `02_define_concrete_material.json`)

**Template to copy:**
```json
{
  "request": "",
  "guidance": [
    "",
    "",
    ""
  ]
}
```

### Method 3: Hybrid Approach (Recommended)

1. **Perform the task manually** and take rough notes
2. **Use AI to convert notes to JSON** with the prompt template
3. **Verify accuracy** against the actual ETABS workflow
4. **Refine and save**

Example:
```
My rough notes from performing the task:
- Clicked Define menu
- Selected Materials
- Clicked Add button
- Chose Concrete from dropdown
- Typed material name "C4000"
- Entered fc = 4000 psi
- Clicked OK twice

Convert these to properly formatted JSON documentation following the format:
{
  "request": "Natural language description",
  "guidance": ["step-by-step instructions"]
}

Make the guidance more detailed and explicit.
```

---

## Detail Level Guidelines

### ✅ GOOD: Sufficient Detail

```json
{
  "request": "How to define a concrete column section?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "Hover over 'Frame Sections' and select 'Add Rectangular...'",
    "In the Rectangular Section dialog, select 'Concrete' from the Material dropdown",
    "Enter section name in the Section Name field (e.g., 'C24x24')",
    "Enter depth = 24 inches in the Depth field",
    "Enter width = 24 inches in the Width field",
    "Click the 'Reinforcement' tab",
    "Set cover distance = 1.5 inches",
    "Configure longitudinal rebar as needed",
    "Click 'OK' to save the section"
  ]
}
```

**Why this is good:**
- Specifies exact menu path ("Define" → "Frame Sections" → "Add Rectangular...")
- Names dialogs ("Rectangular Section dialog")
- Identifies dropdowns and fields
- Provides example values
- Includes all steps to completion

### ❌ TOO VAGUE: Insufficient Detail

```json
{
  "request": "How to define a concrete column section?",
  "guidance": [
    "Go to frame sections",
    "Add a new section",
    "Set the properties",
    "Save it"
  ]
}
```

**Why this is bad:**
- No menu paths
- No dialog names
- No field names
- No specific actions
- UFO won't know what to click

### ❌ TOO DETAILED: Over-Specified

```json
{
  "request": "How to define a concrete column section?",
  "guidance": [
    "Move mouse cursor to the top of the screen",
    "Look for the menu bar containing File, Edit, View, Define, Draw, Select, Assign, Analyze, Design, Display, Options, Help",
    "Click on the word 'Define' which is the fourth menu item from the left",
    "A dropdown menu will appear with approximately 20 options",
    "Move the mouse cursor down to 'Frame Sections' option",
    "...and 20 more micro-steps..."
  ]
}
```

**Why this is too much:**
- Unnecessary mouse movement details
- Over-description of UI layout
- Too granular for UFO's capabilities
- Makes documentation hard to maintain

### ✅ IDEAL BALANCE

**Rule of thumb:**
- Include: Menu names, dialog names, button labels, field names
- Exclude: Pixel coordinates, mouse movements, UI layout descriptions
- Think: "What would I tell a junior engineer who knows ETABS but hasn't done this task?"

---

## How Many Instructions to Create

### Starter Set (Week 1): 10 Core Tasks

**Modeling (5 tasks):**
1. Create a new ETABS model
2. Define grid system
3. Define story levels
4. Define materials (concrete and steel)
5. Define frame sections (beams and columns)

**Analysis (5 tasks):**
6. Draw frame elements
7. Define load cases
8. Assign loads to elements
9. Run analysis
10. View analysis results

**Time estimate:** 2-4 hours for all 10 (15-25 minutes per task)

### Expansion Set (Week 2-3): +10 Design Tasks

11. Define load combinations
12. Run concrete frame design
13. Run steel frame design
14. View design forces
15. View design ratios
16. Generate design reports
17. Check code compliance
18. Modify design preferences
19. Override design parameters
20. Export results to Excel

### Advanced Set (Month 2+): +20-30 Specialized Tasks

- Area elements (slabs, walls, shells)
- Advanced analysis (nonlinear, staged construction)
- Import/Export (CAD, other formats)
- Advanced modeling features
- Results visualization and interpretation
- Customization and automation

---

## Batch Creation Template

Use this template to create multiple JSON files at once:

### Template File: `batch_template.txt`

```
TASK 1: Create a new ETABS model
Request: How to create a new ETABS model?
Steps:
- Click File menu
- Select New Model
- Choose model template (Grid Only, Beam, etc.)
- Set grid spacing and number of lines
- Click OK

---

TASK 2: Define a concrete material
Request: How to define a new concrete material in ETABS?
Steps:
- Click Define menu
- Select Materials
- Click Add New Material button
- Select Concrete from Material Type dropdown
- Enter material name
- Enter compressive strength (fc)
- Click OK to save
- Click OK to close dialog

---

TASK 3: [Your next task]
Request: [Your request]
Steps:
- [Your steps]

---
```

Then use this prompt with AI:

```
Convert each task in this batch template to proper JSON format.
Each task should become a separate JSON object following this structure:

{
  "request": "Natural language description",
  "guidance": ["step 1", "step 2", ...]
}

Make the guidance steps clear and detailed with exact menu names, dialog names, and button labels.

Here's my batch template:
[Paste your batch_template.txt content here]

Please generate JSON for each task separately, labeled Task 1, Task 2, etc.
```

---

## Quality Checklist

Before saving each JSON file, verify:

- [ ] **Request is clear**: Describes what the user wants to accomplish
- [ ] **Request is searchable**: Uses natural language that matches how users would ask
- [ ] **Steps are ordered**: Sequential from start to finish
- [ ] **Menus are named**: Exact menu text (e.g., "Define" not "definitions menu")
- [ ] **Dialogs are named**: When a dialog opens, mention its name
- [ ] **Buttons are specified**: Exact button text (e.g., "OK", "Apply", "Cancel")
- [ ] **Fields are identified**: Name the input fields when entering data
- [ ] **Complete workflow**: Goes from start to end, not just partial steps
- [ ] **JSON is valid**: No syntax errors (use a validator)
- [ ] **File is named descriptively**: e.g., `02_define_concrete_material.json`

---

## Example: Complete Documentation Process

### Step 1: Identify the Task
**Task:** Define a rectangular beam section in ETABS

### Step 2: Perform and Document
Open ETABS and perform the task while taking notes:

**Raw notes:**
```
1. Clicked Define
2. Hovered over Frame Sections → clicked Add Rectangular
3. Dialog "Rectangular Section" opened
4. Selected Steel from Material dropdown
5. Typed "W18x50" in Section Name
6. Entered depth = 18 in
7. Entered width = 7.5 in
8. Clicked OK
```

### Step 3: Convert to JSON

```json
{
  "request": "How to define a rectangular beam section in ETABS?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "Hover over 'Frame Sections' and select 'Add Rectangular...'",
    "In the Rectangular Section dialog, select material from the Material dropdown (e.g., Steel)",
    "Enter section name in the Section Name field (e.g., 'W18x50')",
    "Enter the depth dimension in the Depth field (e.g., 18 inches)",
    "Enter the width dimension in the Width field (e.g., 7.5 inches)",
    "Review other properties as needed",
    "Click 'OK' to save the section definition"
  ]
}
```

### Step 4: Validate and Save
- ✅ JSON syntax valid
- ✅ All steps present
- ✅ Clear menu paths
- ✅ Dialog named
- ✅ Fields specified

**Save as:** `05_define_beam_section.json`

---

## Common Patterns in ETABS

Recognize these common patterns to speed up documentation:

### Pattern 1: Define Menu Items
```
Define → [Category] → [Action]
- Dialog opens
- Configure properties
- Click OK
```

### Pattern 2: Assign Properties
```
Select elements
→ Assign → [Property Type]
→ Select from list or define new
→ Click OK
```

### Pattern 3: Run Analysis/Design
```
Analyze/Design → [Options]
→ Configure settings
→ Run
→ Wait for completion
→ Review results
```

### Pattern 4: View Results
```
Display → [Result Type]
→ Select load case/combination
→ Adjust display options
→ View in model window
```

---

## File Organization

Organize your JSON files for easy management:

```
C:\ETABS_UFO_Docs\
├── 01_create_new_model.json
├── 02_define_concrete_material.json
├── 03_define_steel_material.json
├── 04_define_column_section.json
├── 05_define_beam_section.json
├── 06_define_grid_system.json
├── 07_draw_frame_elements.json
├── 08_define_load_cases.json
├── 09_assign_loads.json
└── 10_run_analysis.json
```

**Naming convention:** `[number]_[short_description].json`
- Number: For ordering (01, 02, ..., 10, 11, ...)
- Description: Lowercase with underscores
- Extension: `.json`

---

## Testing Your Documentation

After creating JSON files, test them:

### 1. JSON Validation
```powershell
# In PowerShell
Get-Content .\01_create_new_model.json | ConvertFrom-Json
# Should not show errors
```

### 2. Manual Verification
- Open ETABS
- Follow your documentation steps manually
- Verify every menu, dialog, and button exists
- Note any discrepancies

### 3. UFO Testing
```powershell
# Create index
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# Test with UFO
python -m ufo -r "create a new ETABS model"
```

### 4. Refinement
- Review UFO logs in `ufo/logs/`
- Check screenshots for each step
- Update documentation if UFO struggled
- Re-index after changes

---

## Tips for High-Quality Documentation

### ✅ DO:
- Use exact text from ETABS UI
- Include dialog names
- Mention when dialogs open
- Provide example values (e.g., "24 inches")
- Test instructions manually before finalizing
- Keep steps atomic (one action per step)
- Use consistent terminology
- Mention data units when relevant

### ❌ DON'T:
- Use vague terms ("click the button" - which button?)
- Skip intermediate steps
- Assume implicit knowledge (be explicit)
- Use coordinates or pixel positions
- Over-complicate with unnecessary detail
- Mix multiple tasks in one file
- Forget to save frequently

---

## Advanced: Context-Aware Documentation

For more sophisticated documentation, include contextual hints:

```json
{
  "request": "How to assign a distributed load to a beam?",
  "guidance": [
    "Before starting, ensure the beam element is already drawn in the model",
    "Click on the 'Select' menu and choose 'Select' → 'Frames' to enable frame selection",
    "Click on the beam element you want to assign the load to (it should highlight)",
    "Click on the 'Assign' menu in the top menu bar",
    "Hover over 'Frame Loads' and select 'Distributed'",
    "In the Frame Distributed Loads dialog, select the load case from the 'Load Case Name' dropdown",
    "Set the load type to 'Forces' or 'Moments' as needed",
    "Choose 'Gravity' or 'Projected' for load direction",
    "Enter the load magnitude in the 'Load' field (e.g., 2 kip/ft)",
    "Set the direction (typically 'Gravity' or '-Z' for downward loads)",
    "Review the distribution (uniform by default)",
    "Click 'OK' to apply the load",
    "The load should now appear on the selected beam in the model view"
  ]
}
```

**Notice:**
- Prerequisites mentioned upfront
- Element selection explained
- Dropdown options named
- Example values provided
- Expected result at the end

---

## Quick Start Command Summary

```powershell
# 1. Create documentation directory
mkdir C:\ETABS_UFO_Docs
cd C:\ETABS_UFO_Docs

# 2. Create your JSON files (manually or with AI)
# Save as: 01_task_name.json, 02_task_name.json, etc.

# 3. Validate JSON syntax
Get-Content .\01_create_new_model.json | ConvertFrom-Json

# 4. Create FAISS index
cd C:\Users\nniem\source\repos\UFO
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# 5. Enable RAG in config
# Edit ufo/config/config.yaml: Set RAG_OFFLINE_DOCS: True

# 6. Test with UFO
python -m ufo -r "create a new ETABS model"

# 7. Review logs and refine
# Check ufo/logs/ for results, update JSON files as needed

# 8. Re-index after changes
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

---

## Summary

**To generate JSON instructions:**
1. Use the AI prompt template provided (or manual workflow)
2. Start with 10 core tasks
3. Aim for "sufficient detail" (menu names, dialog names, button labels, field names)
4. Test each instruction manually in ETABS
5. Validate JSON syntax
6. Create FAISS index with learner tool
7. Test with UFO and iterate

**Key principle:** Documentation should be detailed enough for UFO to follow, but not so detailed that it becomes unmaintainable or brittle to UI changes.

**Time investment:** 15-25 minutes per task × 10 tasks = 2-4 hours for initial set

**Result:** UFO will be able to autonomously perform these ETABS tasks based on your documentation.
