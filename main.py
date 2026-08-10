# PRUEBA DE GITHUB

"""
Punto de entrada de la aplicación.
Inicializa la base de datos (capa de datos) y lanza la interfaz
gráfica (capa de presentación).
"""
from capas.datos.conexion_bd import inicializar_esquema
from capas.presentacion.app_gui import iniciar_aplicacion

if __name__ == "__main__":
    inicializar_esquema()
    iniciar_aplicacion()

    DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "1011094395"
DB_NAME = "acceso_militar"