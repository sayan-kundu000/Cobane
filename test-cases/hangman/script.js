const API_URL = 'http://localhost:8081/api';
let tries = 6;
let wrongLetters = [];
let gameActive = false;

const gallowsStages = [
`  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========`,
`  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========`,
`  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========`,
`  +---+
  |   |
  O   |
 /|   |
      |
      |
=========`,
`  +---+
  |   |
  O   |
  |   |
      |
      |
=========`,
`  +---+
  |   |
  O   |
      |
      |
      |
=========`,
`  +---+
  |   |
      |
      |
      |
      |
=========`,
];

document.addEventListener('DOMContentLoaded', () => {
    buildKeyboard();
    checkBackendConnection();
});

function buildKeyboard() {
    const kb = document.getElementById('keyboard');
    kb.innerHTML = '';
    
    const letters = 'abcdefghijklmnopqrstuvwxyz'.split('');
    letters.forEach(char => {
        const key = document.createElement('button');
        key.className = 'key';
        key.innerText = char;
        key.id = `key-${char}`;
        key.disabled = true;
        key.onclick = () => makeGuess(char);
        kb.appendChild(key);
    });
}

async function checkBackendConnection() {
    const statusText = document.getElementById('connection-status');
    const pulseDot = document.querySelector('.pulse-dot');
    
    try {
        const res = await fetch(`${API_URL}/hangman/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
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

function updateVisuals(triesLeft) {
    document.getElementById('tries-left').innerText = triesLeft;
    document.getElementById('wrong-letters').innerText = wrongLetters.length > 0 ? wrongLetters.join(', ').toUpperCase() : '-';
    
    const gallows = document.getElementById('gallows');
    gallows.innerText = gallowsStages[triesLeft];
}

async function startNewSession() {
    wrongLetters = [];
    tries = 6;
    gameActive = true;
    updateVisuals(tries);
    
    // Reset keys
    document.querySelectorAll('.key').forEach(key => {
        key.disabled = false;
        key.className = 'key';
    });
    
    document.getElementById('clue-text').innerText = 'Loading clues...';
    document.getElementById('word-display').innerText = '_ _ _ _ _';
    
    try {
        const res = await fetch(`${API_URL}/hangman/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('clue-text').innerText = data.clue;
            
            const display = Array(data.length).fill('_').join(' ');
            document.getElementById('word-display').innerText = display;
        } else {
            throw new Error(data.error || 'Server error.');
        }
    } catch (e) {
        document.getElementById('clue-text').innerText = 'Offline backup loaded: An interpreted general-purpose programming language.';
        document.getElementById('word-display').innerText = '_ _ _ _ _ _';
        gameActive = false;
        document.querySelectorAll('.key').forEach(key => key.disabled = true);
    }
}

async function makeGuess(char) {
    if (!gameActive) return;
    
    const key = document.getElementById(`key-${char}`);
    key.disabled = true;
    
    try {
        const res = await fetch(`${API_URL}/hangman/guess`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ letter: char })
        });
        const data = await res.json();
        
        if (data.success) {
            // Update display
            const display = data.display.split('').join(' ');
            document.getElementById('word-display').innerText = display;
            
            if (data.correct) {
                key.classList.add('correct');
            } else {
                key.classList.add('incorrect');
                wrongLetters.push(char);
                tries = data.tries_left;
                updateVisuals(tries);
            }
            
            // Check win/loss
            if (data.win) {
                document.getElementById('clue-text').innerText = 'CONGRATULATIONS! Matrix decrypted successfully!';
                gameActive = false;
                document.querySelectorAll('.key').forEach(k => k.disabled = true);
            } else if (data.tries_left <= 0) {
                document.getElementById('clue-text').innerText = `DECRYPTION FAILURE! The correct pattern word was: "${data.word.toUpperCase()}"`;
                gameActive = false;
                document.querySelectorAll('.key').forEach(k => k.disabled = true);
            }
        } else {
            throw new Error(data.error || 'Guess processing failed.');
        }
    } catch (e) {
        console.error(e);
    }
}
