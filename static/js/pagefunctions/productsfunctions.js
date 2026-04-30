document.addEventListener("DOMContentLoaded", () => {

    // ─────────────────────────────────────────────
    // STORAGE KEY
    // ─────────────────────────────────────────────
    const STORAGE_KEY = "productsPageState";

    // ─────────────────────────────────────────────
    // STATE
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
    const brandsToggleBtn = document.querySelector('[data-filter="brands"]');
    const brandsSubmenuAuthorized = document.getElementById("brands-toc-authorized");
    const brandsSubmenuRestricted = document.getElementById("brands-toc-restricted");

    // ─────────────────────────────────────────────
    // CATEGORY → API SLUG MAP
    // Maps the sidebar data-category values to the
    // slugs used in the categories table of the DB.
    // ─────────────────────────────────────────────
    const CATEGORY_SLUG_MAP = {
        firearms: "firearms",
        blades: "blades",
        blunts: "blunts",
        projectiles: "projectile",
        explosive: "explosives",
        electronic: "electronic",
        chemical: "chemical",
        biological: "biological",
        vehicle: "vehicle",
        cyber: "cyber",
        security: "security",
        ammunition: "ammunition",
        protective: "protective",
        tactical: "tactical",
        attachments: "attachments",
        maintenance: "maintenance-equipment",
        storage: "storage-equipment",
        communication: "communication",
        survival: "survival",
        training: "training-equipment",
    };

    // ─────────────────────────────────────────────
    // LANG / CURRENCY CHANGE → BUST CACHE
    // Listen for cookie changes triggered by the
    // navbar language / currency selectors so that
    // product cards re-fetch with fresh translations
    // and converted prices without needing a reload.
    // ─────────────────────────────────────────────
    function getCookie(name) {
        const m = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
        return m ? m[1] : null;
    }

    let _trackedLang = getCookie('lang') || 'english';
    let _trackedCurrency = getCookie('currency') || 'PHP';

    function clearProductCache() {
        Object.keys(_productCache).forEach(k => delete _productCache[k]);
    }

    // Poll every 300 ms — negligible overhead, fires only on change
    setInterval(() => {
        const lang = getCookie('lang') || 'english';
        const currency = getCookie('currency') || 'PHP';
        if (lang !== _trackedLang || currency !== _trackedCurrency) {
            _trackedLang = lang;
            _trackedCurrency = currency;
            clearProductCache();
            // Re-render the current panel so cards update immediately
            loadPanel();
        }
    }, 300);

    // ─────────────────────────────────────────────
    // PRODUCT CARD CACHE (per category + access)
    // ─────────────────────────────────────────────
    const _productCache = {};

    async function fetchCategoryProducts(categoryKey, access) {
        const cacheKey = `${categoryKey}__${access}`;
        if (_productCache[cacheKey]) return _productCache[cacheKey];

        const slug = CATEGORY_SLUG_MAP[categoryKey];
        if (!slug) return [];

        try {
            const resp = await fetch(`/api/products/${slug}?access=${access}`);
            if (!resp.ok) return [];
            const data = await resp.json();
            _productCache[cacheKey] = data.products || [];
            return _productCache[cacheKey];
        } catch (e) {
            console.error("Product fetch error:", e);
            return [];
        }
    }

    // ─────────────────────────────────────────────
    // RENDER FC-CARDS INTO SUB-SECTIONS
    // ─────────────────────────────────────────────

    /** Format a number with commas */
    function fmt(n) {
        return Number(n).toLocaleString("en-US");
    }

    /** Render filled + empty star SVGs for a rating (0-5, floored to int) */
    function buildStars(rating) {
        const full = Math.floor(rating || 0);
        const empty = 5 - full;
        const starFull = `<svg class="fc-star fc-star--full"  width="9" height="9" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg"><polygon points="6,1 7.8,4.2 11.5,4.7 8.8,7.3 9.5,11 6,9.2 2.5,11 3.2,7.3 0.5,4.7 4.2,4.2" fill="#f0c040"/></svg>`;
        const starEmpty = `<svg class="fc-star fc-star--empty" width="9" height="9" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg"><polygon points="6,1 7.8,4.2 11.5,4.7 8.8,7.3 9.5,11 6,9.2 2.5,11 3.2,7.3 0.5,4.7 4.2,4.2" fill="rgba(168,196,100,0.22)"/></svg>`;
        return starFull.repeat(full) + starEmpty.repeat(empty);
    }

    /** Cart icon SVG — shared across all cards */
    const CART_SVG = `<svg class="fc-cart-icon" width="9" height="9" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M1 1h2l2.4 8.4a1 1 0 0 0 1 .6h5.2a1 1 0 0 0 .97-.76L14 5H4" stroke="rgba(168,196,154,0.55)" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="6.5" cy="13" r="1" fill="rgba(168,196,154,0.55)"/><circle cx="11.5" cy="13" r="1" fill="rgba(168,196,154,0.55)"/></svg>`;

    /** Build a single fc-card element */
    function buildCard(p) {
        const card = document.createElement("div");
        card.className = "fc-card";
        card.dataset.slug = p.slug;
        card.dataset.price = p.new_price;
        card.dataset.rating = p.rating || 0;
        card.dataset.sales = p.sales_count || 0;
        card.style.cursor = "pointer";

        const hasDiscount = p.discount > 0;
        const imgPath = p.image_file
            ? `/static/assets/images/productsimages/${p.image_file}`
            : "";

        card.innerHTML = `
            <div class="fc-card-bg" ${imgPath ? `style="background-image:url('${imgPath}')"` : ""}>
                <div class="fc-overlay"></div>
            </div>
            <div class="fc-content">
                <div class="fc-name large">${p.name}</div>
                <div class="fc-pricing">
                    <div class="fc-pricing-row fc-pricing-row--price">
                        ${hasDiscount
                ? `<span class="fc-discount">&#8211;${Math.round(p.discount)}%</span>
                               <span class="fc-prices">
                                   <span class="fc-old">${p.currency_symbol}${fmt(p.old_price)}</span>
                                   <span class="fc-new large">${p.currency_symbol}${fmt(p.new_price)}</span>
                               </span>`
                : `<span class="fc-prices fc-prices--nodiscount">
                                   <span class="fc-new large">${p.currency_symbol}${fmt(p.new_price)}</span>
                               </span>`
            }
                    </div>
                    <div class="fc-pricing-row fc-pricing-row--meta">
                        <span class="fc-stars">${buildStars(p.rating)}</span>
                        <span class="fc-sold">${CART_SVG}<span class="fc-sold-count">${fmt(p.sales_count || 0)}</span></span>
                    </div>
                </div>
            </div>`;

        card.addEventListener("click", () => {
            window.location.href = `/product/${p.slug}`;
        });

        return card;
    }

    /**
     * Explicit map from HTML section id → exact DB subcategory slug.
     * This avoids the fragile suffix-guessing approach which fails whenever
     * the section id abbreviation doesn't match the DB slug suffix
     * (e.g. sub-smg → firearms-submachine-guns, sub-mg → firearms-machine-guns).
     */
    const SECTION_ID_TO_SUBCAT_SLUG = {
        // ── Firearms ────────────────────────────────────────────────────────────
        "sub-handguns": "firearms-handguns",
        "sub-rifles": "firearms-rifles",
        "sub-shotguns": "firearms-shotguns",
        "sub-smg": "firearms-submachine-guns",
        "sub-mg": "firearms-machine-guns",
        "sub-sniper": "firearms-sniper-rifles",
        "sub-carbines": "firearms-carbines",
        "sub-pdw": "firearms-pdw",
        // ── Blades ──────────────────────────────────────────────────────────────
        "sub-knives": "blades-knives",
        "sub-swords": "blades-swords",
        "sub-daggers": "blades-daggers",
        "sub-machetes": "blades-machetes",
        "sub-bayonets": "blades-bayonets",
        "sub-axes": "blades-axes",
        "sub-hatchets": "blades-hatchets",
        "sub-spears": "blades-combat-spears",
        "sub-polearms": "blades-polearms",
        "sub-throwing": "blades-throwing-knives",
        // ── Blunts ──────────────────────────────────────────────────────────────
        "sub-batons": "blunts-batons",
        "sub-clubs": "blunts-clubs",
        "sub-maces": "blunts-maces",
        "sub-hammers": "blunts-hammers",
        "sub-flails": "blunts-flails",
        "sub-nunchaku": "blunts-nunchaku",
        "sub-staves": "blunts-staves",
        "sub-saps": "blunts-saps",
        "sub-blackjacks": "blunts-blackjacks",
        // ── Projectiles ─────────────────────────────────────────────────────────
        "sub-bows": "projectile-bows",
        "sub-crossbows": "projectile-crossbows",
        "sub-slingshots": "projectile-slingshots",
        "sub-spearlaunchers": "projectile-spear-launchers",
        "sub-blowguns": "projectile-blowguns",
        "sub-javelin": "projectile-javelin-systems",
        "sub-pneumatic": "projectile-pneumatic-launchers",
        // ── Explosives ──────────────────────────────────────────────────────────
        "sub-grenades": "explosives-grenades",
        "sub-bombs": "explosives-bombs",
        "sub-mines": "explosives-mines",
        "sub-demolition": "explosives-demolition-charges",
        "sub-rockets": "explosives-rocket-launchers",
        "sub-mortars": "explosives-mortars",
        "sub-artillery": "explosives-artillery-shells",
        "sub-breaching": "explosives-breaching-charges",
        "sub-flashbangs": "explosives-flash-bangs",
        // ── Electronic ──────────────────────────────────────────────────────────
        "sub-tasers": "electronic-tasers",
        "sub-stunguns": "electronic-stun-guns",
        "sub-emp": "electronic-emp-devices",
        "sub-jamming": "electronic-jamming-devices",
        "sub-dew": "electronic-directed-energy-weapons",
        "sub-sonic": "electronic-sonic-devices",
        "sub-laser": "electronic-laser-dazzlers",
        // ── Chemical ────────────────────────────────────────────────────────────
        "sub-teargas": "chemical-tear-gas",
        "sub-smoke": "chemical-smoke-agents",
        "sub-incendiary": "chemical-incendiary",
        "sub-peppersprays": "chemical-pepper-sprays",
        "sub-aerosol": "chemical-aerosol-dispersants",
        "sub-rca": "chemical-riot-control",
        // ── Biological ──────────────────────────────────────────────────────────
        "sub-delivery": "biological-delivery-systems",
        "sub-containment": "biological-containment-units",
        "sub-biodetection": "biological-detection-equipment",
        "sub-neutralize": "biological-neutralization-agents",
        // ── Vehicle ─────────────────────────────────────────────────────────────
        "sub-armed": "vehicle-armed",
        "sub-drones": "vehicle-drones",
        "sub-naval": "vehicle-naval",
        "sub-aerial": "vehicle-aerial",
        "sub-antivehicle": "vehicle-anti-vehicle",
        // ── Cyber ───────────────────────────────────────────────────────────────
        "sub-malware": "cyber-malware-tools",
        "sub-exploits": "cyber-exploit-kits",
        "sub-hackdevices": "cyber-hacking-devices",
        "sub-intrusion": "cyber-intrusion-systems",
        "sub-exfil": "cyber-data-exfiltration",
        "sub-ransomware": "cyber-ransomware-platforms",
        // ── Security ────────────────────────────────────────────────────────────
        "sub-accesscontrol": "security-access-control",
        "sub-crowdcontrol": "security-crowd-control",
        "sub-nonlethal": "security-non-lethal",
        "sub-deterrent": "security-deterrent",
        "sub-restraint": "security-restraint",
        // ── Ammunition ──────────────────────────────────────────────────────────
        "sub-bullets": "ammo-bullets",
        "sub-shells": "ammo-shells",
        "sub-cartridges": "ammo-cartridges",
        "sub-energycells": "ammo-energy-cells",
        "sub-primers": "ammo-primers",
        "sub-propellants": "ammo-propellants",
        "sub-specialty": "ammo-specialty-rounds",
        "sub-caseless": "ammo-caseless",
        // ── Protective ──────────────────────────────────────────────────────────
        "sub-helmets": "protective-helmets",
        "sub-bodyarmor": "protective-body-armor",
        "sub-shields": "protective-shields",
        "sub-suits": "protective-suits",
        "sub-glasses": "protective-ballistic-glasses",
        "sub-hearing": "protective-hearing",
        "sub-gasmasks": "protective-gas-masks",
        "sub-blast": "protective-blast-resistant",
        // ── Tactical ────────────────────────────────────────────────────────────
        "sub-loadbearing": "tactical-load-bearing",
        "sub-holsters": "tactical-holsters",
        "sub-utilitybelts": "tactical-utility-belts",
        "sub-fieldkits": "tactical-field-kits",
        "sub-chestrigs": "tactical-chest-rigs",
        "sub-platecarriers": "tactical-plate-carriers",
        "sub-dropleg": "tactical-drop-leg",
        "sub-pouches": "tactical-modular-pouches",
        // ── Attachments ─────────────────────────────────────────────────────────
        "sub-suppressors": "attachments-suppressors",
        "sub-grips": "attachments-grips",
        "sub-lasersights": "attachments-laser-sights",
        "sub-foregrips": "attachments-foregrips",
        "sub-bipods": "attachments-bipods",
        "sub-muzzlebrakes": "attachments-muzzle-brakes",
        "sub-flashlights": "attachments-flashlights",
        "sub-bayonetmounts": "attachments-bayonet-mounts",
        // ── Maintenance ─────────────────────────────────────────────────────────
        "sub-cleaningkits": "maint-cleaning-kits",
        "sub-repairtools": "maint-repair-tools",
        "sub-lubricants": "maint-lubricants",
        "sub-boresnakes": "maint-bore-snakes",
        "sub-armorertools": "maint-armorer-tools",
        "sub-partskits": "maint-parts-kits",
        "sub-solventtraps": "maint-solvent-traps",
        // ── Storage ─────────────────────────────────────────────────────────────
        "sub-safes": "storage-safes",
        "sub-cases": "storage-cases",
        "sub-lockers": "storage-lockers",
        "sub-ammocans": "storage-ammo-cans",
        "sub-weaponracks": "storage-weapon-racks",
        "sub-concealment": "storage-concealment-furniture",
        "sub-transport": "storage-transport-containers",
        // ── Communication ───────────────────────────────────────────────────────
        "sub-radios": "comm-radios",
        "sub-signal": "comm-signal-devices",
        "sub-encryption": "comm-encryption-units",
        "sub-earpieces": "comm-earpieces",
        "sub-headsets": "comm-tactical-headsets",
        "sub-satellite": "comm-satellite",
        "sub-covert": "comm-covert-devices",
        // ── Survival ────────────────────────────────────────────────────────────
        "sub-firstaid": "survival-first-aid",
        "sub-rations": "survival-rations",
        "sub-water": "survival-water-purification",
        "sub-navigation": "survival-navigation",
        "sub-shelters": "survival-shelters",
        "sub-firestarters": "survival-fire-starters",
        "sub-multitools": "survival-multi-tools",
        "sub-tourniquets": "survival-tourniquets",
        // ── Training ────────────────────────────────────────────────────────────
        "sub-simulators": "training-simulators",
        "sub-dummy": "training-dummy-equipment",
        "sub-targets": "training-targets",
        "sub-manuals": "training-manuals",
        "sub-blueguns": "training-blue-guns",
        "sub-fof": "training-force-on-force",
        "sub-recoil": "training-recoil-trainers",
    };

    /**
     * After the category panel HTML is injected, fetch its products
     * and fill each `.specific-sub-body` with cards grouped by subcategory slug.
     * Uses the explicit SECTION_ID_TO_SUBCAT_SLUG map for exact matching.
     */
    async function populateCategoryProducts(categoryKey) {
        const products = await fetchCategoryProducts(categoryKey, state.access);

        // Index products by their subcategory_slug for O(1) lookup
        const bySubcat = {};
        for (const p of products) {
            const key = p.subcategory_slug || "__none__";
            if (!bySubcat[key]) bySubcat[key] = [];
            bySubcat[key].push(p);
        }

        // Find all sub-sections currently rendered in selectionContent
        const subSections = selectionContent.querySelectorAll(".specific-sub");

        subSections.forEach(section => {
            const sectionId = section.id; // e.g. "sub-smg"
            const body = section.querySelector(".specific-sub-body");
            if (!body) return;

            // Look up the exact DB slug from the explicit map
            const dbSlug = SECTION_ID_TO_SUBCAT_SLUG[sectionId];
            if (!dbSlug) return; // unmapped section — leave as-is

            const matched = bySubcat[dbSlug] || [];

            if (matched.length === 0) {
                // Leave the empty-section message in place
                return;
            }

            // Replace empty-section placeholder with a card grid
            body.classList.remove("empty-section");
            body.innerHTML = "";

            const grid = document.createElement("div");
            grid.className = "fc-grid";

            matched.forEach(p => grid.appendChild(buildCard(p)));
            body.appendChild(grid);
        });

        // Re-apply any active sort after grids are populated
        applySort();
    }

    // ─────────────────────────────────────────────
    // BRAND SUBMENU HELPERS
    // ─────────────────────────────────────────────
    function activeBrandsSubmenu() {
        return state.access === "restricted"
            ? brandsSubmenuRestricted
            : brandsSubmenuAuthorized;
    }
    function inactiveBrandsSubmenu() {
        return state.access === "restricted"
            ? brandsSubmenuAuthorized
            : brandsSubmenuRestricted;
    }

    // ─────────────────────────────────────────────
    // LOAD PANEL
    // ─────────────────────────────────────────────
    function loadPanel() {
        let templateId;

        if (state.filter === "categories" && state.category) {
            templateId = `panel-category-${state.category}`;
        } else if (state.filter === "brands" && state.brand) {
            templateId = `panel-brand-${state.brand}`;
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

        selectionContent.closest(".products-content").classList.toggle(
            "restricted-mode", state.access === "restricted"
        );

        bindCategoryItems();
        addScrollSpacing();
        updateHeaderTitle();
        syncActiveStates();
        saveState();

        // After the panel is rendered, populate products if it's a specific category
        if (state.filter === "categories" && state.category && CATEGORY_SLUG_MAP[state.category]) {
            populateCategoryProducts(state.category);
        }
    }

    // ─────────────────────────────────────────────
    // BIND CATEGORY/BRAND ITEM CLICKS
    // ─────────────────────────────────────────────
    function bindCategoryItems() {
        selectionContent.querySelectorAll("[data-category]").forEach(item => {
            item.addEventListener("click", () => {
                const cat = item.dataset.category;
                if (!cat) return;
                state.category = cat;
                highlightCategoryLink(cat);
                loadPanel();
            });
        });

        selectionContent.querySelectorAll("[data-brand]").forEach(item => {
            item.addEventListener("click", () => {
                const brand = item.dataset.brand;
                if (!brand) return;
                state.brand = brand;
                highlightBrandLink(brand);
                loadPanel();
            });
        });
    }

    // ─────────────────────────────────────────────
    // SIDEBAR HIGHLIGHT HELPERS
    // ─────────────────────────────────────────────
    function highlightCategoryLink(cat) {
        document.querySelectorAll(".toc-link--category").forEach(l => {
            l.classList.toggle("toc-active", l.dataset.category === cat);
        });
    }

    function highlightBrandLink(brand) {
        document.querySelectorAll(".toc-link--brand").forEach(l => {
            if (!l.dataset.crossAccess) {
                l.classList.toggle("toc-active", l.dataset.brand === brand);
            }
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
        } else if (state.filter === "brands" && state.brand) {
            const brandName = state.brand.replace(/-/g, " ").replace(/\b\w/g, c => c.toUpperCase());
            filterText = `Brands · ${brandName}`;
        } else {
            filterText = cap(state.filter);
        }

        selectionTitle.textContent = `${accessText} · ${filterText}`;
        heroTypeDisplay.textContent = accessText;
    }

    // ─────────────────────────────────────────────
    // SYNC ACTIVE STATES
    // ─────────────────────────────────────────────
    function syncActiveStates() {
        accessBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.access === state.access);
        });
        filterBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.filter === state.filter);
        });

        if (state.filter === "categories" && state.category) {
            highlightCategoryLink(state.category);
        } else {
            document.querySelectorAll(".toc-link--category").forEach(l =>
                l.classList.remove("toc-active")
            );
        }

        if (state.filter === "brands" && state.brand) {
            highlightBrandLink(state.brand);
        } else {
            document.querySelectorAll(".toc-link--brand").forEach(l =>
                l.classList.remove("toc-active")
            );
        }

        if (state.filter === "brands") {
            openSubmenu(brandsToggleBtn, activeBrandsSubmenu());
            closeSubmenu(brandsToggleBtn, inactiveBrandsSubmenu());
        }
    }

    // ─────────────────────────────────────────────
    // SCROLL SPACING (promo panels)
    // ─────────────────────────────────────────────
    function addScrollSpacing() {
        selectionContent.querySelectorAll(".promo-section").forEach(
            sec => (sec.style.minHeight = "260px")
        );
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
        menu.classList.contains("open")
            ? closeSubmenu(btn, menu)
            : openSubmenu(btn, menu);
    }

    // ─────────────────────────────────────────────
    // EVENTS — ACCESS TOGGLE
    // ─────────────────────────────────────────────
    accessBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            state.access = btn.dataset.access;
            if (state.filter === "brands") {
                state.brand = null;
                openSubmenu(brandsToggleBtn, activeBrandsSubmenu());
                closeSubmenu(brandsToggleBtn, inactiveBrandsSubmenu());
            }
            // Clear product cache so fresh data is fetched for new access level
            Object.keys(_productCache).forEach(k => delete _productCache[k]);
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
                toggleSubmenu(promoToggleBtn, promoSubmenu);
                closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
                closeSubmenu(brandsToggleBtn, brandsSubmenuAuthorized);
                closeSubmenu(brandsToggleBtn, brandsSubmenuRestricted);
                state.filter = "promotions";
                state.category = null;
                loadPanel();
                return;
            }

            if (filter === "categories") {
                const isOpen = categoriesSubmenu.classList.contains("open");
                closeSubmenu(promoToggleBtn, promoSubmenu);
                closeSubmenu(brandsToggleBtn, brandsSubmenuAuthorized);
                closeSubmenu(brandsToggleBtn, brandsSubmenuRestricted);

                if (isOpen && state.category) {
                    state.filter = "categories";
                    state.category = null;
                    loadPanel();
                    return;
                }
                if (isOpen) {
                    closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
                    return;
                }
                openSubmenu(categoriesToggleBtn, categoriesSubmenu);
                state.filter = "categories";
                state.category = null;
                loadPanel();
                return;
            }

            if (filter === "brands") {
                const active = activeBrandsSubmenu();
                const inactive = inactiveBrandsSubmenu();
                const isOpen = active.classList.contains("open");
                closeSubmenu(promoToggleBtn, promoSubmenu);
                closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
                closeSubmenu(brandsToggleBtn, inactive);

                if (isOpen && state.brand) {
                    state.filter = "brands";
                    state.brand = null;
                    loadPanel();
                    return;
                }
                if (isOpen) {
                    closeSubmenu(brandsToggleBtn, active);
                    return;
                }
                openSubmenu(brandsToggleBtn, active);
                state.filter = "brands";
                state.brand = null;
                loadPanel();
                return;
            }

            closeSubmenu(promoToggleBtn, promoSubmenu);
            closeSubmenu(categoriesToggleBtn, categoriesSubmenu);
            closeSubmenu(brandsToggleBtn, brandsSubmenuAuthorized);
            closeSubmenu(brandsToggleBtn, brandsSubmenuRestricted);
            state.filter = filter;
            state.category = null;
            state.brand = null;
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — PROMOTIONS TOC SCROLL LINKS
    // ─────────────────────────────────────────────
    document.querySelectorAll("#promotions-toc .toc-link").forEach(link => {
        link.addEventListener("click", () => {
            if (state.filter !== "promotions") {
                state.filter = "promotions";
                state.category = null;
                loadPanel();
                setTimeout(() => scrollToTarget(link.dataset.target, link), 80);
            } else {
                scrollToTarget(link.dataset.target, link);
            }
        });
    });

    function scrollToTarget(targetId, activeLink) {
        const target = document.getElementById(targetId);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
        document.querySelectorAll("#promotions-toc .toc-link").forEach(l =>
            l.classList.remove("toc-active")
        );
        if (activeLink) activeLink.classList.add("toc-active");
    }

    // ─────────────────────────────────────────────
    // EVENTS — CATEGORIES SIDEBAR LINKS
    // ─────────────────────────────────────────────
    document.querySelectorAll(".toc-link--category").forEach(link => {
        link.addEventListener("click", () => {
            state.filter = "categories";
            state.category = link.dataset.category;
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — BRANDS SIDEBAR LINKS
    // ─────────────────────────────────────────────
    document.querySelectorAll(".toc-link--brand:not(.toc-link--cross-access)").forEach(link => {
        link.addEventListener("click", () => {
            state.filter = "brands";
            state.brand = link.dataset.brand;
            loadPanel();
        });
    });

    document.querySelectorAll(".toc-link--cross-access").forEach(link => {
        link.addEventListener("click", () => {
            state.access = link.dataset.crossAccess;
            state.filter = "brands";
            state.brand = link.dataset.brand;
            openSubmenu(brandsToggleBtn, activeBrandsSubmenu());
            closeSubmenu(brandsToggleBtn, inactiveBrandsSubmenu());
            loadPanel();
        });
    });

    // ─────────────────────────────────────────────
    // EVENTS — HEADER FILTER UI  (sort by sales / price / rating)
    // ─────────────────────────────────────────────

    /**
     * Sort all .fc-grid elements currently in selectionContent.
     * Only one sort axis is active at a time; activating a new one
     * clears the others.
     */
    function applySort() {
        const salesVal = document.getElementById("hf-sales") ? document.getElementById("hf-sales").value : "";
        const priceVal = document.getElementById("hf-price") ? document.getElementById("hf-price").value : "";
        const ratingVal = document.getElementById("hf-rating") ? document.getElementById("hf-rating").value : "";

        // Determine active sort axis (last changed wins via the change handler)
        let key = null, dir = 1;
        if (salesVal) { key = "sales"; dir = salesVal === "high-low" ? -1 : 1; }
        if (priceVal) { key = "price"; dir = priceVal === "high-low" ? -1 : 1; }
        if (ratingVal) { key = "rating"; dir = ratingVal === "high-low" ? -1 : 1; }

        selectionContent.querySelectorAll(".fc-grid").forEach(grid => {
            const cards = Array.from(grid.querySelectorAll(".fc-card"));
            if (key) {
                cards.sort((a, b) => {
                    const va = parseFloat(a.dataset[key]) || 0;
                    const vb = parseFloat(b.dataset[key]) || 0;
                    return (va - vb) * dir;
                });
            }
            // Re-append in sorted order (detach + append = reorder, no clone needed)
            cards.forEach(c => grid.appendChild(c));
        });
    }

    hfSelects.forEach(select => {
        select.addEventListener("change", () => {
            // When one select changes, clear the others so only one axis is active
            hfSelects.forEach(s => {
                if (s !== select) {
                    s.value = "";
                    s.style.borderColor = "";
                }
            });
            select.style.borderColor = select.value ? "#a8c47a" : "";
            applySort();
        });
    });

    clearBtn.addEventListener("click", () => {
        hfSelects.forEach(select => {
            select.value = "";
            select.style.borderColor = "";
        });
        applySort(); // restores original insertion order (no-op sort)
    });

    // ─────────────────────────────────────────────
    // RESTORE SUBMENU OPEN STATE ON LOAD
    // ─────────────────────────────────────────────
    function restoreSubmenus() {
        if (state.filter === "promotions") openSubmenu(promoToggleBtn, promoSubmenu);
        if (state.filter === "categories") openSubmenu(categoriesToggleBtn, categoriesSubmenu);
        if (state.filter === "brands") {
            openSubmenu(brandsToggleBtn, activeBrandsSubmenu());
            closeSubmenu(brandsToggleBtn, inactiveBrandsSubmenu());
        }
    }

    // ─────────────────────────────────────────────
    // INITIAL LOAD
    // ─────────────────────────────────────────────
    restoreSubmenus();
    loadPanel();

    // ─────────────────────────────────────────────
    // HAMBURGER / SIDEBAR DRAWER (≤1100px)
    // ─────────────────────────────────────────────
    const hamburgerBtn = document.getElementById("sidebar-hamburger");
    const sidebarEl = document.getElementById("products-sidebar");
    const overlayEl = document.getElementById("sidebar-overlay");

    function openSidebar() {
        sidebarEl.classList.add("drawer-open");
        overlayEl.classList.add("visible");
        hamburgerBtn.classList.add("is-open");
        hamburgerBtn.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        sidebarEl.classList.remove("drawer-open");
        overlayEl.classList.remove("visible");
        hamburgerBtn.classList.remove("is-open");
        hamburgerBtn.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
    }

    function isMobileBreakpoint() {
        return window.matchMedia("(max-width: 1100px)").matches;
    }

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener("click", () => {
            sidebarEl.classList.contains("drawer-open")
                ? closeSidebar()
                : openSidebar();
        });
    }

    if (overlayEl) overlayEl.addEventListener("click", closeSidebar);

    document.querySelectorAll(".toc-link, .filter-btn:not(.filter-btn--has-sub)").forEach(el => {
        el.addEventListener("click", () => {
            if (isMobileBreakpoint()) closeSidebar();
        });
    });

    window.addEventListener("resize", () => {
        if (!isMobileBreakpoint()) closeSidebar();
    });

    document.addEventListener("keydown", e => {
        if (e.key === "Escape" && sidebarEl.classList.contains("drawer-open")) {
            closeSidebar();
        }
    });

});