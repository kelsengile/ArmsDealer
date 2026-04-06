/**
 * ========================================
 * COMBINED JAVASCRIPT - COMPLETE
 * ========================================
 * All sections organized with variable names tracked
 */

// ===========================================
// SECTION 1: HERO CAROUSEL
// ===========================================
(function () {
    const carousel = document.getElementById('heroCarousel');
    const slides = carousel.querySelectorAll('.hero-slide');
    const dotsWrap = document.getElementById('heroDots');
    const counter = document.getElementById('heroCurrentNum');
    const prevBtn = document.getElementById('heroPrev');
    const nextBtn = document.getElementById('heroNext');

    let current = 0;
    let animating = false;
    let autoTimer = null;
    const TOTAL = slides.length;
    const DELAY = 10000; // ms between auto-advances

    /* ── Build dot indicators ─────────────────────────────── */
    slides.forEach((_, i) => {
        const dot = document.createElement('button');
        dot.className = 'hero-dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
        dot.addEventListener('click', () => goTo(i, i > current ? 'right' : 'left'));
        dotsWrap.appendChild(dot);
    });

    const dots = dotsWrap.querySelectorAll('.hero-dot');

    /* ── Text elements selector ───────────────────────────── */
    const TEXT_SELECTORS = '.hero-tag, .hero-title, .hero-subtitle, .hero-cta';

    /* Hard-reset text children so CSS transitions re-fire every time */
    function resetTextChildren(slide) {
        slide.querySelectorAll(TEXT_SELECTORS).forEach(el => {
            el.style.transition = 'none';
            el.style.opacity = '0';
            el.style.transform = 'translateY(14px)';
        });
        /* Force reflow so the reset is painted before restoring transitions */
        void slide.offsetHeight;
        slide.querySelectorAll(TEXT_SELECTORS).forEach(el => {
            el.style.transition = '';
            el.style.opacity = '';
            el.style.transform = '';
        });
    }

    /* ── Core transition ──────────────────────────────────── */
    function goTo(next, direction) {
        if (animating || next === current) return;
        animating = true;

        const outSlide = slides[current];
        const inSlide = slides[next];

        /* 1. Remove active from outgoing slide */
        outSlide.classList.remove('active');

        /* 2. Force-reset text children on the incoming slide BEFORE
              adding .active, so CSS transitions see a real 0→1 change */
        resetTextChildren(inSlide);

        /* 3. Position incoming slide off-screen with no transition */
        inSlide.style.transition = 'none';
        inSlide.style.opacity = '0';
        inSlide.style.transform = direction === 'right'
            ? 'translateX(60px) scale(1.04)'
            : 'translateX(-60px) scale(1.04)';

        /* 4. Force reflow */
        void inSlide.offsetHeight;

        /* 5. Restore transition and activate */
        inSlide.style.transition = '';
        inSlide.style.opacity = '';
        inSlide.style.transform = '';
        inSlide.classList.add('active');

        /* Update dots & counter */
        dots[current].classList.remove('active');
        dots[next].classList.add('active');
        counter.textContent = String(next + 1).padStart(2, '0');

        current = next;

        /* Unlock after transition completes */
        setTimeout(() => { animating = false; }, 850);

        resetAuto();
    }

    function goPrev() { goTo((current - 1 + TOTAL) % TOTAL, 'left'); }
    function goNext() { goTo((current + 1) % TOTAL, 'right'); }

    prevBtn.addEventListener('click', goPrev);
    nextBtn.addEventListener('click', goNext);

    /* ── Auto-advance ─────────────────────────────────────── */
    function startAuto() { autoTimer = setInterval(goNext, DELAY); }
    function resetAuto() { clearInterval(autoTimer); startAuto(); }

    startAuto();

    /* ── Pause on hover ───────────────────────────────────── */
    carousel.addEventListener('mouseenter', () => clearInterval(autoTimer));
    carousel.addEventListener('mouseleave', startAuto);

    /* ── Keyboard support ─────────────────────────────────── */
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') goPrev();
        if (e.key === 'ArrowRight') goNext();
    });

    /* ── Touch / swipe support ────────────────────────────── */
    let touchStartX = 0;
    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    carousel.addEventListener('touchend', (e) => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) > 40) dx < 0 ? goNext() : goPrev();
    }, { passive: true });

})();


