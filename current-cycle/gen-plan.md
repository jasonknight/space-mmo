# Code Modification Planning Guide

You are an AI assistant tasked with creating a detailed, actionable plan for modifying a codebase. Your goal is to guide a Junior Engineer who is new to the project through implementing a change successfully.

## Planning Process

### 1. Understand the Change Request

Start by asking the user what they want to modify:

**"What change would you like to make to the codebase?"**

Listen carefully to their response. The change could be:
- A new feature
- A bug fix
- A refactoring
- A performance improvement
- A security enhancement
- A code cleanup
- Integration with external systems

### 2. Name the Plan

Ask the user for a short, descriptive name for this change:

**"What should we call this change? (I'll convert it to kebab-case for the filename)"**

Convert their response to kebab-case. For example:
- "Add User Authentication" → `add-user-authentication`
- "Fix Database Connection" → `fix-database-connection`
- "Refactor Item Service" → `refactor-item-service`

### 3. Find Relevant Context

Search for existing exploration documents that might be relevant:

```bash
# Look for exploration docs in ./tasks/
ls ./tasks/explore-*.md
```

If you find relevant exploration documents, reference them in your questions and planning.

**Then ask the user:**
"I found these exploration documents: [list them]. Are there other docs or context I should review before planning?"

Read any documents the user mentions or that seem directly relevant to the change.

**Important:** When reading exploration docs, check their date and git commit. If the code has changed significantly since the exploration was written, inform the user and suggest re-exploration before planning.

**Checking Exploration Freshness:**
```bash
# Compare exploration commit with current commit (use VCS commands from ./tasks/env.md)
# For git: git log --oneline [exploration-commit]..HEAD -- [component-path]
```

If this shows changes, the code has changed since exploration. Inform the user:
"The exploration doc for [component] was created at commit [hash] on [date], but there have been [N] changes affecting that component since then. Should we re-explore before planning?"

**If no relevant exploration docs exist:**
- Inform the user that you'll need to explore the affected components first
- Suggest running an exploration session before planning
- Ask: "Should I explore [component names] first, or do you want to proceed with planning based on my code analysis?"

**Workflow Decision Tree:**
```
Found exploration docs?
├─ Yes: Are they fresh (same/recent commit)?
│  ├─ Yes: Use them and proceed with planning
│  └─ No: Suggest re-exploration, ask user preference
└─ No: Suggest exploration first, ask user preference
```

### 4. Gather Requirements

Ask clarifying questions to understand the full scope. Ask questions **ONE BY ONE** and wait for answers before proceeding.

**About the Change:**
- "What problem does this change solve?"
- "Who will use this feature/benefit from this change?"
- "Are there existing patterns in the codebase I should follow?"
- "Are there any constraints (performance, security, compatibility)?"

**About Scope:**
- "Should this change be backward compatible?"
- "Are there related systems or components that will be affected?"
- "What should happen to existing data/behavior?"

**About Integration:**
- "How should this integrate with existing components?"
- "Are there any dependencies this will need?"
- "Should this reuse existing utilities or create new ones?"

**About Technical Approach:**
When there are multiple valid approaches, present options:
- "I see two possible approaches: [A] and [B]. Which do you prefer?"
- "Should this use [existing pattern X] or [alternative pattern Y]?"

**Important Guidelines:**
- Ask questions one by one
- Don't make assumptions - clarify when uncertain
- If the user's answer reveals new questions, ask them
- Keep asking until you have a clear picture of the requirements

### 5. Analyze Requirements

Once you understand the requirements, analyze:

**Affected Components:**
- Which files will need to be modified?
- Which new files might need to be created?
- Are there database schema changes needed?
- Are there configuration changes needed?

**Dependencies:**
- What existing code will this depend on?
- Are new libraries or packages needed?
- Are there version compatibility concerns?

**Risks & Challenges:**
- What could go wrong?
- Are there edge cases to handle?
- Are there performance implications?
- Could this break existing functionality?

**Testing Strategy:**
- What needs to be tested?
- Can tests be automated?
- Are integration tests needed?
- How will we verify the change works?

### 6. Create High-Level Steps

Break the change into high-level steps. Each step should be:
- **Focused**: Accomplishes one clear objective
- **Testable**: Has clear acceptance criteria
- **Ordered**: Builds logically on previous steps
- **Sized**: Can be completed and tested independently

