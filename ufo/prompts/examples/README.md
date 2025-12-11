# UFO Log Extraction Examples

Tools and scripts for extracting automation details from UFO execution logs.

## Available Tools

### `extract_automation_from_logs.py`

Converts UFO execution logs into traditional automation scripts (pywinauto).

**What it does:**
- ✅ Parses UFO response.log and UI tree files
- ✅ Extracts all control details (IDs, types, coordinates)
- ✅ Generates a pywinauto Python script
- ✅ Creates a complete automation data export (JSON)
- ✅ Shows summary of all actions and controls

**Usage:**
```bash
python extract_automation_from_logs.py <log_folder_path>
```

**Example:**
```bash
# First, run UFO with full logging enabled
cd c:\Users\nniem\source\repos\UFO

# Then extract the automation details
python ufo/prompts/examples/extract_automation_from_logs.py logs/notepad_task_20250101_120000
```

**Output:**
- `generated_automation.py` - Ready-to-run pywinauto script
- `automation_data.json` - Complete control map and action sequence
- Console output with detailed summary

---

## Quick Start Guide

### Step 1: Enable Full Logging

Edit `ufo/config/config_dev.yaml`:

```yaml
SAVE_UI_TREE: True      # Save UI control hierarchies
LOG_XML: True           # Save XML dumps
LOG_LEVEL: "DEBUG"      # Verbose logging
PRINT_LOG: True         # Console output
```

### Step 2: Run UFO on Your Task

```bash
python ufo.py --task "Open Notepad and type Hello World"
```

This creates logs in: `logs/notepad_task_<timestamp>/`

### Step 3: Extract Automation Details

```bash
python ufo/prompts/examples/extract_automation_from_logs.py logs/notepad_task_<timestamp>
```

### Step 4: Review Generated Script

Open `logs/notepad_task_<timestamp>/generated_automation.py`:

```python
from pywinauto import Application
import time

# Launch application
app = Application(backend='uia').start('notepad.exe')

# Get main window
main_window = app.window(title_re='.*')

# Step 0: Type text
ctrl = main_window.child_window(auto_id='edit1', control_type='Edit')
ctrl.type_keys('Hello World')

print("Automation complete!")
```

### Step 5: Test the Generated Script

```bash
python logs/notepad_task_<timestamp>/generated_automation.py
```

---

## Example Output

### Console Summary
```
Loading logs from: logs/notepad_task_20250101_120000
Loaded 5 steps
Loaded 5 UI trees

================================================================================
AUTOMATION SUMMARY
================================================================================
Application: NOTEPAD.EXE
Total Steps: 5

--- Step 0: Open Notepad ---
  Action: click_input
  Arguments: {'button': 'left'}
  Control: Notepad Window (Label: 1)
  Status: CONTINUE
  Available Controls:
    [1] Edit: 'Text Editor'
        AutoID: 15
        Coords: (0, 50) - (800, 600)

--- Step 1: Type text ---
  Action: type_keys
  Arguments: {'text': 'Hello World'}
  Control: Text Editor (Label: 1)
  Status: FINISH
...
```

### Control Map
```
================================================================================
CONTROL MAP (All Detected Controls)
================================================================================

Button (3 found):
  - 'File'
    AutoID: Item 20127
    Class: MenuItem
    Coords: (0, 0) - (37, 25)

  - 'Save'
    AutoID: 1
    Class: Button
    Coords: (700, 500) - (780, 530)

Edit (1 found):
  - 'Text Editor'
    AutoID: 15
    Class: Edit
    Coords: (0, 50) - (800, 600)
```

---

## Understanding the Generated Script

The extractor creates pywinauto code based on:

1. **Control Automation IDs** - Best for reliable automation
   ```python
   ctrl = main_window.child_window(auto_id='btnOK', control_type='Button')
   ```

2. **Coordinates** - Fallback when IDs not available
   ```python
   main_window.click_input(coords=(150, 75))
   ```

3. **Control Types** - Ensures correct element selected
   ```python
   control_type='Edit'  # Button, Edit, MenuItem, etc.
   ```

---

## Customizing the Generated Script

