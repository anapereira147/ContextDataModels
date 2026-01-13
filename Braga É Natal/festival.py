from pydantic import Field, HttpUrl, validator
from typing import List, Optional, Union
from pydantic_schemaorg.Festival import Festival
import pandas as pd
import json
import numpy as np
import re

class FestivalModel(Festival):
    id_festival: int = Field(None, alias="identifier")
    nome: str = Field(..., alias="name")
    descricao: Optional[str] = Field(None, alias="description")
    organizado_por: Optional[str] = Field(None, alias="organizer")
    data_inicio: str = Field(..., alias="startDate")
    data_fim: str = Field(..., alias="endDate")
    parceiro: Optional[List[str]]= Field(None, alias="contributor")
    site_web: Optional[HttpUrl] = Field(default=None, alias="url")
    imagem: Optional[List[Union[HttpUrl, str]]] = Field(default=None, alias="image")

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
df = pd.read_csv("Schemas - versao 2/Braga é Natal/csv/Festival.csv", dtype=str).replace({np.nan: None})

campos_lista = ["parceiro", "imagem"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

festivais = [FestivalModel(**row.to_dict()) for _, row in df.iterrows()]

# Converter para NGSI-LD
def to_ngsi_ld_strict(entity: FestivalModel) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Festival:{data['identifier']}",
        "type": "Festival"
    }

    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
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
festival_ngsi = [to_ngsi_ld_strict(festival) for festival in festivais]

with open("festival_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(festival_ngsi, f, indent=2, ensure_ascii=False)
