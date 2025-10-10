# Sifts

Code analysis tool with YAML configuration support.

## Configuration

You can now run Sifts using a YAML configuration file:

```bash
python -m src.cli run-with-config config_example.yaml
````

### Configuration Format

The configuration file follows this structure:

```yaml
analysis:
  working_dir: "."              # Working directory (must exist)
  include_files:
    - "src/**/*.py"             # Glob patterns for files to include
  exclude_files:
    - "tests/**"                # Glob patterns for files to exclude
  lines_to_check:               # Specific lines to check in specific files (must exist)
    - file: "src/cli.py"
      lines: [12, 45, 78]
    - file: "src/config.py"     # You can specify multiple files
      lines: [10, 20]
    - file: "src/cli.py"        # Entries with the same file path will be merged
      lines: [100, 200]         # Will be combined with the previous entry for src/cli.py
  include_vulnerabilities:      # Types of vulnerabilities to check for
    - insecure_auth
    - sql_injection
    - xss
  exclude_vulnerabilities: []   # Types of vulnerabilities to exclude
  use_default_exclude_files: true  # Use default exclude files list
  split_subdirectories: true    # Split subdirectories for analysis

output:
  format: "json"                # Output format
  path: "reports/report.json"   # Output file path (directory will be created if needed)

runtime:
  parallel: true                # Whether to run in parallel
  threads: 4                    # Number of threads to use
```

## Line Merging

When multiple entries in `lines_to_check` reference the same file path, they will be automatically merged into a single entry with the combined list of line numbers. Duplicate line numbers are automatically removed, and the final list is sorted in ascending order.

For example, the above configuration will result in the following after processing:

```yaml
lines_to_check:
  - file: "src/cli.py"
    lines: [12, 45, 78, 100, 200]  # Combined from both entries
  - file: "src/config.py"
    lines: [10, 20]
```

## Path Validation

The configuration includes strict path validation:

### Paths that must exist (for analysis)

* Working directory (`working_dir`)
* Files specified in `lines_to_check`
* Exact file paths in `include_files` (non-glob patterns)

### Paths that will be created (for output)

* Output directory (parent directory of `output.path`)

The validation ensures that all files to be analyzed actually exist, while automatically creating any necessary output directories.

## Requirements

Install the required dependencies using Poetry:

```bash
poetry install
```
