# ETABS Documentation for UFO - Complete Guide

This folder contains everything you need to customize UFO for ETABS structural engineering software.

---

## 📁 Folder Structure (Organized by Topic)

```
prompts/
├── etabs_customization/    Everything for ETABS RAG setup
├── configuration/          Config and troubleshooting
├── general_reference/      General UFO reference docs
└── README.md              This file
```

---

## 🚀 Quick Start

### Fastest Path (5 Steps):

1. **Read the main guide**
   - [etabs_customization/etabs_rag_customization_guide.md](etabs_customization/etabs_rag_customization_guide.md)

2. **Generate instructions with Claude**
   - Open [etabs_customization/claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)
   - Copy prompt → Paste into Claude → Save output

3. **Split into individual files**
   ```powershell
   python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs
   ```

4. **Create FAISS index**
   ```powershell
   python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json
   ```

5. **Enable and test**
   ```powershell
   # Edit ufo/config/config.yaml: Set RAG_OFFLINE_DOCS: True
   python -m ufo -r "create a new ETABS model"
   ```

---

## 📚 Documentation by Topic

### 🏗️ ETABS Customization (`etabs_customization/`)
**Everything you need to set up RAG for ETABS**

| File | Purpose | Priority |
|------|---------|----------|
| **[etabs_rag_customization_guide.md](etabs_customization/etabs_rag_customization_guide.md)** | Complete implementation plan | ⭐ Start here |
| **[claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)** | Copy-paste prompt for Claude | ⭐ Generate instructions |
| **[ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md)** | How to write specific instructions | ⭐ Critical for success |
| **[BULK_WORKFLOW_GUIDE.md](etabs_customization/BULK_WORKFLOW_GUIDE.md)** | Quick command reference | Fast lookup |
| **[json_instruction_generator_guide.md](etabs_customization/json_instruction_generator_guide.md)** | Manual approach (alternative) | Optional |
| **[multiple_instructions_format_guide.md](etabs_customization/multiple_instructions_format_guide.md)** | File organization explained | Optional |

**Topic Coverage:**
- RAG system architecture
- JSON instruction format
- Bulk generation workflow
- UI element specificity
- File organization
- Indexing with learner
- Testing and refinement

### ⚙️ Configuration (`configuration/`)
**Troubleshooting and config fixes**

| File | Purpose |
|------|---------|
| **[fix_rag_config.md](configuration/fix_rag_config.md)** | RAG configuration fixes |
| **[rate_limit_solutions.md](configuration/rate_limit_solutions.md)** | API rate limit solutions |
| **[azure_openai_429_rate_limit_analysis.md](configuration/azure_openai_429_rate_limit_analysis.md)** | Azure OpenAI rate limit deep dive |

**Topic Coverage:**
- RAG configuration issues
- API rate limits
- Azure OpenAI setup
- Troubleshooting

### 📖 General Reference (`general_reference/`)
**General UFO documentation (not ETABS-specific)**

| File | Purpose |
|------|---------|
| **[PERFORMANCE_OPTIMIZATION_GUIDE.md](general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md)** | Performance tuning |
| **[QUICK_REFERENCE.md](general_reference/QUICK_REFERENCE.md)** | Command cheat sheet |
| **[UI_LOGGING_GUIDE.md](general_reference/UI_LOGGING_GUIDE.md)** | Logging and debugging |

**Topic Coverage:**
- UFO performance optimization
- Quick command reference
- Logging and debugging
- General best practices

---

## 🎯 Learning Path by Topic

### Topic 1: ETABS RAG Setup (Week 1)

**Day 1 - Understanding:**
1. Read [etabs_customization/etabs_rag_customization_guide.md](etabs_customization/etabs_rag_customization_guide.md) (30 min)
2. Read [etabs_customization/ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md) (20 min)
3. Identify ETABS process name (5 min)

