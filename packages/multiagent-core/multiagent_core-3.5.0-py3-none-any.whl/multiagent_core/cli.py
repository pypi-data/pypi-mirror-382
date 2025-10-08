"""Multi-Agent Core CLI

Command-line interface for the multi-agent development framework.
"""

from __future__ import annotations

import click
import json
import os
import subprocess
import tempfile
import requests
import glob
import threading
from typing import Any, Dict, Optional, Tuple, List
from packaging import version
try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata
from importlib import resources as importlib_resources
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from shutil import which
from .config import config
# from .feedback import runtime as feedback_runtime  # Legacy - removed
# Docker imports removed - using simple file operations instead
from .detector import ProjectDetector
from .analyzer import TechStackAnalyzer
from .env_generator import EnvironmentGenerator
from .templates import TemplateManager
from .update_checker import UpdateChecker, MULTIAGENT_PACKAGES, clear_cache
from . import __version__

console = Console()


def _load_version_metadata() -> Dict[str, Any]:
    """Return version metadata bundled with the package if available."""

    candidate_paths = [
        Path(__file__).resolve().parent / "VERSION",
        Path(__file__).resolve().parent.parent / "VERSION",
        Path.cwd() / "VERSION",
        Path.home() / ".multiagent" / "VERSION",
    ]

    for candidate in candidate_paths:
        if candidate.exists():
            try:
                with candidate.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    return data
            except (OSError, json.JSONDecodeError):
                continue

    try:
        with importlib_resources.files("multiagent_core").joinpath("VERSION").open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        pass

    return {}


def _current_framework_version() -> str:
    """Return the installed multiagent-core version string."""

    metadata_blob = _load_version_metadata()
    version_value = metadata_blob.get("version") if metadata_blob else None
    return str(version_value) if version_value else (__version__ or "unknown")


def _load_components_registry(project_root: Path) -> Dict[str, Any]:
    """Load `.multiagent/components.json` if present."""

    components_file = project_root / ".multiagent" / "components.json"
    if components_file.exists():
        try:
            with components_file.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def _write_components_registry(project_root: Path, registry: Dict[str, Any]) -> None:
    """Persist `.multiagent/components.json` with pretty formatting."""

    multiagent_dir = project_root / ".multiagent"
    multiagent_dir.mkdir(parents=True, exist_ok=True)
    components_file = multiagent_dir / "components.json"
    with components_file.open("w", encoding="utf-8") as fh:
        json.dump(registry, fh, indent=2)
        fh.write("\n")


