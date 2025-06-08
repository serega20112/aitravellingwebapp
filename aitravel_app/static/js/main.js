document.addEventListener('DOMContentLoaded', function() {
    console.log("AI Travel App (Google AI) Main JS Initialized");
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});
