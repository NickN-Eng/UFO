#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Split Bulk JSON Instructions into Individual Files

This script takes a single JSON file containing multiple ETABS instructions
and splits it into individual JSON files (one per task) for use with UFO's
RAG system.

Usage:
    python split_json_instructions.py <input_file> <output_folder>

Example:
    python split_json_instructions.py etabs_bulk_instructions.json C:\ETABS_UFO_Docs

Author: Generated for UFO ETABS Customization
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any


def clean_filename(text: str, max_length: int = 50) -> str:
    """
    Convert a request text into a clean filename.

    Args:
        text: The request text to convert
        max_length: Maximum length of the filename

    Returns:
        Clean filename suitable for filesystem
    """
    # Remove "How to" prefix if present
    text = re.sub(r'^how to\s+', '', text, flags=re.IGNORECASE)

    # Remove question mark
    text = text.replace('?', '')

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and special characters with underscores
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)

    # Trim to max length
    if len(text) > max_length:
        text = text[:max_length].rstrip('_')

    return text


def validate_bulk_json(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate the bulk JSON structure.

    Args:
        data: The parsed JSON data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Root element must be a dictionary"

    if 'instructions' not in data:
        return False, "Missing 'instructions' key in root object"

    if not isinstance(data['instructions'], list):
        return False, "'instructions' must be an array"

    if len(data['instructions']) == 0:
        return False, "'instructions' array is empty"

    # Validate each instruction
    for idx, instruction in enumerate(data['instructions']):
        if not isinstance(instruction, dict):
            return False, f"Instruction {idx} is not a dictionary"

        # Only request and guidance are required (task_id is optional and auto-generated)
        required_fields = ['request', 'guidance']
        for field in required_fields:
            if field not in instruction:
                return False, f"Instruction {idx} missing required field: {field}"

        if not isinstance(instruction['guidance'], list):
            return False, f"Instruction {idx}: 'guidance' must be an array"

    return True, ""


def create_individual_json(instruction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create an individual JSON structure from a bulk instruction.

    Args:
        instruction: Single instruction from bulk file

    Returns:
        Individual JSON structure for UFO
    """
    return {
        "request": instruction['request'],
        "guidance": instruction['guidance']
    }


def split_instructions(
    input_file: str,
    output_folder: str,
    prefix_with_id: bool = True,
    organize_by_category: bool = False
) -> None:
    """
    Split bulk JSON file into individual instruction files.

    Args:
        input_file: Path to the bulk JSON file
        output_folder: Path to the output folder for individual files
        prefix_with_id: Whether to prefix filenames with task_id
        organize_by_category: Whether to create subfolders by category
    """
    print(f"Reading bulk JSON file: {input_file}")

    # Read the bulk JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            bulk_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in file: {e}")
        sys.exit(1)

    # Validate structure
    is_valid, error_msg = validate_bulk_json(bulk_data)
    if not is_valid:
        print(f"ERROR: Invalid bulk JSON structure: {error_msg}")
        sys.exit(1)

    instructions = bulk_data['instructions']
    print(f"Found {len(instructions)} instructions to process")

    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: {output_folder}")

    # Process each instruction
    created_files = []
    skipped_files = []

    for idx, instruction in enumerate(instructions, start=1):
        # Use provided task_id if available, otherwise auto-generate from position
        task_id = instruction.get('task_id', f"{idx:02d}")
        category = instruction.get('category', 'general')
        request = instruction['request']

        # Generate filename
        clean_name = clean_filename(request)
        if prefix_with_id:
            filename = f"{task_id}_{clean_name}.json"
        else:
            filename = f"{clean_name}.json"

        # Determine output path
        if organize_by_category:
            category_path = output_path / category
            category_path.mkdir(exist_ok=True)
            file_path = category_path / filename
        else:
            file_path = output_path / filename

        # Create individual JSON structure
        individual_json = create_individual_json(instruction)

        # Check if file already exists
        if file_path.exists():
            print(f"  [!] SKIPPED (already exists): {file_path.name}")
            skipped_files.append(str(file_path))
            continue

        # Write individual file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(individual_json, f, indent=2, ensure_ascii=False)
            print(f"  [+] Created: {file_path.name}")
            created_files.append(str(file_path))
        except Exception as e:
            print(f"  [X] ERROR writing {file_path.name}: {e}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total instructions: {len(instructions)}")
    print(f"Files created: {len(created_files)}")
    print(f"Files skipped: {len(skipped_files)}")
    print(f"Output location: {output_folder}")

    if created_files:
        print("\n[+] Successfully created files:")
        for file in created_files[:5]:  # Show first 5
            print(f"  - {Path(file).name}")
        if len(created_files) > 5:
            print(f"  ... and {len(created_files) - 5} more")

    if skipped_files:
        print("\n[!] Skipped files (already existed):")
        for file in skipped_files[:3]:  # Show first 3
            print(f"  - {Path(file).name}")
        if len(skipped_files) > 3:
            print(f"  ... and {len(skipped_files) - 3} more")

    print("\n" + "="*60)
    print("Next steps:")
    print("="*60)
    print(f"1. Review the created files in: {output_folder}")
    print(f"2. Create FAISS index:")
    print(f"   python -m learner --app ETABS --docs {output_folder} --format json")
    print(f"3. Test with UFO:")
    print(f"   python -m ufo -r \"your ETABS task here\"")
    print("="*60)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python split_json_instructions.py <input_file> <output_folder>")
        print("\nExample:")
        print("  python split_json_instructions.py etabs_bulk.json C:\\ETABS_UFO_Docs")
        print("\nOptions:")
        print("  --no-prefix       Don't prefix filenames with task_id")
        print("  --organize        Organize files into category subfolders")
        sys.exit(1)

    input_file = sys.argv[1]
    output_folder = sys.argv[2]

    # Parse optional flags
    prefix_with_id = '--no-prefix' not in sys.argv
    organize_by_category = '--organize' in sys.argv

    # Run the split
    split_instructions(
        input_file,
        output_folder,
        prefix_with_id=prefix_with_id,
        organize_by_category=organize_by_category
    )


if __name__ == "__main__":
    main()
