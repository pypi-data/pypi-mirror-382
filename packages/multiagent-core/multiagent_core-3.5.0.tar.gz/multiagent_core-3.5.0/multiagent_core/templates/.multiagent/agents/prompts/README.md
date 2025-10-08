# AI Agent Startup Prompts

**Quick-start guidance prompts** to direct each AI agent to their proper documentation and workflow setup.

## Purpose

These prompts are **initial direction-setters** - they guide agents to:
1. 📖 Read their specific agent documentation files  
2. 🔍 Find their assigned tasks in specs
3. 🚀 Start the proper 6-phase worktree workflow
4. 🎯 Focus on their specialization area

## Usage

These prompts are designed for AI CLI startup in non-interactive mode:

```bash
# Claude - CTO-Level Technical Leader
claude -p "$(cat .multiagent/agents/prompts/claude-startup.txt)"

# Codex - Full-Stack Development (Frontend Focus)  
codex -p "$(cat .multiagent/agents/prompts/codex-startup.txt)"

# Copilot - Backend Implementation & APIs
copilot -p "$(cat .multiagent/agents/prompts/copilot-startup.txt)"

# Qwen - Performance Optimization & Algorithms
qwen -p "$(cat .multiagent/agents/prompts/qwen-startup.txt)"

# Gemini - Research, Documentation & Analysis
gemini -p "$(cat .multiagent/agents/prompts/gemini-startup.txt)"
```

## Updated Agent Roles

- **🔴 @claude** - CTO-Level Technical Leader & Strategic Guide (high complexity)
- **🟢 @codex** - Full-Stack Development Specialist with Frontend Expertise (medium-high)  
- **🔵 @copilot** - Backend Implementation & API Development Specialist (low-medium)
- **🟡 @qwen** - Performance Optimization & Algorithm Specialist (medium)
- **🟠 @gemini** - Research, Documentation & Large-Scale Analysis Specialist (research-intensive)

## Framework Structure

Each prompt follows this structure:
1. **Agent Identity** - Role and specialization  
2. **Essential Reading Order** - Specific files to read first
3. **Task Discovery** - How to find assigned work
4. **Workflow Start** - 6-phase process reference
5. **Specialization Focus** - What this agent excels at

## Key Updates

- ✅ **@codex is now full-stack** (not just frontend) with frontend expertise
- ✅ **Consistent framework structure** across all prompts
- ✅ **Proper file path references** to agent documentation
- ✅ **Clear reading order** for optimal onboarding
- ✅ **Color coding** for quick agent identification