from pydantic import Field
from typing import Optional
from pydantic_schemaorg.Person import Person
import pandas as pd
import json


class Pessoa(Person):
    id_pessoa: str = Field(..., alias="identifier")
    nome: str = Field(..., alias="name")  
    email: Optional[str] = Field(None, alias="email") 
    telemovel: Optional[str] = Field(None, alias="telephone") 

data = [
    {
        "id_pessoa": "PG53629",
        "nome": "Ana Pereira",
    }
]
df = pd.DataFrame(data)
pessoas = [Pessoa(**row.to_dict()) for _, row in df.iterrows()]

# Conversão para NGSI-LD
def to_ngsi_ld(entity: Pessoa) -> dict:
    data = entity.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {
        "id": f"urn:ngsi-ld:Person:{data['identifier']}",
        "type": "Person"
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
        "https://raw.githubusercontent.com/anapereira147/ContextDataModels/main/ContextDSI.jsonld"
    ]
    return ngsi

pessoas_ngsi = [to_ngsi_ld(pessoa) for pessoa in pessoas]

# Exportar
with open("pessoas_ngsi.jsonld", "w", encoding="utf-8") as f:
    json.dump(pessoas_ngsi, f, indent=2, ensure_ascii=False)


