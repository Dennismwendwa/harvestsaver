
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