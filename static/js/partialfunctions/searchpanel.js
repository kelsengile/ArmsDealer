/**
 * searchpanel.js — ArmsDealer
 * Mirrors accountpanel.js open/close pattern exactly.
 * Save as: static/js/partialfunctions/searchpanel.js
 * Include in base.html after navbarfunctions.js
 */
(function () {
    'use strict';

    /* ── Element refs ─────────────────────────────────────────────── */
    const overlay = document.getElementById('searchOverlay');
    const sidebar = document.getElementById('searchSidebar');
    const closeBtn = document.getElementById('searchClose');
    const input = document.getElementById('searchInput');
    const clearBtn = document.getElementById('searchInputClear');
    const body = document.getElementById('searchBody');

    if (!sidebar) return; // partial not present

    /* ── Open / Close ─────────────────────────────────────────────── */
    function openSearch() {
        overlay.classList.add('active');
        sidebar.classList.add('open');
        document.body.style.overflow = 'hidden';
        // Focus input after transition starts
        setTimeout(() => input && input.focus(), 80);
    }

    function closeSearch() {
        overlay.classList.remove('active');
        sidebar.classList.remove('open');
        document.body.style.overflow = '';
    }

    // Overlay click → close
    overlay.addEventListener('click', closeSearch);
    // Close button
    if (closeBtn) closeBtn.addEventListener('click', closeSearch);
    // Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSearch();
    });

    /* ── Trigger: all .nav-btn-search buttons (desktop + drawer) ──── */
    document.querySelectorAll('.nav-btn-search').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close mobile drawer if open (same pattern as account panel)
            const drawer = document.getElementById('navDrawer');
            const hamburger = document.getElementById('navHamburger');
            if (drawer && drawer.classList.contains('open')) {
                drawer.classList.remove('open');
                if (hamburger) {
                    hamburger.classList.remove('open');
                    hamburger.setAttribute('aria-expanded', 'false');
                }
                document.body.style.overflow = '';
            }
            openSearch();
        });
    });

    /* ── Clear button ─────────────────────────────────────────────── */
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            input.value = '';
            clearBtn.classList.remove('visible');
            resetBody();
            input.focus();
        });
    }

    /* ── Input handler — debounced ────────────────────────────────── */
    let debounceTimer = null;
    let lastQuery = '';

    input.addEventListener('input', () => {
        const q = input.value.trim();

        // Toggle clear button
        if (clearBtn) clearBtn.classList.toggle('visible', q.length > 0);

        clearTimeout(debounceTimer);

        if (q.length < 2) {
            if (q.length === 0) resetBody();
            else showMsg('search-idle-msg', '⍝ KEEP TYPING...');
            lastQuery = '';
            return;
        }

        showMsg('search-loading-msg', 'SCANNING DATABASE…');

        debounceTimer = setTimeout(() => {
            if (q !== lastQuery) {
                lastQuery = q;
                runSearch(q);
            }
        }, 280);
    });

    /* ── API fetch ────────────────────────────────────────────────── */
    async function runSearch(q) {
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            renderResults(data, q);
        } catch (_) {
            showMsg('search-empty-msg', '◌ CONNECTION ERROR');
        }
    }

    /* ── Render ───────────────────────────────────────────────────── */
    function renderResults(data, q) {
        const products = data.products || [];
        const brands = data.brands || [];
        const isGuest = data.is_guest;

        if (!products.length && !brands.length) {
            showMsg('search-empty-msg', `◌ NO RESULTS FOR "${esc(q.toUpperCase())}"`);
            return;
        }

        let html = '';

        /* ── Products ─────────────────────────────────────────────── */
        if (products.length) {
            html += `<div class="search-section-label">Products</div>`;

            for (const p of products) {
                const meta = [p.brand_name, p.category_slug].filter(Boolean).join(' · ').toUpperCase();
                const restricted = (!isGuest && p.is_authorized === 0)
                    ? `<span class="search-restricted-tag">RESTRICTED</span>` : '';
                const price = `${esc(p.currency_symbol)}${(p.new_price || 0).toLocaleString()}`;
                const href = p.category_slug
                    ? `/products/${esc(p.category_slug)}#${esc(p.slug)}`
                    : '/products';

                html += `
                <a class="search-result-row" href="${href}">
                  <span class="search-result-icon">
                    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="2" y="1" width="12" height="14" rx="1" stroke="currentColor" stroke-width="1.4"/>
                      <path d="M5 5h6M5 8h6M5 11h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    </svg>
                  </span>
                  <span class="search-result-text">
                    <span class="search-result-name">${esc(p.name)}</span>
                    <span class="search-result-meta">${esc(meta)} &nbsp;${price}</span>
                  </span>
                  ${restricted}
                  <span class="search-result-arrow">
                    <svg width="8" height="8" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                      <path d="M5 2l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </span>
                </a>`;
            }

            // "View all products" link
            html += `
            <a class="search-view-all-link" href="/products?q=${encodeURIComponent(q)}">
              <span class="search-result-icon" style="opacity:0.4">
                <svg width="13" height="13" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </span>
              VIEW ALL PRODUCT RESULTS
              <span class="search-result-arrow">
                <svg width="8" height="8" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 2l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </span>
            </a>`;
        }

        /* ── Brands ───────────────────────────────────────────────── */
        if (brands.length) {
            if (products.length) html += `<div class="search-divider"></div>`;
            html += `<div class="search-section-label">Brands</div>`;

            for (const b of brands) {
                const count = b.product_count > 0
                    ? `${b.product_count} product${b.product_count !== 1 ? 's' : ''}`
                    : 'no products';
                const restricted = (!isGuest && b.is_authorized === 0)
                    ? `<span class="search-restricted-tag">RESTRICTED</span>` : '';

                html += `
                <a class="search-result-row brand-row" href="/products?brand=${encodeURIComponent(b.slug)}">
                  <span class="search-result-icon">
                    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M8 1l2 4.5h4.5L10.7 8.7l1.5 4.8L8 11l-4.2 2.5 1.5-4.8L1.5 5.5H6z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>
                    </svg>
                  </span>
                  <span class="search-result-text">
                    <span class="search-result-name">${esc(b.name)}</span>
                    <span class="search-result-meta">${esc(count.toUpperCase())}</span>
                  </span>
                  ${restricted}
                  <span class="search-result-arrow">
                    <svg width="8" height="8" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
                      <path d="M5 2l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </span>
                </a>`;
            }
        }

        body.innerHTML = html;

        // Close panel when a result is clicked
        body.querySelectorAll('a').forEach((a) => {
            a.addEventListener('click', () => closeSearch());
        });
    }

    /* ── Helpers ──────────────────────────────────────────────────── */
    function resetBody() {
        body.innerHTML = `
        <div class="search-idle-msg" id="searchIdleMsg">
            <span>⍝</span> AWAITING INPUT
        </div>`;
    }

    function showMsg(cls, text) {
        body.innerHTML = `<div class="${cls}">${text}</div>`;
    }

    function esc(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

})();