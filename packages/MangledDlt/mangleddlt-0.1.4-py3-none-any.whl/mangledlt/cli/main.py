"""Main CLI entry point for MangledDLT commands"""
import argparse
import sys
from pathlib import Path

try:
    from .scaffold import scaffold_dlt_structure, add_table, add_view
except ImportError:
    from scaffold import scaffold_dlt_structure, add_table, add_view


def main():
    """Main entry point for mangleddlt command"""
    parser = argparse.ArgumentParser(
        prog='mangleddlt',
        description='MangledDLT CLI - Local Databricks Development Bridge'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scaffold command
    scaffold_parser = subparsers.add_parser(
        'scaffold',
        help='Create a DLT folder structure for your project'
    )
    scaffold_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path where to create the DLT structure (default: current directory)'
    )

    # Add command with subcommands
    add_parser = subparsers.add_parser(
        'add',
        help='Add components to a DLT project'
    )
    add_subparsers = add_parser.add_subparsers(dest='add_type', help='Component types')

    # Add table subcommand
    table_parser = add_subparsers.add_parser(
        'table',
        help='Add a new table to the project'
    )
    table_parser.add_argument(
        'name',
        help='Name of the table to create'
    )
    table_parser.add_argument(
        'project',
        help='Path to the DLT project'
    )

    # Add view subcommand
    view_parser = add_subparsers.add_parser(
        'view',
        help='Add a new view to the project'
    )
    view_parser.add_argument(
        'name',
        help='Name of the view to create'
    )
    view_parser.add_argument(
        'project',
        help='Path to the DLT project'
    )

    args = parser.parse_args()

    if args.command == 'scaffold':
        try:
            path = Path(args.path).resolve()
            print(f"Creating DLT structure in {path}...")
            scaffold_dlt_structure(str(path))
            print("✓ DLT structure created successfully!")
            print("\nCreated folders:")
            print("  • Exploration/")
            print("  • Transformations/")
            print("  • Utilities/")
            print("    ├── views/")
            print("    ├── tables/")
            print("    ├── __init__.py")
            print("    ├── utils.py")
            print("    └── example files")
        except Exception as e:
            print(f"Error creating DLT structure: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == 'add':
        if args.add_type == 'table':
            try:
                add_table(args.name, args.project)
                sys.exit(0)
            except Exception as e:
                print(f"Error adding table: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.add_type == 'view':
            try:
                add_view(args.name, args.project)
                sys.exit(0)
            except Exception as e:
                print(f"Error adding view: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.add_type is None:
            add_parser.print_help()
            sys.exit(0)
    elif args.command is None:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()