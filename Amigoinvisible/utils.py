import json
import os
from pathlib import Path

import streamlit as st


def _admin_password():
    password = os.environ.get("AMIGO_ADMIN_PASSWORD")
    if password:
        return password
    try:
        return st.secrets.get("admin_password", "admin123")
    except Exception:
        return "admin123"


ADMIN_PASSWORD = _admin_password()
DATA_FILE = Path(__file__).resolve().with_name("data.json")


def cargar_datos():
    """Load the saved draw, keeping compatibility with the original JSON format."""
    if not DATA_FILE.exists():
        return {"nombres": [], "emparejamientos": {}, "base_url": ""}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        if not isinstance(datos, dict) or not isinstance(datos.get("emparejamientos", {}), dict):
            st.error("El archivo data.json tiene un formato no válido.")
            return {"nombres": [], "emparejamientos": {}, "base_url": ""}
        return {
            "nombres": datos.get("nombres", []),
            "emparejamientos": datos.get("emparejamientos", {}),
            "base_url": datos.get("base_url", ""),
        }
    except (json.JSONDecodeError, OSError) as error:
        st.error(f"No se pudo leer data.json: {error}")
        return {"nombres": [], "emparejamientos": {}, "base_url": ""}


def guardar_datos(nombres, emparejamientos_numerados, base_url=""):
    """Save the draw without changing the original participant assignments format."""
    datos = {
        "nombres": nombres,
        "emparejamientos": emparejamientos_numerados,
        "base_url": base_url,
    }
    with DATA_FILE.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
