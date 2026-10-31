# Decisiones del proyecto RAG Legal UNAL

## 2026-10-31 · Página de presentación (docs/index.html, GitHub Pages)

- **Usuario:** estudiantes del semillero AtarraIA, con niveles distintos. Abren la página desde el celular, con el enlace que llega por WhatsApp.
- **Acción principal:** ir al repositorio. La tarea mínima es dejar una pregunta real sobre la normativa en un issue.
- **La votación de la fecha va por fuera:** se hace en el grupo de WhatsApp (lo decidió Nicolás).
- **Estilo:** cyberpunk con una paleta inspirada en *Cyberpunk: Edgerunners*, pedido explícito de Nicolás. El negro con neón no es un valor por defecto: es lo que pidió el líder.
  - Tokens: noche `#0d0920`, paneles `#171033`, luna (texto) `#efeaf7`, amarillo de acción `#f5e829` (chaqueta de David), cian de marca `#5ce1e6` y rosa de acento `#ff4fb8` (pelo de Lucy).
  - Fuentes: Chakra Petch para títulos (angular, de interfaz técnica) y Barlow para el texto (industrial y legible). Space Grotesk se evitó porque es la huella típica de IA.
  - La decoración es propia: luna, ciudad generada en SVG, lluvia en canvas, un rastro de color en el título que evoca el sandevistan y una terminal que se escribe sola. **No se usan imágenes ni GIFs de la serie** porque tienen derechos de autor y el repositorio es público.
  - Las animaciones respetan `prefers-reduced-motion`.
- **Enlaces de cursos:** apuntan a búsquedas de YouTube, porque no se verificó cada URL directa.
- **Demo de la terminal:** es una maqueta. El artículo aparece como `??` para no inventar contenido normativo.
- **PDF descartado (31-10):** Nicolás decidió que basta con la página. `../arranque_rag_legal.pdf` y su .tex quedan como borrador viejo y no se usan.

## 2026-10-31 · Ajustes después de la crítica y de Nicolás

- **Crítica UX aplicada:**
  - La tarea sube a la segunda escena y queda como el botón principal de la portada.
  - Los enlaces de la tarea van directos al video; se verificó el video de IBM (`T-D1OfcDW1M`).
  - Se agregaron las etiquetas Open Graph y la imagen `og.png` para la vista previa en WhatsApp.
  - La convocatoria quedó fechada.
  - La ruta va por nivel.
  - La página tiene firma.
  - Se corrigieron los fallos de la luna y los márgenes en celular.
- **Nicolás pidió un lenguaje más de cine:** título en cursiva inclinada con sombra dura estilo Trigger, cintas de advertencia entre escenas, letreros de neón verticales, AV volando, dos siluetas en una azotea mirando la luna, rastro del cursor y del título tipo sandevistan, terminal tipo braindance y un pulso que recorre el circuito del RAG.
- **Nicolás pidió que fuera asequible y que no saturara:**
  - Tarea obligatoria: 1 video de 6 minutos (IBM, con subtítulos en español) y 1 pregunta.
  - Karpathy y todo lo demás pasan a ser opcionales, con la indicación de que basta un video.

## 2026-10-31 · La página es el centro del proyecto

- **Nicolás decidió que, de ahora en adelante, la página y el repo centralizan todo**, en lugar del grupo de WhatsApp.
- La página tiene una barra fija (Tarea, Reunión, Enlaces, Novedades) y una sección "Todo el proyecto, aquí", con el repositorio, las preguntas, la disponibilidad y el enlace de la reunión, más una lista de **Novedades**.
- **Para actualizarla:** se edita `docs/index.html` (agregar un `<li>` arriba en Novedades, activar el enlace de la reunión, etc.) y se hace push a `main`. GitHub Pages la publica sola.
- **Disponibilidad:** el When2meet https://www.when2meet.com/?39606729-rn6Ir (del 3 al 6 de noviembre, de 8:00 a 21:00, hora de Bogotá) reemplaza la votación por WhatsApp.
- **Roles:** no son fijos. El semillero es formativo, así que todos rotan por datos, búsqueda, modelo y evaluación para aprender el RAG completo.

## 2026-10-31 · Semanas, luna de vectores y revisión del agente estudiante

- **Contenido semanal en `docs/datos.json`** (semanas, novedades y datos de la reunión). La página lo lee al cargar y, para actualizarla, no hay que tocar el HTML. El enlace de la reunión va por WhatsApp, no en la página (lo decidió Nicolás).
- **Luna final:** es una esfera 3D de partículas que representa el espacio de embeddings. Cada tanto dispara una consulta que enciende su top-k. Reemplazó a unas siluetas de personas que se veían genéricas.
- **Cursor:** cinta arcoíris con estelas de aberración cromática y onda al hacer clic. Se quitaron los cuadrados.
- **Agente estudiante (31-10). Se aplicó:**
  - El When2meet pasa a ser el paso 1 de la tarea y el botón de la portada dice "3 pasos, unos 15 minutos".
  - Ahora se dice cómo se anuncia el horario.
  - Las dudas van por el grupo de WhatsApp.
  - El video de IBM sale de los niveles opcionales.
  - Ajustes en celular: terminal, sello, novedades y rombos de las semanas. Se agregó un favicon.
- **Pendiente de Nicolás:** la fecha límite para marcar el When2meet y dejar la pregunta, y cuánto tiempo semanal va a pedir el proyecto.
