# Sistema de Gestión de Boyas y Sensores (Django)

Aplicación web desarrollada en Django para el monitoreo, administración y control de boyas y sensores, con control de acceso por roles (administradores y usuarios propietarios).

---

## 🚀 Guía de Instalación y Ejecución

Sigue estos pasos en tu terminal para descargar el código, instalar las dependencias necesarias y poner en marcha el proyecto en tu entorno local.

### 1. Clonar el repositorio
Descarga el código fuente del proyecto en tu computadora:
```bash
git https://github.com/exequieldev/aquasmart.git
cd aquasmart
```

### 2. Crear y activar el entorno virtual
Es obligatorio utilizar un entorno virtual para aislar las dependencias de Python:

* **En Windows (CMD o PowerShell):**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

* **En macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar las dependencias del proyecto
Con el entorno virtual activo, instala las librerías necesarias especificadas en el archivo de configuración:
```bash
pip install -r requirements.txt
```

### 4. Aplicar las migraciones de la base de datos
Prepara la base de datos local ejecutando las migraciones de Django:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear un Superusuario (Administrador)
Como el sistema valida permisos de superusuario para ciertas acciones, es necesario crear una cuenta de administrador para poder iniciar sesión y probar la aplicación:
```bash
python manage.py createsuperuser
```
*(Sigue las instrucciones en pantalla para ingresar tu nombre de usuario, correo y contraseña).*

### 6. Ejecutar el servidor de desarrollo
Finalmente, arranca el servidor local de Django para empezar a usar el proyecto:
```bash
python manage.py runserver
```

¡Listo! Abre tu navegador web y entra a **`http://127.0.0.1:8000/`** para ejecutar y utilizar el sistema.