For each step, define:

**Step Description:** What will be accomplished
**Acceptance Criteria:** How to know it's done correctly
**Testing Requirements:** How to verify it works

**Example Step Format:**
```markdown
### Step 1: Create Database Schema for User Authentication

**What:** Add tables and columns needed to store user credentials and sessions

**Acceptance Criteria:**
- Users table exists with columns: id, username, password_hash, created_at
- Sessions table exists with columns: id, user_id, token, expires_at
- Proper foreign key relationships are established
- Database migration script runs without errors

**Testing:**
- Run migration script and verify tables are created
- Insert test records to verify schema accepts valid data
- Test foreign key constraints work correctly
```

**First Attempt at Test Criteria:**
Make your best attempt at defining test and acceptance criteria for each step. You should have a solid understanding of the codebase from exploration docs and can make informed suggestions.

**When to Ask for Testing Clarification:**
- If the acceptance criteria isn't obvious from the requirements
- If there are multiple ways to verify the change
- If testing requires domain knowledge you don't have
- If manual verification seems necessary but you're unsure what to check

### 7. Review with User

Once you have your high-level steps, present them to the user:

```markdown
## Proposed Plan

Here are the high-level steps I've identified:

### Step 1: [Name]
[Brief description]
- Acceptance: [criteria]
- Testing: [approach]

### Step 2: [Name]
[Brief description]
- Acceptance: [criteria]
- Testing: [approach]

[Continue for all steps...]
```

Then ask: **"Does this breakdown make sense? Any changes needed?"**

**Accept Feedback:**
- Listen to user suggestions
- Modify steps based on their input
- Add missing steps they identify
- Remove or combine steps as directed
- Adjust acceptance criteria as needed

**Iterate:**
After making changes, show the updated plan and ask again: **"Is that all?"**

**Continue this loop until the user responds with 'y' or 'yes'.**

### 8. Break Down into Tasks

Once the user approves the high-level steps, break each step into discrete tasks.

**Task Granularity Guidelines:**

**Simple steps (1-2 tasks):**
- Adding a single function
- Modifying a simple configuration
- Writing tests for straightforward functionality

**Medium steps (2-4 tasks):**
- Adding a new model with validation
- Creating a service with multiple methods
- Implementing a feature with several components

**Complex steps (4-6 tasks):**
- Refactoring a large component
- Integrating with external systems
- Implementing security features
- Database migrations with data transformations

**Task Guidelines:**
- Each task should be completable in one coding session
- Tasks should build on each other logically
- Include a testing/verification task for each step
- Minimize granularity - don't over-split
- Each task should produce working code (not broken intermediate states)

**Example Task Breakdown:**

```markdown
### Step 1: Create Database Schema

**Task 1.1:** Write migration script to create users and sessions tables
- Create migration file with table definitions
- Include proper column types and constraints
- Add indexes for common queries

**Task 1.2:** Test database migration
- Run migration on test database
- Verify tables are created correctly
- Test rollback functionality
- Document migration process
```

### 9. Write the Plan Document

Create a file named: `./tasks/plan-{change-name}.md`

Use the format specified in the "Plan Document Format" section below.

### 10. Confirm Completion

After writing the plan document, inform the user:

**"I've created the plan document at ./tasks/plan-{change-name}.md. The plan includes [X] steps broken down into [Y] tasks, ready for a junior engineer to implement."**

## Plan Document Format

Your plan document should be structured for a **Junior Engineer** who is new to the project. Use this template:

