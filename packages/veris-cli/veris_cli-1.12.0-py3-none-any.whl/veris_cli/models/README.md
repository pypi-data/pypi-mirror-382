# Models

## Purpose
Pydantic data models defining the structure and validation for all data flowing through the simulation system, ensuring type safety and consistency.

## Key Components
- **api.py**: Request/response models for API endpoints
  - Defines simulation statuses: PENDING, IN_PROGRESS, COMPLETED, FAILED
- **engine.py**: Core simulation models (SimulatorOutput, ResponseExpectation)
- **scenarios/**: Scenario-related models and configuration
- **evals/**: Evaluation framework models

## Program Flow
1. API receives JSON data
2. Pydantic validates and parses into model instances
3. Models passed through service layers
4. Validation ensures data integrity at each boundary
5. Models serialized back to JSON for responses

## Data Flow
- **API Layer**: JSON → Pydantic models → Services
- **Service Layer**: Models passed between services maintaining type safety
- **Persistence**: Models → dict → Redis → Models
- **Response**: Models → JSON → Client

## Common Tasks
- To add new field: Update model class and handle migrations
- To validate data: Add Pydantic validators to model
- To debug validation: Check model field types and constraints
- To extend scenarios: Modify scenario models in scenarios/ subdirectory
