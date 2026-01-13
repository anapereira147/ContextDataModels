from typing import Optional, List
from pydantic_schemaorg.Place import Place
from pydantic_schemaorg.GeoCoordinates import GeoCoordinates
from pydantic import Field
import pandas as pd
import json
import numpy as np
import re

class Local(Place):
    id_local: str = Field(default=None, alias="identifier")
    local: str = Field(alias="address")
    geolocalizacao: Optional[GeoCoordinates] = Field(alias="geo")
    id_evento: List[str] = Field(default=None, alias="event")
    palco: Optional[str] = Field(alias="containsPlace")

# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,]", str(val))
    return [x.strip() for x in parts if x.strip()]

# Ler CSV e preparar o DataFrame
df = pd.read_csv("Schemas - versao 2/Braga é Natal/csv/Local.csv", dtype=str).replace({np.nan: None})

campos_lista = ["id_evento"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

locais = [Local(**row.to_dict()) for _, row in df.iterrows()]

# Converter para NGSI-LD
def to_ngsi_ld_strict(entity: Local) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Place:{data['identifier']}",
        "type": "Place"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "event":
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
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextBragaNatal.jsonld",
    ]
    return ngsi

# Exportar
local_ngsi = [to_ngsi_ld_strict(local) for local in locais]
with open("local_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(local_ngsi, f, indent=2, ensure_ascii=False)