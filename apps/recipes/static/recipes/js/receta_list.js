(() => {
  const tableEl = document.getElementById("tabla-recetas");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterNombre = document.getElementById("filter-nombre");
  const filterEstado = document.getElementById("filter-estado");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[0, "asc"]],
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
    const nombre = filterNombre?.value.trim() || "";
    const estado = filterEstado?.value || "";
    table.column(0).search(nombre, false, true);
    table.column(6).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterNombre) filterNombre.value = "";
    if (filterEstado) filterEstado.value = "";
    applyFilters();
  }

  filterNombre?.addEventListener("input", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
