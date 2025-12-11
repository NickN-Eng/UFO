# UFO RAG Customization Plan - ETABS Implementation Guide

## Research Summary

### RAG Architecture in UFO

UFO implements a multi-source RAG (Retrieval-Augmented Generation) system with **4 distinct knowledge sources**:

1. **Offline Help Documents** - Static, pre-indexed documentation
2. **Online Bing Search** - Real-time web search
3. **Self-Experience Learning** - Automatic learning from successful tasks
4. **User Demonstrations** - Recorded user workflows

### Technology Stack
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: HuggingFace Sentence Transformers (`sentence-transformers/all-mpnet-base-v2`)
- **Storage**: Local filesystem (`.faiss` and `.pkl` files)

---

## How Offline Help Documents Work

### Document Loading Process

**When documents are loaded:**
- Documents are indexed **offline** (preprocessing step) using the `learner` CLI tool
- FAISS vector indices are created and saved to disk
- At **runtime**, indices are loaded on-demand when an AppAgent is initialized for a specific application

**Loading flow:**
```
1. INDEXING (One-time):
   python -m learner --app <app_name> --docs <path> --format json
   → Creates FAISS index in vectordb/docs/<app_name>/
   → Registers in learner/records.json

2. RUNTIME (Per-request):
   User Request → HostAgent → AppAgent
   → AppAgent.context_provision()
   → Loads FAISS index from disk
   → Ready for similarity search
```

### Current Document Formats

**JSON Format** (Recommended for custom instructions):
```json
{
    "application": "MyApp.exe",
    "request": "How to perform Save As",
    "guidance": [
        "Click on the File menu in the top-left corner",
        "Select 'Save As' from the dropdown menu",
        "Choose the destination folder",
        "Enter the desired filename",
        "Click the Save button"
    ]
}
```

**XML Format** (For Microsoft documentation):
- Microsoft-specific format requiring metadata files
- Less suitable for custom instructions

### Key Files
- **Indexer**: [learner/indexer.py](learner/indexer.py)
- **JSON Loader**: [learner/json_loader.py](learner/json_loader.py)
- **Retriever**: [ufo/rag/retriever.py](ufo/rag/retriever.py)
- **Registry**: [learner/records.json](learner/records.json)
- **Storage**: `vectordb/docs/<app_name>/`

---

## Steps to Add Custom Instructions

### Current Process

1. **Create JSON help documents** with request-guidance pairs
2. **Run indexer**: `python -m learner --app <app_name> --docs <path> --format json`
3. **Enable in config**: Set `RAG_OFFLINE_DOCS: True` in [ufo/config/config.yaml](ufo/config/config.yaml)
4. **Use at runtime**: UFO automatically matches application name and loads relevant docs

### Application Matching
- UFO matches the **process name** (e.g., `WINWORD.EXE`) to the indexed app name
- The retriever performs semantic similarity search between user requests and indexed documents

---

## Options for Loading Data

### Option 1: Offline Help Documents (Static Knowledge)
**Best for**: Curated, application-specific instructions

**Pros:**
- Fast retrieval (pre-indexed)
- No API costs
- Full control over content
- Works offline

**Cons:**
- Requires preprocessing
- Must rebuild index for updates
- Limited to pre-defined knowledge

**Use case**: Perfect for custom "Save As" type instructions

### Option 2: Online Bing Search (Dynamic Knowledge)
**Best for**: Current information, general queries

**Pros:**
- No preprocessing needed
- Always up-to-date
- Access to web knowledge

**Cons:**
- Requires API key and costs money
- Slower (network latency)
- Less control over quality
- May retrieve irrelevant results

**Use case**: Not ideal for specific software workflows

### Option 3: Self-Experience Learning (Automatic)
**Best for**: Continuous improvement

**Pros:**
- Automatically learns from successful tasks
- No manual curation needed
- Improves over time

**Cons:**
- Requires successful task completions first
- Quality depends on execution success
- Not suitable for initial setup

**Use case**: Complementary to offline docs

### Option 4: User Demonstrations (Recorded Workflows)
**Best for**: Complex, multi-step workflows

**Pros:**
- Captures actual UI interactions
- Includes screenshots and context
- High fidelity to real workflows

**Cons:**
- Requires Windows Steps Recorder
- Manual recording and processing
- More complex setup

**Use case**: Alternative to JSON docs for complex workflows

---

## Recommended Approach for Custom Software

**Primary Method: Offline Help Documents (JSON Format)**

This is the most suitable option because:
- Direct mapping of user intents to step-by-step instructions
- Fast, offline, and fully controllable
- Easy to author and maintain
- Perfect for "Save As" style instructions

