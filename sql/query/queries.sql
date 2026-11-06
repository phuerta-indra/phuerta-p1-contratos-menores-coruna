-- 1) Contratos totales e importe total por año


SELECT 
COUNT(*) AS N_CONTRATOS,
SUM(C.PRECIO)/1000000 AS PRECIO_TOTAL,
ROUND(AVG(C.PRECIO) , 2) AS PRECIO_MEDIO,
F.ANHO
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_FECHAS AS F
ON C.FK_FECHA = F.PK_FECHA
GROUP BY F.ANHO


/*
 Se puede observar que la tendencia de contratación va disminuyendo: 2536 > 2365 > 2269 > 2076 (519 x 4 trimestres) 
 para los años 2023 - 2024 - 2025 - 2026 (estimado).

 En cuanto a los gastos totales por cada año, pese a que el número de contratos va disminuyendo los gastos aumentan:
 7,77 - 8,83 - 8,9 - 10,32 (estimado --> 2,58 x 4 trimestres) en millones de euros.

 La media refuerza la idea de que las contrataciones cada vez son más costosas, un poco por encima de 3000€ en 2023
 frente a los casi 4000€ en 2025. Es decir, que en 2 años se ha incrementado casi un 30% más los costes de contratación
*/


-- 2) Empresas con mayor gasto


SELECT 
ADJ.ADJUDICATARIO, 
ADJ.TIPO_ADJUDICATARIO,
SUM(C.PRECIO) AS TOTAL_PRECIO,
COUNT(C.REFERENCIA) AS N_REGISTROS
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_ADJUDICATARIO AS ADJ
ON C.FK_ADJUDICATARIO = ADJ.PK_ADJUDICATARIO
GROUP BY ADJ.ADJUDICATARIO, TIPO_ADJUDICATARIO
ORDER BY TOTAL_PRECIO DESC
LIMIT 10


/*
En el top 10 de adjudicatarios con mayor importe acumulado aparecen únicamente empresas; predominan las sociedades 
limitadas según la clasificación disponible. Al comparar el gasto total con el número de referencias distintas,
se observa que ambas métricas no siguen necesariamente el mismo orden: algunas empresas acumulan un importe elevado
sin tener el mayor número de referencias. Esto sugiere que para grandes importes puede que no hayan habido un gran
número de registros
*/


-- 3.1) Áreas con mayor gasto (las 10 primeras)


SELECT N.CLAVE_NEGOCIADO, N.NEGOCIADO, SUM(PRECIO)
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_NEGOCIADO AS N
ON C.FK_NEGOCIADO = N.PK_NEGOCIADO
GROUP BY N.CLAVE_NEGOCIADO, N.NEGOCIADO
ORDER BY SUM(PRECIO) DESC
LIMIT 10


-- 3.2) Tipos de contrato con mayor gasto


SELECT TC.TIPO_CONTRATO, TC.DESCRIPCION_TIPO_CONTRATO AS DESCRIPCION, SUM(PRECIO) AS PRECIO_TOTAL
FROM MODELING.FACT_CONTRATOS
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = FK_TIPO_CONTRATO
GROUP BY TC.TIPO_CONTRATO, TC.DESCRIPCION_TIPO_CONTRATO
ORDER BY PRECIO_TOTAL DESC


-- 4) Patrones a investigar
-- 4.1) Contratos que superan el límite de precio:


-- Para los contratos que no son de obra:


SELECT REFERENCIA, TC.TIPO_CONTRATO, PRECIO 
FROM MODELING.FACT_CONTRATOS
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = FK_TIPO_CONTRATO
WHERE PRECIO > 15000 AND TIPO_CONTRATO != 'A'
ORDER BY PRECIO DESC


-- Para los contratos de obra: 


SELECT REFERENCIA, TC.TIPO_CONTRATO, PRECIO 
FROM MODELING.FACT_CONTRATOS
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = FK_TIPO_CONTRATO
WHERE PRECIO > 40000 AND TIPO_CONTRATO = 'A'
ORDER BY PRECIO DESC


-- 4.2) Adjudicatarios que más aparecen por tipo de contrato:


-- 4.3) Las empresas con más gasto son las que más contratos tienen?

