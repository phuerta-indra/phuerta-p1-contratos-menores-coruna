-- 1) Contratos totales e importe total por año

SELECT COUNT( DISTINCT C.REFERENCIA) AS N_CONTRATOS, SUM(PRECIO) AS PRECIO_TOTAL, F.ANHO
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_FECHAS AS F
WHERE C.FK_FECHA = F.PK_FECHA
GROUP BY F.ANHO


-- 2) Empresas con mayor gasto










-- 3.1) Áreas con mayor gasto







-- 3.2) Tipos de contrato con mayor gasto










-- 3.1) Patrones a investigar