# RAG Legal UNAL

Proyecto del **Semillero AtarraIA (Redes Neuronales)** de la Universidad Nacional de Colombia, sede Medellín.

Vamos a construir un sistema al que le preguntes por la normativa de la UNAL (acuerdos, resoluciones, estatutos y reglamentos) y te responda **citando la norma exacta**, no inventándose la respuesta.

**Página del proyecto:** https://mr-percival.github.io/rag-legal-unal/

## Cómo funciona un RAG

El modelo no se sabe la normativa. Primero buscamos los pedazos de las normas que tienen que ver con la pregunta y se los pasamos al modelo para que responda con eso.

1. **Normas:** bajamos los documentos del [Régimen Legal de la UNAL](http://www.legal.unal.edu.co).
2. **Chunks:** los partimos en pedazos con sentido (artículo, parágrafo).
3. **Embeddings:** cada pedazo se vuelve un vector que captura su significado.
4. **Base vectorial:** guardamos los vectores para buscar por parecido.
5. **LLM + contexto:** le pasamos al modelo la pregunta y los pedazos más parecidos.
6. **Respuesta con cita:** responde y dice de qué norma salió.

## Tarea de arranque

1. Ver [What is RAG?, de IBM](https://www.youtube.com/watch?v=T-D1OfcDW1M) (6 min; se pueden activar subtítulos en español).
2. [Dejar una pregunta real sobre la normativa](https://github.com/Mr-Percival/rag-legal-unal/issues/new?template=pregunta.yml). Con esas preguntas armamos el conjunto de prueba para medir si el RAG acierta cuando empiece a responder. Si no tienes cuenta de GitHub, [créala aquí](https://github.com/signup): es gratis y toma unos 5 minutos.

Eso es todo. La ruta de aprendizaje opcional, por nivel, está en la [página del proyecto](https://mr-percival.github.io/rag-legal-unal/#ruta).

## Estado

Arrancando. El alcance de la primera versión, las herramientas y cómo nos repartimos el trabajo se definen en la reunión de arranque (entre el 3 y el 6 de noviembre). Marca tu disponibilidad en el [When2meet](https://www.when2meet.com/?39606729-rn6Ir) hasta el lunes 2 de noviembre a las 8 p. m. La idea es que todos pasemos por todas las partes del RAG para aprenderlo completo.

## Equipo

Es un proyecto del Semillero AtarraIA y lo construimos entre todos. Para dudas de organización: [@Mr-Percival](https://github.com/Mr-Percival).

## Licencia

[MIT](LICENSE).