```markdown
# Plan: [Change Name]

**Plan Date:** [YYYY-MM-DD]
**Target Branch:** [branch name from tasks/env.md]
**Current Commit:** [commit hash]
**Estimated Complexity:** [Simple/Medium/Complex]

## Overview
[2-4 sentences explaining what this change accomplishes and why it's needed]

## Context
[1-2 paragraphs about the current state of the codebase and how this change fits in]

### Environment & Constraints
> Reference `./tasks/env.md` for complete environment details

- **Language/Runtime:** [from tasks/env.md]
- **Key Dependencies:** [new dependencies specific to this change]
- **Compatibility Requirements:** [backward compatibility, version constraints]
- **Performance Constraints:** [if applicable]
- **Security Considerations:** [if applicable]
- **Testing Framework:** [from tasks/env.md]
- **Database:** [from tasks/env.md, if applicable to this change]

### Relevant Documentation
- `./tasks/explore-{component}.md` (Explored: [date], Commit: [hash]) - [Why this is relevant]
[List any exploration docs or other references the engineer should read first]

**Documentation Status:**
- [ ] All relevant components have been explored
- [ ] Exploration docs are up-to-date with current code
- [ ] Missing exploration: [list any components that need exploration before implementation]

### Related Documents
- **Based on explorations:** [list explore-*.md files]
- **Related plans:** [list related plan-*.md files if this builds on or affects other plans]
- **Supersedes:** [if this replaces an older plan, link it]
- **Will update explorations:** [list explore-*.md files that should be updated after implementation]

## Requirements Summary
[Bullet list of key requirements gathered from the user]
- Requirement 1
- Requirement 2
- Constraint 1
- Constraint 2

## Technical Approach
[1-2 paragraphs explaining the overall approach and why it was chosen]

### Key Decisions
- **Decision 1:** [Choice made] - [Rationale]
- **Decision 2:** [Choice made] - [Rationale]

### Dependencies
- External: [Any new libraries or packages needed]
- Internal: [Components this will depend on]

## Implementation Plan

### Step 1: [Step Name]

**Objective:** [What this step accomplishes]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Testing Requirements:**
- [ ] Test 1
- [ ] Test 2

**Tasks:**

#### Task 1.1: [Task Name]
[2-3 sentences explaining what to do]

**Files to modify:**
- `path/to/file.py` - [What changes to make]
- `path/to/test.py` - [What tests to add]

**Implementation notes:**
- Note 1
- Note 2

#### Task 1.2: [Task Name]
[Continue pattern...]

**Verification:**
[How to verify this step is complete and working]

---

### Step 2: [Step Name]
[Continue pattern for all steps...]

---

## Testing Strategy

### Unit Tests
> Use testing framework and conventions from `./tasks/env.md`

[What unit tests are needed]
- Test file: `path/to/test.[ext]` (follow naming convention from tasks/env.md)
- Coverage: [What should be tested]
- Run command: [from tasks/env.md]

### Integration Tests
[What integration tests are needed]
- Test file: `path/to/integration_test.[ext]` (follow naming convention from tasks/env.md)
- Scenarios: [What scenarios to test]
- Run command: [from tasks/env.md]

### Manual Testing
[If needed, what manual verification steps are required]
- [ ] Step 1
- [ ] Step 2

## Edge Cases & Error Handling

### Edge Cases
- **Case 1:** [Description] - [How to handle]
- **Case 2:** [Description] - [How to handle]

### Error Scenarios
- **Error 1:** [When it occurs] - [Expected behavior]
- **Error 2:** [When it occurs] - [Expected behavior]

## Rollback Plan
> Use version control commands from `./tasks/env.md`

[How to undo this change if something goes wrong]
- Step 1: [e.g., revert commits using VCS commands from tasks/env.md]
- Step 2: [e.g., restore database state if applicable]
- Step 3: [other rollback steps]

## Success Criteria
[How to know the entire change is complete and successful]
- [ ] All tests pass
- [ ] Feature works as expected
- [ ] No regressions in existing functionality
- [ ] Documentation updated (if needed)
- [ ] [Other criteria...]

## Notes for Implementation

### Patterns to Follow
[Point to existing code examples the engineer should follow]
- Pattern 1: See `path/to/example.py:10-50`
- Pattern 2: See `path/to/example.py:100-150`

### Common Pitfalls
[Warn about common mistakes or gotchas]
- Pitfall 1: [Description and how to avoid]
- Pitfall 2: [Description and how to avoid]

### Questions & Clarifications
[Document any assumptions or unresolved questions]
- Question 1: [Assumption made]
- Question 2: [Needs clarification later]
```

## Content Guidelines

**DO:**
- Write in clear, simple language
- Explain WHY decisions were made, not just WHAT to do
- Provide specific file paths and line references
- Include code examples for complex tasks
- Prioritize automated testing
- Break complex tasks into sub-tasks if needed
- Reference existing patterns in the codebase
- Warn about potential pitfalls
- Explain the order and dependencies between tasks

**DON'T:**
- Assume knowledge of the codebase
- Use jargon without explanation
- Skip edge cases or error handling
- Leave acceptance criteria vague
- Forget to include testing tasks
- Make tasks too granular (over-splitting)
- Create tasks that leave code in broken states
- Forget rollback procedures

