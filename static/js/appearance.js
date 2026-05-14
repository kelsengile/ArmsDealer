/* ========================================================================================================================================================
   APPEARANCE SETTINGS - GLOBAL APPLICATION
   Handles live preview, saving, and cross-tab sync.
   The initial page-load application (before first paint) is done by the
   inline <script> in <head> in base.html / subbase.html — not here.
   ======================================================================================================================================================== */

/* ── Default settings ──────────────────────────────────────────── */
var APPEARANCE_DEFAULTS = {
    colorMode: 'Dark (Default)',
    accentColor: 'olive',
    scanlines: true,
    bgOpacity: 38,
    bgImage: 'camobackground',
    fontScale: 'Default (12px)',
    monospaceBody: true,
    compactMode: false,
    animations: true
};

var ACCENT_COLORS = {
    olive: '#a8c47a',
    steel: '#5b9bd5',
    red: '#c0392b',
    amber: '#e8b84b',
    violet: '#9b59b6'
};

var FONT_SIZES = {
    'Small (10px)': '10px',
    'Default (12px)': '12px',
    'Large (14px)': '14px'
};

/* ── Apply all settings to the live page ─────────────────────── */
function applyAppearanceSettings(settings) {
    var root = document.documentElement;
    var body = document.body;

    // Font scale
    root.style.fontSize = FONT_SIZES[settings.fontScale] || '12px';

    // Animations
    if (!settings.animations) {
        root.style.setProperty('--transition-fast', '0s');
        root.style.setProperty('--transition-base', '0s');
        root.style.setProperty('--transition-slow', '0s');
    } else {
        root.style.setProperty('--transition-fast', '150ms ease-in-out');
        root.style.setProperty('--transition-base', '300ms ease-in-out');
        root.style.setProperty('--transition-slow', '500ms ease-in-out');
    }

    // Compact mode
    var m = settings.compactMode ? 0.7 : 1;
    root.style.setProperty('--spacing-sm', (8 * m) + 'px');
    root.style.setProperty('--spacing-md', (12 * m) + 'px');
    root.style.setProperty('--spacing-lg', (15 * m) + 'px');

    // Scanlines
    if (settings.scanlines) {
        body.classList.add('scanlines');
    } else {
        body.classList.remove('scanlines');
    }

    // Accent color
    var accent = ACCENT_COLORS[settings.accentColor] || ACCENT_COLORS.olive;
    root.style.setProperty('--mil-bright', accent);
    root.style.setProperty('--mil-green', accent);

    // Background — update the inline <style> tag injected by the head script
    var op = (settings.bgOpacity != null ? settings.bgOpacity : 38) / 100;
    var dop = Math.min(1, op * 1.35).toFixed(3);
    var bg = settings.bgImage || 'camobackground';
    var url = '/static/assets/images/pageimages/globalmages/' + bg + '.png';
    var css = 'body{background:linear-gradient(rgba(0,0,0,' + op + '),rgba(2,15,4,' + dop + ')),url("' + url + '")!important;background-size:cover!important;background-position:center!important;background-repeat:repeat!important;background-attachment:fixed!important;}';

    var inlineStyle = document.getElementById('appearance-inline');
    if (!inlineStyle) {
        inlineStyle = document.createElement('style');
        inlineStyle.id = 'appearance-inline';
        document.head.appendChild(inlineStyle);
    }
    inlineStyle.textContent = css;

    window.currentAppearanceSettings = settings;
}

/* ── Save + apply (called from settings page APPLY button) ─────── */
window.saveAppearanceSettings = function (settings) {
    localStorage.setItem('armsdealer_appearance', JSON.stringify(settings));
    applyAppearanceSettings(settings);
};

/* ── Live preview (no save) ────────────────────────────────────── */
window.previewAppearanceSetting = function (key, value) {
    var current = window.currentAppearanceSettings
        || JSON.parse(localStorage.getItem('armsdealer_appearance') || 'null')
        || Object.assign({}, APPEARANCE_DEFAULTS);
    var preview = Object.assign({}, current);
    preview[key] = value;
    applyAppearanceSettings(preview);
};

/* ── Cross-tab sync ────────────────────────────────────────────── */
window.addEventListener('storage', function (e) {
    if (e.key === 'armsdealer_appearance' && e.newValue) {
        try {
            applyAppearanceSettings(JSON.parse(e.newValue));
        } catch (err) {
            console.warn('[appearance] Could not parse storage event:', err);
        }
    }
});

/* ── Track current settings state (head script handled visual apply) */
(function () {
    var saved = localStorage.getItem('armsdealer_appearance');
    var settings = saved ? JSON.parse(saved) : Object.assign({}, APPEARANCE_DEFAULTS);
    settings = Object.assign({}, APPEARANCE_DEFAULTS, settings);
    window.currentAppearanceSettings = settings;
})();

// Expose globally
window.applyAppearanceSettings = applyAppearanceSettings;
window.APPEARANCE_DEFAULTS = APPEARANCE_DEFAULTS;