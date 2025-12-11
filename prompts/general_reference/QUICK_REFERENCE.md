# UFO Quick Reference Guide
## Finding UI Control Details for Non-LLM Automation

---

## Quick Answer: "Where do I find...?"

| I need to find... | Look in this file | Section/Field |
|-------------------|-------------------|---------------|
| **Control IDs** | `ui_trees/ui_tree_step*.json` | `automation_id` |
| **Control names** | `ui_trees/ui_tree_step*.json` | `name` |
| **Control types** | `ui_trees/ui_tree_step*.json` | `control_type` |
| **Coordinates** | `ui_trees/ui_tree_step*.json` | `rectangle` |
| **What was clicked** | `output.md` | Action sections |
| **Action sequence** | `output.md` or `response.log` | Step by step |
| **Visual layout** | `action_step*_annotated.png` | Numbered labels |
| **Control hierarchy** | `ui_trees/ui_tree_step*.json` | `children` array |
| **Function calls** | `response.log` | `Function` + `Args` |
| **Text that was typed** | `response.log` | `Args.text` |

---

## The 3 Most Important Files

### 1. `output.md` - Start Here! 📄
**Human-readable summary of everything**

```markdown
## Round 0, Step 0

Application: NOTEPAD.EXE

Action:
- Function: click_input
- Control: Text Editor (Edit)
- Status: CONTINUE

Results: Success
```

**Use this to:** Understand what UFO did step-by-step

---

### 2. `ui_trees/ui_tree_step*.json` - Control Details 🌳
**Complete UI structure with IDs and coordinates**

```json
{
  "id": "node_42",
  "name": "Save",
  "control_type": "Button",
  "automation_id": "btnSave",
  "class_name": "Button",
  "rectangle": {
    "left": 700,
    "top": 500,
    "right": 780,
    "bottom": 530
  }
}
```

**Use this to:** Get automation IDs for pywinauto scripts

---

### 3. `action_step*_annotated.png` - Visual Reference 🖼️
**Screenshots with numbered control labels**

**Use this to:** See what controls were available and which were clicked

---

## Quick Extraction Workflow

### Step 1: Enable Logging (30 seconds)

```yaml
# Edit: ufo/config/config_dev.yaml
SAVE_UI_TREE: True
LOG_XML: True
LOG_LEVEL: "DEBUG"
```

### Step 2: Run UFO (varies)

```bash
python ufo.py --task "Your task here"
```

### Step 3: Extract Automation (10 seconds)

```bash
python ufo/prompts/examples/extract_automation_from_logs.py logs/<task_folder>
```

### Step 4: Get Your Script!

Find it in: `logs/<task_folder>/generated_automation.py`

---

## File Structure Cheat Sheet

```
logs/your_task_20250101_120000/
│
├── 📄 output.md                          ← Start here! Human-readable
│
├── 📊 response.log                       ← Action history (JSON)
├── 📊 request.log                        ← Control details (JSON)
│
├── 🖼️ action_step0.png                   ← Clean screenshot
├── 🖼️ action_step0_annotated.png         ← With numbered labels ⭐
├── 🖼️ action_step0_selected_controls.png ← Highlighted clicked controls
│
├── ui_trees/
│   ├── 🌳 ui_tree_step0.json             ← UI hierarchy ⭐⭐⭐
│   ├── 🌳 ui_tree_step1.json
│   └── 🌳 ui_tree_step2.json
│
└── xml/
    ├── 📋 action_step0.xml               ← XML format (alternative)
    ├── 📋 action_step1.xml
    └── 📋 action_step2.xml
```

**Key:**
- ⭐⭐⭐ = Most useful for automation extraction
- ⭐ = Very helpful
- Others = Nice to have

---

## Common Control Properties

### From UI Tree JSON

```json
{
  "id": "node_123",                    // Internal UFO ID
  "name": "OK",                        // Visible text/label
  "control_type": "Button",            // Button, Edit, MenuItem, etc.
  "automation_id": "btnOK",            // ⭐ USE THIS for pywinauto
  "class_name": "Button",              // Windows class
  "rectangle": {
    "left": 100, "top": 50,            // Screen coordinates
    "right": 200, "bottom": 100
  },
  "adjusted_rectangle": {              // Relative to app window
    "left": 10, "top": 5,
    "right": 110, "bottom": 55
  },
  "relative_rectangle": {              // Normalized 0-1
    "left": 0.05, "top": 0.025,
    "right": 0.55, "top": 0.275
  },
  "level": 2,                          // Depth in UI tree
  "children": [...]                    // Child controls
}
```

---

## Quick Code Snippets

### Read UI Tree
```python
import json

with open('logs/task/ui_trees/ui_tree_step0.json') as f:
    tree = json.load(f)

# Find all buttons
def find_buttons(node):
    buttons = []
    if node['control_type'] == 'Button':
        buttons.append(node)
    for child in node.get('children', []):
        buttons.extend(find_buttons(child))
    return buttons

buttons = find_buttons(tree)
for btn in buttons:
    print(f"{btn['name']}: {btn['automation_id']}")
```

