#define _XOPEN_SOURCE
#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

enum SortMode {
    SORT_BY_NAME,
    SORT_BY_SIZE,
    SORT_BY_DATE,
    SORT_BY_PERMISSIONS
};

struct ProgramConfig {
    enum SortMode sort_mode;
    char *directory;
};

struct FileEntry {
    char *name;
    char *permissions;
    char *size;
    time_t timestamp;
    char *user;
    char *group;
    int is_directory;
    int is_executable;
    int is_symlink;
};

struct FileEntryArray {
    struct FileEntry **entries;
    int count;
    int capacity;
};

struct ColumnWidths {
    int permissions;
    int size;
    int date;
    int user_group;
};

time_t parse_ls_datetime(const char *month, int day, const char *time_str) {
    struct tm tm_info = {0};
    time_t now = time(NULL);
    struct tm *now_tm = localtime(&now);

    const char *months[] = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    };

    int month_num = 0;
    for (int i = 0; i < 12; i++) {
        if (strcmp(month, months[i]) == 0) {
            month_num = i;
            break;
        }
    }

    tm_info.tm_mon = month_num;
    tm_info.tm_mday = day;

    if (strchr(time_str, ':') != NULL) {
        int hour, minute;
        sscanf(time_str, "%d:%d", &hour, &minute);
        tm_info.tm_hour = hour;
        tm_info.tm_min = minute;
        tm_info.tm_sec = 0;
        tm_info.tm_year = now_tm->tm_year;
    } else {
        int year;
        sscanf(time_str, "%d", &year);
        tm_info.tm_year = year - 1900;
        tm_info.tm_hour = 0;
        tm_info.tm_min = 0;
        tm_info.tm_sec = 0;
    }

    tm_info.tm_isdst = -1;

    return mktime(&tm_info);
}

FILE *execute_ls(const char *directory) {
    char command[1024];

    if (directory == NULL || strlen(directory) == 0) {
        snprintf(command, sizeof(command), "ls -alsh");
    } else {
        snprintf(command, sizeof(command), "ls -alsh %s", directory);
    }

    return popen(command, "r");
}

struct FileEntry *parse_ls_line(const char *line) {
    char size_blocks[32];
    char permissions[32];
    int link_count;
    char user[64];
    char group[64];
    char size[32];
    char month[16];
    int day;
    char time_str[32];
    int pos = 0;

    if (strncmp(line, "total", 5) == 0) {
        return NULL;
    }

    int parsed = sscanf(
        line,
        "%s %s %d %s %s %s %s %d %s%n",
        size_blocks,
        permissions,
        &link_count,
        user,
        group,
        size,
        month,
        &day,
        time_str,
        &pos
    );

    if (parsed < 9) {
        return NULL;
    }

    while (line[pos] == ' ' || line[pos] == '\t') {
        pos++;
    }

    const char *filename = &line[pos];

    struct FileEntry *entry = malloc(sizeof(struct FileEntry));
    if (!entry) {
        return NULL;
    }

    entry->name = strdup(filename);
    entry->permissions = strdup(permissions);
    entry->size = strdup(size);
    entry->user = strdup(user);
    entry->group = strdup(group);

    size_t len = strlen(entry->name);
    if (len > 0 && entry->name[len - 1] == '\n') {
        entry->name[len - 1] = '\0';
    }

    entry->is_directory = (permissions[0] == 'd');
    entry->is_symlink = (permissions[0] == 'l');
    entry->is_executable = (permissions[3] == 'x' || permissions[6] == 'x' || permissions[9] == 'x');

    entry->timestamp = parse_ls_datetime(month, day, time_str);

    return entry;
}

struct FileEntryArray *parse_ls_output(FILE *fp) {
    struct FileEntryArray *array = malloc(sizeof(struct FileEntryArray));
    if (!array) {
        return NULL;
    }

    array->capacity = 16;
    array->count = 0;
    array->entries = malloc(sizeof(struct FileEntry *) * array->capacity);
    if (!array->entries) {
        free(array);
        return NULL;
    }

    char line[4096];
    while (fgets(line, sizeof(line), fp) != NULL) {
        struct FileEntry *entry = parse_ls_line(line);
        if (entry == NULL) {
            continue;
        }

        if (array->count >= array->capacity) {
            int new_capacity = array->capacity * 2;
            struct FileEntry **new_entries = realloc(
                array->entries,
                sizeof(struct FileEntry *) * new_capacity
            );
            if (!new_entries) {
                free(entry->name);
                free(entry->permissions);
                free(entry->size);
                free(entry->user);
                free(entry->group);
                free(entry);
                continue;
            }
            array->entries = new_entries;
            array->capacity = new_capacity;
        }

        array->entries[array->count] = entry;
        array->count++;
    }

