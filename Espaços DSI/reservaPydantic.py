from pydantic import Field, validator
from pydantic_schemaorg.Reservation import Reservation
from typing import Optional
from datetime import date
import re
import pandas as pd
import json

class ReservaSala(Reservation):

    id_reserva: str = Field(..., alias="identifier")

    data_inicio: date = Field(..., alias="startDate")
    data_fim: date = Field(..., alias="endDate")
    hora_inicio: str = Field(None, alias="startTime")
    hora_fim: str = Field(None, alias="endTime")
    finalidade: Optional[str] = Field(None, alias="description")
    id_pessoa: str = Field(default=None, alias="underName")
    id_sala: str = Field(..., alias="reservationFor")   

    @validator("data_inicio", "data_fim")
    def validar_data(cls, v):
        if v is None or str(v).strip() == "":
            return None

        data = str(v).strip()

        # formato YYYY-MM-DD
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
            return data

        raise ValueError(f"Data inválida: '{data}'. Usar 'YYYY-MM-DD'.") 
    
    @validator("hora_inicio", "hora_fim")
    def validar_hora(cls, v):
        if v is None or str(v).strip() == "":
            return None

        hora = str(v).strip()

        # formato YYYY-MM-DD
        if re.fullmatch(r"\d{2}:\d{2}:\d{2}", hora):
            return hora

        raise ValueError(f"Hora inválida: '{hora}'. Usar 'HH:MM:SS'.") 
    
    
    class Config:
        allow_population_by_field_name = True

# Criar um exemplo
data = [
    {
        "id_reserva": "1",
        "data_inicio": date(2025, 6, 1),
        "data_fim": date(2025, 6, 1),
        "hora_inicio": "09:00:00",
        "hora_fim": "11:00:00",
        "finalidade": "Reunião de Dissertação",
        "id_pessoa": "1",
        "id_sala": "141"
    }
]
df = pd.DataFrame(data)

reservaSalas = [ReservaSala(**row.to_dict()) for _, row in df.iterrows()]

# Conversão para NGSI-LD
def to_ngsi_ld(entity: ReservaSala) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Reservation:{data['identifier']}",
        "type": "Reservation"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "reservationFor":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Room:{value}",
                "objectType": "Room"
            }
        elif key == "underName":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Person:{value}",
                "objectType": "Person"
            }
        else:
            ngsi[key] = {
                "type": "Property",
                "value": value if not isinstance(value, list) else [v for v in value if v]
            }
    ngsi["@context"] = [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextDSI.jsonld"
    ]
    return ngsi

reservaSalas_ngsi = [to_ngsi_ld(reservaSala) for reservaSala in reservaSalas]

# Exportar
with open("reservaSalas_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(reservaSalas_ngsi, f, indent=2, ensure_ascii=False)
