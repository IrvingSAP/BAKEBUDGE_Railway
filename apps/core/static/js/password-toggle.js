/**
 * BAKEBUDGE — Toggle visibilidad de contraseña
 * Inicializa todos los .password-field del documento.
 */
(function () {
  "use strict";

  var LABEL_SHOW = "Mostrar contraseña";
  var LABEL_HIDE = "Ocultar contraseña";

  function setPasswordVisible(input, btn, visible) {
    input.type = visible ? "text" : "password";
    btn.setAttribute("aria-pressed", visible ? "true" : "false");
    btn.setAttribute("aria-label", visible ? LABEL_HIDE : LABEL_SHOW);

    var iconShow = btn.querySelector(".password-field__icon--show");
    var iconHide = btn.querySelector(".password-field__icon--hide");
    if (iconShow) {
      iconShow.hidden = visible;
    }
    if (iconHide) {
      iconHide.hidden = !visible;
    }
  }

  function initPasswordField(root) {
    var input = root.querySelector(".password-field__input");
    var btn = root.querySelector(".password-field__toggle");
    if (!input || !btn) {
      return;
    }

    btn.addEventListener("click", function () {
      setPasswordVisible(input, btn, input.type === "password");
    });

    var form = root.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        setPasswordVisible(input, btn, false);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".password-field").forEach(initPasswordField);
  });
})();