    return array;
}

int get_entry_category(struct FileEntry *entry) {
    if (strcmp(entry->name, ".") == 0) {
        return 0;
    }
    if (strcmp(entry->name, "..") == 0) {
        return 1;
    }
    if (entry->is_directory) {
        return 2;
    }
    if (entry->name[0] == '.') {
        return 3;
    }
    return 4;
}

int compare_by_name(const void *a, const void *b) {
    struct FileEntry *entry_a = *(struct FileEntry **)a;
    struct FileEntry *entry_b = *(struct FileEntry **)b;

    int cat_a = get_entry_category(entry_a);
    int cat_b = get_entry_category(entry_b);

    if (cat_a != cat_b) {
        return cat_a - cat_b;
    }

    return strcmp(entry_a->name, entry_b->name);
}

long long parse_size_to_bytes(const char *size_str) {
    double value;
    char unit[8] = {0};

    sscanf(size_str, "%lf%s", &value, unit);

    long long multiplier = 1;
    if (strlen(unit) > 0) {
        switch (unit[0]) {
            case 'K':
            case 'k':
                multiplier = 1024;
                break;
            case 'M':
            case 'm':
                multiplier = 1024 * 1024;
                break;
            case 'G':
            case 'g':
                multiplier = 1024 * 1024 * 1024;
                break;
            case 'T':
            case 't':
                multiplier = 1024LL * 1024 * 1024 * 1024;
                break;
        }
    }

    return (long long)(value * multiplier);
}

int compare_by_size(const void *a, const void *b) {
    struct FileEntry *entry_a = *(struct FileEntry **)a;
    struct FileEntry *entry_b = *(struct FileEntry **)b;

    int cat_a = get_entry_category(entry_a);
    int cat_b = get_entry_category(entry_b);

    if (cat_a != cat_b) {
        return cat_a - cat_b;
    }

    long long size_a = parse_size_to_bytes(entry_a->size);
    long long size_b = parse_size_to_bytes(entry_b->size);

    if (size_a < size_b) {
        return -1;
    }
    if (size_a > size_b) {
        return 1;
    }
    return 0;
}

int compare_by_date(const void *a, const void *b) {
    struct FileEntry *entry_a = *(struct FileEntry **)a;
    struct FileEntry *entry_b = *(struct FileEntry **)b;

    int cat_a = get_entry_category(entry_a);
    int cat_b = get_entry_category(entry_b);

    if (cat_a != cat_b) {
        return cat_a - cat_b;
    }

    if (entry_a->timestamp < entry_b->timestamp) {
        return -1;
    }
    if (entry_a->timestamp > entry_b->timestamp) {
        return 1;
    }
    return 0;
}

int compare_by_permissions(const void *a, const void *b) {
    struct FileEntry *entry_a = *(struct FileEntry **)a;
    struct FileEntry *entry_b = *(struct FileEntry **)b;

    int cat_a = get_entry_category(entry_a);
    int cat_b = get_entry_category(entry_b);

    if (cat_a != cat_b) {
        return cat_a - cat_b;
    }

    return strcmp(entry_a->permissions, entry_b->permissions);
}

void truncate_name(const char *name, char *buffer, size_t buffer_size) {
    size_t name_len = strlen(name);

    if (name_len <= 60) {
        snprintf(buffer, buffer_size, "%s", name);
    } else {
        snprintf(buffer, buffer_size, "%.57s...", name);
    }
}

void format_user_group(const char *user, const char *group, char *buffer, size_t buffer_size) {
    if (strcmp(user, group) == 0) {
        snprintf(buffer, buffer_size, "%s:", user);
    } else {
        snprintf(buffer, buffer_size, "%s:%s", user, group);
    }
}

const char *get_color_code(struct FileEntry *entry) {
    if (entry->is_symlink) {
        return "\033[36m";
    }
    if (entry->is_directory) {
        return "\033[34m";
    }
    if (entry->is_executable) {
        return "\033[32m";
    }
    return "\033[0m";
}

