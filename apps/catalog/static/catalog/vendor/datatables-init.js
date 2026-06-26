/**
 * Configuración estándar BAKEBUDGE para DataTables 2.x.
 * Requiere jQuery cargado antes (dependencia del paquete estándar).
 * Manual oficial: https://datatables.net/manual/
 *
 * Uso:
 *   BakeBudgeDataTables.init("#tabla-productos");
 *   BakeBudgeDataTables.init("#tabla-productos", { order: [[0, "asc"]] });
 *   BakeBudgeDataTables.initMarked(); // tablas con [data-datatable]
 */
const BakeBudgeDataTables = (() => {
  const I18N_ES = window.BAKEBUDGE_DT_I18N_URL || "/static/catalog/i18n/datatables-es-ES.json";

  /** @see https://datatables.net/reference/option/ */
  const defaults = {
    language: { url: I18N_ES },
    pageLength: 10,
    lengthMenu: [10, 20, 50],
    order: [],
    layout: {
      topStart: "pageLength",
      topEnd: "search",
      bottomStart: "info",
      bottomEnd: "paging",
    },
  };

  function resolveElement(table) {
    if (typeof table === "string") {
      return document.querySelector(table);
    }
    return table;
  }

  function init(table, options = {}) {
    if (typeof DataTable === "undefined") {
      return null;
    }
    const el = resolveElement(table);
    if (!el) {
      return null;
    }
    return new DataTable(el, { ...defaults, ...options });
  }

  function initMarked(selector = ".table-bakebudge[data-datatable]") {
    document.querySelectorAll(selector).forEach((table) => {
      init(table);
    });
  }

  return { defaults, init, initMarked };
})();
