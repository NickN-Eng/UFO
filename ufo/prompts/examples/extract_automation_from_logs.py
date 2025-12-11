"""
UFO Log Extraction Tool
Converts UFO execution logs to traditional automation scripts (pywinauto)

Usage:
    python extract_automation_from_logs.py <log_folder_path>

Example:
    python extract_automation_from_logs.py logs/notepad_task_20250101_120000
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


class UFOLogExtractor:
    """Extract automation details from UFO logs"""

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.steps = []
        self.ui_trees = {}
        self.application = None

    def load_logs(self):
        """Load all log files"""
        print(f"Loading logs from: {self.log_path}")

        # Load response.log (action history)
        response_log = self.log_path / "response.log"
        if response_log.exists():
            with open(response_log, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        step = json.loads(line)
                        self.steps.append(step)
                        if not self.application and 'Application' in step:
                            self.application = step['Application']
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse line (may be compressed): {e}")
                        continue

        print(f"Loaded {len(self.steps)} steps")

        # Load UI trees
        ui_tree_dir = self.log_path / "ui_trees"
        if ui_tree_dir.exists():
            for tree_file in sorted(ui_tree_dir.glob("ui_tree_step*.json")):
                step_num = int(tree_file.stem.replace("ui_tree_step", ""))
                with open(tree_file, 'r', encoding='utf-8') as f:
                    self.ui_trees[step_num] = json.load(f)

        print(f"Loaded {len(self.ui_trees)} UI trees")

    def print_summary(self):
        """Print human-readable summary of automation"""
        print("\n" + "=" * 80)
        print("AUTOMATION SUMMARY")
        print("=" * 80)
        print(f"Application: {self.application}")
        print(f"Total Steps: {len(self.steps)}")
        print()

        for step in self.steps:
            step_num = step.get('Step', 0)
            subtask = step.get('Subtask', 'N/A')
            actions = step.get('Action', [])

            print(f"\n--- Step {step_num}: {subtask} ---")

            for action in actions:
                func = action.get('Function', 'unknown')
                args = action.get('Args', {})
                control_text = action.get('ControlText', '')
                control_label = action.get('ControlLabel', '')
                status = action.get('Status', 'N/A')

                print(f"  Action: {func}")
                print(f"  Arguments: {args}")
                print(f"  Control: {control_text} (Label: {control_label})")
                print(f"  Status: {status}")

            # Print control details
            control_logs = step.get('ControlLog', {})
            if control_logs:
                print(f"  Available Controls:")
                for label, ctrl in control_logs.items():
                    ctrl_name = ctrl.get('control_name', '')
                    ctrl_type = ctrl.get('control_type', '')
                    auto_id = ctrl.get('control_automation_id', 'N/A')
                    coords = ctrl.get('control_coordinates', {})

                    print(f"    [{label}] {ctrl_type}: '{ctrl_name}'")
                    print(f"        AutoID: {auto_id}")
                    print(f"        Coords: ({coords.get('left')}, {coords.get('top')}) - "
                          f"({coords.get('right')}, {coords.get('bottom')})")

    def find_control_in_tree(self, tree: Dict, label: str, control_text: str = None) -> Dict:
        """Find control details in UI tree"""
        def search(node):
            # Match by label (if it's in the node ID)
            if label and label in node.get('id', ''):
                return node

            # Match by name/text
            if control_text and node.get('name') == control_text:
                return node

            # Search children
            for child in node.get('children', []):
                result = search(child)
                if result:
                    return result

            return None

        return search(tree)

    def generate_pywinauto_script(self) -> str:
        """Generate pywinauto Python script"""
        lines = [
            '"""',
            'Auto-generated automation script from UFO logs',
            f'Source: {self.log_path}',
            '"""',
            '',
            'from pywinauto import Application',
            'from pywinauto.keyboard import send_keys',
            'import time',
            '',
            '# Launch application',
        ]

        if self.application:
            app_name = self.application.lower()
            lines.append(f"app = Application(backend='uia').start('{app_name}')")
        else:
            lines.append("# TODO: Specify application to launch")
            lines.append("app = Application(backend='uia').start('notepad.exe')")

        lines.extend([
            '',
            '# Get main window',
            "main_window = app.window(title_re='.*')",
            '',
        ])

        # Generate code for each step
        for step in self.steps:
            step_num = step.get('Step', 0)
            subtask = step.get('Subtask', 'N/A')
            actions = step.get('Action', [])
            control_logs = step.get('ControlLog', {})

            lines.append(f"# Step {step_num}: {subtask}")

            for action in actions:
                func = action.get('Function', 'unknown')
                args = action.get('Args', {})
                control_label = action.get('ControlLabel', '')
                control_text = action.get('ControlText', '')

                # Get control details from logs
                control_info = control_logs.get(control_label, {})
                auto_id = control_info.get('control_automation_id', '')
                ctrl_type = control_info.get('control_type', 'Unknown')
                coords = control_info.get('control_coordinates', {})

                # Generate appropriate code
                if func == 'click_input':
                    if auto_id:
                        lines.append(f"# Click on {ctrl_type}: '{control_text}'")
                        lines.append(f"ctrl = main_window.child_window(auto_id='{auto_id}', "
                                   f"control_type='{ctrl_type}')")
                        lines.append(f"ctrl.click_input()")
                    elif coords:
                        lines.append(f"# Click at coordinates for: '{control_text}'")
                        x = (coords.get('left', 0) + coords.get('right', 0)) // 2
                        y = (coords.get('top', 0) + coords.get('bottom', 0)) // 2
                        lines.append(f"main_window.click_input(coords=({x}, {y}))")
                    else:
                        lines.append(f"# TODO: Click on '{control_text}'")

                elif func == 'type_keys' or func == 'set_edit_text':
                    text = args.get('text', '')
                    if auto_id:
                        lines.append(f"# Type text into {ctrl_type}")
                        lines.append(f"ctrl = main_window.child_window(auto_id='{auto_id}', "
                                   f"control_type='{ctrl_type}')")
                        if func == 'type_keys':
                            lines.append(f"ctrl.type_keys('{text}')")
                        else:
                            lines.append(f"ctrl.set_edit_text('{text}')")
                    else:
                        lines.append(f"# Type: '{text}'")
                        lines.append(f"send_keys('{text}')")

                elif func == 'texts':
                    lines.append(f"# Get text from {ctrl_type}")
                    if auto_id:
                        lines.append(f"ctrl = main_window.child_window(auto_id='{auto_id}', "
                                   f"control_type='{ctrl_type}')")
                        lines.append(f"text = ctrl.window_text()")
                        lines.append(f"print(f'Retrieved text: {{text}}')")
                    else:
                        lines.append(f"# TODO: Get text from '{control_text}'")

                elif func == 'wheel_mouse_input':
                    wheel_dist = args.get('wheel_dist', 0)
                    lines.append(f"# Scroll mouse wheel")
                    lines.append(f"main_window.wheel_mouse_input(wheel_dist={wheel_dist})")

                elif func == 'annotation':
                    # This is just for annotation, skip
                    lines.append(f"# Annotation: {args}")

                else:
                    lines.append(f"# TODO: {func}({args})")

                lines.append('')

            lines.append('time.sleep(0.5)  # Wait for UI to update')
            lines.append('')

        lines.append('print("Automation complete!")')

        return '\n'.join(lines)

    def generate_control_map(self) -> Dict[str, List[Dict]]:
        """Generate a map of all controls found"""
        control_map = {}

        for step in self.steps:
            step_num = step.get('Step', 0)
            control_logs = step.get('ControlLog', {})

            for label, ctrl in control_logs.items():
                ctrl_type = ctrl.get('control_type', 'Unknown')
                ctrl_name = ctrl.get('control_name', '')

                if ctrl_type not in control_map:
                    control_map[ctrl_type] = []

                control_map[ctrl_type].append({
                    'step': step_num,
                    'label': label,
                    'name': ctrl_name,
                    'automation_id': ctrl.get('control_automation_id', ''),
                    'class': ctrl.get('control_class', ''),
                    'coordinates': ctrl.get('control_coordinates', {})
                })

        return control_map

    def print_control_map(self):
        """Print all controls organized by type"""
        control_map = self.generate_control_map()

        print("\n" + "=" * 80)
        print("CONTROL MAP (All Detected Controls)")
        print("=" * 80)

        for ctrl_type, controls in sorted(control_map.items()):
            print(f"\n{ctrl_type} ({len(controls)} found):")
            seen = set()
            for ctrl in controls:
                key = (ctrl['automation_id'], ctrl['name'])
                if key in seen:
                    continue
                seen.add(key)

                print(f"  - '{ctrl['name']}'")
                print(f"    AutoID: {ctrl['automation_id']}")
                print(f"    Class: {ctrl['class']}")
                coords = ctrl['coordinates']
                print(f"    Coords: ({coords.get('left')}, {coords.get('top')}) - "
                      f"({coords.get('right')}, {coords.get('bottom')})")

    def export_to_json(self, output_file: str):
        """Export all data to JSON"""
        data = {
            'application': self.application,
            'total_steps': len(self.steps),
            'steps': self.steps,
            'ui_trees': self.ui_trees,
            'control_map': self.generate_control_map()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nExported to: {output_file}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python extract_automation_from_logs.py <log_folder_path>")
        print("\nExample:")
        print("  python extract_automation_from_logs.py logs/notepad_task_20250101_120000")
        sys.exit(1)

    log_path = sys.argv[1]

    if not os.path.exists(log_path):
        print(f"Error: Log path does not exist: {log_path}")
        sys.exit(1)

    # Create extractor
    extractor = UFOLogExtractor(log_path)

    # Load logs
    extractor.load_logs()

    if not extractor.steps:
        print("Error: No steps found in logs. Make sure response.log exists.")
        sys.exit(1)

    # Print summary
    extractor.print_summary()

    # Print control map
    extractor.print_control_map()

    # Generate pywinauto script
    script = extractor.generate_pywinauto_script()

    # Save script
    output_script = Path(log_path) / "generated_automation.py"
    with open(output_script, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"\n" + "=" * 80)
    print(f"Generated pywinauto script: {output_script}")
    print("=" * 80)
    print("\nPreview:")
    print(script[:1000])
    if len(script) > 1000:
        print("\n... (truncated, see full file)")

    # Export JSON
    output_json = Path(log_path) / "automation_data.json"
    extractor.export_to_json(output_json)

    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  1. {output_script} - Python automation script")
    print(f"  2. {output_json} - Complete automation data (JSON)")
    print("\nNext steps:")
    print("  1. Review the generated script")
    print("  2. Test with: python generated_automation.py")
    print("  3. Adjust automation IDs if needed")


if __name__ == "__main__":
    main()
