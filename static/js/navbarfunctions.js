/**
 * NavbarScript.js — ArmsDealer
 **/
(function () {
    // 'use strict';
    // /* ──────────────────────────────────────────────────────────────────────────
    //     SCROLL-HIDE BEHAVIOUR
    // ───────────────────────────────────────────────────────────────────────────── */
    // const header = document.querySelector('.site-header');
    // if (header) {
    //     let lastScrollY = window.scrollY;
    //     let ticking = false;
    //     const SCROLL_THRESHOLD = 80; // px before hide kicks in
    //     function handleScroll() {
    //         const currentY = window.scrollY;
    //         const delta = currentY - lastScrollY;
    //         // Add scrolled shadow class
    //         if (currentY > 10) {
    //             header.classList.add('nav-scrolled');
    //         } else {
    //             header.classList.remove('nav-scrolled');
    //         }
    //         // Only hide after threshold
    //         if (currentY > SCROLL_THRESHOLD) {
    //             if (delta > 0) {
    //                 // Scrolling DOWN — hide
    //                 header.classList.add('nav-hidden');
    //                 closeDrawer(); // also close mobile menu if open
    //             } else if (delta < -4) {
    //                 // Scrolling UP (at least 4px) — reveal
    //                 header.classList.remove('nav-hidden');
    //             }
    //         } else {
    //             // Near top — always visible
    //             header.classList.remove('nav-hidden');
    //         }
    //         lastScrollY = currentY;
    //         ticking = false;
    //     }
    //     window.addEventListener('scroll', () => {
    //         if (!ticking) {
    //             requestAnimationFrame(handleScroll);
    //             ticking = true;
    //         }
    //     }, { passive: true });
    // }
    /* /* ──────────────────────────────────────────────────────────────────────────
      //     ACTIVE PAGE HIGHLIGHT 
      // ───────────────────────────────────────────────────────────────────────────── */
    // Match nav links against the current URL path — works for any page
    const currentPath = window.location.pathname.toLowerCase();
    const currentSegment = currentPath.replace(/\/+$/, '').split('/').filter(Boolean).pop() || '';
    const allNavLinks = document.querySelectorAll('.nav-links a, .nav-drawer a');
    allNavLinks.forEach((link) => {
        const href = (link.getAttribute('href') || '').toLowerCase();
        if (!href || href === '/' || href === '#') return;
        const linkSegment = href.replace(/\?.*$/, '').replace(/\/+$/, '').split('/').filter(Boolean).pop() || '';
        if (linkSegment && currentSegment && linkSegment === currentSegment) {
            link.classList.add('nav-active');
            link.setAttribute('aria-current', 'page');
        }
    });
    /* ────────────────────────────────────────────────────────────────────────── 
  // HAMBURGER MENU 
  // ───────────────────────────────────────────────────────────────────────── */
    const hamburger = document.getElementById("navHamburger");
    const drawer = document.getElementById("navDrawer");
    let lastScrollY = window.scrollY;
    const SCROLL_THRESHOLD = 100;
    const DRAWER_BREAKPOINT = 980; // ← change this to your desired breakpoint
    function openDrawer() {
        if (!hamburger || !drawer) return;
        hamburger.classList.add("open");
        hamburger.setAttribute("aria-expanded", "true");
        drawer.classList.add("open");
        document.body.style.overflow = "";
    }
    function closeDrawer() {
        if (!hamburger || !drawer) return;
        hamburger.classList.remove("open");
        hamburger.setAttribute("aria-expanded", "false");
        drawer.classList.remove("open");
    }
    function toggleDrawer() {
        if (drawer && drawer.classList.contains("open")) {
            closeDrawer();
        } else {
            openDrawer();
        }
    }
    // ── Close drawer when viewport exceeds breakpoint ──────────────────────────
    function handleBreakpoint() {
        if (window.innerWidth > DRAWER_BREAKPOINT) {
            closeDrawer();
        }
    }
    // ResizeObserver watches the <body> width (fires less often than scroll)
    if (typeof ResizeObserver !== "undefined") {
        const resizeObserver = new ResizeObserver(() => handleBreakpoint());
        resizeObserver.observe(document.body);
    } else {
        // Fallback for older browsers
        window.addEventListener("resize", handleBreakpoint);
    }
    // ──────────────────────────────────────────────────────────────────────────
    if (hamburger) {
        hamburger.addEventListener("click", (e) => {
            e.stopPropagation();
            toggleDrawer();
        });
    }
    // Close on scroll after threshold
    window.addEventListener("scroll", () => {
        const currentScrollY = window.scrollY;
        if (
            drawer &&
            drawer.classList.contains("open") &&
            Math.abs(currentScrollY - lastScrollY) > SCROLL_THRESHOLD
        ) {
            closeDrawer();
        }
        lastScrollY = currentScrollY;
    });
    // Close on outside click
    document.addEventListener("click", (e) => {
        if (
            drawer &&
            drawer.classList.contains("open") &&
            !drawer.contains(e.target) &&
            !hamburger.contains(e.target)
        ) {
            closeDrawer();
        }
    });
    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeDrawer();
    });
    // Close drawer when a drawer link is clicked
    if (drawer) {
        drawer.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeDrawer);
        });
    }

    /* ── data-href buttons (cart redirect) ────────────────────────── */
    document.querySelectorAll(".nav-btn-cart[data-href]").forEach((btn) => {
        btn.addEventListener("click", () => {
            window.location.href = btn.dataset.href;
        });
    });

    /* ═══════════════════════════════════════════════════════════════
       NAVBAR LANGUAGE SELECT — write-through to armsdealer_region
       ─────────────────────────────────────────────────────────────
       The inline onchange="setLanguage(this.value)" in base.html calls
       setLanguage() which saves to localStorage['lang'] but NOT to the
       'armsdealer_region' bundle. On the next page load applyRegionToNavbar()
       reads armsdealer_region and overwrites the select, undoing the change.

       Fix: listen here (after the inline handler fires) and patch
       armsdealer_region.language so the two stores stay in sync.
       The navbar only has the five mapped values (english | filipino |
       japanese | spanish | mandarin) so we store them directly as-is —
       they are all valid keys in the settings panel's LANG_NAVBAR_MAP too.
    ═══════════════════════════════════════════════════════════════ */
    (function wireNavbarRegionSync() {
        var langSel = document.getElementById('languageSelect');
        if (langSel) {
            langSel.addEventListener('change', function () {
                var chosen = this.value; // e.g. 'filipino'
                try {
                    var region = JSON.parse(localStorage.getItem('armsdealer_region') || 'null') || {};
                    region.language = chosen;
                    localStorage.setItem('armsdealer_region', JSON.stringify(region));
                } catch (e) { /* storage unavailable — ignore */ }
                // Also keep the standalone 'lang' key in sync (used by translations.js DOMContentLoaded init)
                try { localStorage.setItem('lang', chosen); } catch (e) { }
                // Sync settings panel select if it happens to be on the same page
                var settingsLangSel = document.getElementById('settingsLanguageSelect');
                if (settingsLangSel) settingsLangSel.value = chosen;
            });
        }

        /* ── NAVBAR CURRENCY SELECT — same write-through pattern ── */
        var curSel = document.getElementById('currencySelect');
        if (curSel) {
            curSel.addEventListener('change', function () {
                var chosen = this.value; // e.g. 'USD'
                try {
                    var region = JSON.parse(localStorage.getItem('armsdealer_region') || 'null') || {};
                    region.currency = chosen;
                    localStorage.setItem('armsdealer_region', JSON.stringify(region));
                } catch (e) { }
                try { localStorage.setItem('currency', chosen); } catch (e) { }
                // Sync settings panel select if present
                var settingsCurSel = document.getElementById('settingsCurrencySelect');
                if (settingsCurSel) settingsCurSel.value = chosen;
            });
        }
    })();

    /* ═══════════════════════════════════════════════════════════════
       REGION PERSISTENCE
       ─────────────────────────────────────────────────────────────
       On every page load, read 'armsdealer_region' from localStorage
       (written by the Settings > Language & Region panel) and apply:

         • language  → sync the top-bar #languageSelect and call setLanguage()
         • currency  → sync the top-bar #currencySelect and call setCurrency()
         • lat / lng → update the .nav-coord decorative readout so it always
                       reflects the user's chosen timezone city coordinates,
                       shown as LAT / LNG in the navbar.

       The .nav-coord element is decorative (aria-hidden="true") so no
       accessibility impact from updating it here.
    ═══════════════════════════════════════════════════════════════ */
    (function applyRegionToNavbar() {
        var region;
        try {
            region = JSON.parse(localStorage.getItem('armsdealer_region') || 'null');
        } catch (e) { region = null; }
        if (!region) return;

        /* ── 1. Language ─────────────────────────────────────────── */
        // The navbar <select id="languageSelect"> carries:
        //   english | filipino | japanese | spanish | mandarin
        // The settings panel may store values outside that set; we map
        // them to the closest navbar value (same table as RegionSettings).
        var LANG_NAVBAR_MAP = {
            english: 'english',
            spanish: 'spanish',
            french: 'english',
            german: 'english',
            japanese: 'japanese',
            mandarin: 'mandarin',
            russian: 'english',
            arabic: 'english',
            filipino: 'filipino'
        };
        if (region.language) {
            var navbarLang = LANG_NAVBAR_MAP[region.language] || 'english';

            // Guard: if localStorage.lang disagrees with armsdealer_region.language
            // it means the user changed the navbar select on a previous page (which
            // writes to localStorage.lang but not yet to armsdealer_region).
            // In that case, trust localStorage.lang and patch armsdealer_region to
            // match so the two stores converge instead of fighting each other.
            var standaloneLang = null;
            try { standaloneLang = localStorage.getItem('lang'); } catch (e) { }
            if (standaloneLang && standaloneLang !== navbarLang) {
                // Navbar-driven change wins — update region bundle to match
                try {
                    region.language = standaloneLang;
                    localStorage.setItem('armsdealer_region', JSON.stringify(region));
                } catch (e) { }
                navbarLang = standaloneLang;
            }

            var langSel = document.getElementById('languageSelect');
            if (langSel && langSel.value !== navbarLang) {
                langSel.value = navbarLang;
            }
            // setLanguage() is defined in translations.js, which loads before
            // this script. Call it to apply the correct translations immediately.
            if (typeof setLanguage === 'function') {
                setLanguage(navbarLang);
            }
        }

        /* ── 2. Currency ─────────────────────────────────────────── */
        // The navbar <select id="currencySelect"> carries:
        //   PHP | USD | EUR | JPY | CNY
        var CURRENCY_NAVBAR_MAP = {
            PHP: 'PHP',
            USD: 'USD',
            EUR: 'EUR',
            GBP: 'USD',
            SGD: 'USD',
            JPY: 'JPY',
            CNY: 'CNY'
        };
        if (region.currency) {
            var navbarCur = CURRENCY_NAVBAR_MAP[region.currency] || region.currency;
            var curSel = document.getElementById('currencySelect');
            if (curSel && curSel.value !== navbarCur) {
                curSel.value = navbarCur;
            }
            // setCurrency() is defined in translations.js / currency.js.
            // Only call if it exists so we don't break pages where it isn't loaded.
            if (typeof setCurrency === 'function') {
                setCurrency(navbarCur);
            }
        }

        /* ── 3. Nav coordinates (timezone-derived) ───────────────── */
        // The .nav-coord element looks like:
        //   <div class="nav-coord" aria-hidden="true">
        //     <div><span>LAT</span> 14.5995° N</div>
        //     <div><span>LNG</span> 120.9842° E</div>
        //   </div>
        // We replace the text node that follows each <span> with the
        // stored city coordinates, keeping the <span> label intact.
        if (region.lat && region.lng) {
            var coordEl = document.querySelector('.nav-coord');
            if (coordEl) {
                var divs = coordEl.querySelectorAll('div');

                // Update LAT row
                if (divs[0]) {
                    var spanLat = divs[0].querySelector('span');
                    if (spanLat) {
                        // Remove stale text nodes after the span
                        var node = spanLat.nextSibling;
                        while (node) {
                            var next = node.nextSibling;
                            if (node.nodeType === Node.TEXT_NODE) spanLat.parentNode.removeChild(node);
                            node = next;
                        }
                        spanLat.parentNode.appendChild(document.createTextNode(' ' + region.lat));
                    }
                }

                // Update LNG row
                if (divs[1]) {
                    var spanLng = divs[1].querySelector('span');
                    if (spanLng) {
                        var node2 = spanLng.nextSibling;
                        while (node2) {
                            var next2 = node2.nextSibling;
                            if (node2.nodeType === Node.TEXT_NODE) spanLng.parentNode.removeChild(node2);
                            node2 = next2;
                        }
                        spanLng.parentNode.appendChild(document.createTextNode(' ' + region.lng));
                    }
                }
            }
        }
    })();

})();


/* ── Search button clicks are handled by searchpanel.js ── */