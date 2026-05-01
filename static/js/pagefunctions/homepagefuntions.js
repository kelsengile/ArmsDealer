// ───────────────────────────────────────────────────────────────────────────── //
//     HOMEPAGE FUNCTIONS
// ───────────────────────────────────────────────────────────────────────────── //
// ───────────────────────────────────────────//
//     HERO SECTION
// ───────────────────────────────────────────//
(function () {
  const carousel = document.getElementById("heroCarousel");
  const slides = carousel.querySelectorAll(".hero-slide");
  const dotsWrap = document.getElementById("heroDots");
  const counter = document.getElementById("heroCurrentNum");
  const prevBtn = document.getElementById("heroPrev");
  const nextBtn = document.getElementById("heroNext");
  let current = 0;
  let animating = false;
  let autoTimer = null;
  const TOTAL = slides.length;
  const DELAY = 10000; // ms between auto-advances
  /* ── Build dot indicators ─────────────────────────────── */
  slides.forEach((_, i) => {
    const dot = document.createElement("button");
    dot.className = "hero-dot" + (i === 0 ? " active" : "");
    dot.setAttribute("aria-label", `Go to slide ${i + 1}`);
    dot.addEventListener("click", () =>
      goTo(i, i > current ? "right" : "left"),
    );
    dotsWrap.appendChild(dot);
  });
  const dots = dotsWrap.querySelectorAll(".hero-dot");
  /* ── Text elements selector ───────────────────────────── */
  const TEXT_SELECTORS = ".hero-tag, .hero-title, .hero-subtitle, .hero-cta";
  /* Hard-reset text children so CSS transitions re-fire every time */
  function resetTextChildren(slide) {
    slide.querySelectorAll(TEXT_SELECTORS).forEach((el) => {
      el.style.transition = "none";
      el.style.opacity = "0";
      el.style.transform = "translateY(14px)";
    });
    /* Force reflow so the reset is painted before restoring transitions */
    void slide.offsetHeight;
    slide.querySelectorAll(TEXT_SELECTORS).forEach((el) => {
      el.style.transition = "";
      el.style.opacity = "";
      el.style.transform = "";
    });
  }
  /* ── Core transition ──────────────────────────────────── */
  function goTo(next, direction) {
    if (animating || next === current) return;
    animating = true;
    const outSlide = slides[current];
    const inSlide = slides[next];
    /* 1. Remove active from outgoing slide */
    outSlide.classList.remove("active");
    /* 2. Force-reset text children on the incoming slide BEFORE
              adding .active, so CSS transitions see a real 0→1 change */
    resetTextChildren(inSlide);
    /* 3. Position incoming slide off-screen with no transition */
    inSlide.style.transition = "none";
    inSlide.style.opacity = "0";
    inSlide.style.transform =
      direction === "right"
        ? "translateX(60px) scale(1.04)"
        : "translateX(-60px) scale(1.04)";
    /* 4. Force reflow */
    void inSlide.offsetHeight;
    /* 5. Restore transition and activate */
    inSlide.style.transition = "";
    inSlide.style.opacity = "";
    inSlide.style.transform = "";
    inSlide.classList.add("active");
    /* Update dots & counter */
    dots[current].classList.remove("active");
    dots[next].classList.add("active");
    counter.textContent = String(next + 1).padStart(2, "0");
    current = next;
    /* Unlock after transition completes */
    setTimeout(() => {
      animating = false;
    }, 850);
    resetAuto();
  }
  function goPrev() {
    goTo((current - 1 + TOTAL) % TOTAL, "left");
  }
  function goNext() {
    goTo((current + 1) % TOTAL, "right");
  }
  prevBtn.addEventListener("click", goPrev);
  nextBtn.addEventListener("click", goNext);
  /* ── Auto-advance ─────────────────────────────────────── */
  function startAuto() {
    autoTimer = setInterval(goNext, DELAY);
  }
  function resetAuto() {
    clearInterval(autoTimer);
    startAuto();
  }
  startAuto();
  /* ── Pause on hover ───────────────────────────────────── */
  carousel.addEventListener("mouseenter", () => clearInterval(autoTimer));
  carousel.addEventListener("mouseleave", startAuto);
  /* ── Keyboard support ─────────────────────────────────── */
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") goPrev();
    if (e.key === "ArrowRight") goNext();
  });
  /* ── Touch / swipe support ────────────────────────────── */
  let touchStartX = 0;
  carousel.addEventListener(
    "touchstart",
    (e) => {
      touchStartX = e.changedTouches[0].clientX;
    },
    { passive: true },
  );
  carousel.addEventListener(
    "touchend",
    (e) => {
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) > 40) dx < 0 ? goNext() : goPrev();
    },
    { passive: true },
  );
})();
// ───────────────────────────────────────────//
//     CATEGORIES CAROUSEL
// ───────────────────────────────────────────//
const carouselData = {
  weapons: [
    {
      name: "Firearms",
      translationKey: "homepagecategoryFirearms",
      image: "../../../static/assets/icons/categoriesicons/firearms.png",
    },
    {
      name: "Blades",
      translationKey: "homepagecategoryBlades",
      image: "../../../static/assets/icons/categoriesicons/blade.png",
    },
    {
      name: "Blunts",
      translationKey: "homepagecategoryBlunts",
      image: "../../../static/assets/icons/categoriesicons/blunt.png",
    },
    {
      name: "Projectile",
      translationKey: "homepagecategoryProjectile",
      image: "../../../static/assets/icons/categoriesicons/projectile.png",
    },
    {
      name: "Explosives",
      translationKey: "homepagecategoryExplosives",
      image: "../../../static/assets/icons/categoriesicons/explosives.png",
    },
    {
      name: "Electronic",
      translationKey: "homepagecategoryElectronic",
      image: "../../../static/assets/icons/categoriesicons/electronic.png",
    },
    {
      name: "Chemical",
      translationKey: "homepagecategoryChemical",
      image: "../../../static/assets/icons/categoriesicons/chemical.png",
    },
    {
      name: "Biological",
      translationKey: "homepagecategoryBiological",
      image: "../../../static/assets/icons/categoriesicons/biological.png",
    },
    {
      name: "Vehicle",
      translationKey: "homepagecategoryVehicle",
      image: "../../../static/assets/icons/categoriesicons/vehicle.png",
    },
    {
      name: "Cyber",
      translationKey: "homepagecategoryCyber",
      image: "../../../static/assets/icons/categoriesicons/cyber.png",
    },
    {
      name: "Security",
      translationKey: "homepagecategorySecurity",
      image: "../../../static/assets/icons/categoriesicons/security.png",
    },
  ],
  equipment: [
    {
      name: "Ammunition",
      translationKey: "homepagecategoryAmmunition",
      image: "../../../static/assets/icons/categoriesicons/ammunition.png",
    },
    {
      name: "Protective",
      translationKey: "homepagecategoryProtective",
      image: "../../../static/assets/icons/categoriesicons/protective.png",
    },
    {
      name: "Tactical",
      translationKey: "homepagecategoryTactical",
      image: "../../../static/assets/icons/categoriesicons/tactical.png",
    },
    {
      name: "Attachments",
      translationKey: "homepagecategoryAttachments",
      image: "../../../static/assets/icons/categoriesicons/attachments.png",
    },
    {
      name: "Maintenance",
      translationKey: "homepagecategoryMaintenance",
      image: "../../../static/assets/icons/categoriesicons/maintenance.png",
    },
    {
      name: "Storage",
      translationKey: "homepagecategoryStorage",
      image: "../../../static/assets/icons/categoriesicons/storage.png",
    },
    {
      name: "Communication",
      translationKey: "homepagecategoryCommunication",
      image: "../../../static/assets/icons/categoriesicons/communication.png",
    },
    {
      name: "Survival",
      translationKey: "homepagecategorySurvival",
      image: "../../../static/assets/icons/categoriesicons/survival.png",
    },
    {
      name: "Training",
      translationKey: "homepagecategoryTraining",
      image: "../../../static/assets/icons/categoriesicons/training.png",
    },
  ],
  services: [
    {
      name: "Manufacturing",
      translationKey: "homepagecategoryManufacturing",
      image: "../../../static/assets/icons/categoriesicons/manufacturing.png",
    },
    {
      name: "Customization",
      translationKey: "homepagecategoryCustomization",
      image: "../../../static/assets/icons/categoriesicons/customization.png",
    },
    {
      name: "Maintenance",
      translationKey: "homepagecategoryMaintenance",
      image: "../../../static/assets/icons/categoriesicons/maintenance.png",
    },
    {
      name: "Transport",
      translationKey: "homepagecategoryTransport",
      image: "../../../static/assets/icons/categoriesicons/transport.png",
    },
    {
      name: "Storage",
      translationKey: "homepagecategoryStorage",
      image: "../../../static/assets/icons/categoriesicons/storage.png",
    },
    {
      name: "Training",
      translationKey: "homepagecategoryTraining",
      image: "../../../static/assets/icons/categoriesicons/training.png",
    },
    {
      name: "Protection",
      translationKey: "homepagecategoryProtection",
      image: "../../../static/assets/icons/categoriesicons/protection.png",
    },
    {
      name: "Consulting",
      translationKey: "homepagecategoryConsulting",
      image: "../../../static/assets/icons/categoriesicons/consulting.png",
    },
    {
      name: "Research",
      translationKey: "homepagecategoryResearch",
      image: "../../../static/assets/icons/categoriesicons/reasearch.png",
    },
    {
      name: "Testing",
      translationKey: "homepagecategoryTesting",
      image: "../../../static/assets/icons/categoriesicons/testing.png",
    },
    {
      name: "Disposal",
      translationKey: "homepagecategoryDisposal",
      image: "../../../static/assets/icons/categoriesicons/disposal.png",
    },
    {
      name: "Surveillance",
      translationKey: "homepagecategorySurveillance",
      image: "../../../static/assets/icons/categoriesicons/surveilance.png",
    },
    {
      name: "Contracting",
      translationKey: "homepagecategoryContracting",
      image: "../../../static/assets/icons/categoriesicons/contracting.png",
    },
  ],
};
// Maps carousel card names → products page URL with ?category= param.
// The category value must match the data-category attributes in the products sidebar.
const categoryPageMap = {
  // WEAPONS CATEGORIES
  Firearms: "/products?category=firearms",
  Blades: "/products?category=blades",
  Blunts: "/products?category=blunts",
  Projectile: "/products?category=projectiles",
  Explosives: "/products?category=explosive",
  Electronic: "/products?category=electronic",
  Chemical: "/products?category=chemical",
  Biological: "/products?category=biological",
  Vehicle: "/products?category=vehicle",
  Cyber: "/products?category=cyber",
  Security: "/products?category=security",
  // EQUIPMENT CATEGORIES
  Ammunition: "/products?category=ammunition",
  Protective: "/products?category=protective",
  Tactical: "/products?category=tactical",
  Attachments: "/products?category=attachments",
  Maintenance: "/products?category=maintenance",
  Storage: "/products?category=storage",
  Communication: "/products?category=communication",
  Survival: "/products?category=survival",
  Training: "/products?category=training",
  // SERVICES — route to the services page (no category filter applied)
  Manufacturing: "/services",
  Customization: "/services",
  Transport: "/services",
  Protection: "/services",
  Consulting: "/services",
  Research: "/services",
  Testing: "/services",
  Disposal: "/services",
  Surveillance: "/services",
  Contracting: "/services",
};
// ────────── TRANSITION HELPERS ──────────────//
/**
 * Gets a translated string for the current language.
 * Falls back to English, then to the raw key if not found.
 * @param {string} key - The translation key
 * @returns {string} - The translated string
 */
