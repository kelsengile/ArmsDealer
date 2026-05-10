(function () {
    /* ── Nav routing ─────────────────────────────────────────── */
    const params = new URLSearchParams(window.location.search);
    const initSection = params.get('section') || null;

    function activateSection(section) {
        document.querySelectorAll('.setpage-nav-item').forEach(i => i.classList.remove('active'));
        document.querySelectorAll('.setpage-panel').forEach(p => p.classList.remove('active'));
        if (!section) {
            document.getElementById('setpanel-default').classList.add('active');
            return;
        }
        const btn = document.querySelector(`.setpage-nav-item[data-section="${section}"]`);
        const panel = document.getElementById(`setpanel-${section}`);
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
        else document.getElementById('setpanel-default').classList.add('active');
    }

    document.querySelectorAll('.setpage-nav-item').forEach(btn => {
        btn.addEventListener('click', function () {
            const sec = this.dataset.section;
            activateSection(sec);
            const url = new URL(window.location);
            url.searchParams.set('section', sec);
            window.history.replaceState({}, '', url);
        });
    });

    activateSection(initSection);

    /* ── Display name live preview ───────────────────────────── */
    const nameInput = document.getElementById('displayNameInput');
    if (nameInput) {
        nameInput.addEventListener('input', function () {
            const val = this.value.trim() || 'AD';
            document.getElementById('displayNamePreview').textContent = val || 'Arms Dealer';
            const initials = val.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || 'AD';
            document.getElementById('avatarInitials').textContent = initials;
        });
    }

    /* ── Password strength ───────────────────────────────────── */
    window.updatePasswordStrength = function (pw) {
        let score = 0;
        if (pw.length >= 8) score++;
        if (pw.length >= 12) score++;
        if (/[A-Z]/.test(pw)) score++;
        if (/[0-9]/.test(pw)) score++;
        if (/[^A-Za-z0-9]/.test(pw)) score++;
        const pct = Math.round((score / 5) * 100);
        const bar = document.getElementById('pwStrengthBar');
        const lbl = document.getElementById('pwStrengthLabel');
        const colors = ['#c0392b', '#c0392b', '#e8b84b', '#a8c47a', '#a8c47a'];
        const labels = ['WEAK', 'WEAK', 'FAIR', 'STRONG', 'VERY STRONG'];
        bar.style.width = pct + '%';
        bar.style.background = colors[score] || '#c0392b';
        lbl.textContent = pw.length === 0 ? 'ENTER PASSWORD TO CHECK STRENGTH' : (labels[score] || 'WEAK') + ' · ' + pct + '% STRENGTH';
    };

    /* ── 2FA toggle ──────────────────────────────────────────── */
    window.toggle2FA = function (cb) {
        const tag = document.getElementById('twoFaTag');
        const setup = document.getElementById('twoFaSetup');
        if (cb.checked) {
            tag.textContent = 'ENABLED';
            tag.className = 'set-tag set-tag--on';
            setup.style.display = 'block';
            renderQR();
        } else {
            tag.textContent = 'DISABLED';
            tag.className = 'set-tag set-tag--off';
            setup.style.display = 'none';
        }
    };

    function renderQR() {
        const pattern = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1];
        const grid = document.getElementById('qrGrid');
        if (!grid) return;
        grid.innerHTML = '';
        pattern.forEach(v => {
            const c = document.createElement('div');
            c.className = 'set-qr-cell' + (v ? ' on' : '');
            grid.appendChild(c);
        });
    }

    /* ── Quiet hours toggle ──────────────────────────────────── */
    window.toggleQuietHours = function (cb) {
        document.getElementById('quietHoursConfig').style.display = cb.checked ? 'block' : 'none';
    };

    /* ── Accent swatches ─────────────────────────────────────── */
    document.querySelectorAll('.set-swatch').forEach(sw => {
        sw.addEventListener('click', function () {
            document.querySelectorAll('.set-swatch').forEach(s => s.classList.remove('active'));
            this.classList.add('active');
        });
    });

    /* ── Delete modal ────────────────────────────────────────── */
    window.openDeleteModal = function () {
        document.getElementById('deleteModal').classList.add('open');
        document.getElementById('deleteConfirmInput').value = '';
        document.getElementById('confirmDeleteBtn').disabled = true;
        document.getElementById('confirmDeleteBtn').style.opacity = '0.4';
        document.getElementById('confirmDeleteBtn').style.cursor = 'not-allowed';
    };
    window.closeDeleteModal = function () {
        document.getElementById('deleteModal').classList.remove('open');
    };
    window.checkDeleteConfirm = function (val) {
        const btn = document.getElementById('confirmDeleteBtn');
        const ok = val.trim() === 'DELETE MY ACCOUNT';
        btn.disabled = !ok;
        btn.style.opacity = ok ? '1' : '0.4';
        btn.style.cursor = ok ? 'pointer' : 'not-allowed';
    };
    document.getElementById('deleteModal').addEventListener('click', function (e) {
        if (e.target === this) closeDeleteModal();
    });

    /* ── Save / toast feedback ───────────────────────────────── */
    window.saveSettings = function (section) {
        if (typeof showToast === 'function') {
            showToast('Settings saved', 'success');
        } else {
            const notice = document.createElement('div');
            notice.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#1c211c;border:1px solid var(--mil-bright);color:var(--mil-bright);font-family:var(--font-stencil);font-size:11px;letter-spacing:0.18em;text-transform:uppercase;padding:12px 20px;z-index:9999;';
            notice.textContent = '✓ SETTINGS SAVED';
            document.body.appendChild(notice);
            setTimeout(() => notice.remove(), 2800);
        }
    };
    window.resetSection = function (section) {
        if (typeof showToast === 'function') {
            showToast('Changes discarded', 'info');
        }
    };
    window.submitSupport = function () {
        if (typeof showToast === 'function') {
            showToast('Ticket submitted', 'success');
        } else {
            alert('Support ticket submitted.');
        }
    };
})();