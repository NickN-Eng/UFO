# UI Element Specificity Guide

This guide explains how to write highly specific, actionable instructions for UFO by properly identifying and describing UI elements.

---

## Why Specificity Matters

UFO uses Windows UI Automation to interact with applications. The more specific your instructions:
- ✅ Higher success rate in finding correct UI elements
- ✅ Fewer errors from clicking wrong buttons/menus
- ✅ Better handling of similar-looking elements
- ✅ Clearer documentation for both UFO and human users

---

## UI Element Identification Hierarchy

When describing any UI element, provide information in this priority order:

### 1. **Element Type** (Required)
What kind of UI control is it?

**Common Types:**
- Menu item
- Button
- Dropdown / Combo box
- Text field / Edit box
- Checkbox
- Radio button
- Tab
- List item
- Tree view item

**Example:**
❌ "Click Define"
✅ "Click on the 'Define' **menu**"

### 2. **Element Label** (Required)
The exact text shown to the user

**Rules:**
- Use exact text as it appears in the UI
- Include quotes to make it clear: 'Button Text'
- Case-sensitive when possible
- Include & symbols if present (e.g., "&File" in accelerator keys)

**Example:**
❌ "Click the ok button"
✅ "Click the 'OK' button"

### 3. **Parent Context** (Highly Recommended)
Which window, dialog, or section contains this element?

**Example:**
❌ "Click the 'OK' button"
✅ "In the 'Material Properties' dialog, click the 'OK' button"
✅ BETTER: "At the bottom right of the 'Material Properties' dialog, click the 'OK' button"

### 4. **Visual Cues** (Optional but Helpful)
Icons, colors, position

**Example:**
✅ "Click the 'Add New Material' button (shows a blue plus icon)"
✅ "Click the 'Save' button (green button with disk icon)"
✅ "Locate the 'Material Name' field at the top of the dialog"

### 5. **Example Values** (For Input Fields)
What should users enter?

**Example:**
✅ "Enter '4000' in the 'fc' field (units: psi)"
✅ "Type a material name (e.g., 'C4000' or 'Concrete 4000 psi')"

---

## Element-Specific Guidelines

### Menus

**Bad:**
```
Click Define
Go to Materials
```

**Good:**
```
Click on the 'Define' menu in the top menu bar
From the Define menu dropdown, select 'Materials'
```

**Best:**
```
Click on the 'Define' menu in the top menu bar
Hover over the 'Materials' option in the dropdown menu and click it
Wait for the 'Define Materials' dialog to appear
```

**Template:**
```
Click on the '[Menu Name]' menu in the [location]
From the [Menu Name] menu dropdown, select '[Submenu Item]'
```

### Buttons

**Bad:**
```
Click the button
Press OK
Click add
```

**Good:**
```
Click the 'OK' button
Click the 'Add New Material' button
Click the 'Run Analysis' button in the toolbar
```

**Best:**
```
Click the 'OK' button at the bottom right of the dialog
Click the 'Add New Material' button (typically shows a plus icon)
In the main toolbar, click the 'Run Analysis' button (green play icon)
```

**Template:**
```
[In the [Dialog Name] dialog,] click the '[Button Text]' button [at the [position]] [(visual cue)]
```

### Dropdowns / Combo Boxes

**Bad:**
```
Select Concrete
Choose the type
```

**Good:**
```
Click the 'Material Type' dropdown and select 'Concrete'
From the 'Load Case' dropdown, select 'DEAD'
```

**Best:**
```
Locate the 'Material Type' dropdown menu in the properties section
Click the 'Material Type' dropdown to expand the list of options
From the expanded list, select 'Concrete'
```

**Template:**
```
Click the '[Dropdown Name]' dropdown menu [in the [section]]
From the '[Dropdown Name]' dropdown, select '[Option]'
```

### Text Fields / Edit Boxes

**Bad:**
```
Enter the name
Type 4000
Fill in the value
```

**Good:**
```
In the 'Material Name' field, enter 'C4000'
Enter '4000' in the 'fc' field
Type the section name in the 'Section Name' text box
```

**Best:**
```
Locate the 'Material Name' text field at the top of the dialog
In the 'Material Name' field, type a descriptive name (e.g., 'C4000')
Find the 'fc (compressive strength)' numeric input field in the properties section
Enter the value '4000' in the 'fc' field (units will be psi or MPa depending on model units)
```

**Template:**
```
[Locate/Find] the '[Field Name]' [text field/input box] [in the [section]]
In the '[Field Name]' field, [enter/type] '[value]' [(units: [unit])]
```

