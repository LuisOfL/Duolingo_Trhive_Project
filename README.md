# Duolingo Thrive: RAG System para Datos de Soporte

¡Hola y bienvenido al proyecto! Este repositorio contiene una solución basada en **RAG (Retrieval-Augmented Generation)** diseñada específicamente para potenciar y agilizar el soporte en **Duolingo Thrive**.

---

## 🚀 Presentación del Proyecto

El objetivo de este proyecto es conectar un modelo de lenguaje con la base de conocimientos y datos de soporte de Duolingo Thrive. Gracias a la arquitectura RAG, el sistema es capaz de buscar información precisa en los documentos de ayuda y generar respuestas contextualizadas, exactas y rápidas para los usuarios o agentes de soporte.

### Características Principales
- **Búsqueda Semántica:** Recuperación de fragmentos de soporte relevantes mediante embeddings vectoriales.
- **Generación Contextual:** Respuestas precisas basadas exclusivamente en la documentación oficial de Duolingo Thrive.
- **Eficiencia:** Reducción de tiempos de respuesta en las consultas de soporte.

---

## 🏗️ Arquitectura y Funcionamiento

El flujo del sistema RAG opera en los siguientes pasos:

1. **Ingesta y Procesamiento de Datos:** Los documentos de soporte de Duolingo Thrive (PDFs, Markdown, FAQs) se limpian y se dividen en fragmentos (*chunks*).
2. **Vectorización (Embeddings):** Cada fragmento se convierte en un vector numérico utilizando un modelo de embeddings y se almacena en una base de datos vectorial.
3. **Recuperación (Retrieval):** Cuando un usuario realiza una consulta, el sistema busca los fragmentos vectoriales más cercanos semánticamente a la pregunta.
4. **Generación (Generation):** La consulta del usuario junto con el contexto recuperado se envían al LLM para redactar una respuesta coherente y fundamentada.

```
[ Consulta del Usuario ] 
        │
        ▼
[ Buscador Vectorial ] ──( Recupera contexto )──> [ Base de Datos Vectorial ]
        │
        ▼
[ LLM (Generación) ] <──( Contexto + Pregunta )
        │
        ▼
[ Respuesta Final para Soporte ]
```

---

