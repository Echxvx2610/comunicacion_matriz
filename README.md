# Analisis de material

Se tienen dos aplicaciones que tienen en comun la edicion de un archivo CSV el cual se utiliza como analisis de un no.parte la primera aplicacion se llama MFG.py la cual es la principal por asi decirlo, en ella se generan los registros para el CSV.
contiene operacion CRUD, como registrar,editar,eliminar etc. todo desde la misma app. como segunda aplicacion se tiene setuproom.py,esta app solo visualiza los registros que genera MFG permitiendole editar y recargar la info de la tabla. lo interesante en este caso es la implementacion de la libreria watchdog con la cual monitoreamos constantemente la modificacion del CSV notificando a MFG cuando este a sido alterado y asi poder hacer los cambios pertinentes.

## Galleria
![image](https://github.com/Echxvx2610/comunicacion_matriz/assets/99057175/d02a9930-f87f-4bd5-a2ec-6200f7d3c31f)

Img.1-Captura App MFG.py

![image](https://github.com/Echxvx2610/comunicacion_matriz/assets/99057175/c215d0a6-978d-4e10-85a5-ca785856733c)

Img.2-Captura App Setuproom.py

![image](https://github.com/Echxvx2610/comunicacion_matriz/assets/99057175/d5540378-7144-41af-a4dc-ae35cbacebed)

Img.3- Notificacion de cambios en tiempo real con sonido
