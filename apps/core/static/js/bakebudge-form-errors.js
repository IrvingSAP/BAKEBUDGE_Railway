/**
 * Resalta campos con error y enfoca el primero inválido.
 * El modal global muestra message_modal desde la vista Django.
 */
(function (global) {
  function findControl(form, fieldName) {
    return (
      form.querySelector(`#${CSS.escape(fieldName)}`) ||
      form.querySelector(`[name="${fieldName}"]`)
    );
  }

  function apply(form, errors, options) {
    options = options || {};
    if (!form || !errors || typeof errors !== "object") {
      return;
    }

    let firstControl = null;

    Object.entries(errors).forEach(([fieldName, message]) => {
      const control = findControl(form, fieldName);
      if (!control) {
        return;
      }

      const wrapper = control.closest(".form-field");
      if (!wrapper) {
        return;
      }

      wrapper.classList.add("form-field--invalid");
      control.setAttribute("aria-invalid", "true");

      let errorEl = wrapper.querySelector(".form-field__error");
      if (!errorEl) {
        errorEl = document.createElement("p");
        errorEl.className = "form-field__error";
        errorEl.id = `${fieldName}-error`;
        wrapper.appendChild(errorEl);
      }

      errorEl.textContent = message;
      control.setAttribute("aria-describedby", errorEl.id);

      if (!firstControl) {
        firstControl = control;
      }
    });

    if (firstControl && options.focus !== false && typeof firstControl.focus === "function") {
      firstControl.focus({ preventScroll: false });
      firstControl.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  function bindClearOnInput(form) {
    if (!form || form.dataset.bbValidateBound === "1") {
      return;
    }
    form.dataset.bbValidateBound = "1";

    form.addEventListener(
      "input",
      (event) => {
        const control = event.target;
        if (!(control instanceof HTMLElement)) {
          return;
        }
        const wrapper = control.closest(".form-field--invalid");
        if (!wrapper) {
          return;
        }
        wrapper.classList.remove("form-field--invalid");
        control.removeAttribute("aria-invalid");
        const errorEl = wrapper.querySelector(".form-field__error");
        if (errorEl) {
          errorEl.remove();
        }
      },
      true
    );
  }

  global.BakeBudgeFormErrors = {
    apply,
    bindClearOnInput,
  };
})(window);
