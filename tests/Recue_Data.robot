*** Settings ***
Library    MyKeywords.py
Library    Collections

*** Variables ***
${RASPBERRY_PI_IP}    10.212.42.42
${HIL_PORT}           65432

*** Test Cases ***
Rescatar Datos De La Noche
    [Documentation]    NO ENVÍA COMANDOS. Solo recupera los logs que están en memoria de la RPi y genera el CSV.
    Log To Console     \n *** INICIANDO RESCATE DE DATOS ***
    
    # 1. Recuperamos los logs físicos de la RPi (que siguen en memoria)
    Log To Console     Intentando descargar logs de la RPi...
    ${rpi_logs}=    Hil Get Logs Force    ${RASPBERRY_PI_IP}    ${HIL_PORT}    
    # 2. Recuperamos los traps que tu PC ha estado guardando toda la noche
    # Usamos start_index 0 para coger TODO lo que haya en memoria de la sesión actual
    Log To Console     Recuperando Traps de la memoria del PC...

    ${empty_list}=    Create List

    # 3. Generamos el informe
    Log To Console     Generando CSV Maestro...
    ${csv_path}    ${t3_traps_count}    ${t4_traps_count}=    Generate Burst Performance Report    ${rpi_logs}    ${empty_list}    ${empty_list}

    Log To Console     \n *** ¡RESCATE COMPLETADO! ***
    Log To Console     Informe guardado en: ${csv_path}