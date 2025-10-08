"""Component Linker for MultiAgent Framework

Automatically links local development components to projects during init.
"""

import os
import json
from pathlib import Path

# Define where local components live - link to FULL source, not just CLI!
COMPONENT_SOURCES = {
    "agentswarm": {
        "source": "/home/vanman2025/Projects/agentswarm",
        "src_subdir": "src",  # Link to full src directory with all code
        "description": "Multi-agent orchestration and coordination"
    },
    "devops": {
        "source": "/home/vanman2025/Projects/devops", 
        "src_subdir": "src",  # Link to full src directory
        "description": "DevOps automation and CI/CD tools"
    },
    "testing": {
        "source": "/home/vanman2025/Projects/multiagent-testing",
        "src_subdir": "src",  # Link to full src directory
        "description": "Testing framework and automation"
    }
}

def setup_component_links(project_path: Path, console=None):
    """Set up symlinks to local development components."""
    
    # Check if this project IS a component
    project_path_str = str(project_path.resolve())
    is_component_project = False
    self_component_name = None
    
    for name, config in COMPONENT_SOURCES.items():
        if project_path_str == config["source"]:
            is_component_project = True
            self_component_name = name
            if console:
                console.print(f"[yellow]Project detected as {name} component - will skip self-linking[/yellow]")
            break
    
    components_dir = project_path / "components"
    components_dir.mkdir(exist_ok=True)
    
    linked = []
    skipped = []
    
    for name, config in COMPONENT_SOURCES.items():
        # Skip if this is the component itself
        if is_component_project and name == self_component_name:
            skipped.append(f"{name} (self-linking prevented)")
            continue
        source_path = Path(config["source"])
        
        if not source_path.exists():
            skipped.append(f"{name} (not found at {source_path})")
            continue
            
        # Create component directory
        component_dir = components_dir / name
        component_dir.mkdir(exist_ok=True)
        
        # Link the entire source directory structure
        src_link = component_dir / "src"
        if src_link.exists() or src_link.is_symlink():
            src_link.unlink()
            
        # Link to the src directory
        if config["src_subdir"]:
            actual_source = source_path / config["src_subdir"]
            if not actual_source.exists():
                actual_source = source_path  # Fall back to root
        else:
            actual_source = source_path
            
        src_link.symlink_to(actual_source)
        
        # Also link VERSION and pyproject.toml from the component root
        for file_name in ["VERSION", "pyproject.toml", "README.md"]:
            source_file = source_path / file_name
            if source_file.exists():
                link_file = component_dir / file_name
                if link_file.exists() or link_file.is_symlink():
                    link_file.unlink()
                link_file.symlink_to(source_file)
        
        linked.append(f"{name}/src -> {actual_source}")
        
    # Create launcher script
    launcher_script = project_path / "run-component.py"
    launcher_content = '''#!/usr/bin/env python3
"""Run locally linked components"""
import sys
import os
from pathlib import Path

# Add component paths
COMPONENTS = {
    'agentswarm': 'components/agentswarm',
    'devops': 'components/devops',
    'testing': 'components/testing',
}

if len(sys.argv) < 2:
    print("Usage: ./run-component.py <component> [args...]")
    print(f"Available: {', '.join(COMPONENTS.keys())}")
    sys.exit(1)

component = sys.argv[1]
if component not in COMPONENTS:
    print(f"Unknown component: {component}")
    sys.exit(1)

# Add to path and run
component_path = Path(COMPONENTS[component]).resolve()
sys.path.insert(0, str(component_path))

# Import and run the component's main
if component == 'agentswarm':
    from agentswarm import main
    main.run(sys.argv[2:])
elif component == 'devops':
    from devops import main
    main.run(sys.argv[2:])
elif component == 'testing':
    from testing import main
    main.run(sys.argv[2:])
'''
    
    with open(launcher_script, 'w') as f:
        f.write(launcher_content)
    launcher_script.chmod(0o755)
    
    # Update components registry
    registry_file = project_path / ".multiagent" / "components.json"
    if registry_file.exists():
        with open(registry_file) as f:
            registry = json.load(f)
    else:
        registry = {}
        
    registry["linked_components"] = {
        name: {
            "source": str(config["source"]),
            "description": config["description"],
            "linked": name in [l.split(" -> ")[0] for l in linked]
        }
        for name, config in COMPONENT_SOURCES.items()
    }
    
    registry_file.parent.mkdir(exist_ok=True)
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)
        
    if console:
        if linked:
            console.print("\n[bold green]Linked Local Components:[/bold green]")
            for link in linked:
                console.print(f"  ✅ {link}")
        if skipped:
            console.print("\n[yellow]Components not found (skipped):[/yellow]")
            for skip in skipped:
                console.print(f"  ⚠️  {skip}")
                
    return linked, skipped