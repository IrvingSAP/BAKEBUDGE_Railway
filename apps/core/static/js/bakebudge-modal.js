/**
 * Modal global BAKEBUDGE — mensajes de error, éxito, aviso e info.
 * Sin Bootstrap ni jQuery. Ver docs/ui-ux.md#modal-global-de-mensajes
 *
 * Uso:
 *   BakeBudgeModal.showError("El costo debe ser mayor que cero.");
 *   BakeBudgeModal.show({ type: "OK", message: "Producto guardado." });
 *
 * Django (template base): atributos en <body>
 *   data-modal-type="{{ error_tipo|default:'' }}"
 *   data-modal-message="{{ message_modal|default:''|escape }}"
 */
(function (global) {
  const TYPES = {
    ER: {
      key: "error",
      title: "Error de validación",
      headerClass: "bb-modal__header--error",
      btnClass: "bb-modal__btn--error",
      btnLabel: "Cerrar",
    },
    OK: {
      key: "success",
      title: "Operación exitosa",
      headerClass: "bb-modal__header--success",
      btnClass: "bb-modal__btn--success",
      btnLabel: "Aceptar",
    },
    AV: {
      key: "warning",
      title: "Atención",
      headerClass: "bb-modal__header--warning",
      btnClass: "bb-modal__btn--warning",
      btnLabel: "Entendido",
    },
    IN: {
      key: "info",
      title: "Información",
      headerClass: "bb-modal__header--info",
      btnClass: "bb-modal__btn--info",
      btnLabel: "Aceptar",
    },
  };

  const ALIASES = {
    error: "ER",
    ER: "ER",
    success: "OK",
    OK: "OK",
    warning: "AV",
    AV: "AV",
    info: "IN",
    IN: "IN",
  };

  let lastFocus = null;

  function getEl(id) {
    return document.getElementById(id);
  }

  function resolveType(tipo) {
    if (!tipo) return TYPES.ER;
    const code = ALIASES[String(tipo).trim()] || "ER";
    return TYPES[code] || TYPES.ER;
  }

  function setMessageContent(el, message, allowHtml) {
    if (!el) return;
    if (allowHtml) {
      el.innerHTML = message;
    } else {
      el.textContent = "";
      const lines = String(message).split(/\n/);
      lines.forEach((line, i) => {
        if (i > 0) el.appendChild(document.createElement("br"));
        el.appendChild(document.createTextNode(line));
      });
    }
  }

  function openModal() {
    const modal = getEl("bbModal");
    if (!modal) return;
    lastFocus = document.activeElement;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("bb-modal-open");
    const btn = getEl("bbModalBtn");
    btn?.focus();
  }

  function closeModal() {
    const modal = getEl("bbModal");
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("bb-modal-open");
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  function bindModalEvents() {
    const modal = getEl("bbModal");
    if (!modal || modal.dataset.bound === "1") return;
    modal.dataset.bound = "1";

    modal.querySelectorAll("[data-modal-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("is-open")) {
        closeModal();
      }
    });
  }

  function show(options) {
    bindModalEvents();

    const opts = typeof options === "string" ? { message: options } : options || {};
    const config = resolveType(opts.type || opts.tipo || "ER");
    const header = getEl("bbModalHeader");
    const title = getEl("bbModalTitle");
    const body = getEl("bbModalBody");
    const btn = getEl("bbModalBtn");

    if (header) {
      header.className = "bb-modal__header " + config.headerClass;
    }
    if (title) {
      title.textContent = opts.title || config.title;
    }
    setMessageContent(body, opts.message || opts.mensaje || "", Boolean(opts.html));
    if (btn) {
      btn.className = "bb-modal__btn " + config.btnClass;
      btn.textContent = opts.buttonLabel || config.btnLabel;
    }

    openModal();
    return { close: closeModal };
  }

  function showError(message, title) {
    return show({ type: "ER", message, title });
  }

  function showSuccess(message, title) {
    return show({ type: "OK", message, title });
  }

  function showWarning(message, title) {
    return show({ type: "AV", message, title });
  }

  function showInfo(message, title) {
    return show({ type: "IN", message, title });
  }

  function initFromBodyDataset() {
    const body = document.body;
    const msg = (body.dataset.modalMessage || "").trim();
    const tipo = (body.dataset.modalType || "").trim();
    if (msg) {
      show({ type: tipo || "ER", message: msg });
    }
  }

  const api = {
    show,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    close: closeModal,
    initFromBodyDataset,
  };

  global.BakeBudgeModal = api;

  document.addEventListener("DOMContentLoaded", () => {
    bindModalEvents();
    initFromBodyDataset();
  });
})(window);
