# Documentation Generation Rules

## Purpose
Generate clear, practical documentation for code files or directories. The output is a markdown file that helps developers quickly understand how the code works through execution graphs and real-world examples.

## Initial Steps

1. **Ask the user**: "What file or directory should I document?"
2. **Determine the primary execution path**: Identify entry points, main classes, and key methods
3. **Filter**: Skip trivial helpers, small utility functions, and simple data classes/structs

## Documentation Structure

### 1. File Header
```markdown
# [Library/Module Name] Documentation

## Dependencies
- import statement 1
- import statement 2
- ...
```

### 2. Table of Contents
Create a clickable table of contents linking to each documented class and method:
```markdown
## Table of Contents
- [ClassName](#classname)
  - [method_name()](#classname-method_name)
  - [another_method()](#classname-another_method)
- [AnotherClass](#anotherclass)
  ...
```

### 3. Class and Method Documentation

For each class and important method, create an entry with:

#### A. Function Signature
Show the function/method with its body replaced by `...`:
```markdown
### ClassName.method_name

\`\`\`python
def method_name(self, param1: str, param2: int) -> bool:
    ...
\`\`\`
```

#### B. ASCII Execution Graph (Tree Style)
Create a tree-style diagram showing major logic branches:
```
Start
├─ Check authentication
│  ├─ [authenticated] → Load user data
│  │  ├─ [data exists] → Process request
│  │  │  └─ Return success
│  │  └─ [data missing] → Return error
│  └─ [not authenticated] → Redirect to login
└─ End
```

**Rules for execution graphs:**
- Use tree-style with indentation and branch characters (├─ └─ │)
- Show only major logic branches (not every if/else)
- Highlight different operation modes, error paths, and key decisions
- Keep it readable - focus on the big picture

#### C. Functions Called
List all functions called by this method:
```markdown
**Functions called:**
- `function_name()` - [link to section](#classname-function_name) *(if documented in this file)*
- `external_function()` - external call
- `another_method()` - [link to section](#classname-another_method)
```

**Rules for function list:**
- Include all function calls except trivial built-ins (like `len()`, `str()`, `int()`)
- Filter out obvious standard library calls (like `print()`, `range()`)
- Include meaningful stdlib calls (like `json.loads()`, `datetime.now()`)
- Cross-link to other documented items in the same markdown file
- Include method calls on objects (like `obj.save()`, `db.query()`)

#### D. Real-World Examples
Find and show 1-3 real-world usage examples from the codebase:
```markdown
**Examples:**

1. **Simple usage** (`path/to/file.py:45-52`)
\`\`\`python
user = User()
user.set_name("Alice")
result = user.save()
\`\`\`

2. **Complex usage** (`path/to/other_file.py:123-135`)
\`\`\`python
user = User()
user.set_name("Bob")
user.set_email("bob@example.com")
if user.validate():
    user.save()
\`\`\`
```

**Rules for examples:**
- Search 1-2 directories up from the documented file for examples
- Select best 1-3 examples showing a mix of:
  - Simple/clear usage
  - Comprehensive usage with multiple features
  - Different use cases
- Show focused snippets (just the relevant code, not entire functions)
- Always include file path and line range: `(path/to/file.py:start-end)`
- If no examples found, write "No examples found in codebase"

## Important Guidelines

1. **Be succinct**: No lengthy explanations. Let the code and graphs speak.
2. **No overview sections**: Jump straight into documentation.
3. **No jargon**: Write for junior developers.
4. **One file**: If documenting a directory, create one large markdown file.
5. **Consistent naming**: Name the output file after the library/module (e.g., `generate_models_documentation.md`).

## What to Skip

- Trivial helper functions (1-3 lines, obvious purpose)
- Simple getters/setters with no logic
- Data classes/structs with no methods
- Private methods unless they contain important algorithms or are called from multiple places

## Final Output

A markdown file with:
1. Header with dependencies list
2. Table of contents
3. Documentation for each class
4. Documentation for each important method
5. All cross-links working
6. Examples with file paths and line ranges

The documentation should give a developer a quick tour and practical understanding of how to use the code.
