(() => {
  const form = document.querySelector("[data-bb-facturacion-form]");
  if (!form) return;

  const ownerField = form.querySelector("#owner");
  const isCreate = Boolean(ownerField);

  function calcularEndDate(startStr, modalidad) {
    if (!startStr) return "";
    const parts = startStr.split("-");
    if (parts.length !== 3) return "";
    const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    if (Number.isNaN(d.getTime())) return "";
    if (modalidad === "A") {
      d.setFullYear(d.getFullYear() + 1);
    } else {
      d.setMonth(d.getMonth() + 1);
    }
    return d.toISOString().slice(0, 10);
  }

  function syncEndDate() {
    const start = form.querySelector("#start_date");
    const end = form.querySelector("#end_date");
    const modalidad = form.querySelector("#modalidad");
    if (end && !end.value && start?.value && modalidad) {
      end.value = calcularEndDate(start.value, modalidad.value);
    }
  }

  form.querySelector("#start_date")?.addEventListener("change", syncEndDate);
  form.querySelector("#modalidad")?.addEventListener("change", syncEndDate);

  function validatePlazoDeGracia(errors) {
    const field = form.querySelector("#plazoDeGracia");
    const raw = (field?.value ?? "").trim();
    if (raw === "") {
      if (field) field.value = "0";
      return;
    }
    const days = Number.parseInt(raw, 10);
    if (Number.isNaN(days) || days < 0 || days > 30) {
      errors.plazo_de_gracia = "El plazo de gracia debe estar entre 0 y 30 días.";
    }
  }

  function validateActivation(errors, activar) {
    if (!activar) return;

    const paymentDate = form.querySelector("#payment_date");
    const paymentMethod = form.querySelector("#payment_method");
    const monto = form.querySelector("#monto");
    const moneda = form.querySelector("#moneda");
    const startDate = form.querySelector("#start_date");

    if (!paymentDate?.value) {
      errors.payment_date = "La fecha de pago es obligatoria al activar.";
    }
    if (!paymentMethod?.value) {
      errors.payment_method = "El método de pago es obligatorio al activar.";
    }
    const montoVal = parseFloat(monto?.value ?? "");
    if (Number.isNaN(montoVal) || montoVal <= 0) {
      errors.monto = "El monto debe ser mayor que 0 al activar.";
    }
    if (!moneda?.value) {
      errors.moneda = "La moneda es obligatoria al activar.";
    }
    if (!startDate?.value) {
      errors.start_date = "La fecha inicio es obligatoria al activar.";
    } else {
      syncEndDate();
    }
  }

  function validateForm(event) {
    const errors = {};
    const activar = event.submitter?.name === "guardar_activar";

    if (isCreate && !ownerField?.value) {
      errors.owner = "El campo «Usuario (owner)» es obligatorio.";
    }

    validatePlazoDeGracia(errors);
    validateActivation(errors, activar);

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