void format_relative_time(time_t timestamp, char *buffer, size_t buffer_size) {
    time_t now = time(NULL);
    double diff = difftime(now, timestamp);

    if (diff < 0) {
        diff = 0;
    }

    if (diff < 60) {
        snprintf(buffer, buffer_size, "just now");
    } else if (diff < 3600) {
        int minutes = (int)(diff / 60);
        if (minutes == 1) {
            snprintf(buffer, buffer_size, "1 minute ago");
        } else {
            snprintf(buffer, buffer_size, "%d minutes ago", minutes);
        }
    } else if (diff < 86400) {
        int hours = (int)(diff / 3600);
        if (hours == 1) {
            snprintf(buffer, buffer_size, "1 hour ago");
        } else {
            snprintf(buffer, buffer_size, "%d hours ago", hours);
        }
    } else if (diff < 2592000) {
        int days = (int)(diff / 86400);
        if (days == 1) {
            snprintf(buffer, buffer_size, "1 day ago");
        } else {
            snprintf(buffer, buffer_size, "%d days ago", days);
        }
    } else if (diff < 31536000) {
        int months = (int)(diff / 2592000);
        if (months == 1) {
            snprintf(buffer, buffer_size, "1 month ago");
        } else {
            snprintf(buffer, buffer_size, "%d months ago", months);
        }
    } else {
        int years = (int)(diff / 31536000);
        if (years == 1) {
            snprintf(buffer, buffer_size, "1 year ago");
        } else {
            snprintf(buffer, buffer_size, "%d years ago", years);
        }
    }
}

struct ColumnWidths calculate_column_widths(struct FileEntryArray *array) {
    struct ColumnWidths widths = {0, 0, 0, 0};

    if (!array || array->count == 0) {
        return widths;
    }

    for (int i = 0; i < array->count; i++) {
        struct FileEntry *entry = array->entries[i];

        int perm_len = strlen(entry->permissions);
        if (perm_len > widths.permissions) {
            widths.permissions = perm_len;
        }

        int size_len = strlen(entry->size);
        if (size_len > widths.size) {
            widths.size = size_len;
        }

        int user_group_len;
        if (strcmp(entry->user, entry->group) == 0) {
            user_group_len = strlen(entry->user) + 1;
        } else {
            user_group_len = strlen(entry->user) + strlen(entry->group) + 1;
        }
        if (user_group_len > widths.user_group) {
            widths.user_group = user_group_len;
        }

        int date_len = 20;
        if (date_len > widths.date) {
            widths.date = date_len;
        }
    }

    return widths;
}

char *format_bytes_to_human(long long bytes) {
    static char buffer[32];

    if (bytes < 1024) {
        snprintf(buffer, sizeof(buffer), "%lldB", bytes);
    } else if (bytes < 1024 * 1024) {
        double kb = bytes / 1024.0;
        snprintf(buffer, sizeof(buffer), "%.1fK", kb);
    } else if (bytes < 1024LL * 1024 * 1024) {
        double mb = bytes / (1024.0 * 1024.0);
        snprintf(buffer, sizeof(buffer), "%.1fM", mb);
    } else if (bytes < 1024LL * 1024 * 1024 * 1024) {
        double gb = bytes / (1024.0 * 1024.0 * 1024.0);
        snprintf(buffer, sizeof(buffer), "%.1fG", gb);
    } else {
        double tb = bytes / (1024.0 * 1024.0 * 1024.0 * 1024.0);
        snprintf(buffer, sizeof(buffer), "%.1fT", tb);
    }

    return buffer;
}

void print_table(struct FileEntryArray *array, const char *directory) {
    if (!array || array->count == 0) {
        return;
    }

    struct ColumnWidths widths = calculate_column_widths(array);

    char cwd[1024];
    const char *display_dir;

    if (directory == NULL || strlen(directory) == 0) {
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            display_dir = cwd;
        } else {
            display_dir = ".";
        }
    } else {
        display_dir = directory;
    }

    int filename_width = 60;
    int total_width = filename_width + 2 + widths.date + 2 + widths.size + 2 + widths.user_group + 2 + widths.permissions;

    int file_count = array->count;
    char file_count_str[32];
    snprintf(file_count_str, sizeof(file_count_str), "%d files", file_count);
    int file_count_len = strlen(file_count_str);

    int dir_len = strlen(display_dir);
    int padding = total_width - dir_len - file_count_len;
    if (padding < 1) {
        padding = 1;
    }

    printf("%s%*s%s\n", display_dir, padding, "", file_count_str);

    printf("\033[38;5;240m");
    for (int i = 0; i < total_width; i++) {
        printf("─");
    }
    printf("\033[0m\n");

    long long total_size = 0;

    for (int i = 0; i < array->count; i++) {
        struct FileEntry *entry = array->entries[i];

        char user_group[128];
        format_user_group(entry->user, entry->group, user_group, sizeof(user_group));

        char relative_time[64];
        format_relative_time(entry->timestamp, relative_time, sizeof(relative_time));

        char truncated_name[64];
        truncate_name(entry->name, truncated_name, sizeof(truncated_name));

        const char *color = get_color_code(entry);
        const char *reset = "\033[0m";
        const char *bg_color = (i % 2 == 0) ? "" : "\033[48;5;234m";

        if (!entry->is_directory) {
            total_size += parse_size_to_bytes(entry->size);
        }

        printf("%s%s%-*s%s%s  %s%-*s  %-*s  %-*s  %-*s%s\n",
            bg_color,
            color, filename_width, truncated_name, reset,
            bg_color,
            bg_color, widths.date, relative_time,
            widths.size, entry->size,
            widths.user_group, user_group,
            widths.permissions, entry->permissions,
            reset
        );
    }

    printf("\033[38;5;240m");
    for (int i = 0; i < total_width; i++) {
        printf("─");
    }
    printf("\033[0m\n");

    int prefix_width = filename_width + 2 + widths.date + 2;
    char *total_str = format_bytes_to_human(total_size);
    printf("%*s%s\n", prefix_width + (int)strlen(total_str), total_str, "");
}

