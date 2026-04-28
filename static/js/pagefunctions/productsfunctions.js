document.addEventListener("DOMContentLoaded", () => {

    // ─────────────────────────────────────────────
    // STORAGE KEY
    // ─────────────────────────────────────────────
    const STORAGE_KEY = "productsPageState";

    // ─────────────────────────────────────────────
    // STATE (default = AUTHORIZED WEAPONS)
    // ─────────────────────────────────────────────
    let state = loadState() || {
        category: "weapons",
        access: "authorized",
        filter: "promotions"
    };

    function saveState() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function loadState() {
        const saved = localStorage.getItem(STORAGE_KEY);
        return saved ? JSON.parse(saved) : null;
    }

    const selectionContent = document.getElementById("selection-content");
    const selectionTitle = document.getElementById("selection-title");
    const heroTypeDisplay = document.getElementById("hero-type-display");

    const categoryBtns = document.querySelectorAll(".toggle-category");
    const accessBtns = document.querySelectorAll(".toggle-access");
    const filterBtns = document.querySelectorAll(".filter-btn");
    const tocLinks = document.querySelectorAll(".toc-link");

    const hfSelects = document.querySelectorAll(".hf-select");
    const clearBtn = document.getElementById("hf-clear-btn");

    const promoToggleBtn = document.querySelector('[data-filter="promotions"]');
    const promoSubmenu = document.getElementById("promotions-toc");

    // ─────────────────────────────────────────────
    function loadPanel() {
        const templateId = `panel-${state.category}-${state.access}-${state.filter}`;
        const template = document.getElementById(templateId);

        if (!template) {
            selectionContent.innerHTML = `<p>No content available.</p>`;
            return;
        }

        selectionContent.innerHTML = "";
        selectionContent.appendChild(template.content.cloneNode(true));

        updateHeaderTitle();
        addScrollSpacing();
        syncActiveStates();
        saveState();
    }

    function updateHeaderTitle() {
        const cap = (str) => str.charAt(0).toUpperCase() + str.slice(1);

        const accessText = cap(state.access);
        const categoryText = cap(state.category);
        const filterText = cap(state.filter);

        // Content header (unchanged)
        selectionTitle.textContent =
            `${accessText} · ${categoryText} · ${filterText}`;

        // ✅ HERO TITLE (UPDATED HERE)
        heroTypeDisplay.textContent = `${accessText} ${categoryText}`;
    }

    function syncActiveStates() {
        categoryBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.category === state.category);
        });

        accessBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.access === state.access);
        });

        filterBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.filter === state.filter);
        });
    }

    function addScrollSpacing() {
        const sections = selectionContent.querySelectorAll(".promo-section");
        sections.forEach(sec => sec.style.minHeight = "260px");
    }

    // ─────────────────────────────────────────────
    // EVENTS
    // ─────────────────────────────────────────────
    categoryBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            state.category = btn.dataset.category;
            loadPanel();
        });
    });

    accessBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            state.access = btn.dataset.access;
            loadPanel();
        });
    });

    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const filter = btn.dataset.filter;

            if (filter === "promotions") {
                promoSubmenu.classList.toggle("open");
                btn.classList.toggle("submenu-open");
            }

            state.filter = filter;
            loadPanel();
        });
    });

    tocLinks.forEach(link => {
        link.addEventListener("click", () => {
            const target = document.getElementById(link.dataset.target);

            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }

            tocLinks.forEach(l => l.classList.remove("toc-active"));
            link.classList.add("toc-active");
        });
    });

    hfSelects.forEach(select => {
        select.addEventListener("change", () => {
            select.style.borderColor = "#a8c47a";
        });
    });

    clearBtn.addEventListener("click", () => {
        hfSelects.forEach(select => {
            select.value = "";
            select.style.borderColor = "";
        });
    });

    // ─────────────────────────────────────────────
    // INITIAL LOAD
    // ─────────────────────────────────────────────
    loadPanel();

});