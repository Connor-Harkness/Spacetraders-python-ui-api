// SpaceTraders WebUI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    console.log('SpaceTraders WebUI initialized');
    
    // Add any client-side functionality here
    // For now, the dashboard auto-refreshes via the template
    
    // Add smooth transitions for cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-2px)';
        });
    });
    
    // Add loading state for nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            this.style.opacity = '0.7';
        });
    });
}

// Utility function to format numbers
function formatNumber(num) {
    return num.toLocaleString();
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Function to refresh specific sections via AJAX (for future enhancement)
function refreshSection(sectionId) {
    // This could be used to refresh individual sections without full page reload
    console.log(`Refreshing section: ${sectionId}`);
}