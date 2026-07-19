const API_URL = 'http://localhost:8080/api';
let selectedDifficulty = 'easy';

document.addEventListener('DOMContentLoaded', () => {
    buildGrid();
    checkBackendConnection();
});

function buildGrid() {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const cell = document.createElement('div');
            cell.className = 'sudoku-cell';
            
            // Add right border thick separator
            if (c === 2 || c === 5) {
                cell.classList.add('border-right');
            }
            // Add bottom border thick separator
            if (r === 2 || r === 5) {
                cell.classList.add('border-bottom');
            }

            const input = document.createElement('input');
            input.type = 'text';
            input.maxLength = 1;
            input.id = `cell-${r}-${c}`;
            
            // Key validations (only digits 1-9)
            input.addEventListener('input', (e) => {
                const val = e.target.value;
                if (!/^[1-9]$/.test(val)) {
                    e.target.value = '';
                }
                cell.classList.remove('error');
            });

            cell.appendChild(input);
            grid.appendChild(cell);
        }
    }
}

async function checkBackendConnection() {
    const statusText = document.getElementById('connection-status');
    const pulseDot = document.querySelector('.pulse-dot');
    
    try {
        const res = await fetch(`${API_URL}/sudoku/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: Array(9).fill(null).map(() => Array(9).fill(0)) })
        });
        
        if (res.ok) {
            statusText.innerText = 'Backend Active';
            statusText.style.color = '#10b981';
            pulseDot.style.backgroundColor = '#10b981';
        } else {
            throw new Error('Connection active but error returned.');
        }
    } catch (e) {
        statusText.innerText = 'Offline Mode (Mock)';
        statusText.style.color = '#f59e0b';
        pulseDot.style.backgroundColor = '#f59e0b';
    }
}

function selectDifficulty(diff) {
    selectedDifficulty = diff;
    document.querySelectorAll('.btn-diff').forEach(btn => {
        if (btn.getAttribute('data-difficulty') === diff) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    logStatus(`Selected difficulty: ${diff.toUpperCase()}`);
}

function logStatus(msg, type = 'info') {
    const console = document.getElementById('status-message');
    console.innerText = msg;
    if (type === 'error') {
        console.style.color = '#fca5a5';
    } else if (type === 'success') {
        console.style.color = '#6ee7b7';
    } else {
        console.style.color = '#38bdf8';
    }
}

function getBoardState() {
    const board = [];
    for (let r = 0; r < 9; r++) {
        const row = [];
        for (let c = 0; c < 9; c++) {
            const input = document.getElementById(`cell-${r}-${c}`);
            const val = input.value;
            row.push(val ? parseInt(val) : 0);
        }
        board.push(row);
    }
    return board;
}

function setBoardState(board, lockGiven = false) {
    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const input = document.getElementById(`cell-${r}-${c}`);
            const val = board[r][c];
            input.value = val !== 0 ? val : '';
            
            if (lockGiven) {
                if (val !== 0) {
                    input.disabled = true;
                } else {
                    input.disabled = false;
                }
            } else {
                input.disabled = false;
            }
            input.parentElement.classList.remove('error');
        }
    }
}

function clearBoard() {
    buildGrid();
    logStatus('Board cells reset to initial state.');
}

async function generateBoard() {
    logStatus('Generating new puzzle matrix from server...');
    try {
        const res = await fetch(`${API_URL}/sudoku/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty: selectedDifficulty })
        });
        const data = await res.json();
        
        if (data.success && data.board) {
            setBoardState(data.board, true);
            logStatus(`New ${selectedDifficulty.toUpperCase()} puzzle loaded. blue cells are locked clues!`, 'success');
        } else {
            throw new Error(data.error || 'Server error.');
        }
    } catch (e) {
        logStatus(`Generation failed: ${e.message}. Using offline backup.`, 'error');
        // Offline mock generator fallback
        const mockBoard = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ];
        setBoardState(mockBoard, true);
    }
}

async function validateBoard() {
    logStatus('Validating current matrix cell placements...');
    const board = getBoardState();
    
    try {
        const res = await fetch(`${API_URL}/sudoku/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board })
        });
        const data = await res.json();
        
        if (data.success) {
            if (data.valid) {
                logStatus('Board is VALID! Keep going or trigger solve helper.', 'success');
            } else {
                logStatus('Board is INVALID! Detections found conflicts in rows, columns, or 3x3 grids.', 'error');
                highlightConflicts(data.conflicts || []);
            }
        } else {
            throw new Error(data.error || 'Server error.');
        }
    } catch (e) {
        logStatus(`Validation failed: ${e.message}.`, 'error');
    }
}

function highlightConflicts(conflicts) {
    conflicts.forEach(([r, c]) => {
        const input = document.getElementById(`cell-${r}-${c}`);
        if (input) {
            input.parentElement.classList.add('error');
        }
    });
}

async function solveBoard() {
    logStatus('Triggering quantum solver thread...');
    const board = getBoardState();
    
    try {
        const res = await fetch(`${API_URL}/sudoku/solve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board })
        });
        const data = await res.json();
        
        if (data.success && data.solution) {
            setBoardState(data.solution, false);
            logStatus('Backtracking algorithm completed. Puzzle SOLVED successfully!', 'success');
        } else {
            throw new Error(data.error || 'No solution exists for this matrix.');
        }
    } catch (e) {
        logStatus(`Solver failed: ${e.message}`, 'error');
    }
}
