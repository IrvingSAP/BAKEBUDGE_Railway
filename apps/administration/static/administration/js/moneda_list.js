(() => {
  const tableEl = document.getElementById("tabla-monedas");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterTexto = document.getElementById("filter-texto");
  const filterActiva = document.getElementById("filter-activa");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[5, "asc"], [0, "asc"]],
    columnDefs: [{ orderable: false, targets: 7 }],
    layout: {
      topStart: "pageLength",
      topEnd: null,
      bottomStart: "info",
      bottomEnd: "paging",
    },
  });

  if (!table) return;

  function escapeRegex(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function applyFilters() {
    const texto = filterTexto?.value.trim() || "";
    const activa = filterActiva?.value || "";

    table.column(1).search(texto, false, true);
    table.column(4).search(activa ? `^${escapeRegex(activa)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterTexto) filterTexto.value = "";
    if (filterActiva) filterActiva.value = "";
    applyFilters();
  }

  filterTexto?.addEventListener("input", applyFilters);
  filterActiva?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
