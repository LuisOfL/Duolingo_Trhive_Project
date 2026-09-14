from utils import (
    convertir_texto_a_embedding,
    buscar_chunks_cercanos,
    generar_respuesta_rag
)

def main():
    # 1. El usuario escribe una pregunta
    pregunta_usuario = "¿Cómo puedo ganar XP más rápido y mantener mi racha?"

    print(f"Pregunta: {pregunta_usuario}\n")

    # 2. Paso A: Convertir la pregunta a embedding con Titan de Bedrock
    vector_pregunta = convertir_texto_a_embedding(pregunta_usuario)

    if not vector_pregunta:
        print("❌ Proceso detenido: No se pudo generar el embedding de la pregunta.")
        return

    # 3. Paso B: Buscar los k=3 fragmentos más cercanos en RDS usando el índice IVF
    chunks_relevantes = buscar_chunks_cercanos(vector_pregunta, k=3)

    # 4. Paso C: Enviar la pregunta y los fragmentos recuperados al LLM de Bedrock para la respuesta final
    respuesta_final = generar_respuesta_rag(pregunta_usuario, chunks_relevantes)

    print("\n=== RESPUESTA DEL CHATBOT ===")
    print(respuesta_final)

if __name__ == "__main__":
    main()