# Technical Context - AI Learning Pipeline

## Core Technology Stack

### Runtime Environment
- **Python Version**: 3.10+ (uses modern type hints, pattern matching)
- **Package Management**: pip with requirements.txt
- **Virtual Environment**: venv for dependency isolation

### Key Dependencies

#### Core Libraries
```txt
python-dotenv==1.0.0      # Environment variable management
pyyaml==6.0.1             # YAML configuration parsing
pydantic==2.5.0           # Data validation and serialization
click==8.1.7              # CLI framework with argument parsing
rich==13.7.0              # Terminal UI and progress indicators
```

#### Integration Libraries
```txt
notion-client==2.2.1      # Notion API integration
genanki==0.13.0           # Anki deck generation
```

### Development Tools

#### Code Quality
- **Type Checking**: Python's built-in typing system with mypy potential
- **Linting**: flake8 or ruff for code style
- **Formatting**: black for consistent code formatting

#### Testing Framework
- **Unit Testing**: pytest for comprehensive test coverage
- **Test Structure**: tests/ directory with test_* files
- **Mocking**: pytest-mock for external service mocking

#### Version Control
- **Git**: Standard branching workflow
- **GitHub**: For collaboration and CI/CD potential

## Development Setup

### Environment Setup Commands
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with actual API keys
```

### Project Structure Standards
- **Source Code**: `src/` directory with module separation
- **Scripts**: `scripts/` directory for executable CLI tools
- **Configuration**: `config/` for YAML files, `.env` for secrets
- **Templates**: `templates/` for prompt templates
- **Output**: `output/` for generated files (prompts, responses, anki)
- **Tests**: `tests/` with parallel structure to `src/`

## Technical Constraints

### API Limitations
- **Notion API**: Rate limits and property type restrictions
- **External AI Services**: Token limits, processing time, cost per request
- **File System**: Path length limits on Windows, permission issues

### Data Format Constraints
- **JSON Responses**: Must match expected schema for parsing
- **Notion Properties**: Limited field types and validation rules
- **Anki Format**: Specific requirements for deck structure and cards

### Performance Constraints
- **Memory Usage**: Large response files from AI services
- **Network Latency**: API calls to Notion and external AI services
- **File I/O**: Reading templates, writing output files

## Tool Usage Patterns

### CLI Design Patterns
- **Click Framework**: Declarative command definition with options
- **Rich Library**: Progress bars, colored output, tables
- **Argument Validation**: Built-in validation with helpful error messages

### Configuration Management
- **YAML for Structure**: Human-readable configuration files
- **Environment Variables**: Sensitive data and runtime overrides
- **Pydantic Models**: Runtime validation of configuration objects

### Error Handling
- **Custom Exceptions**: Specific error types for different failure modes
- **Logging**: Structured logging with configurable levels
- **User-Friendly Messages**: Clear error descriptions with recovery steps

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API integrations with mock servers
- **Fixture Files**: Sample responses for consistent testing
- **Test Data**: Representative examples of all data types

## Deployment Considerations

### Packaging
- **PyInstaller**: For standalone executable distribution
- **Docker**: Containerized deployment with all dependencies
- **pip install**: Direct installation from source

### Distribution
- **GitHub Releases**: Pre-built binaries for different platforms
- **PyPI**: Python package distribution
- **Docker Hub**: Container images

## Development Workflow

### Local Development
1. **Environment Setup**: Virtual environment activation
2. **Code Changes**: Edit source files with live reloading
3. **Testing**: Run test suite before commits
4. **Linting**: Automatic code formatting and style checks

### CI/CD Pipeline
- **Automated Testing**: Run tests on every push
- **Code Quality**: Linting and type checking
- **Build Verification**: Ensure package builds correctly
- **Release Automation**: Tag releases and build distributions

## Security Considerations

### API Key Management
- **Environment Variables**: Never commit secrets to version control
- **Validation**: Verify API keys are present and valid format
- **Permissions**: Minimal required permissions for Notion integration

### Data Privacy
- **Local Processing**: Sensitive content stays on user's machine
- **External AI**: User responsible for content sent to third-party services
- **Output Storage**: Generated files contain processed learning materials

## Monitoring and Observability

### Logging Strategy
- **Structured Logs**: JSON format for machine parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **File Output**: logs/pipeline.log with rotation

### Metrics Collection
- **Performance Timing**: Track processing duration
- **Success Rates**: Monitor API call success/failure
- **Error Categorization**: Track common failure patterns
