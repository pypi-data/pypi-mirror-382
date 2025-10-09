import sys
import tempfile
import subprocess
import os

from .utils import check_dependencies, run_command
from .commit import generate_commit_message


VALID_TYPES = ["feat", "fix", "refactor", "style", "test", "docs", "build", "ops", "chore", "revert"]


def get_commit_type():
    """Prompt user for commit type."""
    print("Select commit type (feat, fix, refactor, style, test, docs, build, ops, chore, revert):")
    commit_type = input().strip()
    if commit_type not in VALID_TYPES:
        print(f"Invalid commit type. Please use one of: {', '.join(VALID_TYPES)}.")
        sys.exit(1)
    return commit_type


def get_scope():
    """Prompt user for optional scope."""
    print("Enter scope (optional, max 20 characters, press Enter to skip):")
    scope = input().strip()
    if len(scope) > 20:
        print("Error: Scope must be 20 characters or less.")
        sys.exit(1)
    return scope


def edit_commit_message(message):
    """Open Vim to edit commit message."""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        temp_file.write(message)
        temp_file_path = temp_file.name

    try:
        subprocess.run(['vim', temp_file_path], check=True)
        
        with open(temp_file_path, 'r') as temp_file:
            edited_message = temp_file.read().strip()
        
        os.unlink(temp_file_path)
        
        if not edited_message:
            print("Commit message cannot be empty.")
            return None
        
        return edited_message
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to open Vim for editing: {e}")
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        sys.exit(1)


def commit_changes(message):
    """Commit changes with the given message."""
    try:
        run_command(f'git commit -m "{message}"')
        print("Changes committed successfully!")
        return True
    except SystemExit:
        print("Commit failed. Please check your changes and try again.")
        return False


def interactive_commit_loop(commit_type, scope):
    """Interactive loop for accepting, editing, or regenerating commit message."""
    commit_message = generate_commit_message(commit_type, scope)
    
    while True:
        print("\nProposed commit message:")
        print(commit_message)
        
        choice = input("Do you want to (a)ccept, (e)dit, (r)egenerate, or (c)ancel? ").strip().lower()
        
        if choice == "a":
            if commit_changes(commit_message):
                break
            else:
                sys.exit(1)
        elif choice == "e":
            edited_message = edit_commit_message(commit_message)
            if edited_message:
                commit_message = edited_message
                if commit_changes(commit_message):
                    break
                else:
                    sys.exit(1)
        elif choice == "r":
            print("Regenerating commit message...")
            commit_message = generate_commit_message(commit_type, scope)
        elif choice == "c":
            print("Commit cancelled.")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


def main():
    """Main entry point for the CLI."""
    check_dependencies()
    
    commit_type = get_commit_type()
    scope = get_scope()
    
    print("Generating AI-powered commit message with Google Gemini API...")
    interactive_commit_loop(commit_type, scope)


if __name__ == "__main__":
    main()