def _apply_framework_metadata(registry: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the registry records the framework version + metadata."""

    metadata_blob = _load_version_metadata()
    if metadata_blob:
        registry["framework_version_metadata"] = metadata_blob
        registry["framework_version"] = metadata_blob.get("version", __version__ or "unknown")
    else:
        registry["framework_version"] = __version__ or "unknown"
    registry.setdefault("installation_order", [])
    return registry


def _resolve_component_version(package_name: str, fallback: Optional[str] = None) -> str:
    """Best-effort lookup for a companion package version."""

    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return fallback or "unknown"
    except Exception:  # pragma: no cover - unexpected importlib issues
        return fallback or "unknown"


def _locate_specify_executable() -> Optional[str]:
    """Return the best-effort path to the `specify` CLI if available."""

    candidates = []
    env_path = which('specify')
    if env_path:
        candidates.append(env_path)

    fallback_paths = [
        Path.home() / '.local' / 'bin' / 'specify',
        Path.home() / '.npm-global' / 'bin' / 'specify',
        Path('/usr/local/bin/specify'),
        Path('/usr/bin/specify'),
    ]

    for candidate in fallback_paths:
        candidate_str = str(candidate)
        if candidate.exists() and candidate_str not in candidates:
            candidates.append(candidate_str)

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    return None


def _spec_kit_available() -> Tuple[bool, Optional[str]]:
    """Detect whether spec-kit is accessible on the current PATH."""

    specify_path = _locate_specify_executable()
    if not specify_path:
        return False, None

    try:
        result = subprocess.run(
            [specify_path, '--help'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, specify_path
    except (FileNotFoundError, subprocess.SubprocessError):
        return False, specify_path

    return False, specify_path

@click.group()
@click.version_option(__version__)
def main():
    """Multi-Agent Development Framework CLI"""
    # Auto-detect WSL environment and warn if using wrong Python
    _check_python_environment()
    # Check for updates on every command (non-blocking)
    _check_for_updates_async()
    pass

@main.command()
@click.argument('path', type=click.Path(), required=False)
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--create-repo', is_flag=True, help='Create a GitHub repository')
@click.option('--interactive/--no-interactive', default=True, help='Use interactive prompts to configure initialization')
@click.option('--backend-heavy', is_flag=True, help='Optimize for backend development (minimal frontend scaffolding)')
def init(path, dry_run, create_repo, interactive, backend_heavy):
    """Initialize multi-agent framework in a new or existing directory."""
    


    # Check if spec-kit is installed (REQUIRED)
    spec_kit_available, spec_kit_path = _spec_kit_available()

    if not spec_kit_available:
        console.print("[bold yellow]⚠️  Spec-Kit Not Found[/bold yellow]")
        console.print("\nMultiAgent works with spec-kit for specification-driven development.")
        console.print("Please install spec-kit first:\n")
        console.print("  [cyan]# Install uv if needed[/cyan]")
        console.print("  [cyan]curl -LsSf https://astral.sh/uv/install.sh | sh[/cyan]")
        console.print("  [cyan]# Install spec-kit[/cyan]")
        console.print("  [cyan]uv tool install specify-cli --from git+https://github.com/github/spec-kit.git[/cyan]")
        console.print("  [cyan]# Verify installation[/cyan]")
        console.print("  [cyan]specify check[/cyan]\n")

        if interactive:
            if not click.confirm("Continue without spec-kit? (not recommended)", default=False):
                console.print("[red]Initialization cancelled. Please install spec-kit first.[/red]")
                return
        else:
            console.print("[yellow]Continuing without spec-kit (not recommended)[/yellow]")
    else:
        if spec_kit_path:
            console.print(f"[dim]spec-kit detected at {spec_kit_path}[/dim]")

    if path:
        target_path = Path(path).resolve()
        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Error creating directory {target_path}: {e}[/red]")
            return
    else:
        target_path = Path.cwd()

    # Change current working directory to the target path
    os.chdir(target_path)
    cwd = target_path

    if dry_run:
        console.print("[bold blue]Dry run mode - no changes will be made[/bold blue]")

    if backend_heavy:
        console.print("[bold blue]Backend-heavy mode - optimizing for backend development[/bold blue]")

    console.print(f"Initializing multi-agent framework in: {cwd}")

    # Interactive setup prompts
    # Initialize defaults first
    git_exists = (cwd / ".git").exists()
    use_existing_git = git_exists  # Default to using existing git if it exists
    create_github = create_repo
    install_git_hooks = True

    if not dry_run and interactive:
        # Check if existing git repository
        github_remote_exists = False

        if git_exists:
            # Check if GitHub remote already exists
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      cwd=str(cwd), capture_output=True, text=True)
                if result.returncode == 0 and 'github.com' in result.stdout:
                    github_remote_exists = True
                    console.print(f"[yellow]GitHub remote detected: {result.stdout.strip()}[/yellow]")
                    if not click.confirm("Overwrite existing GitHub repository configuration?", default=False):
                        console.print("[dim]Keeping existing GitHub configuration[/dim]")
                        create_github = False
                    else:
                        create_github = click.confirm("Continue with GitHub repository setup?", default=True)
                else:
                    use_existing_git = click.confirm("Existing git repository detected. Use existing repository?", default=True)
                    create_github = create_repo or click.confirm("Create GitHub repository?", default=False)
            except:
                use_existing_git = click.confirm("Existing git repository detected. Use existing repository?", default=True)
                create_github = create_repo or click.confirm("Create GitHub repository?", default=False)
        else:
            use_existing_git = False
            create_github = create_repo or click.confirm("Create GitHub repository?", default=False)

        # Git hooks installation
        install_git_hooks = click.confirm("Install git hooks for multi-agent workflow?", default=True)
        
        # Claude Code GitHub App setup prompt
        if create_github or github_remote_exists:
            console.print("\n[bold blue]🤖 Claude Code Integration Setup[/bold blue]")
            console.print("For automated PR reviews and agent feedback, Claude Code needs GitHub access.")
            console.print("\n[cyan]To set up Claude Code with your GitHub repository:[/cyan]")
            console.print("  1. In Claude, run: [yellow]/install github[/yellow]")
            console.print("  2. Follow the GitHub App installation flow")
            console.print("  3. Grant access to your repositories")
            console.print("  4. Claude will then be able to review PRs automatically")
            
            setup_claude = click.confirm("\nHave you installed the Claude Code GitHub app?", default=False)
            if not setup_claude:
                console.print("\n[yellow]💡 Tip: After init completes, run '/install github' in Claude to enable automated reviews![/yellow]")

    # Copy framework structure from package
    if not dry_run:
        success = _generate_project_structure(cwd, backend_heavy=backend_heavy)
        if not success:
            console.print("[red]Framework initialization failed[/red]")
            return

        registry = _load_components_registry(cwd)
        _apply_framework_metadata(registry)
        _write_components_registry(cwd, registry)

        console.print("[green]Core framework initialized[/green]")

        _run_documentation_bootstrap(cwd)

    # Handle git repository setup FIRST
    if not dry_run and not use_existing_git:
        console.print("Initializing git repository...")
        try:
            subprocess.run(['git', 'init'], cwd=str(cwd), check=True)
            # Handle git ownership issues in WSL/Windows
            try:
                subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', str(cwd)],
                             capture_output=True, text=True)
            except:
                pass  # Non-critical if this fails
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Git initialization failed: {e}[/yellow]")

    # Handle git hooks installation (after git is initialized)
    # NOTE: Git hooks now installed via _install_git_hooks_from_templates in _generate_project_structure
    # if not dry_run and install_git_hooks:
    #     _install_git_hooks(cwd)

    # Create an initial commit before creating the repo
    if not dry_run and not use_existing_git:
        try:
            subprocess.run(['git', 'add', '.'], cwd=str(cwd), check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(cwd), check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Initial commit failed: {e}[/yellow]")

    # Handle GitHub repository creation
    if not dry_run and create_github:
        _create_github_repo(cwd)

    # Recommend additional components based on detected CLIs and project structure
    if not dry_run:
        _recommend_additional_components(cwd)

    # Link local development components if available
    if not dry_run:
        try:
            from .component_linker import setup_component_links
            console.print("\n[bold blue]Setting up local component links...[/bold blue]")
            linked, skipped = setup_component_links(cwd, console)
            if linked:
                console.print("[green]Local components linked for development[/green]")
        except Exception as e:
            console.print(f"[yellow]Component linking skipped: {e}[/yellow]")

    # Auto-generate smart environment configuration
    if not dry_run:
        console.print("\n[bold blue]Smart Environment Detection[/bold blue]")
        try:
            detector = ProjectDetector(cwd)
            project_info = detector.detect()

            if project_info.project_type != 'unknown':
                console.print(f"Detected: [cyan]{project_info.project_type}[/cyan] project")

                if project_info.frameworks:
                    console.print(f"Frameworks: [cyan]{', '.join(list(project_info.frameworks)[:3])}[/cyan]")

            else:
                console.print("[dim]Unknown project type - skipping auto environment detection[/dim]")
        except Exception as e:
            console.print(f"[yellow]Warning: Environment detection failed: {e}[/yellow]")

    # Auto-register project for updates
    try:
        from multiagent_core.auto_updater import register_deployment
        register_deployment(cwd)
        console.print("[dim]Project registered for automatic updates[/dim]")
    except Exception:
        pass  # Silent fail if registration doesn't work
    
    console.print("[green]Multi-agent framework initialization complete![/green]")

def _install_component(component, multiagent_dir, dry_run):
    """Install a specific component with intelligent directory merging"""
    console.print(f"Installing component: {component}")

    if not dry_run:
        # Create component-specific directories
        github_dir = Path.cwd() / ".github" / "workflows" / component
        github_dir.mkdir(parents=True, exist_ok=True)

        claude_dir = Path.cwd() / ".claude" / component
        claude_dir.mkdir(parents=True, exist_ok=True)

        project_root = multiagent_dir.parent
        registry = _load_components_registry(project_root)
        if not isinstance(registry, dict):  # pragma: no cover - defensive against corrupted files
            registry = {}

        components_map = registry.setdefault("components", {})
        existing_entry = components_map.get(component)
        previous_version = existing_entry.get("version") if isinstance(existing_entry, dict) else None

        components_map[component] = {
            "version": _resolve_component_version(component, previous_version),
            "installed": True,
        }

        install_order = registry.setdefault("installation_order", [])
        if component not in install_order:
            install_order.append(component)

        _apply_framework_metadata(registry)
        _write_components_registry(project_root, registry)

    console.print(f"[green]Component {component} installed with intelligent directory merging[/green]")

@main.command()
def status():
    """Show installation status and component information"""
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if not multiagent_dir.exists():
        console.print("[red]Multi-agent framework not initialized in this directory[/red]")
        console.print("Run 'multiagent init' to get started")
        return

    # Read components registry
    components_file = multiagent_dir / "components.json"
    registry = _load_components_registry(cwd)

    if components_file.exists():
        updated_registry = _apply_framework_metadata(dict(registry))
        if updated_registry != registry:
            _write_components_registry(cwd, updated_registry)
        registry = updated_registry

        installed_version = _current_framework_version()
        recorded_version = registry.get("framework_version", "unknown")
        metadata_blob = registry.get("framework_version_metadata")
        if not isinstance(metadata_blob, dict) or not metadata_blob:
            metadata_blob = _load_version_metadata()

        console.print(f"Framework version (installed): [cyan]{installed_version}[/cyan]")
        if recorded_version not in {"unknown", installed_version}:
            console.print(
                f"[yellow]Project registry recorded {recorded_version}. Run `multiagent upgrade` to align if needed.[/yellow]"
            )
        elif recorded_version != "unknown":
            console.print(f"Project registry version: [cyan]{recorded_version}[/cyan]")

        if isinstance(metadata_blob, dict):
            commit = metadata_blob.get("commit")
            build_date = metadata_blob.get("build_date")
            details = []
            if commit:
                details.append(f"commit [dim]{commit}[/dim]")
            if build_date:
                details.append(f"built [dim]{build_date}[/dim]")
            if details:
                console.print("; ".join(details))

        table = Table(title="Multi-Agent Framework Status")
        table.add_column("Component", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Status", style="green")

        components = registry.get("components", registry)
        rows_added = False

        for component, info in components.items():
            if component in ["installation_order", "framework_version", "framework_version_metadata"]:
                continue

            if isinstance(info, dict):
                status = "[green]Installed[/green]" if info.get("installed", False) else "[red]Not installed[/red]"
                version_label = info.get("version", "unknown")
                table.add_row(component, version_label, status)
                rows_added = True
            elif isinstance(info, str):
                table.add_row(component, info, "[yellow]Legacy format[/yellow]")
                rows_added = True
            else:
                table.add_row(component, str(info), "[yellow]Unknown format[/yellow]")
                rows_added = True

        if rows_added:
            console.print(table)
        else:
            console.print("[yellow]No components recorded in registry[/yellow]")

        install_order = registry.get("installation_order", [])
        if install_order:
            console.print(f"\nInstallation order: {' -> '.join(install_order)}")
    else:
        console.print("[yellow]WARNING: No components registry found[/yellow]")
        console.print(f"Framework version (installed): [cyan]{_current_framework_version()}[/cyan]")

@main.command()
@click.argument('component')
def uninstall(component):
    """Remove a component from the framework"""
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if not multiagent_dir.exists():
        console.print("[red]ERROR: Multi-agent framework not initialized[/red]")
        return

    console.print(f"Removing component: {component}")

    # Update registry
    components_file = multiagent_dir / "components.json"
    if not components_file.exists():
        console.print(f"[red]ERROR: Component {component} not found[/red]")
        return

    registry = _load_components_registry(cwd)
    if not registry:
        console.print(f"[red]ERROR: Component {component} not found[/red]")
        return

    components_map = registry.get("components")
    removed = False

    if isinstance(components_map, dict) and component in components_map:
        components_map.pop(component, None)
        removed = True
    elif component in registry:
        registry.pop(component, None)
        removed = True

    if not removed:
        console.print(f"[red]ERROR: Component {component} not found[/red]")
        return

    install_order = registry.get("installation_order", [])
    if component in install_order:
        install_order.remove(component)

    # Drop empty containers to keep registry tidy
    if isinstance(components_map, dict) and not components_map:
        registry.pop("components", None)

    _apply_framework_metadata(registry)
    _write_components_registry(cwd, registry)

    console.print(f"[green]Component {component} removed[/green]")

@main.command()
def upgrade():
    """Check for and install updates for all multiagent packages."""

    console.print("[bold blue]Checking for multiagent package updates...[/bold blue]")

    checker = UpdateChecker()
    updates = checker.check(force=True)
    current_versions = checker.current_versions
    latest_versions = checker.latest_versions

    for package in MULTIAGENT_PACKAGES:
        current = current_versions.get(package)
        latest = latest_versions.get(package)
        if current is None:
            console.print(f"[dim]{package}: not installed[/dim]")
            continue
        if latest and version.parse(latest) > version.parse(current):
            console.print(f"[yellow]{package}: {current} → {latest}[/yellow]")
        else:
            console.print(f"[green]{package}: {current} (up to date)[/green]")

    if not updates:
        console.print("[green]\nAll installed packages are up to date![/green]")
        return

    console.print(f"\n[bold yellow]{len(updates)} package(s) have updates available[/bold yellow]")

    if not click.confirm("Install updates?"):
        return

    for update in updates:
        package = update.package
        console.print(f"Upgrading {package} ({update.current} → {update.latest})...")
        try:
            pipx_cmd = ['pipx', 'upgrade', package]
            pip_cmd = ['pip', 'install', '--upgrade', package]

            try:
                pipx_result = subprocess.run(pipx_cmd, capture_output=True, text=True)
            except FileNotFoundError:
                pipx_result = subprocess.CompletedProcess(pipx_cmd, returncode=1, stdout='', stderr='pipx not installed')

            if pipx_result.returncode == 0:
                console.print(f"[green]{package} upgraded successfully via pipx[/green]")
                continue

            result = subprocess.run(pip_cmd, capture_output=True, text=True)
            if result.returncode != 0 and "externally-managed-environment" in result.stderr:
                result = subprocess.run(pip_cmd + ['--break-system-packages'], capture_output=True, text=True)

            if result.returncode == 0:
                console.print(f"[green]{package} upgraded successfully via pip[/green]")
            else:
                console.print(f"[red]Failed to upgrade {package}: {result.stderr.strip()}[/red]")
                console.print(f"[yellow]Try manual upgrade: pipx upgrade {package}[/yellow]")
        except Exception as exc:  # pragma: no cover - unexpected subprocess issues
            console.print(f"[red]Error upgrading {package}: {exc}[/red]")

    clear_cache()

@main.command()
def config_show():
    """Show current configuration"""
    console.print("[bold blue]MultiAgent Core Configuration[/bold blue]\n")

    # Core settings
    console.print("[bold]Core Settings:[/bold]")
    console.print(f"Debug: {config.debug}")
    console.print(f"Log Level: {config.log_level}")
    console.print(f"Development Mode: {config.development_mode}")
    console.print(f"Interactive: {config.interactive}")

    # GitHub settings
    console.print("\n[bold]GitHub Settings:[/bold]")
    console.print(f"GitHub Token: {'[green]Set[/green]' if config.github_token else '[red]Not set[/red]'}")
    console.print(f"GitHub Username: {config.github_username or '[red]Not set[/red]'}")

    # Docker settings
    console.print("\n[bold]Docker Settings:[/bold]")
    console.print(f"Docker Host: {config.docker_host}")
    console.print(f"Force Docker: {config.force_docker}")
    console.print(f"Docker Timeout: {config.docker_timeout}s")

    # WSL/Windows settings
    console.print("\n[bold]WSL/Windows Settings:[/bold]")
    console.print(f"Auto Convert Paths: {config.wsl_auto_convert_paths}")

    # Component defaults
    console.print("\n[bold]Component Installation Defaults:[/bold]")
    console.print(f"DevOps: {config.get_bool('default_install_devops', True)}")
    console.print(f"Testing: {config.get_bool('default_install_testing', True)}")
    console.print(f"AgentSwarm: {config.get_bool('default_install_agentswarm', False)}")

    console.print(f"\n[dim]Configuration loaded from .env file and environment variables[/dim]")
    console.print(f"[dim]Copy .env.example to .env to customize settings[/dim]")

@main.command()
def detect():
    """Detect project structure and tech stack"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Analyzing project structure in: {cwd}[/bold blue]\n")

    # Run detection
    detector = ProjectDetector(cwd)
    project_info = detector.detect()

    # Display results
    console.print("[bold]Project Detection Results:[/bold]")
    console.print(f"Project Type: [cyan]{project_info.project_type}[/cyan]")
    console.print(f"Language: [cyan]{project_info.language}[/cyan]")
    console.print(f"Structure: [cyan]{project_info.structure}[/cyan]")

    if project_info.frameworks:
        console.print(f"Frameworks: [cyan]{', '.join(project_info.frameworks)}[/cyan]")

    console.print(f"\n[bold]Components:[/bold]")
    console.print(f"Backend: {'[green]Yes[/green]' if project_info.has_backend else '[red]No[/red]'}")
    console.print(f"Frontend: {'[green]Yes[/green]' if project_info.has_frontend else '[red]No[/red]'}")
    console.print(f"Database: {'[green]Yes[/green]' if project_info.has_database else '[red]No[/red]'}")

    if project_info.deployment_target:
        console.print(f"Deployment Target: [cyan]{project_info.deployment_target}[/cyan]")

    console.print(f"\n[dim]Found {len(project_info.config_files)} configuration files[/dim]")

