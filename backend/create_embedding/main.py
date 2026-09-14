from utils import (
    extraer_texto_de_pdf_s3,
    dividir_pdf_duolingo_por_secciones,
    generar_embeddings_chunks_aws,
    insertar_chunks_con_vectores_en_rds
)

def main():
    BUCKET_NAME = "duolingo-thrive-234"
    FILE_KEY = "example.pdf"

    print("--- INICIANDO PIPELINE RAG (S3 -> Bedrock -> RDS) ---")

    texto_pdf = extraer_texto_de_pdf_s3(bucket_name=BUCKET_NAME, file_key=FILE_KEY)
    
    if not texto_pdf:
        print("❌ Proceso detenido: No se pudo extraer texto del PDF.")
        return

    chunks_optimizados = dividir_pdf_duolingo_por_secciones(texto_pdf)

    chunks_con_vectores = generar_embeddings_chunks_aws(chunks_optimizados, region_name="us-east-1")

    insertar_chunks_con_vectores_en_rds(chunks_con_vectores)

    print("--- PIPELINE FINALIZADO ---")

if __name__ == "__main__":
    main()