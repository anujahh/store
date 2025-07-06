// script.js

document.addEventListener('DOMContentLoaded', function() {
    console.log("Nike Storefront Initialized");

    // Example: Add to cart via AJAX (You would need to implement the backend view)
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Check if user is authenticated
            // This is a simple check; server-side validation is crucial
            const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
            if (!isAuthenticated) {
                window.location.href = '/login/'; // Redirect to login
                return;
            }

            const productId = this.dataset.productId;
            const url = `/add-to-cart/${productId}/`;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                    // Update cart count in navbar
                    updateCartCount();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Function to update cart count
    function updateCartCount() {
        fetch('/api/cart-item-count/') // You'll need to create this API endpoint
            .then(response => response.json())
            .then(data => {
                document.getElementById('cart-count').innerText = data.count;
            });
    }

    // Initial cart count load
    // updateCartCount(); // Uncomment after creating the API endpoint
});