function getTranslatedString(key) {
  const lang = localStorage.getItem("lang") || "english";
  return translations?.[lang]?.[key] || translations?.["english"]?.[key] || key;
}
// ────────── CATEGORY CAROUSEL FUNCTIONS ──────────────//
let currentCategory = "weapons";
let autoScrollId = null;
let resetTimeoutId = null;
let isScrolling = false;
let direction = 1; // 1 = right, -1 = left
function getWrapperEl() {
  return document.querySelector(".carousel-wrapper");
}
function getTrackEl() {
  return document.querySelector(".carousel-track");
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
  trackEl.innerHTML = "";
  // Create new cards for the selected category
  data.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "category-rect";
    card.dataset.index = index;
    card.dataset.name = item.name; // keep English name for routing
    const imageDiv = document.createElement("div");
    imageDiv.className = "category-image";
    const img = document.createElement("img");
    img.src = item.image;
    img.alt = item.name;
    imageDiv.appendChild(img);
    const label = document.createElement("div");
    label.className = "category-label";
    // Use translated string for display; store the key for live re-renders
    label.dataset.translate = item.translationKey;
    label.textContent = getTranslatedString(item.translationKey);
    card.appendChild(imageDiv);
    card.appendChild(label);
    trackEl.appendChild(card);
    // Add click handler — always route using the English name key
    card.addEventListener("click", () => {
      const targetPage = categoryPageMap[item.name];
      trackEl
        .querySelectorAll(".category-rect")
        .forEach((c) => c.classList.remove("active"));
      card.classList.add("active");
      if (targetPage) {
        window.location.href = targetPage;
      } else {
        console.warn(`No page mapping found for: ${item.name}`);
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
  const buttonContainer = document.querySelector(".category-buttons");
  if (!buttonContainer) return;
  // Each entry: { label shown in English, translationKey, data-category value }
  const buttonDefs = [
    {
      englishLabel: "Weapons",
      translationKey: "homepagecategoryBtnWeapons",
      category: "weapons",
    },
    {
      englishLabel: "Equipment",
      translationKey: "homepagecategoryBtnEquipment",
      category: "equipment",
    },
    {
      englishLabel: "Services",
      translationKey: "homepagecategoryBtnServices",
      category: "services",
    },
  ];
  buttonDefs.forEach(({ translationKey, category }) => {
    const button = document.createElement("button");
    button.className = "category-btn";
    button.dataset.category = category;
    button.dataset.translate = translationKey; // for setLanguage() to pick up
    button.textContent = getTranslatedString(translationKey);
    if (category === currentCategory) {
      button.classList.add("active");
    }
    button.addEventListener("click", () => {
      document
        .querySelectorAll(".category-btn")
        .forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      currentCategory = category;
      renderCategory(category);
    });
    buttonContainer.appendChild(button);
  });
}
function setupScrollListeners() {
  const wrapperEl = getWrapperEl();
  wrapperEl.addEventListener("mousedown", () => {
    isScrolling = true;
    stopAutoScroll();
  });
  wrapperEl.addEventListener(
    "wheel",
    () => {
      isScrolling = true;
      stopAutoScroll();
    },
    { passive: true },
  );
  wrapperEl.addEventListener("scroll", () => {
    if (isScrolling) {
      clearTimeout(resetTimeoutId);
      resetTimeoutId = setTimeout(() => {
        isScrolling = false;
        startAutoScroll();
      }, 3000);
    }
  });
  wrapperEl.addEventListener("mouseup", () => {
    isScrolling = false;
  });
  wrapperEl.addEventListener("mouseleave", () => {
    if (isScrolling) {
      isScrolling = false;
      resetTimeoutId = setTimeout(() => {
        startAutoScroll();
      }, 3000);
    }
  });
}
// ───────────────────────────────────────────//
//  SMOOTH SCROLL & CTA HANDLERS
// ───────────────────────────────────────────//
/**
 * Smooth scroll behavior for anchor links
 */
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    } else {
      console.log("Navigate to: " + this.getAttribute("href"));
    }
  });
});
/**
 * CTA Button Handler
 */
