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
    "1_keyboard_utils.sh": """# Configuración de Teclado
set_latam() { setxkbmap latam 2>/dev/null && echo -e "\\e[1;32m[+] Teclado: LATAM\\e[0m"; }
set_es() { setxkbmap es 2>/dev/null && echo -e "\\e[1;32m[+] Teclado: ES\\e[0m"; }
set_us() { setxkbmap us 2>/dev/null && echo -e "\\e[1;32m[+] Teclado: US\\e[0m"; }
""",
    
    "2_system_utils.sh": """# Utilidades de Sistema e Historial
hclear() {
    unset HISTFILE
    export HISTSIZE=0
    rm -f ~/.bash_history ~/.zsh_history ~/.python_history 2>/dev/null
    history -c 2>/dev/null
    clear
    echo -e "\\e[1;33m[*] Modo Incógnito Activado (Historial erradicado)\\e[0m"
}

update_os() {
    sudo apt update && sudo apt dist-upgrade -y && sudo apt autoremove -y && sudo apt autoclean -y
    echo -e "\\e[1;32m[+] Sistema actualizado. Reiniciando en 5s...\\e[0m"
    sleep 5 && sudo reboot
}
""",

    "3_workspace_utils.sh": """# Gestión de Entorno y Directorios
mkt() {
    mkdir {nmap,content,exploits,scripts} 
}

mkvenv() {
    local name="${1:-.venv}"
    python3 -m venv "$name" && source "$name/bin/activate" && pip install --upgrade pip
    [ -f "requirements.txt" ] && pip install -r requirements.txt
    echo -e "\\e[1;32m[+] Entorno '$name' activado.\\e[0m"
}
""",

    "4_pentest_arsenal.sh": """# Herramientas de Pentesting
whichSystem() {
    local ttl=$(ping -c 1 "$1" 2>/dev/null | grep -oP 'ttl=\\d+' | cut -d= -f2)
    if [ -z "$ttl" ]; then echo -e "\\e[1;31m[!] Host inalcanzable\\e[0m"; return 1; fi
    if [ "$ttl" -le 64 ]; then echo -e "\\e[1;32m[+] $1 -> Linux (TTL $ttl)\\e[0m"
    elif [ "$ttl" -le 128 ]; then echo -e "\\e[1;34m[+] $1 -> Windows (TTL $ttl)\\e[0m"
    else echo -e "\\e[1;33m[+] $1 -> Desconocido (TTL $ttl)\\e[0m"; fi
}

extractPorts() {
    if ! command -v xclip &> /dev/null; then echo "Falta xclip"; return 1; fi
    ports=$(cat "$1" | grep -oP '\\d{1,5}/open' | awk '{print $1}' FS='/' | xargs | tr ' ' ',')
    echo "$ports" | tr -d '\\n' | xclip -sel clip
    echo -e "\\e[1;32m[+] Puertos copiados al portapapeles: $ports\\e[0m"
}
"""
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
    print("║  🛠️  INSTALADOR DE ARSENAL UNIVERSAL          ║")
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
