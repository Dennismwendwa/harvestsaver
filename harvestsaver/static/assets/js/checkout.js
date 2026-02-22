
const paymentSelect = document.getElementById('paymentMethod');
const mpesaForm = document.getElementById('mpesaForm');
const bankForm = document.getElementById('bankForm');

paymentSelect.addEventListener('change', function() {
    const value = this.value;
    
    // Hide all forms initially
    mpesaForm.classList.add('d-none');
    bankForm.classList.add('d-none');

    // Show the selected payment form
    if (value === 'mpesa') {
        mpesaForm.classList.remove('d-none');
    } else if (value === 'bank_transfer') {
        bankForm.classList.remove('d-none');
    }
    // Pay on Delivery requires no extra form
});

document.addEventListener("DOMContentLoaded", function () {
    const express = document.getElementById("express");
    const standard = document.getElementById("standard");
    const shippingCostEl = document.getElementById("shippingCost");
    const isPerishable = document.getElementById("isPerishable")?.value === "true";

    // Base shipping values (adjust as needed)
    const EXPRESS_COST = 300;
    const STANDARD_COST = 150;

    function updateShipping() {
        if (express.checked) {
            shippingCostEl.textContent = EXPRESS_COST;
        } else {
            shippingCostEl.textContent = STANDARD_COST;
        }
    }

    // Disable Standard for perishable goods
    if (isPerishable) {
        standard.disabled = true;
        standard.closest(".form-check").classList.add("opacity-50");
        express.checked = true;
        updateShipping();
    }

    // Listen for changes
    express.addEventListener("change", updateShipping);
    standard.addEventListener("change", updateShipping);

    // Initial load
    updateShipping();
});
