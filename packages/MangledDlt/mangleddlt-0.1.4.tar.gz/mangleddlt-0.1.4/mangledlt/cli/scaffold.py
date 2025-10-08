"""Scaffold DLT folder structure - Minimal implementation to pass tests"""
import os
import sys
from pathlib import Path


def scaffold_dlt_structure(base_path: str) -> None:
    """Create DLT folder structure with minimal implementation"""
    base = Path(base_path)

    # Create base directory if it doesn't exist
    base.mkdir(parents=True, exist_ok=True)

    # Create main folders
    (base / 'Exploration').mkdir(exist_ok=True)
    (base / 'Transformations').mkdir(exist_ok=True)
    utilities = base / 'Utilities'
    utilities.mkdir(exist_ok=True)

    # Create utilities subfolders
    views_dir = utilities / 'views'
    views_dir.mkdir(exist_ok=True)
    tables_dir = utilities / 'tables'
    tables_dir.mkdir(exist_ok=True)

    # Create utilities/__init__.py
    init_content = """from .views.example import example_view
from .tables.example import example_table"""
    (utilities / '__init__.py').write_text(init_content)

    # Create views/example.py
    view_content = """def example_view():
    df = spark.read.table("example_table")
    return df"""
    (views_dir / 'example.py').write_text(view_content)

    # Create tables/example.py
    table_content = """import sys
import os

# Needed so it will work both in a Declarative Pipeline and outside of it

sys.path.append(os.path.dirname(os.getcwd()))

try:
    from utils import *
    from views.example import example_view
except ModuleNotFoundError:
    from utilities.utils import *

def example_table():
    # Table definition function
    pass"""
    (tables_dir / 'example.py').write_text(table_content)

    # Create utils.py
    utils_content = """import sys
import subprocess
import logging
from datetime import datetime, timedelta
import os


from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql import Window
from pyspark.sql.functions import when
from pyspark.sql.types import *
from pyspark.sql import DataFrame

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()"""
    (utilities / 'utils.py').write_text(utils_content)

    # Create Transformations/view_example.py
    transformations_view_content = """from utilities import *

dlt.view(
    name = 'example_view',
)(example_view)"""
    (base / 'Transformations' / 'view_example.py').write_text(transformations_view_content)

    # Create Transformations/table_example.py
    transformations_table_content = """from utilities import *

dlt.table(
    name = 'main.example_table',
    comment="an example table",
    cluster_by_auto=True,
)(example_table)"""
    (base / 'Transformations' / 'table_example.py').write_text(transformations_table_content)


def _validate_project(project: str) -> tuple[Path, Path]:
    """Validate project structure and return base and utilities paths"""
    base = Path(project)

    if not base.exists():
        print(f"Error: Project '{project}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Check for both capitalized and lowercase versions
    utilities = base / 'Utilities'
    if not utilities.exists():
        utilities = base / 'utilities'
        if not utilities.exists():
            print(f"Error: Project '{project}' does not have a Utilities folder", file=sys.stderr)
            sys.exit(1)

    return base, utilities


def _update_init_file(utilities: Path, component_type: str, name: str) -> None:
    """Update __init__.py with new import"""
    init_file = utilities / '__init__.py'
    new_import = f"from .{component_type}s.{name} import {name}"

    if init_file.exists():
        existing_content = init_file.read_text()
        if new_import not in existing_content:
            updated_content = existing_content + f"\n{new_import}"
            init_file.write_text(updated_content)
    else:
        init_file.write_text(new_import)


def add_table(name: str, project: str) -> None:
    """Add a new table to an existing DLT project"""
    base, utilities = _validate_project(project)

    tables_dir = utilities / 'tables'
    tables_dir.mkdir(exist_ok=True)

    # Create the new table file
    table_file = tables_dir / f'{name}.py'
    if table_file.exists():
        print(f"Error: Table '{name}' already exists in project '{project}'", file=sys.stderr)
        sys.exit(1)

    table_content = f"""import sys
import os

# Needed so it will work both in a Declarative Pipeline and outside of it

sys.path.append(os.path.dirname(os.getcwd()))

try:
    from utils import *
except ModuleNotFoundError:
    from utilities.utils import *

def {name}():
    # Table definition function
    pass"""

    table_file.write_text(table_content)

    # Update __init__.py
    _update_init_file(utilities, 'table', name)

    # Create transformation file - check for existing folder casing
    transformations_dir = base / 'Transformations'
    if not transformations_dir.exists():
        transformations_dir = base / 'transformations'
    transformations_dir.mkdir(exist_ok=True)

    transformation_file = transformations_dir / f'table_{name}.py'
    transformation_content = f"""from utilities import *

dlt.table(
    name = '{name}',
    comment="",
    cluster_by_auto=True,
)({name})"""

    transformation_file.write_text(transformation_content)

    print(f"Successfully added table '{name}' to project '{project}'")


def add_view(name: str, project: str) -> None:
    """Add a new view to an existing DLT project"""
    base, utilities = _validate_project(project)

    views_dir = utilities / 'views'
    views_dir.mkdir(exist_ok=True)

    # Create the new view file
    view_file = views_dir / f'{name}.py'
    if view_file.exists():
        print(f"Error: View '{name}' already exists in project '{project}'", file=sys.stderr)
        sys.exit(1)

    view_content = f"""import sys
import os

# Needed so it will work both in a Declarative Pipeline and outside of it

sys.path.append(os.path.dirname(os.getcwd()))

try:
    from utils import *
except ModuleNotFoundError:
    from utilities.utils import *

def {name}():
    # View definition function
    pass"""

    view_file.write_text(view_content)

    # Update __init__.py
    _update_init_file(utilities, 'view', name)

    # Create transformation file - check for existing folder casing
    transformations_dir = base / 'Transformations'
    if not transformations_dir.exists():
        transformations_dir = base / 'transformations'
    transformations_dir.mkdir(exist_ok=True)

    transformation_file = transformations_dir / f'view_{name}.py'
    transformation_content = f"""from utilities import *

dlt.view(
    name = '{name}',
)({name})"""

    transformation_file.write_text(transformation_content)

    print(f"Successfully added view '{name}' to project '{project}'")