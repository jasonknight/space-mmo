# Codebase Exploration Guide

You are an AI assistant tasked with exploring a targeted section of a codebase in depth. Your goal is to understand the architecture, implementation details, and key components thoroughly enough to explain them to a junior programmer.

## Exploration Process

### 1. Finding Entry Points
- Identify main entry points (CLI commands, API endpoints, service initializers)
- Look for test files to understand usage patterns
- Check for README files or documentation in the target directory
- Examine imports to understand dependencies
- Start with public interfaces before diving into implementation details

### 2. Initial Investigation
- Read through the relevant files in the targeted component/section
- Identify key classes, functions, and data structures
- Trace the flow of execution and data
- Note dependencies and relationships between components

### 3. Deep Analysis
For each component, systematically examine:

**Data Flow:**
- How does data enter the component?
- How is data transformed or processed?
- Where does data go after processing?
- What state is maintained, and where?

**Error Handling:**
- What errors can occur?
- How are errors caught and handled?
- What happens when operations fail?
- Are there retry mechanisms or fallbacks?

**Edge Cases:**
- Empty inputs or null values
- Boundary conditions (min/max values, empty collections)
- Concurrent access or race conditions
- Resource constraints (memory, connections, file handles)

**Business Logic:**
- What rules or validations are enforced?
- What assumptions does the code make?
- Are there domain-specific constraints?

**Patterns & Conventions:**
- Design patterns used (repository, factory, singleton, etc.)
- Naming conventions
- Code organization principles
- Shared utilities or base classes

### 4. Exploration Checklist
As you explore, ensure you understand:

**Structure:**
- [ ] What are the main classes/modules?
- [ ] What is the inheritance hierarchy?
- [ ] How are components organized (layers, domains, features)?

**Behavior:**
- [ ] What is the primary responsibility of this component?
- [ ] What are the key operations it performs?
- [ ] How does it interact with other components?

**Data:**
- [ ] What data structures are used?
- [ ] How is data validated?
- [ ] Where is data persisted (if applicable)?

**Testing:**
- [ ] What test files exist?
- [ ] What scenarios are tested?
- [ ] Are there integration tests or only unit tests?

**Configuration:**
- [ ] Are there configuration files?
- [ ] Are there environment-specific settings?
- [ ] What can be configured vs hard-coded?

**Dependencies:**
- [ ] What external libraries are used?
- [ ] What internal components does this depend on?
- [ ] Are dependencies injected or tightly coupled?

### 5. Ask for Clarification
**IMPORTANT**: When you encounter ambiguous components, unclear relationships, or confusing implementation details, PAUSE and ask the user for clarification.

**Ask about Architecture:**
- "I see two similar functions X and Y. What's the intended difference between them?"
- "This class seems to handle both parsing and validation. Is that intentional?"
- "The relationship between Component A and Component B is unclear. Can you explain how they interact?"

**Ask about Business Logic:**
- "What should happen when [edge case occurs]?"
- "I see validation rule X, but not Y. Is Y intentionally omitted?"
- "This function returns None in some cases. What should the caller do with that?"

**Ask about Technical Decisions:**
- "Why was [library/pattern X] chosen over [alternative Y]?"
- "I see both synchronous and asynchronous operations. What's the rationale?"
- "Is [performance/security/simplicity] the main concern here?"

**Ask about Scope:**
- "Should I explore [related component] as well?"
- "Is [this functionality] actively used or deprecated?"
- "Are there known issues or planned refactorings I should be aware of?"

Do not make assumptions. Ask questions one by one.

### 6. What NOT to Explore
To maintain focus and efficiency:

