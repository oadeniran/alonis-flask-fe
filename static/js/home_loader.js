document.addEventListener('DOMContentLoaded', () => {
    const quoteContainer = document.getElementById('quote-container');
    const storyContainer = document.getElementById('story-container');
    const storyLoader = document.getElementById('story-loader');
    const storyContentArea = document.getElementById('story-content-area');

    // --- Function to fetch and display the story ---
    const loadStory = () => {
        fetch('/api/story')
            .then(response => response.ok ? response.json() : Promise.reject('Failed'))
            .then(data => {
                if (data.story && data.story.trim() !== '') {
                    storyLoader.style.display = 'none';
                    storyContentArea.textContent = data.story;
                    storyContentArea.style.display = 'block';

                    document.querySelector('.story-signature').style.display = 'block';
                } else {
                    // If the story is empty, show the personalized prompt
                    storyContainer.innerHTML = `
                        <div class="empty-state-prompt">
                            <i class="fas fa-book-open"></i>
                            <h4>Reflective Stories show here</h4>
                            <p>
                                This is where I share meaningful stories you can relate to based on our conversations, you traits, goals and interactions.
                                <br/><br/>
                                Take an asessment, start a conversatiion or add notes and goals to start seeing stories here.
                            </p>
                        </div>
                    `;
                }

            })
            .catch(error => {
                console.error('Error fetching story:', error);
                storyContainer.innerHTML = '<p>Could not load your story.</p>';
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
                else {
                    quoteContainer.innerHTML = '<p>No quote available.</p>';
                }

                console.log('Quote loaded:', data.quote);
            })
            .catch(error => {
                console.error('Error fetching quote:', error);
                quoteContainer.innerHTML = '<p>Could not load quote of the day.</p>';
            });
    };

    // --- Run both functions when the page loads ---
    loadQuote();
    loadStory();
});