### Checkboxes

**Bad:**
```
Check the box
Enable self-weight
```

**Good:**
```
Check the 'Include self-weight' checkbox
Ensure the 'Display results' checkbox is checked
```

**Best:**
```
Locate the 'Include self-weight' checkbox in the load options section
Click the 'Include self-weight' checkbox to check it (a checkmark should appear)
Verify that the 'Display results' checkbox is checked (has a checkmark)
```

**Template:**
```
[Locate] the '[Checkbox Label]' checkbox [in the [section]]
[Check/Uncheck] the '[Checkbox Label]' checkbox
[Ensure/Verify] the '[Checkbox Label]' checkbox is [checked/unchecked]
```

### Radio Buttons

**Bad:**
```
Select Gravity
Choose the option
```

**Good:**
```
Select the 'Gravity' radio button
Click the 'Forces' radio button in the load type section
```

**Best:**
```
In the 'Direction' section, locate the group of radio buttons
Select the 'Gravity' radio button (a filled circle should appear)
Verify that 'Gravity' is selected (should have a filled/selected indicator)
```

**Template:**
```
[In the [section],] select the '[Option]' radio button
Click the '[Option]' radio button [in the [group name]]
```

### Tabs

**Bad:**
```
Go to Reinforcement
Switch tabs
```

**Good:**
```
Click on the 'Reinforcement' tab
Switch to the 'Design' tab
```

**Best:**
```
At the top of the 'Section Properties' dialog, locate the row of tabs
Click on the 'Reinforcement' tab to switch to the reinforcement settings
The tab content will change to show reinforcement options
```

**Template:**
```
[At the [location],] click on the '[Tab Name]' tab
Switch to the '[Tab Name]' tab [to access [functionality]]
```

### Dialogs

**When dialogs open:**

**Bad:**
```
A window opens
A dialog appears
```

**Good:**
```
The 'Define Materials' dialog will open
Wait for the 'Material Properties' dialog to appear
```

**Best:**
```
The 'Define Materials' dialog will open - this is a modal window showing the list of materials
Wait for the 'Material Properties' dialog to fully load (may take a moment for complex models)
You should now see the 'Section Designer' dialog with drawing tools on the left
```

**Template:**
```
The '[Dialog Name]' dialog will [open/appear]
Wait for the '[Dialog Name]' dialog to [fully load/appear on screen]
[Description of what the dialog contains]
```

---

## Common Patterns

### Pattern 1: Menu → Dialog → Action
```
1. Click on the 'Define' menu in the top menu bar
2. From the dropdown, select 'Materials'
3. The 'Define Materials' dialog will open
4. In the 'Define Materials' dialog, click the 'Add New Material' button
5. The 'Material Property Data' dialog will open
6. [Continue with actions in this dialog]
```

### Pattern 2: Fill Form → Save
```
1. Locate the '[Field 1 Name]' text field
2. Enter '[value]' in the '[Field 1 Name]' field
3. Find the '[Field 2 Name]' dropdown
4. Select '[option]' from the '[Field 2 Name]' dropdown
5. Verify all entered values are correct
6. Click the 'OK' button to save and close the dialog
```

### Pattern 3: Select → Assign → Confirm
```
1. Click on the element you want to modify (it should highlight)
2. Click on the 'Assign' menu in the top menu bar
3. Select '[Property Type]' from the dropdown
4. The '[Assignment Dialog]' dialog will open
5. [Configure the assignment]
6. Click 'OK' to apply the assignment to the selected element
```

---

## Context Clarity

### Always Mention Current Context

**Bad - Ambiguous:**
```
Click 'OK'
Enter the name
Select Concrete
```
*Problem: Which OK button? Which name field? From which list?*

**Good - Clear Context:**
```
In the 'Material Properties' dialog, click the 'OK' button
In the 'Section Name' field at the top of the 'Section Data' dialog, enter 'C24x24'
From the 'Material' dropdown in the 'Frame Section' dialog, select 'Concrete'
```

### Nested Dialogs

When dialogs open from other dialogs:

```
1. The 'Define Materials' dialog will open [CONTEXT: First dialog]
2. In the 'Define Materials' dialog, click 'Add New Material'
3. The 'Material Property Data' dialog will open [CONTEXT: Second dialog, child of first]
4. In the 'Material Property Data' dialog, enter properties [CONTEXT: Still in second dialog]
5. Click 'OK' in the 'Material Property Data' dialog [CONTEXT: Explicitly state which dialog's OK]
6. You will return to the 'Define Materials' dialog [CONTEXT: Back to first dialog]
7. Click 'OK' in the 'Define Materials' dialog to close it [CONTEXT: Closing first dialog]
```

