# Agents with Design Patterns

This repository contains a collection of simple agents designed to demonstrate various design patterns in AI-driven workflows. Each pattern is implemented with practical examples and detailed explanations to help developers and researchers understand and apply these patterns effectively in their projects. 

The samples will be light on frameworks to reduce complexity. I decided to use [Pydantic AI](https://ai.pydantic.dev/) for agentic development as it's lightweight and me the necessary building blocks that I need, without too much ceremony getting a basic agent running. 

## Design Patterns Covered

This section showcases the capabilities of a single agent and highlights its use cases in different scenarios.

#### Tooling - Using Asana
- Demonstrates how an agent can integrate with third-party tools like Asana to automate task management and improve efficiency.
- Example: Fetching tasks, creating assignments, or updating task statuses programmatically.
- Features:
  - Tool calling 
  - steaming - console
  - streaming - streamlit
- **NOTE**: The Asana API is a mock and will use _sqlite_ to maintain states i.e. Projects and Tasks

## WORK IN PROGRESS SUBJECT TO CHANGE

#### Prompt Chaining Workflow
- A structured workflow where outputs from one prompt become inputs for the next step, enabling multi-step reasoning or task execution.
- Example: A task planning agent that generates subtasks from a high-level goal and then provides detailed execution plans for each subtask.

#### Routing Workflow (Supervisor Role)
- An agent acts as a router, directing incoming tasks to specialized sub-agents or workflows.
- Example: Categorizing customer support requests and assigning them to the appropriate department.

#### Routing Parallelization (Supervisor Role)
- Similar to the routing workflow, but tasks are distributed and processed in parallel by multiple sub-agents.
- Example: Distributing multiple language translation requests to agents specializing in specific languages.

#### Orchestrator-Workers Workflow (Supervisor Role)
- An orchestrator agent coordinates multiple worker agents to perform tasks collaboratively, ensuring dependencies are resolved and tasks are completed efficiently.
- Example: A research agent orchestrating data collection, analysis, and reporting by worker agents.

#### Evaluator-Optimizer Workflow
- An evaluator agent assesses the output of other agents and provides feedback, which is then used by an optimizer agent to improve results iteratively.
- Example: A code generation agent whose outputs are reviewed by an evaluator for correctness, followed by optimization for performance.

#### Human-in-the-Loop (HITL) Workflow
- Combines agent autonomy with human oversight, allowing humans to review, validate, or intervene in the agent's decision-making process.
- Example: A content generation agent that drafts articles, reviewed by a human editor for quality assurance.

#### Long-Running with HITL Workflow - Hydrating/Dehydrating
- Enables agents to handle long-running tasks with intermittent human interactions, while maintaining state persistence through hydration (storing state) and dehydration (resuming state).
- Example: A legal document review agent that pauses for human feedback at critical decision points and resumes processing afterward.

## How to Use
1. Clone this repository: 
   ```bash
   git clone https://github.com/yourusername/simple-agents-design-patterns.git
   ```
2. Explore each design pattern example in the respective directories.
3. Follow the instructions in each example's README to set up and run the agent.

## Requirements
- Python 3.13.1
- Required libraries listed in `requirements.txt`

Install the dependencies:
```bash
pip install -r requirements.txt
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to suggest improvements or add new patterns.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
