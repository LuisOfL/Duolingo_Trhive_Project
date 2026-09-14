from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import (
    convertir_texto_a_embedding,
    buscar_chunks_cercanos,
    generar_respuesta_rag
)

# Inicializar la aplicación de FastAPI
app = FastAPI(
    title="Duolingo Thrive RAG API",
    description="API para el chatbot conversacional basada en AWS Bedrock, S3 y RDS PostgreSQL con pgvector.",
    version="1.0.0"
)

# Definir la estructura del JSON que recibirá la API de entrada
class PreguntaRequest(BaseModel):
    pregunta: str


@app.post("/chat", summary="Realizar una pregunta al chatbot RAG")
def endpoint_chat(request: PreguntaRequest):
    """
    Endpoint que recibe una pregunta, calcula su embedding, 
    busca los fragmentos más cercanos en RDS y genera la respuesta con el LLM de Bedrock.
    """
    pregunta_usuario = request.pregunta

    if not pregunta_usuario or not pregunta_usuario.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    # 1. Paso A: Convertir la pregunta a embedding con Titan de Bedrock[cite: 3]
    vector_pregunta = convertir_texto_a_embedding(pregunta_usuario)

    if not vector_pregunta:
        raise HTTPException(
            status_code=500, 
            detail="No se pudo generar el embedding de la pregunta en AWS Bedrock."
        )

    # 2. Paso B: Buscar los k=3 fragmentos más cercanos en RDS usando el índice IVF[cite: 3]
    chunks_relevantes = buscar_chunks_cercanos(vector_pregunta, k=3)

    # 3. Paso C: Enviar la pregunta y los fragmentos recuperados al LLM de Bedrock para la respuesta final[cite: 3]
    respuesta_final = generar_respuesta_rag(pregunta_usuario, chunks_relevantes)

    # Devolver el resultado en formato JSON estructurado
    return {
        "pregunta": pregunta_usuario,
        "total_chunks_utilizados": len(chunks_relevantes),
        "respuesta": respuesta_final
    }


@app.get("/", summary="Estado de la API")
def root():
    return {"mensaje": "¡La API de Duolingo Thrive RAG está activa y funcionando con éxito!"}