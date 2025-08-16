(function () {
  function formatPriceCommas() {
    document.querySelectorAll('.price-commas').forEach(el => {
      const raw = el.getAttribute('data-price') || el.textContent;
      const n = parseInt(String(raw).replace(/[^\d]/g, ''), 10);
      el.textContent = Number.isFinite(n) ? n.toLocaleString('ko-KR') : raw;
    });
  }

  if (document.readyState !== "loading") {
    formatPriceCommas();
  } else {
    document.addEventListener("DOMContentLoaded", formatPriceCommas);
  }

  window.formatPriceCommas = formatPriceCommas;
})();