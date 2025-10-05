# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: HealthSmart Multi-Agent Healthcare Assistant

An AI-powered healthcare service navigation system built with Google's Agent Development Kit (ADK) that uses a multi-agent architecture to help patients find and enroll in appropriate healthcare services through intelligent assessment, emergency screening, and dynamic routing.

## Core Architecture

### Multi-Agent System
- **Coordinator Agent** ([app/smart_health_agent.py](app/smart_health_agent.py)): Main orchestrator with emergency screening and assessment capabilities
- **Specialist Agents**: Service-specific agents (RPM, Telehealth, Insurance, Pharmacy, Wellness) for detailed consultation and enrollment
- **Rules Engine** ([app/rules_engine_enhanced.py](app/rules_engine_enhanced.py)): JSON-based eligibility assessment with confidence scoring and decision trails
- **Session Management**: Uses ADK's `InMemorySessionService` for persistent conversation context

### Data Architecture
- **JSON Rules** (`rules/*.json`): Service eligibility rules, assessment questions, emergency screening criteria
  - `rpm_eligibility.json`, `telehealth_eligibility.json`, `insurance_enrollment.json`
  - `pharmacy_savings.json`, `wellness_programs.json`
  - `assessment_questions.json`, `emergency_screening.json`
- **Legacy CSV** (`data/*.csv`): Original rule files kept as backup (not actively used)

### Web Interfaces
- **Development** ([web_app.py](web_app.py)): Full-featured interface on port 8000 with comprehensive API
- **Production** ([simple_web_app.py](simple_web_app.py)): Cloud Run-ready interface on port 8080 (HealthAngel branding)

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (recommended)
source activate.sh

# Or manually
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Running the Application
```bash
# Production web app (Cloud Run ready)
python simple_web_app.py       # http://localhost:8080

# Development web app (full features)
python web_app.py              # http://localhost:8000

# Direct agent testing
python app/smart_health_agent.py
```

### Testing
```bash
# Run all tests
python -m pytest Testing/

# Run specific test suites
python Testing/test_gemini_api.py           # API validation
python Testing/test_service_flow.py         # Service flow testing
python Testing/test_interactive_app.py      # Interactive scenarios

# Run with coverage
python -m pytest Testing/ --cov=app
```

### Common Development Tasks
```bash
# Install/update dependencies
pip install -r requirements.txt

# Check API configuration
python Testing/test_gemini_api.py

# Deploy to Google Cloud Run (production)
gcloud run deploy healthsmart-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --port 8080
```

## Configuration

### Environment Variables (.env)
- `GEMINI_API_KEY`: Google Gemini API key (required)
- `GOOGLE_CLOUD_PROJECT`: Google Cloud project ID (optional, auto-detected)
- `GOOGLE_CLOUD_LOCATION`: Region (default: us-central1)

### Model Configuration
- **Primary Model**: `gemini-2.5-flash` (configurable in [config.py](config.py))
- **API Provider**: Google Gemini API (with Vertex AI fallback support)
- **API Key**: Set via `GEMINI_API_KEY` environment variable (takes precedence over Vertex AI)

## Key Implementation Details

### Agent Handoff Flow
1. Coordinator presents services and screens for emergencies
2. Conducts dynamic assessment using JSON rules
3. Evaluates eligibility with confidence scoring
4. Routes to appropriate specialist agent
5. Specialist handles service-specific consultation and enrollment

### JSON Rules Engine
- **Confidence Scoring**: Each eligibility assessment includes confidence levels
- **Decision Trails**: Complete audit trail of assessment decisions
- **Fallback Options**: Alternative services when primary unavailable
- **Dynamic Questions**: Intelligent question sequencing based on missing data

### Session Management
- Uses ADK's built-in session service (InMemorySessionService)
- Session IDs managed automatically by ADK framework
- Conversation context preserved across interactions
- No persistent storage (HIPAA-compliant for demo purposes)

## Working vs Broken Components

**✅ Working:**
- [web_app.py](web_app.py) - Development interface (port 8000)
- [simple_web_app.py](simple_web_app.py) - Production interface (port 8080)
- [app/smart_health_agent.py](app/smart_health_agent.py) - Main multi-agent system
- [app/rules_engine_enhanced.py](app/rules_engine_enhanced.py) - JSON rules engine
- [app/session_manager.py](app/session_manager.py) - Session management
- All specialist agents embedded in smart_health_agent.py
- Emergency screening system

**⚠️ Deprecated/Broken:**
- [main.py](main.py) - Uses outdated imports
- Files with `_backup`, `_fixed`, `fix_` prefixes - Historical versions
- Legacy CSV system - Replaced by JSON rules in `rules/` directory

## File Organization

### Active Production Files
- [simple_web_app.py](simple_web_app.py) - Production web app (port 8080)
- [web_app.py](web_app.py) - Development web app (port 8000)
- [app/smart_health_agent.py](app/smart_health_agent.py) - Main agent system
- [app/rules_engine_enhanced.py](app/rules_engine_enhanced.py) - JSON rules engine
- [app/session_manager.py](app/session_manager.py) - Session management utilities
- [config.py](config.py) - Configuration management

### Data Files
- `rules/*.json` - Active JSON rules (primary)
- `data/*.csv` - Legacy CSV files (backup only)

### Testing
- [Testing/](Testing/) - All test files
- `test_use_cases.py` - Legacy test file (use Testing/ directory instead)

### Documentation
- [doc-specs/](doc-specs/) - Technical specifications and PRDs
- [README.md](README.md) - Comprehensive project documentation
- PRD files describe system architecture and implementation plans

### Backup/Deprecated
- [backup/](backup/) - Archived files
- Files with `_backup`, `_fixed`, `fix_` prefixes - Deprecated/historical

## Development Patterns

### Adding New Services
1. Create JSON rule file in `rules/` directory (e.g., `new_service_eligibility.json`)
2. Add service enum to `ServiceType` in [smart_health_agent.py](app/smart_health_agent.py):34
3. Create specialist agent class following existing patterns in [smart_health_agent.py](app/smart_health_agent.py)
4. Update `present_available_services()` tool to include new service
5. Add eligibility assessment logic to rules engine if needed

### Modifying Eligibility Rules
- Edit JSON files in `rules/` directory
- No code changes required - rules are loaded dynamically by [rules_engine_enhanced.py](app/rules_engine_enhanced.py)
- Restart application to reload rules

### Testing New Features
1. Add test file in [Testing/](Testing/) directory
2. Follow existing test patterns (see [test_service_flow.py](Testing/test_service_flow.py))
3. Run with pytest to ensure compatibility
