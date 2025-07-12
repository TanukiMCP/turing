"""
TuringMCP - A Cognitive Planning Engine for MCP

⚠️ CRITICAL: This server ONLY generates plans, it does NOT execute actions! ⚠️

This server acts as a "cognitive head" that maintains an internal world model
and generates action plans for clients to execute. It separates the "thinking"
from the "doing" in AI agent architectures.

WORKFLOW:
1. Client calls planning tools (plan_read_at_head, plan_write_at_head, etc.)
2. Server returns JSON action plans with reasoning
3. Client executes plans using their own tools (edit_file, read_file, etc.)
4. Client reports execution results back using update_world_model
5. Server updates its world model based on results

Core Philosophy:
- Server maintains internal state and world model
- Server generates JSON action plans (PLANNING ONLY)
- Client (executor) performs the actual actions (EXECUTION ONLY)
- Feedback loop updates the server's world model
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from fastmcp import FastMCP, Context
from datetime import datetime
import uuid

# Global world model state - persists across calls
_world_model = None

@dataclass
class WorldModel:
    """Internal representation of the client's environment - The 'Tape' of our cognitive Turing machine"""
    session_id: str
    start_time: str
    current_working_directory: str
    file_system: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    operation_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def update_cwd(self, new_path: str) -> None:
        """Update the internal current working directory"""
        old_cwd = self.current_working_directory
        self.current_working_directory = new_path
        self.operation_history.append({
            "operation": "cwd_change",
            "from": old_cwd,
            "to": new_path,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_file(self, file_path: str, file_info: Dict[str, Any]) -> None:
        """Add file information to the world model"""
        self.file_system[file_path] = file_info
        self.operation_history.append({
            "operation": "file_tracked",
            "path": file_path,
            "info": file_info,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def remove_file(self, file_path: str) -> None:
        """Remove file from the world model"""
        if file_path in self.file_system:
            del self.file_system[file_path]
            self.operation_history.append({
                "operation": "file_removed",
                "path": file_path,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information from the world model"""
        return self.file_system.get(file_path)
    
    def add_operation(self, operation_type: str, details: Dict[str, Any]) -> None:
        """Add an operation to the history tape"""
        self.operation_history.append({
            "operation": operation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_tape_summary(self) -> Dict[str, Any]:
        """Get a summary of the cognitive tape state"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "current_working_directory": self.current_working_directory,
            "files_tracked": len(self.file_system),
            "operations_performed": len(self.operation_history),
            "last_5_operations": self.operation_history[-5:] if self.operation_history else [],
            "file_paths": list(self.file_system.keys())
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world model to dictionary"""
        return asdict(self)

def get_world_model() -> WorldModel:
    """
    Get the current world model instance.
    Throws an error if the session is not initialized.
    """
    global _world_model
    if _world_model is None:
        raise Exception("SESSION NOT INITIALIZED: You must call 'initialize_session' before any other operation.")
    return _world_model

# Initialize the FastMCP server
mcp = FastMCP(
    name="TuringMCP - Cognitive Planner",
    instructions="""
    🧠 COGNITIVE PLANNING ENGINE - I THINK, YOU DO 🧠
    
    CRITICAL: I am a PLANNING-ONLY system. I DO NOT execute actions.
    
    SESSION WORKFLOW:
    1. START: Call `initialize_session` to begin a new task.
    2. PLAN: Generate JSON action plans (e.g., `plan_read_at_head`, `plan_write_at_head`).
    3. EXECUTE: You execute those plans using your own tools (`edit_file`, `run_terminal_cmd`, etc.).
    4. FEEDBACK: Report results back using `update_world_model`.
    5. END: Call `archive_session` to complete the task and clear the world model.
    
    YOUR ROLE AS CLIENT:
    - You MUST start every task with `initialize_session()`.
    - You MUST end every task with `archive_session`.
    - You execute plans and report results.
    
    Architecture: Brain (Me) ↔ Hands (You)
    """
)

@mcp.tool
async def initialize_session(ctx: Context) -> Dict[str, Any]:
    """
    🚀 STARTING TOOL - Initializes a new cognitive planning session.
    
    This tool MUST be called before any other operation. It creates a new, clean
    world model for the current task and returns a unique session ID.
    
    Returns:
        A dictionary confirming session initialization and providing the new session ID.
    """
    global _world_model
    session_id = str(uuid.uuid4())
    start_time = datetime.utcnow().isoformat()
    
    # Use current directory as default since Cursor handles CWD internally
    working_directory = "."
    
    _world_model = WorldModel(
        session_id=session_id, 
        start_time=start_time,
        current_working_directory=working_directory
    )
    
    await ctx.info(f"New session initialized: {session_id}")
    await ctx.info(f"Working directory: {working_directory}")
    
    return {
        "status": "session_initialized",
        "session_id": session_id,
        "start_time": start_time,
        "message": "Cognitive planning session started. You may now proceed with planning tools."
    }

@mcp.tool
async def archive_session(ctx: Context) -> Dict[str, Any]:
    """
    🏁 ENDING TOOL - Archives the session and clears the world model.
    
    This tool MUST be called at the end of a task. It archives the final state of
    the world model and prepares the server for a new session.
    
    Returns:
        A dictionary containing the final archived world model and a confirmation message.
    """
    global _world_model
    world_model = get_world_model()
    
    archive_data = world_model.to_dict()
    archive_data["end_time"] = datetime.utcnow().isoformat()
    
    session_id = world_model.session_id
    
    # Clear the world model for the next session
    _world_model = None
    
    await ctx.info(f"Session archived and cleared: {session_id}")
    
    return {
        "status": "session_archived",
        "session_id": session_id,
        "archive": archive_data,
        "message": "Session complete. The world model has been cleared."
    }

@mcp.tool
async def plan_read_at_head(path: str, ctx: Context) -> Dict[str, Any]:
    """
    ⚠️ PLANNING TOOL - DOES NOT EXECUTE ACTIONS ⚠️
    
    This tool ONLY generates a JSON action plan for reading a file. It does NOT actually read the file.
    
    WORKFLOW:
    1. Call this tool to get a reading plan.
    2. Use the returned plan to execute the actual read using tools like `read_file`, `list_dir`, etc.
    3. Report the execution results back using `update_world_model`.
    
    Args:
        path: The file or directory path to read
        
    Returns:
        A JSON action plan that you must execute separately with other tools.
    """
    await ctx.info(f"Planning to read: {path}")
    
    world_model = get_world_model()
    
    # Convert relative path to absolute if needed using pathlib for cross-platform compatibility
    if not os.path.isabs(path):
        full_path = str(Path(world_model.current_working_directory) / path)
    else:
        full_path = str(Path(path))
    
    action_plan = {
        "action_plan": {
            "tool": "read",
            "path": full_path
        },
        "reasoning": f"I need to read the contents of '{path}' to understand what it contains and update my world model accordingly."
    }
    
    await ctx.debug(f"Generated read plan: {json.dumps(action_plan, indent=2)}")
    return action_plan

@mcp.tool
async def plan_write_at_head(path: str, content: str, ctx: Context) -> Dict[str, Any]:
    """
    ⚠️ PLANNING TOOL - DOES NOT EXECUTE ACTIONS ⚠️
    
    This tool ONLY generates a JSON action plan for writing to a file. It does NOT actually write the file.
    
    WORKFLOW:
    1. Call this tool to get a writing plan.
    2. Use the returned plan to execute the actual write using tools like `edit_file`, `search_replace`, etc.
    3. Report the execution results back using `update_world_model`.
    
    Args:
        path: The file path to write to
        content: The content to write to the file
        
    Returns:
        A JSON action plan that you must execute separately with other tools.
    """
    await ctx.info(f"Planning to write to: {path}")
    
    world_model = get_world_model()
    
    # Convert relative path to absolute if needed using pathlib for cross-platform compatibility
    if not os.path.isabs(path):
        full_path = str(Path(world_model.current_working_directory) / path)
    else:
        full_path = str(Path(path))
    
    action_plan = {
        "action_plan": {
            "tool": "write",
            "path": full_path,
            "content": content
        },
        "reasoning": f"I need to write the specified content to '{path}' to create or update this file as part of achieving the current goal."
    }
    
    await ctx.debug(f"Generated write plan for {len(content)} characters")
    return action_plan

@mcp.tool
async def plan_move_head(new_path: str, ctx: Context) -> Dict[str, Any]:
    """
    ⚠️ PLANNING TOOL - DOES NOT EXECUTE ACTIONS ⚠️
    
    This tool ONLY generates a JSON action plan for changing directories. It does NOT actually change directories.
    Note: This tool updates the server's internal CWD state for planning purposes.
    
    WORKFLOW:
    1. Call this tool to get a directory change plan.
    2. Use the returned plan to execute the actual directory change using tools like `run_terminal_cmd`.
    3. Report the execution results back using `update_world_model`.
    
    Args:
        new_path: The new directory path to move to
        
    Returns:
        A JSON action plan that you must execute separately with other tools.
    """
    await ctx.info(f"Planning to move to: {new_path}")
    
    world_model = get_world_model()
    old_cwd = world_model.current_working_directory
    
    # Convert relative path to absolute if needed using pathlib for cross-platform compatibility
    if not os.path.isabs(new_path):
        full_path = str(Path(world_model.current_working_directory) / new_path)
    else:
        full_path = str(Path(new_path))
    
    # Update the internal world model CWD BEFORE generating the plan
    world_model.update_cwd(full_path)
    
    action_plan = {
        "action_plan": {
            "tool": "change_directory",
            "path": full_path
        },
        "reasoning": f"I need to change my focus from '{old_cwd}' to '{full_path}' because my next actions will concern files and operations in this directory."
    }
    
    await ctx.debug(f"Updated internal CWD: {old_cwd} -> {full_path}")
    return action_plan

@mcp.tool
async def plan_execute_at_head(command: str, ctx: Context) -> Dict[str, Any]:
    """
    ⚠️ PLANNING TOOL - DOES NOT EXECUTE ACTIONS ⚠️
    
    This tool ONLY generates a JSON action plan for executing shell commands. It does NOT actually execute commands.
    
    WORKFLOW:
    1. Call this tool to get a command execution plan.
    2. Use the returned plan to execute the actual command using tools like `run_terminal_cmd`.
    3. Report the execution results back using `update_world_model`.
    
    Args:
        command: The shell command to execute
        
    Returns:
        A JSON action plan that you must execute separately with other tools.
    """
    await ctx.info(f"Planning to execute: {command}")
    
    world_model = get_world_model()
    
    action_plan = {
        "action_plan": {
            "tool": "execute_shell",
            "command": command
        },
        "reasoning": f"I need to execute the shell command '{command}' to perform system operations, install dependencies, or run processes required for the current goal."
    }
    
    await ctx.debug(f"Generated execution plan: {command}")
    return action_plan

@mcp.tool
async def update_world_model(action_result: Dict[str, Any], ctx: Context) -> Dict[str, Any]:
    """
    🔄 FEEDBACK TOOL - Reports execution results back to the cognitive planner.
    
    CRITICAL: This updates the "tape" of our cognitive Turing machine. Every operation 
    should be reported here to maintain the persistent memory that enables true cognitive planning.
    
    WORKFLOW:
    1. Get a plan from a planning tool.
    2. Execute that plan using appropriate tools.
    3. Call this tool to report the execution results.
    4. The cognitive planner updates its world model based on your report.
    
    Args:
        action_result: The result of an executed action. Can be flexible format.
        
    Returns:
        A dictionary confirming the world model update and current tape state.
    """
    await ctx.info("Updating cognitive tape with action result")
    
    world_model = get_world_model()
    
    try:
        # Add the operation to the history tape regardless of format
        world_model.add_operation("client_feedback", action_result)
        
        # Extract key information intelligently
        tool_type = action_result.get("tool", "unknown")
        status = action_result.get("status", "unknown")
        path = action_result.get("path") or action_result.get("file_path") or action_result.get("target_file")
        
        # Handle different tool types and variations
        if tool_type in ["write", "edit_file", "search_replace"] and status == "success":
            if path:
                file_info = {
                    "type": "file",
                    "exists": True,
                    "last_modified": action_result.get("timestamp", datetime.utcnow().isoformat()),
                    "size": action_result.get("size"),
                    "operation": tool_type
                }
                world_model.add_file(path, file_info)
                await ctx.debug(f"Added file to cognitive tape: {path}")
            else:
                await ctx.warning("Write operation succeeded but no path provided - tape may be incomplete")
            
        elif tool_type in ["read", "read_file", "list_dir"] and status == "success":
            if path:
                if action_result.get("is_directory"):
                    file_info = {
                        "type": "directory",
                        "exists": True,
                        "contents": action_result.get("contents", []),
                        "operation": tool_type
                    }
                else:
                    file_info = {
                        "type": "file",
                        "exists": True,
                        "size": action_result.get("size"),
                        "last_modified": action_result.get("timestamp"),
                        "operation": tool_type
                    }
                world_model.add_file(path, file_info)
                await ctx.debug(f"Updated file info in cognitive tape: {path}")
            else:
                await ctx.warning("Read operation succeeded but no path provided - tape may be incomplete")
            
        elif tool_type in ["change_directory", "cd"] and status == "success":
            if path:
                world_model.update_cwd(path)
                await ctx.debug(f"Updated CWD in cognitive tape: {path}")
            
        elif tool_type in ["execute_shell", "run_terminal_cmd"] and status == "success":
            await ctx.debug(f"Confirmed shell execution: {action_result.get('command', 'unknown')}")
            
        elif status == "error":
            error_msg = action_result.get("error", "Unknown error")
            await ctx.warning(f"Action failed: {error_msg}")
            
            if tool_type in ["read", "write"] and "not found" in error_msg.lower():
                if path and world_model.get_file_info(path):
                    world_model.remove_file(path)
                    await ctx.debug(f"Removed non-existent file from cognitive tape: {path}")
        
        # Return enhanced feedback with tape summary
        tape_summary = world_model.get_tape_summary()
        
        return {
            "status": "world_model_updated",
            "current_cwd": world_model.current_working_directory,
            "files_tracked": len(world_model.file_system),
            "operations_performed": len(world_model.operation_history),
            "update_summary": f"Processed {tool_type} action with {status} status",
            "tape_summary": tape_summary
        }
        
    except Exception as e:
        await ctx.error(f"Error updating cognitive tape: {str(e)}")
        world_model.add_operation("error", {"error": str(e), "action_result": action_result})
        return {
            "status": "world_model_update_failed",
            "error": str(e),
            "operations_performed": len(world_model.operation_history)
        }

@mcp.tool
async def get_world_model_state(ctx: Context) -> Dict[str, Any]:
    """
    🔍 QUERY TOOL - Get the current state of the cognitive planner's world model.
    
    This tool retrieves the cognitive planner's internal understanding of the file system
    and current working directory. Use this to understand what the planner "knows" about
    the current state before generating new plans.
    
    Returns:
        A dictionary containing the current world model state (files tracked, current directory, etc.).
    """
    await ctx.info("Retrieving current world model state")
    
    world_model = get_world_model()
    
    state = world_model.to_dict()
    
    await ctx.debug(f"Current world model has {len(world_model.file_system)} tracked files")
    return state

@mcp.tool
async def validate_cognitive_tape(ctx: Context) -> Dict[str, Any]:
    """
    🧠 VALIDATION TOOL - Validate that the cognitive "tape" is functioning properly.
    
    This tool provides detailed diagnostics about the Turing machine's tape state,
    including operation history, file tracking, and cognitive memory functionality.
    Use this to debug and ensure the persistent memory system is working correctly.
    
    Returns:
        A comprehensive diagnostic report of the cognitive tape state.
    """
    await ctx.info("Validating cognitive tape functionality")
    
    world_model = get_world_model()
    
    # Comprehensive tape analysis
    tape_report = {
        "tape_status": "functional" if len(world_model.operation_history) > 0 else "not_recording",
        "session_info": {
            "session_id": world_model.session_id,
            "start_time": world_model.start_time,
            "session_duration": f"{datetime.utcnow().timestamp() - datetime.fromisoformat(world_model.start_time).timestamp():.2f} seconds"
        },
        "cognitive_memory": {
            "files_tracked": len(world_model.file_system),
            "operations_recorded": len(world_model.operation_history),
            "current_working_directory": world_model.current_working_directory
        },
        "tape_contents": {
            "tracked_files": list(world_model.file_system.keys()),
            "recent_operations": world_model.operation_history[-10:] if world_model.operation_history else [],
            "operation_types": list(set(op.get("operation", "unknown") for op in world_model.operation_history))
        },
        "turing_machine_analogy": {
            "tape_head_position": world_model.current_working_directory,
            "tape_symbols": len(world_model.file_system),
            "state_transitions": len(world_model.operation_history),
            "memory_persistence": "active" if world_model.operation_history else "inactive"
        },
        "recommendations": []
    }
    
    # Add specific recommendations based on tape state
    if len(world_model.operation_history) == 0:
        tape_report["recommendations"].append("No operations recorded - ensure you're calling update_world_model after each action")
    
    if len(world_model.file_system) == 0:
        tape_report["recommendations"].append("No files tracked - ensure file paths are included in action results")
    
    if len(world_model.operation_history) > 0 and len(world_model.file_system) == 0:
        tape_report["recommendations"].append("Operations recorded but no files tracked - check action result format")
    
    await ctx.debug(f"Tape validation: {tape_report['tape_status']}")
    return tape_report

if __name__ == "__main__":
    # Alan Turing Tribute Port: 6754 for June 7, 1954, the date of his death.
    # A reminder of the persecution he faced for his sexual identity.
    # Smithery's runtime will provide its own PORT env var.
    TURING_PORT = int(os.environ.get("PORT", 6754))

    print("🧠 TuringMCP Cognitive Planner Starting...")
    print("📍 Role: I think, you do.")
    print("🔄 Architecture: Brain (Server) ↔ Hands (Client)")
    print("🌍 World Model: Internal state tracking enabled")
    print(f"🎯 Serving on port {TURING_PORT} (Tribute to Alan Turing: June 7, 1954)")
    print("🌐 Smithery.ai Compatible - Streamable HTTP")
    print("⚡ Ready to generate action plans!")

    # Use streamable HTTP for Smithery.ai compatibility
    mcp.run(transport="streamable-http", port=TURING_PORT) 