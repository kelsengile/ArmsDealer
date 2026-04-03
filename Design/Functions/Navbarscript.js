/**
 * NavbarScript.js — ArmsDealer
 * Handles:
 *  1. Scroll-hide / scroll-reveal on the .site-header
 *  2. Active nav link highlighting based on body[data-page]
 *  3. Mobile hamburger toggle + drawer
 */

(function () {
    // 'use strict';

    // /* ── 1. SCROLL-HIDE BEHAVIOUR ───────────────────────────────────
    //    - Hides header when scrolling DOWN past 80px
    //    - Reveals header when scrolling UP by any amount
    // ─────────────────────────────────────────────────────────────── */
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

    /* ── 2. ACTIVE PAGE HIGHLIGHT ───────────────────────────────────
       Reads body[data-page] and adds .nav-active to the matching
       anchor in both .nav-links and .nav-drawer.
       Homepage gets NO highlight (per requirements).

       Usage: <body data-page="products"> on Products.html, etc.
       Valid values: products | services | contacts | about
       Leave attribute absent (or set to "home") for Homepage.
    ─────────────────────────────────────────────────────────────── */
    const currentPage = (document.body.dataset.page || 'home').toLowerCase();

    if (currentPage !== 'home') {
        // Match anchors whose href contains the page keyword
        const allNavLinks = document.querySelectorAll('.nav-links a, .nav-drawer a');
        allNavLinks.forEach(link => {
            const href = link.getAttribute('href') || '';
            const pageName = href.replace(/.*\/|\.html.*/g, '').toLowerCase();
            if (pageName === currentPage) {
                link.classList.add('nav-active');
                link.setAttribute('aria-current', 'page');
            }
        });
    }

    /* ── 3. HAMBURGER MENU ──────────────────────────────────────────
       Toggles .open on both the button and the drawer.
       Closes when clicking outside or pressing Escape.
    ─────────────────────────────────────────────────────────────── */
    const hamburger = document.getElementById('navHamburger');
    const drawer = document.getElementById('navDrawer');

    function openDrawer() {
        if (!hamburger || !drawer) return;
        hamburger.classList.add('open');
        hamburger.setAttribute('aria-expanded', 'true');
        drawer.classList.add('open');
        document.body.style.overflow = ''; // don't lock scroll on mobile
    }

    function closeDrawer() {
        if (!hamburger || !drawer) return;
        hamburger.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        drawer.classList.remove('open');
    }

    function toggleDrawer() {
        if (drawer && drawer.classList.contains('open')) {
            closeDrawer();
        } else {
            openDrawer();
        }
    }

    if (hamburger) {
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDrawer();
        });
    }

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (drawer && drawer.classList.contains('open')) {
            if (!header.contains(e.target)) {
                closeDrawer();
            }
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeDrawer();
    });

    // Close drawer when a drawer link is clicked (navigation)
    if (drawer) {
        drawer.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeDrawer);
        });
    }

})();