# Scenarios Models

## Purpose
Data models for simulation scenarios, including personas, objectives, and configuration that drive the simulation behavior.

## Key Components
- **scenario.py**: Core SingleScenario and ScenarioForGeneration models
- **agent_spec.py**: Agent specification for scenario generation
- **generation.py**: Models for scenario generation requests and responses
- **skeleton.py**: Skeleton patterns for scenario generation
- **settings.py**: Environment and configuration settings

## Program Flow
1. Agent spec defines capabilities and use cases
2. Skeleton generator creates patterns from spec
3. LLM generates ScenarioForGeneration instances
4. System assigns UUID to create SingleScenario
5. Scenario drives simulation conversation

## Data Flow
- **Generation**: AgentSpec → Skeletons → ScenarioForGeneration → SingleScenario
- **Storage**: SingleScenario → Redis with generation_id:scenario_id key
- **Retrieval**: Redis → SingleScenario → SimulationService
- **Inheritance**: ScenarioForGeneration (base) → SingleScenario (adds scenario_id)

## Common Tasks
- To add scenario field: Update ScenarioForGeneration (not SingleScenario)
- To modify generation: Update skeleton patterns and prompts
- To change defaults: Modify field defaults in scenario.py
- To debug scenarios: Check Redis storage and UUID assignment
