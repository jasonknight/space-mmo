# Tasks Directory

This directory contains exploration and planning documents created by AI agents to support software development workflows.

## Document Types

### Exploration Documents (`explore-{component-name}.md`)

**Purpose:** Deep-dive analysis of existing codebase components

**When to create:**
- Before planning modifications to a component
- When onboarding to a new part of the codebase
- When component behavior is unclear or undocumented

**Naming convention:**
- Standard: `explore-{component-name}.md` (e.g., `explore-database-layer.md`)
- Versioned: `explore-{component-name}-{YYYY-MM-DD}.md` (for major rewrites)

**Created by:** AI agents following instructions in `../gen-explore.md`

### Planning Documents (`plan-{change-name}.md`)

**Purpose:** Detailed implementation plans for code modifications

**When to create:**
- Before implementing new features
- Before refactoring existing code
- Before fixing complex bugs
- Before architectural changes

**Naming convention:**
- Standard: `plan-{change-name}.md` (e.g., `plan-add-user-authentication.md`)
- Addendum: `plan-{change-name}-addendum-{YYYY-MM-DD}.md` (for requirement changes)

**Created by:** AI agents following instructions in `../gen-plan.md`

## Workflow

### Standard Workflow

```
1. EXPLORE → 2. PLAN → 3. IMPLEMENT → 4. TEST → 5. DEPLOY

┌─────────────────┐
│  User requests  │
│  code change    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  AI explores    │─────→│  explore-*.md    │
│  component(s)   │      │  created         │
└────────┬────────┘      └──────────────────┘
         │                        │
         │                        │ (read as context)
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  AI creates     │─────→│  plan-*.md       │
│  detailed plan  │      │  created         │
└────────┬────────┘      └──────────────────┘
         │                        │
         │                        │ (follow steps)
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  Engineer       │      │  Implementation  │
│  implements     │─────→│  complete        │
└─────────────────┘      └──────────────────┘
```

### Workflow Variations

**Quick changes (no exploration needed):**
```
User request → Plan → Implement
```

**Re-exploration needed:**
```
User request → Check exploration freshness → Re-explore → Plan → Implement
```

**Implementation without planning (trivial changes):**
```
User request → Implement directly
```

## File Metadata

All documents in this directory should include metadata headers:

### Exploration Documents

```markdown
# [Component Name] Exploration

**Exploration Date:** 2025-11-26
**Git Commit:** a803046abc123
**Git Branch:** main
**Component Path:** ./gamedb/thrift/py/
**Environment:**
- Python: 3.11
- Key dependencies: sqlite3, thrift
```

### Planning Documents

```markdown
# Plan: [Change Name]

**Plan Date:** 2025-11-26
**Target Branch:** feature/add-caching
**Current Commit:** a803046abc123
**Estimated Complexity:** Medium
**Based on Explorations:**
- explore-database-layer.md (2025-11-20, commit: abc123)
```

## Document Freshness

Documents can become stale as code evolves. Check freshness before using:

### Check if exploration is stale

```bash
# From exploration doc, get commit hash and component path
EXPLORE_COMMIT="abc123"
COMPONENT_PATH="./gamedb/thrift/py/"

# Check for changes since exploration
git log --oneline $EXPLORE_COMMIT..HEAD -- $COMPONENT_PATH
```

If this shows commits, the component has changed since exploration.

### Check if plan is stale

```bash
# From plan doc, get commit hash and affected paths
PLAN_COMMIT="abc123"
AFFECTED_PATHS="./gamedb/thrift/py/ ./services/"

# Check for changes since plan
git log --oneline $PLAN_COMMIT..HEAD -- $AFFECTED_PATHS
```

If this shows commits, the plan may need updates.

## Document Lifecycle

### Creating Documents

1. **Exploration:** Run AI agent with `gen-explore.md` instructions
2. **Planning:** Run AI agent with `gen-plan.md` instructions

