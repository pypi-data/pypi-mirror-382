#!/usr/bin/env python3
"""
dbbasic CLI - Unix-style tool wrapper

Following the Unix philosophy:
1. Optional - Can use dbbasic without it
2. Simple - ~100 lines of code
3. Thin wrapper - Just automates Unix commands
4. Extensible - Modules can add commands
5. No magic - Everything is visible
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path


# Template locations
TEMPLATES_REPO = "https://github.com/askrobots/dbbasic-examples"
TEMPLATES_DIR = Path.home() / ".dbbasic" / "templates"


def ensure_templates():
    """Clone templates repo if not present"""
    if not TEMPLATES_DIR.exists():
        print("Downloading templates...")
        subprocess.run([
            'git', 'clone', TEMPLATES_REPO, str(TEMPLATES_DIR)
        ])
        print(f"Templates downloaded to {TEMPLATES_DIR}")


def cmd_new(args):
    """Create new app from template"""
    if len(args) < 2:
        print("Usage: dbbasic new <type> <name>")
        print("\nAvailable templates:")
        print("  blog        - WordPress-like blog")
        print("  microblog   - Twitter-like social app")
        print("  api         - REST API")
        print("  shop        - E-commerce")
        print("  intranet    - Basecamp-like project manager")
        print("\nRun 'dbbasic list' to see all templates")
        return

    template_type = args[0]
    app_name = args[1]

    ensure_templates()

    template_path = TEMPLATES_DIR / template_type
    if not template_path.exists():
        print(f"Template '{template_type}' not found")
        print("Run: dbbasic list")
        return

    # Copy template
    print(f"Creating {app_name} from {template_type} template...")
    try:
        shutil.copytree(template_path, app_name)
    except FileExistsError:
        print(f"Error: Directory '{app_name}' already exists")
        return

    # Remove .git
    git_dir = Path(app_name) / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)

    print(f"\n✓ Created {app_name}!")
    print(f"  cd {app_name}")
    print(f"  pip install -r requirements.txt")
    print(f"  python app.py")


def cmd_list(args):
    """List available templates"""
    ensure_templates()

    print("Available templates:\n")

    # Define templates and descriptions (fallback if repo not available)
    default_templates = {
        "blog": "WordPress-like blog (~200 lines)",
        "microblog": "Twitter-like social app (~300 lines)",
        "api": "REST API (~150 lines)",
        "shop": "E-commerce (~400 lines)",
        "intranet": "Basecamp-like project manager (~500 lines)",
    }

    found_templates = False
    if TEMPLATES_DIR.exists():
        for template in sorted(TEMPLATES_DIR.iterdir()):
            if template.is_dir() and not template.name.startswith('.'):
                found_templates = True
                readme = template / "README.md"
                description = default_templates.get(template.name, "No description")
                if readme.exists():
                    # Extract first line from README
                    first_line = readme.read_text().split('\n')[0].strip('# ')
                    if first_line:
                        description = first_line

                print(f"  {template.name:15} - {description}")

    if not found_templates:
        # Show default list
        for name, desc in default_templates.items():
            print(f"  {name:15} - {desc}")

    print("\nUsage: dbbasic new <type> <name>")


def cmd_run(args):
    """Run the app (optional, just 'python app.py' works too)"""
    if Path('app.py').exists():
        print("Starting app...")
        subprocess.run(['python', 'app.py'] + args)
    else:
        print("No app.py found in current directory")


def cmd_test(args):
    """Run tests"""
    if Path('tests').exists():
        print("Running tests...")
        subprocess.run(['pytest'] + args)
    else:
        print("No tests directory found")


def discover_commands():
    """
    Discover commands from installed modules

    Modules can provide CLI commands by including a cli.py with COMMANDS dict:

    # dbbasic_queue/cli.py
    def worker_command(args):
        '''Run the queue worker'''
        from .worker import process_jobs
        print("Starting queue worker...")
        while True:
            process_jobs()

    COMMANDS = {
        'queue:worker': worker_command,
        'queue:stats': stats_command,
    }
    """
    import importlib
    import pkg_resources

    commands = {}

    # Find all installed packages starting with dbbasic-
    # Use pkg_resources to find installed distributions
    try:
        for dist in pkg_resources.working_set:
            project_name = dist.project_name
            if project_name.startswith('dbbasic-'):
                # Convert package name to module name (dbbasic-queue -> dbbasic_queue)
                module_name = project_name.replace('-', '_')
                try:
                    # Try to import module.cli
                    module = importlib.import_module(f'{module_name}.cli')
                    if hasattr(module, 'COMMANDS'):
                        commands.update(module.COMMANDS)
                except (ImportError, AttributeError):
                    pass  # Module doesn't have CLI commands
    except Exception:
        # Fallback: try common module names
        for module_name in ['dbbasic_queue', 'dbbasic_logs', 'dbbasic_accounts', 'dbbasic_web']:
            try:
                module = importlib.import_module(f'{module_name}.cli')
                if hasattr(module, 'COMMANDS'):
                    commands.update(module.COMMANDS)
            except (ImportError, AttributeError):
                pass

    return commands


def print_help():
    """Print help message"""
    print("Usage: dbbasic <command> [args]")
    print("\nCore commands:")
    print("  new <type> <name>  - Create new app from template")
    print("  list               - List available templates")
    print("  run                - Run the app")
    print("  test               - Run tests")

    # Discover module commands
    commands = discover_commands()
    if commands:
        print("\nModule commands:")
        for name in sorted(commands.keys()):
            cmd = commands[name]
            doc = cmd.__doc__ or "No description"
            # Get first line of docstring
            doc_first_line = doc.strip().split('\n')[0]
            print(f"  {name:20} - {doc_first_line}")

    print("\nRun 'dbbasic <command> --help' for command-specific help")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    # Core commands
    if command in ['help', '--help', '-h']:
        print_help()
    elif command == 'new':
        cmd_new(args)
    elif command == 'list':
        cmd_list(args)
    elif command == 'run':
        cmd_run(args)
    elif command == 'test':
        cmd_test(args)
    else:
        # Try module commands
        commands = discover_commands()
        if command in commands:
            commands[command](args)
        else:
            print(f"Unknown command: {command}")
            print("Run 'dbbasic help' to see available commands")
            sys.exit(1)


if __name__ == '__main__':
    main()
