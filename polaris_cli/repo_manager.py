# src/repo_manager.py

import os
import shutil
import sys
from pathlib import Path

import git
from rich.console import Console

from src.utils import get_project_root

console = Console()

REPO_URL = "https://github.com/bigideainc/polarise-compute-subnet"
REPO_FOLDER_NAME = "compute_subnet"

def get_repo_path():
    """Get the path where the repository should be cloned."""
    project_root = get_project_root()
    return os.path.join(project_root, REPO_FOLDER_NAME)

def ensure_repository_exists():
    """
    Check if repository exists and clone if needed.
    
    Returns:
        tuple: (success: bool, main_py_path: str or None)
    """
    try:
        repo_path = get_repo_path()
        os.makedirs(repo_path, exist_ok=True)
        
        main_py_path = os.path.join(repo_path, "main.py")
        
        if not os.path.exists(main_py_path):
            console.print("[yellow]Repository not found. Cloning...[/yellow]")
            
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                
            git.Repo.clone_from(REPO_URL, repo_path)
            console.print("[green]Repository cloned successfully.[/green]")
            return True, main_py_path
        else:
            console.print("[green]Repository already exists.[/green]")
            return True, main_py_path

    except Exception as e:
        console.print(f"[red]Failed to manage repository: {e}[/red]")
        return False, None

def update_repository():
    """
    Update the repository to the latest version.
    
    Returns:
        bool: True if update was successful, False otherwise.
    """
    try:
        repo_path = get_repo_path()
        
        if not os.path.exists(repo_path):
            console.print("[yellow]Repository not found. Cloning...[/yellow]")
            success, _ = ensure_repository_exists()
            return success
            
        try:
            repo = git.Repo(repo_path)
            console.print("[yellow]Fetching updates...[/yellow]")
            
            # Fetch updates
            repo.remotes.origin.fetch()
            
            # Get current branch
            current = repo.active_branch
            
            # Get status
            if repo.is_dirty():
                console.print("[yellow]Local changes detected. Stashing changes...[/yellow]")
                repo.git.stash()
            
            # Pull latest changes
            repo.remotes.origin.pull()
            
            console.print("[green]Repository updated successfully.[/green]")
            return True
            
        except git.GitCommandError as e:
            console.print(f"[red]Git operation failed: {e}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Failed to update repository: {e}[/red]")
        return False
