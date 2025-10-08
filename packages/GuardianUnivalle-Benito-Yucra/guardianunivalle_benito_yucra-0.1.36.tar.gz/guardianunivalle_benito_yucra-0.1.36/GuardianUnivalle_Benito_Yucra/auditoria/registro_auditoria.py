import datetime
import json
import os

# Archivo donde se guardarán los eventos
LOG_FILE = "auditoria_guardian.log"


def registrar_evento(
    tipo: str,
    descripcion: str = "",
    severidad: str = "MEDIA",
    extra: dict | None = None,
):
    """
    Registra un evento de auditoría en un archivo.
    :param tipo: Tipo de evento (DoS, CSRF, XSS, SQLi, etc.)
    :param descripcion: Descripción detallada del evento
    :param severidad: Nivel de severidad (BAJA, MEDIA, ALTA)
    :param extra: Datos adicionales opcionales
    """
    try:
        evento = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "descripcion": descripcion,
            "severidad": severidad,
            "extra": extra or {},
        }

        # Asegurar que el archivo exista
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"[Auditoría] Error al registrar evento: {e}")


def generar_reporte() -> str:
    """Devuelve todo el contenido del archivo de auditoría."""
    if not os.path.exists(LOG_FILE):
        return "No hay registros aún."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()
