document.addEventListener('DOMContentLoaded', () => {

    const pageTrackers = { alonis: 1, books: 1, movies: 1, songs: 1, news: 1 };
    // Icons for each category empty state
    const emptyStateIcons = {
        alonis: 'fas fa-brain',
        books: 'fas fa-book',
        movies: 'fas fa-film',
        songs: 'fas fa-music',
        news: 'fas fa-newspaper'
    };
    // Text for empty state headers
    const emptyStateHeader = {
        alonis: 'My Personal Suggestions For You',
        movies: 'No Movie Suggestions Yet',
        books: 'No Book Suggestions Yet',
        song: 'Looking for a New Soundtrack?',
        news: 'No Relevant News Right Now'
    }
    // Text for empty state prompts
    const emptyStateText = {
        alonis: 'My own recommendations will appear here. The more we interact, the better they get!',
        books: 'I will suggest books based on your interests. Keep interacting and they will beigin to appear!',
        movies: 'The more you interact with Alonis, the better I can tailor movie night for you!',
        songs: 'Your song recommendations will appear here as I get to know your tastes',
        news: 'I always scan for articles that match your interests. Check back soon!'
    }
    
    // Get modal elements once at the start
    const viewModal = document.getElementById('view-details-modal');
    const closeModalBtn = document.getElementById('close-view-modal-btn');

    // --- Helper function to mark an item as complete ---
    const markAsComplete = (itemId, buttonElement) => {
        buttonElement.textContent = 'Marking...';
        buttonElement.disabled = true;

        fetch(`/api/recommendation/complete/${itemId}`, { method: 'POST' })
            .then(response => response.ok ? response.json() : Promise.reject('Action failed'))
            .then(data => {
                if (data.status !== 'success') throw new Error(data.message);

                // --- Update UI on Success ---
                // Find the original card on the page
                const originalCard = document.querySelector(`.item-card[data-item-id="${itemId}"]`);
                if (originalCard) {
                    const indicator = originalCard.querySelector('.action-indicator');
                    if (indicator) {
                        indicator.classList.add('achieved');
                        if (!indicator.querySelector('.fa-check-circle')) {
                             indicator.innerHTML += ' <i class="fas fa-check-circle"></i>';
                        }
                    }
                    // Remove the action button from the card's dropdown
                    originalCard.querySelector('.action-btn')?.remove();
                    // Update the card's stored data
                    let itemData = JSON.parse(originalCard.dataset.itemData);
                    itemData.action.status = true;
                    originalCard.dataset.itemData = JSON.stringify(itemData);
                }
                
                // If the button clicked was in the modal, update it
                if (buttonElement.classList.contains('modal-action-btn')) {
                    let itemData = JSON.parse(originalCard.dataset.itemData);
                    buttonElement.textContent = itemData.action.name;
                    buttonElement.classList.add('achieved');
                }
            })
            .catch(err => {
                console.error("Action failed:", err);
                alert("Sorry, we couldn't update this item. Please try again.");
                buttonElement.textContent = `Mark as...`; // Reset button text
                buttonElement.disabled = false;
            });
    };

    // --- Function to create a card element with all features ---
    const createCard = (item, category) => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.dataset.itemId = item.id;
        // Store the entire item object on the card for easy access
        card.dataset.itemData = JSON.stringify(item);

        let title = item.title || item.headline;
        let details = item.truncated_description || item.description || `by ${item.artist}` || `Source: ${item.source}` || '';
        if (category === 'movies' && item.year) title += ` (${item.year})`;

        // --- NEW: Generic Metadata Logic ---
        let metaHTML = '';
        if (category === 'books' && item.author) {
            metaHTML = `<span class="card-meta">by ${item.author}</span>`;
        } else if (category === 'songs' && item.artist) {
            metaHTML = `<span class="card-meta">by ${item.artist}</span>`;
        } else if (category === 'movies' && item.genre) {
            metaHTML = `<span class="card-meta">Genre: ${item.genre}</span>`;
        } else if (category === 'news' && item.source) {
            metaHTML = `<span class="card-meta">Source: ${item.source}</span>`;
        }

        let actionIndicatorHTML = '', actionButtonHTML = '';
        if (item.action) {
            actionIndicatorHTML = `
                <div class="action-indicator ${item.action.status ? 'achieved' : ''}">
                    <i class="fas fa-bullseye"></i>${item.action.name}
                    ${item.action.status ? '<i class="fas fa-check-circle"></i>' : ''}
                </div>`;
            if (!item.action.status) {
                actionButtonHTML = `<a href="#" class="dropdown-item action-btn">Mark as ${item.action.name}</a>`;
            }
        }
        
        let viewMoreBtnHTML = '';
        const fullDetails = item.description || item.details;
        if (fullDetails && fullDetails.length > 100) {
            viewMoreBtnHTML = `<button class="view-more-btn">View More <i class="fas fa-expand-alt"></i></button>`;
        }
        
        card.innerHTML = `
            <div class="menu-container">
                <button class="menu-btn"><i class="fas fa-ellipsis-v"></i></button>
                <div class="dropdown-menu">${actionButtonHTML}</div>
            </div>
            ${actionIndicatorHTML}
            <h3>${title}</h3>
            ${metaHTML}
            <p>${details}</p>
            <div class="card-footer">${viewMoreBtnHTML}</div>
        `;
        return card;
    };

    // Main function to fetch and display data
    const fetchData = (category) => {
        const container = document.getElementById(`${category}-grid`);
        const loaderContainer = document.getElementById(`${category}-loader`);
        if (!container || !loaderContainer) return;

        const page = pageTrackers[category];
        loaderContainer.innerHTML = '<p>Loading...</p>';

        fetch(`/api/recommendations/${category}?page=${page}`)
            .then(response => response.ok ? response.json() : Promise.reject('Failed'))
            .then(data => {
                if (page === 1) container.innerHTML = '';
                loaderContainer.innerHTML = '';

                if (data.items && data.items.length > 0) {
                    data.items.forEach(item => container.appendChild(createCard(item, category)));
                } else if (page === 1) {
                    // Show empty state if no items on first page
                    const emptystateiconClass = emptyStateIcons[category] || 'fas fa-info-circle';
                    const emptyStateHeaderText = emptyStateHeader[category] || 'No Recommendations Available';
                    const emptyStateTextForCategory = emptyStateText[category] || 'No recommendations available.';
                    container.innerHTML = `
                    <div class="empty-state-prompt">
                        <i class="${emptystateiconClass}"></i>
                        <h4>${emptyStateHeaderText}</h4>
                        <p>${emptyStateTextForCategory}</p>
                    </div>`;
                }
                
                if (data.has_next_page) {
                    const loadMoreBtn = document.createElement('button');
                    loadMoreBtn.className = 'load-more-btn';
                    loadMoreBtn.textContent = 'Load More';
                    loadMoreBtn.onclick = () => {
                        // Disable the button and change text while loading
                        loadMoreBtn.textContent = 'Loading...';
                        loadMoreBtn.disabled = true; 
                        
                        pageTrackers[category]++;
                        fetchData(category);
                    };
                    loaderContainer.appendChild(loadMoreBtn);
                }
                else {
                    // Show end of list message only if there was ever a list
                    if (pageTrackers[category] > 1) {
                        const endMessage = document.createElement('p');
                        endMessage.className = 'end-of-list-message';
                        endMessage.textContent = 'No more recommendations for now. Keep interacting with Me and come back for more! p.s. Interacting with any of these items helps me learn your preferences better.';
                        loaderContainer.appendChild(endMessage);
                    }
                }
            })
            .catch(error => {
                console.error(`Error fetching ${category}:`, error);
                loaderContainer.innerHTML = '<p>Could not load this section.</p>';
            });
    };

    // --- Unified Click Handler for the entire page ---
    document.body.addEventListener('click', (event) => {
        const target = event.target;

        // Logic for "View More" Modal
        const viewMoreButton = target.closest('.view-more-btn');
        if (viewMoreButton) {
            const card = viewMoreButton.closest('.item-card');
            const itemData = JSON.parse(card.dataset.itemData); // Get full data

            document.getElementById('view-modal-title').textContent = itemData.title + (itemData.year ? ` (${itemData.year})` : '');
            document.getElementById('view-modal-details').textContent = itemData.description || itemData.details;
            
            const modalFooter = document.getElementById('view-modal-footer');
            modalFooter.innerHTML = '';

            // 1. Add the generic metadata
            let metaText = '';
            if (itemData.author) {
                metaText = `Author: ${itemData.author}`;
            } else if (itemData.artist) {
                metaText = `by ${itemData.artist}`;
            } else if (itemData.genre) {
                metaText = `Genre: ${itemData.genre}`;
            } else if (itemData.source) {
                metaText = `Source: ${itemData.source}`;
            }

            if (metaText) {
                const metaSpan = document.createElement('span');
                metaSpan.className = 'modal-meta';
                metaSpan.textContent = metaText;
                modalFooter.appendChild(metaSpan);
            }

            if (itemData.action) {
                const actionBtn = document.createElement('button');
                actionBtn.className = 'btn-action modal-action-btn';
                if (itemData.action.status) {
                    actionBtn.textContent = itemData.action.name;
                    actionBtn.classList.add('achieved');
                    actionBtn.disabled = true; // Disable if already achieved
                } else {
                    actionBtn.textContent = `Mark as ${itemData.action.name}`;
                }
                actionBtn.dataset.itemId = itemData.id;
                modalFooter.appendChild(actionBtn);
            }
            viewModal.style.display = 'flex';

            // Log the interaction with the item if is_red_by_user exists and is false
            if (itemData.is_read_by_user === false) {
                fetch(`/api/recommendation/note_interaction/${itemData.id}`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        console.log(`Interaction logged for item: ${itemData.id}`);
                        // Update the card's data to reflect the interaction
                        itemData.is_read_by_user = true; // Mark as read
                    } else {
                        console.error('Failed to log interaction.');
                    }
                })
                .catch(error => console.error('Interaction API call failed:', error));
            }
        }

        // Logic for dropdown menus
        const isMenuButton = target.closest('.menu-btn');
        document.querySelectorAll('.dropdown-menu.active').forEach(menu => {
            if (!isMenuButton || !menu.closest('.menu-container').contains(isMenuButton)) {
                menu.classList.remove('active');
            }
        });
        if (isMenuButton) {
            isMenuButton.closest('.menu-container').querySelector('.dropdown-menu').classList.toggle('active');
        }

        // Logic for "Mark as..." Action from EITHER dropdown or modal
        const actionButton = target.closest('.action-btn, .modal-action-btn');
        if (actionButton) {
            event.preventDefault();
            const itemId = actionButton.dataset.itemId || actionButton.closest('.item-card').dataset.itemId;
            markAsComplete(itemId, actionButton);
        }
    });

    // Logic to close the modal
    if (closeModalBtn) closeModalBtn.addEventListener('click', () => { viewModal.style.display = 'none'; });
    if (viewModal) viewModal.addEventListener('click', (event) => {
        if (event.target === viewModal) viewModal.style.display = 'none';
    });

    // --- Initial Fetch for all Categories ---
    fetchData('alonis'); 
    fetchData('books');
    fetchData('movies');
    fetchData('songs');
    fetchData('news');
});