@main.command()
def env_detect():
    """Analyze environment requirements for current project"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Analyzing environment requirements in: {cwd}[/bold blue]\n")

    # Run detection and analysis
    detector = ProjectDetector(cwd)
    analyzer = TechStackAnalyzer(detector)
    env_summary = analyzer.get_environment_summary()

    # Display summary
    console.print("[bold]Environment Requirements Summary:[/bold]")
    console.print(f"Total Services: [cyan]{env_summary['total_services']}[/cyan]")
    console.print(f"Required Environment Variables: [cyan]{env_summary['required_env_vars']}[/cyan]")
    console.print(f"Optional Environment Variables: [cyan]{env_summary['optional_env_vars']}[/cyan]")

    if env_summary['service_categories']:
        console.print(f"Service Categories: [cyan]{', '.join(env_summary['service_categories'])}[/cyan]")

    # Show services by category
    if env_summary['services_by_category']:
        console.print("\n[bold]Required Services:[/bold]")
        for category, services in env_summary['services_by_category'].items():
            console.print(f"  {category}: {', '.join(services)}")

    # Show requirements
    env_reqs = analyzer.analyze()
    if env_reqs.database_requirements:
        console.print("\n[bold]Database Setup Needed:[/bold]")
        for req in env_reqs.database_requirements:
            console.print(f"  • {req}")

    if env_reqs.deployment_requirements:
        console.print("\n[bold]Deployment Setup Needed:[/bold]")
        for req in env_reqs.deployment_requirements:
            console.print(f"  • {req}")

@main.command()
@click.option('--interactive/--no-interactive', default=True, help='Run interactive configuration')
@click.option('--template', help='Use specific template instead of auto-detection')
def env_init(interactive, template):
    """Generate smart environment configuration"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Generating environment configuration for: {cwd}[/bold blue]\n")

    # Run detection and analysis
    detector = ProjectDetector(cwd)
    project_info = detector.detect()
    analyzer = TechStackAnalyzer(detector)
    generator = EnvironmentGenerator(analyzer)

    console.print(f"Detected: [cyan]{project_info.project_type}[/cyan] project with [cyan]{project_info.language}[/cyan]")

    if project_info.frameworks:
        console.print(f"Frameworks: [cyan]{', '.join(project_info.frameworks)}[/cyan]")

    # Check if template specified
    if template:
        template_manager = TemplateManager()
        project_template = template_manager.get_template(template)
        if not project_template:
            console.print(f"[red]Template '{template}' not found[/red]")
            console.print("Available templates:")
            for tmpl in template_manager.list_templates():
                console.print(f"  • {tmpl['name']}: {tmpl['description']}")
            return
        console.print(f"Using template: [cyan]{project_template.name}[/cyan]")
    else:
        console.print("Auto-detecting best configuration...")

    # Generate environment files
    try:
        env_example_path, env_template_path = generator.write_env_files(cwd)
        console.print(f"\n[green]Environment files generated:[/green]")
        console.print(f"  • {env_example_path.name} (for git repository)")
        console.print(f"  • {env_template_path.name} (with example values)")

        if interactive:
            console.print("\n[bold]Interactive Configuration:[/bold]")
            prompts = generator.generate_interactive_prompts()
            env_values = {}

            current_category = None
            for prompt in prompts:
                if prompt['type'] == 'category_header':
                    if current_category:
                        console.print()  # Add spacing between categories
                    current_category = prompt['category']
                    console.print(f"\n[bold cyan]{prompt['category']}[/bold cyan]")
                    console.print(f"[dim]{prompt['description']}[/dim]")
                elif prompt['type'] == 'input':
                    description = prompt['description']
                    if prompt.get('example'):
                        description += f" [dim](e.g., {prompt['example']})[/dim]"

                    if prompt['required']:
                        value = Prompt.ask(f"  {prompt['name']}", default="")
                        if value.strip():
                            env_values[prompt['name']] = value.strip()
                    else:
                        value = Prompt.ask(f"  {prompt['name']} [dim](optional)[/dim]", default="")
                        if value.strip():
                            env_values[prompt['name']] = value.strip()

            # Write .env file with user values
            if env_values:
                env_path = cwd / '.env'
                if env_path.exists():
                    if not Confirm.ask(f".env file already exists. Overwrite?"):
                        console.print("[yellow]Environment configuration cancelled[/yellow]")
                        return

                # Generate final .env content
                with open(env_template_path) as f:
                    env_content = f.read()

                # Replace values in template
                for var_name, var_value in env_values.items():
                    env_content = env_content.replace(f'{var_name}=', f'{var_name}={var_value}')

                with open(env_path, 'w') as f:
                    f.write(env_content)

                console.print(f"\n[green].env file created with your configuration![/green]")

                # Validate configuration
                errors = generator.validate_environment(env_values)
                if errors:
                    console.print("\n[yellow]Configuration warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  • {error}")
                else:
                    console.print("[green]Environment configuration is valid[/green]")

        # Show setup instructions
        setup_instructions = generator.get_setup_instructions()
        if setup_instructions:
            console.print("\n[bold]Next Steps - Service Setup:[/bold]")
            for i, instruction in enumerate(setup_instructions, 1):
                console.print(f"  {i}. {instruction}")

    except Exception as e:
        console.print(f"[red]Error generating environment configuration: {e}[/red]")

