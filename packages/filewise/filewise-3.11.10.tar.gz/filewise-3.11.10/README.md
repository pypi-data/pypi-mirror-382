# filewise

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/filewise.svg)](https://pypi.org/project/filewise/)

**filewise** is a comprehensive Python toolkit designed to simplify file operations, data manipulation, and scientific data processing. It provides a robust set of tools for file handling, directory management, format conversion, and data analysis, making it an essential utility package for Python developers working with diverse file types and data formats.

## Features

- **File Operations**:
  - Advanced bulk file renaming with automatic and manual modes
  - Intelligent file searching with glob patterns and extensions
  - File and directory permission management
  - Comprehensive file copying, moving, and synchronisation (rsync)
  - Path utilities with pattern matching and filtering

- **Format Converters**:
  - PDF manipulation: merging, compression, page extraction, and tweaking
  - Email format conversion: EML and MSG to PDF conversion
  - Document processing with external tool integration
  - Batch file format conversion capabilities

- **Data Processing**:
  - **Pandas utilities**: DataFrame manipulation, merging, time series standardisation
  - **Xarray utilities**: NetCDF file handling, climate data processing, coordinate operations
  - **JSON utilities**: Advanced JSON serialisation, encoding operations, DataFrame integration
  - Scientific data format conversion and analysis

- **Automation Scripts**:
  - Copy and compress workflows for file management
  - PDF processing automation (compression, tweaking, merging)
  - Bulk file operations with customisable parameters
  - Email conversion automation scripts

- **General Utilities**:
  - Function introspection and debugging tools
  - Memory usage analysis and object inspection
  - Dynamic function argument retrieval and validation

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **Required Third-Party Libraries**:

  ```bash
  pip install pandas numpy xarray netcdf4 openpyxl xlsxwriter odfpy
  ```

  Or via Anaconda (recommended channel: `conda-forge`):

  ```bash
  conda install -c conda-forge pandas numpy xarray netcdf4 openpyxl xlsxwriter odfpy
  ```

- **External Tools** (for PDF and email conversion):

  ```bash
  # Ubuntu/Debian
  sudo apt-get install ghostscript pdftk wkhtmltopdf poppler-utils

  # For email conversion
  sudo apt-get install libemail-address-xs-perl
  ```

- **Internal Package Dependencies**:

  ```bash
  pip install paramlib
  pip install pygenutils                    # Core functionality
  pip install pygenutils[arrow]             # With arrow support (optional)
  ```

### Installation Instructions

#### For regular users (from PyPI)

```bash
# Install filewise from PyPI (includes all dependencies)
pip install filewise
```

**Note:** The package now includes all dependencies with version constraints, so no additional installation steps are required.

#### For contributors/developers (with latest Git versions)

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/filewise.git
cd filewise

# Install with development dependencies (includes latest Git versions)
pip install -e .[dev]

# Alternative: Use requirements-dev.txt for explicit Git dependencies
pip install -r requirements-dev.txt
pip install -e .
```

**Benefits of the new approach:**

- **Regular users**: Simple `pip install filewise` with all dependencies included
- **Developers**: Access to latest Git versions for development and testing
- **PyPI compatibility**: All packages can be published without Git dependency issues

### Package Updates

To stay up-to-date with the latest version of this package, simply run:

```bash
pip install --upgrade filewise
```

## Development Setup

### For Contributors and Developers

If you're planning to contribute to the project or work with the source code, follow these setup instructions:

#### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/filewise.git
cd filewise

# Install with development dependencies (includes latest Git versions)
pip install -e .[dev]
```

**Note**: The `-e` flag installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling. The `[dev]` flag includes the latest Git versions of interdependent packages.

#### Alternative Setup (Explicit Git Dependencies)

If you prefer to use the explicit development requirements file:

```bash
# Clone the repository
git clone https://github.com/EusDancerDev/filewise.git
cd filewise

# Install development dependencies from requirements-dev.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .
```

This approach gives you the latest development versions of all interdependent packages for testing and development.

### Troubleshooting

If you encounter import errors after cloning:

1. **For regular users**: Run `pip install filewise` (all dependencies included)
2. **For developers**: Run `pip install -e .[dev]` to include development dependencies
3. **Verify Python environment**: Make sure you're using a compatible Python version (3.10+)

### Verify Installation

To verify that your installation is working correctly, you can run this quick test:

```python
# Test script to verify installation
try:
    import filewise
    from pygenutils.arrays_and_lists.data_manipulation import flatten_list
    from paramlib.global_parameters import BASIC_OBJECT_TYPES
    
    print("✅ All imports successful!")
    print(f"✅ filewise version: {filewise.__version__}")
    print("✅ Installation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 For regular users: pip install filewise")
    print("💡 For developers: pip install -e .[dev]")
```

### Implementation Notes

This project implements a **dual-approach dependency management** system:

- **Production Dependencies**: Version-constrained dependencies for PyPI compatibility
- **Development Dependencies**: Git-based dependencies for latest development versions
- **Installation Methods**:
  - **Regular users**: Simple `pip install filewise` with all dependencies included
  - **Developers**: `pip install -e .[dev]` for latest Git versions and development tools
- **PyPI Compatibility**: All packages can be published without Git dependency issues
- **Development Flexibility**: Contributors get access to latest versions for testing and development

## Usage

### Basic Example - File Operations

```python
from filewise.file_operations.path_utils import find_files
from filewise.file_operations.bulk_rename_auto import reorder_objs

# Find all PDF files in a directory
pdf_files = find_files(
    patterns="pdf",
    search_path="/path/to/documents",
    match_type="ext",
    top_only=False
)

# Automatically rename files with sequential numbering
reorder_objs(
    path="/path/to/documents",
    obj_type="file",
    extensions2skip="tmp",
    starting_number=1,
    zero_padding=3
)
```

### Advanced Example - PDF Processing

```python
from filewise.format_converters.pdf_tools import merge_files, file_compressor

# Merge multiple PDF files
pdf_list = ["document1.pdf", "document2.pdf", "document3.pdf"]
merge_files(
    in_path_list=pdf_list,
    out_path="merged_document.pdf"
)

# Compress PDF files
file_compressor(
    in_path="large_document.pdf",
    out_path="compressed_document.pdf"
)
```

### Data Processing Example - Pandas

```python
from filewise.pandas_utils.pandas_obj_handler import merge_excel_files, standardise_time_series
from filewise.pandas_utils.data_manipulation import sort_df_values

# Merge multiple Excel files
result = merge_excel_files(
    input_file_list=["data1.xlsx", "data2.xlsx"],
    output_file_path="merged_data.xlsx",
    save_merged_file=True
)

# Standardise time series data
standardised_df = standardise_time_series(
    dfs=[df1, df2, df3],
    date_value_pairs=[("date", "value1"), ("timestamp", "value2"), ("time", "value3")],
    handle_duplicates=True
)
```

### Scientific Data Example - Xarray

```python
from filewise.xarray_utils.file_utils import scan_ncfiles, ncfile_integrity_status
from filewise.xarray_utils.patterns import get_latlon_bounds
from filewise.xarray_utils.xarray_obj_handler import save2nc

# Scan NetCDF files in directory
file_info = scan_ncfiles("/path/to/netcdf/files")

# Check file integrity
dataset = ncfile_integrity_status("climate_data.nc")

# Extract coordinate bounds
lat_bounds, lon_bounds = get_latlon_bounds(
    nc_file="climate_data.nc",
    lat_dimension_name="latitude",
    lon_dimension_name="longitude"
)
```

### JSON Processing Example

```python
from filewise.json_utils.json_obj_handler import serialise_to_json, deserialise_json_to_df

# Serialise data to JSON with custom formatting
serialise_to_json(
    data={"results": [1, 2, 3], "metadata": {"version": "1.0"}},
    out_file_path="output.json",
    indent=2,
    sort_keys=True
)

# Convert JSON to DataFrame
df = deserialise_json_to_df(
    json_obj_list=["data1.json", "data2.json"],
    orient="records"
)
```

### Automation Script Example

```python
from filewise.scripts.copy_compress import _execute_copy_compress_workflow

# Execute automated file copy and compression workflow
# (Configure parameters in the script as needed)
_execute_copy_compress_workflow()
```

## Project Structure

The package is organised into specialised sub-packages for different file operations:

```text
filewise/
├── file_operations/
│   ├── bulk_rename_auto.py          # Automatic bulk file renaming
│   ├── bulk_rename_manual.py        # Manual file renaming templates
│   ├── cat_file_content.py          # File content display utilities
│   ├── ops_handler.py               # Core file operations (copy, move, sync)
│   ├── path_utils.py                # Path searching and pattern matching
│   └── permission_manager.py        # File/directory permission management
├── format_converters/
│   └── pdf_tools.py                 # PDF manipulation and conversion tools
├── pandas_utils/
│   ├── conversions.py               # DataFrame format conversions
│   ├── data_manipulation.py         # DataFrame operations and analysis
│   └── pandas_obj_handler.py        # Excel, CSV, ODS file handling
├── xarray_utils/
│   ├── conversions.py               # Climate data format conversion
│   ├── data_manipulation.py         # NetCDF data processing
│   ├── file_utils.py                # NetCDF file utilities and integrity checks
│   ├── patterns.py                  # Coordinate and dimension pattern analysis
│   └── xarray_obj_handler.py        # NetCDF file creation and manipulation
├── json_utils/
│   ├── json_encoding_operations.py  # Custom JSON encoding/decoding
│   └── json_obj_handler.py          # JSON file operations and DataFrame integration
├── general/
│   └── introspection_utils.py       # Function introspection and debugging
└── scripts/
    ├── bulk_rename.py               # Bulk renaming automation
    ├── compress_pdf.py              # PDF compression automation
    ├── copy_compress.py             # File copy and compression workflow
    ├── eml2pdf_exec.py             # Email to PDF conversion
    ├── modify_properties.py         # File property modification
    ├── msg2pdf_exec.py             # MSG to PDF conversion
    └── tweak_pdf.py                # PDF page manipulation
```

## Key Functions

### File Operations

- `find_files()` - Advanced file searching with pattern matching
- `reorder_objs()` - Automatic sequential file/directory renaming
- `rsync()` - Directory synchronisation with advanced options
- `modify_obj_permissions()` - Batch permission modification

### Format Conversion

- `merge_files()` - PDF merging with customisable options
- `file_compressor()` - PDF compression with quality control
- `eml_to_pdf()`, `msg_to_pdf()` - Email format conversion

### Data Processing

- `merge_excel_files()` - Multi-file Excel processing
- `standardise_time_series()` - Time series data normalisation
- `scan_ncfiles()` - NetCDF file analysis and cataloguing
- `get_latlon_bounds()` - Climate data coordinate extraction

### JSON Operations

- `serialise_to_json()` - Advanced JSON serialisation
- `deserialise_json_to_df()` - JSON to DataFrame conversion
- Custom encoding for complex Python objects

### Automation

- Ready-to-use scripts for common file operations
- Configurable workflows for batch processing
- Integration with system tools and external programs

## Advanced Features

### Defensive Programming

- Automatic nested list flattening for robust parameter handling
- Comprehensive error handling and validation
- Type checking and parameter validation

### Performance Optimisation

- LRU caching for pattern compilation
- Efficient file searching algorithms
- Memory-conscious data processing

### Scientific Data Support

- Climate data processing with coordinate system handling
- NetCDF file integrity checking and validation
- Advanced time series manipulation and standardisation

## Version Information

Current version: **3.10.0**

For detailed version history and changelog, see [CHANGELOG.md](CHANGELOG.md) and [VERSIONING.md](VERSIONING.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow the existing code structure and naming conventions
- Add comprehensive docstrings for new functions
- Include error handling and parameter validation
- Write tests for new functionality
- Update the changelog for significant changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NumPy and Pandas communities** for foundational data processing tools
- **Xarray developers** for climate and scientific data handling capabilities
- **Python packaging community** for best practices and standards
- **Open-source contributors** to file processing and automation tools

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.

## Dependencies

This package relies on several high-quality external packages:

- `pygenutils` - General utility functions and data manipulation
- `paramlib` - Parameter and configuration management
- Standard scientific Python stack (NumPy, Pandas, Xarray)
- External system tools for advanced file operations

## System Requirements

- Python 3.8 or higher
- Unix-like operating system (Linux, macOS) for full functionality
- Optional: External tools for PDF and email processing (ghostscript, pdftk, etc.)
