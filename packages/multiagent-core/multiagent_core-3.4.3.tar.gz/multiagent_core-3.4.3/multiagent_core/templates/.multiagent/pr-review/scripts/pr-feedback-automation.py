#!/usr/bin/env python3
"""
Complete PR Feedback Automation using Claude Code Python SDK

This script implements the full workflow:
1. Uses Python SDK to execute slash commands that work properly
2. Generates actionable task files following codex's format
3. Integrates with existing GitHub data fetching scripts
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions
from claude_code_sdk.types import AssistantMessage, SystemMessage, ResultMessage, TextBlock, ToolUseBlock, ToolResultBlock

class PRFeedbackAutomation:
    """Complete PR feedback automation using Claude Code SDK"""
    
    def __init__(self, pr_number: str):
        self.pr_number = pr_number
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent
        self.logs_dir = self.project_root / ".multiagent" / "feedback" / "logs"
        
    async def process_pr_feedback(self):
        """Execute the complete PR feedback workflow using SDK"""
        
        print(f"🤖 Processing PR #{self.pr_number} feedback using Claude Code SDK...")
        
        # Step 1: Find session directory
        session_dir = self.find_latest_session()
        if not session_dir:
            print(f"❌ No session directory found for PR #{self.pr_number}")
            return False
            
        print(f"📁 Found session directory: {session_dir.name}")
        
        # Step 2: Use SDK with proper slash command execution
        try:
            # Configure SDK options for automation
            options = ClaudeCodeOptions(
                permission_mode='bypassPermissions',  # Allow all tools for automation
                max_turns=5,  # Allow multiple turns to complete the task
                allowed_tools=['Bash', 'Read', 'Write', 'Glob', 'TodoWrite'],
                cwd=str(self.project_root)  # Set working directory
            )
            
            # Use the slash command that we know works
            prompt = f"/process-pr-feedback {self.pr_number}"
            
            print(f"🔄 Executing Claude SDK query: {prompt}")
            
            # Execute the query and collect results
            total_cost = 0
            messages = []
            
            async for message in query(prompt=prompt, options=options):
                messages.append(message)
                
                if isinstance(message, SystemMessage):
                    if hasattr(message, 'session_id'):
                        print(f"📋 Session ID: {message.session_id}")
                        
                elif isinstance(message, AssistantMessage):
                    # Print tool usage for debugging
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            print(f"🔧 Tool used: {block.name}")
                        elif isinstance(block, TextBlock) and len(block.text.strip()) > 0:
                            # Print first line of significant text blocks
                            first_line = block.text.strip().split('\n')[0]
                            if len(first_line) > 100:
                                first_line = first_line[:100] + "..."
                            print(f"💬 Claude: {first_line}")
                            
                elif isinstance(message, ResultMessage):
                    total_cost = message.total_cost_usd
                    success = not message.is_error
                    print(f"✅ Query completed - Cost: ${total_cost:.4f}, Success: {success}")
                    
                    if message.is_error:
                        print(f"❌ Error: {message.result}")
                        return False
            
            # Step 3: Verify the generated-tasks.md file was created
            tasks_file = session_dir / "generated-tasks.md"
            if tasks_file.exists():
                print(f"📝 Generated tasks file: {tasks_file}")
                
                # Show preview of the file
                with open(tasks_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    preview_lines = lines[:10]
                    print("\n📋 Tasks file preview:")
                    for line in preview_lines:
                        print(f"   {line}")
                    if len(lines) > 10:
                        print(f"   ... ({len(lines) - 10} more lines)")
                        
                return True
            else:
                print("❌ Generated tasks file not found")
                
                # Try to find any new files in the session directory
                print("\n🔍 Files in session directory:")
                for file in session_dir.iterdir():
                    if file.is_file():
                        print(f"   - {file.name}")
                        
                return False
                
        except Exception as e:
            print(f"❌ Error during SDK execution: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def find_latest_session(self) -> Path | None:
        """Find the most recent session directory for the PR"""
        
        if not self.logs_dir.exists():
            return None
            
        # Look for directories matching pattern pr-{number}-*
        pattern = f"pr-{self.pr_number}-*"
        matching_dirs = list(self.logs_dir.glob(pattern))
        
        if not matching_dirs:
            return None
            
        # Return the most recent one (sorted by name which includes timestamp)
        return sorted(matching_dirs)[-1]

async def main():
    """Main entry point for PR feedback automation"""
    
    if len(sys.argv) != 2:
        print("Usage: python3 pr-feedback-automation.py <PR_NUMBER>")
        print("Example: python3 pr-feedback-automation.py 8")
        sys.exit(1)
    
    pr_number = sys.argv[1]
    
    automation = PRFeedbackAutomation(pr_number)
    success = await automation.process_pr_feedback()
    
    if success:
        print(f"\n🎉 PR #{pr_number} feedback processing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ PR #{pr_number} feedback processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())