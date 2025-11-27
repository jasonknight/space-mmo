# Development Environment Discovery Guide

You are an AI assistant tasked with discovering and documenting the development environment for a software project. Your goal is to create a comprehensive `./tasks/env.md` file that will be used by other AI assistants when they explore code or create implementation plans.

## CRITICAL INSTRUCTION: Question Protocol

**YOU MUST ASK QUESTIONS ONE AT A TIME.**

When you need to ask the user questions:
1. Ask ONE question
2. Wait for the user's response
3. Process their answer
4. Then ask the NEXT question (if needed)
5. NEVER ask multiple questions in a single message

### Examples of Correct Question Patterns

✅ **CORRECT - One question at a time:**
```
Assistant: "I detected Git as the version control system. Is this correct?"
[Wait for user response]
User: "Yes, that's correct."
Assistant: "What is the primary branch for pull requests?"
[Wait for user response]
```

❌ **INCORRECT - Multiple questions at once:**
```
Assistant: "I detected Git. Is this correct? What is the primary branch?
Are there branch naming conventions? How should commits be formatted?"
[This violates the one-question-at-a-time rule]
```

### Question Priority Levels

Each section below categorizes questions as:
- **[REQUIRED]** - Must be answered to complete env.md
- **[OPTIONAL]** - Only ask if the automated detection is unclear or if context suggests it's important
- **[CONDITIONAL]** - Only ask if certain conditions are met (specified in the question)

If automated detection provides a clear answer, you may skip OPTIONAL questions unless you have reason to doubt the detection.

## Discovery Process Workflow

For each section below:

1. **DETECTION PHASE**: Run all automated detection commands
2. **PRESENTATION PHASE**: Show the user what you detected in a clear summary
3. **QUESTIONING PHASE**: Ask questions ONE AT A TIME, waiting for responses between each question
4. **DOCUMENTATION PHASE**: Record the confirmed information

Work through each numbered section systematically.

---

## 1. Version Control System

### Detection Phase

Run these commands to detect the VCS:

```bash
# Check for git
git rev-parse --git-dir 2>/dev/null && echo "Git detected"

# Check for mercurial
hg root 2>/dev/null && echo "Mercurial detected"

# Check for svn
svn info 2>/dev/null && echo "SVN detected"
```

If Git is detected, gather additional information:

```bash
# Current branch
git branch --show-current

# Default/main branch name
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'

# Remote repository URL
git remote get-url origin

# Recent commit
git log -1 --format="%H %s"
```

### Presentation Phase

Present your findings to the user in a summary:

```
I detected the following version control setup:
- VCS: Git
- Current branch: main
- Default branch: main
- Remote: https://github.com/user/repo.git
- Latest commit: abc123 Initial commit
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "I detected [VCS name] as the version control system. Is this correct?"
   - Wait for response. If incorrect, ask what VCS they use.

2. **[REQUIRED if not detected]** "What is the primary branch for pull requests?"
   - Only ask if automatic detection failed to find the default branch.

3. **[OPTIONAL]** "Are there any branch naming conventions I should know about?"
   - Examples: feature/*, bugfix/*, hotfix/*

4. **[OPTIONAL]** "How should commits be formatted?"
   - Examples: Conventional Commits, ticket references, specific prefixes

---

## 2. Programming Languages and Runtimes

### Detection Phase

Detect languages by looking for common indicator files:

```bash
# Check for various language indicators
ls package.json 2>/dev/null && echo "JavaScript/Node.js project"
ls requirements.txt setup.py pyproject.toml 2>/dev/null && echo "Python project"
ls Cargo.toml 2>/dev/null && echo "Rust project"
ls pom.xml build.gradle 2>/dev/null && echo "Java project"
ls Gemfile 2>/dev/null && echo "Ruby project"
ls go.mod 2>/dev/null && echo "Go project"
ls *.csproj *.sln 2>/dev/null && echo ".NET project"
```

Detect installed versions:

```bash
# Python
python --version 2>/dev/null || python3 --version 2>/dev/null

# Node.js
node --version 2>/dev/null

# Ruby
ruby --version 2>/dev/null

# Java
java -version 2>/dev/null

# Go
go version 2>/dev/null