**Supporting Method: User Demonstrations**

For complex workflows that are difficult to describe in text:
- Record the actual workflow using Windows Steps Recorder
- Process and index for retrieval

---

## Potential Modifications Needed

### None Required for Basic Use
The current JSON format already supports the use case:
- User request: "Save As"
- Guidance: Step-by-step instructions

### Potential Enhancements

**1. Richer Metadata**
Currently, documents only have `title`, `summary`, and `text` metadata. Could extend to include:
- UI element identifiers (button names, menu paths)
- Prerequisites or context requirements
- Screenshots or UI element descriptions
- Difficulty level or estimated steps

**2. Hierarchical Instructions**
Current format is flat. Could support:
- Sub-tasks and nested steps
- Conditional branches ("if X, then Y")
- Alternative paths

**3. Multi-Application Workflows**
Current retriever filters by single application. Could support:
- Cross-application workflows
- Application switching instructions

**4. Custom Document Loader**
Create a new loader specifically for your software documentation format if JSON isn't ideal.

---

## Implementation Plan for ETABS

### Overview
Customize UFO to work with ETABS (CSI structural engineering software) using offline help documents and experience learning. No code modifications required - only documentation creation and configuration changes.

### Phase 1: Discovery & Setup (Day 1)

**1.1 Identify ETABS Process Name**
- Open ETABS on your Windows machine
- Press `Ctrl+Shift+Esc` to open Task Manager
- Go to "Details" tab and find ETABS process (likely `ETABS.exe`, `ETABSv20.exe`, or similar)
- Note the exact executable name for indexing

**1.2 Explore ETABS UI Elements (Optional but Recommended)**

Install Windows Inspect tool to capture UI automation IDs:
```powershell
# Inspect.exe ships with Windows SDK
# Or download Accessibility Insights from: https://accessibilityinsights.io/
```

Use to record:
- Menu automation IDs (File, Define, Analyze, Design menus)
- Common dialog names
- Button and control identifiers

This helps create more precise instructions but is not required for initial setup.

### Phase 2: Create Documentation (Days 2-5)

**2.1 Create Documentation Directory**
```powershell
mkdir C:\ETABS_UFO_Docs
cd C:\ETABS_UFO_Docs
```

**2.2 JSON Format to Use**

Use the **simple JSON format** (recommended for initial setup):

```json
{
  "request": "How to define a new concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "Select 'Materials' from the dropdown menu",
    "Click the 'Add New Material' button in the Materials dialog",
    "Select 'Concrete' from the material type dropdown",
    "Enter the material name in the 'Material Name' field",
    "Set the compressive strength (fc) value",
    "Click 'OK' to save the material",
    "Click 'OK' again to close the Materials dialog"
  ]
}
```

**Key principles:**
- `request`: What the user wants to accomplish (natural language)
- `guidance`: Step-by-step instructions as a list of strings
- Each step should be a clear, actionable instruction
- Include menu paths, button names, and dialog names
- Mention specific field names when entering data

**2.3 Document 10 Core ETABS Tasks (Priority)**

Create these initial JSON files:

1. `01_create_new_model.json` - Create a new ETABS model
2. `02_define_concrete_material.json` - Define concrete material properties
3. `03_define_steel_material.json` - Define steel material properties
4. `04_define_column_section.json` - Create concrete or steel column section
5. `05_define_beam_section.json` - Create beam section
6. `06_define_grid_system.json` - Set up structural grid
7. `07_draw_frame_elements.json` - Draw columns and beams
8. `08_define_load_cases.json` - Define dead load, live load, etc.
9. `09_assign_loads.json` - Assign loads to elements
10. `10_run_analysis.json` - Execute structural analysis

**Documentation workflow for each task:**
1. Manually perform the task in ETABS while taking notes
2. Write down each menu click, dialog interaction, and button press
3. Create JSON file from your notes
4. Verify JSON syntax is valid
5. Test the instructions manually to ensure completeness

### Phase 3: Create Vector Index (Day 6)

**3.1 Run the Indexer**

From the UFO root directory:

```powershell
cd C:\Users\nniem\source\repos\UFO
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

This will:
- Load all JSON files from `C:\ETABS_UFO_Docs`
- Create embeddings using HuggingFace sentence transformers
- Build FAISS vector index
- Save to `vectordb/docs/ETABS/` (contains `index.faiss` and `index.pkl`)
- Register in `learner/records.json`

**3.2 Verify Index Creation**

Check that these files exist:
- `learner/records.json` - Should contain `"ETABS": "vectordb/docs/ETABS"`
- `vectordb/docs/ETABS/index.faiss` - The FAISS vector index
- `vectordb/docs/ETABS/index.pkl` - Metadata pickle file

### Phase 4: Configure UFO (Day 6)

**4.1 Enable RAG Features**

Edit [ufo/config/config.yaml](ufo/config/config.yaml):

```yaml
### For RAG

