# Product Requirements Document: lsa - Enhanced Directory Listing Tool

## 1. Introduction/Overview

`lsa` is a command-line utility written in C that wraps the standard `ls` command and presents directory listings in a cleaner, more organized table format. The tool addresses the need for developers to quickly scan directory contents with improved readability through consistent sorting, aligned columns, and visual enhancements.

**Problem Statement**: The default `ls` output can be difficult to parse visually, especially in directories with many files. Information is not always consistently aligned, and finding specific types of files (hidden files, directories) requires careful scanning.

**Solution**: `lsa` reformats `ls` output into a well-structured table with custom sorting rules, proper column alignment, color coding, and relative timestamps for improved usability.

## 2. Goals

1. Provide a cleaner, more readable alternative to standard `ls` output
2. Enable quick identification of directories vs files through sorting and color coding
3. Support flexible sorting options by different columns (name, size, date, permissions)
4. Maintain compatibility with standard Linux systems and easy installation
5. Parse and display directory listings with 100+ files efficiently

## 3. User Stories

1. **As a developer**, I want to see directories listed before files so that I can quickly identify subdirectories to navigate into.

2. **As a developer**, I want hidden files (starting with `.`) to be grouped together so that I can easily spot configuration files.

3. **As a developer**, I want to see relative timestamps (e.g., "2 hours ago") so that I can quickly identify recently modified files.

4. **As a developer**, I want columns to be properly aligned so that I can scan information vertically without eye strain.

5. **As a developer**, I want to sort the output by different criteria (size, date, permissions) so that I can find the largest files or most recently modified files quickly.

6. **As a developer**, I want directories to be color-coded so that I can visually distinguish them from regular files at a glance.

7. **As a system user**, I want the tool to install easily with standard make commands so that I can add it to my system without complex setup.

## 4. Functional Requirements

### Core Functionality

1. The program must be named `lsa` and written in C.

2. The program must execute `ls --alsh` internally to gather file information.

3. The program must capture and parse the complete output from `ls --alsh`.

4. The program must sort output according to the following rules:
   - `.` (current directory) appears first
   - `..` (parent directory) appears second
   - Directories appear next, sorted alphabetically
   - Files starting with `.` appear next, sorted alphabetically
   - All other files appear last, sorted alphabetically

### Output Format

5. The program must display results in a table with the following columns (left to right):
   - Name (truncated at 30 characters)
   - Permissions
   - Size
   - Date/Time (relative format: "2 hours ago", "3 days ago", etc.)
   - User:Group (display as "user:" when user and group are identical)

6. All columns must be left-aligned.

7. All columns must be padded to match the width of the maximum value in that column, except:
   - The name column must be truncated at 30 characters maximum

8. The date/time column must display relative time (e.g., "2 hours ago", "3 days ago", "just now").

### Visual Enhancements

9. The program must apply color coding to the output:
   - Directories: blue
   - Executables: green
   - Symbolic links: cyan
   - Other files: default terminal color
   - Follow standard `ls` color conventions

### Command-Line Interface

10. The program must support the following command-line flags:
    - `--sort-name` or `-n`: Sort by filename (default behavior)
    - `--sort-size` or `-s`: Sort by file size
    - `--sort-date` or `-d`: Sort by modification date/time
    - `--sort-permissions` or `-p`: Sort by permissions
    - `[directory]`: Optional directory path argument (defaults to current directory)

11. When sorting by non-name columns, the basic sorting rules (`.`, `..`, directories-first) must still apply as a primary sort, with the specified column as a secondary sort.

### Error Handling

12. If `ls` command fails or returns an error, the program must:
    - Print the error message from `ls` to stderr
    - Exit with the same error code that `ls` returned

13. The program must handle edge cases:
    - Files with very long names (>30 characters) - truncate with visual indicator
    - Empty directories (display only `.` and `..`)
    - Permission denied errors (pass through from `ls`)
    - Directories with 100+ files

### Build and Installation

14. A Makefile must be provided with the following targets:
    - `make`: Compile the program
    - `make install`: Install the program to `/usr/local/bin`
    - `make clean`: Remove compiled binaries
    - `make uninstall`: Remove the installed program

15. The program must compile without warnings using standard C compiler flags.

16. The installation process must work on standard Linux systems without additional dependencies beyond standard C libraries.

## 5. Non-Goals (Out of Scope)

1. **Recursive directory listing**: The tool will not traverse subdirectories recursively. Users should use `ls -R` or `tree` for that purpose.

2. **Filtering by file type or pattern**: The tool will not support glob patterns or filtering (e.g., `*.txt`). It displays all files returned by `ls --alsh`.