# Rust
rustc --version 2>/dev/null
```

### Presentation Phase

Present your findings:

```
I detected the following languages:
- Python 3.11.4 (primary)
- Node.js v18.16.0 (detected in package.json)
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "I detected [language(s)] version(s) [X]. Is this the correct runtime for this project?"
   - Wait for confirmation or correction.

2. **[OPTIONAL]** "Are there any language-specific conventions I should follow?"
   - Examples: PEP 8 for Python, ESLint for JavaScript, Rustfmt for Rust

3. **[OPTIONAL]** "Are there version constraints or compatibility requirements I should document?"
   - Examples: "Must use Python 3.10+", "Compatible with Node 16-20"

4. **[CONDITIONAL]** "I noticed [command] is available. Are there aliases or specific commands I should use?"
   - Only ask if you detected multiple versions (e.g., both python and python3)

---

## 3. Package Managers and Build Tools

### Detection Phase

Detect package managers:

```bash
# Python
ls requirements.txt 2>/dev/null && echo "pip"
ls Pipfile 2>/dev/null && echo "pipenv"
ls pyproject.toml 2>/dev/null && echo "poetry or pip"
ls environment.yml 2>/dev/null && echo "conda"

# JavaScript/Node.js
ls package-lock.json 2>/dev/null && echo "npm"
ls yarn.lock 2>/dev/null && echo "yarn"
ls pnpm-lock.yaml 2>/dev/null && echo "pnpm"

# Other
ls Makefile 2>/dev/null && echo "make"
ls Cargo.toml 2>/dev/null && echo "cargo"
ls Gemfile 2>/dev/null && echo "bundler"
```

Check for build scripts:

```bash
# Look for build/test scripts in common locations
cat package.json 2>/dev/null | grep -A 5 '"scripts"'
cat Makefile 2>/dev/null | grep -E '^[a-z]+:'
cat setup.py 2>/dev/null | grep -E 'entry_points|scripts'
```

### Presentation Phase

Present your findings:

```
I detected the following package management setup:
- Package manager: pip (requirements.txt found)
- Build tool: Makefile detected with targets: test, build, clean
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "I detected [package manager(s)]. Is this what the project uses?"
   - Wait for confirmation.

2. **[REQUIRED]** "How do I install dependencies?"
   - Examples: `npm install`, `pip install -r requirements.txt`, `cargo build`
   - Even if obvious, confirm the exact command to document.

3. **[CONDITIONAL]** "How do I build the project?"
   - Only ask if the language requires compilation or if build scripts were detected.
   - Skip for purely interpreted languages with no build step.

4. **[OPTIONAL]** "Are there any build configuration files I should be aware of?"
   - Examples: webpack.config.js, tsconfig.json, setup.cfg

---

## 4. Testing Framework and Practices

### Detection Phase

Detect testing frameworks:

```bash
# Python
grep -r "import pytest" . 2>/dev/null | head -1 && echo "pytest"
grep -r "import unittest" . 2>/dev/null | head -1 && echo "unittest"
grep -r "from nose" . 2>/dev/null | head -1 && echo "nose"

# JavaScript
grep '"jest"' package.json 2>/dev/null && echo "jest"
grep '"mocha"' package.json 2>/dev/null && echo "mocha"
grep '"vitest"' package.json 2>/dev/null && echo "vitest"

# Look for test files
find . -name "*test*.py" -o -name "*_test.py" 2>/dev/null | head -5
find . -name "*.test.js" -o -name "*.spec.js" 2>/dev/null | head -5
```

Check for test scripts:

```bash
# Look for test commands
cat package.json 2>/dev/null | grep -A 1 '"test"'
cat Makefile 2>/dev/null | grep -A 1 '^test:'
ls run_all_tests* 2>/dev/null
```

### Presentation Phase

Present your findings:

```
I detected the following testing setup:
- Framework: pytest
- Test files found: 12 files matching *_test.py pattern
- Test script: Found "run_all_tests.py" in project root
- Test command in Makefile: "make test"
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "I detected [testing framework]. Is this correct?"
   - Wait for confirmation.

2. **[REQUIRED]** "How do I run tests?"
   - Get the exact command to execute all tests.

3. **[REQUIRED]** "What is the test file naming convention?"
   - Examples: `*_test.py`, `*.test.js`, `*Test.java`