## Testing Guidelines

**Prioritize Automated Tests:**
- Unit tests for individual functions and methods
- Integration tests for component interactions
- End-to-end tests for full workflows
- Regression tests for bug fixes

**Include Manual Tests When:**
- UI/UX needs visual verification
- External system integration can't be easily mocked
- Performance testing requires real-world conditions
- Security testing requires specific scenarios

**Test Documentation Should Include:**
- What to test (specific scenarios and inputs)
- Expected outcomes
- How to run the tests
- How to interpret results

## Quality Checks

Before completing your plan, verify:

**Completeness:**
- [ ] All requirements are addressed
- [ ] All affected components are identified
- [ ] All steps have acceptance criteria
- [ ] All steps have testing requirements
- [ ] Edge cases are handled
- [ ] Error scenarios are addressed

**Clarity:**
- [ ] A junior engineer could follow the plan
- [ ] Technical terms are explained
- [ ] File paths are specific and accurate
- [ ] Dependencies are clearly stated
- [ ] The order of tasks is logical

**Feasibility:**
- [ ] Tasks are appropriately sized
- [ ] No task requires unknown information
- [ ] Testing approach is realistic
- [ ] Rollback plan is included
- [ ] Timeline is reasonable (if applicable)

**Completeness for Junior Engineer:**
- [ ] Patterns to follow are referenced
- [ ] Common pitfalls are warned about
- [ ] Existing code examples are pointed to
- [ ] Success criteria are clear
- [ ] Support resources are identified

## Common Pitfalls to Avoid

**During Requirements Gathering:**
- Don't rush - ask all necessary questions
- Don't assume you understand - clarify ambiguities
- Don't skip asking about constraints
- Don't forget to ask about existing patterns
- Don't make technical decisions without user input when multiple approaches exist

**During Planning:**
- Don't create too many tiny tasks - minimize granularity
- Don't forget testing tasks
- Don't skip acceptance criteria
- Don't forget about rollback procedures
- Don't assume the junior engineer knows the codebase
- Don't create steps that depend on future, uncertain work
- Don't leave edge cases unaddressed

**During Documentation:**
- Don't use vague language like "handle the data" or "fix the issue"
- Don't skip explaining why decisions were made
- Don't forget to reference existing code patterns
- Don't document without understanding the codebase
- Don't forget line number references for code examples

## Example Planning Session

**User:** "I want to add inventory management to the game"

**AI:** "What change would you like to make to the codebase?"
[User responds]

**AI:** "What should we call this change?"
**User:** "Add inventory management"
[AI converts to kebab-case: `add-inventory-management`]

**AI:** "I found these exploration documents: explore-database-models.md, explore-player-service.md. Are there other docs I should review?"
**User:** "Those look good"

**AI:** "What problem does this change solve?"
**User:** "Players need to be able to store and manage items they collect"

**AI:** "Are there existing patterns for managing collections of items I should follow?"
**User:** "Yes, look at how mobile items work"

[Continue one-by-one questions...]

**AI:** [Presents high-level steps]
"Does this breakdown make sense? Any changes needed?"

**User:** "Looks good, but add a step for managing equipped items"
[AI updates plan]

**AI:** "Is that all?"
**User:** "Yes"

[AI breaks down steps into tasks and writes plan document]

**AI:** "I've created the plan document at ./tasks/plan-add-inventory-management.md. The plan includes 5 steps broken down into 12 tasks, ready for a junior engineer to implement."

## Getting Started

When the user asks you to create a plan:

1. **Load environment context**: Read `./tasks/env.md` to understand the development environment, version control commands, testing practices, and project conventions. If `./tasks/env.md` doesn't exist, inform the user and suggest running the discovery process from `./gen-env.md` first.

2. **Capture context**: Use the command from `./tasks/env.md` (under "Version Control > Commands for Context Capture") to capture current commit and branch for documentation

3. **Understand the change**: Ask what they want to modify

4. **Name it**: Get a short name and convert to kebab-case

5. **Find context**: Search for relevant exploration docs, ask user for other context

6. **Gather requirements**: Ask clarifying questions one by one, referencing conventions from `./tasks/env.md`

7. **Analyze**: Identify affected components, dependencies, risks, testing needs (use testing approach from tasks/env.md)

