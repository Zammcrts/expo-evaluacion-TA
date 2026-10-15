"""Sube evaluadores, proyectos y calificaciones a la API.

Uso:  pip install requests
      python load_data.py
Si tus endpoints piden login, llena USUARIO y PASSWORD.
"""
import json
import requests

BASE = "http://127.0.0.1:8000/api"
USUARIO, PASSWORD = "zam", "santiago11"  # ej. "admin", "tu_password"
auth = (USUARIO, PASSWORD) if USUARIO else None


def cargar(nombre):
    with open(f"{nombre}.json", encoding="utf-8") as f:
        return json.load(f)


def post(recurso, body):
    r = requests.post(f"{BASE}/{recurso}/", json=body, auth=auth)
    if r.status_code != 201:
        raise SystemExit(f"Error {r.status_code} en {recurso}: {r.text}\nBody: {body}")
    return r.json()["id"]


ids_eval = [post("evaluadores", e) for e in cargar("evaluadores")]
print("Evaluadores creados:", len(ids_eval))

ids_proy = [post("proyectos", p) for p in cargar("proyectos")]
print("Proyectos creados:", len(ids_proy))

n = 0
for c in cargar("calificaciones"):
    post("calificaciones", {
        "proyecto": ids_proy[c["proyecto"] - 1],
        "evaluador": ids_eval[c["evaluador"] - 1],
        "puntaje": c["puntaje"],
        "comentario": c["comentario"],
    })
    n += 1
print("Calificaciones creadas:", n)
