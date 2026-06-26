(() => {

  const tableEl = document.getElementById("tabla-usuarios");

  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;



  const filterUsuario = document.getElementById("filter-usuario");

  const filterTipo = document.getElementById("filter-tipo");

  const filterEstado = document.getElementById("filter-estado");

  const filterEmailVerificado = document.getElementById("filter-email-verificado");

  const filterLimpiar = document.getElementById("filter-limpiar");



  const table = BakeBudgeDataTables.init(tableEl, {

    order: [[7, "desc"]],

    columnDefs: [{ orderable: false, targets: 8 }],

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

    const usuario = filterUsuario?.value.trim() || "";

    const tipo = filterTipo?.value || "";

    const estado = filterEstado?.value || "";

    const emailVerificado = filterEmailVerificado?.value || "";



    table.column(0).search(usuario, false, true);

    table.column(3).search(tipo ? `^${escapeRegex(tipo)}$` : "", true, false);

    table.column(4).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);

    table.column(6).search(emailVerificado ? `^${escapeRegex(emailVerificado)}$` : "", true, false);

    table.draw();

  }



  function clearFilters() {

    if (filterUsuario) filterUsuario.value = "";

    if (filterTipo) filterTipo.value = "";

    if (filterEstado) filterEstado.value = "";

    if (filterEmailVerificado) filterEmailVerificado.value = "";

    applyFilters();

  }



  filterUsuario?.addEventListener("input", applyFilters);

  filterTipo?.addEventListener("change", applyFilters);

  filterEstado?.addEventListener("change", applyFilters);

  filterEmailVerificado?.addEventListener("change", applyFilters);

  filterLimpiar?.addEventListener("click", clearFilters);

})();

