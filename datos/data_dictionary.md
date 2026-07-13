# Diccionario de Datos - AndinaRetail S.A.C. (datos sintéticos)

**Proyecto Grupal - Analítica de Datos · UNMSM - FISI - E.P. Ingeniería de Software · 2026-1**

Datos 100% sintéticos generados con `generar_datos.py` (Python 3.11+, pandas, numpy, Faker).
**Reproducibilidad:** semillas fijas `numpy.random.seed(2026)`, `random.seed(2026)`, `Faker.seed(2026)`.
Ninguna persona o empresa real está representada; todos los nombres son ficticios.

> Nota técnica: el locale `es_PE` de Faker no existe en las versiones recientes de la librería
> (verificado en Faker 40.x). El script intenta `es_PE` y usa como alternativa `es_CO`/`es_ES`
> (nombres en español), lo cual queda registrado en la bitácora de prompts.

---

## 1. tiendas.csv (12 filas)

| Campo | Tipo | Dominio / Descripción |
|---|---|---|
| id_tienda | str (PK) | T01–T12. T01–T10 físicas; T11 = canal Web, T12 = canal App |
| nombre | str | Nombre comercial ficticio de la tienda |
| ciudad | str | Lima, Arequipa, Trujillo, Cusco, Piura (virtuales registradas en Lima/sede central) |
| region | str | Región correspondiente a la ciudad (Trujillo → La Libertad) |
| tipo | str | Física / Virtual |
| area_m2 | int | 450–2200 m² (NaN en tiendas virtuales) |
| fecha_apertura | date | AAAA-MM-DD |

## 2. productos.csv (800 filas)

| Campo | Tipo | Dominio / Descripción |
|---|---|---|
| id_producto | str (PK) | P0001–P0800 |
| nombre | str | Nombre ficticio (subcategoría + marca + variante) |
| categoria | str | Abarrotes, Bebidas, Limpieza, Cuidado Personal, Electrohogar, Hogar |
| subcategoria | str | 5–6 subcategorías por categoría |
| marca | str | 15 marcas ficticias (Qori, Wayra, Inti, …). (~1.5% faltantes) |
| precio_lista | float | Soles (S/). Log-uniforme por rango de categoría (Electrohogar: 90–2800) |
| costo_unitario | float | 60%–80% del precio_lista |
| fecha_alta | date | Hasta 2022-12-31 (todo el catálogo existe antes del periodo de ventas) |

## 3. clientes.csv (15 000 filas)

| Campo | Tipo | Dominio / Descripción |
|---|---|---|
| id_cliente | str (PK) | C00001–C15000 |
| nombre | str | Nombre ficticio (Faker) |
| edad | float | Normal(μ=38, σ=12) truncada a [18, 80]. (~2% faltantes) |
| genero | str | F / M. (~1% faltantes) |
| ciudad | str | Mezcla: Lima 46%, Arequipa 16%, Trujillo 15%, Cusco 12%, Piura 11% |
| distrito | str | Distritos reales de cada ciudad. (~1.5% faltantes) |
| fecha_registro | date | 2022-01-01 a 2025-09-30 |
| canal_preferido | str | Tienda 55%, Web 25%, App 20% (influye en el canal de compra) |
| segmento | str | Consumidor 55%, Familiar 33%, Premium 12% |

## 4. ventas.csv (~275 000 líneas; 2023-01-01 a 2025-12-31)

Grano: **línea de venta** (un producto dentro de un ticket). Las líneas de un mismo ticket
comparten id_venta, fecha, cliente, tienda, canal y método de pago.

