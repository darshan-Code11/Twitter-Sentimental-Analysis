document.addEventListener('DOMContentLoaded', () => {
    const tweetInput = document.getElementById('tweetInput');
    const currentCharCount = document.getElementById('currentChar');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultSection = document.getElementById('resultSection');
    const sentimentLabel = document.getElementById('sentimentLabel');
    const sentimentDesc = document.getElementById('sentimentDesc');
    const sentimentIcon = document.getElementById('sentimentIcon');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceFill = document.getElementById('confidenceFill');
    const cleanedTweet = document.getElementById('cleanedTweet');
    const loader = analyzeBtn.querySelector('.loader');
    const btnText = analyzeBtn.querySelector('.btn-text');
    
    // Add scanning line to card
    const analysisBox = document.querySelector('.analysis-box');
    const scanLine = document.createElement('div');
    scanLine.className = 'scanning-line';
    analysisBox.appendChild(scanLine);

    // 3D Tilt Effect on Container
    const container = document.querySelector('.container');
    const cards = document.querySelectorAll('.card');

    document.addEventListener('mousemove', (e) => {
        const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
        const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
        
        cards.forEach(card => {
            card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
        });
    });

    // Reset tilt on mouse leave
    document.addEventListener('mouseleave', () => {
        cards.forEach(card => {
            card.style.transform = `rotateY(0deg) rotateX(0deg)`;
            card.style.transition = 'all 0.5s ease';
        });
    });
    
    document.addEventListener('mouseenter', () => {
        cards.forEach(card => {
            card.style.transition = 'none'; // Remove transition while moving for smooth effect
        });
    });

    // Update character count
    tweetInput.addEventListener('input', () => {
        const length = tweetInput.value.length;
        currentCharCount.textContent = length;
        if (length > 280) {
            currentCharCount.style.color = '#EF4444';
        } else {
            currentCharCount.style.color = '#6B7280';
        }
    });

    // Analyze button click
    analyzeBtn.addEventListener('click', async () => {
        const text = tweetInput.value.trim();
        if (!text) {
            alert('Please enter a tweet to analyze.');
            return;
        }

        // Show loading state
        analyzeBtn.disabled = true;
        loader.classList.remove('hidden');
        btnText.textContent = 'Processing...';
        resultSection.classList.add('hidden');
        analysisBox.classList.add('is-scanning');
        
        // Reset dynamic classes
        resultSection.className = 'result-card card hidden';
        confidenceFill.className = 'meter-fill';

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tweet: text }),
            });

            if (!response.ok) {
                throw new Error('API request failed');
            }

            const data = await response.json();
            
            // Add a slight delay to show off the scanning animation
            setTimeout(() => {
                updateUI(data);
                analysisBox.classList.remove('is-scanning');
                analyzeBtn.disabled = false;
                loader.classList.add('hidden');
                btnText.textContent = 'Analyze Sentiment';
            }, 800);
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the analysis server. Make sure the backend is running.');
            analysisBox.classList.remove('is-scanning');
            analyzeBtn.disabled = false;
            loader.classList.add('hidden');
            btnText.textContent = 'Analyze Sentiment';
        }
    });

    function updateUI(data) {
        // Show result section
        resultSection.classList.remove('hidden');
        
        // Update label and styling
        if (data.prediction === 1) {
            sentimentLabel.textContent = data.label || 'Positive';
            sentimentLabel.className = 'sentiment-positive';
            sentimentDesc.textContent = "We've detected a positive tone in this tweet. It radiates good energy! ✨";
            sentimentIcon.innerHTML = '😊';
            sentimentIcon.className = 'sentiment-icon bg-positive';
            resultSection.classList.add('card-positive');
            confidenceFill.classList.add('fill-positive');
        } else if (data.prediction === 0) {
            sentimentLabel.textContent = data.label || 'Neutral';
            sentimentLabel.className = 'sentiment-neutral';
            sentimentDesc.textContent = "This tweet appears to have a neutral tone. Just stating facts. 📊";
            sentimentIcon.innerHTML = '😐';
            sentimentIcon.className = 'sentiment-icon bg-neutral';
            resultSection.classList.add('card-neutral');
            confidenceFill.classList.add('fill-neutral');
        } else {
            sentimentLabel.textContent = data.label || 'Negative';
            sentimentLabel.className = 'sentiment-negative';
            sentimentDesc.textContent = "Warning: This tweet has been flagged as negative or potentially toxic. 🚩";
            sentimentIcon.innerHTML = '⚠️';
            sentimentIcon.className = 'sentiment-icon bg-negative';
            resultSection.classList.add('card-negative');
            confidenceFill.classList.add('fill-negative');
        }

        // Update confidence
        const confidencePercent = Math.round(data.confidence * 100);
        
        // Count up animation for percentage
        let currentPercent = 0;
        const duration = 1200; // ms
        const interval = 20; // ms
        const steps = duration / interval;
        const increment = confidencePercent / steps;
        
        const counter = setInterval(() => {
            currentPercent += increment;
            if (currentPercent >= confidencePercent) {
                currentPercent = confidencePercent;
                clearInterval(counter);
            }
            confidenceValue.textContent = `${Math.round(currentPercent)}%`;
        }, interval);
        
        // Reset and trigger width animation
        confidenceFill.style.width = '0%';
        setTimeout(() => {
            confidenceFill.style.width = `${confidencePercent}%`;
        }, 100);

        // Update cleaned tweet
        cleanedTweet.textContent = data.cleaned_tweet || 'No tokens remaining after processing';
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
