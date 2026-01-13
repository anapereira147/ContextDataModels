
print("\n")
print("\n")
print("\n")
print("\n")


import json

with open("GtfsRouteTripStop.jsonld", "r", encoding="utf-8") as f:
    routetripstop_ngsi = json.load(f)

def mostrar_tabela_paragens(trip_id: str):
    trip_urn = f"urn:ngsi-ld:GtfsTrip:{trip_id}"
    entidades = [e for e in routetripstop_ngsi if e["hasTrip"]["object"] == trip_urn]
    entidades.sort(key=lambda e: e["stopSequence"]["value"])

    max_len = max(len(e["stopName"]["value"]) for e in entidades)
    col_width = max(20, max_len + 2)

    print(f"{'Sequência':<10} {'Nº da Paragem':<15} {'Nome da Paragem':<{col_width}} {'Tempo de Chegada':<10}")
    print("-" * (col_width + 44))

    for e in entidades:
        seq = e["stopSequence"]["value"]
        stop_name = e["stopName"]["value"]
        stop_id = e["hasStop"]["object"].split(":")[-1]  # extrair apenas o id (sem URN completo)
        arr = e["arrivalTime"]["value"]
        print(f"{seq:<10} {stop_id:<15} {stop_name:<{col_width}} {arr:<10}")

# Exemplo
mostrar_tabela_paragens("87_157")

print("\n")
print("\n")
print("\n")
print("\n")

def mostrar_autocarros_paragem(stop_id: str):
    stop_urn = f"urn:ngsi-ld:GtfsStop:{stop_id}"
    entidades = [e for e in routetripstop_ngsi if e["hasStop"]["object"] == stop_urn]
    rotas_vistas = set()
    entidades.sort(key=lambda e: e["arrivalTime"]["value"])

    max_len_short = max(len(e.get("routeShortName", {}).get("value", "-")) for e in entidades)
    max_len_long  = max(len(e.get("routeLongName", {}).get("value", "-")) for e in entidades)
    col_width_short = max(20, max_len_short + 2)
    col_width_long  = max(20, max_len_long + 2)

    print(f"{'Nº do Autocarro':<{col_width_short}} {'Nome do Autocarro':<{col_width_long}}")
    print("-" * (col_width_short + col_width_long))

    for e in entidades:
        route_short = e.get("routeShortName", {}).get("value", "-")
        route_long  = e.get("routeLongName", {}).get("value", "-")
        chave = (route_short, route_long)
        if chave in rotas_vistas:
            continue
        rotas_vistas.add(chave)
        print(f"{route_short:<{col_width_short}} {route_long:<{col_width_long}}")

# Exemplo
mostrar_autocarros_paragem("1722")

from datetime import datetime, timedelta

print("\n")
print("\n")
print("\n")
print("\n")

from datetime import datetime, timedelta

def mostrar_autocarros_15min(stop_id: str, hora: str):
    stop_urn = f"urn:ngsi-ld:GtfsStop:{stop_id}"
    entidades = [e for e in routetripstop_ngsi if e["hasStop"]["object"] == stop_urn]

    hora_atual = datetime.strptime(hora, "%H:%M:%S")

    limite = hora_atual + timedelta(minutes=15)

    # filtrar autocarros que chegam nos próximos 15 minutos
    proximos = []
    for e in entidades:
        arr_time_str = e["arrivalTime"]["value"]
        arr_time = datetime.strptime(arr_time_str, "%H:%M:%S")
        if hora_atual <= arr_time <= limite:
            proximos.append((arr_time, e))

    # ordenar pela hora de chegada
    proximos.sort(key=lambda x: x[0])

    max_len_short = max(len(e[1].get("routeShortName", {}).get("value", "-")) for e in proximos)
    max_len_long  = max(len(e[1].get("routeLongName", {}).get("value", "-")) for e in proximos)
    col_width_short = max(20, max_len_short + 2)
    col_width_long  = max(20, max_len_long + 2)

    print(f"{'Nº do Autocarro':<{col_width_short}} {'Nome do Autocarro':<{col_width_long}} {'Tempo de Chegada':<25} {'Em (Minutos e Segundos)':<20}")
    print("-" * (col_width_short + col_width_long + 51))

    rotas_vistas = set()
    for arr_time, e in proximos:
        route_short = e.get("routeShortName", {}).get("value", "-")
        route_long  = e.get("routeLongName", {}).get("value", "-")
        chave = (route_short, route_long)
        if chave in rotas_vistas:
            continue
        rotas_vistas.add(chave)
        delta = arr_time - hora_atual
        total_segundos = int(delta.total_seconds())
        if total_segundos <= 0:
            tempo_restante = "A passar na paragem"
        else:
            minutos, segundos = divmod(total_segundos, 60)
            tempo_restante = f"{minutos:02d}m{segundos:02d}s"
        print(f"{route_short:<{col_width_short}} {route_long:<{col_width_long}} {arr_time.strftime('%H:%M:%S'):<25} {tempo_restante:<20}")

# Exemplo
mostrar_autocarros_15min("1722", "13:00:00")


print("\n")
print("\n")
print("\n")
print("\n")