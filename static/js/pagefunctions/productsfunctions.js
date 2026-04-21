document.addEventListener("DOMContentLoaded", function () {
    initializeProductsPage();
});

function initializeProductsPage() {
    const toggleButtons = document.querySelectorAll(".toggle-btn");
    const filterButtons = document.querySelectorAll(".filter-btn");

    toggleButtons.forEach((button) => {
        button.addEventListener("click", () => {
            toggleButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            updateHeroType(button.dataset.type);
            updateProductsSelection();
        });
    });

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filterButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            updateProductsSelection();
        });
    });

    updateHeroType("weapons");
    updateProductsSelection();
}

function updateHeroType(type) {
    const heroTitle = document.querySelector(".hero-sign-title");
    if (!heroTitle) return;
    heroTitle.textContent = type.toUpperCase();
}

function updateProductsSelection() {
    const activeTypeButton = document.querySelector(".toggle-btn.active");
    const activeFilterButton = document.querySelector(".filter-btn.active");
    const selectionContent = document.getElementById("selection-content");
    const selectionTitle = document.getElementById("selection-title");

    if (
        !activeTypeButton ||
        !activeFilterButton ||
        !selectionContent ||
        !selectionTitle
    )
        return;

    const type = activeTypeButton.dataset.type;
    const filter = activeFilterButton.dataset.filter;
    const titleText = `${type.charAt(0).toUpperCase() + type.slice(1)} · ${filter.charAt(0).toUpperCase() + filter.slice(1)}`;

    selectionTitle.textContent = titleText;
    selectionContent.innerHTML = `<p class="selection-status">Active selection: ${titleText}</p>`;
}
