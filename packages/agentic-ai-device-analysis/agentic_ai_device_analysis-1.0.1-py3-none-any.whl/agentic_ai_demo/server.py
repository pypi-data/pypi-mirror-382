"""
Agentic AI Demo Server - Deployable version
"""
import json
import random
import time
import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

class AgenticDemoHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/' or path == '/index.html':
            self.serve_demo_page()
        elif path.startswith('/api/analyze'):
            self.serve_analysis()
        elif path == '/health':
            self.serve_health()
        elif path == '/favicon.ico':
            # Handle favicon request
            self.send_response(404)
            self.end_headers()
        else:
            # For any other requests, return 404
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def serve_demo_page(self):
        # Try to load template from file system first
        template_paths = [
            os.path.join(os.path.dirname(__file__), 'templates', 'index.html'),
            os.path.join(os.getcwd(), 'agentic_ai_demo', 'templates', 'index.html'),
            os.path.join(os.getcwd(), 'templates', 'index.html')
        ]
        
        html_content = None
        for template_path in template_paths:
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    break
                except Exception as e:
                    print(f"Error loading template from {template_path}: {e}")
                    continue
        
        # Fallback to embedded template
        if html_content is None:
            html_content = self._get_embedded_template()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def _get_embedded_template(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic AI based Device Attributes Analysis Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .risk-low { background: linear-gradient(135deg, #4ade80, #22c55e); }
        .risk-medium { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
        .risk-high { background: linear-gradient(135deg, #f87171, #ef4444); }
        .pulse-animation { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body class="bg-gray-100">
    <div class="min-h-screen gradient-bg">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold text-white text-center mb-8">🤖 Agentic AI based Device Attributes Analysis Demo</h1>
            
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Device Analysis Panel -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-2xl font-bold mb-4">Device Analysis</h2>
                    <div class="space-y-4">
                        <button onclick="analyzeDevice('normal')" class="w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600">
                            Analyze Normal Device
                        </button>
                        <button onclick="analyzeDevice('suspicious')" class="w-full bg-yellow-500 text-white py-2 px-4 rounded hover:bg-yellow-600">
                            Analyze Suspicious Device
                        </button>
                        <button onclick="analyzeDevice('fraud')" class="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600">
                            Analyze Fraudulent Device
                        </button>
                    </div>
                </div>
                
                <!-- Results Panel -->
                <div class="bg-white rounded-lg shadow-lg p-6">
                    <h2 class="text-2xl font-bold mb-4">Analysis Results</h2>
                    <div id="results" class="space-y-4">
                        <p class="text-gray-500">Click a button to start analysis...</p>
                    </div>
                </div>
            </div>
            
            <!-- AI Decision Process -->
            <div class="mt-8 bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold mb-4">🧠 AI Decision Process</h2>
                <div id="aiProcess" class="space-y-2">
                    <p class="text-gray-500">AI reasoning will appear here...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function analyzeDevice(type) {
            const resultsDiv = document.getElementById('results');
            const processDiv = document.getElementById('aiProcess');
            
            // Show loading
            resultsDiv.innerHTML = '<div class="pulse-animation">🔄 Analyzing device...</div>';
            processDiv.innerHTML = '<div class="pulse-animation">🧠 AI is thinking...</div>';
            
            try {
                console.log('Making request to:', `/api/analyze?type=${type}`);
                const response = await fetch(`/api/analyze?type=${type}`);
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                console.log('Response data:', data);
                
                // Display results
                const riskClass = data.risk_level === 'LOW' ? 'risk-low' : 
                                 data.risk_level === 'MEDIUM' ? 'risk-medium' : 'risk-high';
                
                resultsDiv.innerHTML = `
                    <div class="${riskClass} text-white p-4 rounded">
                        <h3 class="font-bold">Risk Level: ${data.risk_level}</h3>
                        <p>Score: ${data.risk_score}%</p>
                    </div>
                    <div class="mt-4">
                        <h4 class="font-bold">Anomalies Detected:</h4>
                        <ul class="list-disc list-inside">
                            ${data.anomalies.map(a => `<li>${a.type}: ${a.description}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="mt-4">
                        <h4 class="font-bold">AI Recommendations:</h4>
                        <ul class="list-disc list-inside">
                            ${data.recommendations.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                `;
                
                // Display AI process
                processDiv.innerHTML = `
                    <div class="space-y-2">
                        ${data.ai_reasoning.map(step => `
                            <div class="bg-blue-50 p-2 rounded">
                                <strong>${step.step}:</strong> ${step.reasoning}
                            </div>
                        `).join('')}
                    </div>
                `;
                
            } catch (error) {
                console.error('Error:', error);
                resultsDiv.innerHTML = `<div class="text-red-500">Error: ${error.message}</div>`;
                processDiv.innerHTML = '<div class="text-red-500">AI process failed</div>';
            }
        }
    </script>
</body>
</html>
        """
    
    def serve_analysis(self):
        try:
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            analysis_type = query_params.get('type', ['normal'])[0]
            
            print(f"Processing analysis request for type: {analysis_type}")
            
            # Simulate AI analysis based on type
            if analysis_type == 'normal':
                result = {
                    "risk_level": "LOW",
                    "risk_score": random.randint(5, 25),
                    "anomalies": [
                        {"type": "Device Fingerprint", "description": "Consistent with user history"},
                        {"type": "Behavioral Pattern", "description": "Normal interaction patterns"}
                    ],
                    "recommendations": [
                        "Continue monitoring",
                        "No additional verification needed"
                    ],
                    "ai_reasoning": [
                        {"step": "Device Analysis", "reasoning": "Device fingerprint matches historical patterns"},
                        {"step": "Behavior Assessment", "reasoning": "User behavior consistent with profile"},
                        {"step": "Risk Calculation", "reasoning": "Low anomaly score indicates legitimate user"}
                    ]
                }
            elif analysis_type == 'suspicious':
                result = {
                    "risk_level": "MEDIUM",
                    "risk_score": random.randint(40, 70),
                    "anomalies": [
                        {"type": "Location Change", "description": "Unusual geographic location"},
                        {"type": "Device Mismatch", "description": "New device characteristics detected"}
                    ],
                    "recommendations": [
                        "Request additional verification",
                        "Monitor closely for 24 hours",
                        "Consider step-up authentication"
                    ],
                    "ai_reasoning": [
                        {"step": "Anomaly Detection", "reasoning": "Multiple suspicious indicators detected"},
                        {"step": "Pattern Analysis", "reasoning": "Deviation from established user patterns"},
                        {"step": "Risk Assessment", "reasoning": "Medium risk requires additional verification"}
                    ]
                }
            else:  # fraud
                result = {
                    "risk_level": "HIGH",
                    "risk_score": random.randint(80, 95),
                    "anomalies": [
                        {"type": "Device Spoofing", "description": "Potential device fingerprint manipulation"},
                        {"type": "Behavioral Anomaly", "description": "Highly unusual interaction patterns"},
                        {"type": "Velocity Check", "description": "Impossible travel time between locations"}
                    ],
                    "recommendations": [
                        "Block transaction immediately",
                        "Require manual review",
                        "Contact user through verified channel",
                        "Update fraud models with new patterns"
                    ],
                    "ai_reasoning": [
                        {"step": "Fraud Detection", "reasoning": "Multiple high-risk indicators present"},
                        {"step": "Pattern Matching", "reasoning": "Matches known fraudulent behavior patterns"},
                        {"step": "Decision Engine", "reasoning": "High confidence fraud detection - immediate action required"}
                    ]
                }
            
            print(f"Sending response: {result}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Error in serve_analysis: {e}")
            error_response = {"error": str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def serve_health(self):
        result = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


class AgenticDemoServer:
    """Main server class for the Agentic AI Demo"""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.server = None
    
    def start(self):
        """Start the demo server"""
        self.server = HTTPServer((self.host, self.port), AgenticDemoHandler)
        print(f"🚀 Starting Agentic AI Device Analysis Demo Server...")
        print(f"📊 Demo available at: http://{self.host}:{self.port}")
        print(f"🔍 Features:")
        print(f"   • Device analysis simulation")
        print(f"   • Risk assessment visualization") 
        print(f"   • AI decision process tracking")
        print(f"   • Interactive fraud scenarios")
        print(f"\n✅ No external dependencies required!")
        print(f"Press Ctrl+C to stop the server")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            self.stop()
    
    def stop(self):
        """Stop the demo server"""
        if self.server:
            self.server.shutdown()
            self.server = None


def main():
    """Main entry point for the console script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agentic AI Device Attributes Analysis Demo')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    
    args = parser.parse_args()
    
    server = AgenticDemoServer(host=args.host, port=args.port)
    server.start()


if __name__ == "__main__":
    main()