### Updating Documents

**When to update vs. create new:**

| Scenario | Action | Naming |
|----------|--------|--------|
| Minor code changes | Update existing | Keep same filename |
| Bug fixes | Update existing | Keep same filename |
| Small refactors | Update existing | Keep same filename |
| Major architectural changes | Create new version | Add date suffix |
| Complete rewrites | Create new version | Add date suffix |
| Plan addendums | Create addendum | Add addendum suffix |

**Update history format:**

```markdown
## Update History
- **2025-11-26 (Commit: def456)**: Updated to reflect new caching layer
- **2025-11-20 (Commit: abc123)**: Initial exploration
```

### Archiving Documents

When documents are no longer relevant:

```bash
# Create archive directory if needed
mkdir -p ./tasks/archive/

# Move old documents
mv explore-old-component.md ./tasks/archive/
```

## Best Practices

### For AI Agents

1. **Always capture git context** at the start of each session
2. **Check exploration freshness** before creating plans
3. **Use absolute paths** or paths relative to project root
4. **Document incomplete areas** so future agents know what's missing
5. **Cross-reference related documents** in metadata sections

### For Human Engineers

1. **Check document dates** before relying on them
2. **Update documents** when making significant changes
3. **Add notes** about discovered issues or gotchas
4. **Link plans to PRs** in commit messages or PR descriptions
5. **Archive obsolete documents** rather than deleting them

## Common Issues

### "Plan references non-existent exploration doc"

**Cause:** Exploration was skipped or file was moved/deleted

**Solution:**
1. Search for related exploration docs: `ls explore-*related*.md`
2. If none exist, create exploration before implementing
3. Update plan to reference correct exploration doc

### "Exploration is 50+ commits old"

**Cause:** Code has evolved significantly since exploration

**Solution:**
1. Review commits: `git log --oneline <old-commit>..HEAD -- <path>`
2. Check if changes are significant
3. Re-explore if architecture has changed
4. Update exploration doc if changes are minor

### "Multiple exploration docs for same component"

**Cause:** Component was re-explored without archiving old version

**Solution:**
1. Check dates and commits on each
2. Use most recent version
3. Archive older versions to `./tasks/archive/`
4. Consider if old versions have useful historical context

### "Plan references commit that doesn't exist"

**Cause:** Working across different git clones or branches

**Solution:**
1. Check if commit exists: `git log <commit-hash>`
2. If missing, check branch: `git branch -r --contains <commit-hash>`
3. Ensure working on correct branch
4. Update plan with current commit if needed

## File Naming Quick Reference

```
explore-{component}.md           # Standard exploration
explore-{component}-{date}.md    # Versioned exploration
plan-{change}.md                 # Standard plan
plan-{change}-addendum-{date}.md # Plan addendum
```

## Examples

### Example Exploration Filename
```
explore-database-layer.md
explore-authentication-service.md
explore-api-endpoints-2025-11-26.md (versioned)
```

### Example Plan Filename
```
plan-add-user-authentication.md
plan-refactor-database-layer.md
plan-add-caching-addendum-2025-11-26.md (addendum)
```

## Directory Structure

```
tasks/
├── README.md                           # This file
├── explore-component-a.md              # Exploration docs
├── explore-component-b.md
├── plan-feature-x.md                   # Planning docs
├── plan-feature-y.md
└── archive/                            # Archived docs
    ├── explore-old-component.md
    └── plan-deprecated-feature.md
```

## Getting Help

- **For exploration instructions:** See `../gen-explore.md`
- **For planning instructions:** See `../gen-plan.md`
- **For implementation guidelines:** See project `../CLAUDE.md`
- **For git workflow:** See project documentation

## Contributing

When improving the exploration or planning process:

1. Update the relevant guide (`explore.md` or `plan.md`)
2. Update this README if workflow changes
3. Update example documents to reflect new format
4. Communicate changes to team members and AI agent users
