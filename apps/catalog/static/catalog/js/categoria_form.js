(() => {
  const select = document.getElementById("color");
  const preview = document.getElementById("colorPreview");
  if (!select || !preview) return;

  function syncPreview() {
    const value = select.value;
    preview.style.backgroundColor = value || "";
    preview.classList.toggle("categoria-color-badge--empty", !value);
  }

  select.addEventListener("change", syncPreview);
  syncPreview();
})();
