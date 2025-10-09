"""
Sync command implementation.

Handles reading editor-specific markdown files and updating/creating
PrompTrek configuration from them.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
import yaml

from ...adapters import registry
from ...core.exceptions import PrompTrekError, UPFParsingError
from ...core.models import Instructions, ProjectContext, PromptMetadata, UniversalPrompt
from ...core.parser import UPFParser


def sync_command(
    ctx: click.Context,
    source_dir: Path,
    editor: str,
    output_file: Optional[Path],
    dry_run: bool,
    force: bool,
) -> None:
    """
    Sync editor-specific files to PrompTrek configuration.

    Args:
        ctx: Click context
        source_dir: Directory containing editor files to read
        editor: Editor type to sync from
        output_file: Output PrompTrek file (defaults to project.promptrek.yaml)
        dry_run: Show what would be done without making changes
        force: Overwrite existing files without confirmation
    """
    if output_file is None:
        output_file = Path("project.promptrek.yaml")

    # Get the adapter for the specified editor
    try:
        adapter = registry.get(editor)
    except Exception:
        raise PrompTrekError(f"Unsupported editor: {editor}")

    # Check if adapter supports reverse parsing
    if not adapter.supports_bidirectional_sync():
        raise PrompTrekError(f"Editor '{editor}' does not support syncing from files")

    # Parse files from the source directory
    try:
        parsed_prompt = adapter.parse_files(source_dir)
    except Exception as e:
        raise PrompTrekError(f"Failed to parse {editor} files: {e}")

    # Handle existing PrompTrek file
    existing_prompt = None
    if output_file.exists():
        if not force and not dry_run:
            if not click.confirm(f"File {output_file} exists. Update it?"):
                click.echo("Sync cancelled.")
                return

        try:
            parser = UPFParser()
            existing_prompt = parser.parse_file(output_file)
        except Exception as e:
            click.echo(f"Warning: Could not parse existing file {output_file}: {e}")

    # Merge with existing configuration if present
    if existing_prompt:
        merged_prompt = _merge_prompts(existing_prompt, parsed_prompt, editor)
    else:
        merged_prompt = parsed_prompt

    # Write the result
    if dry_run:
        click.echo(f"🔍 Dry run mode - would write to: {output_file}")
        _preview_prompt(merged_prompt)
    else:
        _write_prompt_file(merged_prompt, output_file)
        click.echo(f"✅ Synced {editor} configuration to: {output_file}")


def _merge_metadata(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge metadata intelligently, preserving user-defined data.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated metadata dictionary
    """
    if not parsed.metadata:
        return existing_data

    metadata = existing_data.get("metadata", {})

    # Prefer existing user-defined metadata over auto-generated
    # Only update if existing is empty or if parsed is from a real source
    if (
        parsed.metadata.title
        and not metadata.get("title")
        and parsed.metadata.author != "PrompTrek Sync"
    ):
        metadata["title"] = parsed.metadata.title

    if (
        parsed.metadata.description
        and not metadata.get("description")
        and parsed.metadata.author != "PrompTrek Sync"
    ):
        metadata["description"] = parsed.metadata.description

    # Update timestamp from parsed data or current time
    if parsed.metadata.updated:
        metadata["updated"] = parsed.metadata.updated
    else:
        metadata["updated"] = datetime.now().isoformat()[:10]  # YYYY-MM-DD

    existing_data["metadata"] = metadata
    return existing_data


def _merge_instructions(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge instructions intelligently, avoiding duplicates.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated configuration with merged instructions
    """
    if not parsed.instructions:
        return existing_data

    if "instructions" not in existing_data:
        existing_data["instructions"] = {}

    parsed_instructions = parsed.instructions.model_dump(exclude_none=True)
    existing_instructions = existing_data.get("instructions", {})

    for category, new_instructions in parsed_instructions.items():
        if not new_instructions:
            continue

        if category not in existing_instructions:
            # New category - add all instructions
            existing_instructions[category] = list(new_instructions)
        else:
            # Merge with existing, preserving order and avoiding duplicates
            existing_list = existing_instructions[category] or []
            existing_set = set(existing_list)

            # Add new instructions that don't exist
            for instruction in new_instructions:
                if instruction not in existing_set:
                    existing_list.append(instruction)
                    existing_set.add(instruction)

            existing_instructions[category] = existing_list

    existing_data["instructions"] = existing_instructions
    return existing_data


def _merge_context(existing_data: dict, parsed: UniversalPrompt) -> dict:
    """
    Merge context information intelligently.

    Args:
        existing_data: Existing configuration data
        parsed: Newly parsed data from editor files

    Returns:
        Updated configuration with merged context
    """
    if not parsed.context:
        return existing_data

    existing_context = existing_data.get("context", {})
    parsed_context = parsed.context.model_dump(exclude_none=True)

    # Merge technologies additively
    if "technologies" in parsed_context:
        existing_techs = set(existing_context.get("technologies", []))
        new_techs = set(parsed_context["technologies"])
        existing_context["technologies"] = sorted(existing_techs | new_techs)

    # Update project type if not set or if parsed is more specific
    if parsed_context.get("project_type") and (
        not existing_context.get("project_type")
        or existing_context.get("project_type") == "application"
    ):
        existing_context["project_type"] = parsed_context["project_type"]

    # Update description if parsed has better info
    if parsed_context.get("description") and not existing_context.get("description"):
        existing_context["description"] = parsed_context["description"]

    existing_data["context"] = existing_context
    return existing_data


def _merge_prompts(
    existing: UniversalPrompt, parsed: UniversalPrompt, editor: str
) -> UniversalPrompt:
    """
    Intelligently merge parsed prompt data with existing PrompTrek configuration.

    Merge Strategy:
    1. Preserve user-defined metadata (title, description) unless empty
    2. Merge instructions additively, avoiding duplicates
    3. Update context info with parsed data
    4. Mark sync timestamp and editor

    Args:
        existing: Existing PrompTrek configuration
        parsed: Newly parsed data from editor files
        editor: Editor name being synced

    Returns:
        Merged UniversalPrompt
    """
    # Start with existing configuration
    merged_data = existing.model_dump(exclude_none=True)

    # Use helper functions to merge each section
    merged_data = _merge_metadata(merged_data, parsed)
    merged_data = _merge_instructions(merged_data, parsed)
    merged_data = _merge_context(merged_data, parsed)

    # Ensure the target editor is included in targets
    targets = merged_data.get("targets", [])
    if not targets:
        targets = [editor]
    elif editor not in targets:
        targets.append(editor)
    merged_data["targets"] = targets

    return UniversalPrompt.model_validate(merged_data)


def _preview_prompt(prompt: UniversalPrompt) -> None:
    """Preview the prompt that would be written."""
    click.echo("📄 Preview of configuration that would be written:")
    click.echo(f"  Title: {prompt.metadata.title}")
    click.echo(f"  Description: {prompt.metadata.description}")

    if prompt.instructions:
        instructions_data = prompt.instructions.model_dump(exclude_none=True)
        for category, instructions in instructions_data.items():
            if instructions:
                click.echo(f"  {category.title()}: {len(instructions)} instructions")


def _write_prompt_file(prompt: UniversalPrompt, output_file: Path) -> None:
    """Write prompt to YAML file."""
    prompt_data = prompt.model_dump(exclude_none=True, by_alias=True)

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(prompt_data, f, default_flow_style=False, sort_keys=False)