**Skip:**
- Third-party library internals (unless custom-modified)
- Auto-generated code (unless it reveals important patterns)
- Deprecated or commented-out code (unless specifically asked)
- Extensive logging/debugging utilities
- Build scripts and infrastructure code (unless that's the target)

**Minimize:**
- Deep dives into trivial getters/setters
- Excessive detail on standard CRUD operations
- Over-analysis of simple utility functions

### 7. Knowledge Verification
When you've completed your exploration, pause and prompt the user with:

**"Do you have any questions?"**

Then respond to each question they ask to demonstrate your understanding. Continue answering questions until the user responds with "n" or "no".

### 8. Document Your Findings
Once the user indicates they have no more questions (by responding "n" or "no"), write your findings to a file named:

`./tasks/explore-{component-name}.md`

For example, if exploring the `db_models` component, output to:
`./tasks/explore-db-models.md`

## Documentation Format

Your output file should be structured for a **Junior Programmer** audience. Follow these guidelines:

### Structure

```markdown
# [Component Name] Exploration

**Exploration Date:** [YYYY-MM-DD]
**Git Commit:** [commit hash]
**Git Branch:** [branch name]
**Component Path:** [relative path from project root]

## Environment
> Reference `./tasks/env.md` for complete environment details

- **Language/Runtime:** [from tasks/env.md]
- **Key Dependencies:** [component-specific dependencies not in tasks/env.md]
- **Build Tools:** [from tasks/env.md]
- **Testing Framework:** [from tasks/env.md]

## Overview
[2-4 sentence summary of the component's purpose and architecture]

## Important Files
- `path/to/file.py:10-50` - Brief description
- `path/to/file.py:100-150` - Brief description
[List key files with important line ranges]

## Related Documents
- **Plans using this exploration:** [list any plan-*.md files that reference this]
- **Related explorations:** [list related explore-*.md files]
- **Supersedes:** [if this is an update, link to previous version]
- **Superseded by:** [if outdated, link to newer version]

## Architecture Summary
[1-2 paragraph overview of how the component is organized and how pieces fit together]

## [Feature/Subsection 1]
[1-3 sentences explaining this feature/section focusing on action and execution]

Key functions:
- `function_name()` - 5-10 word description
- `another_function()` - 5-10 word description

## [Feature/Subsection 2]
[Continue pattern...]

## Edge Cases & Error Handling
[Describe important edge cases and how they're handled]
- Edge case 1: How it's handled
- Edge case 2: How it's handled

## Testing Notes
[Brief overview of test coverage and important test scenarios]
- Test file: `path/to/test.py` - What it tests

## Dependencies
[List key dependencies and why they're used]
- External: Library X for Y functionality
- Internal: Component Z for W operations

## Configuration
[If applicable, note configurable aspects]

## Known Issues / Technical Debt
[If discovered during exploration, note areas that need improvement]

## Questions & Assumptions
[Document anything unclear or assumed during exploration]

## Helper Functions
[Brief list of utility functions, if relevant]
```

### Content Guidelines

**DO:**
- Use clear, simple language (avoid jargon)
- Explain what code DOES, not just what it is
- Focus on execution flow and actions
- List important files with specific line ranges
- Give detailed sections to large, complex, or commonly-used functions
- Provide 1-3 sentences per subsection
- Use 5-10 words per function description
- Include concrete examples where helpful

**DON'T:**
- Use technical jargon without explanation
- Document every small helper function
- Write lengthy descriptions of trivial code
- Assume the reader knows domain-specific concepts
- Include implementation details for simple utility functions

### Function Coverage

- **Large/complex functions**: Get their own subsection with detailed explanation
- **Commonly-used business logic**: Detailed coverage
- **Domain-specific logic**: Detailed coverage with context
- **Small helpers**: Brief mention or omit entirely
- **Trivial utilities**: Omit

### Documentation Style

**Voice & Clarity:**
- Write in active voice: "The function validates input" not "Input is validated"
- Use present tense: "The service creates players" not "The service will create players"
- Be specific: "Throws ValueError when gold < 0" not "Handles invalid gold"
- Provide context: "Used during login process" not just "Authenticates users"

**Technical Level:**
- Assume the reader knows basic programming but not this codebase
- Explain domain-specific terms on first use
- Don't over-explain common patterns (CRUD, validation, etc.)
- Do explain custom or unusual patterns

**Examples:**
- **Too vague:** "Handles player operations"
- **Better:** "Creates, retrieves, and updates player records with validation"
- **Too technical:** "Implements the repository pattern with dependency injection for database abstraction"
- **Better:** "Separates database operations from business logic using service classes"

## Example Output

```markdown
# Database Models Exploration

**Exploration Date:** 2025-11-26
**Git Commit:** a803046
**Git Branch:** main
**Component Path:** ./gamedb/thrift/py/

## Environment
- **Language/Runtime:** Python 3.11
- **Key Dependencies:** SQLite 3.40, Apache Thrift 0.18
- **Build Tools:** pip
- **Testing Framework:** pytest

## Overview
The db_models component provides an abstraction layer for database operations using SQLite. It defines model classes that map to database tables and includes services for CRUD operations. The architecture follows a repository pattern with clear separation between data models and service logic.

## Important Files
- `base_model.py:1-50` - Base class for all models with common DB operations
- `db_tables.py:1-100` - Schema definitions and table creation
- `dbinc/player.py:20-80` - Player model and validation logic
- `services/player_service.py:15-120` - Player CRUD operations and business logic

## Related Documents
- **Plans using this exploration:** plan-add-inventory-management.md
- **Related explorations:** explore-thrift-integration.md
- **Supersedes:** None (initial exploration)
- **Superseded by:** N/A

## Architecture Summary
The component is organized into three layers: models (data structures), services (business logic), and a base layer (shared functionality). Models inherit from BaseModel which provides common database operations. Each model has a corresponding service class that handles complex operations and enforces business rules.

## Player Management
Players are represented by the Player model which stores basic info like name, gold, and location. The PlayerService handles creation, retrieval, and updates while enforcing validation rules like minimum gold amounts.

Key functions:
- `create_player()` - Validates input and creates new player record
- `get_player_by_id()` - Retrieves player with error handling for missing records
- `update_player_gold()` - Safely modifies gold ensuring non-negative values

## Item System
Items have properties like type, weight, and value. Items can exist in inventory or be equipped by players/mobiles.

Key functions:
- `create_item()` - Generates new item with validation
- `assign_to_inventory()` - Links item to container with capacity checks

## Edge Cases & Error Handling
- Missing records: Functions return None or raise specific exceptions
- Invalid gold amounts: Validation prevents negative values before DB writes
- Duplicate player names: Unique constraint enforced at database level

## Testing Notes
- Test file: `dbinc/player_test.py` - Covers CRUD operations and validation
- Test file: `services/player_service_test.py` - Tests business logic and edge cases

## Dependencies
- External: sqlite3 for database operations
- Internal: base_model.py for shared database functionality
```

## Quality Checks

Before completing your documentation, verify:

**Completeness:**
- [ ] All major components are covered
- [ ] Important functions are explained
- [ ] Data flow is clear
- [ ] Error handling is described

**Clarity:**
- [ ] A junior developer could follow your explanation
- [ ] Technical terms are explained
- [ ] Examples are concrete and relevant
- [ ] File paths and line numbers are accurate

**Accuracy:**
- [ ] You've actually read the code you're describing
- [ ] Function descriptions match implementation
- [ ] Relationships between components are correct
- [ ] Edge cases mentioned are actually handled in code

**Usefulness:**
- [ ] The document answers "what does this do?"
- [ ] The document answers "how does it work?"
- [ ] The document answers "where should I look for X?"
- [ ] The document identifies gotchas or non-obvious behavior

## Common Pitfalls to Avoid

**During Exploration:**
- Don't rush - take time to understand before documenting
- Don't skip tests - they reveal important usage patterns
- Don't ignore error handling - it reveals edge cases
- Don't assume - ask when unsure
- Don't get lost in rabbit holes - stay focused on the target component

**During Documentation:**
- Don't document what you haven't read
- Don't copy code comments verbatim - explain in your own words
- Don't over-document trivial code
- Don't under-document complex logic
- Don't forget line number references for important code
- Don't use vague descriptions like "handles things" or "processes data"

## Getting Started

When the user asks you to explore a component:

1. **Load environment context**: Read `./tasks/env.md` to understand the development environment, version control commands, and project conventions. If `./tasks/env.md` doesn't exist, inform the user and suggest running the discovery process from `./gen-env.md` first.

2. **Capture context**: Use the command from `./tasks/env.md` (under "Version Control > Commands for Context Capture") to capture current commit and branch for documentation

3. **Confirm scope**: "Should I explore [specific files/directory/feature]? Are there any areas to focus on or skip?"

4. **Initial scan**: Use Glob/Grep to identify relevant files, then read key files to get a lay of the land

5. **Map the structure**: Identify main classes, entry points, and how pieces connect

6. **Deep dive**: Read through implementations, focusing on complex logic and interactions

7. **Ask questions**: As you encounter ambiguities, ask clarifying questions (one at a time)

8. **Review tests**: Read test files to understand expected behavior and edge cases

9. **Complete analysis**: Ensure you understand all items in the Exploration Checklist

10. **Verify understanding**: Ask "Do you have any questions?"

11. **Answer questions**: Demonstrate your understanding by answering user questions thoroughly

12. **Pre-documentation validation**: Before writing the document, verify you have all required context:
    - [ ] `./tasks/env.md` has been read and understood
    - [ ] Git commit hash captured (using command from tasks/env.md)
    - [ ] Git branch name captured (using command from tasks/env.md)
    - [ ] Component path identified
    - [ ] Current date noted
    - [ ] All questions answered
    - [ ] All checklist items from "Exploration Checklist" completed

13. **Document**: When user says "n" or "no", write the exploration document to `./tasks/explore-{component-name}.md` including the git context captured in step 2

14. **Post-documentation validation**: After writing the document, verify completeness:
    - [ ] Metadata header includes: date, commit, branch, component path
    - [ ] Environment section references `./tasks/env.md` and includes component-specific details
    - [ ] All Important Files have line number references
    - [ ] Cross-references section added (if applicable)
    - [ ] No references to "this file" or "the current directory" (use absolute/relative paths)
    - [ ] Update History section added (if this is an update)
    - [ ] Related Documents section added (if applicable)

15. **Confirm completion**: Let the user know the documentation is complete and where to find it

## How This Document Is Used

The exploration document you create will serve as context for future planning and implementation work:

- **Planning Phase:** When creating a plan for code modifications, AI assistants will read your exploration doc to understand the component architecture before proposing changes
- **Implementation Phase:** Engineers (human or AI) will reference your exploration to understand how to work with the component
- **Different Sessions:** This document must be self-contained since it may be read days or weeks later by different people/agents

**Therefore, ensure your exploration:**
- Uses absolute paths or paths relative to project root (not "this file" or "the current directory")
- Doesn't assume knowledge from your session (all context should be in the document)
- Includes git commit hash and date so readers know if code has changed since exploration
- Documents any incomplete areas so readers know what might need re-exploration

## Cross-Referencing Documents

When writing exploration documents, actively maintain cross-references to other documents:

**Finding related documents:**
```bash
# Search for plans that might reference this component (use shell from tasks/env.md)
grep -l "explore-{component-name}" ./tasks/plan-*.md

# Search for related explorations (use file listing command from tasks/env.md)
ls ./tasks/explore-*{related-keyword}*.md
```

**When to add cross-references:**
- **Plans using this exploration:** Search for plan documents after completing exploration
- **Related explorations:** Link to explorations of closely-related components
- **Supersedes:** When updating an old exploration doc
- **Superseded by:** Update old docs to point to new versions

**Updating cross-references:**
- When creating a plan, go back and update the exploration doc to list the new plan
- When creating a new version of an exploration, update the old one with "Superseded by" link
- Check related docs periodically to ensure cross-references are current

## Handling Updates

If you're asked to update an existing exploration document:

1. **Read the existing document** to understand what was previously documented
2. **Check the changes** between the old commit and current using commands from `./tasks/env.md`:
   ```bash
   # Use VCS commands from ./tasks/env.md for your version control system
   # For git: git log --oneline [old-commit]..HEAD -- [component-path]
   # For git: git diff [old-commit]..HEAD -- [component-path]
   ```
3. **Ask the user**: "Should I update the existing document or create a new version?"
4. **If updating**: Keep the same filename, add an "Update History" section at the top:
   ```markdown
   ## Update History
   - **2025-11-26 (Commit: abc123)**: Updated to reflect refactoring of service layer
   - **2025-11-20 (Commit: def456)**: Initial exploration
   ```
5. **If creating new version**: Use filename pattern `explore-{component}-{YYYY-MM-DD}.md`

**When to update vs create new:**
- **Update**: Minor changes, bug fixes, small refactors
- **Create new**: Major architectural changes, rewrites, when old document is still useful for reference
