# 🏴‍☠️ Red Team Arsenal & Environment Builder

![Bash](https://img.shields.io/badge/Language-Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)
![Python](https://img.shields.io/badge/Language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Kali](https://img.shields.io/badge/OS-Kali%20Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white)

Este repositorio contiene mi entorno de trabajo automatizado para auditorías de seguridad y despliegues de Red Team. He desarrollado un instalador en Python (`install_arsenal.py`) que configura dependencias, establece un entorno virtual seguro (PEP 668) y despliega una suite de utilidades personalizadas de forma agnóstica al sistema operativo (soporta tanto usuarios estándar como `root`).

## 🚀 Características Principales (Mis Desarrollos)

He creado varias utilidades para agilizar mis auditorías y asegurar mi entorno:

*   **`hclear`**: Un script de amnesia total que destruye el historial físico de la terminal, limpia la RAM de la shell actual y desactiva las variables de registro. Ideal para mantener el sigilo.
*   **`update_os`**: Un actualizador profundo del sistema que gestiona repositorios, limpieza de caché y purga de dependencias huérfanas en un solo comando.
*   **`mkvenv`**: Automatización segura de entornos virtuales en Python que evita romper el sistema base de Kali/Debian, actualiza `pip` y detecta archivos `requirements.txt` automáticamente.
*   **Gestión de Teclado**: Funciones rápidas (`set_latam`, `set_us`, `set_es`) para alternar distribuciones de teclado en entornos gráficos sin perder tiempo en menús.

## 🤝 Créditos y Atribuciones (S4vitar Style)

Este entorno de trabajo está inspirado en las metodologías de agilidad y eficiencia del *Pentesting*. Por ello, quiero dejar estipulado y dar el crédito correspondiente a **Marcelo Vázquez (S4vitar)**, creador de la academia Hack4u y referente en la comunidad de ciberseguridad, por la lógica y el diseño de las siguientes herramientas indispensables que he integrado en la categoría de *Pentest Arsenal*:

*   **`extractPorts`**: Funcionalidad icónica diseñada por S4vitar para extraer, limpiar y copiar al portapapeles de manera instantánea los puertos abiertos desde archivos "grepables" de Nmap (`.gnmap`).
*   **`whichSystem`**: Herramienta de enumeración pasiva basada en la técnica de S4vitar que evalúa el TTL (Time To Live) de las trazas ICMP para determinar si el sistema objetivo es Linux o Windows.
*   **`mkt` (Make Target)**: Lógica de creación ágil de entornos de trabajo que despliega instantáneamente la estructura de carpetas estándar (`nmap`, `content`, `exploits`, `scripts`) recomendada por S4vitar para la resolución de máquinas (HTB, VulnHub, etc.).

> *"El conocimiento es libre y en la comunidad nos apoyamos mutuamente para ser más eficientes."* - Puedes encontrar el trabajo original de S4vitar en su [GitHub](https://github.com/s4vitar) o en [Hack4u](https://hack4u.io/).

El resto de herramientas (`hclear`, `update_os`, `mkvenv` y utilidades de teclado) son desarrollos propios creados para complementar este flujo de trabajo.


## ⚙️ Instalación Universal (Multi-Shell & Multi-User)

El instalador detecta dinámicamente tu usuario y configura tanto `.zshrc` como `.bashrc`, garantizando que las herramientas estén disponibles incluso al escalar privilegios con `sudo su`.
```bash
git clone [https://github.com/TU_USUARIO/red-team-arsenal.git](https://github.com/TU_USUARIO/red-team-arsenal.git)
cd red-team-arsenal
sudo python3 install_arsenal.py
source ~/.zshrc # o ~/.bashrc
