# Product Requirements Document: lsa UI/UX Refactor

## Introduction/Overview

The `lsa` enhanced directory listing tool is currently functional but needs UI/UX improvements to enhance readability and provide better context to users. This refactor focuses on improving the visual presentation of the output without changing the core functionality or approach. The primary changes include reordering columns for better usability, adding a descriptive header, implementing zebra-striped rows for easier reading, and displaying a summary footer with total file sizes.

**Problem**: The current output format doesn't prioritize the most important information (filename first), lacks context (which directory is being listed), is difficult to read when scanning many entries, and doesn't provide summary information about the total size of files.

**Goal**: Improve the user experience by making the output more readable, informative, and easier to scan at a glance.

## Goals

1. Reorder table columns to prioritize filename as the first column
2. Add a descriptive header showing the current working directory and file count
3. Implement zebra-striped rows (alternating black/dark-grey backgrounds) for improved readability
4. Add a footer with a horizontal rule and total file size summary
5. Maintain all existing functionality (sorting, colors, filtering, CLI interface)
6. Ensure the refactored version passes all existing tests

## User Stories

1. **As a user**, I want to see the filename first in each row so that I can quickly identify files without scanning across multiple columns.

2. **As a user**, I want to see which directory I'm listing and how many files were found so that I have context for the output, especially when running multiple lsa commands in sequence.

3. **As a user**, I want alternating row backgrounds so that I can easily track across columns when reading long file listings.

4. **As a user**, I want to see the total size of all files in the directory so that I can quickly understand the disk space usage without manually summing sizes.

5. **As a user**, I want all my existing sort options and color coding to continue working so that I don't lose familiar functionality.

## Functional Requirements

### Column Reordering
1. The output table must display columns in this order: **Filename, DateTime, Size, User, Permissions**
2. All existing column formatting rules (truncation, padding, alignment) must continue to work with the new column order
3. Color coding for filenames (blue for directories, green for executables, cyan for symlinks) must remain functional

### Header Section
4. The program must print a header section before the file listing table
5. The header must display the current working directory being listed on the left side
6. The header must display the number of files found, right-aligned on the same line
7. After the header information, a horizontal line separator must be printed before the table entries begin
8. The horizontal line should span the full width of the table

### Zebra Striping
9. The program must alternate row background colors between black and dark-grey
10. The first data row (after any header) should use the default/black background
11. The second row should use dark-grey background (ANSI code: `\033[48;5;236m` or similar)
12. This pattern must continue alternating for all rows
13. Background colors must be reset at the end of each line to avoid terminal display issues
14. The zebra striping must not interfere with existing foreground color codes for file types

### Footer Section
15. After all file entries are printed, a horizontal rule line must be displayed
16. Below the horizontal rule the total sum of all file sizes must be printed
17. The total size must be aligned under the Size column
18. The total size should be formatted consistently with individual file sizes (e.g., "4.2M", "128K", "1.5G")
19. The horizontal rule should span the full width of the table

### Preserved Functionality
20. All existing command-line flags must continue to work: `--sort-name/-n`, `--sort-size/-s`, `--sort-date/-d`, `--sort-permissions/-p`, `--help/-h`, `--version`
21. All existing sorting behavior (by category first, then by the selected attribute) must remain unchanged
22. The relative time formatting ("X minutes ago", "X days ago", etc.) must continue to work
23. The user:group formatting rules must remain unchanged
24. All error handling (permission denied, non-existent directories, etc.) must continue to work

## Non-Goals (Out of Scope)

1. Changing the core parsing approach (will continue to use `popen()` with `ls`)
2. Adding new sorting options or filtering capabilities
3. Supporting configuration files or user preferences
4. Adding new command-line flags (beyond what's already implemented)
5. Modifying the sorting algorithm or category prioritization
6. Adding pagination or scrolling for large directory listings
7. Supporting multiple directory listings in a single invocation
8. Creating a GUI or interactive mode

## Design Considerations

### Column Order Rationale
The new column order (Filename, DateTime, Size, User, Permissions) prioritizes information by typical user importance:
- **Filename** is the primary identifier users look for
- **DateTime** helps users understand recency and chronological context
- **Size** is often the next most important piece of information
- **User** and **Permissions** are typically needed less frequently and can be scanned at the end

### Color Scheme
- **Zebra striping**: Use ANSI escape code `\033[48;5;236m` for dark-grey background (256-color mode)
- **Reset code**: Use `\033[0m` to reset all formatting at line end, then reapply foreground colors as needed
- Ensure zebra striping works in common terminals (xterm, gnome-terminal, iTerm2, etc.)

### Header Format Example
```
/home/user/projects                                                    42 files
────────────────────────────────────────────────────────────────────────────────
```

### Footer Format Example
```
────────────────────────────────────────────────────────────────────────────────
                                          Total: 15.3M
```

## Technical Considerations

1. **ANSI Escape Codes**: The zebra striping will require careful management of ANSI codes to avoid conflicts with existing color codes for file types
2. **String Width Calculation**: The header and footer horizontal rules must account for the total table width including column spacing
3. **Terminal Compatibility**: Test with common terminal emulators to ensure ANSI codes render correctly
4. **Size Summation**: Need to parse the size strings (which may have suffixes like K, M, G) and sum them correctly
5. **Memory Management**: No new dynamic allocations should be needed; existing entry structures can be reused
6. **Build System**: No changes to the Makefile should be necessary

## Success Metrics

1. **Functional Correctness**: All existing tests pass without modification (except tests that verify exact output format)
2. **Visual Verification**: Manual QA testing confirms:
   - Columns appear in the correct order
   - Header shows correct directory and file count
   - Rows alternate between black and dark-grey backgrounds
   - Footer displays correct total file size
   - All colors and formatting render correctly in common terminals
3. **No Regressions**: All existing features (sorting, filtering, error handling) continue to work as before
4. **Performance**: No significant performance degradation (output generation should remain fast even for directories with 100+ files)

## Open Questions

1. Should the horizontal rules use ASCII characters (e.g., "─" or "-") or Unicode box-drawing characters?
2. Should the total size line include a label like "Total:" or just show the size aligned under the column?
3. Should the file count in the header include hidden files in the count, or only visible files?
4. Should directories be included in the total size calculation, or only regular files?
5. Should we add a configuration option to disable zebra striping for users who prefer plain output?
6. What should happen with the zebra striping when viewing directories with only 1-2 entries?

## Answers to open questions

1. Use Unicode box-drawing, and make the color light-grey
2. Just show the total, there is no need for a label.
3. Yes, include hidden files. 
4. No, as we don't do recursion, and directories are always a fake size anyway.
5. No, we don't want to go down the rabbit-hole of "customizability".
6. Just apply a rule, first entry black, second dark-grey in a cycle. If it is just one entry, then that's fine, it will be black. If it's two, it will be black then grey. Simplicity is probably better here.

## Implementation Notes

This refactor should be implemented by modifying the existing `src/lsa.c` file:
- The `print_table()` function will need the most significant changes to handle zebra striping and the new column order
- A new helper function to calculate total sizes may be needed
- The header and footer printing logic can be added before and after the existing table printing loop
- No changes to the Makefile or build system should be required
