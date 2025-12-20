# System Patterns - AI Learning Pipeline

## Core Architecture

### Two-Stage Pipeline Pattern
```
Input Media → Stage 1: Prompt Generation → AI Processing → Stage 2: Response Processing → Output
```

**Stage 1 (Generate)**: Topic-aware prompt creation with template injection
**Stage 2 (Process)**: Response parsing, validation, and dual output generation

### Modular Component Architecture
- **Configuration Layer**: Centralized config management with validation
- **Template System**: Extensible prompt templates with placeholder substitution
- **Parser Layer**: Structured response validation and extraction
- **Output Adapters**: Separate Notion and Anki clients with unified interfaces

## Key Design Patterns

### Configuration as Code Pattern
- YAML-based topic configurations with schema validation
- Environment-specific settings via .env files
- Runtime config loading with caching and error handling

### Template Method Pattern for Prompts
- Base template with common structure
- Topic-specific extensions with custom instructions
- Placeholder injection system for dynamic content

### Adapter Pattern for Outputs
- Unified interface for Notion page creation
- Consistent API for Anki deck generation
- Extensible for future output formats (PDF, etc.)

### Factory Pattern for Topic Configurations
- Runtime topic resolution from command line args
- Dynamic loading of topic-specific schemas
- Validation of required vs optional configurations

## Component Relationships

### Data Flow Architecture
```
CLI Args → Config Loader → Topic Config
                        ↓
Template Engine ← Topic Config → Placeholder Injection
                        ↓
Prompt Output ← Template → AI Processing (External)
                        ↓
Response Parser → Validation → Structured Data
                        ↓
Output Router → Notion Adapter | Anki Adapter
```

### Dependency Injection Pattern
- All components receive dependencies through constructor injection
- Easy testing with mock dependencies
- Clear separation of concerns and single responsibility

## Critical Implementation Paths

### Configuration Loading Path
1. Load environment variables (.env)
2. Validate required API keys
3. Load and merge YAML configurations
4. Validate topic schemas against requirements
5. Cache validated configurations for performance

### Prompt Generation Path
1. Resolve topic from CLI args or defaults
2. Load appropriate template file
3. Inject media URL and topic-specific parameters
4. Add JSON schema specification for AI response
5. Output formatted prompt with metadata

### Response Processing Path
1. Parse JSON response with error handling
2. Validate against Pydantic models
3. Extract notes and flashcards separately
4. Route to appropriate output adapters
5. Handle partial failures gracefully

### Notion Integration Path
1. Initialize client with API key
2. Map structured data to Notion properties
3. Create page with proper database association
4. Add content blocks for rich formatting
5. Handle rate limiting and errors

### Anki Generation Path
1. Create deck with unique ID generation
2. Add flashcards with proper tagging
3. Include metadata notes for traceability
4. Package as .apkg file
5. Validate file integrity

## Error Handling Patterns

### Graceful Degradation
- Partial success: Notion succeeds, Anki fails → Report both statuses
- Configurable error levels: warnings vs failures
- Detailed error messages with recovery suggestions

### Validation Layers
- Input validation at CLI level
- Schema validation for configurations
- Response validation for AI outputs
- API validation for external services

## Performance Considerations

### Caching Strategy
- Configuration caching to avoid file I/O
- Template caching for repeated use
- Connection pooling for API clients

### Asynchronous Processing
- Potential for async API calls to Notion
- Background processing for large Anki decks
- Streaming for large response files

## Extensibility Patterns

### Plugin Architecture
- Topic configurations as plugins
- Output adapters as extensible modules
- Template system supporting custom formats

### Configuration-Driven Behavior
- New topics without code changes
- Custom fields via configuration
- Output routing based on config flags
