# Commit → Push → PR Workflow

## The Correct Order (ALWAYS)

```
1. COMMIT in worktree
2. PUSH to origin  
3. CREATE PR
```

## Why This Order Matters

### ❌ WRONG: Creating PR First
```bash
# DON'T DO THIS
gh pr create --title "WIP: Working on feature"
# Now what? PR has no commits!
git commit -m "feat: Add feature"  # Too late!
```

### ✅ CORRECT: Commit First, PR Last
```bash
# 1. Do your work in worktree
cd ../project-codex
vim src/component.js

# 2. Commit your changes
git add src/
git commit -m "feat: Add new component"

# 3. Push commits to origin
git push origin agent-codex-feature

# 4. NOW create PR (with actual commits to review!)
gh pr create --title "feat: New component (#123)"
```

## Complete Agent Workflow

### Morning: Start Work
```bash
# 1. Go to your worktree
cd ../project-codex

# 2. Sync with main
git fetch origin main
git rebase origin/main

# 3. Check your tasks
gh issue list --assignee @me
```

### During Day: Work and Commit
```bash
# 4. Work on features
vim src/feature.js

# 5. Commit frequently (small commits are good!)
git add src/feature.js
git commit -m "feat: Add user authentication"

# More work...
vim tests/feature.test.js

# 6. Another commit
git add tests/
git commit -m "test: Add auth tests"

# 7. Push commits regularly (backup + visibility)
git push origin agent-codex-feature
```

### End of Day: Create PR
```bash
# 8. Final commit if needed
git add .
git commit -m "docs: Update API documentation"

# 9. Push final commits
git push origin agent-codex-feature

# 10. NOW create PR (has all commits!)
gh pr create \
  --title "feat: User authentication system (#123, #124)" \
  --body "## Summary
  Complete authentication implementation
  
  ## Commits Included
  - feat: Add user authentication
  - test: Add auth tests  
  - docs: Update API documentation
  
  ## Issues Resolved
  Closes #123
  Closes #124
  
  Ready for review @claude"
```

## Key Points

### Commits Come BEFORE PR
- **Commits** = Your actual work
- **PR** = Request to merge your commits
- Can't have PR without commits!

### Multiple Commits Are Fine
```bash
# Make many commits while working
git commit -m "feat: Start dashboard"
git commit -m "style: Add CSS"
git commit -m "test: Add tests"
git commit -m "fix: Handle edge case"

# Push them all
git push origin agent-branch

# PR includes ALL commits
gh pr create --title "feat: Complete dashboard"
```

### Push Frequently (Don't Wait)
```bash
# Good: Push after each commit (backup!)
git commit -m "feat: Add feature"
git push

# Also good: Push every few commits
git commit -m "feat: Part 1"
git commit -m "feat: Part 2"
git push

# Bad: Wait until end to push everything
# (Risk losing work if local machine crashes)
```

## Common Scenarios

### Scenario 1: Forgot to Push Before PR
```bash
gh pr create --title "My feature"
# ERROR: No commits on remote branch!

# Fix: Push first
git push origin agent-branch
# Now try PR again
gh pr create --title "My feature"
```

### Scenario 2: Need to Add More Commits to PR
```bash
# PR already exists
# Make new commits
git add .
git commit -m "fix: Address review feedback"

# Push new commits
git push origin agent-branch

# PR automatically updates with new commits!
```

### Scenario 3: Empty PR
```bash
# If you see this in GitHub:
"This PR has no commits"

# You created PR before pushing
# Fix: Push your commits
git push origin agent-branch
```

## Summary

**Remember: C → P → PR**
1. **C**ommit (your work)
2. **P**ush (to origin)
3. **P**ull **R**equest (to merge)

Never create empty PRs! Always have commits first!