### Add Error Handling
```python
try:
    ctrl = main_window.child_window(auto_id='btnOK')
    ctrl.click_input()
except Exception as e:
    print(f"Error clicking button: {e}")
```

### Add Waits
```python
from pywinauto import timings
timings.Timings.after_click_wait = 0.5

# Or explicit waits
ctrl.wait('visible', timeout=10)
```

### Use Window Titles
```python
# Instead of title_re='.*'
main_window = app.window(title='Notepad')
```

---

## JSON Export Format

`automation_data.json` contains:

```json
{
  "application": "NOTEPAD.EXE",
  "total_steps": 5,
  "steps": [
    {
      "Step": 0,
      "Subtask": "Open Notepad",
      "Action": [
        {
          "Function": "click_input",
          "Args": {"button": "left"},
          "ControlText": "Notepad",
          "Status": "CONTINUE"
        }
      ],
      "ControlLog": {
        "1": {
          "control_name": "Text Editor",
          "control_type": "Edit",
          "control_automation_id": "15",
          "control_coordinates": {
            "left": 0,
            "top": 50,
            "right": 800,
            "bottom": 600
          }
        }
      }
    }
  ],
  "ui_trees": {...},
  "control_map": {...}
}
```

Use this for:
- Custom script generation
- Integration with other tools
- Analysis and reporting
- Test data generation

---

## Common Use Cases

### 1. Creating Regression Tests
Run UFO once, extract automation, convert to pytest:

```python
import pytest
from pywinauto import Application

@pytest.fixture
def notepad():
    app = Application(backend='uia').start('notepad.exe')
    yield app
    app.kill()

def test_type_text(notepad):
    main = notepad.window(title_re='.*Notepad.*')
    editor = main.child_window(auto_id='15', control_type='Edit')
    editor.type_keys('Test text')
    assert editor.window_text() == 'Test text'
```

### 2. Documenting Manual Processes
Use UFO to "record" a manual process, then share the generated script.

### 3. Migrating to Traditional Automation
Start with UFO for rapid prototyping, extract to pywinauto for production.

### 4. Learning Application Structure
Explore UI trees to understand how the application is organized.

---

## Troubleshooting

### "No steps found in logs"
**Cause:** `response.log` is empty or compressed
**Solution:**
- Ensure task completed successfully
- Check if logs are compressed (may need decompression)
- Verify `LOG_LEVEL: "DEBUG"` in config

### "UI tree files not found"
**Cause:** `SAVE_UI_TREE: False` in config
**Solution:** Enable it:
```yaml
SAVE_UI_TREE: True
```

### Generated script doesn't work
**Cause:** Automation IDs may be dynamic or missing
**Solution:**
- Use coordinate-based clicks as fallback
- Inspect application with `python -m pywinauto.application`
- Add explicit waits for UI elements

### Control coordinates are wrong
**Cause:** Multi-monitor setup or window position changed
**Solution:**
- Use automation IDs instead of coordinates
- Maximize window before automation
- Use relative coordinates

---

## Advanced Usage

### Extract Specific Steps Only

Modify the script to filter steps:

```python
# Only extract steps 2-5
extractor.steps = [s for s in extractor.steps if 2 <= s.get('Step', 0) <= 5]
```

### Generate Selenium Script Instead

Fork the script and modify `generate_pywinauto_script()` to output Selenium commands.

### Create AutoIt Script

Similar approach - convert actions to AutoIt syntax:
```autoit
ControlClick("Notepad", "", "[CLASS:Edit]")
ControlSend("Notepad", "", "[CLASS:Edit]", "Hello World")
```

---

## Related Documentation

- [UI Logging Guide](../UI_LOGGING_GUIDE.md) - Complete logging documentation
- [Performance Optimization](../PERFORMANCE_OPTIMIZATION_GUIDE.md) - Optimize UFO execution
- [Config Examples](../config_examples/) - Ready-to-use configurations

---

## Contributing

Have improvements or additional extraction tools? Submit a PR!

Suggestions:
- Selenium/Playwright script generator
- AutoIt script generator
- Robot Framework test generator
- CSV export for manual test cases
- Visual regression test generator
