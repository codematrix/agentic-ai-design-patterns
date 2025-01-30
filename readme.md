# AI Agentic Design Patterns

This repository showcases a collection of simple AI agents designed to demonstrate various design patterns in `AI Agentic` driven workflows. Each pattern is implemented with practical examples and detailed explanations to help developers and researchers understand and apply these concepts effectively in their projects.

To keep things simple and to reduce unnecessary complexity, the examples will minimize framework dependencies. We've chosen [Pydantic AI](https://ai.pydantic.dev/) for our agentic development as it is both lightweight and provides the essential building blocks for building production-quality AI Agents.

All use cases (except for one) leverages [Pydantic Graphs](https://ai.pydantic.dev/api/pydantic_graph/graph/) to manage agentic workflows. Using `graph-based workflows` from the outset is a good **best practice** for several reasons:

- Most agentic workflows involve multiple agents. A graph-based workflow approach provides a consistent foundational pattern, making it easier to understand and maintain across the development team.  
- Introducing graph-based workflows early in the SDLC makes it significantly easier when extensibility and refactoring are required.

### Considerations

#### Use-Cases  
The example scenarios in this repository are contrived and intentionally constructed for simplicity. The goal is to eliminate unnecessary distractions from complicated use-cases and focus purely on the topics at hand - **AI Agentic Design Patterns**.

#### Disclaimer  
I come from a C# background, so my Python skills may not be perfect. Suggestions for improvements are always welcome!


## Design Patterns Covered

This section highlights various design patterns commonly used in AI agentic development. For a deeper understanding of why and when to apply a particular design pattern, refer to the following articles:
- [Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Multi-agent Systems](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

### Single Agent (no graphs)
- Demonstrates how a single agent can integrate with third-party tools like Asana to automate project and task management.
- Features:
  - Tool calling 
  - console app (with streaming)
  - streamlit app (with streaming)
  - chat history
- **Note**: For sake of demonstration, the Asana API is a mock and utilizes _sqlite_ to maintain states i.e. Projects and Tasks

### Prompt Chaining Workflow
- Demonstrates how to use prompt chaining - taking part or in whole, the response of a previous agent and using it as input to the next agent in the chain.
- Use-case: 
  - Obtain a validate city from the user. If a valid city was not provided, the end and with no results.
  - Once a validate city was provided, get details about the city i.e. Regional information and a summarized history about the city. 
  - **Note**: Obviously, this use-case can be achieved using a single agent with a **one-shot** prompt. As stated before, the objective is to demonstrate the design pattern and keeping the use-case as simple as possible for demonstration purposes.
- Features:
  - Multi-Agent
  - Graphs
  - States
  - Result Type
  - Prompt Chaining
- Workflow
<p style="margin-left: 40px;">
  <img src="resources/prompt_chaining.png" alt="AI Agent" width="600">
</p>



## WORK IN PROGRESS SUBJECT TO CHANGE


#### Routing Workflow (Supervisor Role)
- An agent acts as a router, directing incoming tasks to specialized sub-agents or workflows.

#### Routing Parallelization (Supervisor Role)
- Similar to the routing workflow, but tasks are distributed and processed in parallel by multiple sub-agents.

#### Orchestrator-Workers Workflow (Supervisor Role)
- An orchestrator agent coordinates multiple worker agents to perform tasks collaboratively, ensuring dependencies are resolved and tasks are completed efficiently.

#### Evaluator-Optimizer Workflow
- An evaluator agent assesses the output of other agents and provides feedback, which is then used by an optimizer agent to improve results iteratively.

#### Human-in-the-Loop (HITL) Workflow
- Combines agent autonomy with human oversight, allowing humans to review, validate, or intervene in the agent's decision-making process.

#### Long-Running with HITL Workflow - Hydrating/Dehydrating
- Enables agents to handle long-running tasks with intermittent human interactions, while maintaining state persistence through hydration (storing state) and dehydration (resuming state).

## How to Use
1. Clone this repository: 
   ```bash
   git clone https://github.com/codematrix/agent-design-patterns.git
   ```
2. Explore each design pattern example in the respective directories.

### Requirements
- Python 3.13.1
- Required libraries listed in `requirements.txt`

Install the dependencies:
```bash
pip install -r requirements.txt
```

### Create and update the **.env** file

We provided a sample **.env.readme** file. Please copy and create your own **.env** file and update the values using your API keys. 
If you use different model providers, then make sure to update agents used in the examples. 
If you're not using **logfire**, you can exclude those key/value pairs.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request to suggest improvements or add new design patterns.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
