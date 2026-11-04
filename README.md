# Análisis de las Contrataciones Menores Ayuntamiento de A Coruña

## Índice

  - [Introducción](#introducción)
  - [Proceso ETL](#proceso-etl)
    - [Obtención de los datos](#obtención-de-los-datos)
    - [Contexto incial de los datos](#contexto-incial-de-los-datos)
    - [Normalización de los archivos](#normalización-de-los-archivos)
    - [Unificación de los datos](#unificación-de-los-datos)
    - [Limpieza y normalización de los datos](#limpieza-y-normalización-de-los-datos)
      - [Exploración](#exploración)
      - [Limpieza inicial](#limpieza-inicial)
        - [Eliminación de espacios](#eliminación-de-espacios)
        - [Conversión de tipo de dato: cadenas de texto](#conversión-de-tipo-de-dato-cadenas-de-texto)
        - [Conversión de tipo de dato: numérico](#conversión-de-tipo-de-dato-numérico)
        - [Conversión de tipo de dato: datetime](#conversión-de-tipo-de-dato-datetime)
        - [Gestión de duplicados](#gestión-de-duplicados)
      - [Corrección de columnas específicas](#corrección-de-columnas-específicas)
        - [NIF](#nif)
        - [Adjudicatario](#adjudicatario)
        - [Negociado](#negociado)
      - [Ejecución de la limpieza](#ejecución-de-la-limpieza)
    - [Ejecución del proceso ETL](#ejecución-del-proceso-etl)

## Introducción

Este proyecto desarrolla una pipeline end-to-end de los datos sobre contrataciones menores en el Ayuntamiento de A Coruña en el periodo 2023-2026. El proyecto aborda desde la extracción, limpieza y carga de los datos (proceso ETL) hasta el modelado en Snowflake y su análisis con PowerBi.

## Proceso ETL

### Obtención de los datos

Los datos se han descargado manualmente a través del portal de la administración pública

### Contexto incial de los datos

La administración púlbica organiza los datos por trimestres, y al final de cada año añade un anexo con contratos que no se añadieron a los trimestres. El tipo de archivo en el que guardan los datos es un .ods (LibreOffice). En cuanto al formato que utilizan, en los primeros trimestres de 2023 utilizan un formato, a partir del tercer trimestre ya lo estandarizan para el resto. El anexo de 2023 tiene un formato específico.

Los datos están organizados en 8 columnas: Referencia (identificador único para cada contrato), Tipo de contrato (clasifica el contrato dependiendo de su objeto), Objeto (breve descripción de lo que se va a hacer), Fecha (fecha en la que se adjudica el contrato), NIF (identificador de la persona física o empresa adjudicataria), Adjudicatario (persona física o empresa que cubre la necesidad), Precio (presupuesto de la necesidad cubierta) y Negociado (entidad pública que genera la oferta y a la que se destina los fondos). Cada fila representa un registro de contrato.

### Normalización de los archivos

Con el script ```src/transform/processed.py``` el objetivo es conseguir un formato normalizado para todos los ficheros obtenidos. En primer lugar las funciones ```set_headers_format_x(df)``` se encargan de colocar correctamente los encabezados (columnas) y eliminar las filas que no aportan ningún tipo de información:

 - ```set_headers_format_1(df)```: se encarga de normalizar el formato estándar de los ficheros
 - ```set_headers_format_2(df)```: se encarga de normalizar el formato para los dos primeros trimestres de 2023
 - ```set_headers_format_3(df)```: se encarga de normalizar el formato para el anexo de 2023

Para automatizar la aplicación de estas funciones dependiendo del archivo, en el script ```src/utils/utils.py``` se define la función ```files_format()``` que recorre todos los archivos que tengan el formato .ods donde se almacenan los datos brutos (```data/bronze```) y asigna a cada archivo la función necesaria para su normalización de formato.

Finalmente la función ```process_file()``` aplica las funciones de estandarización para cada archivo y a través de una lista estandariza los nombres de las columnas. Los DataFrarmes finales se exportan como .csv en la ruta para datos procesados (```data/silver```). 

### Unificación de los datos

Tras el punto anterior ya tenemos los datos con un formato único y estándar para todos, es decir, que todos tienen la fila de las columnas en primera posición y con los mismos nombres, y el primer registro de contratación en la fila siguiente, algo así:

| referencia | tipo_contrato | objeto | fecha | nif | adjudicatario | precio | negociado |
|---|---|---|---|---|---|---:|---|
| 000/2023/100 | C | FAC 142. SUBMINISTRACIÓN CESTÓN GRANDE FLORES, ENVIO REALACIÓNS PÚBLICAS -PROTOCOLO | 2023-09-19 00:00:00 | ***8447** | NAVEIRAS GOMEZ, ELENA | 190.0 | ALCALDÍA |
| 000/2023/33 | E | SERVIZO DE CATERING PARA RECEPCIÓN INSTITUCIONAL | 2023-03-07 00:00:00 | B42947440 | ATLANTICO CONICNA NOMADA S.L. | 3780.0 | ALCALDÍA |

Con la función ```consolidate_files()``` (```src/transform/consolidate.py```) se unen todos los csv en un único fichero .csv guardado en ```data/silver/consolidated```. El unificar todos los ficheros en uno único, se evita hacer bucles para recorrer todos los archivos en la limpieza y normalización de los datos.

### Limpieza y normalización de los datos

#### Exploración

El fichero ```src/transform/clean.py``` contiene todas las funciones para limpiar y normalizar los datos. La función ```explore()``` da una visión inical de la calidad de los datos obtenidos:

 - Primeras filas: muestra las primeras filas de los datos
 - Dimensiones: devuelve el número de filas y columnas (7695 x 8)
 - Tipos de datos: tipo de dato para cada columna
 - Valores nulos: número de campos vacíos
 - Porcentaje de nulos: representación de los valores nulos en el total
 - Duplicados: valores completamente idénticos
 - Valores únicos por columna: número de valores diferentes que hay en cada columna
 - Distribuciones: estadísticas iniciales básicas
  
#### Limpieza inicial

Una vez entendidos los datos que obtenidos y las características principales, se puede empezar a hacer una limpieza inicial. 

En primer lugar, se asignará a cada columna el tipo de dato más adecuado. Para hacer esto, antes hay que hacer algunos ajustes para que pandas pueda identificar correctamente cada tipo de dato.

##### Eliminación de espacios

Las entradas de los datos, a menudo suelen tener espacios antes o despues del valor introducido. Esto no afecta para una persona que está leyendo los datos. Sin embargo, pandas interpretará esas casillas como cadenas de texto (str). La función ```clean_text()``` recorre todos los registros por columnas y elimina esos espacios.

##### Conversión de tipo de dato: cadenas de texto

En las columnas que tenemos en los datos las columnas cuyos datos deberían de ser cadenas de texto serían las siguientes:

 - Referencia (referencia)
 - Tipo de Contrato (tipo_contrato)
 - Objeto (objeto)
 - NIF (nif)
 - Adjudicatario (adjudicatario)
 - Negociado (negociado)

A todas estas columnas se les asignará el tipo de dato de cadena de texto y además se reescriben en mayúsculas para una mayor legibilidad. La función que se encarga de realizar estos cambios es ```clean_categories()```.

##### Conversión de tipo de dato: numérico

A la columna de precio se le debe asignar el tipo de dato numérico con dos decimales (float64). La función ```clean_prices()``` se encarga precisamente de esto.

Sin embargo, hay que contemplar ciertas cosas antes de forzar la conversión. 

En python, los números decimales se separan por ```.``` y a las unidades de millar no se las separa. En el formato numérico europeo los millares se separan por ```.``` y los decimales por ```,```.
Para cambiar este formato numérico, la función ```clean_prices()``` localiza los número que contengan una coma y después aplica el cambio de formato númerico.

Al cambiar estos formatos, aún quedan dos valores por ajustar. Son datos que tienen un formato específico para cada caso:

 - En el primer caso tenemos ```18.000,00 €```, en este caso habría que eliminar el símbolo del euro para poder después convertirlo a número.

 - En el otro caso, tenemos lo siguiente: ```22.209,07€ (2023). 31.882,29 € (2024)```. Este caso puede estar sujeto a interpretación, ya que se puede duplicar el registro para cada año con los importes indicados, o dejar en un único registro con la suma de ambos. En mi caso, ya que se corresponde con el mismo registro de contrato, opté por el segundo caso.

##### Conversión de tipo de dato: datetime

La función ```clean_dates()``` cambia el tipo de dato a datetime. En los registros las fechas tienen dos formatos:

 - Formato ISO: Año-mes-día
 - Formato Europeo: Día/mes/año

Así que se crean dos series: una para las fechas con el primer formato y otra para el segundo. Cada serie solo cambia solo las fechas de su formato y deja las otras con valores nulos. Así la serie creada para las fechas en formato ISO cambiará las fechas con ese formato y dejará nulo las del formato europeo. La serie para las fechas en formato europeo hará lo mismo pero al revés. Así al cruzar esas dos series (sustituir los valores nulos de una serie por los valores de la otra) obtenemos la columna de las fechas con su tipo de dato correspondiente.

No obstante, tras cambiar los formatos y analizar esta columna, obtenemos un valor atípico (una fecha correspondiente a 2022, cuando los datos analizados van del 2023-2026). Investigando y analizando las referencias contractuales más próximas a ese registro, se concluye que se trata de un error en el registro de origen, ya que las referencias similares corresponden a la franja del primer trimestre de 2023. Para resolver esto, simplemente se le suma un año a esa fecha.

##### Gestión de duplicados

En la exploración inicial, se obtiene que no existen valores duplicados. Pero esto significa que no hay registros con los mismos valores para todas las filas, es decir, que no está contemplando si hay contratos con el mismo registro con diferencias en la ortografía o idioma, si tienen distinta fecha o si tienen distinto precio. Analizando los posibles duplicados ocultos se obtienen 12 parejas duplicadas que se pueden clasificar en tres casos:

 1) Misma referencia pero el objeto o adjudicatario se escriben de forma diferente
 2) Misma referencia e importe pero en fechas diferentes
 3) Misma referencia con importe y fechas diferentes

En este caso, solo el caso 1 se manejará como valor duplicado. El caso 2 puede corresponder a contrataciones periódicas que pueden ser objeto de análisis. Mientras que el caso 3 puede deberse a contrataciones plurianuales asociadas al mismo contrato (como lo que se encotró en la limpieza de los precios).

Con la función ```clean_duplicates()``` se actua sobre los duplicados del caso 1, quedándose con el valor que más se repite y, en caso de que haya un empate, se queda con el primer registro.

#### Corrección de columnas específicas

##### NIF

Analizando los NIFs se observa que tienen diferentes formatos. Esto se puede clasificar como:

 - Empresas con NIF español: Letra + 8 números
 - Empresas con NIF extranjero: identificador del país + números
 - NIF de personas físicas: `***XXX**`

Es decir, que los NIF con 9 dígitos tienen un formato correcto de primeras, pues corresponden a empresas con NIF español. Así que las que se van a analizar son los que tienen una longitud diferente.

Analizando los NIF con una longitud diferente a 9 dígitos, se ve que la gran mayoría se corresponden a NIF de empresas extranjeras. Sin embargo, hay algún valor con errores de escritura:

1) Persona física: hay un registro con el formato `**XXX**`, así que para arreglarlo hay que añadir un `*` al principio.
2) Tres casos de NIF mal escritos, se sustituye por el que más se repite.

La función ```clean_nif()``` se encarga de corregir esos errores en los NIF.

##### Adjudicatario

El objetivo principal de la función ```clean_adjudicatario()``` es unificar el nombre de los adjudicatarios que se pueden estar repitiendo escritos de formas distintas, ej: ATLANTICO CONICNA NOMADA S.L. / ATLANTICO CONICNA NOMADA SL 

##### Negociado

Los negociados en los datos vienen escritos como: Nombre + (Código identificativo). No todos los negociados tienen un codigo identificativo al final del nombre. 

Con la función ```clean_negociados()``` se hacen tres cosas:

1) Unificar los nombres de los negociados en la columna ```negociado```, sin código.
2) Crear una nueva columna ```negociado_cod``` con los códigos identificativos de los negociados, si no tienen queda como valor nulo.
3) Crear una nueva columna ```clave_negociado``` con los códigos negociados y a los que no tienen les asigna su propio nombre.

#### Ejecución de la limpieza

Con la función ```transform_files()``` se ejecutan las funciones de exploración y limpieza de datos, para finalmente guardar el archivo limpio y preparado para su modelado en ```data/gold/cleaned```.

### Ejecución del proceso ETL

Para ejecutar el proceso de ETL se crea una función ```launcher()``` que se importa al fichero ```src/main.py``` para que al ejecutar este script se ejecute todo el programa.














