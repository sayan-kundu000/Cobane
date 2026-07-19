import json
import os
import random
from http.server import SimpleHTTPRequestHandler, HTTPServer

def is_valid(board, r, c, num):
    # Check row
    for col in range(9):
        if board[r][col] == num and col != c:
            return False
    # Check col
    for row in range(9):
        if board[row][c] == num and row != r:
            return False
    # Check 3x3 block
    start_row, start_col = 3 * (r // 3), 3 * (c // 3)
    for i in range(3):
        for j in range(3):
            curr_r, curr_c = start_row + i, start_col + j
            if board[curr_r][curr_c] == num and (curr_r != r or curr_c != c):
                return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for num in range(1, 10):
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True

def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    def fill(b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(b, r, c, num):
                            b[r][c] = num
                            if fill(b):
                                return True
                            b[r][c] = 0
                    return False
        return True
    fill(board)
    return board

def generate_puzzle(difficulty):
    board = generate_full_board()
    # Remove cells based on difficulty
    cells_to_remove = {
        'easy': 30,
        'medium': 45,
        'hard': 55
    }.get(difficulty, 40)

    puzzle = [row[:] for row in board]
    indices = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(indices)

    for i in range(cells_to_remove):
        r, c = indices[i]
        puzzle[r][c] = 0

    return puzzle

class SudokuHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/sudoku/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            difficulty = data.get('difficulty', 'easy')

            try:
                puzzle = generate_puzzle(difficulty)
                response = {'success': True, 'board': puzzle}
            except Exception as e:
                response = {'success': False, 'error': str(e)}

            self.send_api_response(response)

        elif self.path == '/api/sudoku/solve':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            board = data.get('board', [])

            try:
                board_copy = [row[:] for row in board]
                if solve(board_copy):
                    response = {'success': True, 'solution': board_copy}
                else:
                    response = {'success': False, 'error': 'No solution exists.'}
            except Exception as e:
                response = {'success': False, 'error': str(e)}

            self.send_api_response(response)

        elif self.path == '/api/sudoku/validate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            board = data.get('board', [])

            try:
                valid = True
                conflicts = []
                for r in range(9):
                    for c in range(9):
                        num = board[r][c]
                        if num != 0:
                            if not is_valid(board, r, c, num):
                                valid = False
                                conflicts.append([r, c])
                response = {'success': True, 'valid': valid, 'conflicts': conflicts}
            except Exception as e:
                response = {'success': False, 'error': str(e)}

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
    port = 8080
    print(f"Starting Sudoku backend server at http://localhost:{port}")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)
    server = HTTPServer(('0.0.0.0', port), SudokuHandler)
    server.serve_forever()
