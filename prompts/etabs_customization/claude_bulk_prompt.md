# Claude Prompt: ETABS Instruction Generator

Copy and paste this prompt directly into Claude to generate comprehensive ETABS documentation.

---

## Prompt

```
I need you to generate comprehensive JSON documentation for UFO (UI-Focused Agent) to automate ETABS structural engineering software tasks.

OUTPUT FORMAT:
{
  "application": "ETABS",
  "version": "v20+",
  "instructions": [
    {
      "category": "modeling",
      "request": "How to [accomplish task]?",
      "guidance": [
        "Step 1: Specific action with UI element details",
        "Step 2: Next action with dialog/button names",
        "Step 3: Continue with field names and values"
      ]
    },
    {
      "category": "materials",
      "request": "How to [accomplish next task]?",
      "guidance": [...]
    }
  ]
}

TASKS TO DOCUMENT:

Prefer use of menu items rather than toolbars because toolbars can change

- Save
- Save as (given a full filepath)
- Open an existing model from a full filepath
- Show properties (via Define menu) for:
   - Materials
   - Slab sections
   - Wall sections
- Set view
   - Set plan view (by level)
   - Set 3d view
- Display
   - Undeformed shape
   - Load assigns (for a given case, show/hide values)
      - Joint
      - Frame
      - Shell
   - Deformed shape (for a given case or combo)
   - Force diagrams (and provide details of display parameter settings and how to change them):
      - Reactions
      - Frame forces
      - Shell forces

CRITICAL: UI ELEMENT SPECIFICITY REQUIREMENTS

For every action in the guidance, you MUST specify the EXACT UI element type and label:

MENU ITEMS:
❌ BAD: "Click on Define"
✅ GOOD: "Click on the 'Define' menu in the top menu bar"

SUBMENUS:
❌ BAD: "Select Materials"
✅ GOOD: "Hover over 'Materials' and click it from the dropdown menu"
✅ BETTER: "From the Define menu dropdown, select 'Materials'"

DIALOGS:
❌ BAD: "A dialog opens"
✅ GOOD: "The 'Define Materials' dialog will open"
✅ BETTER: "Wait for the 'Define Materials' dialog to appear"

BUTTONS:
❌ BAD: "Click the button"
✅ GOOD: "Click the 'OK' button at the bottom right"
✅ BETTER: "Click the 'Add New Material' button (usually a blue plus icon)"

DROPDOWNS/COMBO BOXES:
❌ BAD: "Select material type"
✅ GOOD: "Click the 'Material Type' dropdown and select 'Concrete'"
✅ BETTER: "From the 'Material Type' dropdown list, select 'Concrete'"

TEXT FIELDS/EDIT BOXES:
❌ BAD: "Enter the name"
✅ GOOD: "In the 'Material Name' text field, enter a name (e.g., 'C4000')"
✅ BETTER: "Locate the 'Material Name' edit box and type 'C4000'"

NUMERIC FIELDS:
❌ BAD: "Set the value"
✅ GOOD: "In the 'fc (compressive strength)' field, enter '4000' (units: psi)"
✅ BETTER: "Set fc = 4000 psi in the compressive strength input field"

CHECKBOXES:
✅ GOOD: "Check the 'Include self-weight' checkbox"
✅ BETTER: "Ensure the 'Include self-weight' checkbox is checked (should have a checkmark)"

RADIO BUTTONS:
✅ GOOD: "Select the 'Gravity' radio button"
✅ BETTER: "Click the 'Gravity' option (radio button) in the direction section"

TABS:
✅ GOOD: "Click on the 'Reinforcement' tab"
✅ BETTER: "Switch to the 'Reinforcement' tab at the top of the dialog"

UI ELEMENT IDENTIFICATION HIERARCHY:

When describing a UI element, provide this information in order of priority:

1. ELEMENT TYPE (menu, button, dropdown, field, checkbox, tab)
2. ELEMENT LABEL (exact text shown to user)
3. PARENT CONTEXT (which dialog/window/section it's in)
4. VISUAL CUES (color, icon, position) if helpful
5. EXAMPLE VALUES (for fields that require input)

Example of EXCELLENT guidance step:
"In the 'Material Property Data' dialog, locate the 'Compressive Strength (fc)' numeric input field in the 'Concrete Properties' section, and enter the value '4000' (units will be psi or MPa depending on your model units)"

CATEGORIES:
Choose from: modeling, materials, sections, loads, analysis, design, results

REQUEST FORMAT:
Start with "How to..." and describe the user's goal in natural language

GUIDANCE FORMAT:
- Array of step-by-step instructions
- One clear action per step
- Be specific about EVERY UI element (type + label)
- Include parent context (which dialog/window)
- Provide example values where helpful
- Mention units when entering numeric values
- Include waiting/verification steps

DETAILED EXAMPLE:

{
  "category": "materials",
  "request": "How to define a new concrete material in ETABS?",
  "guidance": [
    "Click on the 'Define' menu in the top menu bar",
    "From the dropdown menu, select 'Materials' (this will open a new dialog)",
    "Wait for the 'Define Materials' dialog to appear on screen",
    "In the 'Define Materials' dialog, click the 'Add New Material' button (typically shows a plus icon)",
    "A new 'Material Property Data' dialog will open",
    "In the 'Material Property Data' dialog, click the 'Material Type' dropdown menu",
    "From the 'Material Type' dropdown, select 'Concrete' from the list",
    "Locate the 'Material Name' text field near the top of the dialog",
    "In the 'Material Name' field, type a descriptive name for your material (example: 'C4000' or 'Concrete 4000 psi')",
    "Find the 'Compressive Strength (fc)' numeric input field in the properties section",
    "Enter the compressive strength value in the 'fc' field (example: '4000' for 4000 psi, or '27.6' for 27.6 MPa)",
    "Review the 'Modulus of Elasticity (Ec)' field - ETABS typically auto-calculates this, but you can override if needed",
    "Verify all entered values are correct",
    "Click the 'OK' button at the bottom right of the 'Material Property Data' dialog to save the material",
    "You will return to the 'Define Materials' dialog - the new material should now appear in the materials list",
    "Click the 'OK' button in the 'Define Materials' dialog to close it and return to the main model window"
  ]
}

IMPORTANT NOTES:

1. NEVER use vague terms like "the button" or "the field" - ALWAYS specify which button/field
2. ALWAYS mention the dialog name when actions occur in a dialog
3. For nested menus, show the full path: Menu → Submenu → Action
4. When a dialog opens, explicitly state: "The [Dialog Name] dialog will open"
5. Include verification steps: "Verify that..." or "Ensure that..."
6. Provide example values in parentheses: (e.g., 'C4000')
7. Mention units for numeric values: (4000 psi) or (units: psi)
8. Describe visual cues if helpful: (usually a blue plus icon)
9. For sequential dialogs, clarify which dialog you're currently in

Generate the complete JSON for all 10 tasks following these requirements. Ensure the JSON is valid and properly formatted.
```

---

## Usage

1. **Copy** the entire prompt above (from ``` to ```)
2. **Customize** the task list if needed (add/remove/modify tasks)
3. **Paste** into Claude
4. **Save** Claude's response as `etabs_bulk_instructions.json`
5. **Split** using the script: `python split_json_instructions.py etabs_bulk_instructions.json C:\ETABS_UFO_Docs`

---

## Notes

- **No task_id required**: The split script will automatically number files sequentially
- **Category is optional**: Only used for organization with `--organize` flag
- **Focus on UI specificity**: The more specific you are about UI elements, the better UFO performs
- **Include context**: Always mention which dialog/window actions occur in
- **Provide examples**: Example values help users understand what to enter

---

## Quick Customization

To add more tasks, append to the TASKS TO DOCUMENT section:

```
11. Define slab section
    - Category: sections
    - Include: Slab type (shell/membrane), thickness, material

12. Assign frame releases
    - Category: modeling
    - Include: Release types (moment/shear), end conditions

13. Define load combinations
    - Category: loads
    - Include: Combination types, load factors, code requirements
```
