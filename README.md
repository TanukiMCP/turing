# TuringMCP - Cognitive Planning Engine

**A Turing-Complete Cognitive Planner for AI Agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Smithery.ai Compatible](https://img.shields.io/badge/smithery.ai-compatible-green.svg)](https://smithery.ai)

## ⚠️ CRITICAL FOR LLM AGENTS ⚠️

**TuringMCP is a PLANNING-ONLY system that requires a session-based workflow.**

- 🚀 **START**: You MUST call `initialize_session` to begin any new task.
- 🤔 **PLAN**: Generate JSON action plans (e.g., `plan_read_at_head`).
- 🖐️ **EXECUTE**: Execute those plans using your own tools (`edit_file`, `run_terminal_cmd`).
- 📢 **FEEDBACK**: Report execution results back using `update_world_model`.
- 🏁 **END**: You MUST call `archive_session` to complete the task.

📖 **Read the [TuringMCP Usage Guide](./TURINGMCP_USAGE_GUIDE.md) for detailed instructions.**

## 🚀 Quick Start

```python
# 1. Initialize session
session = await client.call_tool("initialize_session", {})

# 2. Get a plan
plan = await client.call_tool("plan_read_at_head", {"path": "config.json"})

# 3. Execute the plan with your tools
content = read_file("config.json")  # Your tool, not TuringMCP's

# 4. Report results
await client.call_tool("update_world_model", {
    "action_result": {"tool": "read_file", "status": "success", "path": "config.json"}
})

# 5. Archive session when done
await client.call_tool("archive_session", {})
```

---

## 🧠 What is TuringMCP?

TuringMCP is a revolutionary **Model Context Protocol (MCP)** server that implements a cognitive planner architecture, separating the "brain" (planning) from the "hands" (execution) in AI agent systems.

### Core Innovation: Cognitive Turing Machine for LLMs

Unlike traditional AI systems, TuringMCP implements a **persistent memory architecture** that enables:
- **Cognitive continuity** across operations
- **Strategic planning** with accumulated context
- **Self-reflection** and state validation
- **Near-AGI capabilities** through memory persistence

## 🏗️ Architecture: Brain ↔ Hands

```ascii
+---------------------+         +----------------------+
|    COGNITIVE BRAIN  |         |    EXECUTION HANDS   |
|   (TuringMCP Server)|         |   (Your AI Agent)    |
+---------------------+         +----------------------+
| • Session Management|         | • File Operations    |
| • Strategic Planning|         | • Terminal Commands  |
| • Memory Persistence|         | • Real-world Actions |
| • State Validation  |         | • User Permissions   |
+---------------------+         +----------------------+
     🧠 THINKS                      🖐️ DOES
```

### Session-Based Cognitive Loop

```ascii
┌─────────────────┐    1. initialize_session    ┌─────────────────┐
│   Cognitive     │ ──────────────────────────► │   Execution     │
│   Planner       │                             │   Agent         │
│  (TuringMCP)    │ ◄── 2. Plan/Execute Loop ──│  (Your Tools)   │
│                 │ ──────────────────────────► │                 │
│                 │ ◄── 3. archive_session ────│                 │
└─────────────────┘                             └─────────────────┘
```

## 🛠️ Cognitive Planning Tools

TuringMCP implements **9 cognitive tools** organized into three categories:

### 🚀 Session Management (Mandatory)

#### `initialize_session()`
**Purpose**: Initialize a new cognitive planning session with persistent memory.

**Returns**:
```json
{
  "status": "session_initialized",
  "session_id": "unique-session-id",
  "start_time": "2024-01-01T12:00:00Z",
  "message": "Cognitive planning session started."
}
```

#### `archive_session()`
**Purpose**: Archive session data and clear memory for the next task.

**Returns**:
```json
{
  "status": "session_archived",
  "session_id": "unique-session-id",
  "archive": { ...complete world model... },
  "message": "Session complete. Memory cleared."
}
```

### 🤔 Planning Tools (Core Intelligence)

#### `plan_read_at_head(path: str)`
Generate intelligent plans for reading files or directories.

#### `plan_write_at_head(path: str, content: str)`
Generate strategic plans for writing content to files.

#### `plan_move_head(new_path: str)`
Generate plans for changing working directory context.

#### `plan_execute_at_head(command: str)`
Generate plans for executing shell commands.

### 🔄 Feedback & Validation Tools

#### `update_world_model(action_result: dict)`
**Critical**: Updates the cognitive "tape" with execution results.

**Enhanced Output**:
```json
{
  "status": "world_model_updated",
  "current_cwd": "/project",
  "files_tracked": 15,
  "operations_performed": 42,
  "update_summary": "Processed edit_file action with success status",
  "tape_summary": {
    "session_id": "unique-session-id",
    "files_tracked": 15,
    "operations_performed": 42,
    "last_5_operations": [...],
    "file_paths": [...]
  }
}
```

#### `get_world_model_state()`
Retrieve complete cognitive state for debugging and analysis.

#### `validate_cognitive_tape()`
**New**: Comprehensive diagnostics of the cognitive "tape" system.

**Returns**:
```json
{
  "tape_status": "functional",
  "cognitive_memory": {
    "files_tracked": 15,
    "operations_recorded": 42
  },
  "turing_machine_analogy": {
    "tape_head_position": "/project",
    "tape_symbols": 15,
    "state_transitions": 42,
    "memory_persistence": "active"
  },
  "recommendations": []
}
```

## 🧠 The Cognitive Turing Machine

TuringMCP implements a **Turing machine for LLMs** - enabling true cognitive computation:

### Traditional vs Cognitive Turing Machine

| Component | Traditional Turing Machine | TuringMCP (Cognitive) |
|-----------|---------------------------|---------------------|
| **Tape** | Static symbols | Dynamic world model with file state |
| **Head** | Physical position | Current working directory context |
| **State** | Fixed rules | Session-based planning context |
| **Memory** | Mechanical | Persistent cognitive memory |
| **Computation** | Rule-based | Reasoning-based with learning |

### Why This Enables Near-AGI

1. **Persistent Memory**: Unlike stateless LLMs, maintains cognitive continuity
2. **Strategic Planning**: Multi-step reasoning with accumulated context
3. **Self-Reflection**: Can examine and validate its own cognitive state
4. **Adaptive Learning**: Strategies improve based on accumulated experience

## 📊 Capabilities Matrix

| TuringMCP DOES | TuringMCP DOESN'T DO |
|----------------|---------------------|
| ✅ Generate strategic action plans | ❌ Execute file operations |
| ✅ Maintain persistent cognitive memory | ❌ Access real file system |
| ✅ Track comprehensive operation history | ❌ Run shell commands |
| ✅ Provide contextual reasoning | ❌ Connect to external APIs |
| ✅ Validate cognitive "tape" integrity | ❌ Perform actual I/O |
| ✅ Enable near-AGI capabilities | ❌ Access network resources |

## 🔧 Validating the Cognitive Tape

The "tape" is TuringMCP's persistent memory system. Ensure it's working:

### 1. Check Tape Status
```python
tape_report = await client.call_tool("validate_cognitive_tape", {})
print(f"Status: {tape_report['tape_status']}")
print(f"Operations: {tape_report['cognitive_memory']['operations_recorded']}")
print(f"Files: {tape_report['cognitive_memory']['files_tracked']}")
```

### 2. Expected Behavior
- ✅ **Every operation recorded** in history
- ✅ **Files tracked** when read/written
- ✅ **Directory changes** update the head position
- ✅ **Memory persists** across tool calls

### 3. Troubleshooting
**Problem**: `files_tracked: 0` after operations
**Solution**: 
- Ensure `update_world_model` is called after each action
- Include `path` field in action results
- Use flexible feedback formats

## 🚀 Getting Started

### Installation

```bash
pip install -r requirements.txt
python server.py
```

### Expected Output
```
🧠 TuringMCP Cognitive Planner Starting...
📍 Role: I think, you do.
🔄 Architecture: Brain (Server) ↔ Hands (Client)
🌍 World Model: Internal state tracking enabled
🎯 Serving on port 6754 (Tribute to Alan Turing: June 7, 1954)
🌐 Smithery.ai Compatible - Streamable HTTP
⚡ Ready to generate action plans!
```

## 🌐 Production Deployment

### Smithery.ai (Recommended)

1. **Fork** this repository
2. **Deploy** on [Smithery.ai](https://smithery.ai)
3. **Connect** your clients to the deployed URL

```python
# Connect to deployed server
mcp_url = "https://server.smithery.ai/@your-username/turingmcp"
async with Client(mcp_url) as client:
    result = await client.call_tool("initialize_session", {})
```

### Docker Deployment

```bash
docker build -t turingmcp .
docker run -p 6754:6754 turingmcp
```

## 🔄 Professional Usage Pattern

### Complete Session Example

```python
async def turingmcp_workflow():
    async with Client("http://localhost:6754/mcp") as client:
        # 1. Initialize cognitive session
        session = await client.call_tool("initialize_session", {})
        
        # 2. Strategic planning phase
        read_plan = await client.call_tool("plan_read_at_head", {"path": "config.json"})
        
        # 3. Execute with your tools
        content = read_file("config.json")
        
        # 4. Report to cognitive tape
        await client.call_tool("update_world_model", {
            "action_result": {
                "tool": "read_file",
                "status": "success",
                "path": "config.json",
                "size": len(content)
            }
        })
        
        # 5. Validate cognitive state
        tape_status = await client.call_tool("validate_cognitive_tape", {})
        
        # 6. Archive session
        await client.call_tool("archive_session", {})
```

## 🔬 Advanced Features

### Flexible Feedback Formats

```python
# Minimal format
{"tool": "edit_file", "status": "success", "path": "/file.txt"}

# Detailed format
{"tool": "read_file", "status": "success", "target_file": "/file.txt", "size": 1024}

# Error handling
{"tool": "write", "status": "error", "path": "/file.txt", "error": "Permission denied"}
```

### Performance Optimization

- **Session Management**: Archive sessions promptly to free memory
- **Concurrent Sessions**: Multiple clients can maintain separate sessions
- **State Monitoring**: Use `validate_cognitive_tape` for health checks

### Integration Examples

#### Cursor/Claude Integration
```python
# In AI agent workflow
session = await initialize_session()
plan = await plan_read_at_head("src/config.py")
result = read_file("src/config.py")  # Your tool
await update_world_model({"tool": "read_file", "status": "success", "path": "src/config.py"})
await archive_session()
```

#### LangChain Integration
```python
from langchain.tools import tool

@tool
def cognitive_planner(action_type: str, **kwargs):
    """Use TuringMCP for cognitive planning with persistent memory"""
    # Integration logic here
    pass
```

## 🧮 Tribute to Alan Turing

**Port 6754** honors **June 7, 1954** - the date of Alan Turing's death.

Turing pioneered the concept of thinking machines. TuringMCP extends his vision by creating a cognitive architecture that separates computation (thinking) from execution (doing) - exactly what modern AI agents need to achieve true intelligence.

> "We can only see a short distance ahead, but we can see plenty there that needs to be done."  
> — Alan Turing

## 🤝 Contributing

TuringMCP represents a paradigm shift in AI architecture. Contributions welcome:

- **Cognitive enhancements** to the planning algorithms
- **Memory optimization** for the persistent world model
- **Integration examples** with popular AI frameworks
- **Documentation improvements** and tutorials

## 📄 License

MIT License - This project embodies the future of AI cognitive architectures.

---

## 🎯 Production-Ready Features

**TuringMCP** is enterprise-ready with:

- 🧠 **Cognitive Planning Engine** - True AI reasoning with memory
- 🎯 **Port 6754** - Honoring Alan Turing (June 7, 1954)
- 🌐 **Streamable HTTP** - Real-time client-server communication
- ☁️ **Cloud-Native** - Deploy anywhere, scale everywhere  
- 🔄 **Persistent Memory** - Cognitive continuity across sessions
- 🛡️ **Production-Grade** - Comprehensive error handling and monitoring
- 🔧 **Diagnostic Tools** - Built-in cognitive tape validation

**TuringMCP: Where thinking meets doing. Intelligence meets action.** 🚀

*"Sometimes it is the people no one expects anything from who do the things that no one can imagine."* — Alan Turing