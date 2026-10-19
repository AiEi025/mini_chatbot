# NEXUS — Stateful AI Assistant

NEXUS is a Python-based AI assistant built with **LangGraph** that combines task routing, specialized agent nodes, persistent conversation state, and long-term user memory.

The project explores how to build a modular AI agent that can handle different types of requests, use external tools, refine its outputs through validation loops, and personalize responses using information retained across conversations.

## Key Features

- **Intent-Based Routing:** Classifies incoming requests and directs them to the appropriate specialized node.
- **Specialized Agent Nodes:** Separates Python code assistance, planning, tool-based tasks, and general conversation.
- **Graph-Based Orchestration:** Uses LangGraph to coordinate execution paths, conditional transitions, and validation loops.
- **Persistent Conversation State:** Uses PostgreSQL-backed checkpointing to preserve graph state across interactions.
- **Long-Term User Memory:** Stores structured user information, including skills, goals, projects, and preferences.
- **Memory Updates:** Supports setting single-value fields, adding list items, and removing list items through structured memory operations.
- **Tool Integration:** Includes a dedicated tools node for tasks such as web search, RAG, uploaded-file workflows, and MCP-based tool integration, depending on the configured integrations.
- **Output Validation:** Uses specialized validation nodes to review results and determine whether another execution cycle is needed.
- **Asynchronous Execution:** Uses Python's `async`/`await` patterns for asynchronous operations such as memory access and tool execution.

## Architecture

NEXUS uses a graph-based architecture in which a router classifies each request and directs execution to a specialized node.

```text
                         User Request
                               |
                               v
                            Router
                               |
                 +-------------+-------------+
                 |             |             |
                 v             v             v
             Python         Planning        Tools
                 |             |             |
                 v             v             v
             Validation    Validation     Validation
                 |             |             |
                 +-------------+-------------+
                               |
                               v
                       Conditional Routing

                         General Node
                               |
                               v
                         Assistant Response
```

The router also retrieves and updates the user's long-term profile. The resulting memory context is added to the relevant generation prompts.

The graph supports conditional transitions, allowing validation nodes to finish execution or send a task back to its corresponding generation node for another iteration.

## Specialized Nodes

### 1. Router

The router acts as the entry point of the agent workflow.

Responsibilities:
- Classify incoming requests.
- Select the appropriate execution path.
- Retrieve the existing user profile from persistent storage.
- Extract structured memory changes from the latest user message.
- Apply memory updates and persist the resulting profile.
- Provide a memory context for downstream nodes.

### 2. Python Node

Handles requests involving Python code, such as debugging, fixing, and modifying Python files.

The workflow instructs the agent to inspect the target file before making changes and avoid modifying unrelated files.

### 3. Planning Node

Handles planning, scheduling, prioritization, and time-management requests.

The planning workflow can generate a plan, evaluate it through a critic or validation step, and revise it according to the feedback.

### 4. Tools Node

Handles requests requiring external capabilities, such as search, retrieval, uploaded-file workflows, and connected tools.

The project includes asynchronous MCP tool integration. Actual tool availability depends on the configured servers and integrations.

### 5. General Node

Handles general questions, explanations, translations, summarization, and conversational requests.

It uses the conversation history and relevant long-term user memory to produce context-aware responses.

### 6. Validation Nodes

Specialized validation nodes review the outputs of the Python, planning, and tools workflows.

Conditional transitions determine whether the current workflow should finish or execute another iteration.

## Memory Architecture

NEXUS distinguishes between two forms of memory.

### Short-Term Memory: Conversation State

LangGraph manages the state of an individual workflow and can maintain conversation-related state through a configured checkpointer.

The project uses PostgreSQL-backed checkpointing to persist graph state. The exact information retained depends on the fields defined in the graph state and the configured checkpointing implementation.

### Long-Term Memory: User Profile

Long-term memory is stored separately through a persistent Store interface backed by PostgreSQL.

The current profile uses structured fields such as:

- `name`
- `occupation`
- `language`
- `response_style`
- `skills`
- `goals`
- `projects`
- `other`

Memory updates are represented as structured operations:

| Operation | Purpose |
|---|---|
| `set` | Set or replace a single-value field |
| `add` | Add a new item to a list field |
| `remove` | Remove an item from a list field |

The memory workflow follows these steps:

1. Retrieve the existing user profile.
2. Analyze the latest user message using a structured-output LLM.
3. Generate justified memory changes.
4. Apply the changes in Python.
5. Persist the updated profile.
6. Build a memory context for relevant agent nodes.

This design separates the model's proposed changes from the Python code that applies them.

The long-term profile and graph checkpoint state serve different purposes and are stored through separate interfaces.

## Technology Stack

| Technology | Role |
|---|---|
| Python | Core application language |
| LangGraph | Agent workflow orchestration and state transitions |
| LangChain | Prompt construction and model integration |
| PostgreSQL | Persistent storage |
| LangGraph Checkpointer | Persistent graph-state and conversation checkpointing |
| LangGraph Store | Long-term user-profile storage |
| Pydantic | Structured models and validation of memory operations |
| Async Python | Non-blocking execution of supported I/O operations |
| MCP | Integration with external tools and servers |
| Streamlit | UI framework for applicable application interfaces |

The exact LLM provider, model configuration, PostgreSQL driver, and MCP servers depend on the project configuration.

## Data Flow

A typical request follows this process:

1. The user submits a request.
2. The router retrieves the current user profile.
3. A memory extraction model identifies justified profile changes.
4. Python applies the changes and saves the updated profile.
5. The router classifies the request.
6. LangGraph routes execution to the appropriate node.
7. The node uses relevant memory and conversation context to perform the task.
8. A validation node reviews the result when applicable.
9. The workflow returns the final result.

## Project Status

NEXUS is an evolving project focused on modular agent architecture, persistent state, and personalized AI interactions.

Implemented areas include:
- Graph-based request routing.
- Specialized agent workflows.
- PostgreSQL-backed persistence for graph state and long-term user memory.
- Structured profile updates.
- Memory-aware generation prompts.
- Validation-driven execution paths.
- Asynchronous tool integration.

Further development areas include containerization with Docker, deployment configuration, automated testing, observability, and production-hardening of memory updates and tool execution.

## Setup

The application requires Python, PostgreSQL, and the dependencies and external services configured by the project.

Before running the application:

1. Install the Python dependencies listed in the project's dependency file.
2. Configure PostgreSQL and create the required database.
3. Set the database connection and LLM configuration through environment variables.
4. Configure any required MCP servers or external integrations.
5. Run the application's entry point according to the project configuration.

**Note:** Exact installation commands, environment-variable names, and launch instructions should be added after confirming the current repository structure and configuration files.

## Security Considerations

- Store database credentials and API keys in environment variables or a secrets manager.
- Never commit `.env` files or credentials to version control.
- Restrict filesystem access for agents that modify Python files.
- Validate tool inputs and outputs before using them in sensitive workflows.
- Review memory extraction and update behavior before using long-term memory in production.

## Learning and Development Goals

NEXUS is also a practical exploration of:
- Stateful AI agent design.
- LangGraph orchestration patterns.
- Short-term and long-term memory.
- PostgreSQL integration and persistence.
- Structured LLM outputs.
- Asynchronous Python programming.
- Tool-using agents and validation loops.
- Deployment and containerization.

---

**NEXUS — A modular AI assistant with persistent state, structured memory, and specialized agent workflows.**