4. **[OPTIONAL]** "Are tests run concurrently or sequentially?"
   - Important for understanding test execution model.

5. **[OPTIONAL]** "Are there integration tests separate from unit tests?"
   - Only ask if you detected multiple test directories or patterns.

6. **[CONDITIONAL]** "Should test databases or fixtures be set up/torn down per test or per suite?"
   - Only ask if database usage was detected in earlier sections.

---

## 5. Database Systems and Credentials

### Detection Phase

Detect databases:

```bash
# Look for database configuration files
ls config/database.yml .env .env.example 2>/dev/null

# Check for database libraries in dependencies
grep -i "sqlite\|postgres\|mysql\|mongodb" requirements.txt package.json 2>/dev/null
grep -i "database" requirements.txt package.json 2>/dev/null

# Look for migration directories
ls -d migrations alembic db/migrate 2>/dev/null
```

Check code for database references:

```bash
# Look for database connection strings or imports
grep -r "sqlite3\|psycopg2\|pymongo\|mysql" --include="*.py" . 2>/dev/null | head -5
grep -r "mongoose\|pg\|mysql" --include="*.js" . 2>/dev/null | head -5
```

### Presentation Phase

Present your findings:

```
I found the following database indicators:
- Database library: psycopg2 (PostgreSQL)
- Migration directory: ./alembic/
- Connection references found in: db.py, models.py
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED if database detected]** "I found references to [database system(s)]. Is this what the project uses?"
   - Confirm the database system.

2. **[REQUIRED if database confirmed]** "What are the testing database credentials?"
   - Ask for: username, password, host, database name, port
   - Note: "I need to document the TEST database credentials (not production)"

3. **[REQUIRED if database confirmed]** "Does the test database need to be created beforehand, or is it auto-created by the tests?"

4. **[CONDITIONAL]** "Are there database migration scripts? How do I run them?"
   - Only ask if migrations directory was detected OR if database requires schema setup.

5. **[OPTIONAL]** "Should tests use a real database or mocks/in-memory databases?"

---

## 6. Operating System and Platform

### Detection Phase

Detect OS:

```bash
# Get OS information
uname -a
cat /etc/os-release 2>/dev/null | grep "PRETTY_NAME"
```

Check for platform-specific requirements:

```bash
# Look for platform-specific documentation
ls README* INSTALL* 2>/dev/null

# Check for Docker
ls Dockerfile docker-compose.yml 2>/dev/null && echo "Docker detected"
```

### Presentation Phase

Present your findings:

```
System information:
- OS: Linux (Ubuntu 22.04)
- Kernel: 5.15.0-76-generic
- Docker: Detected (Dockerfile and docker-compose.yml present)
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "The system is running [OS]. Is this the standard development environment?"
   - Confirm this is the expected environment.

2. **[OPTIONAL]** "Are there platform-specific requirements or limitations I should document?"
   - Examples: "Windows requires WSL2", "macOS requires Xcode"

3. **[OPTIONAL]** "Do developers typically work on Linux, macOS, Windows, or a mix?"

4. **[CONDITIONAL]** "Is Docker or containerization used for development?"
   - Only ask if Docker files were detected and usage is unclear.

---

## 7. Project Structure and Conventions

### Detection Phase

Explore the directory structure:

```bash
# Get high-level directory structure
ls -d */ 2>/dev/null

# Look for common patterns
ls src/ lib/ app/ components/ services/ models/ 2>/dev/null
ls tests/ test/ __tests__/ 2>/dev/null
ls docs/ documentation/ 2>/dev/null
```

### Presentation Phase

Present your findings:

