// ───────────────────────────────────────────────────────────────────────────── //
//     SETTINGS PANEL FUNCTIONS
// ───────────────────────────────────────────────────────────────────────────── //

/* ── Element refs ───────────────────────────────────────────── */
const overlay = document.getElementById("settingsOverlay");
const sidebar = document.getElementById("settingsSidebar");
const closeBtn = document.getElementById("settingsClose");
const openBtn = document.getElementById("settingsOpenBtn");

// Guard: exit silently if the settings panel isn't present on this page.
if (!overlay || !sidebar || !closeBtn || !openBtn) {
    // Nothing to wire up — panel HTML not included on this page.
} else {

    /* ── Open / close ───────────────────────────────────────────── */
    function openSettings() {
        overlay.classList.add("active");
        sidebar.classList.add("open");
    }

    function closeSettings() {
        overlay.classList.remove("active");
        sidebar.classList.remove("open");
    }

    openBtn.addEventListener("click", openSettings);
    closeBtn.addEventListener("click", closeSettings);
    overlay.addEventListener("click", closeSettings);

    /* ── Escape key ─────────────────────────────────────────────── */
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeSettings();
    });

    /* ── Nav item clicks — close panel, then follow the href ────── */
    sidebar.querySelectorAll(".set-item[data-section]").forEach(link => {
        link.addEventListener("click", function (e) {
            // Only intercept real anchor clicks (not middle-click / ctrl-click).
            if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
            e.preventDefault();
            const dest = this.href;   // use the server-rendered url_for() href exactly
            closeSettings();
            // Small delay lets the close CSS transition play before navigating.
            setTimeout(() => { window.location.href = dest; }, 180);
        });
    });

} // end guard block