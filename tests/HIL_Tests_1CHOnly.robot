*** Settings ***
Library    MyKeywords.py
Library   Collections

Documentation    Tests para controlar el Hardware-in-the-Loop (Raspberry Pi).


*** Variables ***
${RASPBERRY_PI_IP}    10.212.40.14      # IP por defecto, la GUI la reemplazará por la que el usuario indique
${HIL_PORT}           65432          # Puerto del servidor HIL
${COMMAND_STR}    default
${CHANNEL}    1    # Canal de prueba para T0 y T5

${NUM_PULSES}    10
${PULSE_DURATION}    0.5
${LOOP_DELAY}       2    # Delay entre pulsos en el test de pulsos repetidos para que de tiempo a que el sistema se estabilice

*** Test Cases ***
Ejecutar Rafaga De Rendimiento_OLD
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B

    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN EL CANAL ${CHANNEL} ***
    # Inicializamos una lista para que se vayan guardando los logs de timestamp de todos los ciclos de pulsos
    ${ALL_TRAPS_A}=    Create List
    ${ALL_TRAPS_B}=    Create List
# **************************************************************
    # HIl Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNEL}
# **************************************************************
    FOR     ${i}    IN RANGE    1    ${NUM_PULSES} + 1
        Log To Console    \n *** Pulso ${i} de ${NUM_PULSES} ***
        #  La idea es captar el numero de traps antes de enviar el pulso, enviar el pulso, esperar un poco, y luego recuperar los traps generados en ese intervalo
        # Adquirimos numero de traps totales antes de enviar el pulso
        ${start_index_A}=    Get Current Trap Count    A
        ${start_index_B}=    Get Current Trap Count    B
        # Enviamos el pulso de activación
        Send Hardware Input Command    PULSE,${CHANNEL},${PULSE_DURATION}
        Sleep    ${LOOP_DELAY}
        # Recuperamos los traps generados por este pulso. SOLO LOS NUEVOS DESDE start_index
        ${new_traps_A}=    Get Traps Since Index    A    ${start_index_A}
        ${new_traps_B}=    Get Traps Since Index    B    ${start_index_B}
        
        Append To List    ${ALL_TRAPS_A}    ${new_traps_A}    # Guardamos los traps de este ciclo en la lista completa
        Append To List    ${ALL_TRAPS_B}    ${new_traps_B}    # Guardamos los traps de este ciclo en la lista completa

        Log To Console    .    no_newline=True   
    END

    Log To Console   \n\n *** RÁFAGA COMPLETADA. DETENIENDO LOG Y RECUPERANDO DATOS... ***
    # **************************************************************
    ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}
    # **************************************************************
    # Generamos el informe final combinando los datos del RPI (${rpi_logs}) y los traps SNMP (${FULL_SNMP_DATA_LIST})
    ${csv_path}=    Generate Performance Report OLD    ${rpi_logs}    ${ALL_TRAPS_A}    ${ALL_TRAPS_B}

Ejecutar Rafaga De Rendimiento
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B y los logs procedentes de los pines de la RPI conectada mediante Socket
    
    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN EL CANAL ${CHANNEL} ***
    # Clear Traps Buffer    A
    # Clear Traps Buffer    B

    ${start_index_A}=    Get Current Trap Count    A
    ${start_index_B}=    Get Current Trap Count    B

# ************************* INICIAMOS LOGGER RPI PARA PINES T0 Y T5*************************************
    Hil Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNEL}

# ******************* EJECUCIÓN *******************************************
    # Calculamos el tiempo total + 10s de margen
    ${total_duration_s}=    Evaluate    (${NUM_PULSES} * ${PULSE_DURATION}) + ((${NUM_PULSES} - 1) * ${LOOP_DELAY}) + 10    # Dejamos un margen de 10s para el timeout
    Log To Console    El comando tarda  ${total_duration_s} segundos aprox.
# **************************************************
    ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST,${CHANNEL},${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY}    ${HIL_PORT}    ${total_duration_s}
    Log To Console   \n\n *** RÁFAGA COMPLETADA. RESPUESTA RPI: ${response} ***

# *************** RECOLECCION DE DATOS ********************************
    # Obtenemos los logs de T0 y T5 de la RPI
    ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}
    Sleep    2s
    # Obtenemos todos los traps recolectados
    ${all_new_traps_A}=    Get Traps Since Index    A    ${start_index_A}
    ${all_new_traps_B}=    Get Traps Since Index    B    ${start_index_B}
    Log To Console    Traps nuevos recibidos A: ${all_new_traps_A}
    Log To Console    Traps nuevos recibidos B: ${all_new_traps_B}
    # **************************************************************
    # Generamos el informe final combinando los datos del RPI (${rpi_logs}) y los traps SNMP (${FULL_SNMP_DATA_LIST})
    Log To Console    Generando informe de rendimiento
    ${csv_path}=    Generate Burst Performance Report    ${rpi_logs}    ${all_new_traps_A}    ${all_new_traps_B}
    Log To Console    Informe generado: ${csv_path}

Test de Log T0 T5
    [Documentation]    Test manual: Inicia logs, espera 5s para que activemos fisicamente las entradas T0 y T5, y luego detiene el log y obtiene los datos.
    Log To Console    \n\n *** Iniciando Test de Log T0 y T5 ***

    Hil Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNEL}
    Log To Console    *** RPI está registrando canal ${CHANNEL}. Active FISICAMENTE las entradas T0 y T5. Esperando 5 segundos... \n
    
    Sleep    5s

    #  Recuperamos los logs en "crudo" (listas de timestamps en ns)
    Log To Console    El tiempo ha finalizado. Recuperando logs...
    ${logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}
    
    # Mostramos los logs obtenidos
    Log To Console    Logs obtenidos del RPI:
    Log Dictionary    ${logs}    # COn Log Dictionary se muestra de forma más legible

    # Tratamos de extraer datos específicos como ejemplo
    ${num_t0_logs}=    Get Length    ${logs['t0_logs']}
    ${num_t5_logs}=    Get Length    ${logs['t5_logs']}
    Log To Console    Número de eventos T0 registrados (INPUT): ${num_t0_logs}
    Log To Console    Número de eventos T5 registrados (OUTPUT): ${num_t5_logs}


Send Input Command
    ${variable}=    Send Hardware Input Command    ${COMMAND_STR}

*** Keywords ***
Send Hardware Input Command
    [Documentation]    Envía un comando genérico al servidor HIL.
    [Arguments]        ${command_str}
    # Llama a la keyword de Python que acabamos de crear
    ${response}=    Send HIL Command    ${RASPBERRY_PI_IP}    ${command_str}    port=${HIL_PORT}
    Log    Respuesta del servidor HIL: ${response}