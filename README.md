# Proyecto Grupal — Caso integrador AndinaRetail S.A.C.

**Asignatura:** Analítica de Datos (2011104) · E.P. Ingeniería de Software · FISI – UNMSM · 2026-1
**Docente:** Mg. Juan Gamarra Moreno

## Integrantes y roles

| Integrante | Rol |
|---|---|
| Oscar Macchiavello | Líder de proyecto / Data PM |
| Oscar Macchiavello | Ingeniero(a) de datos |
| Luis La Torre | Analista estadístico / descriptivo |
| Luis La Torre | Científico(a) de datos |
| Jorge Tomayquispe | Analista de optimización / BI |
| Jorge Tomayquispe | BI |

## Estructura del repositorio (Anexo A)

```
proyecto-andinaretail/
├── datos/                  
├── notebooks/              
├── powerbi/                
├── docs/               
├── presentacion/           
├── exposicion/           
└── README.md
```

## Guía de ejecución (reproducibilidad)

```bash
pip install pandas numpy faker scipy statsmodels scikit-learn xgboost shap pulp \
            matplotlib seaborn jupyter

# 1) Regenerar los datos sintéticos (semillas fijas 2026)
cd datos && python generar_datos.py && cd ..

# 2) Ejecutar los notebooks en orden (dependen solo de datos/)
jupyter nbconvert --to notebook --execute --inplace notebooks/01_estadistica.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_descriptivo_diagnostico.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_predictivo.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/04_prescriptivo.ipynb
```

> Nota: el locale `es_PE` de Faker no existe en versiones recientes; el script usa
> fallback a `es_CO`/`es_ES` (documentado en la bitácora, P-01).

## Resumen de resultados por parte

| Parte | Entregable | Hallazgo principal |
|---|---|---|
| Datos | `generar_datos.py` + 5 CSV + diccionario | 275 115 líneas de venta con patrones controlados y verificados |
| 1 · Estadística | `01_estadistica.ipynb` | Ticket Tienda > Digital (p<0.05, efecto pequeño); ticket homogéneo entre ciudades (ANOVA); método de pago depende del canal, no de la categoría |
| 2 · Descriptivo/diagnóstico | `02_descriptivo_diagnostico.ipynb` | Estacionalidad jul/dic; digital 31%→49%; Pareto marcado; 4 segmentos RFM/K-Means; causa raíz de Trujillo: descuento efectivo +9 pp y almacenaje +65% desde 2025-Q2 |
| 3 · Predictivo | `03_predictivo.ipynb` | Demanda: XGBoost R²=0.915 (test 2025); Churn: AUC=0.815, recencia y frecuencia dominan (sin fuga de información) |
| 4 · Prescriptivo | `04_prescriptivo.ipynb` | Plan óptimo PuLP Q1-2026 en T06 (NS 95%, estado Optimal); presupuesto mínimo cuantificado; descuento óptimo por categoría recupera ≈ S/ 59k/año de margen en Trujillo |
| 5 · Power BI | `powerbi/` | Modelo en estrella, medidas DAX y diseño de 4 páginas listos; el `.pbix` se ensambla siguiendo `guia_construccion_powerbi.md` |