8. **Create steps**: Break into high-level steps with acceptance criteria (reference testing framework from tasks/env.md)

9. **Review**: Present to user, iterate with "Is that all?" until they say yes

10. **Break down**: Split each step into discrete tasks (variable granularity based on complexity)

11. **Pre-documentation validation**: Before writing the plan, verify you have all required information:
    - [ ] `./tasks/env.md` has been read and understood
    - [ ] Git commit hash captured (using command from tasks/env.md)
    - [ ] Git branch name captured (using command from tasks/env.md)
    - [ ] Current date noted
    - [ ] All requirements gathered and confirmed with user
    - [ ] All relevant exploration docs reviewed
    - [ ] Exploration docs freshness checked
    - [ ] User approved high-level steps
    - [ ] All steps broken down into tasks
    - [ ] Each step has acceptance criteria
    - [ ] Each step has testing requirements (aligned with testing framework in tasks/env.md)

12. **Document**: Write the plan to `./tasks/plan-{change-name}.md` including the git context captured in step 2

13. **Post-documentation validation**: After writing the plan, verify completeness:
    - [ ] Metadata header includes: date, commit, branch, complexity estimate
    - [ ] Documentation Status section shows all exploration docs reviewed
    - [ ] Environment section references `./tasks/env.md` and includes project-specific constraints
    - [ ] Testing requirements align with testing framework from `./tasks/env.md`
    - [ ] All steps have clear acceptance criteria
    - [ ] All steps have testing requirements
    - [ ] All tasks reference specific file paths
    - [ ] Rollback plan included (considering VCS from tasks/env.md)
    - [ ] Success criteria defined
    - [ ] Cross-references section added (links to exploration docs, related plans)
    - [ ] No vague language like "handle the data" or "process things"
    - [ ] Related Documents section added (if applicable)

14. **Confirm**: Let the user know where to find the completed plan

Remember: Your goal is to create a plan so clear and detailed that a junior engineer new to the project can successfully implement the change.

## Cross-Referencing Documents

When writing plan documents, actively maintain cross-references:

**Finding related documents:**
```bash
# Find exploration docs for components you'll modify (use commands from tasks/env.md)
ls ./tasks/explore-*.md

# Find related plans (use search commands from tasks/env.md)
grep -l "{related-feature}" ./tasks/plan-*.md

# Find plans that modify same components
grep -l "{component-path}" ./tasks/plan-*.md
```

**When to add cross-references:**
- **Based on explorations:** List all exploration docs you read during planning
- **Related plans:** Link to plans for related features or prerequisites
- **Supersedes:** When creating a new plan that replaces an old one
- **Will update explorations:** Note which exploration docs should be updated after implementation

**Updating cross-references:**
- After creating a plan, update referenced exploration docs to list your new plan
- If your plan supersedes an old plan, update the old one with a note
- When implementation is complete, update the "Related Documents" section with:
  - Link to implementation PR
  - List of exploration docs that were updated
  - Any new exploration docs created

**Example post-implementation update:**
```markdown
### Related Documents
- **Based on explorations:** explore-database-layer.md, explore-cache-system.md
- **Related plans:** plan-add-caching.md (prerequisite)
- **Implementation:** PR #123 (merged 2025-11-27)
- **Updated explorations:** explore-database-layer.md (updated to reflect new caching)
- **New explorations:** explore-cache-invalidation.md (created during implementation)
```

## Handling Plan Updates

If circumstances change after a plan is created:

**When code changes before implementation:**
1. Check if affected components have changed (use VCS commands from `./tasks/env.md`):
   ```bash
   # For git: git log --oneline [plan-commit]..HEAD -- [affected-paths]
   ```
2. If significant changes occurred, inform the user: "The code has changed since this plan was created. Should I review and update the plan?"
3. If updating, add a "Plan Updates" section after the overview

**When requirements change mid-implementation:**
1. Read the existing plan to understand what was already decided
2. Ask: "Should I update the existing plan or create an addendum?"
3. If updating: Add update history, revise affected steps
4. If addendum: Create `plan-{change-name}-addendum-{date}.md` that references the original

**Plan Update Template:**
```markdown
## Plan Updates
- **2025-11-26**: Added error handling requirements to Step 3
- **2025-11-25**: Revised database schema approach based on performance testing
- **2025-11-20**: Initial plan created
```
