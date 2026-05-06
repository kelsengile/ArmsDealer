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
        if (!navCartBadge) return;
        if (panelCartCount && panelCartCount.classList.contains("acct-cart-count")) {
            const initialCount = parseInt(panelCartCount.textContent, 10) || 0;
            if (initialCount > 0) {
                navCartBadge.textContent = initialCount;
                navCartBadge.classList.add("visible");
            }
        }
    })();

})();