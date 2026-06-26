(() => {
  const form = document.getElementById("form-receta-delete");
  if (!form) return;

  document.getElementById("delete-receta-nombre").textContent = "Brownie clásico";

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const inactivar = event.submitter?.name === "inactivar";
    const msg = inactivar
      ? "Receta marcada como inactiva (demo)."
      : "Receta eliminada (demo).";
    BakeBudgeModal.showSuccess(msg);
  });
})();
