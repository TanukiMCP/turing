# TuringMCP Usage Guide for LLM Agents

## ⚠️ CRITICAL: The Session-Based Workflow ⚠️

**TuringMCP is a PLANNING-ONLY system that requires a strict, session-based workflow. You MUST follow this sequence for every task.**

### The Mandatory 3-Step Session Workflow

1.  **🚀 START**: Call `initialize_session` to begin a new task.
    -   This creates a clean, isolated world model for your task.
    -   You will receive a unique `session_id`.

2.  **🤔 PLAN → EXECUTE → FEEDBACK (Loop)**:
    -   **PLAN**: Use planning tools (`plan_read_at_head`, etc.) to get a JSON action plan.
    -   **EXECUTE**: Use **your own tools** (`edit_file`, `run_terminal_cmd`, etc.) to perform the action.
    -   **FEEDBACK**: Call `update_world_model` immediately after execution to report the outcome.

3.  **🏁 END**: Call `archive_session` to complete the task.
    -   This saves the final world model and clears the server memory.
    -   Failure to do this will result in a cluttered state and poor performance.

**Any deviation from this workflow will cause errors.** You cannot call a planning tool before initializing a session, and you must clean up with `archive_session`.

---

## Tool Categories

### 1. Session Management Tools (MUST USE)

These tools control the lifecycle of a cognitive task.

#### `initialize_session()`
-   **Purpose**: To start a new task. MUST be the first call.
-   **Returns**: A confirmation with a new `session_id`.

#### `archive_session()`
-   **Purpose**: To end a task. MUST be the last call.
-   **Returns**: The final archived world model.

### 2. In-Session Planning Tools (Use inside a session)

These tools generate plans. They DO NOT execute actions.

-   `plan_read_at_head(path: str)`
-   `plan_write_at_head(path: str, content: str)`
-   `plan_move_head(new_path: str)`
-   `plan_execute_at_head(command: str)`

### 3. Feedback and Query Tools (Use inside a session)

-   `update_world_model(action_result: dict)`: **CRITICAL** for reporting execution results.
-   `get_world_model_state()`: To check what the planner currently "knows."

---

## Complete Example: Full Session Lifecycle

This example shows the mandatory start-to-finish workflow.

```python
# Step 1: 🚀 Initialize the Session
# This MUST be the very first action for any new task.
session_info = mcp_turingmcp_initialize_session()
print(f"Started session: {session_info['session_id']}")

# Step 2: Begin the Plan -> Execute -> Feedback Loop
# --- Action 1: Read a config file ---

# 2a. PLAN: Get a plan to read the file.
read_plan = mcp_turingmcp_plan_read_at_head(path="config.json")

# 2b. EXECUTE: Use your own tool to perform the read.
# The 'read_file' tool is YOURS, not TuringMCP's.
file_content = read_file(target_file="config.json")

# 2c. FEEDBACK: Report the result immediately.
update_result = mcp_turingmcp_update_world_model(action_result={
  "tool": "read",
  "status": "success",
  "path": "config.json",
  "size": len(file_content)
})

# --- Action 2: Write a new file based on the config ---

# 2a. PLAN: Get a plan to write the new file.
write_plan = mcp_turingmcp_plan_write_at_head(
  path="output.txt",
  content=f"Processed from {file_content}"
)

# 2b. EXECUTE: Use your own tool to perform the write.
edit_file(
  target_file="output.txt",
  code_edit=f"Processed from {file_content}"
)

# 2c. FEEDBACK: Report the result immediately.
update_result_2 = mcp_turingmcp_update_world_model(action_result={
  "tool": "write",
  "status": "success",
  "path": "output.txt"
})

# Step 3: 🏁 Archive the Session
# This MUST be the very last action for the task.
archive_info = mcp_turingmcp_archive_session()
print(f"Session archived: {archive_info['session_id']}")
# The world model is now cleared and ready for a new session.
```

---

## Key Reminders

-   **SESSION IS MANDATORY**: Always wrap your tasks in `initialize_session` and `archive_session`.
-   **PLANNING ≠ EXECUTION**: TuringMCP tools only generate plans.
-   **YOU MUST EXECUTE**: Use your own tools to perform actions.
-   **REPORT IMMEDIATELY**: Call `update_world_model` right after each action.
-   **CHECK STATE**: Use `get_world_model_state` to debug or see what the planner knows.

By following this session-based workflow, you ensure that the cognitive planner has a clean, predictable state for every task, leading to more reliable and accurate planning. 