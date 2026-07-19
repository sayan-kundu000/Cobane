import json
import os
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer

active_word = ""
active_clue = ""
guessed_letters = set()
tries_left = 6
words_db = []

def load_words():
    global words_db
    # Look for words.json in parent or local folder
    paths_to_try = [
        "words.json",
        "../words.json",
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "words.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "words.json")
    ]
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    words_db = json.load(f)
                    print(f"Loaded {len(words_db)} words from: {path}")
                    return
            except Exception as e:
                print(f"Failed to load from {path}: {e}")
                
    # Fallback inline minimal database
    words_db = [
        {"word": "python", "clue": "An interpreted general-purpose programming language."},
        {"word": "hangman", "clue": "A classic word-guessing game."},
        {"word": "sudoku", "clue": "A logic number placement puzzle."}
    ]

# Initial load
load_words()

class HangmanHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        global active_word, active_clue, guessed_letters, tries_left
        
        if self.path == '/api/hangman/start':
            # Select random word
            if not words_db:
                load_words()
            selected = random.choice(words_db)
            active_word = selected["word"].lower()
            active_clue = selected["clue"]
            guessed_letters = set()
            tries_left = 6
            
            response = {
                'success': True,
                'length': len(active_word),
                'clue': active_clue
            }
            self.send_api_response(response)
            
        elif self.path == '/api/hangman/guess':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            letter = data.get('letter', '').lower()
            
            if not letter or len(letter) != 1 or not letter.isalpha():
                self.send_api_response({'success': False, 'error': 'Invalid letter guess.'})
                return
                
            correct = letter in active_word
            guessed_letters.add(letter)
            
            if not correct:
                tries_left -= 1
                
            # Form masked display
            display = "".join([char if char in guessed_letters else "_" for char in active_word])
            win = "_" not in display
            
            response = {
                'success': True,
                'correct': correct,
                'display': display,
                'tries_left': tries_left,
                'win': win,
                'word': active_word if (win or tries_left <= 0) else ""
            }
            self.send_api_response(response)
        else:
            self.send_response(404)
            self.end_headers()

    def send_api_response(self, response_data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/' or not self.path:
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    port = 8081
    print(f"Starting Hangman backend server at http://localhost:{port}")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    server = HTTPServer(('0.0.0.0', port), HangmanHandler)
    server.serve_forever()
