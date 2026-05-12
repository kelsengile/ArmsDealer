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
})();


/* ── Search button clicks are handled by searchpanel.js ── */