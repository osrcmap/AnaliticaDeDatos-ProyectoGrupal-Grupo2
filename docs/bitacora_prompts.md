# Bitácora de Prompts de IA Generativa - Proyecto AndinaRetail S.A.C.

**Asignatura:** Analítica de Datos - UNMSM - FISI - 2026-1 - Grupo 2
Toda salida de IA fue revisada, ejecutada y validada por el equipo antes de incorporarse al proyecto.

---

## P-01 · Datos · Generación del dataset sintético de AndinaRetail

**Prompt utilizado:**

```
Actúa como ingeniero de datos senior. Genera un único script de Python (3.11) que
use pandas, numpy y Faker (locale 'es_PE'; si no está disponible, usar un locale
en español alternativo y documentarlo). Fija las semillas numpy.random.seed(2026),
random.seed(2026) y Faker.seed(2026) para reproducibilidad. Crea los datos sintéticos
de la empresa ficticia 'AndinaRetail S.A.C.' (retail omnicanal peruano con tiendas
físicas y canal digital) y expórtalos como CSV en la carpeta 'datos/'. Genera:
1) tiendas.csv (12 tiendas: 10 físicas en Lima, Arequipa, Trujillo, Cusco y Piura,
   más 2 virtuales Web y App): id_tienda, nombre, ciudad, region, tipo (Física/Virtual),
   area_m2, fecha_apertura.
2) productos.csv (800): id_producto, nombre, categoria (Abarrotes, Bebidas, Limpieza,
   Cuidado Personal, Electrohogar, Hogar), subcategoria, marca, precio_lista,
   costo_unitario (60-80% del precio), fecha_alta.
3) clientes.csv (15000): id_cliente, nombre, edad (normal media 38, desv. 12, truncada
   18-80), genero, ciudad, distrito, fecha_registro (2022-2025), canal_preferido, segmento.
4) ventas.csv (~250000 líneas, 2023-01-01 a 2025-12-31): id_venta (compartido por las
   líneas de un mismo ticket), fecha, id_cliente, id_tienda, id_producto, cantidad
   (1-8, sesgada a 1-2), precio_unitario, descuento_pct (0-35%), monto_total,
   canal (Tienda/Web/App), metodo_pago.
5) inventario.csv (snapshot mensual por producto-tienda física): id_producto, id_tienda,
   periodo (AAAA-MM), stock_inicial, unidades_vendidas (consistentes con ventas.csv),
   reabastecimiento, stock_final, costo_almacenamiento_unitario.
Incorpora estos patrones: estacionalidad (picos en julio y diciembre) y crecimiento del
canal digital; desde 2025-Q2, caída de margen en Trujillo (mayor descuento y costo de
almacenamiento); churn = sin compras en 90 días al 2025-12-31, con mayor probabilidad
cuando la frecuencia de compra es baja, de modo que un modelo pueda aprenderlo; la
cantidad por línea depende de mes, canal y descuento con ruido moderado; incluye 1-3%
de faltantes en columnas no clave y algunos outliers controlados y documentados.
Imprime al final un resumen de verificación de cada patrón. Entrega además
data_dictionary.md describiendo cada tabla, campo, tipo y dominio. Todos los nombres
deben ser ficticios; no uses datos reales.
```

---

## P-02 · Notebook estadístico

- Tengo una tabla de ventas con faltantes y precios rarísimos, ¿cómo detecto cuáles son errores y cuáles son datos reales?
- ¿Qué hago con los valores vacíos de descuento y método de pago sin sesgar el análisis?
- Ayúdame a sacar media, mediana, desviación y esas medidas para el monto y el ticket, y a interpretar qué significan.
- Quiero comparar si el ticket es más alto en tienda o por app, ¿qué prueba estadística uso?
- Me salió el p-valor bien chiquito pero la diferencia parece mínima, ¿eso está bien o me equivoqué?
- ¿Cómo comparo el ticket promedio entre las 5 ciudades a la vez sin hacer un montón de pruebas?
- Quiero ver si el método de pago depende de la categoría del producto, ¿qué test aplico?
- Explícame en palabras simples qué es la d de Cohen para ponerlo en la conclusión.
- ¿Cómo redacto las conclusiones de esta parte para que suenen a negocio y no solo a números?

## P-03 · RFM, clustering y diagnóstico de margen

- Quiero ver la venta mes a mes y separar la tendencia de la estacionalidad, ¿cómo lo hago?
- ¿Cómo armo un gráfico que muestre cómo fue creciendo el canal digital con los años?
- Ayúdame a hacer el análisis de Pareto para ver qué productos y clientes concentran la venta.
- Necesito segmentar a los clientes por recencia, frecuencia y gasto, explícame cómo se hace el RFM.
- ¿Cómo agrupo clientes automáticamente con K-Means y cómo elijo el número de grupos?
- El margen se está cayendo en una ciudad, ¿cómo investigo la causa paso a paso?
- Quiero comparar antes y después de cierto trimestre para ver qué cambió, ¿cómo lo planteo?
- ¿Cómo hago un heatmap que resalte visualmente el problema de esa ciudad?

## P-04 · Pipelines predictivos (demanda y churn)

- Quiero predecir cuántas unidades se van a vender por categoría el próximo mes, ¿por dónde empiezo?
- ¿Cómo le agrego al modelo la "memoria" de meses anteriores y la estacionalidad de julio y diciembre?
- Ayúdame a comparar varios modelos y saber cuál predice mejor sin hacer trampa con los datos.
- ¿Qué es eso de que no debo dejar que el modelo "vea el futuro" y cómo lo evito?
- Quiero predecir qué clientes van a dejar de comprar, ¿cómo defino bien quién es un cliente perdido?
- ¿Cómo separo entrenamiento y prueba para que el resultado sea confiable?
- Me piden reportar precisión, recall y esas métricas, explícame cuál importa más para retención.
- ¿Cómo muestro qué variables pesan más en la predicción de forma que se entienda?

## P-05 · Modelo de optimización en PuLP

- Ahora no solo quiero predecir, quiero decidir cuánto comprar de cada producto, ¿cómo lo modelo?
- Ayúdame a plantear esto como un problema de optimización con presupuesto y espacio de bodega.
- ¿Cómo pongo la condición de que no me quede sin stock el 95% de las veces?
- Quiero probar qué pasa si subo el nivel de servicio o si me recortan el presupuesto.
- El modelo me daba una respuesta trivial, ¿cómo lo hago más realista y exigente?
- Quiero encontrar el descuento que da más ganancia sin regalar el margen, ¿cómo lo calculo?
- ¿Cómo conecto lo del diagnóstico de la ciudad con esta recomendación final?
- Ayúdame a redactar las recomendaciones para que se vea que todo el proyecto está conectado.

---