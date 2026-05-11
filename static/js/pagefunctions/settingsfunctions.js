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
            const initialsEl = document.getElementById('avatarInitials');
            if (initialsEl) initialsEl.textContent = initials;
        });
    }

    /* ── Profile image preview ───────────────────────────────── */
    window.previewProfileImage = function (input) {
        if (!input.files || !input.files[0]) return;
        const file = input.files[0];
        const reader = new FileReader();
        reader.onload = function (e) {
            const photo = document.getElementById('avatarPhoto');
            const initials = document.getElementById('avatarInitials');
            if (photo) {
                photo.src = e.target.result;
                photo.style.display = 'block';
            }
            if (initials) initials.style.display = 'none';

            const nameEl = document.getElementById('photoFilename');
            if (nameEl) {
                nameEl.textContent = '✓ ' + file.name;
                nameEl.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    };

    /* ── Payment option selection ────────────────────────────── */
    window.selectPaymentOpt = function (radio) {
        document.querySelectorAll('.set-payment-opt').forEach(el => el.classList.remove('active'));
        const label = radio.closest('.set-payment-opt');
        if (label) label.classList.add('active');
    };

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
    const deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('click', function (e) {
            if (e.target === this) closeDeleteModal();
        });
    }

    /* ── Save Account Settings (with optional image upload) ──── */
    window.saveAccountSettings = async function () {
        const imageInput = document.getElementById('profileImageInput');
        const hasImage = imageInput && imageInput.files && imageInput.files[0];

        /* Build FormData so we can include the file if present */
        const fd = new FormData();
        fd.append('username', (document.getElementById('displayNameInput')?.value || '').trim());
        fd.append('email', (document.getElementById('emailInput')?.value || '').trim());
        fd.append('contact_number', (document.getElementById('phoneInput')?.value || '').trim());
        fd.append('bio', (document.getElementById('bioInput')?.value || '').trim());
        fd.append('country', document.getElementById('countrySelect')?.value || '');
        fd.append('delivery_address', (document.getElementById('deliveryAddressInput')?.value || '').trim());
        /* Convert the displayed wallet value back to PHP before saving.
           The input carries a data-rate attribute (set server-side and kept in
           sync by saveCurrencyPreference) that holds the current currency's
           rate relative to PHP.  Dividing by that rate gives the PHP amount
           the DB should always store.
           e.g. displayed 25000 USD  ÷  rate 0.0175  ≈  1,428,571 PHP  */
        const walletInput = document.getElementById('walletBalanceInput');
        const displayedWallet = parseFloat(walletInput?.value) || 0;
        const activeRate = parseFloat(walletInput?.dataset.rate) || 1;
        const walletInPhp = activeRate !== 0 ? displayedWallet / activeRate : displayedWallet;
        fd.append('wallet_balance', walletInPhp.toFixed(2));
        const paymentRadio = document.querySelector('input[name="paymentMethod"]:checked');
        fd.append('payment_method', paymentRadio ? paymentRadio.value : 'cash_on_delivery');
        fd.append('social_link_1', (document.getElementById('socialLink1')?.value || '').trim());
        fd.append('social_link_2', (document.getElementById('socialLink2')?.value || '').trim());
        fd.append('social_link_3', (document.getElementById('socialLink3')?.value || '').trim());
        fd.append('social_link_4', (document.getElementById('socialLink4')?.value || '').trim());
        if (hasImage) {
            fd.append('profile_image', imageInput.files[0]);
        }

        try {
            const res = await fetch('/api/settings/account', {
                method: 'POST',
                body: fd
            });
            const data = await res.json();
            if (data.ok) {
                showToast('Settings saved', 'success');
                /* If server returned a new image filename, update the avatar src */
                if (data.profile_image) {
                    const photo = document.getElementById('avatarPhoto');
                    if (photo) {
                        photo.src = '/static/assets/images/userimages/' + data.profile_image;
                        photo.style.display = 'block';
                        const initialsEl = document.getElementById('avatarInitials');
                        if (initialsEl) initialsEl.style.display = 'none';
                    }
                }
            } else {
                showToast(data.error || 'Save failed', 'danger');
            }
        } catch (err) {
            showToast('Network error — could not save', 'danger');
        }
    };

    /* ── Generic save / toast ────────────────────────────────── */
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

    /* ── Currency preference — saves cookie via server endpoint ─── */
    window.saveCurrencyPreference = function (code) {
        fetch('/set-currency', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ currency: code })
        })
            .then(r => r.json())
            .then(data => {
                if (!data.ok) return;

                /* Update symbol span */
                const sym = document.getElementById('settingsWalletSymbol');
                if (sym) sym.textContent = data.symbol;

                /* Re-convert the wallet balance input to the new currency.
                   The input currently shows the value in the OLD currency.
                   We know the old rate (data-rate attr) and the new rate.
                   Flow: displayed_old / old_rate = PHP → PHP * new_rate = displayed_new */
                const walletInput = document.getElementById('walletBalanceInput');
                if (walletInput && data.rate != null) {
                    const oldRate = parseFloat(walletInput.dataset.rate) || 1;
                    const currentDisplayed = parseFloat(walletInput.value) || 0;
                    const phpAmount = oldRate !== 0 ? currentDisplayed / oldRate : currentDisplayed;
                    const newDisplayed = phpAmount * data.rate;
                    walletInput.value = newDisplayed.toFixed(2);
                    walletInput.dataset.rate = data.rate;
                }
            })
            .catch(() => { });
    };
})();