(() => {

  const tableEl = document.getElementById("tabla-facturacion");

  if (!tableEl || typeof BakeBudgeDataTables === "undefined") return;



  const filterUsuario = document.getElementById("filter-usuario");

  const filterEstado = document.getElementById("filter-estado");

  const filterModalidad = document.getElementById("filter-modalidad");

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

    const estado = filterEstado?.value || "";

    const modalidad = filterModalidad?.value || "";



    table.column(0).search(usuario, false, true);

    table.column(2).search(estado ? `^${escapeRegex(estado)}$` : "", true, false);

    table.column(1).search(modalidad ? `^${escapeRegex(modalidad)}$` : "", true, false);

    table.draw();

  }



  function clearFilters() {

    if (filterUsuario) filterUsuario.value = "";

    if (filterEstado) filterEstado.value = "";

    if (filterModalidad) filterModalidad.value = "";

    applyFilters();

  }



  filterUsuario?.addEventListener("input", applyFilters);

  filterEstado?.addEventListener("change", applyFilters);

  filterModalidad?.addEventListener("change", applyFilters);

  filterLimpiar?.addEventListener("click", clearFilters);



  const params = new URLSearchParams(window.location.search);

  const owner = params.get("owner");

  if (owner && filterUsuario) {

    filterUsuario.value = owner;

    applyFilters();

  }

})();

