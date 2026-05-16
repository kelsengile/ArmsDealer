// ───────────────────────────────────────────────────────────────────────────── //
//     ACCOUNTS PANEL FUNCTIONS
// ───────────────────────────────────────────────────────────────────────────── //
(function () {
    "use strict";

    const overlay = document.getElementById("accountOverlay");
    const sidebar = document.getElementById("accountSidebar");
    const closeBtn = document.getElementById("accountClose");
    const accountBtns = document.querySelectorAll(".nav-btn-account");

    if (!overlay || !sidebar) return; // guard: panel not in DOM

    /* ── Open / close ─────────────────────────────────────────────── */
    function openAccount() {
        overlay.classList.add("active");
        sidebar.classList.add("open");
        sidebar.setAttribute("aria-hidden", "false");
    }
    function closeAccount() {
        overlay.classList.remove("active");
        sidebar.classList.remove("open");
        sidebar.setAttribute("aria-hidden", "true");
    }

    /* ── Bind triggers ────────────────────────────────────────────── */
    accountBtns.forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            sidebar.classList.contains("open") ? closeAccount() : openAccount();
        });
    });
    if (closeBtn) closeBtn.addEventListener("click", closeAccount);
    overlay.addEventListener("click", closeAccount);

    /* ── Escape key ───────────────────────────────────────────────── */
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeAccount();
    });

    /* ── Forgot Password Toggle ───────────────────────────────────── */
    const forgotBtn = document.getElementById("forgotPasswordBtn");
    if (forgotBtn) {
        forgotBtn.addEventListener("click", () => {
            window.location.href = forgotBtn.dataset.target || "/forgot-password";
        });
    }

    /* ══════════════════════════════════════════════════════════════
       LIVE CART COUNT — syncs panel badge + navbar badge in real-time
       without a page reload.

       How it works:
         - window.updateCartCount(n) is the public API. Call it from
           any add-to-cart response handler (fetch callback, etc.).
         - It updates:
             1. The #panelCartCount element inside the account panel
             2. The #navCartBadge span on the desktop navbar cart button
         - It also fires a custom event "cartUpdated" so other scripts
           can react if needed.
    ══════════════════════════════════════════════════════════════ */
    const panelCartCount = document.getElementById("panelCartCount");
    const navCartBadge = document.getElementById("navCartBadge");

    /**
     * Update all cart count indicators site-wide.
     * @param {number} count  — new cart item count (integer >= 0)
     */
    window.updateCartCount = function (count) {
        count = parseInt(count, 10) || 0;

        /* ── Panel badge ──────────────────────────────────────────── */
        if (panelCartCount) {
            if (count > 0) {
                panelCartCount.textContent = count;
                panelCartCount.className = "acct-cart-count";
                panelCartCount.removeAttribute("data-translate");
            } else {
                panelCartCount.textContent = "EMPTY";
                panelCartCount.className = "acct-cart-empty";
                panelCartCount.setAttribute("data-translate", "accountpanelempty");
            }
        }

        /* ── All .cart-badge elements (navbar desktop + drawer) ───── */
        document.querySelectorAll(".cart-badge").forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? "99+" : count;
                badge.classList.add("visible");
                badge.style.display = "";
            } else {
                badge.textContent = "";
                badge.classList.remove("visible");
                badge.style.display = "none";
            }
        });

        /* ── #navCartBadge specifically (legacy compat) ───────────── */
        if (navCartBadge) {
            if (count > 0) {
                navCartBadge.textContent = count > 99 ? "99+" : count;
                navCartBadge.classList.add("visible");
            } else {
                navCartBadge.textContent = "";
                navCartBadge.classList.remove("visible");
            }
        }

        /* ── Broadcast so other scripts can react ─────────────────── */
        window.dispatchEvent(new CustomEvent("cartUpdated", { detail: { count } }));
    };

    /* ── Initialise badge from the panel's server-rendered count ─── */
    (function initCartBadge() {
        if (panelCartCount && panelCartCount.classList.contains("acct-cart-count")) {
            const initialCount = parseInt(panelCartCount.textContent, 10) || 0;
            window.updateCartCount(initialCount);
        }
    })();

    /* ══════════════════════════════════════════════════════════════
       WALLET CURRENCY CONVERSION
       — mirrors the same currency codes & localStorage keys used by
         navbarfunctions.js / the top-bar #currencySelect.

       How it works:
         - PHP balance is embedded in the DOM as data-wallet-php so we
           always convert FROM the source-of-truth PHP value.
         - On load, and any time the currency changes (select event or
           cross-tab storage event), we read localStorage['currency']
           (the same key navbarfunctions.js writes) and update the
           symbol + figure spans.
         - Rates are approximate display rates — same approach used
           everywhere else on the site for client-side conversion.
    ══════════════════════════════════════════════════════════════ */
    const WALLET_RATES = {
        PHP: { symbol: '₱', rate: 1 },
        USD: { symbol: '$', rate: 0.0175 },
        EUR: { symbol: '€', rate: 0.0161 },
        JPY: { symbol: 'JP¥', rate: 2.71 },
        CNY: { symbol: 'CN¥', rate: 0.127 },
    };

    const walletAmount = document.getElementById('panelWalletAmount');
    const walletSymbol = document.getElementById('panelWalletSymbol');
    const walletFigure = document.getElementById('panelWalletFigure');

    function applyWalletCurrency(code) {
        if (!walletAmount || !walletSymbol || !walletFigure) return;
        const phpBalance = parseFloat(walletAmount.dataset.walletPhp) || 0;
        const cur = WALLET_RATES[code] || WALLET_RATES['PHP'];
        const converted = phpBalance * cur.rate;
        // JPY gets 0 decimals, all others 2
        const formatted = converted.toLocaleString('en-US', {
            minimumFractionDigits: code === 'JPY' ? 0 : 2,
            maximumFractionDigits: code === 'JPY' ? 0 : 2,
        });
        walletSymbol.textContent = cur.symbol;
        walletFigure.textContent = formatted;
    }

    // Maps any code to the nearest supported one — mirrors CURRENCY_NAVBAR_MAP
    const CURRENCY_MAP = { PHP: 'PHP', USD: 'USD', EUR: 'EUR', GBP: 'USD', SGD: 'USD', JPY: 'JPY', CNY: 'CNY' };

    function readAndApplyCurrency() {
        let code = 'PHP';
        try {
            // Primary: standalone key written by navbar & settings selects
            const standalone = localStorage.getItem('currency');
            if (standalone) {
                code = standalone;
            } else {
                // Fallback: armsdealer_region bundle
                const region = JSON.parse(localStorage.getItem('armsdealer_region') || 'null');
                if (region && region.currency) code = region.currency;
            }
        } catch (e) { /* storage unavailable */ }
        code = CURRENCY_MAP[code] || 'PHP';
        applyWalletCurrency(code);
    }

    // ── Initial render on page load ────────────────────────────────
    readAndApplyCurrency();

    // ── React to navbar #currencySelect changes on THIS page ───────
    const curSelect = document.getElementById('currencySelect');
    if (curSelect) {
        curSelect.addEventListener('change', readAndApplyCurrency);
    }

    // ── React to currency changes made in other tabs ───────────────
    window.addEventListener('storage', function (e) {
        if (e.key === 'currency' || e.key === 'armsdealer_region') {
            readAndApplyCurrency();
        }
    });

})();