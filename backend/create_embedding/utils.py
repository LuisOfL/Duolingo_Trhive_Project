import os
import io
import re
import json
import boto3
import pymupdf
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def extraer_texto_de_pdf_s3(bucket_name: str, file_key: str) -> str:
    """Descarga un PDF desde S3 y extrae todo su contenido de texto plano."""
    s3_client = boto3.client('s3')
    
    print(f"Descargando '{file_key}' desde el bucket S3 '{bucket_name}'...")
    
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        pdf_bytes = response['Body'].read()
        texto_completo = ""
        
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                texto_completo += page.get_text() + "\n"
                
        print("¡Texto extraído con éxito desde S3!")
        return texto_completo.strip()
        
    except Exception as e:
        print(f"Error al procesar el archivo desde S3: {e}")
        return ""


def dividir_pdf_duolingo_por_secciones(texto_completo: str) -> list:
    """Divide el texto del PDF de Duolingo respetando las secciones numeradas del documento."""
    patron_secciones = re.compile(r'\n(?=\d+\.\s+[A-ZÁÉÍÓÚa-záéíóú\s]+)')
    secciones = patron_secciones.split(texto_completo)
    chunks_estructurados = []
    
    for i, seccion in enumerate(secciones):
        seccion_limpia = seccion.strip()
        if not seccion_limpia:
            continue
            
        lineas = seccion_limpia.split('\n')
        titulo_seccion = lineas[0] if lineas else f"Seccion_{i}"
        
        chunks_estructurados.append({
            "chunk_id": i,
            "section_title": titulo_seccion,
            "text": seccion_limpia,
            "source": "Primeros pasos: cómo aprender idiomas en Duolingo (Cindy Blanco, Ph.D., 2025)",
            "token_estimate": len(seccion_limpia.split())
        })
        
    print(f"Total de chunks semánticos generados: {len(chunks_estructurados)}")
    return chunks_estructurados


def generar_embeddings_chunks_aws(chunks_optimizados: list, region_name: str = "us-east-1") -> list:
    """Genera vectores de embedding para cada chunk utilizando AWS Bedrock (Amazon Titan)."""
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=region_name
    )
    
    model_id = "amazon.titan-embed-text-v1"
    print(f"Generando vectores con AWS Bedrock para {len(chunks_optimizados)} chunks...")
    
    for i, chunk in enumerate(chunks_optimizados):
        payload = {
            "inputText": chunk["text"]
        }
        
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            
            response_body = json.loads(response["body"].read())
            chunk["embedding"] = response_body.get("embedding", [])
            print(f"[{i+1}/{len(chunks_optimizados)}] Vectorizado con Bedrock: {chunk.get('section_title', 'Chunk')}")
            
        except Exception as e:
            print(f"Error al vectorizar el chunk {i} con Bedrock: {e}")
            chunk["embedding"] = []
            
    return chunks_optimizados


def insertar_chunks_con_vectores_en_rds(chunks_con_vectores: list):
    """Inserta los chunks con sus respectivos vectores en la base de datos RDS PostgreSQL."""
    if not chunks_con_vectores:
        print("La lista de chunks está vacía. No hay nada que insertar.")
        return

    connection = None
    cursor = None

    try:
        print("Conectando a Amazon RDS PostgreSQL...")
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database="vectorial-rag",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = connection.cursor()
        
        cursor.execute("SELECT current_database();")
        db_actual = cursor.fetchone()[0]
        print(f"🔗 Conectado a la base de datos: '{db_actual}'")
        
        print(f"Insertando {len(chunks_con_vectores)} chunks vectorizados en la base de datos...")
        
        sql_insert = """
            INSERT INTO public.duolingo_chunks (section_title, source, chunk_text, embedding)
            VALUES (%s, %s, %s, %s);
        """
        
        for chunk in chunks_con_vectores:
            section_title = chunk.get("section_title", "Sin título")
            source = chunk.get("source", "Duolingo Thrive Document")
            chunk_text = chunk.get("text", "")
            embedding = chunk.get("embedding", [])
            
            if not embedding:
                continue
                
            cursor.execute(sql_insert, (section_title, source, chunk_text, embedding))
            
        connection.commit()
        print("¡Todos los chunks con vectores fueron guardados con éxito en RDS!")
        
    except Exception as e:
        print(f" Error al insertar los datos en RDS: {e}")
        if connection:
            connection.rollback()
            
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Conexión a RDS cerrada correctamente.")