// ===========================================
// SECTION 2: CAROUSEL DATA & CATEGORY MAP
// ===========================================
const carouselData = {
    weapons: [
        { name: 'Firearms', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Blades', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Blunts', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Projectile', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Explosives', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Electronic', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Chemical', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Biological', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Vehicle', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Cyber', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Security', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' }
    ],
    equipment: [
        { name: 'Ammunition', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Protective', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Tactical', image: '../../../Assets/Images/PageImages/ImbeddedImages/rmsDealerLogo.png' },
        { name: 'Attachments', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Maintenance', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Storage', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Cases', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Communication', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Survival', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Training', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' }
    ],
    services: [
        { name: 'Manufacturing', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Customization', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Maintenance', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Transport', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Storage', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Training', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Protection', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Consulting', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Research', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Testing', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Disposal', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Surveillance', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' },
        { name: 'Contracting', image: '../../../Assets/Images/PageImages/ImbeddedImages/ArmsDealerLogo.png' }
    ]
};

const categoryPageMap = {
    // WEAPONS CATEGORIES
    'Firearms': '/pages/products/firearms.html',
    'Blades': '/pages/products/blades.html',
    'Blunts': '/pages/products/blunts.html',
    'Projectile': '/pages/products/projectile.html',
    'Explosives': '/pages/products/explosives.html',
    'Electronic': '/pages/products/electronic.html',
    'Chemical': '/pages/products/chemical.html',
    'Biological': '/pages/products/biological.html',
    'Vehicle': '/pages/products/vehicle.html',
    'Cyber': '/pages/products/cyber.html',
    'Security': '/pages/products/security.html',

    // EQUIPMENT CATEGORIES
    'Ammunition': '/pages/products/ammunition.html',
    'Protective': '/pages/products/protective.html',
    'Tactical': '/pages/products/tactical.html',
    'Attachments': '/pages/products/attachments.html',
    'Maintenance': '/pages/products/maintenance.html',
    'Storage': '/pages/products/storage.html',
    'Cases': '/pages/products/cases.html',
    'Communication': '/pages/products/communication.html',
    'Survival': '/pages/products/survival.html',
    'Training': '/pages/products/training.html',

    // SERVICES CATEGORIES
    'Manufacturing': '/pages/services/manufacturing.html',
    'Customization': '/pages/services/customization.html',
    'Maintenance': '/pages/services/maintenance.html',
    'Transport': '/pages/services/transport.html',
    'Storage': '/pages/services/storage.html',
    'Training': '/pages/services/training.html',
    'Protection': '/pages/services/protection.html',
    'Consulting': '/pages/services/consulting.html',
    'Research': '/pages/services/research.html',
    'Testing': '/pages/services/testing.html',
    'Disposal': '/pages/services/disposal.html',
    'Surveillance': '/pages/services/surveillance.html',
    'Contracting': '/pages/services/contracting.html'
};


// ===========================================
// SECTION 3: CATEGORY CAROUSEL FUNCTIONS
// ===========================================
let currentCategory = 'weapons';
let autoScrollId = null;
let resetTimeoutId = null;
let isScrolling = false;
let direction = 1; // 1 = right, -1 = left

function getWrapperEl() {
    return document.querySelector('.carousel-wrapper');
}

function getTrackEl() {
    return document.querySelector('.carousel-track');
}

function getMaxScroll() {
    const wrapperEl = getWrapperEl();
    const trackEl = getTrackEl();
    return trackEl.scrollWidth - wrapperEl.clientWidth;
}

function startAutoScroll() {
    clearInterval(autoScrollId);
    clearTimeout(resetTimeoutId);

    let scrollSpeed = 1.5;
    const wrapperEl = getWrapperEl();

    autoScrollId = setInterval(() => {
        const currentScroll = wrapperEl.scrollLeft;
        const maxScroll = getMaxScroll();

        let newScroll = currentScroll + scrollSpeed * direction;

        if (newScroll >= maxScroll) {
            newScroll = maxScroll;
            direction = -1;
        } else if (newScroll <= 0) {
            newScroll = 0;
            direction = 1;
        }

        wrapperEl.scrollLeft = newScroll;
    }, 30);
}

function stopAutoScroll() {
    clearInterval(autoScrollId);
    clearTimeout(resetTimeoutId);
}

function renderCategory(categoryName) {
    const wrapperEl = getWrapperEl();
    const trackEl = getTrackEl();
    const data = carouselData[categoryName];

    // Clear existing cards
    trackEl.innerHTML = '';

    // Create new cards for the selected category
    data.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'category-rect';
        card.dataset.index = index;
        card.dataset.name = item.name;

        const imageDiv = document.createElement('div');
        imageDiv.className = 'category-image';

        const img = document.createElement('img');
        img.src = item.image;
        img.alt = item.name;
        imageDiv.appendChild(img);

        const label = document.createElement('div');
        label.className = 'category-label';
        label.textContent = item.name;

        card.appendChild(imageDiv);
        card.appendChild(label);
        trackEl.appendChild(card);

        // Add click handler
        card.addEventListener('click', (e) => {
            const categoryName = card.dataset.name;
            const targetPage = categoryPageMap[categoryName];

            trackEl.querySelectorAll('.category-rect').forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            if (targetPage) {
                window.location.href = targetPage;
            } else {
                console.warn(`No page mapping found for: ${categoryName}`);
            }
        });
    });

    // Reset scroll position
    wrapperEl.scrollLeft = 0;
    direction = 1;
    isScrolling = false;

    // Restart auto scroll
    startAutoScroll();
}

