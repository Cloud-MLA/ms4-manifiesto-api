"""Datos precargados que sirven los 3 mocks — coherentes entre sí.

Basados en el vuelo id=6058 del seed (SEED=20260905), aunque los mocks aceptan
cualquier vuelo_id que este entre 1 y 25000 y devuelven la misma respuesta
sustituyendo el id — suficiente para dev y tests, no para carga real.
"""


def vuelo(vuelo_id: int) -> dict:
    return {
        "id": vuelo_id,
        "num_vuelo": "LA0032",
        "hora_programada": "2026-08-17T21:55:00Z",
        "hora_real": "2026-08-17T22:11:00Z",
        "estado": "Aterrizado",
        "tipo": "Internacional",
        "origen": "LIM",
        "destino": "SCL",
        "aeronave": {
            "placa": "OB-1111",
            "modelo": "Boeing 787-9",
            "fabricante": "Boeing",
            "capacidad": 296,
            "clase": "E",
        },
        "aerolinea": {
            "ruc": "20100000018",
            "nombre": "GOL",
            "alianza": "Ninguna",
        },
    }


def tickets(vuelo_id: int) -> list[dict]:
    return [
        {
            "id_ticket": 1,
            "id_persona": 134482,
            "precio": "563.04",
            "estado_boarding": "Embarcado",
            "pasajero": {
                "id_persona": 134482,
                "nombre": "Liliana",
                "apellido": "Vilalta",
                "tipo_documento": "DNI",
                "numero_documento": "81766597",
                "categoria_migratoria": {"id": 2, "nombre": "Internacional", "tarifa": 38.45},
            },
            "checkin": {
                "id_ticket": 1,
                "fecha_hora": "2026-08-17T18:45:00Z",
                "counter": "C02",
                "con_equipaje": True,
            },
            "equipaje": [
                {"id": "BHS0000000001", "peso": "17.65"},
            ],
        },
        {
            "id_ticket": 2,
            "id_persona": 158084,
            "precio": "412.30",
            "estado_boarding": "Embarcado",
            "pasajero": {
                "id_persona": 158084,
                "nombre": "Diana",
                "apellido": "León",
                "tipo_documento": "Pasaporte",
                "numero_documento": "AB1234567",
                "categoria_migratoria": {"id": 2, "nombre": "Internacional", "tarifa": 38.45},
            },
            "checkin": None,
            "equipaje": [
                {"id": "BHS0000000002", "peso": "12.10"},
                {"id": "BHS0000000003", "peso": "8.50"},
            ],
        },
    ]


def tripulacion(vuelo_id: int) -> list[dict]:
    return [
        {"id_empleado": 1542, "nombre": "Carlos",  "apellido": "Ruiz",   "num_licencia": "DGAC-001542"},
        {"id_empleado": 2658, "nombre": "Maria",   "apellido": "Torres", "num_licencia": "DGAC-002658"},
        {"id_empleado":  911, "nombre": "Andres",  "apellido": "Vega",   "num_licencia": "DGAC-000911"},
    ]


def incidencias_abiertas(vuelo_id: int) -> list[dict]:
    return [
        {
            "id": 1,
            "gravedad": "Alta",
            "tipo_incidencia": "Falta_Combustible",
            "descripcion": "Reserva de Jet A-1 por debajo del minimo operacional",
            "fecha_reporte": "2026-09-03T20:44:42Z",
            "fecha_cierre": None,
            "recursos_afectados": [{"recurso_id": 429}],
        },
    ]


def asignaciones(vuelo_id: int) -> list[dict]:
    return [
        {"id_vuelo": vuelo_id, "id_recurso": 42, "tipo": "manga",
         "nombre_tecnico_locacion": "Espigon A - Puente A07"},
    ]
