# Claude Code Quickstart

> **Source**: https://docs.claude.com/en/docs/claude-code/quickstart
> **Last Updated**: 2025-09-29

## Prerequisites

Before you begin, ensure you have:
- Terminal or command prompt
- A code project
- Claude.ai or Claude Console account

## Installation

### Option 1: NPM Install (Node.js 18+)

```bash
npm install -g @anthropic-ai/claude-code
```

### Option 2: Native Install

**macOS / Linux / WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```cmd
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

## Getting Started

### Step 1: Install Claude Code
Use one of the installation methods above.

### Step 2: Log In
```bash
claude
# Or use the command:
/login
```

### Step 3: Start Interactive Session
Navigate to your project directory and start Claude Code:

```bash
cd your-project
claude
```

### Step 4: Ask Questions
Once in the interactive session, ask Claude about your project:

```
What does this codebase do?
How is authentication implemented?
Where are the API routes defined?
```

### Step 5: Make Code Changes
Request Claude to make changes:

```
Add input validation to the user registration endpoint
Refactor the database connection code to use connection pooling
Create a new API endpoint for user profile updates
```

### Step 6: Use Git Integration
Claude Code integrates with Git:

```
Create a commit with these changes
Show me the diff of what changed
Create a new branch for this feature
```

### Step 7: Fix Bugs or Add Features
Use Claude to debug issues or implement features:

```
Fix the authentication error in login.ts
Add password reset functionality
Optimize the database queries in the user service
```

## Essential Commands

### Interactive Mode
- `claude` - Start interactive session
- `claude "task"` - Run a one-time task
- `claude -p "query"` - Run query and exit

### In-Session Commands
- `/clear` - Clear conversation history
- `/help` - Show available commands
- `/exit` - Exit the session
- `/login` - Authenticate with Claude

## Pro Tips

### Be Specific with Requests
Instead of: "Fix the bug"
Try: "Fix the null pointer error in the user authentication flow at line 45 of auth.ts"

### Break Complex Tasks into Steps
For large features, break them down:
```
1. First, create the database schema
2. Then implement the API endpoints
3. Finally, add the frontend components
```

### Use Tab for Command Completion
Press Tab to autocomplete commands and file paths.

### Press ↑ for Command History
Use the up arrow to recall previous commands.

## Next Steps

- [Common Workflows](common-workflows.md) - Learn typical development patterns
- [Troubleshooting](troubleshooting.md) - Solve common issues
- [IDE Integrations](ide-integrations.md) - Set up your IDE
- [Security](security.md) - Security best practices

---

*This is a local mirror of Claude Code documentation. For the latest version, visit [docs.claude.com](https://docs.claude.com/en/docs/claude-code/quickstart)*