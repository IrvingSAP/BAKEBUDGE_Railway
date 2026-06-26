(() => {
  const form = document.querySelector("[data-bb-noticia-form]");
  if (!form) return;

  const destBlock = form.querySelector(".noticias-destinatarios");
  const radios = form.querySelectorAll('input[name="alcance"]');

  function syncAlcance() {
    const val = form.querySelector('input[name="alcance"]:checked')?.value || "G";
    if (destBlock) destBlock.hidden = val !== "P";
    const sel = form.querySelector("#destinatarios");
    if (sel && val === "G") {
      Array.from(sel.options).forEach((option) => {
        option.selected = false;
      });
    }
  }

  radios.forEach((radio) => radio.addEventListener("change", syncAlcance));
  syncAlcance();

  function validateForm(event) {
    const errors = {};
    const alcance = form.querySelector('input[name="alcance"]:checked')?.value || "G";
    const tipo = form.querySelector("#tipo")?.value.trim() || "";
    const titulo = form.querySelector("#titulo")?.value.trim() || "";
    const fechaNoticia = form.querySelector("#fecha_noticia")?.value || "";
    const visibleDesde = form.querySelector("#visible_desde")?.value || "";
    const visibleHasta = form.querySelector("#visible_hasta")?.value || "";

    if (!tipo) {
      errors.tipo = "El tipo es obligatorio.";
    } else if (tipo.length > 20) {
      errors.tipo = "El tipo no puede superar 20 caracteres.";
    }
    if (!titulo) errors.titulo = "El título es obligatorio.";
    if (!fechaNoticia) errors.fecha_noticia = "La fecha de la noticia es obligatoria.";
    if (!visibleDesde) errors.visible_desde = "Indica la fecha «visible desde».";
    if (!visibleHasta) errors.visible_hasta = "Indica la fecha «visible hasta».";
    if (visibleDesde && visibleHasta && visibleHasta < visibleDesde) {
      errors.visible_hasta = "La fecha «visible hasta» debe ser posterior o igual a «visible desde».";
    }
    if (alcance === "P") {
      const sel = form.querySelector("#destinatarios");
      const selected = sel ? Array.from(sel.selectedOptions).length : 0;
      if (!selected) {
        errors.destinatarios = "Selecciona al menos un destinatario para noticias personales.";
      }
    }

    if (Object.keys(errors).length === 0) {
      return true;
    }

    event.preventDefault();
    if (window.BakeBudgeFormErrors) {
      BakeBudgeFormErrors.bindClearOnInput(form);
      BakeBudgeFormErrors.apply(form, errors);
    }
    const firstMessage = Object.values(errors)[0];
    if (window.BakeBudgeModal) {
      BakeBudgeModal.showError(firstMessage);
    }
    return false;
  }

  form.addEventListener("submit", validateForm);

  if (window.BakeBudgeFormErrors) {
    BakeBudgeFormErrors.bindClearOnInput(form);
  }
})();
