document.addEventListener("DOMContentLoaded", function () {
    const cartContainer = document.getElementById("cart-buttons");
    const quantityDisplay = document.getElementById("cart_item_quantity");
    const totalPriceEl = document.getElementById("total-price");
    const unitPrice = parseFloat(cartContainer.dataset.unitPrice);
    const productId = cartContainer.dataset.productId;

    // Helper to POST JSON
    async function postCart(action) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch(`/cart/${action}/${productId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({ action: action })
        });

        const data = await response.json();
        return data;
    }

    // Function to attach Add button listener
    function attachAddButton() {
        const addBtn = document.getElementById("add-to-cart-btn");
        if (!addBtn) return;

        addBtn.addEventListener("click", async () => {
            const data = await postCart("add");
            if (data.quantity !== undefined) {
                quantityDisplay.textContent = data.quantity;
                totalPriceEl.textContent = "KES " + (unitPrice * data.quantity).toFixed(2);
                updateGlobalCartBadge(data.total_cart_quantity);
                switchToIncrementDecrement();
            } else {
                alert("Failed to add to cart");
            }
        });
    }

    // Function to switch buttons after first add
    function switchToIncrementDecrement() {
        cartContainer.innerHTML = `
            <div class="d-flex gap-2">
                <button type="button" id="increment-btn" class="btn btn-primary flex-fill">+</button>
                <button type="button" id="decrement-btn" class="btn btn-danger flex-fill">-</button>
            </div>
        `;
        attachIncrementDecrementEvents();
    }

    // Attach increment / decrement events
    function attachIncrementDecrementEvents() {
        const incBtn = document.getElementById("increment-btn");
        const decBtn = document.getElementById("decrement-btn");

        if (incBtn) {
            incBtn.addEventListener("click", async () => {
                const data = await postCart("add");
                quantityDisplay.textContent = data.quantity;
                const totalPrice = unitPrice * data.quantity;
                totalPriceEl.textContent = "KES " + totalPrice.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
                updateGlobalCartBadge(data.total_cart_quantity);
            });
        }

        if (decBtn) {
            decBtn.addEventListener("click", async () => {
                const data = await postCart("remove");
                quantityDisplay.textContent = data.quantity;
                const totalPrice = unitPrice * data.quantity;
                totalPriceEl.textContent = "KES " + totalPrice.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
                updateGlobalCartBadge(data.total_cart_quantity);

                if (data.quantity === 0) {
                    // Replace buttons with Add button
                    cartContainer.innerHTML = `
                        <button type="button" id="add-to-cart-btn" class="btn btn-primary w-100">Add to Cart</button>
                    `;
                    attachAddButton(); // reattach listener here
                }
            });
        }
    }

    attachAddButton();           // Attach listener for initial Add button
    attachIncrementDecrementEvents(); // Attach inc/dec if already present

    function updateGlobalCartBadge(quantity) {
        const badge = document.getElementById("global-cart-quantity");
        if (!badge) return;

        if (quantity > 0) {
            badge.textContent = quantity;
            badge.style.display = "inline";
        } else {
            badge.textContent = 0;
        }
    }
});
