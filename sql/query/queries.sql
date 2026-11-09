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
COUNT(*) AS N_CONTRATOS
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_ADJUDICATARIO AS ADJ
ON C.FK_ADJUDICATARIO = ADJ.PK_ADJUDICATARIO
GROUP BY ADJ.ADJUDICATARIO, TIPO_ADJUDICATARIO
ORDER BY TOTAL_PRECIO DESC
LIMIT 10


/*
En el top 10 de adjudicatarios con mayor importe acumulado aparecen únicamente empresas; predominan las sociedades 
limitadas según la clasificación disponible. Si se compara el gasto total con el número de contratos asignados a 
cada empresa, se observa que no sigue la tendencia del ranking, es decir, las empresas con más importe no necesariamente
son las que más contratos se han adjudicado. Por lo que para grandes importes no necesariamente hay un gran número de
contratos, y viceversa, contratos con importes pequeños pueden significar un gran importe total debido a que hay 
un gran número de registros.
*/


-- 3.1) Áreas con mayor gasto (las 10 primeras)


SELECT 
N.CLAVE_NEGOCIADO, 
N.NEGOCIADO, 
ROUND(SUM(PRECIO)/1000000, 2) AS PRECIO_TOTAL, 
COUNT(*) AS N_CONTRATOS
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_NEGOCIADO AS N
ON C.FK_NEGOCIADO = N.PK_NEGOCIADO
GROUP BY N.CLAVE_NEGOCIADO, N.NEGOCIADO
ORDER BY PRECIO_TOTAL DESC
LIMIT 10


/*
El departamento que concentra más gasto es el de Servicios Generales de CI (3,83 millones de euros) seguido del
departamento de Gestión de Deportes (3,62 millones de euros). Aunque ambos tengan casi el mismo gasto, el número 
de contratos adjudicados al departamento de Servicios Generales de CI son 1368 frente a los 598 del departamento
de Gestión de Deportes. Por lo que los contratos del departamento de Gestión de Deportes tienen un importe más
elevado que los de Servicios Generales CI.
*/


-- 3.2) Tipos de contrato con mayor gasto


SELECT TC.TIPO_CONTRATO, TC.DESCRIPCION_TIPO_CONTRATO AS DESCRIPCION, SUM(PRECIO) AS PRECIO_TOTAL, COUNT(*) AS N_CONTRATOS
FROM MODELING.FACT_CONTRATOS
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = FK_TIPO_CONTRATO
GROUP BY TC.TIPO_CONTRATO, TC.DESCRIPCION_TIPO_CONTRATO
ORDER BY PRECIO_TOTAL DESC


/*
Analizando los gastos por tipo de contrato, destaca claramente los contratos con la categoría de servicios con
más de 15 millones de euros totales frente a los 6,21 de obras y 5,22 de suministros. En cuanto al número de contratos
de cada tipo, los servicios ascienden a 4661 mientras que las obras solamente 308. Esto se debe a que el límite legal
para los contratos de obra son mucho más altos que los de servicios y suministros (40.000 vs. 15.000), por lo que 
las obras será más fácil que el gasto total sea alto con pocos contratos.
*/


-- 4) Patrones a investigar
-- 4.1) Contratos que superan el límite de precio:


SELECT TC.TIPO_CONTRATO, COUNT(C.REFERENCIA) AS N_CONTRATOS, ROUND(AVG(C.PRECIO), 2) - TC.UMBRAL AS IMPORTE_EXTRA
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = FK_TIPO_CONTRATO
WHERE PRECIO > UMBRAL
GROUP BY TC.TIPO_CONTRATO, TC.UMBRAL
ORDER BY TC.TIPO_CONTRATO


/*
Buscando si hay algún registro de contratos con importes superiores al umbral legal, el resultado es sorprendente:
Hay un total de 475 contratos que superan ese límite distribuidos en: 327 contratos de suministros, 73 para obras, 
62 para los contratos de servicios y 13 para otro tipo de contratos. 
El exceso medio por encima del umbral es de: 6322.46 euros para los contratos de obra, 2164.28 euros para 
los servicios, 2409.34 euros para suministros y 2961.43 euros para otro tipo de contratos. Comparando estos valores,
se obtiene que en cualquier caso tanto para contratos con limite de 40000 euros como para los que tienen 15000 euros
de límite, el exceso medio que los supera es de alrededor un 16% aproximadamente.
*/


-- 4.2) Contratos cercanos al umbral legal >= 95%:


SELECT C.REFERENCIA, ADJ.ADJUDICATARIO, N.NEGOCIADO, C.PRECIO, ROUND(C.PRECIO / TC.UMBRAL * 100, 2) AS PCT_UMBRAL
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_ADJUDICATARIO AS ADJ
ON ADJ.PK_ADJUDICATARIO = C.FK_ADJUDICATARIO
LEFT JOIN MODELING.DIM_NEGOCIADO AS N
ON N.PK_NEGOCIADO = C.FK_NEGOCIADO
LEFT JOIN MODELING.DIM_TIPO_CONTRATO AS TC
ON TC.PK_TIPO_CONTRATO = C.FK_TIPO_CONTRATO
WHERE 95 <= PCT_UMBRAL <= 100
ORDER BY PCT_UMBRAL DESC


/*
En este rango hay un total de 63 resultados, de los cuales 6 coinciden con el tope máximo definido.
*/

-- Caso a estudiar a futuro: PALACIO EDREIRA , FERNANDO (3 contratos por el mismo importe 96,8% cerca del umbral)


-- 4.2) Estacionalidad de los contratos:


SELECT F.MES, F.NOMBRE_MES, COUNT(*) AS N_CONTRATOS, ROUND(SUM(C.PRECIO)/1000000, 2) AS TOTAL_PRECIO
FROM MODELING.FACT_CONTRATOS AS C
LEFT JOIN MODELING.DIM_FECHAS AS F
ON C.FK_FECHA = F.PK_FECHA
GROUP BY F.MES, F.NOMBRE_MES
ORDER BY F.MES 


/*
Aunque tampoco hay grandes picos de contratación, el máximo está en noviembre con un total de 940 contratos
y un gasto total de 2,96 millones de euros. El mes de octubre, es el segundo mes que más contratos concentra (840)
y concentra un mayor gasto que noviembre: 3,47 millones de euros. En agosto se encuentra el mínimo de contrataciones,
coincidiendo con el parón de vacaciones.
*/








-- 4.2) Adjudicatarios que más aparecen por tipo de contrato:


-- 4.3) Las empresas con más gasto son las que más contratos tienen?

