"""Auto-update all deployed projects when multiagent-core is built."""

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

DEPLOYMENTS_FILE = Path.home() / ".multiagent-core-deployments.json"
CORE_PROJECT = Path(__file__).parent.parent

def register_deployment(project_path):
    """Register a project for automatic updates (called by multiagent init)."""
    if isinstance(project_path, str):
        project_path = Path(project_path)
    project_path = project_path.resolve()

    # Skip /tmp projects - they're temporary test projects
    if str(project_path).startswith('/tmp/'):
        print(f"[SKIP] Not registering temporary project: {project_path.name}")
        return

    GLOBAL_TRACKING = Path.home() / ".multiagent-core-deployments.json"

    # Load or create tracking file
    if GLOBAL_TRACKING.exists():
        with open(GLOBAL_TRACKING) as f:
            data = json.load(f)
    else:
        data = {"projects": {}, "last_updated": None}

    # Add project if not already tracked
    project_str = str(project_path)
    if project_str not in data["projects"]:
        data["projects"][project_str] = {
            "registered": datetime.now().isoformat(),
            "last_updated": None
        }

        # Save tracking file
        with open(GLOBAL_TRACKING, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"[OK] Registered for automatic updates: {project_path.name}")

def track_deployment(project_path: Path):
    """Add a project to the deployment tracking list (legacy)."""
    project_path = project_path.resolve()
    
    # Load or create deployments file
    if DEPLOYMENTS_FILE.exists():
        with open(DEPLOYMENTS_FILE) as f:
            data = json.load(f)
    else:
        data = {"deployments": [], "last_updated": None}
    
    # Add project if not already tracked
    project_str = str(project_path)
    if project_str not in data["deployments"]:
        data["deployments"].append(project_str)
        print(f"[TRACKED] Tracked new deployment: {project_path}")
    
    # Save deployments file
    with open(DEPLOYMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def sync_directory_recursively(src_dir, dst_dir, exclude_dirs=None):
    """Recursively sync directory structure and files."""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.DS_Store'}

    if not src_dir.exists():
        return

    # Create destination directory if it doesn't exist
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Clean up deprecated files and directories
    if dst_dir.name == 'prompts':
        cleanup_deprecated_prompts(dst_dir)
        # Also remove any files that don't exist in the source
        cleanup_extra_files(src_dir, dst_dir)
    elif dst_dir.name == 'docs':
        cleanup_deprecated_docs(src_dir, dst_dir)

    # CLEANUP: Remove directories and files that don't exist in source
    # Get list of items that should exist (from source)
    src_items = {item.name for item in src_dir.iterdir() if item.name not in exclude_dirs}

    # Remove items in destination that don't exist in source
    for dst_item in list(dst_dir.iterdir()):
        if dst_item.name in exclude_dirs:
            continue

        if dst_item.name not in src_items:
            # This item doesn't exist in source - remove it
            if dst_item.is_dir():
                shutil.rmtree(dst_item)
                print(f"     ✗ Removed obsolete directory: {dst_item.name}")
            else:
                dst_item.unlink()
                print(f"     ✗ Removed obsolete file: {dst_item.name}")

    # Sync all files and subdirectories from source
    for src_item in src_dir.iterdir():
        if src_item.name in exclude_dirs:
            continue

        dst_item = dst_dir / src_item.name

        if src_item.is_file():
            # For template files, always copy to ensure they're up to date
            # For other files, only copy if newer or different
            should_copy = (
                not dst_item.exists() or
                src_dir.name == 'templates' or  # Always sync template files
                src_item.stat().st_mtime > dst_item.stat().st_mtime
            )

            if should_copy:
                shutil.copy2(src_item, dst_item)
                print(f"     → {src_item.relative_to(src_dir)}")
        elif src_item.is_dir():
            # Recursively sync subdirectory
            sync_directory_recursively(src_item, dst_item, exclude_dirs)

def cleanup_deprecated_prompts(prompts_dir):
    """Remove deprecated .md prompt files when .txt equivalents exist."""
    if not prompts_dir.exists():
        return
    
    # Find all .txt files to understand what agents we have
    txt_files = {f.stem for f in prompts_dir.glob("*.txt")}
    agent_names = {stem.split('-')[0] for stem in txt_files if '-' in stem}
    
    for md_file in prompts_dir.glob("*.md"):
        # Skip README.md and task-related documentation files
        if md_file.stem in ['README', 'TASK_CHECKLIST', 'TASK_TRIGGER']:
            continue
        
        should_remove = False
        
        # If there's a corresponding .txt file with exact same stem, remove the .md file
        if md_file.stem in txt_files:
            should_remove = True
            reason = f"replaced by {md_file.stem}.txt"
        
        # If this is an old agent prompt file and we have a new .txt file for that agent
        elif '-' in md_file.stem:
            agent_name = md_file.stem.split('-')[0]
            if agent_name in agent_names:
                should_remove = True
                reason = f"replaced by {agent_name}-startup.txt"
        
        if should_remove:
            print(f"     ✗ Removing deprecated {md_file.name} ({reason})")
            md_file.unlink()

def cleanup_extra_files(src_dir, dst_dir):
    """Remove files from destination that don't exist in source."""
    if not src_dir.exists() or not dst_dir.exists():
        return
    
    # Get list of files that should exist (from source)
    src_files = {item.name for item in src_dir.iterdir() if item.is_file()}
    
    # Remove files from destination that don't exist in source
    for dst_file in dst_dir.iterdir():
        if dst_file.is_file() and dst_file.name not in src_files:
            print(f"     ✗ Removing extra file {dst_file.name} (not in source)")
            dst_file.unlink()

def cleanup_deprecated_docs(src_docs, dst_docs):
    """Remove directories in docs that no longer exist in the template."""
    if not src_docs.exists() or not dst_docs.exists():
        return
    
    # Get list of directories that should exist (from source)
    src_dirs = {item.name for item in src_docs.iterdir() if item.is_dir()}
    
    # Remove directories that no longer exist in the source
    for dst_item in dst_docs.iterdir():
        if dst_item.is_dir() and dst_item.name not in src_dirs:
            print(f"     ✗ Removing deprecated docs directory: {dst_item.name}/")
            shutil.rmtree(dst_item)

def update_all_deployments():
    """Update all tracked deployments with latest templates."""
    
    if not DEPLOYMENTS_FILE.exists():
        print("No deployments tracked yet")
        return
    
    with open(DEPLOYMENTS_FILE) as f:
        data = json.load(f)
    
    templates_dir = CORE_PROJECT / "multiagent_core" / "templates"
    
    # Handle both old format (data['deployments']) and new format (data['projects'])
    if 'projects' in data:
        projects = list(data['projects'].keys())
        print(f"[UPDATE] Auto-updating {len(projects)} deployed projects...")
    else:
        projects = data.get('deployments', [])
        print(f"[UPDATE] Auto-updating {len(projects)} deployed projects...")
    
    for project_path in projects:
        project = Path(project_path)
        
        if not project.exists():
            print(f"[WARNING]  Skipping {project_path} (not found)")
            continue
            
        print(f"[PACKAGE] Updating: {project.name}")
        
        # Update .multiagent directory with full recursive sync
        src_multiagent = templates_dir / ".multiagent"
        dst_multiagent = project / ".multiagent"
        if src_multiagent.exists() and dst_multiagent.exists():
            print(f"   [SYNC] Syncing .multiagent directory structure...")
            sync_directory_recursively(src_multiagent, dst_multiagent)
        
        # Update .claude directory with full recursive sync
        src_claude = templates_dir / ".claude"
        dst_claude = project / ".claude"
        if src_claude.exists():
            print(f"   [SYNC] Syncing .claude directory structure...")
            if not dst_claude.exists():
                dst_claude.mkdir(parents=True, exist_ok=True)
            sync_directory_recursively(src_claude, dst_claude)
            
            # Ensure SDK config directory exists and is synced
            src_sdk_config = src_claude / "sdk-config"
            dst_sdk_config = dst_claude / "sdk-config"
            if src_sdk_config.exists():
                dst_sdk_config.mkdir(exist_ok=True)
                for config_file in src_sdk_config.glob("*.json"):
                    shutil.copy2(config_file, dst_sdk_config / config_file.name)
                    print(f"     → sdk-config/{config_file.name}")
        
        # Update .multiagent-feedback directory with full recursive sync
        src_feedback = templates_dir / ".multiagent-feedback"
        dst_feedback = project / ".multiagent-feedback"
        if src_feedback.exists():
            print(f"   [SYNC] Syncing .multiagent-feedback directory structure...")
            if not dst_feedback.exists():
                dst_feedback.mkdir(parents=True, exist_ok=True)
            sync_directory_recursively(src_feedback, dst_feedback)
        
        # Update .github directory with full recursive sync
        src_github = templates_dir / ".github"
        dst_github = project / ".github"
        if src_github.exists() and dst_github.exists():
            print(f"   [SYNC] Syncing .github directory structure...")
            sync_directory_recursively(src_github, dst_github)
            
            # Ensure webhook entrypoints are synced
            src_webhooks = src_github / "webhooks"
            dst_webhooks = dst_github / "webhooks"
            if src_webhooks.exists():
                dst_webhooks.mkdir(exist_ok=True)
                for webhook_file in src_webhooks.glob("*.json"):
                    shutil.copy2(webhook_file, dst_webhooks / webhook_file.name)
                    print(f"     → webhooks/{webhook_file.name}")
        
        # Update scripts/hooks if they exist in templates
        src_scripts = templates_dir / "scripts"
        if src_scripts.exists():
            src_hooks = src_scripts / "hooks"
            if src_hooks.exists():
                print(f"   [SYNC] Syncing scripts/hooks...")
                dst_scripts = project / "scripts"
                dst_hooks = dst_scripts / "hooks"
                dst_hooks.mkdir(parents=True, exist_ok=True)
                for hook in src_hooks.glob("*"):
                    if hook.is_file():
                        shutil.copy2(hook, dst_hooks / hook.name)
                        # Make sure hooks are executable
                        (dst_hooks / hook.name).chmod(0o755)
                        print(f"     → hooks/{hook.name}")
        
        print(f"   [OK] Updated {project.name}")
    
    # Update last updated time in the appropriate format
    current_time = datetime.now().isoformat()
    if 'projects' in data:
        # New format: update both global and per-project timestamps
        data["last_updated"] = current_time
        for project_path in projects:
            if project_path in data['projects']:
                data['projects'][project_path]['last_updated'] = current_time
    else:
        # Old format: just update global timestamp
        data["last_updated"] = current_time
    
    with open(DEPLOYMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"[SUCCESS] All deployments updated at {current_time}")

def hook_into_build():
    """Called after build to update all deployments."""
    print("\n" + "="*50)
    print("[AUTO-UPDATE] MULTIAGENT-CORE AUTO-UPDATE SYSTEM")
    print("="*50)
    update_all_deployments()
    print("="*50 + "\n")

if __name__ == "__main__":
    # Test the auto-updater
    update_all_deployments()