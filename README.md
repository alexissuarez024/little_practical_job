## Introducción
Este es un trabajo práctico en donde elaboro un mini pipeline el cual se conecta a la API de mercadolibre y extrae ciertos productos a través de un código de producto (en este caso, microondas)
Luego es necesario cargar estos datos en una base de datos con una estructura definída
Y por último, si el precio total de los productos excede cierto monto (el cual estableci de manera arbitraria para motivos del trabajo) debera mandar un mail a cierta persona para dar aviso del hecho.
Cada una de estas tareas estan siendo seguidas con Airflow, de igual forma puede correr el script desde la consola para obtener los mismos resultados.

## Aclaración
Estos ejemplos estan pensados y establecidos en un ambiente local, por ende, las estructuras y ejemplos mostrados a continuación dan como resultado una respuesta local.
En ella se utiliza una base de datos Postgres que, de igual forma, está alojada localmente.
El ambiente de Airflow también está alojado localmente. Éste ultimo fue levantado a través de  Docker Compose. Si quiere saber como levantar un ambiente Airflow de manera local visite este enlace [Airflow with Docker-Compose](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html "Airflow with Docker-Compose")

### Paso 1
Debemos generar, para mayor comodidad y evitar tener errores con otras librerias, un ambiente virtual.

> python -m venv nombreDelAmbiente


Luego debemos activar el ambiente

> source nombreDelAmbiente/bin/activate

Una vez dentro instalaremos las siguientes librerias utilizadas:
> pip install nombreLibreria


- requests
- json
- datetime
- os
- pandas 
- yagmail 
- psycopg2

### Paso 2
En la importación de librerias

```python
import requests
import json
import datetime
import os
import pandas as pd
import yagmail 
import psycopg2
from zona_horaria import rosario_date
from config import configConection, configUser,configPassword,configAddress
```

> *zona_horaria contiene una variable 'rosario_date' que devuelve la fecha del dia actual.
config contiene los datos que son necesarios para el envio del mail y la conexión, estos datos debe reemplazarlos como dice a continuación*

### Paso 3
- Reemplace los valores con datos suyos para que funcione el pipeline
En la siguiente linea ubicada en la función *data_review*, corrija los datos de email:

```python
yag = yagmail.SMTP(user = 'yourUser', password = 'yourPassword')
yag.send('yourAddress', asunto, mensaje , attachments=[archivo]) 

```
> *- Si desea saber más sobre la libreria *yagmail*, visite este enlace [Yagmail ](https://github.com/kootenpv/yagmail "Yagmail ")*

> - Importante: Para que el mail pueda ser enviado desde su usuario, deberá configurar su cuenta gmail desde su cuenta de Google. Debe activar la 'verificación en 2 pasos' para que de ésta forma le genere una contraseña la cual deberá usar como password.

Los parámetros utilizados para la conexión debe pasarlos de la siguiente forma:

```python
 conn = psycopg2.connect(
 		host = 'yourHost',
         port = '5432', # puerto por defecto de postgres
		 user = 'yourUser',
		 password = 'yourPassword',
		 database = 'yourDatabase'
 )
 
```
> *- Si desea saber más sobre ésta conexión postgres, visite el siguiente enlace [Conection to Postgres](https://dungeonofbits.com/conectar-con-una-base-de-datos-postgresql-desde-python.html#:~:text=Conectar%20con%20una%20base%20de%20datos%20PostgreSQL%20desde,datos%20en%20PostgreSQL%20desde%20Python%3A%20...%20M%C3%A1s%20elementos "Conection to Postgres")*



Al final de las funciones si desea correr el pipeline desde consola, descomente la siguiente linea:

```python
if __name__ == '__main__':
    createTablePosg()
    main()
    data_review()
```

### Correr con Airflow
Si desea usar el script mediante Airflow, debera levantar previamente los containers correspondientes que necesita el ambiente de Airflow para funcionar localmente. 
Una vez hecho ese paso, debera generar una conexión desde el webserver de Airflow en la pestaña  "connections".
Ahi debera rellenar los datos que correspondan a los de su máquina, como es el host, base de datos, puerto, etc.
Airflow genera un usuario propio para acceder a su webserver, este usuario se genera por default como "user = airflow, password = airflow". Debera tener en cuenta esto ya que al generar la conexion debe pasar esos datos correspondientemente.

Una vez generada las conexiones necesarias y configurado el ambiente, dirijase a la sección:

```python
"""""
The logic of the DAG
"""""
```
 Y por último en la parte de:
 
 ```python
    create_table = PostgresOperator(
        task_id='Creation_table_postgres',
        postgres_conn_id = 'postgres_localhost',
        sql = """
                CREATE TABLE IF NOT EXISTS mini_pipeline
                        (
                            id VARCHAR(255),
                            site_id VARCHAR(255),
                            title VARCHAR(255),
                            price INTEGER,
                            sold_quantity INTEGER,
                            thumbnail VARCHAR(255),
                            created_date VARCHAR(255)
                        );

        """
    )
 ```
 'postgres_conn_id' debe coincidir con el id que le dio a la conexión mediante el webserver úbicado en la pestaña *connections*.
 
 ## Conclusión

Debe tener en cuenta que cada máquina tiene diferentes configuraciones y , como a mí, si no le funcionan las correcciones apuntadas anteriormente debera visitar diferentes repositorios o páginas para solucionar los inconvenientes que le puedan llegar a surgir!
Es algo que siempre suele pasar, pero todo tiene solución.
Es un pequeño trabajo que realice repasando y aplicándo conocimientos viejos y nuevos, estoy abierto a cualquier cambio y/o correcciones para el código. 
Como todos, sigo aprendiendo día a día y me encanta y disfruto de esto! 
Un saludo :)