document.addEventListener('DOMContentLoaded', () => {
    const recommendationsContainer = document.getElementById('recommendations-container');
    const quoteContainer = document.getElementById('quote-container');

    // --- Function to fetch and display recommendations ---
    const loadRecommendations = () => {
        fetch('/api/recommendations')
            .then(response => response.ok ? response.json() : Promise.reject('Failed'))
            .then(data => {
                recommendationsContainer.innerHTML = ''; // Clear skeleton loaders
                if (data.recommendations) {
                    console.log('Recommendations loaded:', data.recommendations);
                    data.recommendations.forEach(rec => {
                        const card = document.createElement('div');
                        card.className = 'recommendation-card';
                        card.innerHTML = `<h4>${rec.title}</h4><p>${rec.details}</p>`;
                        recommendationsContainer.appendChild(card);
                    });

                    if (data.recommendations.length >= 5) {
                        const viewMoreCard = document.createElement('a');
                        viewMoreCard.href = "recommendations";
                        viewMoreCard.className = 'view-more-card';
                        viewMoreCard.innerHTML = `<span>View More</span><i class="fas fa-arrow-right"></i>`;
                        recommendationsContainer.appendChild(viewMoreCard);
                    }

                    if (data.recommendations && data.recommendations.length <= 0) {
                        // If the list is empty, show the prompt
                        recommendationsContainer.innerHTML = `
                            <div class="empty-state-prompt">
                                <i class="fas fa-magic"></i>
                                <h4>Your Recommendations will appear here</h4>
                                <p>
                                    The more you interact with me, the better I'll get at tailoring recommendations for you.
                                    You can start by jotting down a quick note — maybe a random thought or your goals for the next 3 months.
                                    Want deeper insights? Take a quick personality test or explore the MindLens feature.
                                    Feeling spontaneous? Drop into the Talk Session chat and share whatever's on your mind.
                                    Check back anytime — the more you share, the more I can support you.
                                </p>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching recommendations:', error);
                recommendationsContainer.innerHTML = '<p>Could not load recommendations.</p>';
            });
    };

    // --- Function to fetch and display the quote ---
    const loadQuote = () => {
        fetch('/api/quote')
            .then(response => response.ok ? response.json() : Promise.reject('Failed'))
            .then(data => {
                quoteContainer.innerHTML = ''; // Clear skeleton loader
                if (data.quote) {
                    const blockquote = document.createElement('blockquote');
                    blockquote.textContent = `"${data.quote.quote}"`;
                    const author = document.createElement('p');
                    author.className = 'author';
                    author.textContent = `- ${data.quote.author}`;
                    quoteContainer.appendChild(blockquote);
                    quoteContainer.appendChild(author);
                }
            })
            .catch(error => {
                console.error('Error fetching quote:', error);
                quoteContainer.innerHTML = '<p>Could not load quote of the day.</p>';
            });
    };

    // --- Run both functions when the page loads ---
    loadRecommendations();
    loadQuote();
});