| Campo | Tipo | Dominio / Descripción |
|---|---|---|
| id_venta | str | V0000000… id del ticket (se repite por cada línea del ticket, 1–6 líneas) |
| fecha | date | 2023-01-01 a 2025-12-31 |
| id_cliente | str (FK) | → clientes |
| id_tienda | str (FK) | → tiendas (física de la ciudad del cliente, o T11/T12 si es digital) |
| id_producto | str (FK) | → productos |
| cantidad | int | 1–8, sesgada a 1–2 (Electrohogar máx. 2). (Outliers: 40 líneas con 40–89 unidades (compras mayoristas)) |
| precio_unitario | float | precio_lista × U(0.97, 1.03). (Outliers: 15 líneas con precio ×100 (error de digitación simulado)) |
| descuento_pct | float | 0–35%. ~45% de líneas sin descuento. (~1% faltantes) |
| monto_total | float | cantidad × precio_unitario × (1 − descuento_pct/100) |
| canal | str | Tienda / Web / App |
| metodo_pago | str | Efectivo, Tarjeta, Yape, Plin, Transferencia (mezcla depende del canal). (~2% faltantes) |

## 5. inventario.csv (288 000 filas: 800 productos × 10 tiendas físicas × 36 meses)

| Campo | Tipo | Dominio / Descripción |
|---|---|---|
| id_producto | str (FK) | → productos |
| id_tienda | str (FK) | → tiendas (solo físicas T01–T10) |
| periodo | str | AAAA-MM, de 2023-01 a 2025-12 |
| stock_inicial | int | ≈ unidades_vendidas × U(1.05, 1.5) + buffer de seguridad (3–11) |
| unidades_vendidas | int | Agregado real de ventas.csv por producto-tienda-mes (0 si no hubo venta) |
| reabastecimiento | int | ≈ unidades_vendidas × U(0.8, 1.2) + ruido |
| stock_final | int | stock_inicial + reabastecimiento − unidades_vendidas (≥ 0) |
| costo_almacenamiento_unitario | float | S/ por unidad-mes según categoría (Electrohogar el más alto). (~1% faltantes) |

---

## Patrones controlados incorporados (señales para las Partes 1–4)

1. **Estacionalidad:** picos de venta en **julio** (Fiestas Patrias) y **diciembre** (Navidad).
   Verificado: el monto de julio y diciembre es ~60–70% mayor al promedio de los demás meses.
2. **Crecimiento digital:** la participación Web+App crece de ~31% (2023) a ~41% (2024) y ~49% (2025).
3. **Patrón diagnóstico (caída de margen en Trujillo):** desde **2025-04** (2025-Q2) las líneas
   de tiendas de Trujillo reciben **+6 a +12 pp de descuento adicional** y su inventario un
   **costo de almacenamiento ×1.65**. Resultado verificado: margen bruto de Trujillo cae de
   ~26–28% a ~17–21% desde 2025-Q2, mientras las demás ciudades se mantienen estables.
4. **Churn aprendible:** cliente **inactivo = sin compras en los últimos 90 días al 2025-12-31**.
   La probabilidad de inactividad se generó como función decreciente de la frecuencia mensual
   de compra (sigmoide). Tasa global ≈ **52%**; por cuartil de frecuencia: Q1 (baja) ≈ 85%,
   Q2 ≈ 63%, Q3 ≈ 42%, Q4 (alta) ≈ 18%.
5. **Demanda predecible:** la cantidad por línea aumenta con el **descuento** (+0.03 unidades
   esperadas por punto), con los meses de campaña (**julio/diciembre**: +0.35) y con el canal
   **Tienda** (+0.10), con ruido gaussiano moderado (σ=0.15) sobre la tasa de un Poisson.
6. **Calidad de datos:** faltantes del 1–3% en columnas no clave (edad, género, distrito, marca,
   método de pago, descuento, costo de almacenamiento) y **55 outliers controlados** en ventas
   (40 cantidades mayoristas + 15 precios ×100), para exigir limpieza en la Parte 1.

## Relaciones (modelo de datos)

```
clientes (1) ──< ventas >── (1) productos
tiendas  (1) ──< ventas
productos (1) ──< inventario >── (1) tiendas [solo físicas]
```

## Cómo regenerar

```bash
python venv -m .venv
source .venv/bin/activate
pip install pandas numpy faker
cd datos/
python generar_datos.py
```
