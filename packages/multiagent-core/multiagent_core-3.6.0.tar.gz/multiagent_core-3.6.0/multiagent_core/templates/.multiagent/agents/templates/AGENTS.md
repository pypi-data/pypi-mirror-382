# Agent Development Instructions

## 🔄 AGENT WORKFLOW: Phase-by-Phase Operation

### Phase 1: Setup & Context Reading
1. **Read your specific agent MD file** - Open and study your agent file (CLAUDE.md, QWEN.md, GEMINI.md, etc.)
2. **Read this general agent file completely** - Understand overall workflow and coordination patterns
3. **Study worktree documentation** - Review Git Worktree Management protocols
4. **Read referenced documentation** - Study the workflow guides:
   - Git Worktree Guide (.multiagent/agents/docs/GIT_WORKTREE_GUIDE.md)
   - Agent Branch Protocol (.multiagent/agents/docs/AGENT_BRANCH_PROTOCOL.md) 
   - Agent Coordination Guide (.multiagent/agents/docs/AGENT_COORDINATION_GUIDE.md)
   - Commit PR Workflow (.multiagent/agents/docs/COMMIT_PR_WORKFLOW.md)
5. **Check current assignments** - `grep "@[your-agent]" specs/*/tasks.md`
6. **Configure safe git behavior** - Run mandatory configs to prevent rebases:
   ```bash
   git config --local pull.rebase false
   git config --local pull.ff only
   ```

### Phase 2: Worktree Setup & Environment Preparation  
7. **Verify current branch and location** - `git branch --show-current` (should be main)
8. **Find your pre-created worktree** - Worktrees are created by automation:
   ```bash
   git worktree list  # List all available worktrees
   # Look for: ../project-[name] with branch agent-[name]-*
   cd ../project-[name]
   ```
9. **Verify worktree setup** - `git branch --show-current` (should show agent-[name]-* branch)
10. **Sync with latest main** - `git fetch origin main && git merge origin/main`

   **Note**: If no worktree exists, it means automation hasn't been run yet. Ask user to run:
   ```bash
   .multiagent/iterate/scripts/setup-spec-worktrees.sh <spec-number>
   ```

### Phase 3: Task Discovery & Planning
12. **Find your tasks** - `grep "@[your-agent]" specs/*/tasks.md` 
    ```markdown
    # Example tasks.md showing YOUR tasks:
    - [ ] T015 @[your-agent] Create responsive dashboard component
    - [ ] T045 @[your-agent] Implement user login form
    - [ ] T055 @[your-agent] Add responsive navigation menu
    ```
13. **Use TodoWrite tool** - Track your tasks internally: 
    ```json
    [
      {"content": "Create responsive dashboard component (T015)", "status": "pending", "activeForm": "Creating responsive dashboard component"},
      {"content": "Implement user login form (T045)", "status": "pending", "activeForm": "Implementing user login form"}, 
      {"content": "Add responsive navigation menu (T055)", "status": "pending", "activeForm": "Adding responsive navigation menu"}
    ]
    ```
14. **Analyze task dependencies** - Check if tasks depend on other agents' work
15. **Review existing folder structure** - MANDATORY before coding:
    ```bash
    find . -name "test*" -type d  # See existing test directories
    ls -la tests/                 # Review test organization
    ls -la src/ backend/ frontend/ # Check main code structure
    ```
16. **Plan implementation approach** - Consider architecture, patterns, and integration points

### Phase 4: Implementation & Development Work
17. **Start first task** - Mark `in_progress` in TodoWrite, then implement
18. **🔒 SECURITY - API Keys & Secrets**:
    - **NEVER** hard-code API keys, tokens, or secrets in ANY file
    - **ONLY** place secrets in `.env` file (which is gitignored)
    - Use environment variables: `process.env.API_KEY` or `os.getenv('API_KEY')`
    - Add `.env.example` with placeholder values for documentation
    - If you see hardcoded secrets, move them to `.env` immediately
19. **Make regular work commits** - Use normal commit format (NO @claude, NO @agent tags):
    ```bash
    git commit -m "[WORKING] feat: Implement component

    Working on feature implementation"
    ```
20. **Complete tasks with dual tracking** - Update BOTH places:
    - **Internal**: TodoWrite `{"status": "completed"}`
    - **External**: tasks.md `- [x] T015 @agent Create component ✅`
21. **Basic smoke test** - Verify implementation works locally
22. **DO NOT create scattered test files** - Use existing `/tests/` structure, don't create new test folders
23. **Let GitHub Actions handle quality** - Automated lint/typecheck/integration tests run on PR

### Phase 5: PR Creation & Review Integration
23. **Complete final implementation** - Ensure all assigned work is done
24. **Final TodoWrite cleanup** - Mark all internal tasks as completed
25. **Make final commit with @claude tag** - ONLY for final PR commit (triggers review):
    ```bash
    git commit -m "[COMPLETE] feat: Implementation complete @claude

    All tasks completed and ready for automated review."
    ```
    **IMPORTANT**: @claude tag is ONLY used in the final commit before PR creation