function handleCTA(action) {
  console.log("User clicked: " + action);
  // Replace with your actual navigation logic
  if (action === "create account") {
    alert("Redirecting to product catalog...");
  }
}
// ───────────────────────────────────────────//
//  INTERSECTION OBSERVER (SCROLL ANIMATION)
// ───────────────────────────────────────────//
/**
 * Add subtle animation to trust cards on scroll
 */
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};
const observer = new IntersectionObserver(function (entries) {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1";
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);
// Observe elements for lazy animation
document.querySelectorAll(".trust-card, .process-step").forEach((el) => {
  el.style.opacity = "0.95"; // Ensure visibility
  observer.observe(el);
});
// ───────────────────────────────────────────//
//  HOVER EFFECTS & Z-INDEX
// ───────────────────────────────────────────//
/**
 * Add hover effects to interactive elements
 */
document
  .querySelectorAll(".cta-btn, .trust-card, .process-step")
  .forEach((element) => {
    element.addEventListener("mouseenter", function () {
      // Optional: Add subtle feedback here
      this.style.zIndex = "100";
    });
    element.addEventListener("mouseleave", function () {
      this.style.zIndex = "1";
    });
  });
// ───────────────────────────────────────────//
// FEATURED CAROUSEL (FC)
// ───────────────────────────────────────────//
(function () {
  const pages = Array.from(document.querySelectorAll(".fc-page"));
  const dotsWrap = document.getElementById("fcDots");
  const pageLabel = document.getElementById("fcPageLabel");
  let cur = 0;
  pages.forEach((p, i) => {
    const dot = document.createElement("div");
    dot.className = "fc-dot" + (i === 0 ? " active" : "");
    const label = document.createElement("div");
    label.className = "fc-dot-label";
    label.textContent = p.dataset.label || "Page " + (i + 1);
    dot.appendChild(label);
    dot.addEventListener("click", () => fcGo(i));
    dotsWrap.appendChild(dot);
  });
  const dots = dotsWrap.querySelectorAll(".fc-dot");
  function fcGo(n) {
    pages[cur].classList.remove("active");
    dots[cur].classList.remove("active");
    cur = (n + pages.length) % pages.length;
    pages[cur].classList.add("active");
    dots[cur].classList.add("active");
    pageLabel.textContent = pages[cur].dataset.label || "Page " + (cur + 1);
  }
  document
    .getElementById("fcPrev")
    .addEventListener("click", () => fcGo(cur - 1));
  document
    .getElementById("fcNext")
    .addEventListener("click", () => fcGo(cur + 1));
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") fcGo(cur - 1);
    if (e.key === "ArrowRight") fcGo(cur + 1);
  });
})();
// ───────────────────────────────────────────//
// INITIALIZATION
// ───────────────────────────────────────────//
/**
 * Initialize category carousel on DOM ready
 */
document.addEventListener("DOMContentLoaded", () => {
  setupCategoryButtons();
  setupScrollListeners();
  renderCategory(currentCategory);
});
// ───────────────────────────────────────────//
// DEVELOPER CONSOLE MESSAGE
// ───────────────────────────────────────────//
/**
 * Console message for developers
 */
console.log(
  "%c Welcome to Armsdealer Website ",
  "background: #a8c49a; color: #1a1f1a; padding: 10px; font-size: 16px; font-weight: bold;",
);
console.log(
  "%c Edit content in the HTML sections above ",
  "color: #a8c49a; font-size: 12px;",
);
console.log(
  "%c All CSS is embedded - no external files needed ",
  "color: #a8c49a; font-size: 12px;",
);