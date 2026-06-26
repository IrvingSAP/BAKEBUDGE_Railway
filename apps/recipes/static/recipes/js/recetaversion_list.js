(() => {
  const tableEl = document.getElementById("tabla-versiones");
  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;

  BakeBudgeDataTables.init(tableEl, {
    order: [[0, "desc"]],
    columnDefs: [{ orderable: false, targets: 7 }],
    layout: {
      topStart: "pageLength",
      topEnd: null,
      bottomStart: "info",
      bottomEnd: "paging",
    },
  });
})();