---

## Units and Values

### Numeric Fields

Always provide:
1. The value to enter
2. The units (if applicable)
3. Context about unit system if relevant

**Examples:**
```
Enter '4000' in the 'fc' field (units: psi)
Set fc = 4000 psi (note: use 27.6 for MPa if your model uses metric units)
Enter '24' in the 'Depth' field (units: inches in this model)
Type '200000' in the 'E (Modulus of Elasticity)' field (units: ksi)
```

### Text Fields

Provide example values:

```
Enter a descriptive name in the 'Material Name' field (e.g., 'C4000' or 'Concrete 4000 psi')
Type a unique section name (e.g., 'COL-24x24' or 'C24x24')
Enter a load case name (e.g., 'DEAD', 'LIVE', 'WIND-X')
```

---

## Verification Steps

Include verification steps to confirm actions succeeded:

### After Entering Values
```
Verify that '4000' is shown in the 'fc' field
Review all entered values for correctness
```

### After Creating/Adding
```
The new material 'C4000' should now appear in the materials list
Verify that the section appears in the sections list
```

### After Assignment
```
The assigned load should now be visible on the selected beam (shown as arrows or a distributed load symbol)
Check that the element now shows the assigned section properties
```

### After Analysis
```
A message 'Analysis Complete' should appear
Check the status bar at the bottom - it should show 'Analysis Successful'
```

---

## Common Mistakes to Avoid

### ❌ DON'T: Use Vague References
```
Click the button
Select from the list
Enter the value
Click next
```

### ✅ DO: Be Specific
```
Click the 'Add New Material' button in the 'Define Materials' dialog
Select 'Concrete' from the 'Material Type' dropdown list
Enter '4000' in the 'fc (compressive strength)' field (units: psi)
Click the 'Next' button at the bottom right of the wizard
```

### ❌ DON'T: Assume Context
```
Click OK [Problem: Which OK button?]
Enter the name [Problem: Which name field?]
```

### ✅ DO: Provide Context
```
Click the 'OK' button in the 'Material Properties' dialog
Enter 'C4000' in the 'Material Name' text field at the top of the dialog
```

### ❌ DON'T: Skip Intermediate Steps
```
Define a material
Add concrete properties
Save
```

### ✅ DO: Include All Steps
```
Click on the 'Define' menu in the top menu bar
Select 'Materials' from the dropdown menu
The 'Define Materials' dialog will open
Click the 'Add New Material' button
The 'Material Property Data' dialog will open
Click the 'Material Type' dropdown and select 'Concrete'
Enter material properties as needed
Click 'OK' to save the material
Click 'OK' to close the 'Define Materials' dialog
```

---

## Quick Reference Template

Use this template for any UI action:

```
[Location/Context] + [Action] + [Element Type] + [Element Label] + [Details]
```

**Examples:**
```
[In the 'Material Properties' dialog,] [click] [the 'OK' button] [at the bottom right]

[At the top of the dialog,] [locate] [the 'Section Name' text field]

[From the 'Material Type' dropdown menu,] [select] ['Concrete']

[In the main toolbar,] [click] [the 'Run Analysis' button] [(green play icon)]
```

---

## Summary Checklist

For every UI action in your guidance, ensure you've specified:

- [ ] Element type (menu, button, dropdown, field, checkbox, etc.)
- [ ] Exact element label (text shown to user)
- [ ] Parent context (which dialog/window)
- [ ] Example values (for input fields)
- [ ] Units (for numeric fields)
- [ ] Visual cues (if helpful - icons, colors, position)
- [ ] Expected result (dialog opens, value appears, etc.)

---

## Impact on UFO Performance

**Low Specificity (40-50% success rate):**
```
"Click Define"
"Add material"
"Enter properties"
```

**Medium Specificity (60-70% success rate):**
```
"Click the Define menu"
"Click Add New Material button"
"Enter 4000 in the fc field"
```

**High Specificity (80-90% success rate):**
```
"Click on the 'Define' menu in the top menu bar"
"In the 'Define Materials' dialog, click the 'Add New Material' button"
"In the 'Material Property Data' dialog, enter '4000' in the 'fc (compressive strength)' field (units: psi)"
```

The more specific you are, the better UFO performs!
