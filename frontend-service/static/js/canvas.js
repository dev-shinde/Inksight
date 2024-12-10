// canvas.js
let canvas = document.getElementById('drawingCanvas');
let ctx = canvas.getContext('2d');
let isDrawing = false;
let currentColor = 'white';

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight - 120;
}

window.onload = () => {
    resizeCanvas();
    ctx.lineCap = 'round';
    ctx.lineWidth = 3;
}

window.onresize = resizeCanvas;

canvas.onmousedown = (e) => {
    isDrawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
};

canvas.onmousemove = (e) => {
    if (!isDrawing) return;
    ctx.strokeStyle = currentColor;
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
};

canvas.onmouseup = () => isDrawing = false;
canvas.onmouseout = () => isDrawing = false;

function setColor(color) {
    currentColor = color;
}

function resetCanvas() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Clear output text
    document.getElementById('expressionText').textContent = '';
    document.getElementById('resultText').textContent = '';
    document.getElementById('explanationText').textContent = '';
    
    // Keep panel visible with empty fields
    const resultPanel = document.getElementById('resultPanel');
    resultPanel.classList.remove('hidden');
    resultPanel.style.display = 'flex';
}

// Add this to main.js
function showResults(expr, result, explanation) {
    const resultPanel = document.getElementById('resultPanel');
    resultPanel.classList.remove('hidden');
    document.getElementById('result').innerHTML = expr + ' = ' + result;
    document.getElementById('explanation').textContent = explanation;
}