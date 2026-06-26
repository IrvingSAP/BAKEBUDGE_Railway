(() => {
  const tableEl = document.getElementById("tabla-categorias");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterNombre = document.getElementById("filter-nombre");
  const filterEstado = document.getElementById("filter-estado");
  const filterPredeterminada = document.getElementById("filter-predeterminada");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[0, "asc"]],
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
    const nombre = filterNombre?.value.trim() || "";
    const estado = filterEstado?.value || "";
    const predeterminada = filterPredeterminada?.value || "";

    table.column(1).search(nombre, false, true);
    table.column(5).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.column(4).search(predeterminada ? `^${escapeRegex(predeterminada)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterNombre) filterNombre.value = "";
    if (filterEstado) filterEstado.value = "";
    if (filterPredeterminada) filterPredeterminada.value = "";
    applyFilters();
  }

  filterNombre?.addEventListener("input", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterPredeterminada?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
