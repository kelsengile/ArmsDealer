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