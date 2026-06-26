(() => {
  const sidebarToggle = document.querySelector("[data-sidebar-toggle]");
  const sidebar = document.querySelector("[data-app-sidebar]");
  const overlay = document.querySelector("[data-sidebar-overlay]");

  function closeSidebar() {
    sidebar?.classList.remove("is-open");
    overlay?.classList.remove("is-visible");
  }

  function openSidebar() {
    sidebar?.classList.add("is-open");
    overlay?.classList.add("is-visible");
  }

  sidebarToggle?.addEventListener("click", () => {
    if (sidebar?.classList.contains("is-open")) {
      closeSidebar();
    } else {
      openSidebar();
    }
  });

  overlay?.addEventListener("click", closeSidebar);

  const current = document.body.dataset.page;
  document.querySelectorAll("[data-nav]").forEach((link) => {
    if (link.dataset.nav === current) {
      link.classList.add("active");
    }
  });

  const navGroups = {
    "catalogo-base": ["categorias", "conversiones", "costos-indirectos"],
    administracion: [
      "usuarios",
      "facturacion",
      "gestion-noticias",
      "mensajes-contacto",
    ],
  };

  document.querySelectorAll("[data-nav-group]").forEach((group) => {
    const groupId = group.dataset.navGroup;
    const pages = navGroups[groupId] || [];
    const groupToggle = group.querySelector("[data-nav-group-toggle]");
    if (!groupToggle) return;

    if (pages.includes(current)) {
      group.classList.add("is-open");
      groupToggle.setAttribute("aria-expanded", "true");
      groupToggle.classList.add("active");
    }

    groupToggle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const isOpen = group.classList.toggle("is-open");
      groupToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (isOpen) {
        groupToggle.classList.add("active");
      } else if (!pages.includes(current)) {
        groupToggle.classList.remove("active");
      }
    });
  });

  if (typeof BakeBudgeDataTables !== "undefined") {
    BakeBudgeDataTables.initMarked();
  }
})();
