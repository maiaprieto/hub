# Organización Maia

Tablón personal para el móvil: avisos de la universidad y búsqueda de empleo.

Los datos van cifrados en `data.enc.json` (AES-GCM + PBKDF2) y solo se pueden
leer con la clave. El resto del repositorio es la app (`index.html`), que funciona
como app instalable (PWA) desde GitHub Pages.

Formato de los datos: [`tools/FORMATO.md`](tools/FORMATO.md).
