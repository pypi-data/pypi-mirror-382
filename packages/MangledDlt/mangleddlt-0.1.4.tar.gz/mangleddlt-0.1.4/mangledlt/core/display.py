"""Display functionality for PySpark DataFrames."""

import os
import tempfile
import webbrowser
import threading
from typing import Optional, Any
import pyarrow as pa
from pyspark.sql import DataFrame


def is_databricks_runtime() -> bool:
    """Check if running in Databricks runtime."""
    DATABRICKS_ENV_VARS = [
        'DATABRICKS_RUNTIME_VERSION',
        'DB_IS_DRIVER',
        'DATABRICKS_SERVICE_HOST'
    ]

    # Check for Databricks-specific environment variables
    for var in DATABRICKS_ENV_VARS:
        if os.environ.get(var):
            return True

    # Check SPARK_HOME path
    spark_home = os.environ.get('SPARK_HOME', '')
    if spark_home.endswith('/databricks/spark'):
        return True

    return False


def databricks_display(df: DataFrame) -> None:
    """Use Databricks native display function."""
    # Import the Databricks display function
    try:
        from databricks.sdk.runtime import display
        display(df)
    except ImportError:
        # Fallback to just showing the DataFrame
        df.show()


def convert_to_arrow(df: DataFrame, max_rows: Optional[int] = None) -> pa.Table:
    """Convert PySpark DataFrame to Arrow format.

    Args:
        df: PySpark DataFrame to convert
        max_rows: Maximum number of rows to include (optional)

    Returns:
        PyArrow Table representation of the DataFrame
    """
    # Limit rows if specified
    if max_rows is not None:
        df = df.limit(max_rows)

    # Convert to Pandas first, then to Arrow
    pandas_df = df.toPandas()

    # Convert complex types to string representation
    for col in pandas_df.columns:
        if pandas_df[col].dtype == 'object':
            # Check if it's a complex type (list, dict, etc.)
            if _column_contains_complex_type(pandas_df[col]):
                pandas_df[col] = pandas_df[col].apply(_safe_str_convert)

    # Convert to Arrow
    return pa.Table.from_pandas(pandas_df)


def _column_contains_complex_type(column) -> bool:
    """Check if a column contains complex types like lists or dicts."""
    first_non_null = column.dropna().iloc[0] if not column.dropna().empty else None
    return first_non_null is not None and isinstance(first_non_null, (list, dict))


def _safe_str_convert(value: Any) -> Optional[str]:
    """Safely convert a value to string, handling None."""
    return str(value) if value is not None else None


def _serialize_arrow_to_base64(arrow_table: pa.Table) -> str:
    """Serialize Arrow table to base64 string."""
    import base64

    # Serialize Arrow table to bytes
    sink = pa.BufferOutputStream()
    writer = pa.RecordBatchStreamWriter(sink, arrow_table.schema)
    writer.write_table(arrow_table)
    writer.close()
    arrow_bytes = sink.getvalue().to_pybytes()

    # Convert bytes to base64 for embedding in HTML
    return base64.b64encode(arrow_bytes).decode('utf-8')


def generate_perspective_html(arrow_table: pa.Table, theme: str = 'light', enable_aggregates: bool = False) -> str:
    """Generate HTML content with Perspective viewer.

    Args:
        arrow_table: PyArrow Table to display
        theme: Color theme ('light' or 'dark')
        enable_aggregates: Whether to enable aggregation features

    Returns:
        HTML string with embedded Perspective viewer
    """
    arrow_base64 = _serialize_arrow_to_base64(arrow_table)

    # Generate HTML with Perspective viewer
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MangledDLT DataFrame Display</title>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@finos/perspective@3.1.0/dist/cdn/perspective.js"></script>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@finos/perspective-viewer@3.1.0/dist/cdn/perspective-viewer.js"></script>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-datagrid@3.1.0/dist/cdn/perspective-viewer-datagrid.js"></script>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@finos/perspective-viewer-d3fc@3.1.0/dist/cdn/perspective-viewer-d3fc.js"></script>
    <link rel="stylesheet" crossorigin="anonymous" href="https://cdn.jsdelivr.net/npm/@finos/perspective-viewer@3.1.0/dist/css/themes.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }}
        perspective-viewer {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            height: 100vh;
        }}
    </style>
