import os
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse

app = FastAPI()

FILE_DIRECTORY = "./files"

if not os.path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY)

# --- ENDPOINTS ---

@app.get("/files", response_model=List[str], summary="Lista de Archivos")
async def list_files():
    """
    Devuelve una lista de los nombres de todos los archivos
    disponibles en el directorio de trabajo ('./files').
    """
    try:
        # Filtra solo los archivos, ignorando directorios dentro de './files'
        all_files = [f for f in os.listdir(FILE_DIRECTORY) if os.path.isfile(os.path.join(FILE_DIRECTORY, f))]
        return all_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar archivos: {e}")

@app.post("/files", status_code=201, summary="Crear Archivo")
async def create_file(request: Request):
    """
    Crea un nuevo archivo en el directorio './files' con el nombre
    y contenido proporcionado en el cuerpo de la solicitud JSON.

    Cuerpo esperado (JSON):
    {
        "file_name": "nombre_del_archivo.txt",
        "content": "Contenido del archivo..."
    }
    """
    try:
        # Obtener el cuerpo de la solicitud JSON
        data = await request.json()
        file_name = data.get("file_name")
        content = data.get("content", "")

        if not file_name:
            raise HTTPException(status_code=400, detail="El campo 'file_name' es obligatorio.")

        # Construir la ruta completa del archivo
        file_path = os.path.join(FILE_DIRECTORY, file_name)

        # Verificar si el archivo ya existe (opcional, pero buena práctica)
        if os.path.exists(file_path):
             # 409 Conflict si ya existe
            raise HTTPException(status_code=409, detail=f"El archivo '{file_name}' ya existe.")

        # Escribir el contenido en el archivo
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return JSONResponse(content={"message": f"Archivo '{file_name}' creado exitosamente."}, status_code=201)

    except HTTPException as e:
        raise e
    except Exception as e:
        # Captura errores de lectura/escritura o JSON inválido
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {e}")

@app.get("/files/{file_name}", summary="Obtener Contenido de Archivo")
async def get_file_content(file_name: str):
    """
    Devuelve el contenido de un archivo específico
    del directorio './files'.
    """
    file_path = os.path.join(FILE_DIRECTORY, file_name)

    # 1. Verificar que el archivo exista
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Archivo '{file_name}' no encontrado.")

    try:
        # 2. Leer y devolver el contenido como texto plano
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return PlainTextResponse(content=content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {e}")