```
I found the following directory structure:
- Source code: ./src/
- Tests: ./tests/
- Documentation: ./docs/
- Services: ./src/services/
- Models: ./src/models/
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "What is the general structure of the codebase?"
   - Examples: monorepo, layered architecture, feature-based, microservices

2. **[REQUIRED]** "Where should new code typically go?"
   - Get guidance on where to place new files.

3. **[REQUIRED]** "Where are tests located relative to source files?"
   - Examples: "alongside source files", "in ./tests/ directory mirroring src/"

4. **[REQUIRED]** "Are there naming conventions for files?"
   - Examples: snake_case, kebab-case, PascalCase

5. **[OPTIONAL]** "Are there coding style guides or linters configured?"
   - Examples: ESLint, Pylint, Black, Prettier

---

## 8. Code Review and Pull Request Process

### Detection Phase

Check for PR templates:

```bash
# Look for PR/issue templates
ls .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
ls .gitlab/merge_request_templates/ 2>/dev/null
```

Check for CI/CD configuration:

```bash
# Look for CI configuration
ls .github/workflows/ .gitlab-ci.yml .circleci/ Jenkinsfile 2>/dev/null
```

### Presentation Phase

Present your findings:

```
Pull request infrastructure detected:
- Platform: GitHub (detected .github/ directory)
- PR template: .github/pull_request_template.md
- CI: GitHub Actions (3 workflow files found)
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "How are pull requests typically created?"
   - Examples: GitHub PR, GitLab MR, Bitbucket PR, other

2. **[REQUIRED]** "What branch should PRs target?"
   - Examples: main, master, develop

3. **[OPTIONAL]** "Are there required PR checks or CI tests that must pass?"

4. **[OPTIONAL]** "Should commits be squashed, or kept separate?"

5. **[OPTIONAL]** "Are there code review requirements?"
   - Examples: number of approvers, specific reviewers

6. **[CONDITIONAL]** "Is there a PR description template or format to follow?"
   - Only ask if no template file was detected.

---

## 9. Documentation Location and Format

### Detection Phase

Find documentation:

```bash
# Look for documentation directories and files
ls docs/ documentation/ README.md CONTRIBUTING.md 2>/dev/null
ls *.md 2>/dev/null

# Check for generated documentation
ls -d build/docs/ site/ public/ 2>/dev/null
```

### Presentation Phase

Present your findings:

```
Documentation found:
- README.md in project root
- Documentation directory: ./docs/
- Multiple .md files in root
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "Where should documentation be placed?"
   - Examples: ./docs/, inline comments, wiki, alongside code

2. **[REQUIRED]** "What format should documentation use?"
   - Examples: Markdown, ReStructuredText, JSDoc, Sphinx

3. **[OPTIONAL]** "Should code changes include documentation updates?"

4. **[OPTIONAL]** "Are there existing documentation standards or templates?"

---

## 10. Environment Variables and Configuration

### Detection Phase

Look for environment configuration:

```bash
# Check for environment files
ls .env .env.example .env.template config.json config.yml 2>/dev/null

# Look for configuration directories
ls -d config/ settings/ 2>/dev/null
```

### Presentation Phase

Present your findings:

```
Configuration detected:
- Environment file: .env.example (template found)
- Configuration directory: ./config/
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED]** "Are there environment variables that need to be set for development?"
   - If yes, ask what they are.

2. **[CONDITIONAL]** "Is there a `.env.example` file to copy for local setup?"
   - Only ask if .env files were detected but unclear.

3. **[OPTIONAL]** "Are there different configurations for development, testing, and production?"

4. **[OPTIONAL]** "What secrets or credentials should never be committed to version control?"

---

## 11. Continuous Integration and Deployment

### Detection Phase

Check CI/CD setup:

```bash
# Look for CI configuration files
ls .github/workflows/*.yml .gitlab-ci.yml .circleci/config.yml azure-pipelines.yml 2>/dev/null

# Check for deployment scripts
ls deploy/ scripts/ 2>/dev/null
find . -name "deploy.sh" -o -name "release.sh" 2>/dev/null
```

### Presentation Phase

Present your findings:

```
CI/CD infrastructure detected:
- CI system: GitHub Actions
- Workflow files: test.yml, lint.yml, deploy.yml
- Deployment scripts: ./scripts/deploy.sh
```

### Questioning Phase

Ask these questions ONE AT A TIME:

1. **[REQUIRED if CI detected]** "What CI/CD system is used?"
   - Confirm: GitHub Actions, GitLab CI, CircleCI, Jenkins, etc.

2. **[OPTIONAL]** "Are there automated tests that run on every commit/PR?"

3. **[OPTIONAL]** "How is the project deployed?"
   - Examples: manual, automated, on merge to main

4. **[OPTIONAL]** "Are there pre-commit hooks or git hooks configured?"

---

## 12. Generate the env.md File

Once you've gathered all the information above through systematic detection and questioning, create a file at `./tasks/env.md` using the template below.