3. **Custom output formats**: The tool will not support user-configurable column ordering or custom format strings.

4. **Direct filesystem access**: The tool will not read directories directly; it must parse `ls` output.

5. **Cross-platform support**: Initial version targets Linux only. No Windows or macOS support required.

6. **Special handling of symbolic links**: Symlinks will be displayed as `ls` outputs them, without special parsing of link targets.

## 6. Design Considerations

### User Interface

- The output should resemble a clean table with clear column separation (at least 2 spaces between columns)
- When truncating filenames at 30 characters, append `…` or `...` to indicate truncation
- Color codes should use ANSI escape sequences for terminal compatibility
- The tool should feel like a natural extension of `ls` in terms of usage patterns

### Column Width Calculation

- Parse all entries first before displaying to calculate maximum widths
- Calculate column widths based on actual data to minimize wasted space
- Name column is fixed at maximum 30 characters

### Relative Time Display

- "just now" for files modified within the last minute
- "X minutes ago" for files modified within the last hour
- "X hours ago" for files modified within the last 24 hours
- "X days ago" for files modified within the last 30 days
- "X months ago" for files modified within the last year
- "X years ago" for older files

## 7. Technical Considerations

### Implementation Approach

1. **Process Execution**: Use `popen()` or `fork()`/`exec()` to run `ls --alsh` and capture output via pipe.

2. **Parsing Strategy**:
   - Parse `ls -alsh` output line by line
   - Extract fields: permissions, user, group, size, date/time, filename
   - Handle variations in `ls` output format (especially date/time formats)

3. **Data Structures**:
   - Create a struct to hold parsed file information
   - Use dynamic array or linked list to store all entries
   - Sort array before display using custom comparator functions

4. **Memory Management**:
   - Allocate memory dynamically for file entries
   - Free all allocated memory before program exit
   - Handle potential memory allocation failures gracefully

5. **Color Coding**:
   - Detect file type from permissions field (first character: `d` for directory, `l` for symlink)
   - Detect executables from permissions field (presence of `x` in user permissions)
   - Use ANSI escape codes for colors (e.g., `\033[34m` for blue)

6. **Relative Time Calculation**:
   - Get current time using `time()` or `gettimeofday()`
   - Parse date from `ls` output and convert to timestamp
   - Calculate difference and format as relative time string

### Build System

- Makefile should use standard variables: `CC`, `CFLAGS`, `PREFIX`
- Default `PREFIX` should be `/usr/local`
- Binary name: `lsa`
- Suggest CFLAGS: `-Wall -Wextra -O2`

### Dependencies

- Standard C library (libc)
- POSIX APIs for process execution and time handling
- No external libraries required

## 8. Success Metrics

1. **Functional Correctness**: The program correctly parses and displays `ls` output for directories containing:
   - 0-10 files (small directories)
   - 10-100 files (medium directories)
   - 100+ files (large directories)

2. **File Type Coverage**: The program correctly handles all standard file types:
   - Regular files
   - Directories
   - Symbolic links
   - Executable files
   - Hidden files (starting with `.`)

3. **Installation Success**: The program:
   - Compiles without warnings on standard Linux systems (Ubuntu, Debian, CentOS, Fedora)
   - Installs successfully to `/usr/local/bin` with `make install`
   - Runs without errors after installation

4. **Error Handling**: The program gracefully handles:
   - Non-existent directories
   - Permission denied errors
   - Invalid command-line arguments

5. **Performance**: The program processes and displays output in under 1 second for directories with up to 1000 files.

6. **Usability**: Developers find the output more readable than standard `ls` in informal testing.

## 9. Open Questions

1. **Truncation Indicator**: Should truncated filenames use `…` (single ellipsis character) or `...` (three periods)? Consider terminal compatibility.

2. **Sort Flag Conflicts**: If multiple sort flags are provided (e.g., `-s -d`), which should take precedence? Should the program use the last flag, first flag, or show an error?

3. **Color Customization**: Should the program respect `LS_COLORS` environment variable, or use hardcoded colors?

4. **Help Output**: Should the program support `--help` or `-h` flag to display usage information? If so, what should it display?

5. **Permissions Format**: Should the permissions column show the full `ls` format (e.g., `drwxr-xr-x`) or a simplified version?

6. **Size Format**: Should sizes be displayed as-is from `ls -h` (human-readable), or should the program do its own formatting?

7. **Testing**: Should a test suite be included? What format (bash scripts, C unit tests)?

8. **Version Flag**: Should the program support `--version` or `-v` to display version information?

---

**Document Version**: 1.0
**Created**: 2025-11-25
**Status**: Ready for Review