@main.command()
def env_validate():
    """Validate current environment configuration"""
    cwd = Path.cwd()
    env_path = cwd / '.env'

    if not env_path.exists():
        console.print("[red].env file not found[/red]")
        console.print("Run 'multiagent env-init' to generate environment configuration")
        return

    console.print(f"[bold blue]Validating environment configuration in: {cwd}[/bold blue]\n")

    # Load current environment
    env_vars = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        console.print(f"[red]Error reading .env file: {e}[/red]")
        return

    # Run validation
    detector = ProjectDetector(cwd)
    analyzer = TechStackAnalyzer(detector)
    generator = EnvironmentGenerator(analyzer)

    errors = generator.validate_environment(env_vars)

    if errors:
        console.print("[red]Environment validation failed:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        console.print(f"\nRun 'multiagent env-init --interactive' to fix configuration")
    else:
        console.print("[green]Environment configuration is valid![/green]")
        console.print(f"Found {len(env_vars)} configured variables")

@main.command()
def env_templates():
    """List available environment templates"""
    template_manager = TemplateManager()
    templates = template_manager.list_templates()

    console.print("[bold blue]Available Environment Templates:[/bold blue]\n")

    table = Table()
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Frameworks", style="dim")

    for template in templates:
        table.add_row(template['name'], template['description'], template['frameworks'])

    console.print(table)
    console.print("\nUse: [cyan]multiagent env-init --template <name>[/cyan] to use a specific template")

@main.command()
def version_info():
    """Show detailed version information"""
    console.print(f"[bold blue]MultiAgent Core Version Information[/bold blue]\n")

    version_data = _load_version_metadata()

    if version_data:
        console.print(f"Version: [cyan]{version_data.get('version', 'unknown')}[/cyan]")
        console.print(f"Commit: [dim]{version_data.get('commit', 'unknown')}[/dim]")
        console.print(f"Build Date: [dim]{version_data.get('build_date', 'unknown')}[/dim]")
        console.print(f"Build Type: [dim]{version_data.get('build_type', 'unknown')}[/dim]")
    else:
        console.print(f"Version: [cyan]{__version__}[/cyan]")
        console.print("[dim]No detailed version information available[/dim]")
    
    console.print(f"\nInstallation: [cyan]pipx upgrade multiagent-core[/cyan] to update")

@main.command()
def doctor():
    """Comprehensive environment and package health check"""
    console.print("[bold blue]Multi-Agent Environment Health Check[/bold blue]\n")

    # Check Python version
    import sys
    console.print(f"Python: {sys.version.split()[0]}")

    # Check installed packages and versions
    packages = ['multiagent-core', 'multiagent-agentswarm', 'multiagent-devops', 'multiagent-testing']

    table = Table(title="Package Status")
    table.add_column("Package", style="cyan")
    table.add_column("Installed", style="green")
    table.add_column("Latest", style="yellow")
    table.add_column("Status", style="bold")

    for package in packages:
        try:
            current = metadata.version(package)
            latest = _get_latest_version(package)

            if latest and current != latest:
                status = "[red]Update Available[/red]"
            else:
                status = "[green]Up to Date[/green]"

            table.add_row(package, current, latest or "Unknown", status)
        except metadata.PackageNotFoundError:
            table.add_row(package, "[red]Not Installed[/red]", "Unknown", "[red]Missing[/red]")

    console.print(table)

    # Check spec-kit installation (REQUIRED)
    console.print("\n[bold]Spec-Kit Status (REQUIRED):[/bold]")
    spec_available, spec_path = _spec_kit_available()
    if spec_available:
        location = f" (at {spec_path})" if spec_path else ""
        console.print(f"spec-kit: [green]Available[/green]{location}")
    else:
        if spec_path:
            console.print(f"[yellow]spec-kit executable located at {spec_path} but failed to run[/yellow]")
        else:
            console.print("[red]spec-kit: Not detected on PATH[/red]")
        console.print("[yellow]Install with: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git[/yellow]")

    # Check available AI CLIs
    console.print("\n[bold]AI Assistant CLI Status:[/bold]")
    ai_status = _detect_available_clis()
    for cli, status in ai_status.items():
        if status['available']:
            console.print(f"{cli}: [green]{status['version']}[/green]")
        else:
            console.print(f"{cli}: [red]Not available[/red]")

    # Check GitHub CLI
    console.print("\n[bold]GitHub CLI Status:[/bold]")
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split()[2] if len(result.stdout.split()) > 2 else "unknown"
            console.print(f"GitHub CLI: [green]{version}[/green]")
        else:
            console.print("[red]GitHub CLI: Not found[/red]")
    except FileNotFoundError:
        console.print("[red]GitHub CLI: Not installed[/red]")

    # Check framework status
    console.print("\n[bold]Framework Status:[/bold]")
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if multiagent_dir.exists():
        console.print("[green]Framework: Initialized[/green]")
        registry = _load_components_registry(cwd)

        if registry:
            enriched_registry = _apply_framework_metadata(dict(registry))
            if enriched_registry != registry:
                try:
                    _write_components_registry(cwd, enriched_registry)
                except OSError:
                    pass
            registry = enriched_registry

            install_order = registry.get("installation_order", [])
            components_map = registry.get("components", {})

            if install_order:
                console.print(f"Components (installation order): {', '.join(install_order)}")
            elif isinstance(components_map, dict) and components_map:
                console.print(f"Components: {', '.join(sorted(components_map.keys()))}")
            else:
                console.print("[yellow]Components: Registry present but empty[/yellow]")

            recorded_version = registry.get("framework_version", "unknown")
            if recorded_version != "unknown":
                console.print(f"Framework version recorded in registry: [cyan]{recorded_version}[/cyan]")

            metadata_blob = registry.get("framework_version_metadata")
            if isinstance(metadata_blob, dict) and metadata_blob:
                commit = metadata_blob.get("commit")
                build_date = metadata_blob.get("build_date")
                details = []
                if commit:
                    details.append(f"commit [dim]{commit}[/dim]")
                if build_date:
                    details.append(f"built [dim]{build_date}[/dim]")
                if details:
                    console.print("; ".join(details))
        else:
            console.print("[yellow]Components: No registry found[/yellow]")
    else:
        console.print("[red]Framework: Not initialized[/red]")
        console.print("Run 'multiagent init' to get started")

    # Check git hooks status
    console.print("\n[bold]Git Hook Status:[/bold]")
    git_hooks_dir = cwd / '.git' / 'hooks'

    if not git_hooks_dir.exists():
        console.print("[yellow]Not a git repository - hooks not applicable[/yellow]")
    else:
        expected_hooks = {
            'pre-push': ('Secret scanning before push', ['secret', 'security', 'MultiAgent']),
            'post-commit': ('Agent workflow guidance', ['agent', 'workflow', 'Post-commit'])
        }

        hooks_healthy = True

        for hook_name, (description, keywords) in expected_hooks.items():
            hook_path = git_hooks_dir / hook_name

            if hook_path.exists() and os.access(hook_path, os.X_OK):
                # Verify content
                try:
                    with open(hook_path, 'r') as f:
                        content = f.read()
                        has_keywords = any(keyword in content for keyword in keywords)

                        if has_keywords:
                            console.print(f"{hook_name}: [green]Active[/green] ({description})")
                        else:
                            console.print(f"{hook_name}: [yellow]Installed but may be incorrect[/yellow]")
                            hooks_healthy = False
                except Exception:
                    console.print(f"{hook_name}: [yellow]Could not verify[/yellow]")
                    hooks_healthy = False
            else:
                console.print(f"{hook_name}: [red]Missing or not executable[/red]")
                hooks_healthy = False

        if not hooks_healthy:
            console.print("[dim]Run 'multiagent init' to reinstall hooks[/dim]")

@click.group()
def feedback():
    """Commands for handling feedback."""
    pass


@feedback.command()
@click.option('--pr-number', required=True, type=int, help='The pull request number.')
@click.option('--repo-name', required=True, help='The repository name in format owner/repo.')
@click.option('--json', 'json_output', is_flag=True, help='Output feedback in JSON format.')
def monitor(pr_number, repo_name, json_output):
    """Monitor a pull request for new feedback."""
    try:
        from github import Github
        import json as json_lib

        g = Github(os.environ["GITHUB_TOKEN"])
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        comments = pr.get_issue_comments()
        
        feedback_list = []
        for comment in comments:
            if "claude" in comment.user.login.lower():
                feedback_list.append({
                    "user": comment.user.login,
                    "body": comment.body,
                    "created_at": comment.created_at.isoformat()
                })

        if json_output:
            console.print(json_lib.dumps(feedback_list, indent=2))
        else:
            console.print(f"[bold green]Monitoring PR #{pr_number} for feedback...[/bold green]")
            for feedback in feedback_list:
                console.print(Panel(feedback["body"], title=f"Feedback from @{feedback['user']}", border_style="yellow"))

    except ImportError:
        console.print("[bold red]Error: PyGithub is not installed. Please run 'pip install PyGithub'.[/bold red]")
        exit(1)
    except KeyError as e:
        console.print(f"[bold red]Environment variable error: {e}[/bold red]")
        exit(1)
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        exit(1)


main.add_command(feedback)

def _detect_available_clis():
    """Detect available AI assistant CLIs using non-interactive checks."""

    def _build_search_path() -> str:
        """Return a PATH string that includes common install prefixes."""
        current = os.environ.get("PATH", "")
        paths = [p for p in current.split(os.pathsep) if p]
        seen = set(paths)

        extra_templates = [
            os.path.expanduser("~/.npm-global/bin"),
            os.path.expanduser("~/.local/bin"),
            "/usr/local/bin",
        ]

        nvm_root = Path(os.path.expanduser("~/.nvm/versions/node"))
        if nvm_root.exists():
            for version_dir in nvm_root.iterdir():
                bin_dir = version_dir / "bin"
                if bin_dir.is_dir():
                    extra_templates.append(str(bin_dir))

        for template in extra_templates:
            for candidate in glob.glob(template):
                if candidate and candidate not in seen and Path(candidate).is_dir():
                    seen.add(candidate)
                    paths.append(candidate)

        return os.pathsep.join(paths)

    def _extract_version(raw: str) -> str | None:
        tokens = raw.strip().split()
        for token in tokens:
            if any(char.isdigit() for char in token) and any(ch == '.' for ch in token):
                return token.strip("()")
        return raw.strip() or None

    def _detect(commands: list[str]) -> tuple[bool, str | None]:
        search_path = _build_search_path()
        for cmd in commands:
            exe = which(cmd, path=search_path)
            if not exe:
                continue
            try:
                result = subprocess.run(
                    [exe, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    env={**os.environ, "PATH": search_path},
                )
            except subprocess.TimeoutExpired:
                # Command exists but timed out - still treat as available
                return True, "Available"
            except FileNotFoundError:
                continue

            if result.returncode == 0:
                version = _extract_version(result.stdout or result.stderr)
                return True, version or "Available"

            # Non-zero return code but executable exists – treat as available
            return True, "Available"

        return False, None

    status = {}
    cli_checks = {
        "Gemini CLI": ["gemini"],
        "Qwen CLI": ["qwen"],
        "Codex CLI": ["codex"],
        "GitHub Copilot": ["gh"],
        "Claude Code": ["claude"],
    }

    for cli_name, commands in cli_checks.items():
        available, version = _detect(commands)
        status[cli_name] = {"available": available, "version": version}

    if status["GitHub Copilot"].get("available"):
        gh_path = which("gh", path=_build_search_path())
        if gh_path:
            try:
                result = subprocess.run(
                    [gh_path, "extension", "list"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                output = result.stdout.lower()
                if "github/gh-copilot" in output or "copilot" in output:
                    status["GitHub Copilot"] = {"available": True, "version": "Available (with Copilot)"}
                else:
                    status["GitHub Copilot"] = {"available": True, "version": "Available (no Copilot extension)"}
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                status["GitHub Copilot"] = {"available": True, "version": "Available"}

    openai_available, openai_version = _detect(["openai", "openai-cli"])
    status["OpenAI CLI"] = {"available": openai_available, "version": openai_version}

    return status

def _recommend_additional_components(project_path):
    """Simple component recommendations based on CLI availability"""
    console.print("\n[bold]Checking for additional component recommendations...[/bold]")

    # Check available CLIs
    available_clis = _detect_available_clis()
    available_count = sum(1 for cli in available_clis.values() if cli['available'])

    # Show available CLIs
    for cli, status in available_clis.items():
        if status['available']:
            console.print(f"[green]FOUND[/green] {cli}: {status['version']}")
        else:
            console.print(f"[red]MISSING[/red] {cli}: Not available")

    # Check installed components
    console.print(f"\n[bold]MultiAgent Components Status:[/bold]")
    components = ['multiagent-devops', 'multiagent-testing', 'multiagent-agentswarm']
    
    for component in components:
        try:
            version = metadata.version(component)
            console.print(f"  • [cyan]{component}[/cyan]: [green]Installed (v{version})[/green]")
        except metadata.PackageNotFoundError:
            if component == 'multiagent-devops':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Advanced CI/CD and deployment automation")
                console.print(f"    Install: [dim]pipx install multiagent-devops[/dim]")
                console.print(f"    Initialize: [dim]{_get_python_command()} -m multiagent_devops.cli init[/dim]")
            elif component == 'multiagent-testing':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Comprehensive test automation")
                console.print(f"    Install: [dim]pipx install multiagent-testing[/dim]")
                console.print(f"    Initialize: [dim]{_get_python_command()} -m multiagent_testing.cli init[/dim]")
            elif component == 'multiagent-agentswarm':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Multi-agent coordination and orchestration")
                console.print(f"    Install: [dim]pipx install multiagent-agentswarm[/dim]")

    if available_count > 0:
        console.print(f"    [dim]({available_count} AI assistant CLI(s) detected for enhanced coordination)[/dim]")

    console.print("\n[green]Core framework ready! Install components as needed.[/green]")

# Component installation removed - users install components manually when needed

def _get_latest_version(package_name):
    """Get latest version of package from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def _get_python_command():
    """Get the appropriate python command - simplified since pipx handles environment isolation"""
    return 'python'

def _check_python_environment():
    """Check Python environment - simplified since pipx handles isolation"""
    # pipx handles environment isolation automatically, so no complex checks needed
    pass

def _check_for_updates_async():
    """Spawn a non-blocking update check if allowed by configuration."""

    if config.skip_version_check or os.environ.get("CI"):
        return

    def _worker() -> None:
        try:
            checker = UpdateChecker()
            updates = checker.check()
            if not updates:
                return

            # Respect non-interactive runs
            if not config.interactive:
                return

            message_lines = [
                f"[yellow]{update.package}[/yellow]: {update.current} → {update.latest}"
                for update in updates
            ]
            message_lines.append("[dim]Run `multiagent upgrade` to apply updates.[/dim]")
            console.print(Panel("\n".join(message_lines), title="Updates available", style="yellow", expand=False))
        except Exception:
            # Never interrupt CLI flow because of update checks
            pass

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

def _convert_path_for_windows_tools(path):
    """Convert paths for Windows tools like gh CLI - handles all WSL scenarios"""
    path_str = str(path)

    # Handle different WSL path formats
    if '\\\\wsl.localhost\\' in path_str:
        # Format: \\wsl.localhost\Ubuntu\tmp\test -> C:\Users\user\AppData\Local\Temp\test
        # Extract the Linux path part
        linux_path = path_str.replace('\\\\wsl.localhost\\Ubuntu', '').replace('\\', '/')

        # Try to convert using wslpath
        try:
            result = subprocess.run(['wslpath', '-w', linux_path], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Fallback: if in /tmp, map to Windows temp
        if linux_path.startswith('/tmp/'):
            import tempfile
            windows_temp = tempfile.gettempdir()
            relative_path = linux_path[5:]  # Remove /tmp/
            windows_path = os.path.join(windows_temp, relative_path).replace('/', '\\')

            # Create the directory in Windows if it doesn't exist
            try:
                os.makedirs(windows_path, exist_ok=True)
            except:
                pass

            return windows_path

    elif hasattr(os, 'uname') and 'Microsoft' in os.uname().release:
        # Running directly in WSL - convert to Windows path
        try:
            result = subprocess.run(['wslpath', '-w', path_str], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

    # If all else fails, return original path
    return path_str

def _should_create_github_repo():
    """Interactive prompt to ask if user wants to create GitHub repository"""
    if not config.interactive:
        return False

    while True:
        response = input("Create GitHub repository? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            console.print("Please enter 'y' for yes or 'n' for no")

def _copy_non_destructive(src, dest, console):
    """
    Recursively copy files and directories.
    Does not overwrite existing files EXCEPT for agent template files.
    Agent templates (.multiagent/templates/*.md and .multiagent/docs/*.md) are always updated.
    """
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            _copy_non_destructive(s, d, console)
    else:
        # Check if this is an agent template file that should always be updated
        dest_path = Path(dest)
        relative_to_multiagent = None
        
        # Find if this file is under .multiagent/templates or .multiagent/docs
        for parent in dest_path.parents:
            if parent.name == '.multiagent':
                relative_to_multiagent = dest_path.relative_to(parent)
                break
        
        # Always overwrite agent template files and documentation
        should_overwrite = False
        if relative_to_multiagent:
            path_str = str(relative_to_multiagent)
            # Overwrite all markdown files in templates/ and docs/ directories
            if (path_str.startswith('templates/') and path_str.endswith('.md')) or \
               (path_str.startswith('docs/') and path_str.endswith('.md')) or \
               path_str == 'README.md':  # Also update .multiagent/README.md
                should_overwrite = True
        
        if should_overwrite:
            shutil.copy2(src, dest)
            # console.print(f"[green]Updated: {dest}[/green]")  # Optional: show updates
        elif not os.path.exists(dest):
            shutil.copy2(src, dest)
        else:
            # This is noisy, let's keep it off for now.
            # console.print(f"[dim]Skipped existing file: {dest}[/dim]")
            pass


def _install_git_hooks_from_templates(cwd, templates_root, console):
    """Install git hooks from .multiagent/security/hooks/ and .multiagent/agents/hooks/ to .git/hooks/"""

    # Check if we're in a git repository
    git_hooks_dir = cwd / '.git' / 'hooks'
    if not git_hooks_dir.exists():
        console.print("[yellow]⚠️  Not a git repository - skipping git hooks installation[/yellow]")
        console.print("[dim]   Run 'git init' first to enable git hooks[/dim]")
        return

    console.print("🔗 Installing git hooks...")

    # Define hooks to install from subsystems
    # Format: (subsystem_path, hook_name, description)
    hooks_to_install = [
        (('.multiagent', 'security', 'hooks'), 'pre-push', 'Secret scanning before push'),
        (('.multiagent', 'agents', 'hooks'), 'post-commit', 'Agent workflow guidance'),
    ]

    hooks_installed = 0
    hooks_failed = []

    for hook_path_parts, hook_name, description in hooks_to_install:
        try:
            # Build path to hook in package templates
            hooks_resource = templates_root.joinpath(*hook_path_parts, hook_name)

            with importlib_resources.as_file(hooks_resource) as hook_src_path:
                hook_src_path = Path(hook_src_path)

                if not hook_src_path.exists():
                    hooks_failed.append((hook_name, "not found in templates"))
                    continue

                hook_dest = git_hooks_dir / hook_name

                # Copy the hook
                shutil.copy2(hook_src_path, hook_dest)

                # Make it executable
                hook_dest.chmod(0o755)

                console.print(f"  ✅ Installed {hook_name} hook ({description})")
                hooks_installed += 1

        except FileNotFoundError:
            hooks_failed.append((hook_name, "file not found"))
        except Exception as e:
            hooks_failed.append((hook_name, str(e)))

    if hooks_installed > 0:
        console.print(f"🎣 Installed {hooks_installed} git hooks successfully")
        console.print("[dim]   Git hooks will automatically run on commit/push[/dim]")

    if hooks_failed:
        console.print(f"[yellow]⚠️  Warning: {len(hooks_failed)} hooks could not be installed:[/yellow]")
        for hook_name, reason in hooks_failed:
            console.print(f"[dim]   - {hook_name}: {reason}[/dim]")

    if hooks_installed == 0:
        console.print("[yellow]No git hooks were installed[/yellow]")
        console.print("[dim]   Hooks may need to be installed manually from .multiagent/security/hooks/ and .multiagent/agents/hooks/[/dim]")


def _verify_hook_installation(cwd, console):
    """Verify hooks are installed correctly and provide basic content validation."""

    git_hooks_dir = cwd / '.git' / 'hooks'
    if not git_hooks_dir.exists():
        return

    console.print("\n🔍 Verifying hook installation...")

    hooks_to_verify = {
        'pre-push': ['secret', 'security', 'MultiAgent'],
        'post-commit': ['agent', 'workflow', 'Post-commit']
    }

    all_verified = True

    for hook_name, expected_keywords in hooks_to_verify.items():
        hook_path = git_hooks_dir / hook_name

        if hook_path.exists() and os.access(hook_path, os.X_OK):
            # Quick content verification
            try:
                with open(hook_path, 'r') as f:
                    content = f.read()
                    has_keywords = any(keyword in content for keyword in expected_keywords)

                    if has_keywords:
                        console.print(f"  ✅ {hook_name}: Installed and verified")
                    else:
                        console.print(f"  ⚠️  {hook_name}: Installed but content may be incorrect")
                        all_verified = False
            except Exception as e:
                console.print(f"  ⚠️  {hook_name}: Could not verify content ({e})")
                all_verified = False
        else:
            console.print(f"  ❌ {hook_name}: Missing or not executable")
            all_verified = False

    if all_verified:
        console.print("\n✨ All hooks verified successfully")
        console.print("[dim]   Hooks will run automatically on commit/push[/dim]")
    else:
        console.print("\n[yellow]⚠️  Some hooks may need attention[/yellow]")
        console.print("[dim]   Run 'multiagent doctor' for detailed diagnostics[/dim]")


def _run_documentation_bootstrap(cwd: Path) -> None:
    """Ensure documentation scaffolding exists after init."""
    doc_script = cwd / '.multiagent' / 'documentation' / 'scripts' / 'create-structure.sh'
    if not doc_script.exists():
        return

    console.print('[bold blue]Bootstrapping documentation scaffolding...[/bold blue]')
    try:
        subprocess.run([str(doc_script)], cwd=str(cwd), check=True)
    except subprocess.CalledProcessError as exc:
        console.print(
            f"[yellow]Warning: Documentation bootstrap failed ({exc.returncode}). "
            "Run the script manually if needed.[/yellow]"
        )
    else:
        console.print('[green]Documentation scaffolding ready[/green]')


def _generate_project_structure(cwd, backend_heavy=False):
    """Copy framework directories from package to target directory.

    This function implements location-independent initialization:

    1. Uses importlib to find installed package (works from ANY directory)
    2. Copies templates from multiagent_core/templates/ to target
    3. Runs interactive menu for project configuration
    4. Registers project for automatic template updates

    Location Independence:
        Uses importlib_resources.files() instead of relative paths,
        so 'multiagent init' works from any directory:
        - /tmp/test-project
        - /home/user/my-app
        - Anywhere else

    Package-Based Architecture:
        Post-init operations (like /project-setup) run sync_project.py
        FROM THE INSTALLED PACKAGE, not from copied files. This ensures:
        - Latest sync logic always used
        - No need to copy sync scripts to projects
        - Users never run sync manually

    Auto-Update Registration:
        Project path stored in ~/.multiagent-core-deployments.json
        Next 'python -m build' automatically syncs templates to ALL
        registered projects.

    Args:
        cwd (Path): Target directory (can be anywhere)

    Returns:
        None: Modifies filesystem directly, outputs status to console

    See Also:
        - auto_updater.register_deployment() - Registers for updates
        - build-system/README.md - Build system docs
        - _template_sync.py - Build-time template sync
    """
    console.print("🚀 Setting up MultiAgent framework...")

    # Use directories that actually ship with the package
    if backend_heavy:
        # Backend-heavy mode: skip frontend-focused directories
        dirs_to_copy = {
            ".multiagent": ".multiagent",
            ".claude": ".claude",
            ".github": ".github",
        }
        console.print("[dim]Skipping .vscode and docs/ (backend-heavy mode)[/dim]")
    else:
        # Full mode: include all directories
        dirs_to_copy = {
            ".multiagent": ".multiagent",
            ".claude": ".claude",
            ".vscode": ".vscode",
            ".github": ".github",
            "docs": "docs",
        }

    templates_root = importlib_resources.files("multiagent_core") / "templates"

    for src_rel_path, dest_dir_name in dirs_to_copy.items():
        console.print(f"📁 Setting up {dest_dir_name}/ directory...")
        try:
            resource = templates_root.joinpath(*Path(src_rel_path).parts)
            with importlib_resources.as_file(resource) as src_path:
                src_path = Path(src_path)
                if src_path.exists():
                    _copy_non_destructive(src_path, cwd / dest_dir_name, console)
                    console.print(f"✅ Merged {dest_dir_name} from package resources")
                else:
                    console.print(f"[yellow]Warning: Source directory not found for {dest_dir_name} at {src_path}[/yellow]")
        except FileNotFoundError:
            console.print(f"[yellow]Warning: Source directory not found for {dest_dir_name}[/yellow]")
        except Exception as e:
            console.print(f"[red]Error merging {dest_dir_name}: {e}[/red]")

    # Copy README template to .multiagent/ directory (not root)
    console.print("📄 Setting up .multiagent/README.md...")
    try:
        resource = templates_root.joinpath('.multiagent', 'README.md')
        with importlib_resources.as_file(resource) as readme_src_path:
            readme_src_path = Path(readme_src_path)
            dest_readme_path = cwd / '.multiagent' / 'README.md'
            dest_readme_path.parent.mkdir(exist_ok=True)
            if not dest_readme_path.exists():
                shutil.copy(readme_src_path, dest_readme_path)
                console.print("✅ Copied .multiagent/README.md")
            else:
                console.print("[dim]Skipped existing .multiagent/README.md[/dim]")
    except FileNotFoundError:
        console.print("[yellow]Warning: README.md template not found in package resources[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not copy .multiagent/README.md: {e}[/yellow]")

    # Handle copilot-instructions.md - append instead of overwrite
    console.print("📄 Setting up copilot instructions...")
    try:
        resource = templates_root.joinpath('.github', 'copilot-instructions.md')
        with importlib_resources.as_file(resource) as copilot_src_path:
            copilot_src_path = Path(copilot_src_path)
            dest_copilot_path = cwd / '.github' / 'copilot-instructions.md'
            dest_copilot_path.parent.mkdir(exist_ok=True)

            if dest_copilot_path.exists():
                with open(dest_copilot_path, 'a', encoding='utf-8') as f:
                    f.write('\n\n# MultiAgent Framework Instructions\n\n')
                    with open(copilot_src_path, 'r', encoding='utf-8') as src_f:
                        f.write(src_f.read())
                console.print("✅ Appended MultiAgent instructions to existing copilot-instructions.md")
            else:
                shutil.copy(copilot_src_path, dest_copilot_path)
                console.print("✅ Copied copilot-instructions.md")
    except FileNotFoundError:
        console.print("[yellow]Warning: copilot-instructions.md not found in package resources[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not handle copilot-instructions.md: {e}[/yellow]")

    # Install git hooks from templates (NEW!)
    _install_git_hooks_from_templates(cwd, templates_root, console)

    # Verify hooks are installed correctly
    _verify_hook_installation(cwd, console)

    console.print("🎉 MultiAgent framework setup complete!")
    return True


# Legacy feedback system - removed (no longer used)
# @main.group(name="agent-feedback")
# def agent_feedback() -> None:
#     """Interact with queued feedback routed to local agents."""
#
#
# @agent_feedback.command("pull")
# @click.option("--agent-id", required=True, help="Agent handle that should receive the feedback.")
# @click.option(
#     "--max-items",
#     default=1,
#     show_default=True,
#     type=int,
#     help="Maximum number of feedback messages to consume in one pull.",
# )
# @click.option(
#     "--json-output",
#     "as_json",
#     is_flag=True,
#     help="Return the feedback bundle as JSON for downstream automation.",
# )
# def agent_feedback_pull(agent_id: str, max_items: int, as_json: bool) -> None:
#     """Fetch pending feedback for a given agent from the routing queue."""
#
#     store = feedback_runtime.get_store()
#     try:
#         records = store.pop_feedback(agent_id, max_items=max_items)
#     except ValueError as exc:  # pragma: no cover - defensive guard
#         raise click.BadParameter(str(exc), param_hint="--max-items") from exc
#
#     if not records:
#         click.echo(f"No pending feedback for agent {agent_id}")
#         return
#
#     if as_json:
#         serialised = [
#             {
#                 "record_id": record.id,
#                 "received_at": record.received_at.isoformat(),
#                 **record.payload.to_dict(),
#             }
#             for record in records
#         ]
#         click.echo(json.dumps(serialised, indent=2))
#         return
#
#     for record in records:
#         console.print(f"[bold cyan]Feedback {record.id}[/bold cyan] → {record.payload.agent_id}")
#         console.print(f"[dim]Pull Request:[/dim] {record.payload.pull_request_id}")
#         console.print(f"[dim]Comment:[/dim] {record.payload.comment_id}")
#         console.print(record.payload.feedback_content)
#         console.print("")
#
#     remaining = store.pending_count(agent_id)
#     console.print(
#         f"[green]Delivered {len(records)} item(s). Remaining in queue: {remaining}[/green]"
#     )


def _create_github_repo(cwd):
    """Create a GitHub repository using the gh CLI."""
    repo_name = cwd.name
    console.print(f"Creating GitHub repository: {repo_name}")

    try:
        # Ensure we are in the correct directory
        os.chdir(cwd)

        # Command to create a private repo from the current directory
        command = [
            'gh', 'repo', 'create', repo_name,
            '--private',
            '--source', '.',
            '--push'
        ]

        # The GITHUB_TOKEN is read automatically by 'gh' from env variables
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(cwd)
        )
        console.print(f"[green]Successfully created and pushed to GitHub repository: {repo_name}[/green]")
        console.print(result.stdout)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to create GitHub repository: {e}[/red]")
        console.print(f"[red]stdout: {e.stdout}[/red]")
        console.print(f"[red]stderr: {e.stderr}[/red]")
    except FileNotFoundError:
        console.print("[red]Failed to create GitHub repository: 'gh' command not found.[/red]")
        console.print("[red]Please ensure the GitHub CLI is installed and in your PATH.[/red]")


def _should_install_git_hooks():
    """Interactive prompt to ask if user wants to install git hooks"""
    if not config.interactive:
        return True  # Default to installing git hooks in non-interactive mode

    while True:
        response = input("Install git hooks for multi-agent workflow? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            console.print("Please enter 'y' for yes or 'n' for no")

def _install_git_hooks(project_path):
    """Install git hooks for multi-agent development workflow using tracked directory approach"""
    console.print("Installing git hooks...")

    try:
        # Check if this is a git repository
        if not (project_path / '.git').exists():
            console.print("[yellow]No .git directory found - not a git repository?[/yellow]")
            return False

        # Create scripts/hooks directory for tracked hooks
        scripts_hooks_dir = project_path / 'scripts' / 'hooks'
        scripts_hooks_dir.mkdir(parents=True, exist_ok=True)
        
        console.print(f"[blue]Creating shared Git hooks in: {scripts_hooks_dir}[/blue]")

        # Generate pre-push hook for professional commit strategy
        pre_push_hook = scripts_hooks_dir / 'pre-push'
        pre_push_content = '''#!/bin/bash
# MultiAgent framework pre-push hook
# Provides guidance for professional commit accumulation

# Only guide on main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]]; then
    exit 0
fi

# Count commits to push
commits_to_push=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")

# Only guide if 1 or fewer commits
if [[ "$commits_to_push" -le 1 ]]; then
    echo "Professional Commit Strategy Guidance"
    echo "Commits to push: $commits_to_push"
    echo "For richer release notes, consider accumulating 3-6 commits"
    echo "Rich Release Pattern:"
    echo "   git commit -m 'fix(component): specific issue'"
    echo "   git commit -m 'feat(feature): new capability'"
    echo "   git commit -m 'docs: update guide'"
    echo "   git push  # <- Rich release (3+ bullets)"
    echo ""
    echo "🚀 Continue anyway? Proceeding in 3 seconds..."
    echo "   Press Ctrl+C to cancel, or wait to continue"

    # 3 second countdown
    for i in {3..1}; do
        echo -n "$i "
        sleep 1
    done
    echo ""
fi

exit 0
'''

        with open(pre_push_hook, 'w', encoding='utf-8', newline='\n') as f:
            f.write(pre_push_content)
        pre_push_hook.chmod(0o755)

        # Create post-commit hook for auto-build
        post_commit_hook = scripts_hooks_dir / "post-commit"
        post_commit_content = """#!/bin/bash

# Auto-build and update based on commit type
# This hook runs AFTER a commit is made

# Get the commit message
COMMIT_MSG=$(git log -1 --pretty=%B)

# Check if this is a meaningful commit that needs building
should_build=false

# ONLY skip build for these specific types that never need updates
if echo "$COMMIT_MSG" | grep -qE "^(test|style|wip|temp)(\\(.*\\))?:"; then
    # These are the ONLY commits we skip
    should_build=false
    echo "[AUTO-BUILD] Skipping build for test/style/wip/temp commit"
elif echo "$COMMIT_MSG" | grep -qE "^\\[skip[\\- ]ci\\]|\\[ci[\\- ]skip\\]"; then
    # Also skip if commit message has [skip ci] or [ci skip]
    should_build=false
    echo "[AUTO-BUILD] Skipping build due to [skip ci] flag"
else
    # BUILD for EVERYTHING ELSE: feat, fix, docs, chore, build, ci, refactor, perf, etc.
    should_build=true
    echo "[AUTO-BUILD] Detected meaningful commit - triggering build..."
fi

if [ "$should_build" = true ]; then
    echo "[AUTO-BUILD] Running python -m build to update all projects..."
    
    # Run the build
    python3 -m build
    
    if [ $? -eq 0 ]; then
        echo "[AUTO-BUILD] Build completed successfully!"
        echo "[AUTO-BUILD] All registered projects have been updated"
        
        # Auto-reinstall the local multiagent command
        echo "[AUTO-BUILD] Updating local multiagent command..."
        WHEEL_FILE=$(ls -t dist/multiagent_core-*.whl 2>/dev/null | head -1)
        
        if [ -n "$WHEEL_FILE" ]; then
            # Check if pipx is available
            if command -v pipx >/dev/null 2>&1; then
                # Use the current repo for reinstall (editable mode)
                pipx install -e . --force >/dev/null 2>&1
                if [ $? -eq 0 ]; then
                    echo "[AUTO-BUILD] Local multiagent command updated successfully!"
                else
                    echo "[AUTO-BUILD] Warning: Could not update local command (pipx reinstall failed)"
                fi
            else
                echo "[AUTO-BUILD] Warning: pipx not found - skipping local command update"
            fi
        else
            echo "[AUTO-BUILD] Warning: No wheel file found - skipping local command update"
        fi
    else
        echo "[AUTO-BUILD] Build failed - please run manually to debug"
        exit 0  # Don't fail the commit
    fi
else
    echo "[AUTO-BUILD] Skipping build for commit type: $(echo "$COMMIT_MSG" | head -1)"
fi
"""

        with open(post_commit_hook, 'w', encoding='utf-8', newline='\n') as f:
            f.write(post_commit_content)
        post_commit_hook.chmod(0o755)

        # Configure Git to use the tracked hooks directory
        console.print("[blue]Configuring Git to use project hooks directory...[/blue]")
        try:
            subprocess.run([
                'git', 'config', 'core.hooksPath', './scripts/hooks'
            ], cwd=str(project_path), check=True, capture_output=True)
            console.print("[green]Git configured to use ./scripts/hooks[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Could not configure hooks path: {e}[/yellow]")
            console.print("[dim]You can manually run: git config core.hooksPath ./scripts/hooks[/dim]")

        console.print("[green]Git hooks installed successfully![/green]")
        console.print("[dim]- Hooks location: scripts/hooks/ (tracked by Git)[/dim]")
        console.print("[dim]- pre-push: Professional commit strategy guidance[/dim]")
        console.print("[dim]- post-commit: Auto-build and template sync[/dim]")
        console.print("[dim]- Shared across all team members automatically[/dim]")
        return True

    except Exception as e:
        console.print(f"[red]Failed to install git hooks: {e}[/red]")
        return False

if __name__ == "__main__":
    main()
