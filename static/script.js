document.addEventListener('DOMContentLoaded', () => {
    const classifyBtn = document.getElementById('classifyBtn');
    const productText = document.getElementById('productText');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    
    const resultSection = document.getElementById('resultSection');
    const eccnCode = document.getElementById('eccnCode');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceValue = document.getElementById('confidenceValue');
    const reasoningText = document.getElementById('reasoningText');

    classifyBtn.addEventListener('click', async () => {
        const text = productText.value.trim();
        if (!text) return;

        // Set Loading State
        setLoading(true);
        resultSection.classList.add('hidden');

        try {
            const response = await fetch('/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_text: text })
            });

            if (!response.ok) throw new Error('API Error');

            const data = await response.json();
            displayResult(data);

        } catch (error) {
            console.error(error);
            alert('Failed to classify product. Please try again.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
            classifyBtn.disabled = true;
        } else {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            classifyBtn.disabled = false;
        }
    }

    function displayResult(data) {
        resultSection.classList.remove('hidden');
        
        // Animate Result
        eccnCode.textContent = data.ecn_number;
        
        const score = data.confidence_score ? Math.round(data.confidence_score * 100) : 0;
        confidenceValue.textContent = `${score}%`;
        
        // Trigger reflow for animation
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = `${score}%`;
            // Color coding based on confidence
            if(score > 80) confidenceBar.style.background = '#10b981'; // Green
            else if(score > 50) confidenceBar.style.background = '#f59e0b'; // Orange
            else confidenceBar.style.background = '#ef4444'; // Red
        }, 100);

        reasoningText.textContent = data.reasoning || "No reasoning provided.";
    }
});
