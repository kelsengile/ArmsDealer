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
        dot.addEventListener('click', () => go(i));
        dotsWrap.appendChild(dot);
    });

    const dots = dotsWrap.querySelectorAll('.fc-dot');

    function go(n) {
        pages[cur].classList.remove('active');
        dots[cur].classList.remove('active');
        cur = (n + pages.length) % pages.length;
        pages[cur].classList.add('active');
        dots[cur].classList.add('active');
        pageLabel.textContent = pages[cur].dataset.label || ('Page ' + (cur + 1));
    }

    document.getElementById('fcPrev').addEventListener('click', () => go(cur - 1));
    document.getElementById('fcNext').addEventListener('click', () => go(cur + 1));

    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowLeft') go(cur - 1);
        if (e.key === 'ArrowRight') go(cur + 1);
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