**Day 2 - First Instructions:**
1. Open [etabs_customization/claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)
2. Generate 3-5 test instructions with Claude (15 min)
3. Split and index using [etabs_customization/BULK_WORKFLOW_GUIDE.md](etabs_customization/BULK_WORKFLOW_GUIDE.md) (10 min)
4. Test with UFO (30 min)

**Days 3-7 - Expansion:**
1. Generate 10 core tasks (1 hour)
2. Test each task (2-3 hours)
3. Refine based on results (1-2 hours)
4. Reference [etabs_customization/ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md) for improvements

### Topic 2: Configuration & Troubleshooting (As Needed)

**When issues arise:**
- RAG not working? → [configuration/fix_rag_config.md](configuration/fix_rag_config.md)
- Rate limit errors? → [configuration/rate_limit_solutions.md](configuration/rate_limit_solutions.md)
- Azure setup issues? → [configuration/azure_openai_429_rate_limit_analysis.md](configuration/azure_openai_429_rate_limit_analysis.md)

### Topic 3: Performance & Optimization (Week 2+)

**After basic setup works:**
- Review [general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md](general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md)
- Use [general_reference/QUICK_REFERENCE.md](general_reference/QUICK_REFERENCE.md) for faster workflows
- Reference [general_reference/UI_LOGGING_GUIDE.md](general_reference/UI_LOGGING_GUIDE.md) for debugging

---

## 💡 Key Concepts

### All ETABS/RAG/JSON Content in One Place
Everything related to customizing UFO for ETABS is in `etabs_customization/`:
- Main implementation guide
- Claude prompt template
- JSON format details
- UI specificity guide
- Workflow reference

### No task_id Required
The split script auto-numbers files (01, 02, 03...). Just provide `request` and `guidance`.

### UI Specificity = Success Rate
- **Low specificity:** 40-50% success
- **High specificity:** 80-90% success
- See [etabs_customization/ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md)

---

## 🔧 Tools Provided

### split_json_instructions.py
**Location:** `C:\Users\nniem\source\repos\UFO\split_json_instructions.py`

**Features:**
- ✅ Auto-numbers files (no task_id needed)
- ✅ Validates JSON
- ✅ Clean filenames
- ✅ Category organization (`--organize`)

**Usage:**
```powershell
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs [--organize] [--no-prefix]
```

---

## 📖 Common Workflows

### Workflow 1: Generate First Batch
```powershell
# 1. Copy prompt from etabs_customization/claude_bulk_prompt.md
# 2. Paste into Claude → save output as etabs_bulk.json

# 3. Split into files
python split_json_instructions.py etabs_bulk.json C:\ETABS_UFO_Docs

# 4. Create index
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# 5. Enable RAG (edit ufo/config/config.yaml)
RAG_OFFLINE_DOCS: True

# 6. Test
python -m ufo -r "create a new ETABS model"
```

### Workflow 2: Add More Instructions
```powershell
# 1. Generate new bulk JSON with Claude
# 2. Split (script skips existing files)
python split_json_instructions.py etabs_new.json C:\ETABS_UFO_Docs

# 3. Re-index incrementally
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json --incremental
```

### Workflow 3: Fix Issues
```powershell
# 1. Review UFO logs: ufo/logs/

# 2. Update JSON files based on errors

# 3. Re-index (without --incremental to rebuild)
python -m learner --app ETABS --docs C:\ETABS_UFO_Docs --format json

# 4. Test again
```

---

## 📊 Progress Tracker

### Week 1: ETABS RAG Setup
- [ ] Read main guide: [etabs_customization/etabs_rag_customization_guide.md](etabs_customization/etabs_rag_customization_guide.md)
- [ ] Read specificity guide: [etabs_customization/ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md)
- [ ] Identify ETABS process name
- [ ] Generate 10 instructions using [etabs_customization/claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)
- [ ] Split, index, and test
- [ ] Achieve 50%+ success rate

### Week 2-3: Refinement
- [ ] Generate 10 more instructions
- [ ] Apply UI specificity best practices
- [ ] Enable experience learning
- [ ] Achieve 70%+ success rate