### Parse Action Log
```python
import json

with open('logs/task/response.log') as f:
    for line in f:
        step = json.loads(line.strip())
        for action in step.get('Action', []):
            print(f"Step {step['Step']}: {action['Function']} on {action.get('ControlText')}")
```

### Generate pywinauto Code
```python
# Use the provided script!
python ufo/prompts/examples/extract_automation_from_logs.py logs/task
# Output: logs/task/generated_automation.py
```

---

## Control Type Reference

| UFO Control Type | pywinauto Usage | Common Examples |
|------------------|-----------------|-----------------|
| `Button` | `control_type='Button'` | OK, Cancel, Save |
| `Edit` | `control_type='Edit'` | Text boxes, input fields |
| `MenuItem` | `control_type='MenuItem'` | File, Edit, View menus |
| `Document` | `control_type='Document'` | Rich text editors |
| `ListItem` | `control_type='ListItem'` | List entries |
| `TabItem` | `control_type='TabItem'` | Tab controls |
| `ComboBox` | `control_type='ComboBox'` | Dropdown menus |
| `CheckBox` | `control_type='CheckBox'` | Checkboxes |
| `RadioButton` | `control_type='RadioButton'` | Radio buttons |
| `TreeItem` | `control_type='TreeItem'` | Tree view items |
| `Hyperlink` | `control_type='Hyperlink'` | Links |
| `Image` | `control_type='Image'` | Icons, pictures |

---

## pywinauto Code Templates

### Click a Button by Automation ID
```python
from pywinauto import Application

app = Application(backend='uia').start('notepad.exe')
main = app.window(title_re='.*Notepad.*')

# From UI tree: "automation_id": "btnOK"
ok_btn = main.child_window(auto_id='btnOK', control_type='Button')
ok_btn.click_input()
```

### Type Text in Edit Field
```python
# From UI tree: "automation_id": "edit1", "control_type": "Edit"
text_field = main.child_window(auto_id='edit1', control_type='Edit')
text_field.type_keys('Hello World')
```

### Click Menu Item
```python
# From UI tree: "name": "File", "control_type": "MenuItem"
file_menu = main.child_window(title='File', control_type='MenuItem')
file_menu.click_input()
```

### Click by Coordinates (Fallback)
```python
# From UI tree: "rectangle": {"left": 100, "top": 50, "right": 200, "bottom": 100}
main.click_input(coords=(150, 75))  # Center of the control
```

---

## Common Patterns

### Pattern 1: Menu Navigation
```
UFO Log:
  Step 0: click_input on "File" (MenuItem)
  Step 1: click_input on "Save As" (MenuItem)

pywinauto:
  main.child_window(title='File').click_input()
  main.child_window(title='Save As').click_input()
```

### Pattern 2: Form Filling
```
UFO Log:
  Step 0: click_input on "Name" (Edit)
  Step 1: type_keys("John Doe")
  Step 2: click_input on "Submit" (Button)

pywinauto:
  name_field = main.child_window(auto_id='txtName', control_type='Edit')
  name_field.type_keys('John Doe')
  submit_btn = main.child_window(auto_id='btnSubmit', control_type='Button')
  submit_btn.click_input()
```

### Pattern 3: Dialog Interaction
```
UFO Log:
  Step 0: click_input on "Open" (Button) → Opens dialog
  Step 1: type_keys("file.txt") on filename field
  Step 2: click_input on "OK" (Button)

pywinauto:
  main.child_window(auto_id='btnOpen').click_input()
  dialog = app.window(title='Open File')
  dialog.child_window(auto_id='1148', control_type='Edit').type_keys('file.txt')
  dialog.child_window(auto_id='1', control_type='Button').click_input()
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No `ui_tree_step*.json` files | Enable `SAVE_UI_TREE: True` in config |
| Empty `response.log` | Check task completed, enable `LOG_LEVEL: "DEBUG"` |
| No automation IDs in UI tree | Some apps don't have them, use coordinates instead |
| Coordinates don't work | Window moved/resized, use automation IDs or maximize window |
| Generated script fails | Add waits: `ctrl.wait('visible', timeout=10)` |

---

## Next Steps

1. ✅ **Read this guide** - You are here!
2. ✅ **Enable logging** - Edit `config_dev.yaml`
3. ✅ **Run UFO** - On your target task
4. ✅ **Check output.md** - Understand what happened
5. ✅ **Extract automation** - Run the extraction script
6. ✅ **Test script** - Run the generated pywinauto code
7. ✅ **Refine** - Adjust IDs and add error handling

---

## Full Guides

- 📖 [UI Logging Guide](UI_LOGGING_GUIDE.md) - Complete logging documentation
- 🚀 [Performance Optimization](PERFORMANCE_OPTIMIZATION_GUIDE.md) - Speed up UFO
- 🔧 [Extraction Examples](examples/README.md) - Practical tools
- ⚙️ [Config Examples](config_examples/README.md) - Ready configs

---

## One-Line Summary

**Enable `SAVE_UI_TREE: True`, run UFO, then check `logs/<task>/ui_trees/ui_tree_step*.json` for automation IDs and coordinates!**

---

**Need help?** Open an issue on GitHub or check the full documentation.
