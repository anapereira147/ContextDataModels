from pydantic import BaseModel, Field, AnyUrl
from typing import Optional
import pandas as pd, numpy as np, json

# GtfsAgency
class GtfsAgency(BaseModel):
    agency_id: str
    type: str = Field("GtfsAgency", const=True)
    agency_name: str = Field(..., alias="agencyName")
    agency_url: AnyUrl = Field(..., alias="page")
    agency_timezone: Optional[str] = Field(..., alias="timezone")
    agency_phone: Optional[str] = Field(..., alias="phone")
    agency_lang: Optional[str] = Field(..., alias="language")
    agency_fare_url: Optional[AnyUrl] = Field(..., alias="farePage")
    
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/agency.txt", dtype=str).replace({np.nan: None})
agencies = [GtfsAgency.parse_obj(row.to_dict()) for _, row in df.iterrows()]

def agency_to_ngsi_ld(agency: GtfsAgency) -> dict:
    data = agency.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsAgency:{data['agency_id']}",
            "type": "GtfsAgency"}
    for key, value in data.items():
        if key in ("agency_id","@type"):
            continue
        else:
            ngsi[key] = {
                "type": "Property",
                "value": value if not isinstance(value, list) else [v for v in value if v]
            }
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

gtfsAgency_ngsi = [agency_to_ngsi_ld(a) for a in agencies]





# GtfsStop
class GtfsStop(BaseModel):
    stop_id: str
    type: str = Field("GtfsStop", const=True)
    stop_name: str = Field(..., alias="name")
    stop_lat: float
    stop_lon: float
    zone_id: Optional[str] = Field(..., alias="zoneCode")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/stops.txt", dtype=str).replace({np.nan: None})
df["stop_lat"] = df["stop_lat"].astype(float)
df["stop_lon"] = df["stop_lon"].astype(float)
stops = [GtfsStop(**row.to_dict()) for _, row in df.iterrows()]

def stop_to_ngsi_ld(stop: GtfsStop) -> dict:
    data = stop.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsStop:{data['stop_id']}", 
            "type": "GtfsStop"}
    ngsi["name"] = {"type": "Property", "value": data["name"]}
    if data.get("zoneCode"):
        ngsi["zoneCode"] = {"type": "Property", "value": data["zoneCode"]}
    ngsi["location"] = {
        "type": "GeoProperty",
        "value": {"type": "Point", "coordinates": [data["stop_lon"], data["stop_lat"]]}
    }
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

stops_ngsi = [stop_to_ngsi_ld(s) for s in stops]





# GtfsRoute
class GtfsRoute(BaseModel):
    route_id: str
    type: str = Field("GtfsRoute", const=True)
    agency_id: str  = Field(..., alias="operatedBy")
    route_short_name: Optional[str] = Field(..., alias="shortName")
    route_long_name: Optional[str] = Field(..., alias="LongName")
    route_type: int = Field(..., alias="routeType")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/routes.txt", dtype=str).replace({np.nan: None})
routes = [GtfsRoute(**row.to_dict()) for _, row in df.iterrows()]

def route_to_ngsi_ld(route: GtfsRoute) -> dict:
    data = route.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsRoute:{data['route_id']}", "type": "GtfsRoute"}
    for k, v in data.items():
        if k in ("route_id","type"): continue
        if k == "operatedBy":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:{v}"
            }
        else:
            ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

routes_ngsi = [route_to_ngsi_ld(r) for r in routes]




#tem ja
# GtfsTrip
class GtfsTrip(BaseModel):
    trip_id: str
    type: str = Field("GtfsTrip", const=True)
    route_id: str = Field(..., alias="hasRoute")
    service_id: str = Field(..., alias="hasService")
    trip_headsign: Optional[str] = Field(..., alias="headSign")
    direction_id: Optional[int] = Field(..., alias="direction")
    shape_id: Optional[str] = Field(..., alias="hasShape")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/trips.txt", dtype=str).replace({np.nan: None})
trips = [GtfsTrip(**row.to_dict()) for _, row in df.iterrows()]

