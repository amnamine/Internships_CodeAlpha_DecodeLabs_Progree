/**
 * QuantumCalc - Client-side state, safe expression parsing, and interaction logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const displayExpr = document.getElementById('displayExpr');
    const displayInput = document.getElementById('displayInput');
    const scientificPanel = document.getElementById('scientificPanel');
    const sciToggleBtn = document.getElementById('sciToggleBtn');
    const historyDrawer = document.getElementById('historyDrawer');
    const historyToggleBtn = document.getElementById('historyToggleBtn');
    const historyCloseBtn = document.getElementById('historyCloseBtn');
    const historyContent = document.getElementById('historyContent');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const themeSelectorBtn = document.getElementById('themeSelectorBtn');
    
    // --- State Variables ---
    let currentInput = '0';
    let isResultCalculated = false;
    let history = JSON.parse(localStorage.getItem('calc_history') || '[]');

    // --- Active Theme Initialization ---
    const themes = ['aurora', 'solar', 'cyberpunk'];
    let currentThemeIndex = themes.indexOf(localStorage.getItem('calc_theme') || 'aurora');
    if (currentThemeIndex === -1) currentThemeIndex = 0;
    setTheme(themes[currentThemeIndex]);

    // --- Init UI ---
    updateDisplay();
    renderHistory();

    // ==========================================================================
    // THEME SELECTION LOGIC
    // ==========================================================================
    themeSelectorBtn.addEventListener('click', (e) => {
        currentThemeIndex = (currentThemeIndex + 1) % themes.length;
        const nextTheme = themes[currentThemeIndex];
        setTheme(nextTheme);
    });

    function setTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        localStorage.setItem('calc_theme', themeName);
        
        // Update visual checkmark on theme options
        document.querySelectorAll('.theme-option').forEach(opt => {
            if (opt.getAttribute('data-theme') === themeName) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });
    }

    // ==========================================================================
    // SCIENTIFIC PANEL TOGGLE
    // ==========================================================================
    sciToggleBtn.addEventListener('click', () => {
        scientificPanel.classList.toggle('expanded');
        sciToggleBtn.classList.toggle('active');
    });

    // ==========================================================================
    // HISTORY DRAWER LOGIC
    // ==========================================================================
    historyToggleBtn.addEventListener('click', openHistory);
    historyCloseBtn.addEventListener('click', closeHistory);
    
    // Close history on clicking outside
    document.addEventListener('click', (e) => {
        if (!historyDrawer.contains(e.target) && 
            !historyToggleBtn.contains(e.target) && 
            historyDrawer.classList.contains('open')) {
            closeHistory();
        }
    });

    function openHistory() {
        historyDrawer.classList.add('open');
        historyDrawer.setAttribute('aria-hidden', 'false');
    }

    function closeHistory() {
        historyDrawer.classList.remove('open');
        historyDrawer.setAttribute('aria-hidden', 'true');
    }

    clearHistoryBtn.addEventListener('click', () => {
        history = [];
        localStorage.setItem('calc_history', JSON.stringify(history));
        renderHistory();
    });

    function addHistoryItem(expr, result) {
        // Limit to last 30 history entries
        history.unshift({ expr, result });
        if (history.length > 30) history.pop();
        localStorage.setItem('calc_history', JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        if (history.length === 0) {
            historyContent.innerHTML = '<p class="no-history-msg">No recent calculations</p>';
            return;
        }

        historyContent.innerHTML = '';
        history.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'history-item';
            itemDiv.setAttribute('tabindex', '0');
            itemDiv.innerHTML = `
                <span class="history-item-expr">${item.expr}</span>
                <span class="history-item-result">${item.result}</span>
            `;
            itemDiv.addEventListener('click', () => {
                currentInput = item.result.toString();
                displayExpr.textContent = item.expr;
                isResultCalculated = true;
                updateDisplay();
                closeHistory();
            });
            itemDiv.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    itemDiv.click();
                }
            });
            historyContent.appendChild(itemDiv);
        });
    }

    // ==========================================================================
    // EVENT DELEGATION FOR KEYPAD BUTTONS
    // ==========================================================================
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', (e) => {
            createRipple(e);
            
            const value = button.getAttribute('data-val');
            const action = button.getAttribute('data-action');

            if (value !== null) {
                handleInput(value);
            } else if (action !== null) {
                handleAction(action);
            }
        });
    });

    // Custom Ripple Click Animation Effect
    function createRipple(event) {
        const button = event.currentTarget;
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        const rect = button.getBoundingClientRect();
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - rect.left - radius}px`;
        circle.style.top = `${event.clientY - rect.top - radius}px`;
        circle.classList.add('ripple');

        const ripple = button.getElementsByClassName('ripple')[0];
        if (ripple) {
            ripple.remove();
        }
        button.appendChild(circle);
    }

    // ==========================================================================
    // STATE INPUT & DISPLAY MANAGEMENT
    // ==========================================================================
    function handleInput(val) {
        if (isResultCalculated) {
            // Overwrite input with new digit, or append to result if typing an operator
            if (['+', '-', '*', '/', '%', '^'].includes(val)) {
                currentInput = displayInput.textContent + val;
            } else {
                currentInput = val === '.' ? '0.' : val;
            }
            isResultCalculated = false;
        } else {
            if (currentInput === '0' && val !== '.') {
                if (val === '(' || val === ')' || ['+', '*', '/', '%', '^'].includes(val)) {
                    currentInput += val;
                } else {
                    currentInput = val; // Overwrite initial '0'
                }
            } else {
                // Prevent duplicate decimal points in same number segment
                if (val === '.') {
                    const parts = currentInput.split(/[\+\-\*\/%^()]/);
                    const lastPart = parts[parts.length - 1];
                    if (lastPart.includes('.')) return;
                }
                currentInput += val;
            }
        }
        updateDisplay();
    }

    function handleAction(action) {
        switch (action) {
            case 'clear':
                currentInput = '0';
                displayExpr.textContent = '';
                isResultCalculated = false;
                break;
            case 'backspace':
                if (isResultCalculated) {
                    displayExpr.textContent = '';
                    isResultCalculated = false;
                } else if (currentInput.length > 1) {
                    // Remove functions if they end with '('
                    const functions = ['sin(', 'cos(', 'tan(', 'log(', 'ln(', 'sqrt('];
                    let deletedFunc = false;
                    for (let f of functions) {
                        if (currentInput.endsWith(f)) {
                            currentInput = currentInput.slice(0, -f.length);
                            deletedFunc = true;
                            break;
                        }
                    }
                    if (!deletedFunc) {
                        currentInput = currentInput.slice(0, -1);
                    }
                } else {
                    currentInput = '0';
                }
                break;
            case 'calculate':
                executeCalculation();
                break;
            case 'sin':
            case 'cos':
            case 'tan':
            case 'log':
            case 'ln':
            case 'sqrt':
                insertFunction(action);
                break;
            case 'factorial':
                insertFactorial();
                break;
        }
        updateDisplay();
    }

    function insertFunction(funcName) {
        if (currentInput === '0' || isResultCalculated) {
            currentInput = funcName + '(';
            isResultCalculated = false;
        } else {
            const lastChar = currentInput.slice(-1);
            if (/\d/.test(lastChar) || lastChar === ')' || lastChar === 'e' || lastChar === 'π') {
                currentInput += '*' + funcName + '(';
            } else {
                currentInput += funcName + '(';
            }
        }
    }

    function insertFactorial() {
        if (isResultCalculated) {
            currentInput = displayInput.textContent + '!';
            isResultCalculated = false;
        } else {
            currentInput += '!';
        }
    }

    function updateDisplay() {
        // Format display values for visual elegance
        let formattedInput = currentInput
            .replace(/\*/g, ' × ')
            .replace(/\//g, ' ÷ ')
            .replace(/\^/g, ' ^ ')
            .replace(/pi/g, 'π');
        
        displayInput.textContent = formattedInput;
        adjustFontSize();
    }

    // Auto-adjust font size to avoid container overflow
    function adjustFontSize() {
        const length = displayInput.textContent.length;
        if (length > 20) {
            displayInput.style.fontSize = '1.3rem';
        } else if (length > 14) {
            displayInput.style.fontSize = '1.7rem';
        } else {
            displayInput.style.fontSize = '2.25rem';
        }
    }

    // ==========================================================================
    // CALCULATION PARSER / MATHEMATICAL ENGINE
    // ==========================================================================
    function executeCalculation() {
        let rawExpr = currentInput;
        if (!rawExpr || rawExpr === '0') return;

        try {
            // Clean parenthesis mismatch
            let openParens = (rawExpr.match(/\(/g) || []).length;
            let closeParens = (rawExpr.match(/\)/g) || []).length;
            while (openParens > closeParens) {
                rawExpr += ')';
                openParens--;
            }

            // Standardize expression formatting for parsing
            const parsedValue = evaluateMathExpression(rawExpr);
            
            // Format output safely (avoid long floating point issues like 0.30000000000000004)
            let formattedResult = parsedValue;
            if (typeof parsedValue === 'number') {
                if (Number.isNaN(parsedValue) || !Number.isFinite(parsedValue)) {
                    throw new Error('Math Error');
                }
                
                // Keep up to 10 decimal digits, stripping trailing zeros
                formattedResult = parseFloat(parsedValue.toFixed(10));
            }

            displayExpr.textContent = currentInput.replace(/\*/g, ' × ').replace(/\//g, ' ÷ ').replace(/pi/g, 'π') + ' =';
            currentInput = formattedResult.toString();
            isResultCalculated = true;

            // Save to history
            addHistoryItem(displayExpr.textContent.replace(' =', ''), formattedResult);
        } catch (err) {
            displayInput.textContent = 'Error';
            isResultCalculated = true;
            currentInput = '0';
            console.error('Calculation Error:', err);
        }
    }

    /**
     * Custom secure recursive descent parser for mathematical expressions.
     * Prevents usage of eval() while supporting nested brackets, functions, operators.
     */
    function evaluateMathExpression(exprStr) {
        // Pre-parse: constants
        let str = exprStr
            .replace(/pi/g, Math.PI.toString())
            .replace(/e/g, Math.E.toString());

        let index = 0;

        function peek() {
            return str.charAt(index);
        }

        function getNextToken() {
            while (index < str.length && /\s/.test(str.charAt(index))) {
                index++;
            }
            if (index >= str.length) return null;

            const char = str.charAt(index);

            // Operators & Parenthesis
            if (['+', '-', '*', '/', '(', ')', '^', '%', '!'].includes(char)) {
                index++;
                return char;
            }

            // Numbers
            if (/\d/.test(char) || char === '.') {
                let numberStr = '';
                while (index < str.length && (/\d/.test(str.charAt(index)) || str.charAt(index) === '.')) {
                    numberStr += str.charAt(index);
                    index++;
                }
                return parseFloat(numberStr);
            }

            // Letters (Functions)
            if (/[a-zA-Z]/.test(char)) {
                let funcName = '';
                while (index < str.length && /[a-zA-Z]/.test(str.charAt(index))) {
                    funcName += str.charAt(index);
                    index++;
                }
                return funcName;
            }

            throw new Error(`Unexpected character: ${char}`);
        }

        let currentToken = getNextToken();

        function consume(expected) {
            if (currentToken === expected) {
                currentToken = getNextToken();
            } else {
                throw new Error(`Expected ${expected} but got ${currentToken}`);
            }
        }

        // Precedence: parseExpr -> parseTerm (+, -) -> parseFactor (*, /, %) -> parsePower (^) -> parseUnary (-, +) -> parseFactorial (!) -> parsePrimary
        function parseExpr() {
            let val = parseTerm();
            while (currentToken === '+' || currentToken === '-') {
                const op = currentToken;
                consume(op);
                const nextVal = parseTerm();
                if (op === '+') val += nextVal;
                else val -= nextVal;
            }
            return val;
        }

        function parseTerm() {
            let val = parseFactor();
            while (currentToken === '*' || currentToken === '/' || currentToken === '%') {
                const op = currentToken;
                consume(op);
                const nextVal = parseFactor();
                if (op === '*') val *= nextVal;
                else if (op === '/') {
                    if (nextVal === 0) throw new Error('Divide by zero');
                    val /= nextVal;
                }
                else val %= nextVal;
            }
            return val;
        }

        function parseFactor() {
            let val = parsePower();
            while (currentToken === '^') {
                consume('^');
                const exponent = parseFactor(); // Right associative evaluation
                val = Math.pow(val, exponent);
            }
            return val;
        }

        function parsePower() {
            // Unary prefix minus/plus
            if (currentToken === '-') {
                consume('-');
                return -parsePower();
            } else if (currentToken === '+') {
                consume('+');
                return parsePower();
            }
            return parseUnary();
        }

        function parseUnary() {
            let val = parsePrimary();
            // Handle factorial postfix
            while (currentToken === '!') {
                consume('!');
                val = factorial(val);
            }
            return val;
        }

        function parsePrimary() {
            const token = currentToken;
            if (typeof token === 'number') {
                consume(token);
                return token;
            }

            if (token === '(') {
                consume('(');
                const val = parseExpr();
                consume(')');
                return val;
            }

            // Function evaluations
            if (typeof token === 'string' && ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt'].includes(token)) {
                consume(token);
                consume('(');
                const val = parseExpr();
                consume(')');

                switch (token) {
                    case 'sin': return Math.sin(val);
                    case 'cos': return Math.cos(val);
                    case 'tan': return Math.tan(val);
                    case 'log': return Math.log10(val);
                    case 'ln': return Math.log(val);
                    case 'sqrt':
                        if (val < 0) throw new Error('Square root of negative number');
                        return Math.sqrt(val);
                }
            }

            throw new Error(`Unexpected token inside expression: ${token}`);
        }

        function factorial(n) {
            if (n < 0 || !Number.isInteger(n)) throw new Error('Invalid factorial operand');
            if (n === 0 || n === 1) return 1;
            let result = 1;
            for (let i = 2; i <= n; i++) {
                result *= i;
            }
            return result;
        }

        return parseExpr();
    }

    // ==========================================================================
    // KEYBOARD INTEGRATION & KEY VISUAL FEEDBACK
    // ==========================================================================
    window.addEventListener('keydown', (e) => {
        // Prevent default actions for standard calculator hotkeys to avoid issues (e.g. Backspace going back, Space clicking focus)
        if (e.key === 'Backspace' || e.key === '/' || e.key === 'Enter') {
            e.preventDefault();
        }

        let mappedVal = null;
        let mappedAction = null;

        // Map keyboard keys to calculator keys
        if (/\d/.test(e.key)) {
            mappedVal = e.key;
        } else if (e.key === '.') {
            mappedVal = '.';
        } else if (e.key === '+') {
            mappedVal = '+';
        } else if (e.key === '-') {
            mappedVal = '-';
        } else if (e.key === '*') {
            mappedVal = '*';
        } else if (e.key === '/') {
            mappedVal = '/';
        } else if (e.key === '%') {
            mappedVal = '%';
        } else if (e.key === '(') {
            mappedVal = '(';
        } else if (e.key === ')') {
            mappedVal = ')';
        } else if (e.key === 'Enter' || e.key === '=') {
            mappedAction = 'calculate';
        } else if (e.key === 'Backspace') {
            mappedAction = 'backspace';
        } else if (e.key === 'Escape') {
            mappedAction = 'clear';
        } else if (e.key === '^') {
            mappedAction = 'power';
        }

        // Find visual matching button to trigger visual feedback
        let targetButton = null;

        if (mappedVal !== null) {
            targetButton = document.querySelector(`.btn[data-val="${mappedVal === '*' ? '*' : mappedVal}"]`);
            handleInput(mappedVal);
        } else if (mappedAction !== null) {
            if (mappedAction === 'calculate') {
                targetButton = document.getElementById('btn-equals');
            } else if (mappedAction === 'backspace') {
                targetButton = document.getElementById('btn-back');
            } else if (mappedAction === 'clear') {
                targetButton = document.getElementById('btn-ac');
            } else {
                targetButton = document.querySelector(`.btn[data-action="${mappedAction}"]`);
            }
            handleAction(mappedAction);
        }

        // Visual click feedback animations
        if (targetButton) {
            targetButton.classList.add('active');
            setTimeout(() => {
                targetButton.classList.remove('active');
            }, 100);
        }
    });
});