**Important**: Fill in ALL sections based on the information you collected. Use "N/A" or "None" for sections that don't apply to the project.

```markdown
# Development Environment

**Generated:** [YYYY-MM-DD]
**Last Updated:** [YYYY-MM-DD]
**Git Commit:** [commit hash]
**Git Branch:** [branch name]

> This file documents the development environment for this project. It is used by AI assistants when exploring code or creating implementation plans. Keep this file updated when environment changes occur.

## Version Control

**System:** [Git/Mercurial/SVN]
**Primary Branch:** [main/master/develop]
**Remote Repository:** [URL if applicable]

**Branch Naming Conventions:**
[Describe branch naming patterns, e.g., feature/*, bugfix/*, hotfix/*]

**Commit Message Format:**
[Describe commit message conventions, e.g., Conventional Commits, include ticket numbers]

**Commands for Context Capture:**
```bash
# Get current commit and branch (use this in exploration/planning docs)
[command to get current commit and branch]
```

## Programming Languages

**Primary Language:** [Language name]
**Version:** [version number]
**Aliases:** [e.g., `py` is an alias for `python3`]

**Secondary Languages:** (if applicable)
- [Language]: [version]

**Style Guide:**
[Link to or describe coding standards, e.g., PEP 8, Airbnb JavaScript Style Guide]

**Linting/Formatting:**
[Tools used, e.g., ESLint, Pylint, Black, Prettier]

## Package Management

**Package Manager:** [npm/pip/cargo/bundler/etc.]

**Installing Dependencies:**
```bash
[command to install dependencies]
```

**Adding New Dependencies:**
```bash
[command to add a new package]
```

**Dependency Files:**
- [e.g., requirements.txt, package.json, Cargo.toml]

## Build System

**Build Tool:** [make/npm/cargo/maven/etc.]

**Building the Project:**
```bash
[command to build, or "N/A - interpreted language"]
```

**Build Configuration:**
[Location of build configs, or "N/A"]

## Testing

**Testing Framework:** [pytest/jest/unittest/mocha/etc.]

**Running All Tests:**
```bash
[command to run all tests]
```

**Running Specific Tests:**
```bash
[command to run a specific test file or test]
```

**Test File Naming Convention:**
[Pattern, e.g., *_test.py, *.test.js, *Test.java]

**Test File Locations:**
[Describe where tests are located relative to source, e.g., "alongside source files", "in ./tests/ directory"]

**Test Concurrency:**
[Can tests run in parallel? Any setup/teardown requirements?]

**Test Database:**
[If applicable, describe test database setup]

## Database

**Database System:** [SQLite/PostgreSQL/MySQL/MongoDB/None]
**Version:** [version number]

**Testing Credentials:**
```
Host: [hostname or "N/A"]
Port: [port or "N/A"]
Database: [database name]
Username: [username]
Password: [password]
```

**Connection String for Tests:**
```
[connection string format, if applicable]
```

**Running Migrations:**
```bash
[command to run database migrations, or "N/A"]
```

**Test Database Setup:**
[Describe if database needs to be created beforehand, or is auto-created]

## Operating System

**OS:** [Linux/macOS/Windows]
**Distribution:** [e.g., Ubuntu 22.04, macOS 13, Windows 11]
**Kernel/Version:** [version information]

**Platform-Specific Notes:**
[Any platform-specific requirements or limitations]

**Containerization:**
[Docker/Podman/None, and how to use if applicable]

## Project Structure

**Code Organization:**
[Describe directory structure, e.g., "Feature-based modules", "Layered architecture", etc.]

**Key Directories:**
- `[path]` - [description]
- `[path]` - [description]

**File Naming Conventions:**
- Source files: [convention, e.g., snake_case.py, kebab-case.js, PascalCase.java]
- Test files: [convention]
- Class files: [convention, e.g., PascalCase]

## Pull Request Process

**PR Tool:** [GitHub PR/GitLab MR/Bitbucket PR/etc.]

**Target Branch:** [branch name PRs should target]

**Creating a PR:**
```bash
[command to create PR, e.g., gh pr create, or "Use web UI"]
```

**PR Title Format:**
[Describe format, e.g., "[Type]: Brief description"]

**PR Description Template:**
[Describe required sections or point to template file]

**Required Checks:**
[List CI checks that must pass, e.g., "All tests", "Linting", "Code coverage"]

**Review Requirements:**
[Number of approvals needed, specific reviewers]

**Merge Strategy:**
[Squash/Merge commit/Rebase]

## Continuous Integration

**CI System:** [GitHub Actions/GitLab CI/CircleCI/Jenkins/None]

**Configuration File:** [path to CI config]

**Automated Tests:**
[Describe what tests run automatically on commit/PR]

**Pre-commit Hooks:**
[Describe any git hooks, or "None"]

## Environment Variables

**Configuration Files:**
- [e.g., .env, config.json, settings.py]

**Required Variables for Development:**
```bash
[List environment variables that need to be set]
```

**Setting Up Environment:**
```bash
[Commands to set up environment, e.g., "cp .env.example .env && edit .env"]
```

**Secrets Management:**
[How secrets are managed, what should never be committed]

## Documentation

**Documentation Location:** [./docs/, inline comments, wiki, etc.]

**Documentation Format:** [Markdown/ReStructuredText/JSDoc/etc.]

**Updating Documentation:**
[When and how to update docs]

**Generated Documentation:**
[If applicable, how to generate docs from code]

## Common Commands Reference

Quick reference for common development tasks:

```bash
# Clone repository
[git clone command or equivalent]

