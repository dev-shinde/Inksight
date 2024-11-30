// In your main.js or wherever you handle the calculate function
function calculate() {
    const btn = document.getElementById('calculateBtn');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: canvas.toDataURL()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const result = data.data[0];
            document.getElementById('expressionText').textContent = result.expr;
            document.getElementById('resultText').textContent = result.result;
            document.getElementById('explanationText').textContent = result.explanation;
            document.getElementById('resultPanel').classList.remove('hidden');
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing request');
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Calculate';
    });
}

// Add this to hide results when resetting
function resetCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById('expressionText').textContent = '';
    document.getElementById('resultText').textContent = '';
    document.getElementById('explanationText').textContent = '';
    document.getElementById('resultPanel').style.display = 'none';
}