import os
import datetime
import platform
import json
import subprocess
from pathlib import Path


def get_directory_structure(start_path, ignore_patterns=None):
    """Generate a nested directory structure as a string with clear root display.

    Uses git check-ignore for filtering when inside a git repo, otherwise
    falls back to a sensible default ignore set.
    """
    cwd = Path(start_path).resolve()
    use_git = is_git_repo(str(cwd))

    project_name = os.path.basename(cwd) or "root"
    structure = f"Current Working Directory Structure:\n- {cwd}/ (THIS IS THE CURRENT WORKING DIRECTORY)\n"

    dir_structure = []

    for root, dirs, files in os.walk(cwd, topdown=True):
        all_entries = dirs + files

        if use_git:
            ignored = get_git_ignored_set(root, all_entries)
            ignored.add('.git')  # git check-ignore never flags .git itself
        else:
            ignored = {e for e in all_entries if _matches_default_ignore(e)}

        # Prune ignored directories in-place so os.walk doesn't descend
        dirs[:] = [d for d in dirs if d not in ignored]

        level = root.replace(str(cwd), '').count(os.sep)
        indent = '  ' * (level + 1)
        rel_path = os.path.relpath(root, start_path)

        if rel_path != '.':
            path_parts = rel_path.split(os.sep)
            dir_name = path_parts[-1]
            dir_structure.append(f"{indent}- {dir_name}/")

        sub_indent = '  ' * (level + 2)
        for file in sorted(files):
            if file in ignored:
                continue
            dir_structure.append(f"{sub_indent}- {file}")

    return "".join([structure] + [f"{line}\n" for line in dir_structure])


# Default ignore set for non-git directories
DEFAULT_IGNORE = {
    '.venv', 'venv', '.env', '__pycache__', 'node_modules',
    'dist', 'build', '.git', '.tox', '.mypy_cache', '.pytest_cache',
    '.ruff_cache', '.coverage', '.idea', '.vscode',
}

DEFAULT_IGNORE_EXTENSIONS = {'.pyc', '.egg-info'}


def get_git_ignored_set(cwd, items):
    """Batch-check which items are git-ignored using `git check-ignore --stdin`.

    Args:
        cwd: The working directory (must be inside a git repo).
        items: List of filenames/directory names to check.

    Returns:
        A set of item names that are git-ignored. Empty set on any error.
    """
    if not items:
        return set()
    try:
        input_text = "\n".join(items)
        result = subprocess.run(
            ["git", "-C", cwd, "check-ignore", "--stdin"],
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )
        # git check-ignore prints one ignored path per line (exit code 0 = some ignored, 1 = none ignored)
        return set(line.strip() for line in result.stdout.splitlines() if line.strip())
    except Exception:
        return set()


def _matches_default_ignore(name):
    """Check if a filename matches the default ignore rules (for non-git repos)."""
    if name in DEFAULT_IGNORE:
        return True
    if name.startswith('.'):
        return True
    if any(name.endswith(ext) for ext in DEFAULT_IGNORE_EXTENSIONS):
        return True
    return False


def is_git_repo(path):
    """Check if the given path is a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def get_system_prompt(cwd=None):
    """Generate the system prompt with dynamic values filled in."""
    if cwd is None:
        cwd = os.getcwd()

    # The system message template is now in the same directory as this file
    template_path = os.path.join(os.path.dirname(__file__), 'system_message.txt')

    try:
        # Explicitly specify UTF-8 encoding to handle special characters
        with open(template_path, 'r', encoding='utf-8') as f:
            system_message = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find system_message.txt at {template_path}")
    except UnicodeDecodeError:
        # If UTF-8 fails, try with error handling
        try:
            with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
                system_message = f.read()
        except Exception as e:
            raise RuntimeError(f"Could not read system_message.txt: {e}")

    # Get current date in format M/D/YYYY (Windows-compatible)
    today = datetime.datetime.now()
    if platform.system() == 'Windows':
        date_format = f"{today.month}/{today.day}/{today.year}"
    else:
        date_format = today.strftime("%-m/%-d/%Y")

    # Check if directory is a git repo
    is_repo = is_git_repo(cwd)

    # Replace placeholders in the template with actual values
    # system_message = system_message.replace("{working_directory}", cwd)
    system_message = system_message.replace("{is_git_repo}", "Yes" if is_repo else "No")
    system_message = system_message.replace("{platform}", platform.system().lower())
    system_message = system_message.replace("{date}", date_format)
    system_message = system_message.replace("{model}", "gemini-2.5-pro")

    # Remove the directory structure placeholder entirely
    system_message = system_message.replace("{directory_structure}", "")

    # Add working directory message with ls output
    ls_output = get_simple_directory_listing(cwd)
    working_dir_message = f"\nWe are now in the {cwd} working directory.\nCurrent directory contents: {ls_output}\n"
    system_message = system_message + working_dir_message

    # Add git status if it's a git repository
    if is_repo:
        git_status = get_git_status(cwd)
        system_message = system_message + f"\n<context name=\"gitStatus\">{git_status}</context>\n"

    return system_message


def get_simple_directory_listing(cwd):
    """Get a simple, non-recursive directory listing similar to 'ls' command.

    Filters out gitignored entries when inside a git repo, or applies a
    sensible default ignore set otherwise.
    """
    try:
        raw_items = sorted(os.listdir(cwd))

        if is_git_repo(cwd):
            ignored = get_git_ignored_set(cwd, raw_items)
            ignored.add('.git')  # git check-ignore never flags .git itself
            filtered = [i for i in raw_items if i not in ignored]
        else:
            filtered = [i for i in raw_items if not _matches_default_ignore(i)]

        items = []
        for item in filtered:
            item_path = os.path.join(cwd, item)
            if os.path.isdir(item_path):
                items.append(f"{item}/")
            else:
                items.append(item)
        return "  ".join(items) if items else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def get_git_status(cwd):
    """Get git status information for the context."""
    try:
        # Get current branch
        branch_cmd = ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"]
        branch = subprocess.run(branch_cmd, capture_output=True, text=True, check=False).stdout.strip()

        # Get remote main branch
        main_branch_cmd = ["git", "-C", cwd, "remote", "show", "origin"]
        main_output = subprocess.run(main_branch_cmd, capture_output=True, text=True, check=False).stdout
        main_branch = "main"  # Default
        for line in main_output.splitlines():
            if "HEAD branch" in line:
                main_branch = line.split(":")[-1].strip()

        # Get status
        status_cmd = ["git", "-C", cwd, "status", "--porcelain"]
        status_output = subprocess.run(status_cmd, capture_output=True, text=True, check=False).stdout

        if status_output.strip():
            status_lines = status_output.strip().split("\n")
            status = "\n".join(status_lines)
        else:
            status = "(clean)"

        # Get recent commits
        log_cmd = ["git", "-C", cwd, "log", "--oneline", "--max-count=5"]
        log_output = subprocess.run(log_cmd, capture_output=True, text=True, check=False).stdout.strip()

        git_status_text = f"""This is the git status at the start of the conversation. Note that this status is a snapshot in time, and will not update during the conversation.
Current branch: {branch}

Main branch (you will usually use this for PRs): {main_branch}

Status:
{status}

Recent commits:
{log_output}"""
        return git_status_text
    except Exception as e:
        return f"Error getting git status: {str(e)}"
