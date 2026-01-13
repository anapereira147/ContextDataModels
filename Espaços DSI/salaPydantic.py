from pydantic import Field
from typing import Optional
from pydantic_schemaorg.Room import Room
import pandas as pd
import json

class Sala(Room):

    id_sala: str = Field(..., alias="identifier")    

    # Campos schema.org
    nome: str = Field(..., alias="name")
    andar: int = Field(None, alias="floorLevel")
    area_total_m2: Optional[float] = Field(None, alias="floorSize") 
    capacidade: Optional[int] = Field(None, alias="occupancy") 
    tipo_sala: Optional[str] = Field(None, alias="amenityFeature")

    # Campos personalizados
    acessibilidade: Optional[bool] = Field(None, alias="isHandicappedAcessible")
    num_projetor: Optional[int] = Field(None, alias="numberOfProjectors")
    num_tela_projecao: Optional[int] = Field(None, alias="numberOfProjectionScreens")
    num_quadro_branco: Optional[int] = Field(None, alias="numberOfWhiteboards")
    num_mesa_individual: Optional[int] = Field(None, alias="numberOfSingleDesks")
    num_mesa_dupla: Optional[int] = Field(None, alias="numberOfDoubleDesks")
    num_cadeiras: Optional[int] = Field(None, alias="numberOfChairs")
    num_ecra_interativo: Optional[int] = Field(None, alias="numberOfInteractiveScreens")
    num_computadores: Optional[int] = Field(None, alias="numberOfComputers")
    id_edificio: str = Field(None, alias="containedInPlace")


# Criar um exemplo
data = [
    {
        "id_sala": "141",
        "nome": "LAP1 - Laboratórios pedagógico 1",
        "andar": 1,
        "area_total_m2": 87.44,
        "capacidade": 46,
        "tipo_sala": "Laboratório pedagógico",
        "acessibilidade": True,
        "num_projetor": 1,
        "num_tela_projecao": 1,
        "num_computadores": 16,
        "id_edificio": "11"
    }
]
df = pd.DataFrame(data)

salas = [Sala(**row.to_dict()) for _, row in df.iterrows()]

# Conversão para NGSI-LD
def to_ngsi_ld(entity: Sala) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Room:{data['identifier']}",
        "type": "Room"
    }
    for key, value in data.items():
        if key in ("identifier", "@type"):
            continue
        if key == "containedInPlace":
            ngsi[key] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Building:{value}",
                "objectType": "Building"
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

salas_ngsi = [to_ngsi_ld(sala) for sala in salas]

# Exportar
with open("salas_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(salas_ngsi, f, indent=2, ensure_ascii=False)
