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
            image: canvas.toDataURL(),
            dict_of_vars: {}
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const result = data.data[0];
            // Update the result panel with clean formatting
            document.getElementById('expressionText').textContent = result.expr;
            document.getElementById('resultText').textContent = result.result;
            document.getElementById('explanationText').textContent = result.explanation;
            
            // Show the result panel with a fade effect
            const resultPanel = document.getElementById('resultPanel');
            resultPanel.style.opacity = '0';
            resultPanel.style.display = 'flex';
            setTimeout(() => {
                resultPanel.style.opacity = '1';
            }, 10);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('expressionText').textContent = 'Error processing request';
        document.getElementById('resultText').textContent = '';
        document.getElementById('explanationText').textContent = '';
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