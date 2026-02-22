document.addEventListener("DOMContentLoaded", function () {
    const markDelivedBtn = document.querySelectorAll('.mark_received');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    markDelivedBtn.forEach(btn => {
        btn.addEventListener("click", function() {

            const pk = btn.getAttribute("data-pk");
            const button = this;

            fetch(`/logistics/mark-delivered/${pk}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ pk: pk })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const card = button.closest(".card");
                    if (card) {
                        card.style.transition = "opacity 0.3s ease";
                        card.style.opacity = "0";
                        
                        setTimeout(() => {
                            card.remove();
                        }, 300);
                        
                    }
                }
            })
            .catch(err => console.error(err));
        })
    })

});