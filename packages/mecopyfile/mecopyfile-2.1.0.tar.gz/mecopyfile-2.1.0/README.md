# PyFile

A modern Python library for intuitive file and directory manipulation with an object-oriented approach and advanced automation capabilities.

## Overview

PyFile provides a clean, object-oriented interface for file system operations in Python. Built on top of `pathlib`, it offers enhanced functionality for managing files and directories with support for recursive operations, content manipulation, structured data retrieval, and automated directory bootstrapping.

The library features a well-architected design with a base `Systorage` class that provides common functionality for both `File` and `Directory` objects, along with a custom `Path` wrapper for advanced path operations and cross-platform compatibility.

## Features

### 🗂️ **File Management**
- Create, read, write, and delete files with safety checks
- Content manipulation (append, overwrite, clear)
- File metadata access (name, extension, path)
- Safe file operations with existence validation
- Extension-based file processing

### 📁 **Directory Operations**
- Recursive directory traversal with auto-loading
- Bulk file and subdirectory management
- Segmented and flat result formats for organized processing
- Auto-loading capabilities for instant directory exploration
- Hierarchical data structure support

### 🛤️ **Advanced Path Handling**
- Cross-platform path normalization with universal format
- Custom Path wrapper around pathlib for enhanced functionality
- Recursive path exploration with filtering
- Automated directory and file object creation
- Path validation and existence checking

### 🏗️ **Architecture & Design**
- Object-oriented design with inheritance hierarchy
- Base Systorage class for common functionality
- Composition pattern for path management
- Template method pattern for directory loading
- Strategy pattern for flexible data segmentation

### 🔧 **Utility Functions**
- List flattening for nested recursive structures
- Recursive operations with segmentation support
- Flexible data organization and processing
- Automated directory bootstrapping from path lists

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pyfile

# Install in development mode
pip install -e .
```

## Quick Start

### Basic File Operations

```python
import pyfile

# Create a file object
file = pyfile.File("example.txt")

# Create the file if it doesn't exist
file.create()

# Write content
file.write("Hello, World!")

# Read content
content = file.read_to_end()
print(content)  # Output: Hello, World!

# Get file information
print(file.get_name())        # Output: example
print(file.get_extension())   # Output: .txt
print(file.get_path())        # Output: example.txt
```

### Directory Management with Auto-Loading

```python
import pyfile

# Auto-load directory contents on initialization
directory = pyfile.Directory("my_project", auto_load=True)

# Get all files recursively with segmentation
file_data = directory.get_files_paths(
    recursively=True, 
    segmentation=True
)
# Returns: [{"my_project": ["file1.txt", "file2.py"]}, ...]

# Get directory objects for further processing
subdirs = directory.get_directories(recursively=True)
for subdir in subdirs:
    print(f"Found subdirectory: {subdir.get_path()}")

# Process files with extension filtering
all_files = directory.get_files(recursively=True)
for file in all_files:
    if file.get_extension() == '.py':
        content = file.read_to_end()
        print(f"Python file: {file.get_name(with_extension=True)}")
```

### Automated Directory Bootstrap

```python
import pyfile

# Bootstrap multiple directory structures from a list of paths
project_paths = [
    "/path/to/project1",
    "/path/to/project2", 
    "/path/to/project3"
]

# Auto-load all directories and get their structures
all_directories = []
for path in project_paths:
    path_obj = pyfile.Path(path)
    directories = path_obj.get_directories(recursively=True)
    all_directories.extend(directories)

# Process all directories with auto-loading
for directory in all_directories:
    # Auto-load each directory's contents
    auto_dir = pyfile.Directory(directory.get_path(), auto_load=True)
    
    # Get all files in this directory structure
    files = auto_dir.get_files(recursively=True)
    print(f"Directory {auto_dir.get_path()} contains {len(files)} files")
```

### Advanced Path Operations

```python
import pyfile

# Working with paths for bulk operations
base_path = pyfile.Path("/workspace/projects")

# Get all directories recursively and auto-load them
all_dirs = base_path.get_directories(recursively=True)
auto_loaded_dirs = [pyfile.Directory(dir_path.get_path(), auto_load=True) for dir_path in all_dirs]

# Process each directory's contents with segmentation
for directory in auto_loaded_dirs:
    # Get files with segmentation for organized processing
    files_by_dir = directory.get_files(recursively=True, segmentation=True)
    
    # Process files in each directory
    for dir_files in files_by_dir:
        if isinstance(dir_files, dict):
            for dir_path, files in dir_files.items():
                print(f"Processing {len(files)} files in {dir_path}")
                
# Direct path-based file processing
all_files = base_path.get_files(recursively=True)
python_files = [f for f in all_files if f.get_extension() == '.py']
print(f"Found {len(python_files)} Python files")
```

### Batch File Operations

```python
import pyfile

