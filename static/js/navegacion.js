// Navegación (fase E1a): menú fijo con saltos a cada sección y cohete para volver arriba. No llama a ninguna web.
// El menú se construye con las secciones que existen en la página (atributo data-menu), así que si una
// sección no aparece tampoco sale su enlace. Sin JavaScript no hay menú, pero la página funciona igual.
const destinos = [...document.querySelectorAll("[data-menu]")];  // secciones que quieren salir en el menú
const calmaNav = matchMedia("(prefers-reduced-motion: reduce)").matches;  // ¿reducir movimiento?

if (destinos.length) {
    const menu = document.createElement("nav");  // la barra (createElement: crea la etiqueta sin escribir HTML)
    menu.className = "menu";
    menu.setAttribute("aria-label", "Secciones");  // lectores de pantalla: qué es esta barra
    const enlaces = destinos.map(d => {  // map: un enlace por sección, en el mismo orden
        const a = document.createElement("a");
        a.href = "#" + d.id;  // salto a su id
        a.textContent = d.dataset.menu;  // textContent: texto, nunca HTML
        menu.appendChild(a);
        return a;
    });
    document.querySelector("h1").after(menu);  // justo debajo del título

    // Resaltar la sección que se está viendo: IntersectionObserver avisa cuando una sección entra
    // en una franja fina del centro de la pantalla (sin tener que calcular posiciones en cada scroll)
    const vigia = new IntersectionObserver(entradas => {
        entradas.forEach(e => {
            if (e.isIntersecting) enlaces.forEach((a, i) => a.classList.toggle("activo", destinos[i] === e.target));
        });
    }, { rootMargin: "-45% 0px -50% 0px" });  // márgenes negativos: solo cuenta la franja central
    destinos.forEach(d => vigia.observe(d));
}

// Cohete: aparece al bajar más de una pantalla; al pulsarlo despega y sube al principio
const cohete = document.getElementById("cohete");  // null en la página sin resultados
if (cohete) {
    addEventListener("scroll", () => (cohete.hidden = scrollY < innerHeight), { passive: true });  // passive: no frena el scroll
    cohete.addEventListener("click", () => {
        cohete.classList.add("despega");  // CSS: sale volando hacia arriba con estela
        scrollTo({ top: 0, behavior: calmaNav ? "auto" : "smooth" });  // auto = salto directo, sin animación
        setTimeout(() => cohete.classList.remove("despega"), 900);  // listo para el siguiente viaje
    });
}
