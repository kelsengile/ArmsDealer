document.addEventListener("DOMContentLoaded", () => {

    // ─────────────────────────────────────────────
    // STORAGE KEY
    // ─────────────────────────────────────────────
    const STORAGE_KEY = "productsPageState";

    // ─────────────────────────────────────────────
    // STATE
    // state.filter: "promotions" | "categories" | "brands"
    // state.category: null | "firearms" | "blades" | etc.
    //   when filter === "categories" and category is set → show specific category panel
    //   when filter === "categories" and category is null → show main categories panel
    // ─────────────────────────────────────────────
    let state = loadState() || {
        access: "authorized",
        filter: "promotions",
        category: null
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

    const accessBtns = document.querySelectorAll(".toggle-access");
    const filterBtns = document.querySelectorAll(".filter-btn");

    const hfSelects = document.querySelectorAll(".hf-select");
    const clearBtn = document.getElementById("hf-clear-btn");

    const promoToggleBtn = document.querySelector('[data-filter="promotions"]');
    const promoSubmenu = document.getElementById("promotions-toc");

    const categoriesToggleBtn = document.querySelector('[data-filter="categories"]');
    const categoriesSubmenu = document.getElementById("categories-toc");

    // ─────────────────────────────────────────────
    // LOAD PANEL
    // ─────────────────────────────────────────────
    function loadPanel() {
        let templateId;

        if (state.filter === "categories" && state.category) {
            // Specific category panel — access-agnostic
            templateId = `panel-category-${state.category}`;
        } else {
            templateId = `panel-${state.access}-${state.filter}`;
        }

        const template = document.getElementById(templateId);

        if (!template) {
            selectionContent.innerHTML = `<p class="selection-status">No content available for this selection.</p>`;
            updateHeaderTitle();
            saveState();
            return;
        }

        selectionContent.innerHTML = "";
        selectionContent.appendChild(template.content.cloneNode(true));

        // Wire up clickable items inside the newly injected panel
        bindCategoryItems();

        // Promo: give each section a minimum height for TOC scrolling
        addScrollSpacing();

        updateHeaderTitle();
        syncActiveStates();
        saveState();
    }

    // ─────────────────────────────────────────────
    // BIND CATEGORY ITEM CLICKS (main categories panel)
    // ─────────────────────────────────────────────
    function bindCategoryItems() {
        // Both .cat-all-item and .cat-popular-item open a specific category
        const catItems = selectionContent.querySelectorAll(
            "[data-category]"
        );
        catItems.forEach(item => {
            item.addEventListener("click", () => {
                const cat = item.dataset.category;
                if (!cat) return;
                state.category = cat;
                // Highlight the matching sidebar link
                highlightCategoryLink(cat);
                loadPanel();
            });
        });
    }

    // ─────────────────────────────────────────────
    // HIGHLIGHT SIDEBAR CATEGORY LINK
    // ─────────────────────────────────────────────
    function highlightCategoryLink(cat) {
        document.querySelectorAll(".toc-link--category").forEach(l => {
            l.classList.toggle("toc-active", l.dataset.category === cat);
        });
    }

    // ─────────────────────────────────────────────
    // UPDATE HEADER TITLE
    // ─────────────────────────────────────────────
    function updateHeaderTitle() {
        const cap = str => str.charAt(0).toUpperCase() + str.slice(1);

        const accessText = cap(state.access);

        let filterText;
        if (state.filter === "categories" && state.category) {
            filterText = `Categories · ${cap(state.category)}`;
        } else {
            filterText = cap(state.filter);
        }

        selectionTitle.textContent = `${accessText} · ${filterText}`;
        heroTypeDisplay.textContent = accessText;
    }

    // ─────────────────────────────────────────────
    // ACTIVE STATES
    // ─────────────────────────────────────────────
    function syncActiveStates() {
        accessBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.access === state.access);
        });

        filterBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.filter === state.filter);
        });

        // If a specific category is active, also reflect on sidebar links
        if (state.filter === "categories" && state.category) {
            highlightCategoryLink(state.category);
        } else {
            document.querySelectorAll(".toc-link--category").forEach(l =>
                l.classList.remove("toc-active")
            );
        }
    }

    // ─────────────────────────────────────────────
    // SCROLL SPACING (promo panels)
    // ─────────────────────────────────────────────
    function addScrollSpacing() {
        const sections = selectionContent.querySelectorAll(".promo-section");
        sections.forEach(sec => sec.style.minHeight = "260px");
    }

    // ─────────────────────────────────────────────
    // SUBMENU HELPERS
    // ─────────────────────────────────────────────
    function openSubmenu(btn, menu) {
        menu.classList.add("open");
        btn.classList.add("submenu-open");
    }

    function closeSubmenu(btn, menu) {
        menu.classList.remove("open");
        btn.classList.remove("submenu-open");
    }

    function toggleSubmenu(btn, menu) {
        if (menu.classList.contains("open")) {
            closeSubmenu(btn, menu);
        } else {
            openSubmenu(btn, menu);
        }
    }

    // ─────────────────────────────────────────────
    // EVENTS — ACCESS TOGGLE
    // ─────────────────────────────────────────────
    accessBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            state.access = btn.dataset.access;
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — FILTER BUTTONS
    // ─────────────────────────────────────────────
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const filter = btn.dataset.filter;

            if (filter === "promotions") {
                // Toggle promo submenu; close categories submenu
                toggleSubmenu(promoToggleBtn, promoSubmenu);
                closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
                state.filter = "promotions";
                state.category = null;
                loadPanel();
                return;
            }

            if (filter === "categories") {
                // Toggle categories submenu; close promo submenu
                toggleSubmenu(categoriesToggleBtn, categoriesSubmenu);
                closeSubmenu(promoToggleBtn, promoSubmenu);
                // Clicking "Categories" root always shows the main index panel
                state.filter = "categories";
                state.category = null;
                loadPanel();
                return;
            }

            // Brands (or any other future flat filter)
            closeSubmenu(promoToggleBtn, promoSubmenu);
            closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
            state.filter = filter;
            state.category = null;
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — PROMOTIONS TOC SCROLL LINKS
    // ─────────────────────────────────────────────
    document.querySelectorAll("#promotions-toc .toc-link").forEach(link => {
        link.addEventListener("click", () => {
            // Make sure we're on the promotions panel first
            if (state.filter !== "promotions") {
                state.filter = "promotions";
                state.category = null;
                loadPanel();
                // Scroll after a brief tick to allow the panel to render
                setTimeout(() => scrollToTarget(link.dataset.target, link), 80);
            } else {
                scrollToTarget(link.dataset.target, link);
            }
        });
    });

    function scrollToTarget(targetId, activeLink) {
        const target = document.getElementById(targetId);
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        document.querySelectorAll("#promotions-toc .toc-link").forEach(l =>
            l.classList.remove("toc-active")
        );
        if (activeLink) activeLink.classList.add("toc-active");
    }

    // ─────────────────────────────────────────────
    // EVENTS — CATEGORIES SIDEBAR LINKS (specific category)
    // ─────────────────────────────────────────────
    document.querySelectorAll(".toc-link--category").forEach(link => {
        link.addEventListener("click", () => {
            const cat = link.dataset.category;
            state.filter = "categories";
            state.category = cat;
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — HEADER FILTER UI
    // ─────────────────────────────────────────────
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
    // RESTORE SUBMENU OPEN STATE ON LOAD
    // ─────────────────────────────────────────────
    function restoreSubmenus() {
        if (state.filter === "promotions") {
            openSubmenu(promoToggleBtn, promoSubmenu);
        }
        if (state.filter === "categories") {
            openSubmenu(categoriesToggleBtn, categoriesSubmenu);
        }
    }

    // ─────────────────────────────────────────────
    // INITIAL LOAD
    // ─────────────────────────────────────────────
    restoreSubmenus();
    loadPanel();

});