# Task List: lsa UI/UX Refactor

## Relevant Files

- `lsa/src/lsa.c` - Main source file containing all lsa implementation including table printing logic
- `lsa/Makefile` - Build configuration (should not require changes per PRD)

### Notes

- This refactor focuses on UI/UX improvements without changing core functionality
- All changes will be in `lsa/src/lsa.c`, primarily in the `print_table()` function
- Use `make` to build and `./lsa` to test
- Manual testing required since no automated test suite exists yet

## Tasks

- [ ] 1.0 Reorder table columns to new format (Filename, DateTime, Size, User, Permissions)
  - [ ] 1.1 Read and understand current column order in `print_table()` function
  - [ ] 1.2 Identify where each column (filename, datetime, size, user, permissions) is printed
  - [ ] 1.3 Modify print statements to output columns in new order: Filename, DateTime, Size, User, Permissions
  - [ ] 1.4 Ensure column spacing and padding still aligns properly with new order
  - [ ] 1.5 Verify color coding for filenames (blue for directories, green for executables, cyan for symlinks) still works
  - [ ] 1.6 Test with various directory listings to confirm column alignment

- [ ] 2.0 Implement header section displaying directory path and file count
  - [ ] 2.1 Add code to get current working directory path (using `getcwd()` or equivalent)
  - [ ] 2.2 Add counter to track total number of files being displayed
  - [ ] 2.3 Calculate total table width to determine horizontal rule length
  - [ ] 2.4 Print header line with directory path (left-aligned) and file count right-aligned (format: "X files")
  - [ ] 2.5 Print horizontal rule separator using Unicode box-drawing character (─) in light-grey color
  - [ ] 2.6 Ensure header prints before the first file entry

- [ ] 3.0 Implement zebra-striped rows with alternating black/dark-grey backgrounds
  - [ ] 3.1 Add row counter variable to track current row index
  - [ ] 3.2 Add ANSI escape code constant for dark-grey background (`\033[48;5;236m`)
  - [ ] 3.3 Add logic to determine if current row should have dark-grey or black background (odd/even check)
  - [ ] 3.4 Apply appropriate background color ANSI code at the start of each row
  - [ ] 3.5 Ensure background color is reset at the end of each row using `\033[0m`
  - [ ] 3.6 Test that foreground colors for file types are not affected by background colors
  - [ ] 3.7 Test zebra striping with directories containing 1, 2, and many files

- [ ] 4.0 Implement footer section with horizontal rule and total file size
  - [ ] 4.1 Create helper function to parse size strings (handling K, M, G suffixes)
  - [ ] 4.2 Create function to sum all file sizes, converting to bytes first
  - [ ] 4.3 Create function to format total bytes back to human-readable format (K, M, G)
  - [ ] 4.4 Track cumulative size while printing entries (or iterate through entries at end)
  - [ ] 4.5 Print horizontal rule after all file entries (same format as header rule)
  - [ ] 4.6 Print total size aligned under the Size column
  - [ ] 4.7 Ensure directories are excluded from total size calculation (only count regular files)

- [ ] 5.0 Verify all existing functionality (sorting, colors, error handling) works correctly
  - [ ] 5.1 Test default listing (no flags) shows files correctly with all new UI features
  - [ ] 5.2 Test `--sort-name` / `-n` flag works and maintains new column order
  - [ ] 5.3 Test `--sort-size` / `-s` flag works correctly
  - [ ] 5.4 Test `--sort-date` / `-d` flag works correctly
  - [ ] 5.5 Test `--sort-permissions` / `-p` flag works correctly
  - [ ] 5.6 Test `--help` / `-h` flag displays help message
  - [ ] 5.7 Test `--version` flag displays version information
  - [ ] 5.8 Test with directory containing only files, only subdirectories, and mixed content
  - [ ] 5.9 Test with directory containing hidden files (verify they're counted in header)
  - [ ] 5.10 Test error handling for non-existent directories
  - [ ] 5.11 Test error handling for directories without read permissions
  - [ ] 5.12 Verify color coding: blue for directories, green for executables, cyan for symlinks
  - [ ] 5.13 Test with directories containing 100+ files to ensure no performance degradation
