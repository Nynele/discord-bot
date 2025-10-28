# Bot de Moderación Avanzado para Discord

Este es un bot de moderación para Discord avanzado y funcional, construido con Python usando la librería `discord.py`. Utiliza las últimas características de Discord, como los comandos de barra diagonal (`/`) agrupados, e integra un sistema de moderación completo con registro en base de datos local (SQLite).

## Características

- **Comandos Agrupados:** Para una mayor organización, los comandos están agrupados por categorías (ej. `/moderacion kick`).
- **Sistema de Configuración:** Designa un canal de logs para registrar todas las acciones.
- **Moderación Completa:**
    - `/moderacion advertir`: Advierte a un usuario.
    - `/moderacion historial`: Muestra el historial de sanciones de un usuario.
    - `/moderacion kick`: Expulsa a un usuario del servidor.
    - `/moderacion ban`: Banea permanentemente a un usuario.
    - `/moderacion silenciar`: Silencia a un usuario por un tiempo determinado (ej. `1h`, `30m`).
- **Base de Datos Local:** No requiere configuración de bases de datos externas. Todo se guarda en un archivo `moderation.db`.
- **Organización por Módulos (Cogs):** El código está organizado de manera limpia y es fácilmente extensible.

## Requisitos

- Python 3.8 o superior.
- Una cuenta de Discord y un servidor donde tengas permisos de administrador.

## Guía de Instalación y Configuración

Sigue estos pasos para poner en funcionamiento el bot en tu servidor.

### 1. Clona o Descarga el Proyecto

Obtén los archivos del proyecto en tu máquina local.

### 2. Crea un Bot en el Portal de Desarrolladores de Discord

Si no sabes cómo hacerlo, sigue esta [guía oficial de Discord](https://discordpy.readthedocs.io/en/latest/discord.html).

- **Ve al Portal de Desarrolladores de Discord** y crea una "Nueva Aplicación".
- **Ve a la pestaña "Bot"** y haz clic en "Añadir Bot".
- **Obtén tu Token:** Debajo del nombre del bot, haz clic en "Reset Token" o "View Token" para copiar tu token. **¡Este token es secreto, no lo compartas con nadie!**
- **Activa los "Privileged Gateway Intents":** Asegúrate de que las siguientes opciones estén activadas en la misma pestaña de "Bot":
    - `SERVER MEMBERS INTENT`
    - `MESSAGE CONTENT INTENT` (Opcional, pero recomendado para futuras expansiones)

### 3. Configura tu Entorno

- **Crea un archivo `.env`** en la raíz del proyecto. Este archivo guardará tu token de forma segura.
- **Añade tu token al archivo `.env`:**

  ```
  DISCORD_TOKEN=AQUÍ_VA_TU_TOKEN_SECRETO
  ```

### 4. Instala las Dependencias

Abre una terminal en la carpeta del proyecto y ejecuta el siguiente comando para instalar las librerías de Python necesarias:

```bash
pip install -r requirements.txt
```

### 5. Invita al Bot a tu Servidor

- En el Portal de Desarrolladores, ve a la pestaña **"OAuth2" -> "URL Generator"**.
- Selecciona los siguientes scopes: `bot` y `applications.commands`.
- En "Bot Permissions", selecciona los permisos que necesitará el bot. Para un bot de moderación, se recomienda seleccionar **"Administrador"** para asegurar que todos los comandos funcionen correctamente.
- Copia la URL generada y pégala en tu navegador para invitar al bot a tu servidor.

## Cómo Ejecutar el Bot

Una vez completada la configuración, puedes iniciar el bot con el siguiente comando desde la raíz del proyecto:

```bash
python bot/main.py
```

Si todo está configurado correctamente, verás un mensaje en tu terminal indicando que el bot se ha conectado:

```
Logged in as TuNombreDeBot (123456789012345678)
------
Database initialized successfully.
Loaded cog: config.py
Loaded cog: moderation.py
Slash commands have been synchronized.
```

## Primeros Pasos en tu Servidor

1. **Crea un canal de logs:** Crea un canal de texto privado en tu servidor donde solo los moderadores puedan ver los mensajes (ej. `#moderacion-logs`).
2. **Configura el bot:** En cualquier canal, usa el comando `/configuracion canal_logs` para decirle al bot dónde debe registrar las acciones.
   ```
   /configuracion canal_logs canal:#moderacion-logs
   ```
3. **¡Listo!** Ya puedes empezar a usar todos los comandos de moderación. Por ejemplo:
   ```
   /moderacion advertir usuario:@UsuarioEjemplo razon:Spam
   /moderacion kick usuario:@UsuarioEjemplo razon:Incumplimiento de normas
   ```