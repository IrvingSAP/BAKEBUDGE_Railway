(() => {
  const tableEl = document.getElementById("tabla-conversiones");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  const filterTexto = document.getElementById("filter-texto");
  const filterAlcance = document.getElementById("filter-alcance");
  const filterHacia = document.getElementById("filter-hacia");
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
    const texto = filterTexto?.value.trim() || "";
    const alcance = filterAlcance?.value || "";
    const hacia = filterHacia?.value || "";

    table.column(0).search(texto, false, true);

    if (alcance === "generica") {
      table.column(1).search("^Genérica$", true, false);
    } else if (alcance === "producto") {
      table.column(1).search("^(?!Genérica$).+", true, false);
    } else {
      table.column(1).search("", true, false);
    }

    table.column(3).search(hacia ? `^${escapeRegex(hacia)}$` : "", true, false);
    table.draw();
  }

  function clearFilters() {
    if (filterTexto) filterTexto.value = "";
    if (filterAlcance) filterAlcance.value = "";
    if (filterHacia) filterHacia.value = "";
    applyFilters();
  }

  filterTexto?.addEventListener("input", applyFilters);
  filterAlcance?.addEventListener("change", applyFilters);
  filterHacia?.addEventListener("change", applyFilters);
  filterLimpiar?.addEventListener("click", clearFilters);
})();
