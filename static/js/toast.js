/**
 * toast.js — ArmsDealer Notification System
 *
 * Provides a global `ArmsToast` API for showing tactical popup notifications.
 *
 * USAGE (from any JS file):
 *   ArmsToast.show('Message here', 'success');
 *   ArmsToast.show('Message here', 'danger');
 *   ArmsToast.show('Message here', 'warning');
 *   ArmsToast.show('Message here', 'info');
 *
 * Respects notification preferences stored in localStorage under
 * 'armsdealer_notif_prefs':
 *   - in_app_enabled  : false => all toasts are suppressed
 *   - quiet_hours_*   : toasts suppressed during quiet window (non-forced only)
 *
 * Pass `{ force: true }` as third arg to bypass quiet hours (e.g. security alerts).
 *
 * USAGE (from Jinja — fire on page load from Flask flash messages):
 *   The script auto-reads data-toast elements injected by the
 *   {% include 'partials/toast_init.html' %} partial.
 */

(function () {
    'use strict';

    /* ── Config ──────────────────────────────────────────────────── */
    const DURATION_MS = 4500;
    const ANIM_DELAY_MS = 30;
    const PREFS_KEY = 'armsdealer_notif_prefs';

    /* ── Icon map ────────────────────────────────────────────────── */
    const ICONS = {
        success: '✔',
        danger: '✖',
        warning: '⚠',
        info: 'ℹ',
    };

    /* ── Label map ───────────────────────────────────────────────── */
    const LABELS = {
        success: 'CONFIRMED',
        danger: 'ALERT',
        warning: 'WARNING',
        info: 'NOTICE',
    };

    /* ── Container (created once, lazily) ───────────────────────── */
    let container = null;

    function getContainer() {
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    /* ── Preference helpers ──────────────────────────────────────── */

    function getPrefs() {
        try {
            var raw = localStorage.getItem(PREFS_KEY);
            return raw ? JSON.parse(raw) : {};
        } catch (e) {
            return {};
        }
    }

    function isInAppEnabled() {
        var prefs = getPrefs();
        // Default to enabled if not set
        return prefs.in_app_enabled !== false;
    }

    function isQuietHoursActive() {
        var prefs = getPrefs();
        if (!prefs.quiet_hours_enabled) return false;
        try {
            var now = new Date();
            var nowM = now.getHours() * 60 + now.getMinutes();
            var from = (prefs.quiet_from || '22:00').split(':');
            var until = (prefs.quiet_until || '07:00').split(':');
            var fromM = parseInt(from[0]) * 60 + parseInt(from[1]);
            var untilM = parseInt(until[0]) * 60 + parseInt(until[1]);
            if (fromM <= untilM) {
                return nowM >= fromM && nowM < untilM;
            } else {
                // Overnight window (e.g. 22:00 → 07:00)
                return nowM >= fromM || nowM < untilM;
            }
        } catch (e) {
            return false;
        }
    }

    /* ── Core show function ──────────────────────────────────────── */

    /**
     * @param {string} message
     * @param {string} type        - 'success' | 'danger' | 'warning' | 'info'
     * @param {number|object} [durationMsOrOpts]
     *   Pass a number for duration, or an options object:
     *   { duration: 4500, force: false }
     *   force=true bypasses quiet hours (used for critical/security toasts).
     */
    function show(message, type, durationMsOrOpts) {
        // ── Resolve options ───────────────────────────────────────
        var opts = {};
        if (typeof durationMsOrOpts === 'number') {
            opts.duration = durationMsOrOpts;
        } else if (durationMsOrOpts && typeof durationMsOrOpts === 'object') {
            opts = durationMsOrOpts;
        }
        var duration = typeof opts.duration === 'number' ? opts.duration : DURATION_MS;
        var force = opts.force === true;

        // ── Gate: in-app alerts toggle ────────────────────────────
        if (!isInAppEnabled()) return;

        // ── Gate: quiet hours (skipped for forced/critical toasts) ─
        if (!force && isQuietHoursActive()) return;

        // ── Build toast element ───────────────────────────────────
        var variant = ['success', 'danger', 'warning', 'info'].includes(type) ? type : 'info';

        var toast = document.createElement('div');
        toast.className = 'toast toast--' + variant;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');

        toast.innerHTML =
            '<div class="toast__icon">' + ICONS[variant] + '</div>' +
            '<div class="toast__label">' + LABELS[variant] + '</div>' +
            '<div class="toast__message">' + escapeHtml(message) + '</div>' +
            '<button class="toast__close" aria-label="Dismiss">\u2715</button>' +
            '<div class="toast__progress" style="animation-duration:' + duration + 'ms"></div>';

        getContainer().appendChild(toast);

        // Trigger enter animation on next frame
        requestAnimationFrame(function () {
            setTimeout(function () { toast.classList.add('toast--visible'); }, ANIM_DELAY_MS);
        });

        // Auto-dismiss
        var timer = setTimeout(function () { dismiss(toast); }, duration);

        // Manual dismiss
        toast.querySelector('.toast__close').addEventListener('click', function () {
            clearTimeout(timer);
            dismiss(toast);
        });
    }

    function dismiss(toast) {
        toast.classList.remove('toast--visible');
        toast.classList.add('toast--hiding');
        toast.addEventListener('transitionend', function () {
            if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, { once: true });
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    /* ── Auto-init from Flask flash messages ─────────────────────
       Reads hidden <div data-toast data-type="..." data-message="...">
       elements injected by toast_init.html partial.
    ─────────────────────────────────────────────────────────────── */
    function initFromDOM() {
        document.querySelectorAll('[data-toast]').forEach(function (el) {
            var type = el.dataset.type || 'info';
            var message = el.dataset.message || '';
            var force = el.dataset.force === 'true';
            if (message) show(message, type, { force: force });
            el.parentNode && el.parentNode.removeChild(el);
        });
    }

    /* ── Expose global API ───────────────────────────────────────── */
    window.ArmsToast = {
        show: show,
        isInAppEnabled: isInAppEnabled,
        isQuietHoursActive: isQuietHoursActive,
        getPrefs: getPrefs,
    };

    /* ── Boot on DOM ready ───────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFromDOM);
    } else {
        initFromDOM();
    }

})();