def trip_to_ngsi_ld(trip: GtfsTrip) -> dict:
    data = trip.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsTrip:{data['trip_id']}", "type": "GtfsTrip"}
    for k, v in data.items():
        if k in ("trip_id","type"): continue
        if k == "hasRoute":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{v}"
            }
        elif k == "hasService":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsCalendarRule:{v}"
            }
        elif k == "hasShape":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsShape:{v}"
            }
        else:
            ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

trips_ngsi = [trip_to_ngsi_ld(t) for t in trips]





# GtfsStopTime
class GtfsStopTime(BaseModel):
    type: str = Field("GtfsStopTime", const=True)
    trip_id: str = Field(..., alias="hasTrip")
    arrival_time: str = Field(..., alias="arrivalTime")
    departure_time: str = Field(..., alias="departureTime")
    stop_id: str = Field(..., alias="hasStop")
    stop_sequence: int = Field(..., alias="stopSequence")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/stop_times.txt", dtype=str).replace({np.nan: None})
df["stop_sequence"] = df["stop_sequence"].astype(int)
stop_times = [GtfsStopTime(**row.to_dict()) for _, row in df.iterrows()]

def stoptime_to_ngsi_ld(st: GtfsStopTime) -> dict:
    data = st.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsStopTime:{data['hasTrip']}_{data['stopSequence']}",
            "type": "GtfsStopTime"}
    for k, v in data.items():
        if k in ("type",): continue
        if k == "hasTrip":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsTrip:{v}"
            }
        elif k == "hasStop":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsStop:{v}"
            }
        else:
            ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

stop_times_ngsi = [stoptime_to_ngsi_ld(st) for st in stop_times]





# GtfsCalendarRule
class GtfsCalendarRule(BaseModel):
    service_id: str 
    type: str = Field("GtfsCalendarRule", const=True)
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    start_date: str = Field(..., alias="startDate")
    end_date: str = Field(..., alias="endDate")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/calendar.txt", dtype=str).replace({np.nan: None})
calendars = [GtfsCalendarRule(**row.to_dict()) for _, row in df.iterrows()]

def calendar_to_ngsi_ld(c: GtfsCalendarRule) -> dict:
    data = c.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsCalendarRule:{data['service_id']}", "type": "GtfsCalendarRule"}
    for k, v in data.items():
        if k in ("service_id","type"): continue
        ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

calendars_ngsi = [calendar_to_ngsi_ld(c) for c in calendars]





# GtfsCalendarDateRule
class GtfsCalendarDateRule(BaseModel):
    type: str = Field("GtfsCalendarDateRule", const=True)
    service_id: str = Field(..., alias="hasService")
    date: str = Field(..., alias="appliesOn")
    exception_type: int = Field(..., alias="exceptionType")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/calendar_dates.txt", dtype=str).replace({np.nan: None})
df["exception_type"] = df["exception_type"].astype(int)
cal_dates = [GtfsCalendarDateRule(**row.to_dict()) for _, row in df.iterrows()]

def caldate_to_ngsi_ld(cd: GtfsCalendarDateRule) -> dict:
    data = cd.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsCalendarDateRule:{data['hasService']}_{data['appliesOn']}",
            "type": "GtfsCalendarDateRule"}
    for k, v in data.items():
        if k in ("type",): continue
        if k == "hasService":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsCalendarRule:{v}"
            }
        ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

cal_dates_ngsi = [caldate_to_ngsi_ld(cd) for cd in cal_dates]





# GtfsFareAttribute
class GtfsFareAttribute(BaseModel):
    fare_id: str
    type: str = Field("GtfsFareAttribute", const=True)
    price: float
    currency_type: str = Field(..., alias="currencyType")
    payment_method: int = Field(..., alias="paymentMethod")
    transfers: int
    transfer_duration: int = Field(..., alias="transferDuration")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/fare_attributes.txt", dtype=str).replace({np.nan: None})
