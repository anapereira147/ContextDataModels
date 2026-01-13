from typing import Optional, Union, List
from pydantic import Field, HttpUrl, validator
from pydantic_schemaorg.Sculpture import Sculpture
import pandas as pd
import json
import numpy as np
import re
from datetime import date

class Estatuaria(Sculpture):
    num_inventario:  int = Field(None, alias="identifier")
    type: str = Field(default="Sculpture", alias="@type", const=True)
    designacao: Optional[str] = Field(default=None, alias="name")
    propriedade: Optional[str] = Field(default=None, alias="P51_has_former_or_corrent_owner")
    tipologia: str = Field(default=None, alias="additionalType")
    material: Optional[str] = Field(default=None, alias="material")
    data_construcao: Optional[List[str]] = Field(default=None, alias="dateCreated")
    descricao: Optional[str] = Field(default=None, alias="description")
    endereco: Optional[str] = Field(default=None, alias="address")
    x: Optional[float] = Field(default=None, alias="latitude")
    y: Optional[float] = Field(default=None, alias="longitude")
    referencia_documental:  Optional[List[Union[HttpUrl]]] = Field(default=None, alias="usageInfo")
    seletor_imagem: Optional[List[Union[HttpUrl, str]]] = Field(default=None, alias="image")
    data_inventario: str = Field(default=None, alias="hasAccumulationDate")
    estado_conservacao: Optional[str] = Field(default=None, alias="P44_has_condition")
    id_autor: Optional[List[str]] = Field(default=None, alias="author")

    @validator("data_inventario")
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
        
        # formato YYYY | YYYY
        if re.fullmatch(r"\d{4}|\d{4}", data):
            return data

        raise ValueError(f"Data inválida: '{data}'. Usar 'YYYY' ou 'YYYY-MM-DD'.")
    
    @validator("data_construcao")
    def validar_data_construcao(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("Data inválida: '{data}'. Usar 'YYYY' ou 'YYYY-MM-DD'.")
        return [cls.validar_data(item) for item in v]

# Converte strings com valores separados por |,; em listas
def parse_lista_ou_none(val):
    if pd.isna(val) or not str(val).strip():
        return None
    parts = re.split(r"[|,;]", str(val))
    return [x.strip() for x in parts if x.strip()]

# Ler o CSV
df = pd.read_csv("Schemas - versao 2/Estatuária de Braga/csv/Estatuaria.csv", dtype=str).replace({np.nan: None})

campos_lista = ["seletor_imagem", "referencia_documental", "id_autor", "data_construcao"]
for campo in campos_lista:
    df[campo] = df[campo].apply(parse_lista_ou_none)

estatuarias = [Estatuaria(**row.to_dict()) for _, row in df.iterrows()]

# Conversão para NGSI-LD
def to_ngsi_ld(entity: Estatuaria) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Sculpture:{data['identifier']}",
        "type": "Sculpture"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "author":
            if isinstance(value, list):
                ngsi[key] = {
                    "type": "Relationship",
                    "object": [f"urn:ngsi-ld:Person:{v}" for v in value if v],
                    "objectType": "Person"
                }
            else:
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
    if "latitude" in data and "longitude" in data:
        try:
            lat = float(data["latitude"])
            lon = float(data["longitude"])
            ngsi["location"] = {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        except ValueError:
            pass
    ngsi["@context"] = [
        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextEstatuarias.jsonld"
    ]
    return ngsi

estatuarias_ngsi = [to_ngsi_ld(estatua) for estatua in estatuarias]

# Exportar
with open("estatuarias_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(estatuarias_ngsi, f, indent=2, ensure_ascii=False)

