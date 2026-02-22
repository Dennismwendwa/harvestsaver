document.addEventListener('DOMContentLoaded', function () {

    let map = null;
    let hubMap = null;
    let marker = null;

    // ===== PARSE EXISTING HUBS =====
    const hubsRaw = document.getElementById("hubs-data")?.textContent;
    const hubs = hubsRaw ? JSON.parse(hubsRaw) : [];

    // ===== MAIN MAP: SHOW ALL HUBS =====
    const mapEl = document.getElementById("map");
    if (mapEl) {
        map = L.map('map').setView([-1.286389, 36.817223], 7);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

        hubs.forEach(hub => {
            if (hub.latitude && hub.longitude) {
                L.marker([hub.latitude, hub.longitude])
                    .addTo(map)
                    .bindPopup(hub.name);
            }
        });
    }

    // Ensure map resizes when the tab becomes visible
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tabBtn => {
        tabBtn.addEventListener('shown.bs.tab', function (event) {
            const targetId = event.target.getAttribute('data-bs-target');
            if (targetId === '#create-hub' && hubMap) {
                hubMap.invalidateSize();
                if (marker) hubMap.setView(marker.getLatLng(), 10);
            }
            if (targetId === '#hubs' && map) {
                map.invalidateSize();
            }
        });
    });

    // ===== HUB PICKER MAP =====
    const hubMapEl = document.getElementById("hub-map");
    const formEl = document.getElementById("hub-form");

    if (!hubMapEl || !formEl) return;

    hubMap = L.map('hub-map').setView([-1.286389, 36.817223], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(hubMap);

    hubMap.on('click', function (e) {
        if (marker) hubMap.removeLayer(marker);

        marker = L.marker(e.latlng, { draggable: true }).addTo(hubMap);

        const latInput = formEl.querySelector('input[name="latitude"]');
        const lngInput = formEl.querySelector('input[name="longitude"]');

        latInput.value = e.latlng.lat;
        lngInput.value = e.latlng.lng;

        marker.on('dragend', function (event) {
            const pos = event.target.getLatLng();
            latInput.value = pos.lat;
            lngInput.value = pos.lng;
        });
    });

});

let farmMap = null;
let marker = null;

document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(tabBtn => {
    tabBtn.addEventListener('shown.bs.tab', function (event) {
        const targetId = event.target.getAttribute('data-bs-target');

        if (targetId === '#create') {
            initFarmMap();
        }
    });
});

function initFarmMap() {
    if (farmMap) {
        farmMap.invalidateSize();
        return;
    }

    const farmMapEl = document.getElementById('farm-map');
    const farmFormEl = document.getElementById('new-farm-form');

    farmMap = L.map(farmMapEl).setView([-1.286389, 36.817223], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(farmMap);

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

