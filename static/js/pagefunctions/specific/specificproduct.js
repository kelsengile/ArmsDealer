/* ──────────────────────────────────────────────────────────────────────
   SPECIFIC PRODUCT PAGE — JS
   ────────────────────────────────────────────────────────────────────── */

// ── Brand Navigation — go to brand section in products page ──────────
function spGoToBrand(e, el) {
    e.preventDefault();
    const slug = el.dataset.brandSlug;
    if (!slug) { window.location.href = el.href; return; }
    sessionStorage.setItem('sp_open_brand', slug);
    window.location.href = el.href;
}

// ── Category Navigation — go to category panel in products page ───────
function spGoToCategory(e, el) {
    e.preventDefault();
    const cat = el.dataset.categorySlug;
    if (!cat) { window.location.href = el.href; return; }
    sessionStorage.setItem('sp_open_category', cat);
    sessionStorage.removeItem('sp_open_subcategory');
    window.location.href = el.href;
}

// ── Subcategory Navigation ──────────────────────────────────────────
function spGoToSubcategory(e, el) {
    e.preventDefault();
    const cat = el.dataset.categorySlug;
    const sub = el.dataset.subcategorySlug;
    if (!cat) { window.location.href = el.href; return; }
    sessionStorage.setItem('sp_open_category', cat);
    if (sub) sessionStorage.setItem('sp_open_subcategory', sub);
    window.location.href = el.href;
}

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

// ── Toast helper ─────────────────────────────────────────────────────
function spShowToast(msg, type) {
    let toast = document.getElementById('sp-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'sp-toast';
        toast.style.cssText = [
            'position:fixed', 'bottom:24px', 'right:24px', 'z-index:9999',
            'padding:10px 18px', 'border-radius:6px', 'font-size:13px',
            'font-family:inherit', 'letter-spacing:.04em',
            'box-shadow:0 4px 18px rgba(0,0,0,.35)',
            'opacity:0', 'transition:opacity .25s',
            'pointer-events:none'
        ].join(';');
        document.body.appendChild(toast);
    }
    if (type === 'err') {
        toast.style.background = '#c46a6a';
        toast.style.color = '#fff';
    } else {
        toast.style.background = 'var(--clr-accent, #a8c496)';
        toast.style.color = '#111';
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => { toast.style.opacity = '0'; }, 3000);
}

// ── Update cart badge — delegates to global updateCartCount if available ──
function spUpdateCartBadge(count) {
    if (typeof window.updateCartCount === 'function') {
        // accountpanel.js is loaded — it handles panel + all .cart-badge elements
        window.updateCartCount(count);
    } else {
        // Fallback: update .cart-badge elements directly
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

// ── Add to Cart ──────────────────────────────────────────────────────
const spCartBtn = document.getElementById('sp-add-cart-btn');

if (spCartBtn) {
    spCartBtn.addEventListener('click', function (e) {
        // Ignore clicks that came from the qty stepper buttons
        if (e.target.classList.contains('sp-qty-btn')) return;

        const productId = parseInt(this.dataset.productId, 10);
        if (!productId) {
            spShowToast('Product ID missing', 'err');
            return;
        }

        // Disable button during request
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
} Kw