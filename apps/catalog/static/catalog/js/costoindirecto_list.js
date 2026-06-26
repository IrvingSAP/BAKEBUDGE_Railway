(() => {
  const tableEl = document.getElementById("tabla-costos-indirectos");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterNombre = document.getElementById("filter-nombre");
  const filterEstado = document.getElementById("filter-estado");
  const filterUnidad = document.getElementById("filter-unidad");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[0, "asc"]],
    columnDefs: [{ orderable: false, targets: 5 }],
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
    const unidad = filterUnidad?.value || "";
    table.column(0).search(nombre, false, true);
    table.column(4).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.column(2).search(unidad ? `^${escapeRegex(unidad)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterNombre) filterNombre.value = "";
    if (filterEstado) filterEstado.value = "";
    if (filterUnidad) filterUnidad.value = "";
    applyFilters();
  }

  filterNombre?.addEventListener("input", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterUnidad?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
