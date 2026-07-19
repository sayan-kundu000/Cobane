import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import numpy as np
import sympy

class CalculatorHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/calculate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            expression = data.get('expression', '')
            operation = data.get('operation', 'eval')
            
            try:
                result = None
                if operation == 'eval':
                    # Safe arithmetic evaluation using SymPy
                    allowed_chars = set("0123456789+-*/(). ")
                    # Replace visual representations of constants for SymPy
                    clean_expr = expression.replace('π', 'pi').replace('e', 'E')
                    # Validation: check layout characters against float representation
                    check_expr = expression.replace('π', '3.141592653589793').replace('e', '2.718281828459045')
                    if all(c in allowed_chars for c in check_expr):
                        expr = sympy.sympify(clean_expr)
                        result = float(expr.evalf())
                    else:
                        raise ValueError("Forbidden characters in expression.")
                elif operation == 'sin':
                    result = float(np.sin(np.radians(float(expression))))
                elif operation == 'cos':
                    result = float(np.cos(np.radians(float(expression))))
                elif operation == 'tan':
                    result = float(np.tan(np.radians(float(expression))))
                elif operation == 'sqrt':
                    val = float(expression)
                    if val < 0:
                        raise ValueError("Negative square root.")
                    result = float(np.sqrt(val))
                elif operation == 'log':
                    val = float(expression)
                    if val <= 0:
                        raise ValueError("Non-positive logarithm.")
                    result = float(np.log10(val))
                elif operation == 'ln':
                    val = float(expression)
                    if val <= 0:
                        raise ValueError("Non-positive natural logarithm.")
                    result = float(np.log(val))
                elif operation == 'exp':
                    result = float(np.exp(float(expression)))
                elif operation == 'fact':
                    val = int(float(expression))
                    if val < 0:
                        raise ValueError("Negative factorial.")
                    result = int(sympy.factorial(val))
                else:
                    raise ValueError("Unknown operation.")
                
                # Format to avoid floating point anomalies (e.g. 1.0000000000000002)
                if isinstance(result, float):
                    result = round(result, 10)
                
                response = {'success': True, 'result': result}
            except Exception as e:
                response = {'success': False, 'error': str(e)}
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Redirect default base requests to serve index.html from workspace
        if self.path == '/' or not self.path:
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    port = 8082
    print(f"Starting scientific calculator backend server at http://localhost:{port}")
    # Change working directory to directory containing this script to serve local static files correctly
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    server = HTTPServer(('0.0.0.0', port), CalculatorHandler)
    server.serve_forever()
