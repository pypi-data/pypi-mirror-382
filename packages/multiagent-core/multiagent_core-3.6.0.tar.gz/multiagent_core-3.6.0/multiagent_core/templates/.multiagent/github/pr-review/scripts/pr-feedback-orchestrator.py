#!/usr/bin/env python3
"""
PR Feedback Orchestrator - Proper Implementation

This script orchestrates the complete workflow:
1. Uses bash scripts to extract and structure data
2. Uses Claude SDK to intelligently analyze the structured data
3. Uses templates to format the final output

Usage: python3 pr-feedback-orchestrator.py <session_directory>
"""

import asyncio
import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, ResultMessage, TextBlock

class PRFeedbackOrchestrator:
    """Orchestrates the complete PR feedback workflow using organized scripts + Claude SDK"""
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent
        
    async def orchestrate_feedback_processing(self):
        """Run the complete orchestrated workflow"""
        
        print(f"🎬 Orchestrating PR feedback processing for session: {self.session_dir.name}")
        
        # Step 1: Verify we have the basic GitHub data
        if not self._verify_github_data():
            print("❌ Required GitHub data not found")
            return False
            
        # Step 2: Run the structured analysis scripts
        print("\n🔍 Running structured data analysis...")
        analysis_data = await self._run_analysis_scripts()
        
        # Step 3: Use Claude SDK to intelligently process the analysis
        print("\n🤖 Running intelligent task generation with Claude SDK...")
        success = await self._generate_intelligent_tasks(analysis_data)
        
        return success
    
    def _verify_github_data(self) -> bool:
        """Verify that basic GitHub data exists"""
        required_files = ["pr-data.json", "pr-diff.txt"]
        
        for file in required_files:
            if not (self.session_dir / file).exists():
                print(f"❌ Missing required file: {file}")
                return False
                
        return True
    
    async def _run_analysis_scripts(self) -> dict:
        """Run the organized bash scripts to structure the data"""
        
        analysis_data = {}
        
        # Read the basic PR data
        with open(self.session_dir / "pr-data.json") as f:
            analysis_data["pr_data"] = json.load(f)
            
        with open(self.session_dir / "pr-diff.txt") as f:
            analysis_data["pr_diff"] = f.read()
            
        # Check for comments
        comments_file = self.session_dir / "pr-comments.json"
        if comments_file.exists():
            with open(comments_file) as f:
                comments_data = json.load(f)
                # Handle the nested structure from GitHub CLI
                if isinstance(comments_data, dict) and "comments" in comments_data:
                    analysis_data["pr_comments"] = comments_data["comments"]
                elif isinstance(comments_data, list):
                    analysis_data["pr_comments"] = comments_data
                else:
                    analysis_data["pr_comments"] = []
        else:
            analysis_data["pr_comments"] = []
            
        # Analyze diff statistics
        diff_lines = analysis_data["pr_diff"].split('\n')
        analysis_data["diff_stats"] = {
            "total_lines": len(diff_lines),
            "additions": len([l for l in diff_lines if l.startswith('+') and not l.startswith('+++')]),
            "deletions": len([l for l in diff_lines if l.startswith('-') and not l.startswith('---')]),
            "files_changed": len([l for l in diff_lines if l.startswith('diff --git')])
        }
        
        # Extract file types being changed
        file_extensions = set()
        for line in diff_lines:
            if line.startswith('diff --git'):
                # Extract file path and extension
                parts = line.split(' ')
                if len(parts) >= 4:
                    file_path = parts[3][2:]  # Remove 'b/' prefix
                    if '.' in file_path:
                        ext = file_path.split('.')[-1]
                        file_extensions.add(ext)
                        
        analysis_data["file_types"] = list(file_extensions)
        
        # Analyze PR metadata
        pr_data = analysis_data["pr_data"]
        analysis_data["pr_analysis"] = {
            "is_feature": "feat" in pr_data.get("title", "").lower() or "feature" in pr_data.get("title", "").lower(),
            "is_fix": "fix" in pr_data.get("title", "").lower() or "bug" in pr_data.get("title", "").lower(),
            "is_docs": "doc" in pr_data.get("title", "").lower() or any(ext in ["md", "txt", "rst"] for ext in file_extensions),
            "is_refactor": "refactor" in pr_data.get("title", "").lower(),
            "has_tests": any(ext in ["test.py", "spec.js", "test.js"] for ext in file_extensions) or "test" in analysis_data["pr_diff"].lower()
        }
        
        print(f"  📊 Files changed: {analysis_data['diff_stats']['files_changed']}")
        print(f"  📊 Lines +{analysis_data['diff_stats']['additions']} -{analysis_data['diff_stats']['deletions']}")
        print(f"  📊 File types: {', '.join(analysis_data['file_types']) if analysis_data['file_types'] else 'None detected'}")
        print(f"  📊 PR type: {self._get_pr_type(analysis_data['pr_analysis'])}")
        
        return analysis_data
    
    def _get_pr_type(self, pr_analysis: dict) -> str:
        """Determine the primary type of PR"""
        if pr_analysis["is_feature"]:
            return "Feature"
        elif pr_analysis["is_fix"]:
            return "Bug Fix"
        elif pr_analysis["is_docs"]:
            return "Documentation"
        elif pr_analysis["is_refactor"]:
            return "Refactoring"
        else:
            return "General"
    
    async def _generate_intelligent_tasks(self, analysis_data: dict) -> bool:
        """Use Claude SDK to generate intelligent tasks based on structured analysis"""
        
        pr_data = analysis_data["pr_data"]
        diff_stats = analysis_data["diff_stats"]
        pr_analysis = analysis_data["pr_analysis"]
        session_id = self.session_dir.name
        
        # Prepare comment preview
        comment_preview = "No comments"
        if analysis_data['pr_comments'] and len(analysis_data['pr_comments']) > 0:
            preview_comments = analysis_data['pr_comments'][:3]
            comment_preview = json.dumps(preview_comments, indent=2)
        
        # Create a comprehensive, structured prompt for Claude
        prompt = f"""
You are an expert code reviewer generating actionable tasks based on structured PR analysis.

## PR Overview
- **Number**: #{pr_data.get('number', 'N/A')}
- **Title**: {pr_data.get('title', 'N/A')}
- **Author**: {pr_data.get('author', {}).get('login', 'N/A')}
- **Type**: {self._get_pr_type(pr_analysis)}
- **Branch**: {pr_data.get('headRefName', 'N/A')} → {pr_data.get('baseRefName', 'N/A')}

## Change Analysis
- **Files Changed**: {diff_stats['files_changed']}
- **Lines Added**: {diff_stats['additions']}
- **Lines Removed**: {diff_stats['deletions']}
- **File Types**: {', '.join(analysis_data['file_types']) if analysis_data['file_types'] else 'Mixed'}
- **Has Tests**: {"Yes" if pr_analysis['has_tests'] else "No"}

## Code Changes Context
{analysis_data['pr_diff'][:3000]}...

## Review Comments
{len(analysis_data['pr_comments'])} comments found:
{comment_preview}

## Task Generation Instructions

Generate a comprehensive task list with this EXACT structure:

```markdown
# Feedback Tasks - Session {session_id}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**PR**: #{pr_data.get('number', 'N/A')}
**Title**: {pr_data.get('title', 'N/A')}
**Author**: {pr_data.get('author', {}).get('login', 'N/A')}
**Branch**: {pr_data.get('headRefName', 'N/A')} → {pr_data.get('baseRefName', 'N/A')}
**Session**: [{session_id}](.multiagent/feedback/logs/{session_id}/)

## Claude Code Review Summary

[Based on the analysis above, provide 3-5 specific insights about this PR:
- What type of change this is and its scope
- Key technical considerations based on file types and changes
- Quality observations based on diff analysis
- Any patterns or concerns that need attention]

## Action Items

### Priority 1: Immediate Actions
[Generate 3 specific tasks based on the PR type and changes. For example:
- If it's a feature: Focus on functionality, integration, edge cases
- If it's a bug fix: Focus on root cause, testing, regression prevention  
- If it's refactoring: Focus on behavior preservation, performance, maintainability
- Make tasks specific to the actual file types and changes shown]

- [ ] **T001** [Specific task based on actual changes]
- [ ] **T002** [Specific task based on actual changes]
- [ ] **T003** [Specific task based on actual changes]

### Priority 2: Code Quality
[Generate 3 tasks focused on code quality aspects relevant to this change]

- [ ] **T004** [Quality task relevant to the file types changed]
- [ ] **T005** [Testing task - especially important if no tests detected]
- [ ] **T006** [Documentation/standards task]

### Priority 3: Integration
[Generate 3 tasks focused on integration and deployment considerations]

- [ ] **T007** [Integration testing task]
- [ ] **T008** [Deployment verification task]
- [ ] **T009** [Follow-up monitoring task]

## Change Impact Analysis

### Technical Scope
- **Complexity**: [Low/Medium/High based on files changed and diff size]
- **Risk Level**: [Low/Medium/High based on change type and scope]
- **Testing Coverage**: [Assessment based on has_tests and change type]

### Recommendations
[2-3 specific recommendations based on the analysis]

## Session Details
- **Session ID**: {session_id}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Files Changed**: {diff_stats['files_changed']}
- **Lines Added**: {diff_stats['additions']}
- **Lines Removed**: {diff_stats['deletions']}
- **Change Type**: {self._get_pr_type(pr_analysis)}

---
*Generated by MultiAgent Core Feedback System with Structured Analysis*
```

Generate this task list with specific, actionable tasks based on the ACTUAL code changes and PR context provided.
"""

        try:
            options = ClaudeCodeOptions(
                permission_mode='bypassPermissions',
                max_turns=3,
                allowed_tools=['Write', 'Read'],
                cwd=str(self.project_root)
            )
            
            generated_content = ""
            
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock) and len(block.text.strip()) > 0:
                            # Capture the full content
                            generated_content += block.text
                            first_line = block.text.strip().split('\n')[0]
                            if len(first_line) > 100:
                                first_line = first_line[:100] + "..."
                            print(f"💬 Claude: {first_line}")
                            
                elif isinstance(message, ResultMessage):
                    print(f"✅ Task generation completed - Cost: ${message.total_cost_usd:.4f}")
                    if message.is_error:
                        print(f"❌ Error: {message.result}")
                        return False
            
            # Write the generated content to the tasks file
            tasks_file = self.session_dir / "generated-tasks.md"
            if generated_content.strip():
                with open(tasks_file, 'w') as f:
                    f.write(generated_content.strip())
                print(f"📝 Intelligent tasks file created: {tasks_file}")
                print(f"📏 Content length: {len(generated_content)} characters")
                return True
            else:
                print("❌ No content was generated by Claude")
                return False
                
        except Exception as e:
            print(f"❌ Error during intelligent task generation: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Main entry point"""
    
    if len(sys.argv) != 2:
        print("Usage: python3 pr-feedback-orchestrator.py <session_directory>")
        print("Example: python3 pr-feedback-orchestrator.py /path/to/.multiagent/feedback/logs/pr-8-20250926-155253")
        sys.exit(1)
    
    session_dir = Path(sys.argv[1])
    
    if not session_dir.exists():
        print(f"❌ Session directory does not exist: {session_dir}")
        sys.exit(1)
        
    if not session_dir.is_dir():
        print(f"❌ Path is not a directory: {session_dir}")
        sys.exit(1)
    
    orchestrator = PRFeedbackOrchestrator(session_dir)
    success = await orchestrator.orchestrate_feedback_processing()
    
    if success:
        print(f"\n🎉 Intelligent task generation completed successfully for {session_dir.name}!")
        print("\n🎯 The generated tasks are based on:")
        print("   ✅ Structured data analysis of the PR")
        print("   ✅ Intelligent interpretation by Claude")
        print("   ✅ Specific context from actual code changes")
        print("   ✅ Proper templates and formatting")
        sys.exit(0)
    else:
        print(f"\n❌ Task generation failed for {session_dir.name}!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())