df["price"] = df["price"].astype(float)
df["payment_method"] = df["payment_method"].astype(int)
df["transfers"] = df["transfers"].astype(int)
df["transfer_duration"] = df["transfer_duration"].astype(int)
fares = [GtfsFareAttribute(**row.to_dict()) for _, row in df.iterrows()]

def fare_to_ngsi_ld(f: GtfsFareAttribute) -> dict:
    data = f.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsFareAttribute:{data['fare_id']}", "type": "GtfsFareAttribute"}
    for k, v in data.items():
        if k in ("fare_id","type"): continue
        ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

fares_ngsi = [fare_to_ngsi_ld(f) for f in fares]





# GtfsFareRule
class GtfsFareRule(BaseModel):
    type: str = Field("GtfsFareRule", const=True)
    fare_id: str = Field(..., alias="hasFare")
    route_id: Optional[str] = Field(..., alias="hasRoute")
    origin_id: Optional[str] = Field(..., alias="originId")
    destination_id: Optional[str] = Field(..., alias="destinationId")
    contains_id: Optional[str] = Field(..., alias="containsId")
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/fare_rules.txt", dtype=str).replace({np.nan: None})
fare_rules = [GtfsFareRule(**row.to_dict()) for _, row in df.iterrows()]

def farerule_to_ngsi_ld(fr: GtfsFareRule) -> dict:
    data = fr.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsFareRule:{data['hasFare']}_{data['containsId']}", "type": "GtfsFareRule"}
    for k, v in data.items():
        if k in ("type",): continue
        if k == "hasFare":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsFareAttribute:{v}"
            }
        elif k == "hasRoute":
            ngsi[k] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{v}"
            }
        else:
            ngsi[k] = {"type": "Property", "value": v}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

fare_rules_ngsi = [farerule_to_ngsi_ld(fr) for fr in fare_rules]





# GtfsShape
class GtfsShape(BaseModel):
    type: str = Field("GtfsShape", const=True)
    shape_id: str
    shape_pt_lat: float
    shape_pt_lon: float
    shape_pt_sequence: int
        
    class Config:
        allow_population_by_field_name = True

df = pd.read_csv("Schemas - versao 2/GTFS TUB/txt/shapes.txt", dtype=str, encoding="utf-8-sig").replace({np.nan: None})
df.columns = df.columns.str.strip()
df["shape_pt_lat"] = df["shape_pt_lat"].astype(float)
df["shape_pt_lon"] = df["shape_pt_lon"].astype(float)
df["shape_pt_sequence"] = df["shape_pt_sequence"].astype(int)
shapes = [GtfsShape(**row.to_dict()) for _, row in df.iterrows()]

def shape_to_ngsi_ld(shape: GtfsShape) -> dict:
    data = shape.dict(by_alias=True, exclude_unset=True, exclude_none=True)
    ngsi = {"id": f"urn:ngsi-ld:GtfsShape:{data['shape_id']}_{data['shape_pt_sequence']}",
            "type": "GtfsShape"}
    ngsi["location"] = {
        "type": "GeoProperty",
        "value": {"type": "Point",
                  "coordinates": [data["shape_pt_lon"], data["shape_pt_lat"]]}
    }
    ngsi["shape_pt_sequence"] = {"type": "Property", "value": data["shape_pt_sequence"]}
    ngsi["@context"] = [
        "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
    ]
    return ngsi

shapes_ngsi = [shape_to_ngsi_ld(s) for s in shapes]



#print(json.dumps(gtfsAgency_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(stops_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(routes_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(trips_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(stop_times_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(calendars_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(cal_dates_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(fares_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(fare_rules_ngsi[0], indent=2, ensure_ascii=False))
#print(json.dumps(shapes_ngsi[0], indent=2, ensure_ascii=False))