26. **Push and create PR** - `git push origin agent-[name]-[feature] && gh pr create`
27. **Review system handles feedback routing** - Claude reviews and routes feedback automatically

### Phase 6: Post-Merge Cleanup - MANDATORY
28. **After PR is merged** - Clean up your worktree immediately:
    ```bash
    # Go to main project directory (not your worktree!)
    cd /home/vanman2025/Projects/multiagent-core
    
    # Update main branch
    git checkout main && git pull origin main
    
    # Remove your worktree (MANDATORY!)
    git worktree remove ../project-[name]
    
    # Clean up branch
    git branch -d agent-[name]-[feature]
    ```

---

## Git Worktree Management

**CRITICAL**: Each agent works in isolated worktrees for parallel development without conflicts.

### Worktree Setup

**Worktrees are pre-created by automation** - You should find and use existing worktrees:

```bash
# List available worktrees
git worktree list

# Look for your worktree: ../project-[name]
cd ../project-[name]
git branch --show-current  # Verify: agent-[name]-*
```

**If no worktree exists**, automation hasn't been run. The user needs to run:
```bash
.multiagent/iterate/scripts/setup-spec-worktrees.sh <spec-number>
```

This creates worktrees for all agents automatically with proper structure and symlinks.

### Daily Sync & Commit
```bash
# Configure safe git behavior
git config --local pull.rebase false
git config --local pull.ff only

# Sync with main (NO REBASE - causes data loss)
git fetch origin main && git merge origin/main

# Regular work commits (NO @agent tags during work)
git commit -m "[WORKING] feat: Updates and improvements"
```

### PR Workflow: Commit → Push → PR
```bash
# Final commit with @claude tag ONLY (triggers PR review)
git commit -m "[COMPLETE] feat: Implementation complete @claude"
git push origin agent-[name]-[feature]
gh pr create --title "feat: Updates from @[agent]"
```

**Note**: The `@agent` tag in final commits is for:
- Git history attribution (shows which agent did the work)
- Tracking agent contributions
- **NOT for automated routing** - coordination is manual

## Agent Specializations

**Quick Reference & Direction-Following Capabilities:**
- **@claude**: CTO-level architecture, integration, security, strategic decisions ⭐ **Excellent at following directions**
- **@codex**: Full-stack development, React, UI/UX, interactive development ⭐ **Excellent at following directions**
- **@qwen**: Performance optimization, algorithms, efficiency improvements ⭐ **Excellent at following directions**
- **@copilot**: Backend implementation, API development, database operations ⭐ **Good at following directions**
- **@gemini**: Research, documentation, simple analysis ⚠️ **Use for simple tasks only**

### Permission Settings - AUTONOMOUS OPERATION

#### ✅ ALLOWED WITHOUT APPROVAL (Autonomous)
- **Reading files**: Read any file in the project
- **Editing files**: Edit, modify, update existing files
- **Creating new files**: Create new code, tests, documentation
- **Running commands**: Execute build, test, lint commands
- **Git operations**: Commit, branch, pull, status checks
- **Testing**: Run tests and validate functionality
- **Debugging**: Analyze logs, trace errors
- **Refactoring**: Improve code structure and organization

#### 🛑 REQUIRES APPROVAL (Ask First)
- **Deleting files**: Any file deletion needs explicit approval
- **Overwriting files**: Complete file replacement needs approval
- **Force operations**: Any `--force` flags or overwrites
- **System changes**: Modifying system files or global configs
- **Production deploys**: Any production deployment
- **Breaking changes**: Major API or interface changes

#### Operating Principle
**"Edit freely, delete carefully"** - Make all the changes needed to improve code, but always ask before removing or completely replacing anything.

### Commit Format
```bash
git commit -m "[WORKING] feat: Feature description

Related to #123

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: @qwen <noreply@anthropic.com>
Co-Authored-By: @gemini <noreply@anthropic.com>  
Co-Authored-By: @codex <noreply@anthropic.com>
Co-Authored-By: @copilot <noreply@anthropic.com>"
```

### Documentation References
For detailed information on worktree workflows, see:
- [Git Worktree Guide](.multiagent/agents/docs/GIT_WORKTREE_GUIDE.md)
- [Agent Branch Protocol](.multiagent/agents/docs/AGENT_BRANCH_PROTOCOL.md)
- [Agent Coordination Guide](.multiagent/agents/docs/AGENT_COORDINATION_GUIDE.md)
- [Commit PR Workflow](.multiagent/agents/docs/COMMIT_PR_WORKFLOW.md)

## Screenshot Handling (WSL)

When users provide screenshots in WSL environments, always use the correct path format:
```bash
# Correct WSL paths for reading screenshots
/mnt/c/Users/[username]/Pictures/Screenshots/[filename].png
/mnt/c/Users/[username]/Desktop/[filename].png
/mnt/c/Users/[username]/Downloads/[filename].png

# Example usage with Read tool:
Read: /mnt/c/Users/user/Pictures/Screenshots/Screenshot 2025-09-22.png
```

**Important**: Never use Windows-style paths (C:\Users\...) when working in WSL.