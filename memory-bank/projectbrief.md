# AI Learning Pipeline - Project Brief

## Core Mission
Build a two-stage CLI tool that transforms educational video content into structured learning materials through automated processing with external multimodal AI services.

## Key Objectives
- **Topic-Aware Processing**: Support configurable processing for different educational domains (cooking, general learning, etc.)
- **Dual Output**: Generate both structured notes in Notion and/or flashcard decks for Anki
- **Modular Architecture**: Clean separation between prompt generation and response processing
- **Configurable Databases**: Topic-specific Notion databases and Anki decks with custom schemas

## Scope Boundaries
- **In Scope**: CLI tool development, configuration management, Notion/Anki integration
- **Out of Scope**: AI model training, video processing algorithms, direct video analysis
- **External Dependencies**: Google Cloud Studio (or similar) for multimodal AI processing

## Success Criteria
- Successfully processes educational videos into Notion pages and Anki decks
- Supports multiple topics with custom configurations
- Clean, maintainable codebase with comprehensive testing
- Well-documented setup and usage instructions

## Technical Constraints
- Python 3.10+ only
- External AI service required for content analysis
- API rate limits for Notion and potential AI services
- Cross-platform CLI compatibility (Windows/Mac/Linux)

## Project Timeline
7 implementation phases from infrastructure setup through full integration and documentation.
