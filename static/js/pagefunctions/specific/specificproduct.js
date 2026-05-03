/* ──────────────────────────────────────────────────────────────────────
   SPECIFIC PRODUCT PAGE — JS
   ────────────────────────────────────────────────────────────────────── */

// ── Brand Navigation — go to brand section in products page ──────────
function spGoToBrand(e, el) {
    e.preventDefault();
    const slug = el.dataset.brandSlug;
    if (!slug) { window.location.href = el.href; return; }
    // Store the target brand slug so products page can auto-open it
    sessionStorage.setItem('sp_open_brand', slug);
    window.location.href = el.href;
}

// ── Category Navigation — go to category panel in products page ───────
function spGoToCategory(e, el) {
    e.preventDefault();
    const cat = el.dataset.categorySlug;
    if (!cat) { window.location.href = el.href; return; }
    // Store category so products page opens the correct panel
    sessionStorage.setItem('sp_open_category', cat);
    // Clear any leftover subcategory target
    sessionStorage.removeItem('sp_open_subcategory');
    window.location.href = el.href;
}

// ── Subcategory Navigation — go to category panel + scroll to subcategory ──
function spGoToSubcategory(e, el) {
    e.preventDefault();
    const cat = el.dataset.categorySlug;
    const sub = el.dataset.subcategorySlug;
    if (!cat) { window.location.href = el.href; return; }
    // Store both so products page opens the panel and scrolls to the section
    sessionStorage.setItem('sp_open_category', cat);
    if (sub) sessionStorage.setItem('sp_open_subcategory', sub);
    window.location.href = el.href;
}

// ── Image Gallery ────────────────────────────────────────────────────
const spActiveImg = document.getElementById('sp-active-img');
const spThumbs = document.querySelectorAll('.sp-thumb');

function spSetActive(thumb) {
    // Remove active from all
    spThumbs.forEach(t => t.classList.remove('active'));
    thumb.classList.add('active');

    const newSrc = thumb.dataset.img;
    if (!newSrc || !spActiveImg) return;

    // Fade transition
    spActiveImg.style.opacity = '0';
    setTimeout(() => {
        spActiveImg.src = newSrc;
        spActiveImg.style.opacity = '1';
    }, 180);
}

// ── Quantity Stepper ─────────────────────────────────────────────────
let spQtyVal = 1;
const spQtyDisplay = document.getElementById('sp-qty-display');

function spQty(delta) {
    spQtyVal = Math.max(1, Math.min(99, spQtyVal + delta));
    if (spQtyDisplay) spQtyDisplay.textContent = spQtyVal;
}

// ── Add to Cart ──────────────────────────────────────────────────────
// Wire up here — no inline Jinja needed
const spCartBtn = document.getElementById('sp-add-cart-btn');
if (spCartBtn) {
    spCartBtn.addEventListener('click', function () {
        // Stub — replace with your actual cart endpoint call
        console.log('Add to cart qty:', spQtyVal);
    });
}