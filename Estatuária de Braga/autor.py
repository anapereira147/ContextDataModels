from typing import List, Optional, Union
from pydantic import Field, HttpUrl, validator
from pydantic_schemaorg.Person import Person
import pandas as pd
import json
import numpy as np
import re

class Autor(Person):
    id_autor:  int = Field(None, alias="identifier")
    type: str = Field(default="Person", alias="@type", const=True)
    nome: str = Field(..., alias="name")    
    data_nascimento: Optional[str] = Field(default=None, alias="birthDate")
    data_falecimento: Optional[str] = Field(default=None, alias="deathDate")
    biografia: Optional[str] = Field(default=None, alias="description")
    reconhecimento: Optional[List[str]] = Field(default=None, alias="award")
    url: Optional[List[Union[HttpUrl]]] = Field(default=None, alias="url")
    obras_notaveis: Optional[List[str]] = Field(default=None, alias="knownFor")
    estatuaria_id: List[str] = Field(default=None, alias="publishingPrinciples")
    afiliacao: Optional[List[str]] = Field(default=None, alias="jobTitle")

    @validator("data_nascimento", "data_falecimento")
    def validar_data(cls, v):
        if v is None or str(v).strip() == "":
            return None

        data = str(v).strip()

        # formato YYYY-MM-DD
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
            return data

        # formato YYYY
        if re.fullmatch(r"\d{4}", data):
            return data

        raise ValueError(f"Data inválida: '{data}'. Usar 'YYYY' ou 'YYYY-MM-DD'.")

# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,]", str(val))
    return [x.strip() for x in parts if x.strip()]


# Ler o CSV
df = pd.read_csv("Schemas - versao 2/Estatuária de Braga/csv/Autores.csv", dtype=str).replace({np.nan: None})

campos_lista = ["reconhecimento", "obras_notaveis", "estatuaria_id", "afiliacao", "url"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

autores = [Autor(**row.to_dict()) for _, row in df.iterrows()]


# Converter para NGSI-LD
def to_ngsi_ld_strict(entity: Autor) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Person:{data['identifier']}",
        "type": "Person"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "publishingPrinciples":
            if isinstance(value, list):
                ngsi[key] = {
                    "type": "Relationship",
                    "object": [f"urn:ngsi-ld:Sculpture:{v}" for v in value if v],
                    "objectType": "Sculpture"
                }
            else:
                ngsi[key] = {
                    "type": "Relationship",
                    "object": f"urn:ngsi-ld:Sculpture:{value}",
                    "objectType": "Sculpture"
                }
        else:
            ngsi[key] = {
                "type": "Property",
                "value": value if not isinstance(value, list) else [v for v in value if v]
            }
    ngsi["@context"] = [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextEstatuarias.jsonld"
    ]
    return ngsi


# Exportar
autores_ngsi = [to_ngsi_ld_strict(autor) for autor in autores]

with open("autores_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(autores_ngsi, f, indent=2, ensure_ascii=False)