function setupCategoryButtons() {
    const buttonContainer = document.querySelector('.category-buttons');
    if (!buttonContainer) return;

    ['Weapons', 'Equipment', 'Services'].forEach((label) => {
        const button = document.createElement('button');
        button.className = 'category-btn';
        button.textContent = label;
        button.dataset.category = label.toLowerCase();

        if (label.toLowerCase() === currentCategory) {
            button.classList.add('active');
        }

        button.addEventListener('click', () => {
            const categoryName = button.dataset.category;

            // Update active button
            document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Update category and render
            currentCategory = categoryName;
            renderCategory(categoryName);
        });

        buttonContainer.appendChild(button);
    });
}

function setupScrollListeners() {
    const wrapperEl = getWrapperEl();
    const trackEl = getTrackEl();

    wrapperEl.addEventListener('mousedown', () => {
        isScrolling = true;
        stopAutoScroll();
    });

    wrapperEl.addEventListener('wheel', (e) => {
        isScrolling = true;
        stopAutoScroll();
    }, { passive: true });

    wrapperEl.addEventListener('scroll', () => {
        if (isScrolling) {
            clearTimeout(resetTimeoutId);
            resetTimeoutId = setTimeout(() => {
                isScrolling = false;
                startAutoScroll();
            }, 3000);
        }
    });

    wrapperEl.addEventListener('mouseup', () => {
        isScrolling = false;
    });

    wrapperEl.addEventListener('mouseleave', () => {
        if (isScrolling) {
            isScrolling = false;
            resetTimeoutId = setTimeout(() => {
                startAutoScroll();
            }, 3000);
        }
    });
}


// ===========================================
// SECTION 4: SMOOTH SCROLL & CTA HANDLERS
// ===========================================
/**
 * Smooth scroll behavior for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        } else {
            console.log('Navigate to: ' + this.getAttribute('href'));
        }
    });
});

/**
 * CTA Button Handler
 */
function handleCTA(action) {
    console.log('User clicked: ' + action);
    // Replace with your actual navigation logic
    if (action === 'create account') {
        alert('Redirecting to product catalog...');
    }
}


