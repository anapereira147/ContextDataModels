from typing import List, Optional, Union
from pydantic import Field, HttpUrl, validator
from pydantic_schemaorg.Event import Event
import pandas as pd
import json
import numpy as np
import re
from datetime import date

class EventModel(Event):
    id_evento: int = Field(None, alias="identifier")

    # Campos schema.org
    nome: str = Field(..., alias="name")
    tipo: Optional[str] = Field(None, alias="eventType")
    data_inicio: Union[str, date] = Field(None, alias="startDate")
    data_fim: Optional[Union[str, date]] = Field(None, alias="endDate")
    horario: Optional[str] = Field(None, alias="startTime")
    descricao: Optional[str] = Field(None, alias="description")
    bilhetes: Optional[str] = Field(None, alias="price")
    duracao: Optional[str] = Field(None, alias="duration")
    publico_alvo: Optional[str]  = Field(None, alias="typicalAgeRange")
    num_max_participantes: Optional[str] = Field(None, alias="maximumAttendeeCapacity")
    imagem: Optional[List[Union[HttpUrl, str]]] = Field(default=None, alias="image")
    id_festival: str = Field(alias="superEvent")
    id_participante: Optional[str] = Field(None, alias="attendee")
    id_local: Optional[str] = Field(None, alias="location")
    num_min_participantes: Optional[str] = Field(None, alias="minimumAttendeeCapacity")
    outras_informacoes: Optional[str] = Field(None, alias="comment")

    @validator("data_inicio", "data_fim")
    def validar_data(cls, v):
        if v is None or str(v).strip() == "":
            return None

        data = str(v).strip()

        # formato YYYY-MM-DD
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
            return data

        raise ValueError(f"Data inválida: '{data}'. Usar 'YYYY-MM-DD'.")

# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,]", str(val))
    return [x.strip() for x in parts if x.strip()]

# Ler CSV e preparar o DataFrame
df = pd.read_csv("Schemas - versao 2/Braga é Natal/csv/Evento.csv", dtype=str).replace({np.nan: None})

campos_lista = ["imagem"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

eventos = [EventModel(**row.to_dict()) for _, row in df.iterrows()]

# Converter para NGSI-LD
def to_ngsi_ld_strict(entity: EventModel) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Event:{data['identifier']}",
        "type": "Event"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "superEvent":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Festival:{value}",
                "objectType": "Festival"
            }
        elif key == "attendee":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Attendee:{value}",
                "objectType": "Organization"
            }
        elif key == "location":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Place:{value}",
                "objectType": "Place"
            }
        else:
            ngsi[key] = {
                "type": "Property",
                "value": value if not isinstance(value, list) else [v for v in value if v]
            }
    ngsi["@context"] = [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextBragaNatal.jsonld"
    ]
    return ngsi

# Exportar
evento_ngsi = [to_ngsi_ld_strict(evento) for evento in eventos]
with open("evento_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(evento_ngsi, f, indent=2, ensure_ascii=False)




