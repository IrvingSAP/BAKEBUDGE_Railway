(() => {
  const tableEl = document.getElementById("tabla-productos");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterNombre = document.getElementById("filter-nombre");
  const filterCategoria = document.getElementById("filter-categoria");
  const filterEstado = document.getElementById("filter-estado");
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
    const categoria = filterCategoria?.value || "";
    const estado = filterEstado?.value || "";

    table.column(0).search(nombre, false, true);
    table.column(1).search(categoria ? `^${escapeRegex(categoria)}$` : "", true, false);
    table.column(4).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterNombre) filterNombre.value = "";
    if (filterCategoria) filterCategoria.value = "";
    if (filterEstado) filterEstado.value = "";
    applyFilters();
  }

  filterNombre?.addEventListener("input", applyFilters);
  filterCategoria?.addEventListener("change", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
