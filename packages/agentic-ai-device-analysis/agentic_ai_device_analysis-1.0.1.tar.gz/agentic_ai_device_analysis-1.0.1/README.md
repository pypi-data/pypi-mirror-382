# Agentic AI Device Attributes Analysis Demo

A comprehensive demonstration of an Agentic AI system for device behavior analysis and fraud prevention. This package provides an interactive web-based demo that showcases how AI agents can analyze device attributes to detect suspicious behavior and potential fraud.

## Features

- **Interactive Web Interface**: Clean, modern UI for device analysis demonstration
- **Real-time Analysis**: Simulated AI-powered device attribute analysis
- **Multiple Risk Levels**: Supports normal, suspicious, and fraudulent device scenarios
- **Agentic AI Simulation**: Demonstrates multi-agent decision-making processes
- **Zero Dependencies**: Uses only Python standard library for maximum compatibility
- **Easy Deployment**: Simple installation and deployment options

## Installation

### From PyPI (when published)
```bash
pip install agentic-ai-device-analysis
```

### From Source
```bash
git clone https://github.com/deviceanalysis/agentic-ai-device-analysis.git
cd agentic-ai-device-analysis
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/deviceanalysis/agentic-ai-device-analysis.git
cd agentic-ai-device-analysis
pip install -e ".[dev]"
```

## Quick Start

### Command Line
After installation, you can start the demo server using:

```bash
# Using the main command
agentic-demo

# Alternative command
device-analysis-demo

# With custom host and port
agentic-demo --host 0.0.0.0 --port 8080
```

### Python Module
```bash
# Run as module
python -m agentic_ai_demo

# With arguments
python -m agentic_ai_demo --host localhost --port 8000
```

### Direct Script Execution
```bash
python agentic_ai_demo/server.py
```

## Usage

1. Start the server using any of the methods above
2. Open your web browser and navigate to `http://localhost:8000`
3. Use the interactive interface to analyze different device scenarios:
   - **Normal Device**: Simulates a legitimate user device
   - **Suspicious Device**: Shows elevated risk indicators
   - **Fraudulent Device**: Demonstrates high-risk fraud patterns

## API Endpoints

- `GET /` - Main demo interface
- `GET /api/analyze?type={normal|suspicious|fraud}` - Device analysis API
- `GET /health` - Health check endpoint

## Demo Features

### Device Analysis Types

1. **Normal Device Analysis**
   - Low risk score (0.1-0.3)
   - Standard device fingerprinting
   - Typical user behavior patterns

2. **Suspicious Device Analysis**
   - Medium risk score (0.4-0.7)
   - Anomalous behavior detection
   - Enhanced monitoring recommendations

3. **Fraudulent Device Analysis**
   - High risk score (0.8-0.95)
   - Multiple fraud indicators
   - Immediate action recommendations

### AI Agent Simulation

The demo simulates various AI agents working together:
- **Device Fingerprint Agent**: Analyzes hardware and software characteristics
- **Behavior Analysis Agent**: Monitors user interaction patterns
- **Risk Assessment Agent**: Calculates overall fraud probability
- **Decision Engine**: Coordinates agent findings and recommendations

## Architecture
