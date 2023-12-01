document.addEventListener("DOMContentLoaded", function () {
    var contactOwnerButton = document.querySelector(".contact_owner");
    var overlayContainer = document.getElementById("overlayContainer");

    contactOwnerButton.addEventListener("click", function () {
        overlayContainer.style.display = "flex";
    });

    var form = document.querySelector(".contact_owner_form");
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        fetch(form.action, {
            method: form.method,
            body: new FormData(form),
        })
        .then(response => {
            if (response.ok) {
                form.reset();
                overlayContainer.style.display = "none";
            } else {
                //
            }
        })
    });

});