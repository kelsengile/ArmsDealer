/* ──────────────────────────────────────────────────────────────────────
   SPECIFIC PRODUCT PAGE — JS
   ────────────────────────────────────────────────────────────────────── */

// ── Brand Navigation — go to brand section in products page ──────────
// NOTE: spGoToBrand / spGoToCategory / spGoToSubcategory are defined in the
// inline <script> block at the bottom of specificproduct.html (after this file
// loads). They set sp_open_nav so products.html knows which sidebar section to
// open on arrival. The stubs below are intentionally absent — do not add them
// here or the inline versions will still win (inline runs last) but the file
// becomes misleading.

// ── Image Gallery ────────────────────────────────────────────────────
const spActiveImg = document.getElementById('sp-active-img');
const spThumbs = document.querySelectorAll('.sp-thumb');

function spSetActive(thumb) {
    spThumbs.forEach(t => t.classList.remove('active'));
    thumb.classList.add('active');
    const newSrc = thumb.dataset.img;
    if (!newSrc || !spActiveImg) return;
    spActiveImg.style.opacity = '0';
    setTimeout(() => {
        spActiveImg.src = newSrc;
        spActiveImg.style.opacity = '1';
    }, 180);
}

// ── Quantity Stepper ─────────────────────────────────────────────────
let spQtyVal = 1;
const spQtyDisplay = document.getElementById('sp-qty-display');
const spQtyMinus = document.getElementById('sp-qty-minus');
const spQtyPlus = document.getElementById('sp-qty-plus');

function spSetQty(val) {
    spQtyVal = Math.max(1, Math.min(99, val));
    if (spQtyDisplay) spQtyDisplay.textContent = spQtyVal;
}

if (spQtyMinus) spQtyMinus.addEventListener('click', function (e) {
    e.stopPropagation();
    spSetQty(spQtyVal - 1);
});

if (spQtyPlus) spQtyPlus.addEventListener('click', function (e) {
    e.stopPropagation();
    spSetQty(spQtyVal + 1);
});

// ── Toast helper — delegates to global ArmsToast ─────────────────────
function spShowToast(msg, type) {
    const armsType = type === 'err' ? 'danger' : 'success';
    if (window.ArmsToast) {
        ArmsToast.show(msg, armsType);
    }
}

// ── Update cart badge — delegates to global updateCartCount if available ──
function spUpdateCartBadge(count) {
    if (typeof window.updateCartCount === 'function') {
        window.updateCartCount(count);
    } else {
        document.querySelectorAll('.cart-badge').forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.classList.add('visible');
                badge.style.display = '';
            } else {
                badge.textContent = '';
                badge.classList.remove('visible');
                badge.style.display = 'none';
            }
        });
    }
}

