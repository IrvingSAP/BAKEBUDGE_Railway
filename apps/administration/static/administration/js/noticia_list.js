(() => {
  const tableEl = document.getElementById("tabla-noticias");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterTitulo = document.getElementById("filter-titulo");
  const filterTipo = document.getElementById("filter-tipo");
  const filterAlcance = document.getElementById("filter-alcance");
  const filterEstado = document.getElementById("filter-estado");
  const filterLimpiar = document.getElementById("filter-limpiar");

  const table = BakeBudgeDataTables.init(tableEl, {
    order: [[6, "desc"]],
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
    const titulo = filterTitulo?.value.trim() || "";
    const tipo = filterTipo?.value.trim() || "";
    const alcance = filterAlcance?.value || "";
    const estado = filterEstado?.value || "";

    table.column(0).search(titulo, false, true);
    table.column(1).search(tipo, false, true);
    table.column(2).search(alcance ? `^${escapeRegex(alcance)}$` : "", true, false);
    table.column(5).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterTitulo) filterTitulo.value = "";
    if (filterTipo) filterTipo.value = "";
    if (filterAlcance) filterAlcance.value = "";
    if (filterEstado) filterEstado.value = "";
    applyFilters();
  }

  filterTitulo?.addEventListener("input", applyFilters);
  filterTipo?.addEventListener("input", applyFilters);
  filterAlcance?.addEventListener("change", applyFilters);
  filterEstado?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
