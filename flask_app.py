# flask_app.py
from flask import Flask, render_template_string, request, jsonify
import sympy as sp
from sympy import Eq, latex, Symbol
from sympy.parsing.sympy_parser import (
    parse_expr, 
    standard_transformations, 
    implicit_multiplication_application, 
    convert_xor
)
import re

app = Flask(__name__)

MAX_INPUT_LENGTH = 500

SAFE_LOCALS = {
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan,
    'log': sp.log, 'ln': sp.log, 'exp': sp.exp,
    'sqrt': sp.sqrt, 'cbrt': lambda x: x**(sp.Rational(1,3)),
    'pi': sp.pi, 'e': sp.E, 'oo': sp.oo, 'I': sp.I,
    'Abs': sp.Abs
}

# Define transformations for implicit multiplication (2x -> 2*x) and carets (x^2 -> x**2)
TRANSFORMATIONS = (standard_transformations + (implicit_multiplication_application, convert_xor))

def sanitize_input(text: str):
    if not text or len(text) > MAX_INPUT_LENGTH:
        return None, "Input too long (max 500 chars)"
    text = re.sub(r'[;\'"`]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    # Unicode replacements
    replacements = {
        '²':'^2', '³':'^3', '⁴':'^4', '⁵':'^5', '⁶':'^6', '⁷':'^7', '⁸':'^8', '⁹':'^9',
        '√':'sqrt', '∛':'cbrt', '∞':'oo', 'π':'pi', '×':'*', '·':'*', '÷':'/', '−':'-', '–':'-', '—':'-',
        '½':'1/2', '¼':'1/4', '¾':'3/4'
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    
    # Text replacements
    text = re.sub(r'\bsquare\s+root\s+of\b', 'sqrt', text, flags=re.I)
    text = re.sub(r'\bcube\s+root\s+of\b', 'cbrt', text, flags=re.I)
    
    # Ensure standard caret usage for convert_xor transformation
    text = text.replace('**', '^') 
    return text.strip(), None

def safe_parse(equation_str: str):
    cleaned, err = sanitize_input(equation_str)
    if err: return None, err
    
    # Split into LHS and RHS
    if '=' in cleaned:
        lhs_str, rhs_str = cleaned.split('=', 1)
    else:
        lhs_str, rhs_str = cleaned, '0'
        
    lhs_str = lhs_str.strip()
    rhs_str = rhs_str.strip()

    try:
        # Use parse_expr with transformations instead of manual regex + sympify
        lhs = parse_expr(lhs_str, local_dict=SAFE_LOCALS, transformations=TRANSFORMATIONS, evaluate=False)
        rhs = parse_expr(rhs_str, local_dict=SAFE_LOCALS, transformations=TRANSFORMATIONS, evaluate=False)
        return Eq(lhs, rhs), None
    except Exception as e:
        return None, f"Cannot understand: {e}"

def safe_solve(eq, var):
    try:
        # v1.12+ supports timeout, older versions ignore it
        return sp.solve(eq, var, timeout=4)
    except TypeError:
        return sp.solve(eq, var)
    except Exception:
        return []

def solve_equation(equation_str: str, variable_str: str = 'x'):
    try:
        variable_str = variable_str.strip().lower()
        if not re.fullmatch(r'[a-z]', variable_str):
            return {'error': 'Variable must be a single letter (a-z)'}
        var = Symbol(variable_str)
        
        eq, err = safe_parse(equation_str)
        if err: return {'error': err}
        
        if var not in eq.free_symbols:
            avail = ', '.join(str(s) for s in eq.free_symbols)
            msg = f'Variable "{variable_str}" not found'
            if avail: msg += f'. Found: {avail}'
            return {'error': msg}

        solutions = safe_solve(eq, var)
        
        # Check if solutions is empty or None
        if not solutions and solutions != 0: 
             return {'no_solution': True, 'message': 'No solutions found', 'equation': latex(eq)}

        results = []
        # Ensure solutions is iterable (handle single scalar result edge cases)
        if not isinstance(solutions, list):
            solutions = [solutions]

        for sol in solutions:
            # Handle dictionary results (common in systems of equations, though we target single var)
            val = sol[var] if isinstance(sol, dict) else sol
            
            exact = latex(val)
            plain = str(val)
            try:
                num = val.evalf(12)
                if num.is_real:
                    decimal = f"{float(num):.10f}".rstrip('0').rstrip('.')
                    if decimal == '': decimal = '0' # Handle exact 0 case
                    elif decimal.replace('.','').isdigit() and '.' in decimal: # Ensure X.0 format for integers
                         if float(decimal).is_integer(): decimal = f"{int(float(decimal))}.0"
                else:
                    decimal = str(num)
            except:
                decimal = "Symbolic"
            results.append({'exact': exact, 'decimal': decimal, 'plain': plain})
            
        return {
            'success': True,
            'equation': latex(eq),
            'variable': variable_str,
            'solutions': results,
            'count': len(results)
        }
    except Exception as e:
        return {'error': f'Solving failed: {str(e)}'}

# ------------------- HTML + JS (Unchanged) -------------------
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Equation Solver</title>
<style>
:root{--p:#FF9800;--pd:#F57C00;--pl:#FFB74D;--bg:#FFF8F0;--c:#FFF;--t:#333;--tl:#666;--b:#E0E0E0;--ok:#4CAF50;--err:#F44336}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,var(--bg),#fff);color:var(--t);min-height:100vh;padding:20px}
.container{max-width:800px;margin:auto}header{text-align:center;margin-bottom:30px}
.logo{font-size:2.5em;font-weight:700;color:var(--pd);display:flex;align-items:center;justify-content:center;gap:10px}
.bee{animation:b 2s ease-in-out infinite}@keyframes b{0%,100%{transform:translateY(0)}25%{transform:translateY(-6px) rotate(8deg)}75%{transform:translateY(-4px) rotate(-8deg)}}
.card{background:var(--c);border-radius:20px;padding:30px;box-shadow:0 4px 20px rgba(245,124,0,.1);margin-bottom:20px}
input[type=text]{width:100%;padding:16px 20px;font-size:1.1em;border:2px solid var(--b);border-radius:12px;font-family:'Courier New',monospace;margin:10px 0}
input:focus{outline:none;border-color:var(--p);box-shadow:0 0 0 4px rgba(255,152,0,.1)}
.examples{margin:10px 0;font-size:.9em;color:var(--tl)}
.example-tag{display:inline-block;background:var(--pl);color:#fff;padding:6px 12px;border-radius:8px;margin:4px;cursor:pointer}
.example-tag:hover{background:var(--p)}
button{background:linear-gradient(135deg,var(--p),var(--pd));color:#fff;border:none;padding:16px;font-size:1.1em;font-weight:600;border-radius:12px;cursor:pointer;width:100%;margin-top:10px;position:relative}
.spinner{display:none;width:20px;height:20px;border:3px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:s 1s linear infinite;position:absolute;right:20px}
@keyframes s{to{transform:rotate(360deg)}}
.solution{background:#f9f9f9;border-left:5px solid var(--p);padding:15px;border-radius:8px;margin:8px 0}
.toggle-btn{padding:6px 12px;background:#fff;border:2px solid var(--p);border-radius:6px;cursor:pointer;font-size:.9em;margin:0 4px;color:#D84315}
.toggle-btn.active{background:var(--p);color:#fff}
.copy-btn{padding:6px 10px;background:var(--pl);color:#8D4004;border:none;border-radius:6px;cursor:pointer;margin:2px;font-size:.85em;flex:1;min-width:80px;font-weight:600}
.copy-btn:hover{background:var(--p);color:#fff}
.toast{position:fixed;bottom:20px;right:20px;background:var(--ok);color:#fff;padding:12px 24px;border-radius:8px;opacity:0;transition:opacity .3s;z-index:1000}
.toast.show{opacity:1}
.error-message{background:#ffebee;color:var(--err);padding:15px;border-radius:8px;border-left:4px solid var(--err);margin:15px 0}
#results{max-height:60vh;overflow-y:auto;padding-right:5px}
</style>
<script>MathJax={tex:{inlineMath:[['$','$']]}};</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
<body>
<div class="container">
<header><div class="logo"><span class="bee">Zoom Bee Apps</span></div><p>Free Equation Solver</p></header>
<div class="card">
  <input type="text" id="eq" placeholder="x^2+9x=8  or  sin(x)=0.5  or  2^t=16" autofocus>
  <div class="examples">
    Try:
    <span class="example-tag" onclick="document.getElementById('eq').value='x^2+9x=8'">x²+9x=8</span>
    <span class="example-tag" onclick="document.getElementById('eq').value='x^2-4=0'">x²-4=0</span>
    <span class="example-tag" onclick="document.getElementById('eq').value='sin(x)=0.5'">sin(x)=0.5</span>
    <span class="example-tag" onclick="document.getElementById('eq').value='2^x=32'">2^x=32</span>
  </div>
  <input type="text" id="var" value="x" maxlength="1" style="width:80px;text-align:center;margin-top:10px">
  <button id="btn">Solve <div class="spinner" id="spin"></div></button>
</div>
<div id="results"></div>
<div class="toast" id="toast">Copied!</div>
</div>

<script>
const eq = document.getElementById('eq'), vari = document.getElementById('var'), btn = document.getElementById('btn'),
      spin = document.getElementById('spin'), results = document.getElementById('results'), toast = document.getElementById('toast');

window.solutionsData = [];
window.currentMode = 'exact';

function showToast(msg = 'Copied!') {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2000);
}

async function solve() {
  const equation = eq.value.trim(), variable = vari.value.trim() || 'x';
  if (!equation) return;
  btn.disabled = true; spin.style.display = 'block'; results.innerHTML = '';

  try {
    const r = await fetch('/solve', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                     body: JSON.stringify({equation, variable})});
    const d = await r.json();

    if (d.error) {
      results.innerHTML = `<div class="error-message"><strong>Error:</strong> ${d.error}</div>`;
    } else if (d.no_solution) {
      results.innerHTML = `<div style="text-align:center;padding:30px;background:#fff8e1;border-radius:12px">$${d.equation}$<h3>No solutions</h3></div>`;
      MathJax.typesetPromise();
    } else {
      window.solutionsData = d.solutions;
      let h = `<div style="text-align:center;padding:15px;background:#fff8e1;border-radius:12px;margin-bottom:15px">$${d.equation}$</div>
               <h3 style="margin:10px 0">${d.count} solution${d.count>1?'s':''} for <strong>${d.variable}</strong>:</h3>`;
      d.solutions.forEach((s, i) => {
        h += `<div class="solution">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <strong>${d.variable} =</strong>
            <div>
              <button class="toggle-btn active" data-index="${i}" data-mode="exact">Exact</button>
              <button class="toggle-btn" data-index="${i}" data-mode="decimal">Approximate</button>
            </div>
          </div>
          <div class="solution-content" id="c${i}">$${s.exact}$</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px">
            <button class="copy-btn" onclick="copyResult(${i}, 'latex')">LaTeX</button>
            <button class="copy-btn" onclick="copyResult(${i}, 'md')">Markdown</button>
            <button class="copy-btn" onclick="copyResult(${i}, 'plain')">Simple Text</button>
            <button class="copy-btn" onclick="copyResult(${i}, 'html')">HTML</button>
          </div>
        </div>`;
      });
      results.innerHTML = h;
      document.querySelectorAll('.toggle-btn').forEach(b => {
        b.onclick = () => toggle(b.dataset.index, b.dataset.mode);
      });
      MathJax.typesetPromise();
    }
  } catch (e) {
    console.error(e);
    results.innerHTML = `<div class="error-message">Network error</div>`;
  } finally {
    btn.disabled = false; spin.style.display = 'none';
  }
}

function toggle(i, mode) {
  const s = window.solutionsData[i];
  const content = document.getElementById(`c${i}`);
  content.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  content.innerHTML = mode === 'exact' ? `$${s.exact}$` : `<code>${s.decimal}</code>`;
  window.currentMode = mode;
  MathJax.typesetPromise();
}

async function copyResult(i, type) {
  const s = window.solutionsData[i];
  const isDecimal = window.currentMode === 'decimal';
  let text = '';

  if (type === 'latex') text = isDecimal ? s.decimal : s.exact;
  else if (type === 'md') text = isDecimal ? s.decimal : `$$${s.exact}$$`;
  else if (type === 'plain') text = isDecimal ? s.decimal : s.plain;
  else if (type === 'html') text = isDecimal ? s.decimal : `<math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow>${s.exact.replace(/\\([()])/g, '$1')}</mrow></math>`;

  try {
    await navigator.clipboard.writeText(text);
    showToast();
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    showToast();
  }
}

btn.onclick = solve;
eq.addEventListener('keypress', e => { if (e.key === 'Enter') solve(); });
</script>
</body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json(silent=True) or {}
    equation = data.get('equation', '').strip()
    variable = data.get('variable', 'x').strip()
    if not equation:
        return jsonify({'error': 'Enter an equation'})
    return jsonify(solve_equation(equation, variable))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)))