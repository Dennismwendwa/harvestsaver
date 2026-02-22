
function showSection(sectionId) {
    const sections = document.querySelectorAll('.dashboard-section');

    sections.forEach(section => {
        section.classList.add('d-none');
    });

    document.getElementById(sectionId).classList.remove('d-none');
}

