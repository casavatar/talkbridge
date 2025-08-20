# TalkBridge Desktop - Configuration & Setup Scripts

Este directorio contiene todos los scripts y archivos de configuración necesarios para ejecutar TalkBridge Desktop.

## 📁 Archivos Incluidos

### Scripts de Instalación y Ejecución

- **`setup_conda_desktop.py`** - Script automatizado para crear el entorno Conda
- **`run_desktop_conda.bat`** - Script de inicio para Windows
- **`run_desktop_conda.sh`** - Script de inicio para Linux/macOS

### Archivos de Configuración

- **`environment-desktop.yml`** - Configuración principal del entorno Conda
- **`environment-desktop-simple.yml`** - Configuración simplificada (fallback)
- **`config.yaml`** - Configuración de la aplicación

## 🚀 Uso Rápido

### Directamente desde config

**Windows:**

```cmd
cd config
run_desktop_conda.bat
```

**Linux/macOS:**

```bash
cd config
./run_desktop_conda.sh
```

## 🔧 Funcionamiento

1. **Verificación de Conda** - Comprueba si Conda está instalado
2. **Creación de Entorno** - Si no existe, crea el entorno `talkbridge-desktop`
3. **Activación** - Activa el entorno automáticamente
4. **Información** - Muestra comandos disponibles para ejecutar la aplicación

## 📋 Comandos Disponibles (una vez activado el entorno)

```bash
# Iniciar aplicación desktop
python src/desktop/main.py

# Ejecutar todos los tests
pytest src/desktop/

# Desactivar entorno
conda deactivate
```

## ⚙️ Configuración

Edita `config.yaml` para personalizar:

- URL del servidor Ollama
- Modelo de AI a utilizar
- Configuración de audio
- Configuración de UI
- Nivel de logging

## 🔍 Resolución de Problemas

Si encuentras problemas:

1. Verifica que Conda esté instalado: `conda --version`
2. Elimina el entorno existente: `conda env remove -n talkbridge-desktop`
3. Ejecuta el script nuevamente

## 📝 Notas

- Los scripts detectan automáticamente el sistema operativo
- Se prefiere `environment-desktop-simple.yml` si existe
- Todos los paths son relativos al directorio raíz del proyecto