// ===========================================
// SECTION 5: INTERSECTION OBSERVER (SCROLL ANIMATION)
// ===========================================
/**
 * Add subtle animation to trust cards on scroll
 */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function (entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for lazy animation
document.querySelectorAll('.trust-card, .process-step').forEach(el => {
    el.style.opacity = '0.95'; // Ensure visibility
    observer.observe(el);
});


// ===========================================
// SECTION 6: HOVER EFFECTS & Z-INDEX
// ===========================================
/**
 * Add hover effects to interactive elements
 */
document.querySelectorAll('.cta-btn, .trust-card, .process-step').forEach(element => {
    element.addEventListener('mouseenter', function () {
        // Optional: Add subtle feedback here
        this.style.zIndex = '100';
    });
    element.addEventListener('mouseleave', function () {
        this.style.zIndex = '1';
    });
});


// ===========================================
// SECTION 7: FEATURED CAROUSEL (FC)
// ===========================================
(function () {
    const pages = Array.from(document.querySelectorAll('.fc-page'));
    const dotsWrap = document.getElementById('fcDots');
    const pageLabel = document.getElementById('fcPageLabel');
    let cur = 0;

    pages.forEach((p, i) => {
        const dot = document.createElement('div');
        dot.className = 'fc-dot' + (i === 0 ? ' active' : '');
        const label = document.createElement('div');
        label.className = 'fc-dot-label';
        label.textContent = p.dataset.label || ('Page ' + (i + 1));
        dot.appendChild(label);
        dot.addEventListener('click', () => fcGo(i));
        dotsWrap.appendChild(dot);
    });

    const dots = dotsWrap.querySelectorAll('.fc-dot');

    function fcGo(n) {
        pages[cur].classList.remove('active');
        dots[cur].classList.remove('active');
        cur = (n + pages.length) % pages.length;
        pages[cur].classList.add('active');
        dots[cur].classList.add('active');
        pageLabel.textContent = pages[cur].dataset.label || ('Page ' + (cur + 1));
    }

    document.getElementById('fcPrev').addEventListener('click', () => fcGo(cur - 1));
    document.getElementById('fcNext').addEventListener('click', () => fcGo(cur + 1));

    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowLeft') fcGo(cur - 1);
        if (e.key === 'ArrowRight') fcGo(cur + 1);
    });

    document.querySelectorAll('.fc-card').forEach(card => {
        const popup = card.querySelector('.fc-popup');
        if (!popup) return;

        card.addEventListener('mouseenter', function () {
            const data = JSON.parse(this.dataset.popup || '{}');
            if (!data.name) return;

            popup.querySelector('.fc-popup-name').textContent = data.name;
            popup.querySelector('.fc-popup-desc').textContent = data.desc;
            const tagsEl = popup.querySelector('.fc-popup-tags');
            tagsEl.innerHTML = '';
            (data.tags || []).forEach(t => {
                const span = document.createElement('span');
                span.className = 'fc-popup-tag';
                span.textContent = t;
                tagsEl.appendChild(span);
            });

            // Use card's viewport position to decide pop direction
            const rect = this.getBoundingClientRect();
            this.classList.toggle('pop-left', rect.left + rect.width / 2 > window.innerWidth / 2);
            this.classList.toggle('pop-up', rect.top + rect.height / 2 > window.innerHeight / 2);

            popup.style.display = 'block';
        });

        card.addEventListener('mouseleave', function () {
            popup.style.display = 'none';
        });
    });
})();


// ===========================================
// SECTION 8: INITIALIZATION
// ===========================================
/**
 * Initialize category carousel on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    setupCategoryButtons();
    setupScrollListeners();
    renderCategory(currentCategory);
});


// ===========================================
// SECTION 9: DEVELOPER CONSOLE MESSAGE
// ===========================================
/**
 * Console message for developers
 */
console.log('%c Welcome to Armsdealer Website ', 'background: #a8c49a; color: #1a1f1a; padding: 10px; font-size: 16px; font-weight: bold;');
console.log('%c Edit content in the HTML sections above ', 'color: #a8c49a; font-size: 12px;');
console.log('%c All CSS is embedded - no external files needed ', 'color: #a8c49a; font-size: 12px;');

// ════════════════════════════════════════════════════════════
// BUNDLES SECTION LOGIC
// ════════════════════════════════════════════════════════════