# Process multiple files from different directories
source_dirs = ["/data/input1", "/data/input2", "/data/input3"]

# Auto-load all source directories
loaded_dirs = []
for dir_path in source_dirs:
    directory = pyfile.Directory(dir_path, auto_load=True)
    loaded_dirs.append(directory)

# Collect all files from all directories
all_files = []
for directory in loaded_dirs:
    files = directory.get_files(recursively=True)
    all_files.extend(files)

# Process files in batch with extension filtering
for file in all_files:
    if file.get_extension() == '.txt':
        content = file.read_to_end()
        # Process content...
        print(f"Processed: {file.get_path()}")
        
# Advanced: Process with segmentation for organized output
for directory in loaded_dirs:
    files_by_dir = directory.get_files(recursively=True, segmentation=True)
    for dir_data in files_by_dir:
        if isinstance(dir_data, dict):
            for dir_path, files in dir_data.items():
                print(f"Directory {dir_path}: {len(files)} files")
```

## API Reference

### Systorage Class (Base)

| Method              | Description                          |
| ------------------- | ------------------------------------ |
| `exists()`          | Check if the storage element exists  |
| `get_name()`        | Get the name of the element          |
| `get_parent_name()` | Get the parent directory name        |
| `get_path()`        | Get the full path as string          |
| `get_path_object()` | Get the internal pathlib.Path object |

### File Class

| Method                          | Description                                 |
| ------------------------------- | ------------------------------------------- |
| `create()`                      | Create the file if it doesn't exist         |
| `write(content)`                | Write content to file (overwrites existing) |
| `append(content)`               | Append content to file                      |
| `read_to_end(unexisting_raise)` | Read entire file content                    |
| `delete(delete_content)`        | Delete the file                             |
| `delete_content()`              | Clear file content without deleting         |
| `get_extension()`               | Get file extension with dot                 |
| `get_name(with_extension)`      | Get filename with/without extension         |

### Directory Class

| Method                                             | Description             |
| -------------------------------------------------- | ----------------------- |
| `load(recursive_load)`                             | Load directory contents |
| `get_files(recursively, segmentation)`             | Get file objects        |
| `get_files_paths(recursively, segmentation)`       | Get file paths          |
| `get_directories(recursively, segmentation)`       | Get directory objects   |
| `get_directories_paths(recursively, segmentation)` | Get directory paths     |

### Path Class

| Method                               | Description                          |
| ------------------------------------ | ------------------------------------ |
| `exists()`                           | Check if path exists                 |
| `get_name()`                         | Get the name component               |
| `get_parent_name()`                  | Get parent directory name            |
| `get_literal()`                      | Get the literal path string          |
| `get_internal()`                     | Get the internal pathlib.Path object |
| `get_files(recursively)`             | Get File objects from path           |
| `get_directories(recursively)`       | Get Directory objects from path      |
| `get_files_paths(recursively)`       | Get file paths from path             |
| `get_directories_paths(recursively)` | Get directory paths from path        |

## Use Cases

### 📊 **Data Processing & Analysis**
- Batch file operations with extension filtering
- Content analysis across multiple files recursively
- Automated file organization and categorization
- Data migration between directory structures

### 🗂️ **Project Management & Development**
- Project structure analysis with segmentation
- Asset collection and organization
- Build system integration with auto-loading
- Codebase exploration and documentation generation

### 🔍 **File System Exploration & Management**
- Directory tree analysis with hierarchical data
- File type filtering and processing
- Recursive content discovery and indexing
- Automated directory bootstrapping

### 🤖 **Automation & DevOps**
- Automated backup systems with batch processing
- File synchronization across multiple directories
- Content migration tools with segmentation
- CI/CD pipeline file processing

### 🏗️ **Enterprise Applications**
- Document management systems
- Asset management platforms
- Data pipeline processing
- Automated testing frameworks


## Architecture

PyFile is built with a clean, object-oriented architecture that follows established design patterns:

### **Inheritance Hierarchy**
```
Systorage (Base Class)
├── File (File operations)
└── Directory (Directory operations)

Path (Utility Class)
Utils (Helper Functions)
```

### **Design Patterns**
- **Composition**: Systorage uses Path objects for path management
- **Template Method**: Directory.load() follows a consistent pattern
- **Strategy**: Flexible segmentation and recursive options
- **Factory**: Path class creates File and Directory objects

### **Key Features**
- **Type Safety**: Full type hints with Python 3.7+ support
- **Error Handling**: Comprehensive validation and exception handling
- **Performance**: Optimized with pathlib and efficient algorithms
- **Cross-platform**: Universal path format for Windows/Unix compatibility

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.