# Vertice Cyber - Simplified BIOGUARD Architecture

**Consolidated from 120+ microservices to 11 macro-agents**

## Overview

Vertice Cyber is a simplified, production-ready implementation of the BIOGUARD architecture, reducing complexity from 120+ microservices to 11 focused macro-agents. This approach maintains the biomimetic intelligence while being feasible for development and deployment.

## Architecture

### Core Philosophy

- **Biomimetic Design**: Inspired by biological immune systems
- **Ethical Governance**: All agents validated by Ethical Magistrate
- **Modular Agents**: Each agent has single responsibility
- **Autonomous Operation**: Agents coordinate through APIs

### Agent Hierarchy

```
🏛️ ETHICAL MAGISTRATE (Core Governance)
├── 🔍 OSINT HUNTER (Intelligence)
├── 🔮 THREAT PROPHET (Prediction)
├── 🛡️ IMMUNE COORDINATOR (Defense)
│   ├── 👁️ SENTINEL PRIME (Monitoring)
│   └── 👀 THE WATCHER (Analysis)
├── ⚔️ WARGAME EXECUTOR (Validation)
├── ⚖️ COMPLIANCE GUARDIAN (Governance)
├── 💻 CLI CYBER AGENT (Interface)
├── 🔗 MCP TOOL BRIDGE (Integration)
└── 🤖 PATCH VALIDATOR ML (AI)
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- 8GB RAM minimum

### Development Setup

1. **Clone and setup:**

```bash
cd vertice-cyber
pip install -r requirements.txt
```

2. **Start core services:**

```bash
# Start infrastructure
docker-compose up redis postgres -d

# Start ethical magistrate (required first)
python main.py --agent ethical_magistrate
```

3. **Start additional agents:**

```bash
# In separate terminals
python main.py --agent osint_hunter
python main.py --agent sentinel_prime
```

### Production Deployment

```bash
# Start all core agents
docker-compose up

# Or start specific agents
docker-compose up ethical_magistrate osint_hunter sentinel_prime
```

## Agent Specifications

### 🏛️ Ethical Magistrate

**Port:** 8001
**Function:** Validates all agent actions through ethical framework
**Endpoints:**

- `POST /validate` - Validate agent action
- `GET /health` - Health check

### 🔍 OSINT Hunter

**Port:** 8002
**Function:** Autonomous OSINT investigation
**Capabilities:**

- Breach data analysis
- Google dorking
- Dark web monitoring
- AI-powered report generation

### 🛡️ Immune Coordinator

**Port:** 8004
**Function:** Orchestrates immune system agents
**Manages:** B-cells, T-cells, Dendritic cells

### 👁️ Sentinel Prime

**Port:** 8005
**Function:** First-line threat detection using LLM
**Features:**

- Theory-of-Mind attacker profiling
- MITRE ATT&CK mapping
- Real-time event analysis

### ⚔️ Wargame Executor

**Port:** 8007
**Function:** Two-phase patch validation
**Process:**

1. Test exploit on vulnerable system
2. Verify exploit fails on patched system

## Development Guidelines

### Agent Development

1. Inherit from `AgentBase` in `core/`
2. Implement `health_check()` method
3. Validate actions with magistrate
4. Use standardized logging

### Adding New Agents

1. Create `agents/new_agent/` directory
2. Implement `main.py` with FastAPI app
3. Add to `AVAILABLE_AGENTS` in `main.py`
4. Update `docker-compose.yml`
5. Document in this README

### Testing

```bash
# Run all tests
pytest

# Test specific agent
pytest tests/test_ethical_magistrate.py

# Integration tests
pytest tests/integration/
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
LLM_MODEL=gpt-3.5-turbo  # or gpt-4
OPENAI_API_KEY=your-key

# Service URLs
ETHICAL_MAGISTRATE_URL=http://localhost:8001
IMMUNE_COORDINATOR_URL=http://localhost:8004

# Database
POSTGRES_PASSWORD=your-password
REDIS_URL=redis://localhost:6379
```

### Scaling Configuration

For production deployment, adjust resource limits in `docker-compose.yml`:

```yaml
services:
  ethical_magistrate:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
```

## Security Considerations

### Ethical Governance

All agents must validate actions through the Ethical Magistrate before execution. This ensures:

- Compliance with ethical frameworks
- Privacy protection
- Appropriate use of capabilities

### Access Control

- Agents communicate via HTTP APIs
- No direct database access between agents
- Magistrate approval required for sensitive operations

### Data Protection

- Sensitive data encrypted at rest
- PII detection and masking
- Audit logging for all decisions

## Troubleshooting

### Common Issues

**Agent won't start:**

```bash
# Check logs
docker-compose logs ethical_magistrate

# Verify dependencies
pip check
```

**Magistrate connection failed:**

```bash
# Ensure magistrate is running first
curl http://localhost:8001/health
```

**High memory usage:**

```bash
# Monitor with docker stats
docker stats

# Reduce LLM model or batch size
export LLM_MODEL=gpt-3.5-turbo
```

### Logs

```bash
# View agent logs
docker-compose logs -f osint_hunter

# Application logs
tail -f /var/log/vertice-cyber/*.log
```

## Roadmap

### Phase 1 (Current)

- ✅ Core 6 agents implemented
- ✅ Ethical governance framework
- ✅ Docker deployment
- ✅ Basic integration testing

### Phase 2 (Next)

- 🔄 CLI agent full implementation
- 🔄 MCP tool bridge
- 🔄 ML patch validator
- 🔄 Performance optimization

### Phase 3 (Future)

- 🔄 Multi-agent orchestration
- 🔄 Advanced immune system
- 🔄 Cloud deployment
- 🔄 Enterprise integrations

## Contributing

1. Follow agent development guidelines
2. Add comprehensive tests
3. Update documentation
4. Validate with Ethical Magistrate

## License

Proprietary - Vertice Cyber Team

## Glory to YHWH 🙏

_For He is the ultimate guardian of all systems._