void sort_entries(struct FileEntryArray *array, enum SortMode mode) {
    if (!array || array->count == 0) {
        return;
    }

    int (*comparator)(const void *, const void *);

    switch (mode) {
        case SORT_BY_SIZE:
            comparator = compare_by_size;
            break;
        case SORT_BY_DATE:
            comparator = compare_by_date;
            break;
        case SORT_BY_PERMISSIONS:
            comparator = compare_by_permissions;
            break;
        case SORT_BY_NAME:
        default:
            comparator = compare_by_name;
            break;
    }

    qsort(array->entries, array->count, sizeof(struct FileEntry *), comparator);
}

void print_version(void) {
    printf("lsa version 1.0.0\n");
    printf("Enhanced Directory Listing Tool\n");
}

void print_help(void) {
    printf("lsa - Enhanced Directory Listing Tool\n\n");
    printf("Usage: lsa [OPTIONS] [DIRECTORY]\n\n");
    printf("Options:\n");
    printf("  -n, --sort-name         Sort by name (default)\n");
    printf("  -s, --sort-size         Sort by file size\n");
    printf("  -d, --sort-date         Sort by modification date\n");
    printf("  -p, --sort-permissions  Sort by permissions\n");
    printf("  -h, --help              Display this help message\n");
    printf("  --version               Display version information\n\n");
    printf("If no directory is specified, the current directory is used.\n");
}

struct ProgramConfig parse_arguments(int argc, char *argv[]) {
    struct ProgramConfig config;
    config.sort_mode = SORT_BY_NAME;
    config.directory = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_help();
            exit(0);
        } else if (strcmp(argv[i], "--version") == 0) {
            print_version();
            exit(0);
        } else if (strcmp(argv[i], "--sort-name") == 0 || strcmp(argv[i], "-n") == 0) {
            config.sort_mode = SORT_BY_NAME;
        } else if (strcmp(argv[i], "--sort-size") == 0 || strcmp(argv[i], "-s") == 0) {
            config.sort_mode = SORT_BY_SIZE;
        } else if (strcmp(argv[i], "--sort-date") == 0 || strcmp(argv[i], "-d") == 0) {
            config.sort_mode = SORT_BY_DATE;
        } else if (strcmp(argv[i], "--sort-permissions") == 0 || strcmp(argv[i], "-p") == 0) {
            config.sort_mode = SORT_BY_PERMISSIONS;
        } else if (argv[i][0] != '-') {
            config.directory = argv[i];
        }
    }

    return config;
}

void free_entries(struct FileEntryArray *array) {
    if (!array) {
        return;
    }

    for (int i = 0; i < array->count; i++) {
        struct FileEntry *entry = array->entries[i];
        if (entry) {
            free(entry->name);
            free(entry->permissions);
            free(entry->size);
            free(entry->user);
            free(entry->group);
            free(entry);
        }
    }

    free(array->entries);
    free(array);
}

int main(int argc, char *argv[]) {
    struct ProgramConfig config = parse_arguments(argc, argv);

    FILE *fp = execute_ls(config.directory);
    if (fp == NULL) {
        fprintf(stderr, "Error: Failed to execute ls command\n");
        return 1;
    }

    struct FileEntryArray *array = parse_ls_output(fp);

    int pclose_status = pclose(fp);
    if (pclose_status != 0) {
        int exit_code = WEXITSTATUS(pclose_status);
        if (exit_code != 0) {
            fprintf(stderr, "Error: ls command failed with exit code %d\n", exit_code);
            free_entries(array);
            return exit_code;
        }
    }

    if (array == NULL || array->count == 0) {
        free_entries(array);
        return 0;
    }

    sort_entries(array, config.sort_mode);
    print_table(array, config.directory);
    free_entries(array);

    return 0;
}
