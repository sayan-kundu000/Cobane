let displayValue = '0';
let historyValue = '';
let isNewCalculation = false;

const displayEl = document.getElementById('display');
const historyEl = document.getElementById('history');
const statusEl = document.getElementById('connection-status');
const pulseEl = document.querySelector('.pulse-dot');

const BACKEND_URL = ''; // Relative path since we serve statically

// Check connectivity on load
async function checkBackendConnection() {
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression: '0', operation: 'eval' })
        });
        if (response.ok) {
            statusEl.textContent = 'Backend Connected';
            statusEl.style.color = '#00e5ff';
            pulseEl.style.backgroundColor = '#00e5ff';
            pulseEl.style.boxShadow = '0 0 8px #00e5ff';
        } else {
            throw new Error();
        }
    } catch (e) {
        statusEl.textContent = 'Offline Mode (Local Eval)';
        statusEl.style.color = '#ff1744';
        pulseEl.style.backgroundColor = '#ff1744';
        pulseEl.style.boxShadow = '0 0 8px #ff1744';
    }
}

function updateDisplay() {
    displayEl.textContent = displayValue;
    historyEl.textContent = historyValue;
}

function clearDisplay() {
    displayValue = '0';
    historyValue = '';
    isNewCalculation = false;
    updateDisplay();
}

function deleteChar() {
    if (isNewCalculation) {
        clearDisplay();
        return;
    }
    if (displayValue.length > 1) {
        displayValue = displayValue.slice(0, -1);
    } else {
        displayValue = '0';
    }
    updateDisplay();
}

function appendValue(val) {
    if (isNewCalculation) {
        displayValue = '';
        isNewCalculation = false;
    }
    if (displayValue === '0' && val !== '.') {
        displayValue = val;
    } else {
        displayValue += val;
    }
    updateDisplay();
}

function appendOperator(op) {
    if (isNewCalculation) {
        isNewCalculation = false;
    }
    const lastChar = displayValue.slice(-1);
    const operators = ['+', '-', '*', '/'];
    
    if (operators.includes(lastChar)) {
        displayValue = displayValue.slice(0, -1) + op;
    } else {
        displayValue += op;
    }
    updateDisplay();
}

// Handles single value scientific operations sent directly to python backend
async function handleSciOp(op) {
    historyValue = `${op}(${displayValue})`;
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression: displayValue, operation: op })
        });
        const data = await response.json();
        if (data.success) {
            displayValue = String(data.result);
            isNewCalculation = true;
        } else {
            displayValue = 'Error';
            console.error(data.error);
        }
    } catch (err) {
        // Fallback local eval for offline mode
        try {
            const num = parseFloat(displayValue);
            let result;
            if (op === 'sin') result = Math.sin(num * Math.PI / 180);
            else if (op === 'cos') result = Math.cos(num * Math.PI / 180);
            else if (op === 'tan') result = Math.tan(num * Math.PI / 180);
            else if (op === 'sqrt') result = Math.sqrt(num);
            else if (op === 'log') result = Math.log10(num);
            else if (op === 'ln') result = Math.log(num);
            else if (op === 'exp') result = Math.exp(num);
            else if (op === 'fact') result = factorial(num);
            
            displayValue = String(Number(result.toFixed(10)));
            isNewCalculation = true;
        } catch (e) {
            displayValue = 'Error';
        }
    }
    updateDisplay();
}

function factorial(n) {
    if (n < 0) return NaN;
    if (n === 0 || n === 1) return 1;
    let res = 1;
    for (let i = 2; i <= n; i++) res *= i;
    return res;
}

// Evaluates general expressions containing numbers & operators via API or local fallback
async function evaluateExpression() {
    if (displayValue === '0' || !displayValue) return;
    
    historyValue = displayValue + ' =';
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression: displayValue, operation: 'eval' })
        });
        const data = await response.json();
        if (data.success) {
            displayValue = String(data.result);
            isNewCalculation = true;
        } else {
            displayValue = 'Error';
            console.error(data.error);
        }
    } catch (err) {
        // Fallback standard JS eval in offline mode
        try {
            // Replace visual representation with evaluatable math chars
            let cleanExpr = displayValue.replace(/π/g, Math.PI).replace(/e/g, Math.E);
            let result = eval(cleanExpr);
            displayValue = String(Number(result.toFixed(10)));
            isNewCalculation = true;
        } catch (e) {
            displayValue = 'Error';
        }
    }
    updateDisplay();
}

// Initial connection probe
checkBackendConnection();
updateDisplay();
