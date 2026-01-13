from pydantic import Field
from typing import List, Optional
from pydantic_schemaorg.Place import Place
import pandas as pd
import json
import re

class Edificio(Place):

    id_edificio: str = Field(..., alias="identifier")      

    # Campos schema.org
    nome: str = Field(..., alias="name")  
    local: str = Field(None, alias="address")  
    area_total_m2: Optional[float] = Field(None, alias="floorSize")
    ano_construcao: Optional[int] = Field(None, alias="yearBuilt")
    numero_pisos: int = Field(None, alias="floorCount")
    id_sala: List[str] = Field(..., alias="containsPlace")    


# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,;]", str(val))
    return [x.strip() for x in parts if x.strip()]

# Criar umexemplo
data = [
    {
        "id_edificio": "11",
        "nome": "Escola de Engenharia da Universidade do Minho (EEUM)",
        "local": "Universidade do Minho, Campus de Azurém, 4804-533 Guimarães",
        "area_total_m2": 9249,
        "ano_construcao": 1975,
        "numero_pisos": 3,
        "id_sala": "LAP1,LAP2,LAP3,LAP4,LAP5,LID1,LID2,LID3,LID4"
    }
]
df = pd.DataFrame(data)

campos_lista = ["id_sala"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

edificios = [Edificio(**row.to_dict()) for _, row in df.iterrows()]

# Conversão para NGSI-LD
def to_ngsi_ld(entity: Edificio) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Building:{data['identifier']}",
        "type": "Building"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
       
        if key == "containsPlace":
            if isinstance(value, list):
                ngsi[key] = {
                    "type": "Relationship",
                    "object": [f"urn:ngsi-ld:Room:{v}" for v in value if v],
                    "objectType": "Room"
                }
            else:
                ngsi[key] = {
                    "type": "Relationship",
                    "object": f"urn:ngsi-ld:Room:{value}",
                    "objectType": "Room"
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

edificios_ngsi = [to_ngsi_ld(edificio) for edificio in edificios]

# Exportar
with open("edificios_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(edificios_ngsi, f, indent=2, ensure_ascii=False)