def build_gtfs_RouteTripStop_ngsi(trips_ngsi, routes_ngsi, stops_ngsi, stop_times_ngsi):
    def _urn_tail(urn: str) -> str:
        return urn.split(":")[-1] if urn else None
    def _prop(entity: dict, key: str):
        return entity.get(key, {}).get("value") if entity else None
    def _rel(entity: dict, key: str):
        return entity.get(key, {}).get("object") if entity else None
    def _coords(stop_entity: dict):
        loc = stop_entity.get("location", {}).get("value") if stop_entity else None
        if isinstance(loc, dict) and "coordinates" in loc:
            lon, lat = loc["coordinates"]
            return lat, lon
        return None, None

    trips_idx  = {t["id"]: t for t in trips_ngsi}
    routes_idx = {r["id"]: r for r in routes_ngsi}
    stops_idx  = {s["id"]: s for s in stops_ngsi}

    out = []
    for st in stop_times_ngsi:
        trip_urn = st["hasTrip"]["object"]
        stop_urn = st["hasStop"]["object"]
        seq      = _prop(st, "stopSequence")
        arr      = _prop(st, "arrivalTime")
        dep      = _prop(st, "departureTime")

        trip = trips_idx.get(trip_urn)
        if not trip:
            continue

        # Dados da trip
        route_urn = trip["hasRoute"]["object"]
        head_sign = _prop(trip, "headSign")
        direction = _prop(trip, "direction")
        service_id = _rel(trip, "hasService")
        shape_id = _rel(trip, "hasShape")

        # Dados da route
        route = routes_idx.get(route_urn, {})
        route_short = _prop(route, "shortName")
        route_long  = _prop(route, "LongName") or _prop(route, "longName")
        route_type  = _prop(route, "routeType")
        agency_id = _rel(route, "operatedBy")

        # Dados do stop
        stop = stops_idx.get(stop_urn, {})
        stop_name = _prop(stop, "name")
        zone_code = _prop(stop, "zoneCode")
        stop_lat, stop_lon = _coords(stop)

        # Cria a instância NGSI-LD
        entity = {
            "id": f"urn:ngsi-ld:GtfsRouteTripStop:{_urn_tail(trip_urn)}_{_urn_tail(stop_urn)}_{seq}",
            "type": "GtfsRouteTripStop",
            # Relationships
            "hasTrip":  {"type": "Relationship", "object": trip_urn},
            "hasRoute": {"type": "Relationship", "object": route_urn},
            "hasStop":  {"type": "Relationship", "object": stop_urn},
            **({"operatedBy": {"type": "Relationship", "object": agency_id}} if agency_id else {}),
            **({"hasService": {"type": "Relationship", "object": service_id}} if service_id else {}),
            **({"hasShape": {"type": "Relationship", "object": shape_id}} if shape_id else {}),
            # Route 
            **({"routeShortName": {"type": "Property", "value": route_short}} if route_short else {}),
            **({"routeLongName":  {"type": "Property", "value": route_long}}  if route_long  else {}),
            **({"routeType":      {"type": "Property", "value": route_type}}  if route_type  else {}),
            # Trip 
            **({"headSign": {"type": "Property", "value": head_sign}} if head_sign else {}),
            **({"direction": {"type": "Property", "value": direction}} if direction is not None else {}),
            # Stop 
            **({"stopName": {"type": "Property", "value": stop_name}} if stop_name else {}),
            **({"zoneCode": {"type": "Property", "value": zone_code}} if zone_code else {}),
            **({"location": {"type": "GeoProperty","value": {"type": "Point","coordinates": [stop_lon, stop_lat]}
    }
} if stop_lat and stop_lon else {}),
            # StopTime 
            "stopSequence": {"type": "Property", "value": seq},
            "arrivalTime":  {"type": "Property", "value": arr},
            "departureTime":{"type": "Property", "value": dep},
            "@context": [
                "https://raw.githubusercontent.com/smart-data-models/dataModel.UrbanMobility/master/context.jsonld"
            ]
        }
        out.append(entity)
    return out

routetripstop_ngsi = build_gtfs_RouteTripStop_ngsi(trips_ngsi, routes_ngsi, stops_ngsi, stop_times_ngsi)

# Exportar
with open("GtfsRouteTripStop.jsonld", "w", encoding="utf-8") as f:
    json.dump(routetripstop_ngsi, f, ensure_ascii=False, indent=2)
