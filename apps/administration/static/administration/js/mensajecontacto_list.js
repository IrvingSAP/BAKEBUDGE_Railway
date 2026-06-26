(() => {
  const tableEl = document.getElementById("tabla-mensajecontacto");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterNombre = document.getElementById("filter-nombre");
  const filterEmail = document.getElementById("filter-email");
  const filterEstado = document.getElementById("filter-estado");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[0, "desc"]],
    columnDefs: [{ orderable: false, targets: 4 }],
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
    const email = filterEmail?.value.trim() || "";
    const estado = filterEstado?.value || "";

    table.column(1).search(nombre, false, true);
    table.column(2).search(email, false, true);
    table.column(3).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterNombre) filterNombre.value = "";
    if (filterEmail) filterEmail.value = "";
    if (filterEstado) filterEstado.value = "";
    applyFilters();
  }

  filterNombre?.addEventListener("input", applyFilters);
  filterEmail?.addEventListener("input", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
