# Task List: lsa - Enhanced Directory Listing Tool

## Relevant Files

- `src/lsa.c` - Main source file containing all program logic (complete with data structures, parsing, sorting, formatting, CLI, error handling, and main function)
- `Makefile` - Build system with compile, install, clean, and uninstall targets (completed)
- `README.md` - Basic usage documentation (optional, not yet created)
- `test_lsa.sh` - Bash script for testing various scenarios (optional, not yet created)

### Notes

- This is a C project, so tests may be implemented as bash scripts or C unit tests
- The program should be kept simple - a single C file is likely sufficient given the scope
- Use standard C libraries only (libc, POSIX APIs)
- Compile with: `gcc -Wall -Wextra -O2 lsa.c -o lsa`
- Install to: `/usr/local/bin/lsa`

## Tasks

- [x] 1.0 Project Setup and Build System
  - [x] 1.1 Create project directory structure and initialize lsa.c with basic includes (stdio.h, stdlib.h, string.h, time.h, unistd.h)
  - [x] 1.2 Write Makefile with `make` target to compile with flags: -Wall -Wextra -O2
  - [x] 1.3 Add `make install` target to copy binary to /usr/local/bin (PREFIX=/usr/local)
  - [x] 1.4 Add `make clean` target to remove compiled binaries
  - [x] 1.5 Add `make uninstall` target to remove installed binary from /usr/local/bin
  - [x] 1.6 Test that compilation works without warnings

- [x] 2.0 Core Parsing and Data Structures
  - [x] 2.1 Define `struct FileEntry` to hold: name (char*), permissions (char*), size (char*), timestamp (time_t), user (char*), group (char*), is_directory (int), is_executable (int), is_symlink (int)
  - [x] 2.2 Define dynamic array structure to hold array of FileEntry pointers with capacity and count fields
  - [x] 2.3 Implement `execute_ls()` function using popen() to run "ls --alsh [directory]" and return FILE pointer
  - [x] 2.4 Implement `parse_ls_line()` function to extract fields from a single ls output line using sscanf or string parsing
  - [x] 2.5 Implement `parse_ls_output()` function to read all lines from ls, parse each line, and populate dynamic array of FileEntry structs
  - [x] 2.6 Implement `free_entries()` function to properly deallocate all FileEntry structs and their string fields
  - [x] 2.7 Handle ls date/time parsing - convert "Jan 15 14:30" or "2024-01-15 14:30" format to time_t for timestamp comparison

- [x] 3.0 Sorting Implementation
  - [x] 3.1 Implement `get_entry_category()` helper function that returns sort priority: 0 for ".", 1 for "..", 2 for directories, 3 for hidden files (starting with .), 4 for regular files
  - [x] 3.2 Implement `compare_by_name()` comparator function that sorts by category first, then alphabetically by name
  - [x] 3.3 Implement `compare_by_size()` comparator that sorts by category first, then by file size (parse size string to numeric value)
  - [x] 3.4 Implement `compare_by_date()` comparator that sorts by category first, then by modification timestamp
  - [x] 3.5 Implement `compare_by_permissions()` comparator that sorts by category first, then by permission string
  - [x] 3.6 Implement `sort_entries()` function that uses qsort() with the appropriate comparator based on command-line flag

- [x] 4.0 Table Formatting and Display
  - [x] 4.1 Implement `calculate_column_widths()` function to iterate through all entries and determine max width for each column (permissions, size, date, user:group)
  - [x] 4.2 Implement `format_relative_time()` function to convert timestamp to relative time string: "just now", "X minutes ago", "X hours ago", "X days ago", "X months ago", "X years ago"
  - [x] 4.3 Implement `truncate_name()` function to truncate filenames longer than 30 characters and append "..." or "…" indicator
  - [x] 4.4 Implement `format_user_group()` function to display as "user:" when user and group are identical, otherwise "user:group"
  - [x] 4.5 Implement `get_color_code()` function that returns ANSI color code based on file type: blue (\033[34m) for directories, green (\033[32m) for executables, cyan (\033[36m) for symlinks, reset (\033[0m) for others
  - [x] 4.6 Implement `print_table()` function that iterates through sorted entries and prints each row with proper padding, alignment (left-aligned), and color codes
  - [x] 4.7 Ensure at least 2 spaces between columns for visual separation

- [x] 5.0 Command-Line Interface and Error Handling
  - [x] 5.1 Implement `parse_arguments()` function to process command-line flags: --sort-name/-n, --sort-size/-s, --sort-date/-d, --sort-permissions/-p, and optional [directory] argument
  - [x] 5.2 Set default sort mode to name sorting if no flag provided
  - [x] 5.3 Handle multiple sort flags by using the last flag provided (resolve open question #2)
  - [x] 5.4 Implement --help/-h flag to display usage information (resolve open question #4)
  - [x] 5.5 Implement --version flag to display version information (resolve open question #8)
  - [x] 5.6 Check if ls command fails (popen returns NULL or pclose returns error code) and print error to stderr, exit with same error code
  - [x] 5.7 Test edge cases: empty directories (only . and ..), permission denied, non-existent directories, filenames >30 chars, directories with 100+ files
  - [x] 5.8 Test all sorting modes with various directory contents
  - [x] 5.9 Verify memory cleanup with valgrind or similar tool (no memory leaks)
