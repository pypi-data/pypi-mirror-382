# Deployment Guide

## Package Installation

### From Source
```bash
# Clone or download the source code
cd DeviceBehaviorAnalysis
pip install -e .
```

### From Built Package
```bash
# Build the package
python setup.py sdist bdist_wheel

# Install the built package
pip install dist/agentic-ai-device-analysis-1.0.0.tar.gz
```

## Running the Application

### Command Line
```bash
# Run with default settings (localhost:8000)
agentic-demo

# Run with custom host and port
agentic-demo --host 0.0.0.0 --port 8080
```

### Programmatic Usage
```python
from agentic_ai_demo import AgenticDemoServer

# Create and start server
server = AgenticDemoServer(host='0.0.0.0', port=8080)
server.start()
```

## Deployment Options

### 1. Local Development
```bash
agentic-demo
```

### 2. Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["agentic-demo", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t agentic-ai-demo .
docker run -p 8000:8000 agentic-ai-demo
```

### 3. Cloud Deployment

#### Heroku
Create `Procfile`: