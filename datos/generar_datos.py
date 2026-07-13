# -*- coding: utf-8 -*-
"""
generar_datos.py - Generación de datos sintéticos de AndinaRetail S.A.C.
Proyecto Grupal - Analítica de Datos (UNMSM - FISI - E.P. Ingeniería de Software)

Este script genera 5 tablas CSV reproducibles (con seed 2026) en la carpeta actual:
  tiendas.csv, productos.csv, clientes.csv, ventas.csv, inventario.csv

Los patrones incorporados son (documentados en data_dictionary.md):
  1) Estacionalidad: picos de venta en julio (Fiestas Patrias) y diciembre (Navidad).
  2) Crecimiento del canal digital (Web/App) a lo largo del tiempo.
  3) Patrón diagnóstico: desde 2025-Q2, caída de margen en Trujillo
     (mayor descuento promedio y mayor costo de almacenamiento).
  4) Patrón de churn: cliente inactivo = sin compras en los últimos 90 días
     al 2025-12-31; la probabilidad de inactividad aumenta con baja frecuencia
     de compra histórica (señal aprendible por un modelo).
  5) Demanda predecible: la cantidad depende del mes, el canal y el descuento,
     con ruido aleatorio moderado.
  6) Calidad de datos: ~1-3% de valores faltantes en columnas no clave y
     outliers controlados (cantidades y precios anómalos).

Requisitos: Python 3.11+, pandas, numpy, faker
Ejecución:  python generar_datos.py
"""

import random
import numpy as np
import pandas as pd
from faker import Faker

# 0. REPRODUCIBILIDAD: semillas fijas
SEED = 2026
np.random.seed(SEED)
random.seed(SEED)
Faker.seed(SEED)
# Nota: el locale 'es_PE' no está disponible en todas las versiones de Faker
# (p. ej. Faker 40.x no lo incluye). Se intenta 'es_PE' y, si no existe,
# se usa 'es_CO'/'es_ES' como alternativa en español, sin afectar la semilla.
for _locale in ("es_PE", "es_CO", "es_ES"):
    try:
        fake = Faker(_locale)
        break
    except AttributeError:
        continue
print(f"Locale de Faker en uso: {_locale}")
rng = np.random.default_rng(SEED)

FECHA_INICIO_VENTAS = pd.Timestamp("2023-01-01")
FECHA_FIN_VENTAS = pd.Timestamp("2025-12-31")
FECHA_CORTE_CHURN = FECHA_FIN_VENTAS          # fecha de referencia para churn
DIAS_CHURN = 90                               # inactivo = sin compras en 90 días

# 1. TIENDAS (12: 10 físicas + 2 virtuales)
REGION = {"Lima": "Lima", "Arequipa": "Arequipa", "Trujillo": "La Libertad",
          "Cusco": "Cusco", "Piura": "Piura"}

tiendas_fisicas = [
    ("Lima", "AndinaRetail Miraflores"), ("Lima", "AndinaRetail San Miguel"),
    ("Lima", "AndinaRetail Los Olivos"), ("Arequipa", "AndinaRetail Cayma"),
    ("Arequipa", "AndinaRetail Cercado AQP"), ("Trujillo", "AndinaRetail Trujillo Centro"),
    ("Trujillo", "AndinaRetail Víctor Larco"), ("Cusco", "AndinaRetail Wanchaq"),
    ("Cusco", "AndinaRetail Cusco Centro"), ("Piura", "AndinaRetail Piura Open"),
]

rows = []
for i, (ciudad, nombre) in enumerate(tiendas_fisicas, start=1):
    rows.append({
        "id_tienda": f"T{i:02d}", "nombre": nombre, "ciudad": ciudad,
        "region": REGION[ciudad], "tipo": "Física",
        "area_m2": int(rng.integers(450, 2200)),
        "fecha_apertura": fake.date_between(start_date="-12y", end_date="-2y").isoformat(),
    })
# Canales virtuales (operan a nivel nacional; se registran con ciudad Lima / sede central)
rows.append({"id_tienda": "T11", "nombre": "AndinaRetail Web", "ciudad": "Lima",
             "region": "Lima", "tipo": "Virtual", "area_m2": np.nan,
             "fecha_apertura": "2020-05-15"})
rows.append({"id_tienda": "T12", "nombre": "AndinaRetail App", "ciudad": "Lima",
             "region": "Lima", "tipo": "Virtual", "area_m2": np.nan,
             "fecha_apertura": "2021-08-01"})
tiendas = pd.DataFrame(rows)

TIENDAS_POR_CIUDAD = {c: tiendas.loc[(tiendas.ciudad == c) & (tiendas.tipo == "Física"),
                                     "id_tienda"].tolist() for c in REGION}
TIENDA_WEB, TIENDA_APP = "T11", "T12"

# 2. PRODUCTOS (800)
N_PRODUCTOS = 800
CATALOGO = {
    "Abarrotes":        (["Arroz y menestras", "Fideos y pastas", "Aceites", "Conservas", "Harinas y azúcar", "Snacks"], (2.5, 55)),
    "Bebidas":          (["Gaseosas", "Aguas", "Jugos", "Cervezas", "Vinos y licores", "Energizantes"], (2, 95)),
    "Limpieza":         (["Detergentes", "Lavavajillas", "Desinfectantes", "Papel higiénico", "Ambientadores"], (4, 65)),
    "Cuidado Personal": (["Shampoo", "Jabones", "Cuidado dental", "Cuidado de piel", "Afeitado"], (5, 90)),
    "Electrohogar":     (["Licuadoras", "Hervidores", "Televisores", "Refrigeración", "Lavado", "Microondas"], (90, 2800)),
    "Hogar":            (["Menaje", "Textil hogar", "Decoración", "Muebles pequeños", "Organización"], (12, 650)),
}
MARCAS = ["Qori", "Wayra", "Inti", "Misti", "Chaska", "Kusi", "Pacífico", "Andes",
          "Runa", "Killa", "Sami", "Tika", "Nuna", "Yachay", "Puma Norte"]
# Mezcla de categorías (probabilidad de que un producto pertenezca a cada una)
CATS = list(CATALOGO.keys())
MIX_CAT_PRODUCTO = [0.24, 0.18, 0.14, 0.16, 0.13, 0.15]

cat_prod = rng.choice(CATS, size=N_PRODUCTOS, p=MIX_CAT_PRODUCTO)
rows = []
for i in range(N_PRODUCTOS):
    cat = cat_prod[i]
    subcats, (pmin, pmax) = CATALOGO[cat]
    sub = random.choice(subcats)
    marca = random.choice(MARCAS)
    # precios con distribución log-uniforme (más productos baratos que caros)
    precio = float(np.round(np.exp(rng.uniform(np.log(pmin), np.log(pmax))), 2))
    costo = float(np.round(precio * rng.uniform(0.60, 0.80), 2))  # costo = 60–80% del precio
    rows.append({
        "id_producto": f"P{i+1:04d}",
        "nombre": f"{sub} {marca} {random.choice(['Clásico','Premium','Familiar','Eco','Max','Lite'])} {rng.integers(1, 99)}",
        "categoria": cat, "subcategoria": sub, "marca": marca,
        "precio_lista": precio, "costo_unitario": costo,
        "fecha_alta": fake.date_between(start_date="-8y",
                                        end_date=pd.Timestamp("2022-12-31").date()).isoformat(),
    })
productos = pd.DataFrame(rows)

# 3. CLIENTES (15 000)
N_CLIENTES = 15_000
DISTRITOS = {
    "Lima": ["Miraflores", "San Isidro", "Santiago de Surco", "San Miguel", "Los Olivos",
             "San Juan de Lurigancho", "Comas", "La Molina", "Jesús María", "Ate"],
    "Arequipa": ["Cercado", "Cayma", "Yanahuara", "José Luis B. y Rivero", "Paucarpata"],
    "Trujillo": ["Trujillo", "Víctor Larco", "La Esperanza", "El Porvenir"],
    "Cusco": ["Cusco", "Wanchaq", "San Sebastián", "Santiago"],
    "Piura": ["Piura", "Castilla", "Veintiséis de Octubre"],
}
MIX_CIUDAD = {"Lima": 0.46, "Arequipa": 0.16, "Trujillo": 0.15, "Cusco": 0.12, "Piura": 0.11}

ciudades_cli = rng.choice(list(MIX_CIUDAD), size=N_CLIENTES, p=list(MIX_CIUDAD.values()))
edad = np.clip(np.round(rng.normal(38, 12, N_CLIENTES)), 18, 80).astype(int)
genero = rng.choice(["F", "M"], size=N_CLIENTES, p=[0.53, 0.47])
canal_pref = rng.choice(["Tienda", "Web", "App"], size=N_CLIENTES, p=[0.55, 0.25, 0.20])
segmento = rng.choice(["Consumidor", "Familiar", "Premium"], size=N_CLIENTES, p=[0.55, 0.33, 0.12])

reg_ini, reg_fin = pd.Timestamp("2022-01-01"), pd.Timestamp("2025-09-30")
fecha_registro = reg_ini + pd.to_timedelta(
    rng.integers(0, (reg_fin - reg_ini).days + 1, N_CLIENTES), unit="D")

clientes = pd.DataFrame({
    "id_cliente": [f"C{i+1:05d}" for i in range(N_CLIENTES)],
    "nombre": [fake.name() for _ in range(N_CLIENTES)],
    "edad": edad, "genero": genero, "ciudad": ciudades_cli,
    "distrito": [random.choice(DISTRITOS[c]) for c in ciudades_cli],
    "fecha_registro": fecha_registro.strftime("%Y-%m-%d"),
    "canal_preferido": canal_pref, "segmento": segmento,
})

# 4. VENTAS (~250 000 líneas, 2023-01-01 a 2025-12-31)
# 4.1 Comportamiento por cliente: frecuencia base y churn dependiente de la frecuencia
freq_mensual = rng.gamma(shape=1.3, scale=0.26, size=N_CLIENTES)          # tickets/mes
freq_mensual = np.clip(freq_mensual, 0.03, 3.5)
# P(churn) = sigmoide decreciente en la frecuencia -> baja frecuencia => más churn
p_churn = 1 / (1 + np.exp(-(0.1 - 6.5 * freq_mensual)))
es_churn = rng.random(N_CLIENTES) < p_churn

inicio_actividad = np.maximum(pd.DatetimeIndex(fecha_registro), FECHA_INICIO_VENTAS)
fin_actividad = np.where(
    es_churn,
    # churners: última compra entre 2023-07 y (corte - 91 días)
    pd.DatetimeIndex(pd.Timestamp("2023-07-01")
                     + pd.to_timedelta(rng.integers(0, (FECHA_CORTE_CHURN - pd.Timedelta(days=DIAS_CHURN + 1)
                                                        - pd.Timestamp("2023-07-01")).days, N_CLIENTES), unit="D")),
    FECHA_FIN_VENTAS,
)
fin_actividad = pd.DatetimeIndex(fin_actividad)
fin_actividad = pd.DatetimeIndex(np.maximum(fin_actividad, inicio_actividad + pd.Timedelta(days=20)))

meses_activo = np.clip((fin_actividad - inicio_actividad).days.to_numpy() / 30.44, 0.7, None)
n_tickets = rng.poisson(freq_mensual * meses_activo)
n_tickets = np.clip(n_tickets, 1, None)                                    # todo cliente compra al menos 1 vez

# 4.2 Tickets: fecha uniforme dentro de la ventana de actividad de cada cliente
idx_cli = np.repeat(np.arange(N_CLIENTES), n_tickets)
u = rng.random(idx_cli.size)
fecha_ticket = (inicio_actividad[idx_cli]
                + pd.to_timedelta((u * (fin_actividad[idx_cli] - inicio_actividad[idx_cli]).days).astype(int), unit="D"))

# Estacionalidad: duplicar una fracción de tickets de julio y diciembre (picos de campaña)
mes_t = fecha_ticket.month
boost = ((mes_t == 7) | (mes_t == 12)) & (rng.random(idx_cli.size) < 0.45)
idx_cli = np.concatenate([idx_cli, idx_cli[boost]])
fecha_extra = fecha_ticket[boost] + pd.to_timedelta(rng.integers(-6, 7, boost.sum()), unit="D")
fecha_ticket = pd.DatetimeIndex(np.concatenate([fecha_ticket.values, fecha_extra.values]))
fecha_ticket = pd.DatetimeIndex(np.clip(fecha_ticket.values,
                                        FECHA_INICIO_VENTAS.to_datetime64(),
                                        np.minimum(fin_actividad[idx_cli].values, FECHA_FIN_VENTAS.to_datetime64())))
N_TICKETS = idx_cli.size

# 4.3 Canal por ticket: crecimiento digital en el tiempo + preferencia del cliente
anios = (fecha_ticket - FECHA_INICIO_VENTAS).days / 365.25
p_digital = np.clip(0.24 + 0.09 * anios, 0, 0.60)                          # tendencia creciente
pref = clientes["canal_preferido"].to_numpy()[idx_cli]
p_digital = np.clip(p_digital + np.where(pref == "Tienda", -0.08, 0.15), 0.05, 0.85)
es_digital = rng.random(N_TICKETS) < p_digital
es_app = es_digital & (rng.random(N_TICKETS) < np.clip(0.38 + 0.06 * anios, 0, 0.6))
canal_ticket = np.where(~es_digital, "Tienda", np.where(es_app, "App", "Web"))

# Tienda: física de la ciudad del cliente, o canal virtual correspondiente
ciudad_cli_arr = clientes["ciudad"].to_numpy()[idx_cli]
tienda_ticket = np.empty(N_TICKETS, dtype=object)
for c, tiendas_c in TIENDAS_POR_CIUDAD.items():
    m = (canal_ticket == "Tienda") & (ciudad_cli_arr == c)
    tienda_ticket[m] = rng.choice(tiendas_c, size=int(m.sum()))
tienda_ticket[canal_ticket == "Web"] = TIENDA_WEB
tienda_ticket[canal_ticket == "App"] = TIENDA_APP

# Método de pago (depende del canal)
metodo_ticket = np.empty(N_TICKETS, dtype=object)
m_fis = canal_ticket == "Tienda"
metodo_ticket[m_fis] = rng.choice(["Efectivo", "Tarjeta", "Yape", "Plin"],
                                  size=int(m_fis.sum()), p=[0.34, 0.36, 0.20, 0.10])
metodo_ticket[~m_fis] = rng.choice(["Tarjeta", "Yape", "Plin", "Transferencia"],
                                   size=int((~m_fis).sum()), p=[0.55, 0.25, 0.10, 0.10])

# 4.4 Líneas por ticket y producto por línea
lineas_por_ticket = 1 + rng.poisson(1.15, N_TICKETS)
lineas_por_ticket = np.clip(lineas_por_ticket, 1, 6)
il = np.repeat(np.arange(N_TICKETS), lineas_por_ticket)                    # índice de ticket por línea
N_LINEAS = il.size

# Mezcla de categorías en la venta (rotación alta en consumo masivo)
MIX_CAT_VENTA = {"Abarrotes": 0.30, "Bebidas": 0.21, "Limpieza": 0.13,
                 "Cuidado Personal": 0.15, "Electrohogar": 0.07, "Hogar": 0.14}
prod_por_cat = {c: productos.index[productos.categoria == c].to_numpy() for c in CATS}
cat_linea = rng.choice(CATS, size=N_LINEAS, p=[MIX_CAT_VENTA[c] for c in CATS])
idx_prod = np.empty(N_LINEAS, dtype=int)
for c in CATS:
    m = cat_linea == c
    idx_prod[m] = rng.choice(prod_por_cat[c], size=int(m.sum()))

fecha_l = fecha_ticket[il]
mes_l = fecha_l.month
canal_l = canal_ticket[il]
ciudad_tienda_map = tiendas.set_index("id_tienda")["ciudad"].to_dict()
tienda_l = tienda_ticket[il]

# 4.5 Descuento: base + campañas (jul/dic) + patrón diagnóstico Trujillo desde 2025-Q2
desc = np.where(rng.random(N_LINEAS) < 0.45, 0.0, rng.beta(1.4, 7.0, N_LINEAS) * 30)
desc += np.where((mes_l == 7) | (mes_l == 12), rng.uniform(2, 7, N_LINEAS), 0)
es_trujillo = np.isin(tienda_l, TIENDAS_POR_CIUDAD["Trujillo"])
post_2025q2 = fecha_l >= pd.Timestamp("2025-04-01")
desc += np.where(es_trujillo & post_2025q2, rng.uniform(6, 12, N_LINEAS), 0)   # caída de margen
desc = np.clip(np.round(desc, 1), 0, 35)

# 4.6 Cantidad: depende de mes (campañas), canal y descuento + ruido moderado
efecto = (0.55
          + 0.030 * desc                                   # más descuento -> más unidades
          + np.where((mes_l == 7) | (mes_l == 12), 0.35, 0)
          + np.where(canal_l == "Tienda", 0.10, 0.0)
          + np.where(canal_l == "App", -0.05, 0.0))
cantidad = 1 + rng.poisson(np.clip(efecto + rng.normal(0, 0.15, N_LINEAS), 0.05, None))
cantidad = np.clip(cantidad, 1, 8)
es_electro = productos["categoria"].to_numpy()[idx_prod] == "Electrohogar"
cantidad = np.where(es_electro, np.minimum(cantidad, 2), cantidad)

precio_lista_l = productos["precio_lista"].to_numpy()[idx_prod]
precio_unit = np.round(precio_lista_l * rng.uniform(0.97, 1.03, N_LINEAS), 2)
monto_total = np.round(cantidad * precio_unit * (1 - desc / 100), 2)

ventas = pd.DataFrame({
    "id_venta": np.char.add("V", np.char.zfill(il.astype(str), 7)),
    "fecha": fecha_l.strftime("%Y-%m-%d"),
    "id_cliente": clientes["id_cliente"].to_numpy()[idx_cli[il]],
    "id_tienda": tienda_l,
    "id_producto": productos["id_producto"].to_numpy()[idx_prod],
    "cantidad": cantidad.astype(int),
    "precio_unitario": precio_unit,
    "descuento_pct": desc,
    "monto_total": monto_total,
    "canal": canal_l,
    "metodo_pago": metodo_ticket[il],
})

# 4.7 Outliers controlados (documentados): cantidades mayoristas y precios con error de digitación
out_qty = rng.choice(N_LINEAS, size=40, replace=False)
ventas.loc[out_qty, "cantidad"] = rng.integers(40, 90, 40)
ventas.loc[out_qty, "monto_total"] = np.round(
    ventas.loc[out_qty, "cantidad"] * ventas.loc[out_qty, "precio_unitario"]
    * (1 - ventas.loc[out_qty, "descuento_pct"] / 100), 2)
out_px = rng.choice(np.setdiff1d(np.arange(N_LINEAS), out_qty), size=15, replace=False)
ventas.loc[out_px, "precio_unitario"] = np.round(ventas.loc[out_px, "precio_unitario"] * 100, 2)  # error x100
ventas.loc[out_px, "monto_total"] = np.round(
    ventas.loc[out_px, "cantidad"] * ventas.loc[out_px, "precio_unitario"]
    * (1 - ventas.loc[out_px, "descuento_pct"] / 100), 2)

# 5. INVENTARIO (snapshot mensual por producto x tienda física)
v_tmp = ventas.copy()
v_tmp["periodo"] = v_tmp["fecha"].str.slice(0, 7)
vend = (v_tmp[v_tmp["id_tienda"].isin(tiendas.loc[tiendas.tipo == "Física", "id_tienda"])]
        .groupby(["id_producto", "id_tienda", "periodo"], as_index=False)["cantidad"].sum()
        .rename(columns={"cantidad": "unidades_vendidas"}))

periodos = pd.period_range("2023-01", "2025-12", freq="M").astype(str)
grid = pd.MultiIndex.from_product(
    [productos["id_producto"], tiendas.loc[tiendas.tipo == "Física", "id_tienda"], periodos],
    names=["id_producto", "id_tienda", "periodo"]).to_frame(index=False)
inv = grid.merge(vend, how="left", on=["id_producto", "id_tienda", "periodo"])
inv["unidades_vendidas"] = inv["unidades_vendidas"].fillna(0).astype(int)

n_inv = len(inv)
buffer_seg = rng.integers(3, 12, n_inv)
inv["stock_inicial"] = (inv["unidades_vendidas"] * rng.uniform(1.05, 1.5, n_inv)).round().astype(int) + buffer_seg
inv["reabastecimiento"] = np.maximum(
    0, (inv["unidades_vendidas"] * rng.uniform(0.8, 1.2, n_inv)).round().astype(int)
       + rng.integers(-2, 4, n_inv))
inv["stock_final"] = np.maximum(0, inv["stock_inicial"] + inv["reabastecimiento"] - inv["unidades_vendidas"])

cat_inv = inv["id_producto"].map(productos.set_index("id_producto")["categoria"])
costo_base = cat_inv.map({"Abarrotes": 0.12, "Bebidas": 0.15, "Limpieza": 0.14,
                          "Cuidado Personal": 0.13, "Electrohogar": 2.20, "Hogar": 0.60}).to_numpy()
costo_alm = costo_base * rng.uniform(0.85, 1.25, n_inv)
# Patrón diagnóstico: mayor costo de almacenamiento en Trujillo desde 2025-04
ciudad_inv = inv["id_tienda"].map(tiendas.set_index("id_tienda")["ciudad"])
m_truj = (ciudad_inv == "Trujillo") & (inv["periodo"] >= "2025-04")
costo_alm = np.where(m_truj, costo_alm * 1.65, costo_alm)
inv["costo_almacenamiento_unitario"] = np.round(costo_alm, 3)

# 6. CALIDAD DE DATOS: 1–3% de faltantes en columnas NO clave
def poner_faltantes(df, col, frac):
    idx = rng.choice(len(df), size=int(len(df) * frac), replace=False)
    df.loc[idx, col] = np.nan

poner_faltantes(clientes, "edad", 0.020)
poner_faltantes(clientes, "distrito", 0.015)
poner_faltantes(clientes, "genero", 0.010)
poner_faltantes(productos, "marca", 0.015)
poner_faltantes(ventas, "metodo_pago", 0.020)
poner_faltantes(ventas, "descuento_pct", 0.010)   # exige imputación antes de modelar
poner_faltantes(inv, "costo_almacenamiento_unitario", 0.010)

# 7. EXPORTAR
tiendas.to_csv("tiendas.csv", index=False)
productos.to_csv("productos.csv", index=False)
clientes.to_csv("clientes.csv", index=False)
ventas.to_csv("ventas.csv", index=False)
inv.to_csv("inventario.csv", index=False)

# 8. VERIFICACIÓN DE PATRONES (resumen impreso)
print(f"tiendas: {len(tiendas)} | productos: {len(productos)} | clientes: {len(clientes)}")
print(f"ventas (líneas): {len(ventas):,} | inventario (filas): {len(inv):,}\n")

v = ventas.copy()
v["fecha"] = pd.to_datetime(v["fecha"])
v["mes"] = v["fecha"].dt.month
v["anio"] = v["fecha"].dt.year

print("- Estacionalidad (monto total por mes, millones S/):")
print((v.groupby("mes")["monto_total"].sum() / 1e6).round(2).to_string())

print("\n- Participación digital por año (% de líneas Web+App):")
print((v.assign(dig=v.canal.isin(["Web", "App"])).groupby("anio")["dig"].mean() * 100).round(1).to_string())

costo_map = productos.set_index("id_producto")["costo_unitario"]
v["margen"] = v["monto_total"] - v["cantidad"] * v["id_producto"].map(costo_map)
ciudad_map = tiendas.set_index("id_tienda")["ciudad"]
v["ciudad_tienda"] = v["id_tienda"].map(ciudad_map)
v["trim"] = v["fecha"].dt.to_period("Q").astype(str)
mt = (v[v.canal == "Tienda"].groupby(["ciudad_tienda", "trim"])
      .apply(lambda d: d.margen.sum() / d.monto_total.sum() * 100, include_groups=False)
      .unstack(0).round(1))
print("\n- Margen %% por trimestre (tiendas físicas), Trujillo cae desde 2025Q2:")
print(mt[["Lima", "Trujillo"]].to_string())

ult = v.groupby("id_cliente")["fecha"].max()
frec = v.groupby("id_cliente")["id_venta"].nunique()
inactivo = (FECHA_CORTE_CHURN - ult).dt.days > DIAS_CHURN
print(f"\n- Tasa de inactividad (churn 90 días): {inactivo.mean()*100:.1f}%")
q = pd.qcut(frec.rank(method="first"), 4, labels=["Q1 baja frec.", "Q2", "Q3", "Q4 alta frec."])
print("- Churn por cuartil de frecuencia (señal aprendible):")
print((inactivo.groupby(q, observed=True).mean() * 100).round(1).to_string())

print("\n- Faltantes (%):")
for nom, df in [("clientes", clientes), ("productos", productos), ("ventas", ventas), ("inventario", inv)]:
    tot = df.isna().mean().loc[lambda s: s > 0]
    if len(tot):
        print(f"  {nom}: " + ", ".join(f"{c}={p*100:.1f}%" for c, p in tot.items()))
print("\nOK - datos generados de forma reproducible (semilla 2026).")
