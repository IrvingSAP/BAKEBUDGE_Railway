(() => {
  const tableEl = document.getElementById("tabla-ordenes");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterBusqueda = document.getElementById("filter-busqueda");
  const filterEstado = document.getElementById("filter-estado");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[5, "desc"]],
    columnDefs: [{ orderable: false, targets: 6 }],
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
    const busqueda = filterBusqueda?.value.trim() || "";
    const estado = filterEstado?.value || "";
    table.column(0).search(busqueda, false, true);
    table.column(1).search(busqueda, false, true);
    table.column(4).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.draw();
  }

  filterBusqueda?.addEventListener("input", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", () => {
    if (filterBusqueda) filterBusqueda.value = "";
    if (filterEstado) filterEstado.value = "";
    applyFilters();
  });
})();
