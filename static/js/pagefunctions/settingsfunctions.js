/* ========================================================================================================================================================
   SETTINGS PAGE FUNCTIONS
   Requires appearance.js to be loaded first (subbase.html loads it before this script).
   ======================================================================================================================================================== */

(function () {

    /* ── showToast shim — bridges legacy showToast() calls to ArmsToast.show() ── */
    function showToast(message, type) {
        if (window.ArmsToast && typeof window.ArmsToast.show === 'function') {
            window.ArmsToast.show(message, type || 'info');
        }
    }

    /* ═══════════════════════════════════════════════════════════════
       NAV PANEL SWITCHING
    ═══════════════════════════════════════════════════════════════ */
    var params = new URLSearchParams(window.location.search);
    var initSection = params.get('section') || null;

    function activateSection(section) {
        document.querySelectorAll('.setpage-nav-item').forEach(function (i) { i.classList.remove('active'); });
        document.querySelectorAll('.setpage-panel').forEach(function (p) { p.classList.remove('active'); });

        if (!section) {
            var def = document.getElementById('setpanel-default');
            if (def) def.classList.add('active');
            return;
        }
        var btn = document.querySelector('.setpage-nav-item[data-section="' + section + '"]');
        var panel = document.getElementById('setpanel-' + section);
        if (btn) btn.classList.add('active');
        if (panel) panel.classList.add('active');
        else {
            var def = document.getElementById('setpanel-default');
            if (def) def.classList.add('active');
        }
    }

    document.querySelectorAll('.setpage-nav-item').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var sec = this.dataset.section;
            activateSection(sec);
            var url = new URL(window.location);
            url.searchParams.set('section', sec);
            window.history.replaceState({}, '', url);

            // Load sessions lazily when privacy section is opened
            if (sec === 'privacy' && !window._sessionsLoaded) {
                window._sessionsLoaded = true;
                loadSessions();
            }
        });
    });

    activateSection(initSection);

    // Auto-load sessions if arriving directly via ?section=privacy
    if (initSection === 'privacy') {
        window._sessionsLoaded = true;
        loadSessions();
    }

    /* ═══════════════════════════════════════════════════════════════
       APPEARANCE — load saved settings into the UI controls
    ═══════════════════════════════════════════════════════════════ */

    function loadAppearanceIntoUI(settings) {
        // Color mode
        var colorModeSelect = document.getElementById('colorModeSelect');
        if (colorModeSelect) colorModeSelect.value = settings.colorMode || 'Dark (Default)';

        // Accent color swatches
        var targetSwatch = document.querySelector('#setpanel-appearance .set-swatch[data-color="' + (settings.accentColor || 'olive') + '"]');
        document.querySelectorAll('#setpanel-appearance .set-swatch').forEach(function (s) { s.classList.remove('active'); });
        if (targetSwatch) targetSwatch.classList.add('active');

        // Scanlines toggle
        var scanlinesToggle = document.getElementById('scanlinesToggle');
        if (scanlinesToggle) scanlinesToggle.checked = !!settings.scanlines;

        // Background opacity slider + label
        var bgOpacitySlider = document.getElementById('bgOpacity');
        var bgOpacityLabel = document.getElementById('bgOpacityVal');
        if (bgOpacitySlider) bgOpacitySlider.value = settings.bgOpacity != null ? settings.bgOpacity : 38;
        if (bgOpacityLabel) bgOpacityLabel.textContent = (settings.bgOpacity != null ? settings.bgOpacity : 38) + '%';

        // Background image options
        var targetBg = document.querySelector('#setpanel-appearance .set-bg-option[data-bg="' + (settings.bgImage || 'camobackground') + '"]');
        document.querySelectorAll('#setpanel-appearance .set-bg-option').forEach(function (o) { o.classList.remove('active'); });
        if (targetBg) targetBg.classList.add('active');

        // Font scale
        var fontScaleSelect = document.getElementById('fontScaleSelect');
        if (fontScaleSelect) fontScaleSelect.value = settings.fontScale || 'Default (12px)';

        // Monospace toggle
        var monospaceToggle = document.getElementById('monospaceToggle');
        if (monospaceToggle) monospaceToggle.checked = !!settings.monospaceBody;

        // Compact mode toggle
        var compactToggle = document.getElementById('compactToggle');
        if (compactToggle) compactToggle.checked = !!settings.compactMode;

        // Animations toggle
        var animationsToggle = document.getElementById('animationsToggle');
        if (animationsToggle) animationsToggle.checked = settings.animations !== false;
    }

    // Load saved (or default) settings into the UI on page load
    (function () {
        var saved = localStorage.getItem('armsdealer_appearance');
        var settings = saved ? JSON.parse(saved) : Object.assign({}, window.APPEARANCE_DEFAULTS || {});
        settings = Object.assign({}, window.APPEARANCE_DEFAULTS || {}, settings);
        loadAppearanceIntoUI(settings);
    })();

    /* ── Wire live-preview to every appearance control ─────────── */

    // Accent color swatches
    document.querySelectorAll('#setpanel-appearance .set-swatch').forEach(function (sw) {
        sw.addEventListener('click', function () {
            document.querySelectorAll('#setpanel-appearance .set-swatch').forEach(function (s) { s.classList.remove('active'); });
            this.classList.add('active');
            window.previewAppearanceSetting && window.previewAppearanceSetting('accentColor', this.dataset.color);
        });
    });

    // Background image options
    document.querySelectorAll('#setpanel-appearance .set-bg-option').forEach(function (opt) {
        opt.addEventListener('click', function () {
            document.querySelectorAll('#setpanel-appearance .set-bg-option').forEach(function (o) { o.classList.remove('active'); });
            this.classList.add('active');
            window.previewAppearanceSetting && window.previewAppearanceSetting('bgImage', this.dataset.bg);
        });
    });

    // Background opacity slider
    var bgOpacitySlider = document.getElementById('bgOpacity');
    if (bgOpacitySlider) {
        bgOpacitySlider.addEventListener('input', function () {
            var val = parseInt(this.value);
            var lbl = document.getElementById('bgOpacityVal');
            if (lbl) lbl.textContent = val + '%';
            window.previewAppearanceSetting && window.previewAppearanceSetting('bgOpacity', val);
        });
    }

    // Font scale select
    var fontScaleSelect = document.getElementById('fontScaleSelect');
    if (fontScaleSelect) {
        fontScaleSelect.addEventListener('change', function () {
            window.previewAppearanceSetting && window.previewAppearanceSetting('fontScale', this.value);
        });
    }

    // Toggle switches
    var toggleMap = [
        { id: 'scanlinesToggle', key: 'scanlines' },
        { id: 'monospaceToggle', key: 'monospaceBody' },
        { id: 'compactToggle', key: 'compactMode' },
        { id: 'animationsToggle', key: 'animations' }
    ];
    toggleMap.forEach(function (t) {
        var el = document.getElementById(t.id);
        if (el) {
            el.addEventListener('change', function () {
                window.previewAppearanceSetting && window.previewAppearanceSetting(t.key, this.checked);
            });
        }
    });

    /* ═══════════════════════════════════════════════════════════════
       SAVE / RESET APPEARANCE (called by APPLY and RESET buttons)
    ═══════════════════════════════════════════════════════════════ */

    window.saveSettings = function (section) {
        if (section === 'appearance') {
            var colorModeSelect = document.getElementById('colorModeSelect');
            var fontScaleSelect = document.getElementById('fontScaleSelect');
            var activeSwatch = document.querySelector('#setpanel-appearance .set-swatch.active');
            var activeBg = document.querySelector('#setpanel-appearance .set-bg-option.active');
            var bgOpacityEl = document.getElementById('bgOpacity');
            var scanlinesToggle = document.getElementById('scanlinesToggle');
            var monospaceToggle = document.getElementById('monospaceToggle');
            var compactToggle = document.getElementById('compactToggle');
            var animationsToggle = document.getElementById('animationsToggle');

            var settings = {
                colorMode: colorModeSelect ? colorModeSelect.value : 'Dark (Default)',
                accentColor: activeSwatch ? activeSwatch.dataset.color : 'olive',
                scanlines: scanlinesToggle ? scanlinesToggle.checked : true,
                bgOpacity: bgOpacityEl ? parseInt(bgOpacityEl.value) : 38,
                bgImage: activeBg ? activeBg.dataset.bg : 'camobackground',
                fontScale: fontScaleSelect ? fontScaleSelect.value : 'Default (12px)',
                monospaceBody: monospaceToggle ? monospaceToggle.checked : true,
                compactMode: compactToggle ? compactToggle.checked : false,
                animations: animationsToggle ? animationsToggle.checked : true
            };

            window.saveAppearanceSettings(settings);
            typeof showToast === 'function' && showToast('Appearance settings saved.', 'success');
        } else {
            var labels = {
                privacy: 'Privacy & Security',
                notifications: 'Notification preferences',
                language: 'Language & Region'
            };
            var label = labels[section] || 'Settings';
            typeof showToast === 'function' && showToast(label + ' saved successfully.', 'success');
        }
    };

    window.resetAppearanceSettings = function () {
        var defaults = Object.assign({}, window.APPEARANCE_DEFAULTS || {
            colorMode: 'Dark (Default)', accentColor: 'olive', scanlines: true,
            bgOpacity: 38, bgImage: 'camobackground', fontScale: 'Default (12px)',
            monospaceBody: true, compactMode: false, animations: true
        });
        window.saveAppearanceSettings(defaults);
        loadAppearanceIntoUI(defaults);
        typeof showToast === 'function' && showToast('Appearance reset to defaults.', 'info');
    };

    /* ═══════════════════════════════════════════════════════════════
       DISPLAY NAME LIVE PREVIEW
    ═══════════════════════════════════════════════════════════════ */
    var nameInput = document.getElementById('displayNameInput');
    if (nameInput) {
        nameInput.addEventListener('input', function () {
            var val = this.value.trim() || 'AD';
            var preview = document.getElementById('displayNamePreview');
            if (preview) preview.textContent = val;
            var initials = val.split(' ').map(function (w) { return w[0]; }).join('').toUpperCase().slice(0, 2) || 'AD';
            var initialsEl = document.getElementById('avatarInitials');
            if (initialsEl) initialsEl.textContent = initials;
        });
    }

    /* ═══════════════════════════════════════════════════════════════
       PROFILE IMAGE PREVIEW
    ═══════════════════════════════════════════════════════════════ */
    window.previewProfileImage = function (input) {
        if (!input.files || !input.files[0]) return;
        var file = input.files[0];
        var reader = new FileReader();
        reader.onload = function (e) {
            var photo = document.getElementById('avatarPhoto');
            var initials = document.getElementById('avatarInitials');
            var nameEl = document.getElementById('photoFilename');
            if (photo) { photo.src = e.target.result; photo.style.display = 'block'; }
            if (initials) { initials.style.display = 'none'; }
            if (nameEl) { nameEl.textContent = '✓ ' + file.name; nameEl.style.display = 'block'; }
        };
        reader.readAsDataURL(file);
    };

    /* ═══════════════════════════════════════════════════════════════
       PAYMENT OPTION SELECTION
    ═══════════════════════════════════════════════════════════════ */
    window.selectPaymentOpt = function (radio) {
        document.querySelectorAll('.set-payment-opt').forEach(function (el) { el.classList.remove('active'); });
        var label = radio.closest('.set-payment-opt');
        if (label) label.classList.add('active');
    };

    /* ═══════════════════════════════════════════════════════════════
       PASSWORD STRENGTH
    ═══════════════════════════════════════════════════════════════ */
    window.updatePasswordStrength = function (pw) {
        var score = 0;
        if (pw.length >= 8) score++;
        if (pw.length >= 12) score++;
        if (/[A-Z]/.test(pw)) score++;
        if (/[0-9]/.test(pw)) score++;
        if (/[^A-Za-z0-9]/.test(pw)) score++;
        var pct = Math.round((score / 5) * 100);
        var bar = document.getElementById('pwStrengthBar');
        var lbl = document.getElementById('pwStrengthLabel');
        var colors = ['#c0392b', '#c0392b', '#e8b84b', '#a8c47a', '#a8c47a', '#a8c47a'];
        var labels = ['WEAK', 'WEAK', 'FAIR', 'STRONG', 'VERY STRONG', 'VERY STRONG'];
        if (bar) { bar.style.width = pct + '%'; bar.style.background = colors[score] || '#c0392b'; }
        if (lbl) lbl.textContent = pw.length === 0 ? 'ENTER PASSWORD TO CHECK STRENGTH' : (labels[score] || 'WEAK') + ' · ' + pct + '% STRENGTH';
    };

    /* ═══════════════════════════════════════════════════════════════
       LOGIN HISTORY TOGGLE
    ═══════════════════════════════════════════════════════════════ */
    window.toggleLoginHistory = function (checkbox) {
        var table = document.getElementById('loginHistoryTable');
        var tag = document.getElementById('loginHistoryTag');
        if (checkbox.checked) {
            if (table) table.style.display = 'block';
            if (tag) { tag.textContent = 'VISIBLE'; tag.className = 'set-tag set-tag--on'; }
        } else {
            if (table) table.style.display = 'none';
            if (tag) { tag.textContent = 'HIDDEN'; tag.className = 'set-tag set-tag--off'; }
        }
    };

    /* ═══════════════════════════════════════════════════════════════
       QUIET HOURS TOGGLE
    ═══════════════════════════════════════════════════════════════ */
    window.toggleQuietHours = function (checkbox) {
        var cfg = document.getElementById('quietHoursConfig');
        if (cfg) cfg.style.display = checkbox.checked ? 'block' : 'none';
    };

    /* ═══════════════════════════════════════════════════════════════
       CURRENCY PREFERENCE
    ═══════════════════════════════════════════════════════════════ */
    window.saveCurrencyPreference = function (code) {
        fetch('/set-currency', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ currency: code })
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.ok) { typeof showToast === 'function' && showToast('Could not change currency.', 'danger'); return; }
                var sym = document.getElementById('settingsWalletSymbol');
                if (sym) sym.textContent = data.symbol;
                var walletInput = document.getElementById('walletBalanceInput');
                if (walletInput && data.rate != null) {
                    var oldRate = parseFloat(walletInput.dataset.rate) || 1;
                    var currentDisplay = parseFloat(walletInput.value) || 0;
                    var phpAmount = oldRate !== 0 ? currentDisplay / oldRate : currentDisplay;
                    walletInput.value = (phpAmount * data.rate).toFixed(2);
                    walletInput.dataset.rate = data.rate;
                }
                typeof showToast === 'function' && showToast('Currency changed to ' + code + '.', 'success');
            })
            .catch(function () { typeof showToast === 'function' && showToast('Network error — currency not saved.', 'danger'); });
    };

    /* ═══════════════════════════════════════════════════════════════
       SUPPORT TICKET
    ═══════════════════════════════════════════════════════════════ */
    window.submitSupport = function () {
        typeof showToast === 'function' && showToast('Support ticket submitted. We\'ll respond within 24 hours.', 'success');
    };

    /* ═══════════════════════════════════════════════════════════════
       SAVE ACCOUNT SETTINGS
    ═══════════════════════════════════════════════════════════════ */
    window.saveAccountSettings = async function () {
        var username = (document.getElementById('displayNameInput')?.value || '').trim();
        if (!username) {
            typeof showToast === 'function' && showToast('Display name cannot be empty.', 'danger');
            return;
        }
        var imageInput = document.getElementById('profileImageInput');
        var hasImage = imageInput && imageInput.files && imageInput.files[0];
        var fd = new FormData();
        fd.append('username', username);
        fd.append('email', (document.getElementById('emailInput')?.value || '').trim());
        fd.append('contact_number', (document.getElementById('phoneInput')?.value || '').trim());
        fd.append('bio', (document.getElementById('bioInput')?.value || '').trim());
        fd.append('country', document.getElementById('countrySelect')?.value || '');
        fd.append('delivery_address', (document.getElementById('deliveryAddressInput')?.value || '').trim());
        fd.append('social_link_1', (document.getElementById('socialLink1')?.value || '').trim());
        fd.append('social_link_2', (document.getElementById('socialLink2')?.value || '').trim());
        fd.append('social_link_3', (document.getElementById('socialLink3')?.value || '').trim());
        fd.append('social_link_4', (document.getElementById('socialLink4')?.value || '').trim());
        var walletInput = document.getElementById('walletBalanceInput');
        var displayedWallet = parseFloat(walletInput?.value) || 0;
        var activeRate = parseFloat(walletInput?.dataset.rate) || 1;
        var walletInPhp = activeRate !== 0 ? displayedWallet / activeRate : displayedWallet;
        fd.append('wallet_balance', walletInPhp.toFixed(2));
        var paymentRadio = document.querySelector('input[name="paymentMethod"]:checked');
        fd.append('payment_method', paymentRadio ? paymentRadio.value : 'cash_on_delivery');
        if (hasImage) fd.append('profile_image', imageInput.files[0]);

        try {
            var res = await fetch('/api/settings/account', { method: 'POST', body: fd });
            var data = await res.json();
            if (data.ok) {
                typeof showToast === 'function' && showToast('Account settings saved.', 'success');
                if (data.profile_image) {
                    var photo = document.getElementById('avatarPhoto');
                    if (photo) {
                        photo.src = '/static/assets/images/userimages/' + data.profile_image;
                        photo.style.display = 'block';
                        var initialsEl = document.getElementById('avatarInitials');
                        if (initialsEl) initialsEl.style.display = 'none';
                    }
                }
            } else {
                typeof showToast === 'function' && showToast(data.error || 'Save failed.', 'danger');
            }
        } catch (err) {
            typeof showToast === 'function' && showToast('Network error — could not save.', 'danger');
        }
    };

    window.resetSection = function (section) {
        typeof showToast === 'function' && showToast('Changes discarded.', 'info');
    };

    /* ═══════════════════════════════════════════════════════════════
       DELETE ACCOUNT MODAL
    ═══════════════════════════════════════════════════════════════ */
    window.openDeleteModal = function () {
        var modal = document.getElementById('deleteModal');
        if (modal) modal.classList.add('active');
        var input = document.getElementById('deleteConfirmInput');
        var btn = document.getElementById('confirmDeleteBtn');
        if (input) input.value = '';
        if (btn) { btn.disabled = true; btn.style.opacity = '0.4'; btn.style.cursor = 'not-allowed'; }
    };
    window.closeDeleteModal = function () {
        var modal = document.getElementById('deleteModal');
        if (modal) modal.classList.remove('active');
    };
    window.checkDeleteConfirm = function (val) {
        var btn = document.getElementById('confirmDeleteBtn');
        if (!btn) return;
        var ok = val === 'DELETE MY ACCOUNT';
        btn.disabled = !ok;
        btn.style.opacity = ok ? '1' : '0.4';
        btn.style.cursor = ok ? 'pointer' : 'not-allowed';
    };
    var deleteModal = document.getElementById('deleteModal');
    if (deleteModal) {
        deleteModal.addEventListener('click', function (e) {
            if (e.target === deleteModal) window.closeDeleteModal();
        });
    }

    /* ═══════════════════════════════════════════════════════════════
       TWO-FACTOR AUTHENTICATION
    ═══════════════════════════════════════════════════════════════ */
    var _2fa = { secret: null, backupCodes: [] };

    function _setTwoFaUI(enabled) {
        var tag = document.getElementById('twoFaStatusTag');
        var toggle = document.getElementById('twoFaToggle');
        if (enabled) {
            if (tag) { tag.textContent = 'ENABLED'; tag.className = 'set-tag set-tag--on'; }
            if (toggle) toggle.checked = true;
        } else {
            if (tag) { tag.textContent = 'DISABLED'; tag.className = 'set-tag set-tag--off'; }
            if (toggle) toggle.checked = false;
        }
    }

    function _renderBackupCodes(codes) {
        var list = document.getElementById('twoFaBackupList');
        if (!list) return;
        list.innerHTML = (codes || []).map(function (c) {
            return '<div style="background:rgba(138,170,106,0.07);border:1px solid var(--mil-border);padding:6px 10px;letter-spacing:0.18em;">' + c + '</div>';
        }).join('');
    }

    window.handle2FAToggle = async function (cb) {
        if (cb.checked) {
            cb.disabled = true;
            try {
                var res = await fetch('/api/2fa/setup', { method: 'POST' });
                var data = await res.json();
                if (!data.ok) throw new Error(data.error || 'Server error');
                _2fa.secret = data.secret;
                var secretDisplay = document.getElementById('twoFaSecretDisplay');
                if (secretDisplay) secretDisplay.textContent = data.secret;
                var setupBlock = document.getElementById('twoFaSetupBlock');
                var disableBlock = document.getElementById('twoFaDisableBlock');
                var backupBlock = document.getElementById('twoFaBackupBlock');
                var verifyInput = document.getElementById('twoFaVerifyInput');
                var verifyError = document.getElementById('twoFaVerifyError');
                if (setupBlock) setupBlock.style.display = 'block';
                if (disableBlock) disableBlock.style.display = 'none';
                if (backupBlock) backupBlock.style.display = 'none';
                if (verifyInput) verifyInput.value = '';
                if (verifyError) verifyError.style.display = 'none';
            } catch (err) {
                typeof showToast === 'function' && showToast('Could not start 2FA setup: ' + err.message, 'danger');
                cb.checked = false;
            } finally {
                cb.disabled = false;
            }
        } else {
            var setupBlock = document.getElementById('twoFaSetupBlock');
            var disableBlock = document.getElementById('twoFaDisableBlock');
            var backupBlock = document.getElementById('twoFaBackupBlock');
            var disableInput = document.getElementById('twoFaDisableInput');
            var disableError = document.getElementById('twoFaDisableError');
            if (setupBlock) setupBlock.style.display = 'none';
            if (backupBlock) backupBlock.style.display = 'none';
            if (disableBlock) disableBlock.style.display = 'block';
            if (disableInput) disableInput.value = '';
            if (disableError) disableError.style.display = 'none';
        }
    };

    window.confirm2FASetup = async function () {
        var code = (document.getElementById('twoFaVerifyInput')?.value || '').trim();
        var errEl = document.getElementById('twoFaVerifyError');
        if (code.length !== 6) {
            if (errEl) { errEl.textContent = '⚠ Enter the 6-digit code from your authenticator app.'; errEl.style.display = 'block'; }
            return;
        }
        if (errEl) errEl.style.display = 'none';
        try {
            var res = await fetch('/api/2fa/enable', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) });
            var data = await res.json();
            if (!data.ok) {
                if (errEl) { errEl.textContent = '⚠ ' + (data.error || 'Verification failed.'); errEl.style.display = 'block'; }
                return;
            }
            _2fa.backupCodes = data.backup_codes || [];
            _setTwoFaUI(true);
            _renderBackupCodes(data.backup_codes);
            var setupBlock = document.getElementById('twoFaSetupBlock');
            var backupBlock = document.getElementById('twoFaBackupBlock');
            if (setupBlock) setupBlock.style.display = 'none';
            if (backupBlock) backupBlock.style.display = 'block';
            typeof showToast === 'function' && showToast('Two-factor authentication enabled.', 'success');
        } catch (err) {
            if (errEl) { errEl.textContent = '⚠ Network error — please try again.'; errEl.style.display = 'block'; }
        }
    };

    window.disable2FA = async function () {
        var code = (document.getElementById('twoFaDisableInput')?.value || '').trim();
        var errEl = document.getElementById('twoFaDisableError');
        if (code.length !== 6) {
            if (errEl) { errEl.textContent = '⚠ Enter the 6-digit code from your authenticator app.'; errEl.style.display = 'block'; }
            return;
        }
        if (errEl) errEl.style.display = 'none';
        try {
            var res = await fetch('/api/2fa/disable', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) });
            var data = await res.json();
            if (!data.ok) {
                if (errEl) { errEl.textContent = '⚠ ' + (data.error || 'Verification failed.'); errEl.style.display = 'block'; }
                return;
            }
            _setTwoFaUI(false);
            var disableBlock = document.getElementById('twoFaDisableBlock');
            var backupBlock = document.getElementById('twoFaBackupBlock');
            if (disableBlock) disableBlock.style.display = 'none';
            if (backupBlock) backupBlock.style.display = 'none';
            typeof showToast === 'function' && showToast('Two-factor authentication disabled.', 'warning');
        } catch (err) {
            if (errEl) { errEl.textContent = '⚠ Network error — please try again.'; errEl.style.display = 'block'; }
        }
    };

    window.copyBackupCodes = function () {
        if (!_2fa.backupCodes.length) return;
        navigator.clipboard.writeText(_2fa.backupCodes.join('\n'))
            .then(function () { typeof showToast === 'function' && showToast('Backup codes copied to clipboard.', 'success'); })
            .catch(function () { typeof showToast === 'function' && showToast('Could not copy — please copy manually.', 'warning'); });
    };

    // Check 2FA status on load
    (async function () {
        var toggle = document.getElementById('twoFaToggle');
        if (!toggle) return;
        try {
            var res = await fetch('/api/2fa/status');
            var data = await res.json();
            if (data.ok && data.enabled) _setTwoFaUI(true);
        } catch (_) { }
    })();

    /* ═══════════════════════════════════════════════════════════════
       ACTIVE SESSIONS
    ═══════════════════════════════════════════════════════════════ */
    function _escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    async function loadSessions() {
        var loading = document.getElementById('sessionsLoadingRow');
        var list = document.getElementById('sessionsList');
        var empty = document.getElementById('sessionsEmptyRow');
        if (!list) return;
        try {
            var res = await fetch('/api/sessions');
            var data = await res.json();
            if (loading) loading.style.display = 'none';
            if (!data.ok || !data.sessions || !data.sessions.length) {
                if (empty) empty.style.display = 'block';
                return;
            }
            list.innerHTML = data.sessions.map(function (s) {
                var isCurrent = s.is_current;
                return '<div class="set-session-row" id="sess-' + s.id + '" style="display:flex;align-items:flex-start;gap:14px;padding:14px 20px;border-bottom:1px solid rgba(138,170,106,0.1);' + (isCurrent ? 'background:rgba(138,170,106,0.04);' : '') + '">'
                    + '<div style="font-size:20px;margin-top:2px;flex-shrink:0;">' + (s.device_type === 'mobile' ? '📱' : '🖥') + '</div>'
                    + '<div style="flex:1;min-width:0;">'
                    + '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px;">'
                    + '<span style="font-family:var(--font-stencil);font-size:12px;letter-spacing:0.14em;color:var(--mil-bright);">' + _escHtml(s.device_label || 'Unknown Device') + '</span>'
                    + (isCurrent ? '<span class="set-tag set-tag--on" style="font-size:8px;padding:2px 7px;">CURRENT</span>' : '')
                    + '</div>'
                    + '<div style="font-family:var(--font-mono);font-size:9px;color:var(--mil-muted);letter-spacing:0.06em;line-height:1.8;">'
                    + 'IP: ' + _escHtml(s.ip_address || '—') + ' &nbsp;·&nbsp; '
                    + 'Started: ' + _escHtml(s.created_at || '—') + ' &nbsp;·&nbsp; '
                    + 'Last active: ' + _escHtml(s.last_seen || '—')
                    + '</div>'
                    + '<div style="font-family:var(--font-mono);font-size:9px;color:var(--mil-muted);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + _escHtml(s.user_agent || '') + '</div>'
                    + '</div>'
                    + (!isCurrent
                        ? '<button class="set-btn set-btn--danger" style="font-size:9px;padding:4px 12px;white-space:nowrap;flex-shrink:0;" onclick="revokeSession(\'' + s.id + '\')">⊠ REVOKE</button>'
                        : '<div style="font-family:var(--font-mono);font-size:9px;color:var(--mil-muted);white-space:nowrap;padding-top:4px;">THIS DEVICE</div>')
                    + '</div>';
            }).join('');
            list.style.display = 'block';
        } catch (err) {
            if (loading) loading.textContent = 'FAILED TO LOAD SESSIONS';
        }
    }

    window.revokeSession = async function (sessionId) {
        try {
            var res = await fetch('/api/sessions/' + sessionId + '/revoke', { method: 'POST' });
            var data = await res.json();
            if (data.ok) {
                var row = document.getElementById('sess-' + sessionId);
                if (row) { row.style.transition = 'opacity 0.3s'; row.style.opacity = '0'; setTimeout(function () { row.remove(); }, 320); }
                typeof showToast === 'function' && showToast('Session revoked.', 'success');
            } else {
                typeof showToast === 'function' && showToast(data.error || 'Could not revoke session.', 'danger');
            }
        } catch (_) {
            typeof showToast === 'function' && showToast('Network error — could not revoke session.', 'danger');
        }
    };

    window.revokeAllSessions = async function () {
        if (!confirm('Revoke all sessions except this one? You will need to log in again on other devices.')) return;
        try {
            var res = await fetch('/api/sessions/revoke-all', { method: 'POST' });
            var data = await res.json();
            if (data.ok) {
                typeof showToast === 'function' && showToast('All other sessions revoked.', 'success');
                var list = document.getElementById('sessionsList');
                var empty = document.getElementById('sessionsEmptyRow');
                var loading = document.getElementById('sessionsLoadingRow');
                if (list) list.innerHTML = '';
                if (empty) empty.style.display = 'none';
                if (loading) { loading.style.display = 'block'; loading.textContent = 'LOADING SESSIONS…'; }
                await loadSessions();
            } else {
                typeof showToast === 'function' && showToast(data.error || 'Could not revoke sessions.', 'danger');
            }
        } catch (_) {
            typeof showToast === 'function' && showToast('Network error — could not revoke sessions.', 'danger');
        }
    };

    /* ═══════════════════════════════════════════════════════════════
       LANGUAGE & REGION SETTINGS
       ─────────────────────────────────────────────────────────────
       Storage key: 'armsdealer_region'
       Shape: { language, timezone, timezoneLabel, lat, lng, currency }

       Language values must match the navbar <select id="languageSelect">
       option values so setLanguage() works when called from either side.

       Timezone changes update the .nav-coord readout in the navbar
       immediately on this page (the element exists on subbase.html too),
       and on every other page via the stored lat/lng pair read by
       navbarfunctions.js at load time.
    ═══════════════════════════════════════════════════════════════ */

    /* ── Mapping: language values not carried by the navbar select ──
       The navbar only knows: english | filipino | japanese | spanish | mandarin
       For extras we fall back to the closest supported navbar value. */
    var LANG_NAVBAR_MAP = {
        english: 'english',
        spanish: 'spanish',
        french: 'english',   // navbar has no French — keep English as fallback
        german: 'english',   // same
        japanese: 'japanese',
        mandarin: 'mandarin',
        russian: 'english',
        arabic: 'english',
        filipino: 'filipino'
    };

    /* ── Mapping: currency values → navbar option values ──
       navbar currencySelect options: PHP | USD | EUR | JPY | CNY
       Settings panel adds GBP and SGD which the navbar doesn't carry. */
    var CURRENCY_NAVBAR_MAP = {
        PHP: 'PHP',
        USD: 'USD',
        EUR: 'EUR',
        GBP: 'USD',   // navbar has no GBP — closest is USD
        SGD: 'USD',   // same
        JPY: 'JPY',
        CNY: 'CNY'
    };

    /* ── Load saved region settings into the settings panel selects ── */
    function _loadRegionIntoUI() {
        try {
            var saved = JSON.parse(localStorage.getItem('armsdealer_region') || 'null');
            if (!saved) return;

            // Language
            var langSel = document.getElementById('settingsLanguageSelect');
            if (langSel && saved.language) {
                langSel.value = saved.language;
            }

            // Timezone
            var tzSel = document.getElementById('settingsTimezoneSelect');
            if (tzSel && saved.timezone) {
                // Match by value attribute
                var matched = false;
                for (var i = 0; i < tzSel.options.length; i++) {
                    if (tzSel.options[i].value === saved.timezone) {
                        tzSel.selectedIndex = i;
                        matched = true;
                        break;
                    }
                }
                // Update coord preview to stored values
                if (matched && saved.lat && saved.lng) {
                    _updateCoordPreview(saved.lat, saved.lng);
                }
            }

            // Currency
            var curSel = document.getElementById('settingsCurrencySelect');
            if (curSel && saved.currency) {
                curSel.value = saved.currency;
            }
        } catch (e) { /* ignore */ }
    }

    /* ── Update the live coord preview row on the settings page ── */
    function _updateCoordPreview(lat, lng) {
        var latEl = document.getElementById('coordPreviewLat');
        var lngEl = document.getElementById('coordPreviewLng');
        if (latEl) latEl.textContent = lat;
        if (lngEl) lngEl.textContent = lng;
    }

    /* ── Update the live .nav-coord readout in the navbar (if present on this page) ── */
    function _updateNavCoord(lat, lng) {
        // The navbar .nav-coord contains two child <div>s:
        //   <div><span>LAT</span> 14.5995° N</div>
        //   <div><span>LNG</span> 120.9842° E</div>
        // We replace the text node after each <span>.
        var coordEl = document.querySelector('.nav-coord');
        if (!coordEl) return;
        var divs = coordEl.querySelectorAll('div');
        if (divs[0]) {
            var span0 = divs[0].querySelector('span');
            if (span0) {
                // Clear existing text nodes then append new one
                while (span0.nextSibling) span0.parentNode.removeChild(span0.nextSibling);
                divs[0].appendChild(document.createTextNode(' ' + lat));
            }
        }
        if (divs[1]) {
            var span1 = divs[1].querySelector('span');
            if (span1) {
                while (span1.nextSibling) span1.parentNode.removeChild(span1.nextSibling);
                divs[1].appendChild(document.createTextNode(' ' + lng));
            }
        }
    }

    /* ── Called on language select change (live, before save) ── */
    window.RegionSettings = window.RegionSettings || {};

    window.RegionSettings.onLanguageChange = function (value) {
        // Live-sync the navbar language select if it's on the same page
        // (subbase pages include the full navbar)
        var navLangSel = document.getElementById('languageSelect');
        var navbarVal = LANG_NAVBAR_MAP[value] || 'english';
        if (navLangSel && navLangSel.value !== navbarVal) {
            navLangSel.value = navbarVal;
            // Fire the navbar's onchange so setLanguage() runs and translations update
            if (typeof setLanguage === 'function') setLanguage(navbarVal);
        }
    };

    /* ── Called on timezone select change (live, before save) ── */
    window.RegionSettings.onTimezoneChange = function (value, selectedOption) {
        var lat = selectedOption.dataset.lat || '';
        var lng = selectedOption.dataset.lng || '';
        // Update the preview row immediately
        _updateCoordPreview(lat, lng);
        // Also live-update the navbar coord readout on this page
        _updateNavCoord(lat, lng);
    };

    /* ── Called on currency select change (live, before save) ── */
    window.RegionSettings.onCurrencyChange = function (value) {
        // Sync navbar currency select if present
        var navCurSel = document.getElementById('currencySelect');
        var navbarVal = CURRENCY_NAVBAR_MAP[value] || value;
        if (navCurSel && navCurSel.value !== navbarVal) {
            navCurSel.value = navbarVal;
            // Fire the navbar's onchange handler
            if (typeof setCurrency === 'function') setCurrency(navbarVal);
        }
        // Also call the existing server-side currency save
        window.saveCurrencyPreference(value);
    };

    /* ── SAVE: persist to localStorage and sync navbar ── */
    window.RegionSettings.save = function () {
        var langSel = document.getElementById('settingsLanguageSelect');
        var tzSel = document.getElementById('settingsTimezoneSelect');
        var curSel = document.getElementById('settingsCurrencySelect');

        var language = langSel ? langSel.value : 'english';
        var timezone = tzSel ? tzSel.value : 'UTC+08:00';
        var currency = curSel ? curSel.value : 'PHP';

        // Pull lat/lng from the selected option's data attributes
        var lat = 'N/A', lng = 'N/A', tzLabel = timezone;
        if (tzSel && tzSel.selectedIndex >= 0) {
            var opt = tzSel.options[tzSel.selectedIndex];
            lat = opt.dataset.lat || lat;
            lng = opt.dataset.lng || lng;
            tzLabel = opt.text.trim() || tzLabel;
        }

        // Persist region bundle
        var region = { language: language, timezone: timezone, timezoneLabel: tzLabel, lat: lat, lng: lng, currency: currency };
        localStorage.setItem('armsdealer_region', JSON.stringify(region));

        // Sync navbar language (in case user changed it without triggering onchange)
        var navbarLang = LANG_NAVBAR_MAP[language] || 'english';
        var navLangSel = document.getElementById('languageSelect');
        if (navLangSel) navLangSel.value = navbarLang;
        if (typeof setLanguage === 'function') setLanguage(navbarLang);

        // Sync navbar currency
        var navbarCur = CURRENCY_NAVBAR_MAP[currency] || currency;
        var navCurSel = document.getElementById('currencySelect');
        if (navCurSel) navCurSel.value = navbarCur;
        if (typeof setCurrency === 'function') setCurrency(navbarCur);

        // Apply coords to navbar readout
        _updateNavCoord(lat, lng);

        typeof showToast === 'function' && showToast('Language & Region saved.', 'success');
    };

    /* ── DISCARD: reload stored values back into the UI ── */
    window.RegionSettings.discard = function () {
        _loadRegionIntoUI();
        typeof showToast === 'function' && showToast('Changes discarded.', 'info');
    };

    // Bootstrap: load saved region into UI on page load
    _loadRegionIntoUI();

    // Also wire the timezone select's onchange in case the inline attribute isn't present
    (function () {
        var tzSel = document.getElementById('settingsTimezoneSelect');
        if (tzSel) {
            // Sync coord preview to the initial selected option on load
            var opt = tzSel.options[tzSel.selectedIndex];
            if (opt) _updateCoordPreview(opt.dataset.lat || '', opt.dataset.lng || '');
        }
    })();

})();