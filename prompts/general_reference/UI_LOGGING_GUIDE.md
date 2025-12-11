# UFO UI Logging Guide
## Extracting Automation Details for Non-LLM Replay

---

## Quick Answer

**YES**, UFO can log comprehensive UI control details including:
- ✅ Control IDs (automation IDs, names, types)
- ✅ Exact pixel coordinates of every clicked element
- ✅ Full UI tree hierarchy (XML/JSON)
- ✅ Complete action sequence (clicks, text input, keyboard commands)
- ✅ Control properties (class names, types, states)

You can use this data to create traditional automation scripts (Python pywinauto, Selenium, AutoIt, etc.) without any LLM.

---

## Table of Contents
1. [Enable Full Logging](#enable-full-logging)
2. [Understanding Log Files](#understanding-log-files)
3. [Reading UI Control Details](#reading-ui-control-details)
4. [Extracting Action Sequences](#extracting-action-sequences)
5. [Using UI Trees](#using-ui-trees)
6. [Example: Converting to pywinauto Script](#example-converting-to-pywinauto-script)
7. [Programmatic Access](#programmatic-access)

---

## Enable Full Logging

### Step 1: Configure Maximum Logging

Edit `ufo/config/config_dev.yaml`:

```yaml
# ============================================
# FULL UI LOGGING CONFIGURATION
# ============================================

# UI Tree dumps (hierarchical control structure)
SAVE_UI_TREE: True                  # Save JSON UI tree at each step

# XML State dumps (alternative format)
LOG_XML: True                       # Save XML representation of UI

# Screenshots (visual reference)
SAVE_FULL_SCREEN: True              # Full desktop screenshots
INCLUDE_LAST_SCREENSHOT: True       # Include in context
CONCAT_SCREENSHOT: False            # Separate clean + annotated

# Logging verbosity
PRINT_LOG: True                     # Print to console
LOG_LEVEL: "DEBUG"                  # Maximum detail
LOG_TO_MARKDOWN: True               # Human-readable output

# Screenshot storage
SCREENSHOT_TO_MEMORY: True          # Keep in memory for reference

# Control detection
CONTROL_BACKEND: ["uia"]            # UIA provides most detailed info
CONTROL_LIST: [                     # All control types
    "Button", "Edit", "TabItem", "Document", "ListItem",
    "MenuItem", "ScrollBar", "TreeItem", "Hyperlink",
    "ComboBox", "RadioButton", "CheckBox", "Image", "Spinner"
]
```

### Step 2: Run Your Task

```bash
python ufo.py --task "Open Notepad and type Hello World"
```

### Step 3: Find Your Logs

Logs are saved to:
```
logs/<task_name_timestamp>/
├── response.log                    # Action history (JSON lines)
├── request.log                     # Control details (JSON lines)
├── output.md                       # Human-readable summary
├── action_step0.png               # Screenshots
├── action_step0_annotated.png     # With numbered labels
├── xml/
│   └── action_step0.xml           # XML UI dumps
└── ui_trees/
    └── ui_tree_step0.json         # JSON UI trees
```

---

## Understanding Log Files

### File Overview

| File | Contains | Format | Best For |
|------|----------|--------|----------|
| `output.md` | Human-readable trajectory | Markdown | Quick overview |
| `ui_tree_step*.json` | Full UI hierarchy | JSON | Control structure |
| `xml/action_step*.xml` | UI state dump | XML | Alternative format |
| `response.log` | Action sequences | JSON (compressed) | What was done |
| `request.log` | Control details | JSON (compressed) | What was available |
| `*.png` | Screenshots | PNG | Visual reference |

---

## Reading UI Control Details

### Method 1: UI Tree JSON (Easiest)

**File:** `logs/<task>/ui_trees/ui_tree_step0.json`

```json
{
  "id": "node_0",
  "name": "OK",
  "control_type": "Button",
  "automation_id": "btnOK",
  "class_name": "Button",
  "rectangle": {
    "left": 500,
    "top": 300,
    "right": 600,
    "bottom": 350
  },
  "adjusted_rectangle": {
    "left": 100,
    "top": 50,
    "right": 200,
    "bottom": 100
  },
  "relative_rectangle": {
    "left": 0.1,
    "top": 0.05,
    "right": 0.2,
    "bottom": 0.1
  },
  "level": 2,
  "children": []
}
```

**Key Fields:**
- `name` - Control label/text
- `control_type` - Button, Edit, MenuItem, etc.
- `automation_id` - Unique identifier for pywinauto
- `class_name` - Windows class name
- `rectangle` - Absolute screen coordinates
- `adjusted_rectangle` - Relative to application window
- `relative_rectangle` - Normalized ratios (0-1)

**Finding a Control:**
```python
import json

# Load UI tree
with open('logs/task/ui_trees/ui_tree_step0.json', 'r') as f:
    tree = json.load(f)

def find_control(tree, name):
    """Recursively find control by name"""
    if tree.get('name') == name:
        return tree
    for child in tree.get('children', []):
        result = find_control(child, name)
        if result:
            return result
    return None

# Find the "OK" button
ok_button = find_control(tree, "OK")
print(f"Automation ID: {ok_button['automation_id']}")
print(f"Coordinates: {ok_button['rectangle']}")
```

---

### Method 2: Annotated Screenshots (Visual)

**File:** `logs/<task>/action_step0_annotated.png`

Open the annotated screenshot to see:
- Each control numbered with a label (1, 2, 3, etc.)
- Color-coded by control type
- Bounding boxes around clickable elements

**Use this to:**
- Visually identify which control was clicked
- See the spatial layout of UI elements
- Match control numbers to action logs

---

### Method 3: XML Dumps (Traditional Format)

**File:** `logs/<task>/xml/action_step0.xml`

```xml
<Button Name="OK" AutomationId="btnOK" ControlType="Button">
  <BoundingRectangle Left="500" Top="300" Right="600" Bottom="350"/>
  <ClassName>Button</ClassName>
  <IsEnabled>True</IsEnabled>
  <IsVisible>True</IsVisible>
</Button>
```

**Good for:**
- Tools that parse XML (UIAutomation Inspector)
- Legacy automation frameworks
- Exporting to other tools

---

## Extracting Action Sequences

### Method 1: Read output.md (Easiest)

**File:** `logs/<task>/output.md`

```markdown
## Round 0, Step 0

**Application:** NOTEPAD.EXE

**Action:**
- Function: click_input
- Arguments: {'button': 'left', 'control_label': '1'}
- Control: Text Editor (Edit)
- Status: CONTINUE

**Results:** Success

---

## Round 0, Step 1

**Action:**
- Function: type_keys
- Arguments: {'text': 'Hello World'}
- Control: Text Editor (Edit)
- Status: FINISH

**Results:** Success
```

**Extract:**
1. What was clicked (control label, type)
2. What function was called (click_input, type_keys, etc.)
3. What arguments were passed
4. Success/failure status

---

### Method 2: Parse response.log (Programmatic)

**File:** `logs/<task>/response.log`

**Format:** JSON lines (one JSON object per line, may be compressed)

**Example entry:**
```json
{
  "Step": 0,
  "Subtask": "Click the OK button",
  "Action": [
    {
      "Function": "click_input",
      "Args": {"button": "left", "control_label": "1"},
      "ControlLabel": "1",
      "ControlText": "OK",
      "Status": "CONTINUE",
      "Results": {
        "status": "success"
      }
    }
  ],
  "ControlLog": {
    "1": {
      "control_name": "OK",
      "control_type": "Button",
      "control_automation_id": "btnOK",
      "control_class": "Button",
      "control_coordinates": {
        "left": 100,
        "top": 50,
        "right": 200,
        "bottom": 100
      }
    }
  },
  "Application": "NOTEPAD.EXE"
}
```

**Parse with Python:**
```python
import json

# Read response.log
with open('logs/task/response.log', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line.strip())

            # Extract action details
            for action in step.get('Action', []):
                function = action['Function']
                args = action['Args']
                control = action.get('ControlText', '')

                print(f"Step {step['Step']}: {function}({args}) on '{control}'")

            # Extract control details
            for label, control in step.get('ControlLog', {}).items():
                print(f"  Control {label}: {control['control_type']} '{control['control_name']}'")
                print(f"    Automation ID: {control.get('control_automation_id')}")
                print(f"    Coordinates: {control['control_coordinates']}")

        except json.JSONDecodeError:
            # Line may be compressed, skip for now
            continue
```

---

### Method 3: Use UFO's Trajectory Parser

**Best for:** Complex tasks with many steps

```python
from ufo.module.sessions import Trajectory

# Load trajectory
trajectory = Trajectory("logs/task_name/")

# Access all steps
for step_data in trajectory.step_log:
    step_num = step_data.get('Step', 0)
    actions = step_data.get('Action', [])

    print(f"\n=== Step {step_num} ===")

    for action in actions:
        func = action.get('Function')
        args = action.get('Args', {})
        control_text = action.get('ControlText', '')

        print(f"  {func}({args})")
        print(f"  Target: {control_text}")

    # Get control details
    control_logs = step_data.get('ControlLog', {})
    for label, ctrl in control_logs.items():
        print(f"  Control {label}: {ctrl['control_type']} - {ctrl['control_name']}")
        print(f"    AutoID: {ctrl.get('control_automation_id')}")
        print(f"    Coords: {ctrl['control_coordinates']}")
```

---

## Using UI Trees

### Complete UI Hierarchy

UI trees show the **entire control structure** of the application window:

```json
{
  "id": "node_0",
  "name": "Notepad",
  "control_type": "Window",
  "children": [
    {
      "id": "node_1",
      "name": "File",
      "control_type": "MenuItem",
      "children": [
        {
          "id": "node_2",
          "name": "New",
          "control_type": "MenuItem",
          "automation_id": "menuFileNew"
        },
        {
          "id": "node_3",
          "name": "Open",
          "control_type": "MenuItem",
          "automation_id": "menuFileOpen"
        }
      ]
    },
    {
      "id": "node_4",
      "name": "",
      "control_type": "Edit",
      "automation_id": "edit1",
      "rectangle": {"left": 0, "top": 50, "right": 800, "bottom": 600}
    }
  ]
}
```

### Flatten UI Tree for Search

```python
import json

def flatten_tree(tree, parent_path=""):
    """Flatten hierarchical UI tree into list of controls"""
    controls = []

    path = f"{parent_path}/{tree.get('name', tree.get('id'))}"

    controls.append({
        'path': path,
        'id': tree.get('id'),
        'name': tree.get('name'),
        'type': tree.get('control_type'),
        'automation_id': tree.get('automation_id'),
        'rectangle': tree.get('rectangle'),
        'level': tree.get('level', 0)
    })

    for child in tree.get('children', []):
        controls.extend(flatten_tree(child, path))

    return controls

# Load and flatten
with open('logs/task/ui_trees/ui_tree_step0.json', 'r') as f:
    tree = json.load(f)

flat_controls = flatten_tree(tree)

# Search by type
buttons = [c for c in flat_controls if c['type'] == 'Button']
print(f"Found {len(buttons)} buttons:")
for btn in buttons:
    print(f"  - {btn['name']} (ID: {btn['automation_id']})")
```

---

## Example: Converting to pywinauto Script

### UFO Execution Logs → pywinauto Code

**Scenario:** UFO automated Notepad to create and save a file

**Step 1: Read the logs**

From `output.md`:
```
Step 0: click_input on "File" (MenuItem)
Step 1: click_input on "Save As" (MenuItem)
Step 2: type_keys("document.txt") on filename field (Edit)
Step 3: click_input on "Save" (Button)
```

**Step 2: Extract control identifiers**

From `ui_tree_step*.json`:
```json
Step 0: {"name": "File", "automation_id": "menuFile"}
Step 1: {"name": "Save As", "automation_id": "menuFileSaveAs"}
Step 2: {"name": "", "automation_id": "1148", "control_type": "Edit"}
Step 3: {"name": "Save", "automation_id": "1", "control_type": "Button"}
```

**Step 3: Generate pywinauto script**

```python
from pywinauto import Application
from pywinauto.keyboard import send_keys

# Launch application
app = Application(backend="uia").start("notepad.exe")

# Get main window
main_window = app.window(title_re=".*Notepad.*")

# Step 0: Click File menu
main_window.child_window(auto_id="menuFile", control_type="MenuItem").click_input()

# Step 1: Click Save As
main_window.child_window(auto_id="menuFileSaveAs", control_type="MenuItem").click_input()

# Wait for Save As dialog
save_dialog = app.window(title_re="Save As")

# Step 2: Type filename
filename_field = save_dialog.child_window(auto_id="1148", control_type="Edit")
filename_field.type_keys("document.txt")

# Step 3: Click Save button
save_button = save_dialog.child_window(auto_id="1", control_type="Button")
save_button.click_input()

print("Automation complete!")
```

### Automated Conversion Script

```python
import json

def ufo_to_pywinauto(log_path):
    """Convert UFO logs to pywinauto script"""

    # Read response.log
    with open(f"{log_path}/response.log", 'r') as f:
        steps = [json.loads(line) for line in f if line.strip()]

    # Read UI trees
    ui_trees = {}
    for i in range(len(steps)):
        try:
            with open(f"{log_path}/ui_trees/ui_tree_step{i}.json", 'r') as f:
                ui_trees[i] = json.load(f)
        except FileNotFoundError:
            continue

    # Generate script
    script = [
        "from pywinauto import Application",
        "from pywinauto.keyboard import send_keys",
        "",
        "# Launch application",
        f"app = Application(backend='uia').start('{steps[0]['Application'].lower()}')",
        "",
        "# Get main window",
        "main_window = app.window(title_re='.*')",
        ""
    ]

    for step in steps:
        step_num = step.get('Step', 0)

        for action in step.get('Action', []):
            func = action['Function']
            control_label = action.get('ControlLabel', '')

            # Find control in UI tree
            if step_num in ui_trees:
                # Search for control by label
                # (simplified - real implementation needs tree search)
                pass

            # Generate code based on function
            if func == 'click_input':
                script.append(f"# Step {step_num}: Click {action.get('ControlText', '')}")
                script.append(f"main_window.child_window(auto_id='...').click_input()")
            elif func == 'type_keys':
                text = action['Args'].get('text', '')
                script.append(f"# Step {step_num}: Type text")
                script.append(f"main_window.type_keys('{text}')")

            script.append("")

    return "\n".join(script)

# Usage
script = ufo_to_pywinauto("logs/notepad_task_20250101_120000")
print(script)
```

---

## Programmatic Access

### Using UFO's Built-in Classes

```python
from ufo.module.sessions import Trajectory
from ufo.automator.ui_control.ui_tree import UITree, UITreeNode
import json

# ============================================
# Load Trajectory
# ============================================
trajectory = Trajectory("logs/task_name/")

# Get all steps
steps = trajectory.step_log

# Get specific step
step_0 = steps[0]

# ============================================
# Access Action Details
# ============================================
actions = step_0.get('Action', [])
for action in actions:
    print(f"Function: {action['Function']}")
    print(f"Arguments: {action['Args']}")
    print(f"Control: {action.get('ControlText')}")
    print(f"Status: {action['Status']}")
    print()

# ============================================
# Access Control Information
# ============================================
control_logs = step_0.get('ControlLog', {})
for label, control in control_logs.items():
    print(f"Control {label}:")
    print(f"  Name: {control['control_name']}")
    print(f"  Type: {control['control_type']}")
    print(f"  Automation ID: {control.get('control_automation_id')}")
    print(f"  Coordinates: {control['control_coordinates']}")
    print()

# ============================================
# Load UI Tree
# ============================================
with open('logs/task_name/ui_trees/ui_tree_step0.json', 'r') as f:
    tree_data = json.load(f)

# Reconstruct UITree object
tree = UITree.from_dict(tree_data)

# Get root node
root = tree.root

# Traverse tree
def print_tree(node, indent=0):
    print("  " * indent + f"- {node.name} ({node.control_type})")
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(root)

# ============================================
# Find Controls
# ============================================
def find_controls_by_type(node, control_type):
    """Find all controls of a specific type"""
    results = []
    if node.control_type == control_type:
        results.append(node)
    for child in node.children:
        results.extend(find_controls_by_type(child, control_type))
    return results

# Find all buttons
buttons = find_controls_by_type(root, "Button")
print(f"Found {len(buttons)} buttons:")
for btn in buttons:
    print(f"  - {btn.name}")
```

---

## Summary: What You Can Extract

| Information | Available | Where to Find |
|-------------|-----------|---------------|
| Control Names | ✅ Yes | UI trees, response.log |
| Automation IDs | ✅ Yes | UI trees, XML dumps |
| Control Types | ✅ Yes | All logs |
| Coordinates | ✅ Yes | UI trees, response.log |
| Action Sequence | ✅ Yes | response.log, output.md |
| Function Calls | ✅ Yes | response.log |
| Text Input | ✅ Yes | Action Args |
| Click Locations | ✅ Yes | Control coordinates |
| UI Hierarchy | ✅ Yes | UI trees (JSON) |
| Screenshots | ✅ Yes | PNG files |
| Execution Results | ✅ Yes | response.log |
| Timing Info | ✅ Yes | response.log (time_cost) |

---

## Quick Start Checklist

1. ✅ Enable full logging in `config_dev.yaml`:
   ```yaml
   SAVE_UI_TREE: True
   LOG_XML: True
   LOG_LEVEL: "DEBUG"
   ```

2. ✅ Run your task with UFO

3. ✅ Find logs in `logs/<task_name>/`

4. ✅ Check `output.md` for human-readable summary

5. ✅ Read `ui_tree_step*.json` for control details

6. ✅ Parse `response.log` for action sequences

7. ✅ Use annotated screenshots for visual reference

8. ✅ Convert to pywinauto/Selenium/AutoIt script

---

## Tools for Analysis

### Recommended Tools:
- **JSON Viewer**: VS Code, Notepad++, online viewers
- **pywinauto Inspector**: `python -m pywinauto.application`
- **UIAutomation Spy**: Microsoft Accessibility Insights
- **Python**: For parsing and converting logs

### UFO Utilities:
- `Trajectory` class: Load and parse logs
- `UITree` class: Work with UI hierarchies
- `flatten_ui_tree()`: Convert hierarchy to list
- `ui_tree_diff()`: Compare UI states

---

## Next Steps

1. **Run UFO on your target application** with full logging enabled
2. **Review the generated logs** to understand the automation path
3. **Extract control identifiers** (automation IDs, coordinates)
4. **Write a traditional automation script** using the extracted data
5. **Test and refine** your script

---

**Related Files:**
- Configuration examples: `ufo/prompts/config_examples/debug_full_visual.yaml`
- Log parser: `ufo/module/sessions.py`
- UI tree utilities: `ufo/automator/ui_control/ui_tree.py`

**Need help?** Check the main documentation or open an issue on GitHub.
