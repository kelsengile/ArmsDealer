/**
 * NavbarScript.js — ArmsDealer
**/

(function () {

    /* ──────────────────────────────────────────────────────────────────────────
    //     TRANSLATIONS
    // ───────────────────────────────────────────────────────────────────────────── */



    const translations = {
        english: {
            settings: "Settings",
            preferences: "Preferences",
            account: "Account",
            appearance: "Appearance",
            notifications: "Notifications",
            privacy_security: "Privacy & Security",
            general: "General",
            language_region: "Language & Region",
            help_support: "Help & Support",
            advanced: "Advanced",
            system_actions: "System Actions"
        },

        filipino: {
            settings: "Mga Setting",
            preferences: "Mga Kagustuhan",
            account: "Account",
            appearance: "Hitsura",
            notifications: "Mga Abiso",
            privacy_security: "Pagkapribado at Seguridad",
            general: "Pangkalahatan",
            language_region: "Wika at Rehiyon",
            help_support: "Tulong at Suporta",
            advanced: "Advanced",
            system_actions: "Mga Aksyon ng Sistema"
        },

        japanese: {
            settings: "設定",
            preferences: "設定項目",
            account: "アカウント",
            appearance: "外観",
            notifications: "通知",
            privacy_security: "プライバシーとセキュリティ",
            general: "一般",
            language_region: "言語と地域",
            help_support: "ヘルプとサポート",
            advanced: "詳細設定",
            system_actions: "システム操作"
        },

        spanish: {
            settings: "Configuración",
            preferences: "Preferencias",
            account: "Cuenta",
            appearance: "Apariencia",
            notifications: "Notificaciones",
            privacy_security: "Privacidad y Seguridad",
            general: "General",
            language_region: "Idioma y Región",
            help_support: "Ayuda y Soporte",
            advanced: "Avanzado",
            system_actions: "Acciones del Sistema"
        },

        mandarin: {
            settings: "设置",
            preferences: "偏好",
            account: "账户",
            appearance: "外观",
            notifications: "通知",
            privacy_security: "隐私与安全",
            general: "常规",
            language_region: "语言和地区",
            help_support: "帮助与支持",
            advanced: "高级",
            system_actions: "系统操作"
        }
    };

    function setLanguage(lang) {
        const elements = document.querySelectorAll("[data-translate]");

        elements.forEach(el => {
            const key = el.getAttribute("data-translate");

            el.textContent =
                translations[lang]?.[key] ||
                translations["english"][key] ||
                key;
        });

        localStorage.setItem("lang", lang);
    }


    window.setLanguage = setLanguage;

    document.addEventListener("DOMContentLoaded", () => {
        const savedLang = localStorage.getItem("lang") || "english";

        setLanguage(savedLang);

        const select = document.getElementById("languageSelect");
        if (select) select.value = savedLang;
    });


    /* ──────────────────────────────────────────────────────────────────────────
    //     SEETINGS PANEL
    // ───────────────────────────────────────────────────────────────────────────── */

    /* ── Element refs ───────────────────────────────────────────── */
    const overlay = document.getElementById('settingsOverlay');
    const sidebar = document.getElementById('settingsSidebar');
    const contentPane = document.getElementById('settingsContent');
    const closeBtn = document.getElementById('settingsClose');
    const openBtn = document.getElementById('settingsOpenBtn');

    /* ── Open / close ───────────────────────────────────────────── */
    function openSettings() {
        overlay.classList.add('active');
        sidebar.classList.add('open');
        // auto-open first pane
        const active = sidebar.querySelector('.set-item.active');
        if (active) loadPage(active.dataset.page, active);
    }

    function closeSettings() {
        overlay.classList.remove('active');
        sidebar.classList.remove('open');
        contentPane.classList.remove('open');
    }

    openBtn.addEventListener('click', openSettings);
    closeBtn.addEventListener('click', closeSettings);
    overlay.addEventListener('click', closeSettings);

    /* ── Escape key ─────────────────────────────────────────────── */
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeSettings();
    });


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

    /* /* ──────────────────────────────────────────────────────────────────────────
    //     HAMBURER MENU
    // ───────────────────────────────────────────────────────────────────────────── */
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