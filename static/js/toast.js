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
 * USAGE (from Jinja — fire on page load from Flask flash messages):
 *   The script auto-reads data-toast elements injected by the
 *   {% include 'partials/toast_init.html' %} partial.
 */

(function () {
    'use strict';

    /* ── Config ──────────────────────────────────────────────────── */
    const DURATION_MS = 4500;   // how long toast stays visible
    const ANIM_DELAY_MS = 30;     // brief delay before enter animation fires

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

    /* ── Core show function ──────────────────────────────────────── */
    function show(message, type, durationMs) {
        const variant = ['success', 'danger', 'warning', 'info'].includes(type) ? type : 'info';
        const duration = typeof durationMs === 'number' ? durationMs : DURATION_MS;

        const toast = document.createElement('div');
        toast.className = `toast toast--${variant}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');

        toast.innerHTML = `
            <div class="toast__icon">${ICONS[variant]}</div>
            <div class="toast__label">${LABELS[variant]}</div>
            <div class="toast__message">${escapeHtml(message)}</div>
            <button class="toast__close" aria-label="Dismiss">✕</button>
            <div class="toast__progress" style="animation-duration:${duration}ms"></div>
        `;

        getContainer().appendChild(toast);

        // Trigger enter animation on next frame
        requestAnimationFrame(() => {
            setTimeout(() => toast.classList.add('toast--visible'), ANIM_DELAY_MS);
        });

        // Auto-dismiss
        const timer = setTimeout(() => dismiss(toast), duration);

        // Manual dismiss
        toast.querySelector('.toast__close').addEventListener('click', () => {
            clearTimeout(timer);
            dismiss(toast);
        });
    }

    function dismiss(toast) {
        toast.classList.remove('toast--visible');
        toast.classList.add('toast--hiding');
        toast.addEventListener('transitionend', () => {
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
            const type = el.dataset.type || 'info';
            const message = el.dataset.message || '';
            if (message) show(message, type);
            el.parentNode && el.parentNode.removeChild(el);
        });
    }

    /* ── Expose global API ───────────────────────────────────────── */
    window.ArmsToast = { show: show };

    /* ── Boot on DOM ready ───────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFromDOM);
    } else {
        initFromDOM();
    }

})();