// ── Live Currency Switching ───────────────────────────────────────────
// Updates all prices on this page whenever the navbar currency selector
// changes — no page reload required.
// Strategy 1: intercept window.fetch calls to /set-currency (catches
//             programmatic changes made by navbarfunctions / settingspanel).
// Strategy 2: listen directly on the #currencySelect <select> element
//             as a reliable fallback in case Strategy 1 misses anything.
(function spInitCurrencyWatch() {

    function fmt(n) {
        return Number(n).toLocaleString('en-US');
    }

    // ── Core: rewrite every price element on the page ─────────────────
    function applyPrices(symbol, rate) {
        const btn = document.getElementById('sp-add-cart-btn');
        const pricePhp = btn ? parseFloat(btn.dataset.pricePhp || 0) : 0;
        const discountPct = btn ? parseFloat(btn.dataset.discount || 0) : 0;

        if (!pricePhp) return; // no base price embedded — nothing to convert

        const oldPrice = Math.round(pricePhp * rate);
        const newPrice = Math.round(pricePhp * (1 - discountPct / 100) * rate);
        const hasDiscount = discountPct > 0;

        // ── Main price block ──────────────────────────────────────────
        document.querySelectorAll('.sp-price-new').forEach(el => {
            el.textContent = symbol + fmt(newPrice);
        });
        document.querySelectorAll('.sp-price-old').forEach(el => {
            el.textContent = symbol + fmt(oldPrice);
            el.style.display = hasDiscount ? '' : 'none';
        });
        document.querySelectorAll('.sp-discount-badge').forEach(el => {
            el.textContent = '\u2013' + Math.round(discountPct) + '%';
            el.style.display = hasDiscount ? '' : 'none';
        });
        document.querySelectorAll('.sp-currency-symbol').forEach(el => {
            el.textContent = symbol;
        });

        // ── Related product cards ─────────────────────────────────────
        document.querySelectorAll('.sp-related-card').forEach(card => {
            const cardPhp = parseFloat(card.dataset.pricePhp || 0);
            const cardDiscount = parseFloat(card.dataset.discount || 0);
            if (!cardPhp) return;
            const cardOld = Math.round(cardPhp * rate);
            const cardNew = Math.round(cardPhp * (1 - cardDiscount / 100) * rate);
            const cardHasDiscount = cardDiscount > 0;

            const newEl = card.querySelector('.sp-rel-price-new');
            const oldEl = card.querySelector('.sp-rel-price-old');
            const discEl = card.querySelector('.sp-rel-discount');
            if (newEl) newEl.textContent = symbol + fmt(cardNew);
            if (oldEl) { oldEl.textContent = symbol + fmt(cardOld); oldEl.style.display = cardHasDiscount ? '' : 'none'; }
            if (discEl) { discEl.textContent = '\u2013' + Math.round(cardDiscount) + '%'; discEl.style.display = cardHasDiscount ? '' : 'none'; }
        });
    }

    // ── Strategy 1: patch window.fetch to intercept /set-currency ────
    const _origFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
        const url = (typeof input === 'string' ? input : (input && input.url)) || '';
        const promise = _origFetch(input, init);
        if (url.includes('/set-currency')) {
            promise.then(function (resp) {
                return resp.clone().json();
            }).then(function (data) {
                if (data && data.ok && data.symbol != null && data.rate != null) {
                    applyPrices(data.symbol, data.rate);
                }
            }).catch(function () { /* swallow JSON parse errors */ });
        }
        return promise;
    };

    // ── Strategy 2: listen directly on the navbar currency <select> ───
    // This fires synchronously on user interaction, giving instant feedback
    // even before the /set-currency response arrives.
    function attachSelectListener() {
        const sel = document.getElementById('currencySelect');
        if (!sel) return;

        sel.addEventListener('change', function () {
            const code = this.value; // e.g. "USD"
            // POST to /set-currency — our patched fetch above will catch the
            // response and call applyPrices, so we don't need to duplicate
            // that logic here. Just fire the same request the navbar would.
            fetch('/api/set-currency', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ currency: code })
            }).catch(function () { /* network error — prices stay as-is */ });
        });
    }

    // Attach immediately if DOM is ready, otherwise wait.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachSelectListener);
    } else {
        attachSelectListener();
    }

})();

// ── Add to Cart ──────────────────────────────────────────────────────
const spCartBtn = document.getElementById('sp-add-cart-btn');

if (spCartBtn) {
    spCartBtn.addEventListener('click', function (e) {
        if (e.target.classList.contains('sp-qty-btn')) return;

        const productId = parseInt(this.dataset.productId, 10);
        const stock = parseInt(this.dataset.stock, 10) || 0;

        if (!productId) {
            spShowToast('Product ID missing', 'err');
            return;
        }

        // Check if sold out
        if (stock === 0) {
            spShowToast('This product is sold out', 'err');
            return;
        }

        this.style.opacity = '0.6';
        this.style.pointerEvents = 'none';

        fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
                item_type: 'product',
                item_id: productId,
                quantity: spQtyVal
            })
        })
            .then(r => {
                if (r.status === 401) {
                    window.location.href = '/login';
                    return null;
                }
                return r.json();
            })
            .then(data => {
                if (!data) return;
                if (data.ok) {
                    spShowToast('Added to cart \u00d7' + spQtyVal, 'ok');
                    spUpdateCartBadge(data.cart_count);
                    spSetQty(1);
                } else {
                    spShowToast(data.error || 'Could not add to cart', 'err');
                }
            })
            .catch(() => spShowToast('Network error', 'err'))
            .finally(() => {
                this.style.opacity = '';
                this.style.pointerEvents = '';
            });
    });
}