# Install dependencies
[install command]

# Run tests
[test command]

# Build project
[build command or "N/A"]

# Start development server (if applicable)
[dev server command or "N/A"]

# Run linter
[linting command or "N/A"]

# Format code
[formatting command or "N/A"]

# Create database migrations
[migration command or "N/A"]

# Run database migrations
[migration run command or "N/A"]
```

## Notes and Caveats

[Any additional notes, gotchas, or important information about the development environment]

## Updating This Document

This document should be updated when:
- Version control practices change
- Language versions or runtimes are upgraded
- Testing frameworks or practices change
- Database systems change
- New tools are added to the development workflow

To update this document, run through the discovery process in `./gen-env.md` again and regenerate this file with new information.
```

---

## 13. Confirm Completion

After creating the `./tasks/env.md` file, inform the user:

**"I've created the environment documentation at ./tasks/env.md. This file documents the development environment and will be used by AI assistants during code exploration and planning. Please review it for accuracy and let me know if any corrections are needed."**

---

## Quality Checks

Before completing the env.md file, verify:

**Completeness:**
- [ ] Version control system documented
- [ ] Language and runtime versions captured
- [ ] Package management documented
- [ ] Testing framework and practices documented
- [ ] Database system and credentials documented (if applicable)
- [ ] OS and platform information captured
- [ ] Project structure described
- [ ] PR process documented
- [ ] All required commands are included

**Accuracy:**
- [ ] All automated detections were confirmed with user through one-at-a-time questioning
- [ ] Commands are tested and work correctly
- [ ] Credentials are correct (for test environments only, never production)
- [ ] Version numbers are accurate
- [ ] File paths are correct

**Usability:**
- [ ] Commands are copy-paste ready
- [ ] Clear descriptions for each section
- [ ] Common Commands Reference is complete
- [ ] No ambiguity in instructions

---

## Important Notes

### When to Regenerate env.md

Regenerate or update when:
- Major dependencies are updated
- Database systems change
- CI/CD configuration changes
- Project structure is refactored
- Team development practices change
- Language versions are upgraded

### What NOT to Include in env.md

Never include:
- Production credentials or secrets
- Personal developer configurations
- Temporary experimental setups
- IDE-specific settings (unless standardized for the entire team)
- API keys or tokens

### Keeping env.md Updated

- Review quarterly or when significant changes occur
- Update the "Last Updated" date when changes are made
- Consider adding env.md validation to CI/CD to ensure it stays current
- Commit env.md to version control (it's project-specific, not personal)

### Tips for Effective Discovery

1. **Be patient**: The one-question-at-a-time approach takes longer but ensures accuracy
2. **Confirm assumptions**: Even when detection seems obvious, confirm with the user
3. **Document as you go**: Don't wait until the end to start filling in env.md
4. **Test commands**: When possible, verify that documented commands actually work
5. **Be thorough**: A complete env.md saves time for all future AI assistants
