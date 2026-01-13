from typing import Optional, List, Union
from pydantic_schemaorg.Organization import Organization
from pydantic import Field, HttpUrl
import pandas as pd
import json
import numpy as np
import re

class Participante(Organization):
    id_participante: str = Field(alias="identifier")
    participacao: str = Field(alias="name")
    descricao: Optional[str] = Field(alias="description")
    site_web: Optional[Union[HttpUrl, str]] = Field(default=None, alias="url")
    id_evento: Optional[List[str]] = Field(default=None, alias="performerIn")

# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,]", str(val))
    return [x.strip() for x in parts if x.strip()]

# Ler CSV e preparar o DataFrame
df = pd.read_csv("Schemas - versao 2/Braga é Natal/csv/Participante.csv", dtype=str).replace({np.nan: None})

campos_lista = ["id_evento"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

participantes = [Participante(**row.to_dict()) for _, row in df.iterrows()]

# Converter para NGSI-LD
def to_ngsi_ld_strict(entity: Participante) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Attendee:{data['identifier']}",
        "type": "Attendee"
    }

    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue

        if key == "performerIn":
            if isinstance(value, list):
                ngsi[key] = {
                    "type": "Relationship",
                    "object": [f"urn:ngsi-ld:Event:{v}" for v in value if v],
                    "objectType": "Event"
                }
            else:
                ngsi[key] = {
                    "type": "Relationship",
                    "object": f"urn:ngsi-ld:Event:{value}",
                    "objectType": "Event"
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
participante_ngsi = [to_ngsi_ld_strict(participante) for participante in participantes]

with open("participante_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(participante_ngsi, f, indent=2, ensure_ascii=False)

