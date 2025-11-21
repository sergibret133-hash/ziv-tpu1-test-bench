*** Settings ***
Library    MyKeywords.py
Library   Collections

Documentation    Tests para controlar el Hardware-in-the-Loop (Raspberry Pi).


*** Variables ***
${RASPBERRY_PI_IP}    10.212.42.33      # IP por defecto, la GUI la reemplazará por la que el usuario indique
${HIL_PORT}           65432          # Puerto del servidor HIL
${COMMAND_STR}    default
# ${CHANNEL}    1    # Canal de prueba para T0 y T5
# @{CHANNELS_TO_TEST}    1    2    3    4    5    6
${CHANNELS_TO_TEST}    1,2,3,4,5,6
${CHANNELS_STR}
${NUM_PULSES}    10
${PULSE_DURATION}    0.5
${LOOP_DELAY}    1
${LOOP_DELAY}       2    # Delay entre pulsos en el test de pulsos repetidos para que de tiempo a que el sistema se estabilice

*** Test Cases ***
Ejecutar Rafaga De Rendimiento
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B y los logs procedentes de los pines de la RPI conectada mediante Socket
    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN LOS CANALES ${CHANNELS_TO_TEST} ***

    ${start_index_A}=    Get Current Trap Count    A
    ${start_index_B}=    Get Current Trap Count    B

    # Convertimos de lista a str
    # ${CHANNELS_STR}=    Catenate    SEPARATOR=,    @{CHANNELS_TO_TEST}

# ************************* INICIAMOS LOGGER RPI PARA PINES T0 Y T5 *************************************
    Hil Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNELS_TO_TEST}

# ******************* EJECUCIÓN *******************************************
    # Calculamos el tiempo total + 10s de margen
    # ${total_duration_s}=    Evaluate    (${NUM_PULSES} * ${PULSE_DURATION}) + ((${NUM_PULSES} - 1) * ${LOOP_DELAY}) + 10    
    ${total_duration_s}=    Evaluate    (int(${NUM_PULSES}) * float(${PULSE_DURATION})) + ((int(${NUM_PULSES}) - 1) * float(${LOOP_DELAY})) + 10    # Dejamos un margen de 10s para el timeout
    Log To Console    El comando tarda  ${total_duration_s} segundos aprox.
# **************************************************
    ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY},${CHANNELS_TO_TEST}    ${HIL_PORT}    ${total_duration_s}
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

Ejecutar Rafaga GUI
    Log To Console    \n *** INICIANDO RÁFAGA desde la GUI DE ${NUM_PULSES} PULSOS EN LOS CANALES: ${CHANNELS_STR} ***

    # Calculamos el timeout
    ${total_duration_s}=    Evaluate    (${NUM_PULSES} * ${PULSE_DURATION}) + ((${NUM_PULSES} - 1) * ${LOOP_DELAY}) + 10    # El +10 ultimo lo dejamos de margen. Recordemos que utilizamos esta variable para pasarla como timeout.
    Log To Console    El comando tarda ${total_duration_s} segundos aprox

    # Enviamos el comando HIL
    ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY},${CHANNELS_STR}    ${HIL_PORT}    ${total_duration_s}
    Log To Console   \n\n *** RÁFAGA (GUI) COMPLETADA. RESPUESTA RPI: ${response} ***


# Test de Log T0 T5
#     [Documentation]    Test manual: Inicia logs, espera 5s para que activemos fisicamente las entradas T0 y T5, y luego detiene el log y obtiene los datos.
#     Log To Console    \n\n *** Iniciando Test de Log T0 y T5 ***

#     Hil Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNEL}
#     Log To Console    *** RPI está registrando canal ${CHANNEL}. Active FISICAMENTE las entradas T0 y T5. Esperando 5 segundos... \n
    
#     Sleep    5s

#     #  Recuperamos los logs en "crudo" (listas de timestamps en ns)
#     Log To Console    El tiempo ha finalizado. Recuperando logs...
#     ${logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}
    
#     # Mostramos los logs obtenidos
#     Log To Console    Logs obtenidos del RPI:
#     Log Dictionary    ${logs}    # COn Log Dictionary se muestra de forma más legible

#     # Tratamos de extraer datos específicos como ejemplo
#     ${num_t0_logs}=    Get Length    ${logs['t0_logs']}
#     ${num_t5_logs}=    Get Length    ${logs['t5_logs']}
#     Log To Console    Número de eventos T0 registrados (INPUT): ${num_t0_logs}
#     Log To Console    Número de eventos T5 registrados (OUTPUT): ${num_t5_logs}


Send Input Command
    ${variable}=    Send Hardware Input Command    ${COMMAND_STR}

*** Keywords ***
Send Hardware Input Command
    [Documentation]    Envía un comando genérico al servidor HIL.
    [Arguments]        ${command_str}
    # Llama a la keyword de Python que acabamos de crear
    ${response}=    Send HIL Command    ${RASPBERRY_PI_IP}    ${command_str}    port=${HIL_PORT}
    Log    Respuesta del servidor HIL: ${response}