### Month 2+: Scaling
- [ ] Expand to 50+ instructions
- [ ] Organize by category with `--organize`
- [ ] Review [general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md](general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [ ] Achieve 80%+ success rate

---

## ❓ FAQ by Topic

### ETABS Customization

**Q: Where do I start?**
→ [etabs_customization/etabs_rag_customization_guide.md](etabs_customization/etabs_rag_customization_guide.md)

**Q: How do I generate instructions?**
→ [etabs_customization/claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)

**Q: My instructions are too vague - UFO can't find elements**
→ [etabs_customization/ui_element_specificity_guide.md](etabs_customization/ui_element_specificity_guide.md)

**Q: Do I need task_id in my JSON?**
→ No! Script auto-numbers files. Just provide `request` and `guidance`.

**Q: How do I organize files by category?**
→ Use `--organize` flag: `python split_json_instructions.py ... --organize`

### Configuration

**Q: RAG not working / UFO doesn't use my docs**
→ [configuration/fix_rag_config.md](configuration/fix_rag_config.md)

**Q: Rate limit errors?**
→ [configuration/rate_limit_solutions.md](configuration/rate_limit_solutions.md)

**Q: Azure OpenAI setup issues?**
→ [configuration/azure_openai_429_rate_limit_analysis.md](configuration/azure_openai_429_rate_limit_analysis.md)

### General UFO

**Q: How do I optimize UFO performance?**
→ [general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md](general_reference/PERFORMANCE_OPTIMIZATION_GUIDE.md)

**Q: Where are the logs?**
→ [general_reference/UI_LOGGING_GUIDE.md](general_reference/UI_LOGGING_GUIDE.md)

**Q: Quick command reference?**
→ [general_reference/QUICK_REFERENCE.md](general_reference/QUICK_REFERENCE.md)

---

## 🎓 Understanding by Topic

### ETABS RAG System

**What it does:**
1. You create JSON documentation with request-guidance pairs
2. Learner creates FAISS vector index
3. UFO retrieves relevant instructions
4. UFO executes instructions

**JSON Format:**
```json
{
  "application": "ETABS",
  "instructions": [
    {
      "request": "How to create a new ETABS model?",
      "guidance": [
        "Click on the 'File' menu in the top menu bar",
        "Select 'New Model' from the dropdown menu",
        "..."
      ]
    }
  ]
}
```

**All details in:** `etabs_customization/` folder

### Configuration System

**Key config file:** `ufo/config/config.yaml`

**ETABS RAG settings:**
```yaml
RAG_OFFLINE_DOCS: True
RAG_OFFLINE_DOCS_RETRIEVED_TOPK: 2
RAG_EXPERIENCE: True
RAG_EXPERIENCE_RETRIEVED_TOPK: 3
```

**All details in:** `configuration/` folder

---

## 🎉 Ready to Start?

### Immediate Next Steps

1. **Open:** [etabs_customization/claude_bulk_prompt.md](etabs_customization/claude_bulk_prompt.md)
2. **Generate:** Your first batch of instructions
3. **Follow:** [etabs_customization/BULK_WORKFLOW_GUIDE.md](etabs_customization/BULK_WORKFLOW_GUIDE.md)

### Need Help?

**ETABS setup questions:**
→ Check `etabs_customization/` folder

**Config/troubleshooting:**
→ Check `configuration/` folder

**General UFO questions:**
→ Check `general_reference/` folder

---

## 📋 Topic Index

### By What You're Doing

**Setting up ETABS with UFO:**
→ `etabs_customization/` folder (6 files)

**Fixing config issues:**
→ `configuration/` folder (3 files)

**Optimizing UFO performance:**
→ `general_reference/` folder (3 files)

### By File Type

**Main guides:** All in `etabs_customization/`
**Quick references:** `BULK_WORKFLOW_GUIDE.md`, `QUICK_REFERENCE.md`
**Deep dives:** All `*_guide.md` files
**Troubleshooting:** All in `configuration/`

---

**Last Updated:** 2025-12-10
**Version:** 3.0 (Topic-Based Organization)