## RAG Configuration for the offline docs
RAG_OFFLINE_DOCS: True  # Enable offline help documents
RAG_OFFLINE_DOCS_RETRIEVED_TOPK: 2  # Retrieve top 2 most relevant docs

## RAG Configuration for experience
RAG_EXPERIENCE: True  # Enable experience learning
RAG_EXPERIENCE_RETRIEVED_TOPK: 3  # Retrieve top 3 past experiences
```

**Why these settings:**
- `RAG_OFFLINE_DOCS: True` - Loads your ETABS documentation
- `RETRIEVED_TOPK: 2` - Provides 2 most relevant help documents per task
- `RAG_EXPERIENCE: True` - UFO learns from successful ETABS tasks over time
- `EXPERIENCE_TOPK: 3` - Uses 3 similar past successes to inform actions

### Phase 5: Testing & Refinement (Days 7-10)

**5.1 Test with Simple Task**

```powershell
python -m ufo --task etabs_test1 -r "create a new ETABS model"
```

**5.2 Review Results**

Check the logs in `ufo/logs/etabs_test1/`:
- Screenshots of each step
- Action sequences taken
- Any errors or failures

**5.3 Refine Documentation**

Based on test results:
- Update steps that were unclear
- Add missing intermediate steps
- Fix incorrect menu paths or button names
- Adjust wording for better LLM understanding

**5.4 Re-index After Changes**

```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
```

Note: Re-running without `--incremental` flag replaces the entire index (recommended during initial refinement).

**5.5 Test All 10 Core Tasks**

Test each documented task systematically:
- Track success rate
- Document failure patterns
- Iterate on documentation quality

### Phase 6: Incremental Growth (Weeks 2+)

**6.1 Add More Documentation**

Create additional subdirectories for organization:

```
C:\ETABS_UFO_Docs\
├── core\           (10 initial tasks)
├── design\         (design workflows)
├── analysis\       (advanced analysis)
└── results\        (viewing and exporting results)
```

**6.2 Update Index Incrementally**

When adding new docs:

```powershell
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs\design --format json --incremental
```

The `--incremental` flag:
- Merges new documents with existing index
- Preserves all previous documentation
- Avoids rebuilding entire index

**6.3 Monitor Experience Learning**

Over time, UFO will build an experience database at:
- `vectordb/experience/experience_db/`

This captures successful ETABS task completions and uses them to improve future performance.

### Success Criteria

**Week 1:**
- [ ] ETABS process name identified
- [ ] 10 core tasks documented in JSON
- [ ] FAISS index created successfully
- [ ] At least 5/10 tasks execute successfully with UFO

**Month 1:**
- [ ] 30+ tasks documented
- [ ] 70%+ success rate on core tasks
- [ ] Experience database growing with successful trajectories
- [ ] Common failure patterns identified and addressed

**Month 3:**
- [ ] 50+ tasks documented
- [ ] 80%+ success rate
- [ ] Complex multi-dialog workflows working reliably
- [ ] UFO handles variations in user requests intelligently

---

## Critical Files Reference

### Files to Modify
1. **[ufo/config/config.yaml](ufo/config/config.yaml)** - Enable RAG settings
   - Set `RAG_OFFLINE_DOCS: True`
   - Set `RAG_EXPERIENCE: True`
   - Adjust `RETRIEVED_TOPK` values

### Files Used (No Modification Needed)
2. **[learner/indexer.py](learner/indexer.py)** - Creates FAISS index from JSON docs
3. **[learner/json_loader.py](learner/json_loader.py)** - Loads JSON format documents
4. **[ufo/rag/retriever.py](ufo/rag/retriever.py)** - Retrieves docs based on app name
5. **[ufo/agents/agent/app_agent.py](ufo/agents/agent/app_agent.py)** - Loads retriever at runtime

### Files Created
6. **C:\ETABS_UFO_Docs\*.json** - Your ETABS help documentation
7. **learner/records.json** - Auto-generated registry mapping ETABS to index
8. **vectordb/docs/ETABS/** - Auto-generated FAISS index files

---

## Example JSON Templates

### Template 1: Basic Task
```json
{
  "request": "How to [task description]?",
  "guidance": [
    "[Step 1: First action]",
    "[Step 2: Next action]",
    "[Step 3: Continue...]"
  ]
}
```

### Template 2: Menu Navigation
```json
{
  "request": "How to create a new ETABS model?",
  "guidance": [
    "Click on the 'File' menu in the top menu bar",
    "Select 'New Model' from the dropdown",
    "In the Model Initialization dialog, choose 'Grid Only' or your preferred template",
    "Click 'OK' to create the new model"
  ]
}
```

### Template 3: Complex Multi-Dialog
```json
{
  "request": "How to define a concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "Select 'Materials' from the dropdown menu",
    "Click 'Add New Material' button in the Define Materials dialog",
    "Select 'Concrete' from the Material Type dropdown",
    "Enter a name for the material (e.g., C4000) in the Material Name field",
    "Enter the compressive strength fc value (e.g., 4000 psi)",
    "Review or modify the modulus of elasticity if needed",
    "Click 'OK' to save the material",
    "Click 'OK' again to close the Define Materials dialog"
  ]
}
```

---

## Troubleshooting Common Issues

### Issue 1: UFO Can't Find ETABS
**Symptoms:** "Application not found" error

**Solutions:**
1. Ensure ETABS is running before executing UFO
2. Verify process name matches (check Task Manager)
3. Use just "ETABS" as app name (matches ETABS.exe, ETABSv20.exe, etc.)

### Issue 2: Documentation Not Retrieved
**Symptoms:** UFO doesn't use your docs, makes random guesses

**Solutions:**
1. Verify `RAG_OFFLINE_DOCS: True` in [ufo/config/config.yaml](ufo/config/config.yaml)
2. Check `learner/records.json` contains ETABS entry
3. Verify index files exist in `vectordb/docs/ETABS/`
4. Re-run indexer if files were added/modified

### Issue 3: JSON Syntax Errors
**Symptoms:** Indexer fails with JSON parse errors

**Solutions:**
1. Validate JSON syntax using online tools or VSCode
2. Ensure proper escaping of quotes in strings
3. Remove trailing commas
4. Check bracket/brace matching

### Issue 4: Steps Execute Too Fast
**Symptoms:** Actions fail because dialogs haven't loaded

**Solutions:**
1. Add intermediate wait steps in documentation (e.g., "Wait for the Materials dialog to appear")
2. Be more explicit about dialog appearances
3. Adjust timing in config if needed

### Issue 5: Wrong UI Elements Clicked
**Symptoms:** UFO clicks incorrect buttons or menus

**Solutions:**
1. Be more specific in documentation (include exact button text)
2. Mention parent dialog/window context
3. Use Inspect.exe to verify element names match your docs
4. Add distinguishing details (e.g., "OK button in the Material Properties dialog")

---

## Optional Enhancements (Future)

### Enhancement 1: Enhanced JSON Format
For even more precision, you can extend the JSON format to include:
- UI element automation IDs
- Screenshots for visual reference
- Prerequisites and validation steps
- Version-specific instructions

See the comprehensive plan output for details on creating a custom ETABS JSON loader.

### Enhancement 2: User Demonstrations
Instead of writing JSON, record workflows using Windows Steps Recorder:
```powershell
python -m record_processor -r "create concrete material" -p path/to/recording.zip
```

### Enhancement 3: Version Control
Use Git to track documentation changes:
```powershell
cd C:\ETABS_UFO_Docs
git init
git add .
git commit -m "Initial 10 ETABS core tasks"
```

---

## Quick Start Checklist

- [ ] **Day 1:** Identify ETABS process name (Task Manager → Details)
- [ ] **Days 2-5:** Create 10 JSON documentation files
- [ ] **Day 6:** Run indexer: `python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json`
- [ ] **Day 6:** Edit [ufo/config/config.yaml](ufo/config/config.yaml) - Set `RAG_OFFLINE_DOCS: True`
- [ ] **Day 7:** Test: `python -m ufo -r "create a new ETABS model"`
- [ ] **Days 8-10:** Review logs, refine docs, re-index, repeat
- [ ] **Weeks 2+:** Add more tasks incrementally using `--incremental` flag

---

## Summary

**What You're Building:**
A custom knowledge base for UFO to understand ETABS workflows using:
- Offline help documents (primary) - your JSON files
- Experience learning (secondary) - automatic learning from successes

**No Code Changes Required:**
- Use existing JSON format
- Use existing indexer tool
- Only modify configuration file

**Key Success Factor:**
Quality of your JSON documentation determines UFO's performance. Invest time in:
- Clear, step-by-step instructions
- Accurate menu and button names
- Complete coverage of common tasks
- Iterative testing and refinement

**Timeline:**
- Week 1: Working prototype with 10 core tasks
- Month 1: 30+ tasks with 70% success rate
- Month 3: 50+ tasks with 80% success rate and intelligent variation handling
