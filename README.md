# Banco de Pruebas Automatizado para Equipos de Teleprotección (TFG)

[cite_start]Este repositorio contiene el código fuente para el TFG: "Diseño y Desarrollo de un Banco de Pruebas Automatizado para Pruebas de Robustez de Equipos de Teleprotección en Subestaciones Eléctricas"[cite: 10, 19].

[cite_start]El proyecto expande un framework de pruebas funcionales previo [cite: 47, 65] [cite_start]para crear un sistema integral que valida la robustez de la unidad de teleprotección **ZIV TPU-1**[cite: 46]. [cite_start]El objetivo final es combinar la automatización web (configuración) con pruebas de Hardware-in-the-Loop (HIL) para simular las condiciones electromagnéticas adversas de una subestación eléctrica[cite: 50, 69].

##  Estado actual: En Desarrollo (Fase 1)

[cite_start]Actualmente, el proyecto se encuentra en la **Fase 1: Desarrollo y Mejora del Software de Control y Pruebas**.

El enfoque principal en esta fase es:
* [cite_start]Profesionalizar la interfaz gráfica de usuario (GUI) existente[cite: 86].
* [cite_start]Implementar la visualización de datos en tiempo real, como traps SNMP y eventos del registro cronológico[cite: 87].
* Preparar la arquitectura de software para la futura integración del hardware (Fase 2).

## Tecnologías Principales

Este proyecto integra un stack de software y hardware:

* [cite_start]**Lenguaje:** Python 3.x [cite: 218]
* [cite_start]**Framework de Pruebas:** Robot Framework [cite: 219]
* [cite_start]**Automatización Web:** Selenium Library [cite: 220]
* [cite_start]**GUI:** Tkinter (CustomTkinter) [cite: 222]
* [cite_start]**Control de Hardware (Futuro):** Raspberry Pi 4 [cite: 229] [cite_start]y PySerial [cite: 221]
* [cite_start]**Control de Versiones:** Git [cite: 237]

## Objetivos del Proyecto

Los objetivos se dividen en tres fases principales:

1.  **Fase 1: Desarrollo del Software de Control**
    * [cite_start]Evolucionar la GUI y el entorno de pruebas basado en Python, Robot y Selenium[cite: 86].
    * [cite_start]Implementar almacenamiento y visualización de datos en tiempo real (SNMP, logs)[cite: 87].
    * [cite_start]Generar informes de prueba automatizados y estandarizados[cite: 89].

2.  **Fase 2: Diseño y Construcción del Hardware (HIL)**
    * [cite_start]Diseñar y construir un prototipo basado en una Raspberry Pi 4 y módulos relé[cite: 97, 99].
    * [cite_start]Este hardware reemplazará la simulación por software actual para activar físicamente las entradas de los módulos IPTU[cite: 99, 100].

3.  **Fase 3: Integración, Validación y Análisis**
    * [cite_start]Integrar el hardware (Raspberry Pi) con la interfaz gráfica de control[cite: 109].
    * [cite_start]Definir y ejecutar un conjunto de pruebas de robustez HIL completas[cite: 111].
    * [cite_start]Analizar los resultados para identificar límites operativos y tiempos de transmisión bajo estrés[cite: 112].

## Equipo Bajo Prueba (EUT)

* [cite_start]**Equipo:** Unidad de Teleprotección Universal ZIV TPU-1 [cite: 170]
* **Módulos Clave:**
    * [cite_start]**MWTU:** Módulo de procesamiento principal con servidor web[cite: 174].
    * [cite_start]**IPTU:** Módulo de interfaz de protección por contactos (el objetivo principal de las pruebas HIL)[cite: 176, 180].