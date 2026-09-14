import json
import boto3

def convertir_texto_a_embedding(texto: str, region_name: str = "us-east-1") -> list:
    """
    Toma un texto de entrada, lo convierte en un vector de embedding 
    utilizando AWS Bedrock (Amazon Titan Text Embeddings v1) y lo devuelve.
    
    Args:
        texto (str): El string o pregunta que se quiere vectorizar.
        region_name (str): La región de AWS donde tienes configurado Bedrock.
        
    Returns:
        list: Una lista de floats con el embedding (1536 dimensiones).
    """
    if not texto or not texto.strip():
        print("El texto proporcionado está vacío.")
        return []

    # Inicializar el cliente de Bedrock Runtime
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name
    )
    
    model_id = "amazon.titan-embed-text-v1"
    
    payload = {
        "inputText": texto
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        # Leer la respuesta y extraer el vector
        response_body = json.loads(response["body"].read())
        embedding = response_body.get("embedding", [])
        
        return embedding
        
    except Exception as e:
        print(f"❌ Error al generar el embedding del texto con Bedrock: {e}")
        return []



import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def buscar_chunks_cercanos(vector_consulta: list, k: int = 3) -> list:
    """
    Toma un embedding de consulta y busca en la base de datos RDS PostgreSQL 
    los k chunks más cercanos utilizando el índice vectorial (IVF).
    
    Args:
        vector_consulta (list): El embedding de 1536 dimensiones (la pregunta vectorizada).
        k (int): Número de vecinos más cercanos a recuperar (por defecto 3).
        
    Returns:
        list: Una lista de diccionarios con la información de los chunks más similares.
    """
    if not vector_consulta:
        print("El vector de consulta está vacío.")
        return []

    resultados_cercanos = []
    connection = None
    cursor = None

    try:
        # Conexión forzando la base de datos 'vectorial-rag'
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database="vectorial-rag",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = connection.cursor()

        # Opcional: Aumentar el número de listas a sondear (nprobes) para mejorar la precisión del IVF
        # cursor.execute("SET ivfflat.probes = 2;")

        # Consulta SQL utilizando el operador de distancia de coseno de pgvector (<=>)
        # Nota: Convertimos la lista de Python a formato string vector de PostgreSQL '[val1, val2, ...]'
        vector_str = "[" + ",".join(map(str, vector_consulta)) + "]"

        sql_query = """
            SELECT section_title, source, chunk_text, (embedding <=> %s::vector) AS distancia
            FROM public.duolingo_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """

        # Pasamos el vector dos veces (para el SELECT y para el ORDER BY) y el límite k
        cursor.execute(sql_query, (vector_str, vector_str, k))
        filas = cursor.fetchall()

        for fila in filas:
            section_title, source, chunk_text, distancia = fila
            resultados_cercanos.append({
                "section_title": section_title,
                "source": source,
                "chunk_text": chunk_text,
                "distancia": float(distancia) # Menor distancia = mayor similitud
            })

        print(f"¡Búsqueda completada! Se recuperaron los {len(resultados_cercanos)} chunks más cercanos.")
        return resultados_cercanos

    except Exception as e:
        print(f"❌ Error al realizar la búsqueda vectorial en RDS: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


import boto3
from botocore.exceptions import ClientError

def generar_respuesta_rag(pregunta: str, chunks_cercanos: list, model_id: str = "google.gemma-3-12b-it", region_name: str = "us-east-1") -> str:
    """
    Toma la pregunta del usuario y los chunks recuperados de RDS, construye un contexto 
    y consulta a un modelo LLM en AWS Bedrock usando client.converse().
    """
    if not chunks_cercanos:
        return "Lo siento, no encontré información relevante en los documentos para responder a tu pregunta."

    # 1. Unir los textos de los chunks recuperados para armar el contexto
    contexto_textual = ""
    for i, chunk in enumerate(chunks_cercanos, 1):
        contexto_textual += f"\n--- Fragmento {i} [{chunk.get('section_title', 'Sin título')}] ---\n"
        contexto_textual += chunk.get('chunk_text', '') + "\n"

    # 2. Definir el prompt estructurado para el RAG
    prompt_completo = f"""
SISTEMA: Eres 'Duolingo Thrive', un asistente virtual experto y amigable. 
Tu objetivo es responder a la pregunta del usuario utilizando **única y exclusivamente** el contexto proporcionado a continuación. Si la respuesta no se encuentra en el contexto, di amablemente que no dispones de esa información. No inventes datos.

[CONTEXTO DE DOCUMENTOS]
{contexto_textual}

Pregunta del usuario: {pregunta}

Respuesta:
"""

    # 3. Estructura de mensajes compatible con client.converse()
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt_completo}]
        }
    ]

    client = boto3.client("bedrock-runtime", region_name=region_name)

    try:
        response = client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={
                "maxTokens": 800,
                "temperature": 0.3,
                "topP": 0.9
            }
        )
        
        # Extracción segura de la respuesta usando converse
        respuesta_ia = response['output']['message']['content'][0]['text']
        return respuesta_ia
        
    except ClientError as e:
        print(f"❌ Error de cliente en Bedrock LLM: {e}")
        return "Ocurrió un error de validación o permisos al consultar el modelo en Bedrock."
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return "Ocurrió un error inesperado al intentar generar la respuesta con la Inteligencia Artificial."



# 1. El usuario escribe una pregunta
pregunta_usuario = "¿Cómo puedo ganar XP más rápido y mantener mi racha?"

print(f"Pregunta: {pregunta_usuario}\n")

# 2. Paso A: Convertir la pregunta a embedding con Titan de Bedrock
vector_pregunta = convertir_texto_a_embedding(pregunta_usuario)

# 3. Paso B: Buscar los k=3 fragmentos más cercanos en RDS usando el índice IVF
chunks_relevantes = buscar_chunks_cercanos(vector_pregunta, k=3)

# 4. Paso C: Enviar la pregunta y los fragmentos recuperados al LLM de Bedrock para la respuesta final
respuesta_final = generar_respuesta_rag(pregunta_usuario, chunks_relevantes)

print("\n=== RESPUESTA DEL CHATBOT ===")
print(respuesta_final)