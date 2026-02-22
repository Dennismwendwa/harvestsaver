document.addEventListener('DOMContentLoaded', function () {
    let farmMap = null;
    let marker = null;

    const farmMapEl = document.getElementById('farm-map');
    const farmFormEl = document.getElementById('new-farm-form');

    if (farmMapEl && farmFormEl) {
        // Initialize map
        farmMap = L.map('farm-map').setView([-1.286389, 36.817223], 7);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(farmMap);

        // Add marker on click
        farmMap.on('click', function(e) {
            if (marker) farmMap.removeLayer(marker);
            marker = L.marker(e.latlng, { draggable: true }).addTo(farmMap);

            farmFormEl.querySelector('#id_latitude').value = e.latlng.lat;
            farmFormEl.querySelector('#id_longitude').value = e.latlng.lng;

            marker.on('dragend', function(event) {
                const pos = event.target.getLatLng();
                farmFormEl.querySelector('#id_latitude').value = pos.lat;
                farmFormEl.querySelector('#id_longitude').value = pos.lng;
            });
        });
    }

    // ===== Handle tab shown event =====
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tabBtn => {
        tabBtn.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('data-bs-target');

            if (targetId === '#farm' && farmMap) {
                farmMap.invalidateSize(); // Force Leaflet to recalc map size
                if (marker) {
                    farmMap.setView(marker.getLatLng(), 10);
                } else {
                    farmMap.setView([-1.286389, 36.817223], 7);
                }
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {

    // Sales line chart
    const saleTrendData = JSON.parse(document.getElementById("sales-trend-data").textContent);
    const salesCtx = document.getElementById("salesChart");
    
    new Chart(salesCtx, {
        type: "line",
        data: {
            labels: saleTrendData.labels,
            datasets: [{
                label: "Sales (KES)",
                data: saleTrendData.values,
                tension: 0.4,
                fill: true
            }]
        }
    });

    // Orders pie chart
    const data = JSON.parse(document.getElementById("order-data").textContent);
    const pieCtx = document.getElementById("orderPieChart");

    new Chart(pieCtx, {
        type: "doughnut",
        data: {
            labels: ["Completed", "Pending", "Cancelled"],
            datasets: [{
                data: [data.completed, data.pending, data.cancelled]
            }]
        }
    });

    function scrollToFarmForm() {
        const form = document.getElementById("new-farm-form");
        form.scrollIntoView({ behavior: "smooth" });
        form.classList.add("border", "border-primary", "shadow");
    }

    setTimeout(() => {
        const firstInput = document.querySelector("#product-form-section input");
        if (firstInput) firstInput.focus();
    }, 600);

});