</head>
<body>
    <perspective-viewer id="viewer" theme="{theme}"></perspective-viewer>
    <script type="module">
        import * as perspective from "https://cdn.jsdelivr.net/npm/@finos/perspective@3.1.0/dist/cdn/perspective.js";

        const viewer = document.getElementById('viewer');

        // Decode base64 Arrow data
        const base64ToArrayBuffer = (base64) => {{
            const binaryString = atob(base64);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {{
                bytes[i] = binaryString.charCodeAt(i);
            }}
            return bytes.buffer;
        }};

        const arrowData = base64ToArrayBuffer("{arrow_base64}");

        // Load data into Perspective
        async function loadData() {{
            try {{
                const worker = await perspective.default.worker();
                const table = await worker.table(arrowData);
                await viewer.load(table);

                // Configure aggregates if enabled
                if ({str(enable_aggregates).lower()}) {{
                    viewer.setAttribute('aggregates', JSON.stringify({{}}));
                }}
            }} catch (error) {{
                console.error('Error loading data:', error);
                document.body.innerHTML = '<h1>Error loading data</h1><pre>' + error.toString() + '</pre>';
            }}
        }}

        loadData();
    </script>
</body>
</html>"""

    return html_content


def cleanup_file(filepath: str) -> None:
    """Clean up temporary file after delay."""
    try:
        os.unlink(filepath)
    except:
        pass  # Ignore errors if file already deleted


def display_dataframe(df: DataFrame, max_rows: int = 10000, theme: str = 'light', enable_aggregates: bool = False) -> None:
    """Display a PySpark DataFrame using Perspective viewer."""
    if is_databricks_runtime():
        # Use native Databricks display
        databricks_display(df)
    else:
        # Convert to Arrow
        arrow_table = convert_to_arrow(df, max_rows=max_rows)

        # Generate HTML
        html = generate_perspective_html(arrow_table, theme=theme, enable_aggregates=enable_aggregates)

        # Determine temp directory - use user's home for WSL compatibility
        import platform
        if 'WSL' in platform.uname().release or 'microsoft' in platform.uname().release.lower():
            # In WSL, use home directory for Windows browser access
            temp_dir = os.path.expanduser('~')
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, dir=temp_dir)
        else:
            # Regular Linux/Mac
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)

        # Write HTML to file
        temp_path = temp_file.name
        temp_file.write(html)
        temp_file.flush()
        temp_file.close()

        # Verify file exists
        if not os.path.exists(temp_path):
            raise RuntimeError(f"Failed to create HTML file at {temp_path}")

        # Open in browser
        webbrowser.open(f'file://{temp_path}')

        # Keep file for longer to allow viewing
        print(f"HTML file saved at: {temp_path}")
        print("File will be automatically deleted in 30 minutes")
        print("If browser doesn't open, manually open the file above")

        # Schedule cleanup after 30 minutes
        timer = threading.Timer(1800, cleanup_file, args=[temp_path])
        timer.daemon = True
        timer.start()


# Monkey-patch DataFrame to add display method
def add_display_to_dataframe():
    """Add display method to PySpark DataFrame class."""
    def display(self, max_rows: int = 10000, theme: str = 'light', enable_aggregates: bool = False, **kwargs) -> None:
        """Display this DataFrame in a rich, interactive viewer."""
        display_dataframe(self, max_rows=max_rows, theme=theme, enable_aggregates=enable_aggregates)

    DataFrame.display = display


# Auto-patch when module is imported
add_display_to_dataframe()