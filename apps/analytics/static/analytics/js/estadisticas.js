(() => {
  const form = document.getElementById("estadisticas-filters");
  if (!form) return;

  form.querySelectorAll("select").forEach((el) => {
    el.addEventListener("change", () => form.submit());
  });

  const limpiar = document.getElementById("filter-limpiar");
  if (limpiar) {
    limpiar.addEventListener("click", () => {
      window.location.href = limpiar.dataset.clearUrl || form.action;
    });
  }

  const tableEl = document.getElementById("tabla-analytics");
  if (tableEl && typeof BakeBudgeDataTables !== "undefined") {
    BakeBudgeDataTables.init(tableEl, {
      order: [[7, "desc"]],
      columnDefs: [{ orderable: false, targets: 0 }],
      layout: {
        topStart: "pageLength",
        topEnd: null,
        bottomStart: "info",
        bottomEnd: "paging",
      },
    });
  }
})();
