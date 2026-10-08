---
name: python-fixer
description: Fix Python files uploaded by the user. Use this skill when the user uploads a .py file and asks to correct, debug, or improve it. This skill handles syntax errors, logical bugs, and code quality issues.
---

# Python File Fixer

When a user uploads a Python file and asks for corrections:

1. **Read the file**: Use the filesystem tools to read the uploaded `.py` file content completely before making any changes.

2. **Analyze thoroughly**: 
   - Check for syntax errors (missing colons, indentation, brackets)
   - Identify logical bugs (incorrect operators, missing return statements)
   - Look for common Python pitfalls (mutable default arguments, bare except clauses)

3. **Apply fixes**: Use the `edit_file` or `write_file` tool to correct the identified issues. Make minimal, targeted changes rather than rewriting the entire file.

4. **Verify**: After editing, read the file again to confirm the changes are correct and no new issues were introduced.

5. **Report**: Explain to the user what was wrong and what you changed.

The target Python file already exists in the workspace.
Always inspect the existing file before editing.
Modify the existing target file.
Never create a replacement file unless explicitly requested.

## Guidelines

- Always preserve the original code style (indentation, quotes) when possible.
- If a fix is ambiguous, ask the user for clarification before making destructive changes.
- For complex bugs, explain the root cause in your response.