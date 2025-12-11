*** Settings ***
Library    MyKeywords.py
Library   netstorm_controller.py
Library   Collections
Library    netstorm_controller.py

Documentation    Tests para controlar el Hardware-in-the-Loop (Raspberry Pi).


*** Variables ***
${RASPBERRY_PI_IP}    10.212.42.42      # IP por defecto, la GUI la reemplazará por la que el usuario indique
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

# *** PARA PRUEBAS FUNCIONALES ***
${MAX_LATENCY_THRESHOLD}    15.0    # Umbral de aceptación en ms



# Parámetros para el test de sensibilidad PWM (ms)
${START}    40    # Ancho de pulso inicial en ms
${END}      5     # Ancho de pulso final en ms

# Variables Netstorm
${NETSTORM_IP}          10.212.42.85
${NETSTORM_VNC_PASS}    Passwd@02

${NETWORK_PROFILE}      NONE    # Variable de control (por defecto NONE modo normal sin ruido)

*** Test Cases ***
Ejecutar Rafaga De Rendimiento
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B y los logs procedentes de los pines de la RPI conectada mediante Socket
    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN LOS CANALES ${CHANNELS_TO_TEST} ***

    [Setup]       Setup Con Control de Red
    [Teardown]    Teardown Con Cierre de VNC

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
    # ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY},${CHANNELS_TO_TEST}    ${HIL_PORT}    30
    Log To Console   \n\n *** RÁFAGA COMPLETADA. RESPUESTA RPI: ${response} ***
    Log To Console    Esperando a que se silencien los traps SNMP...
    Wait For Traps Silence    B    silence_window=3

# *************** RECOLECCION DE DATOS ********************************
    # Obtenemos los logs de T0 y T5 de la RPI
    ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}
    Sleep    2s
    # Obtenemos todos los traps recolectados
    ${all_new_traps_A}=    Get Traps Since Index    A    ${start_index_A}
    ${all_new_traps_B}=    Get Traps Since Index    B    ${start_index_B}
    # Log To Console    Traps nuevos recibidos A: ${all_new_traps_A}
    # Log To Console    Traps nuevos recibidos B: ${all_new_traps_B}
    # **************************************************************
    # Generamos el informe final combinando los datos del RPI (${rpi_logs}) y los traps SNMP (${FULL_SNMP_DATA_LIST})
    Log To Console    Generando informe de rendimiento Desarrollo
    ${csv_path}    ${t3_traps_count}    ${t4_traps_count}=    Generate Burst Performance Report    ${rpi_logs}    ${all_new_traps_A}    ${all_new_traps_B}
    Log To Console    Informe Dev generado: ${csv_path}
    Log To Console    Número de traps T3 recibidos: ${t3_traps_count}
    Log To Console    Número de traps T4 recibidos: ${t4_traps_count}


Ejecutar Rafaga De Rendimiento Funcional
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B y los logs procedentes de los pines de la RPI conectada mediante Socket
    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN LOS CANALES ${CHANNELS_TO_TEST} ***

    [Setup]       Setup Con Control de Red
    [Teardown]    Teardown Con Cierre de VNC

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
    # ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY},${CHANNELS_TO_TEST}    ${HIL_PORT}    30
    Log To Console   \n\n *** RÁFAGA COMPLETADA. RESPUESTA RPI: ${response} ***
    Log To Console    Esperando a que se silencien los traps SNMP...
    Wait For Traps Silence    B    silence_window=3

# *************** RECOLECCION DE DATOS ********************************
    # Obtenemos los logs de T0 y T5 de la RPI
    ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}
    Sleep    2s
    # Obtenemos todos los traps recolectados
    ${all_new_traps_A}=    Get Traps Since Index    A    ${start_index_A}
    ${all_new_traps_B}=    Get Traps Since Index    B    ${start_index_B}
    # Log To Console    Traps nuevos recibidos A: ${all_new_traps_A}
    # Log To Console    Traps nuevos recibidos B: ${all_new_traps_B}
    # **************************************************************
    # Generamos el informe final FUNCIONAL combinando los datos del RPI (${rpi_logs}) y los traps SNMP (${FULL_SNMP_DATA_LIST})
    Log To Console    Generando informe funcional de rendimiento
    ${func_csv_path}=    Generate Functional Report    ${rpi_logs}    ${all_new_traps_A}    ${all_new_traps_B}    ${MAX_LATENCY_THRESHOLD}

    Log To Console    \n *** REPORTE FUNCIONAL CREADO: ${func_csv_path} ***
    Log To Console    Puede revisar la tasa de exito y el jitter en el .csv generado

Ejecutar Pruebas de Rendimiento Dev&Functional 
    [Documentation]    Ejecuta una secuencia rápida de disparos, monitorizando los traps SNMP generados en la sesión A y sesión B y los logs procedentes de los pines de la RPI conectada mediante Socket
    Log To Console    \n *** INICIANDO RÁFAGA DE ${NUM_PULSES} PULSOS EN LOS CANALES ${CHANNELS_TO_TEST} ***

    [Setup]       Setup Con Control de Red
    [Teardown]    Teardown Con Cierre de VNC

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
    # ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,${NUM_PULSES},${PULSE_DURATION},${LOOP_DELAY},${CHANNELS_TO_TEST}    ${HIL_PORT}    30
    Log To Console   \n\n *** RÁFAGA COMPLETADA. RESPUESTA RPI: ${response} ***
    Log To Console    Esperando a que se silencien los traps SNMP...
    Wait For Traps Silence    B    silence_window=3

# *************** RECOLECCION DE DATOS ********************************
    # Obtenemos los logs de T0 y T5 de la RPI
    ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}
    Sleep    2s
    # Obtenemos todos los traps recolectados
    ${all_new_traps_A}=    Get Traps Since Index    A    ${start_index_A}
    ${all_new_traps_B}=    Get Traps Since Index    B    ${start_index_B}
    # Log To Console    Traps nuevos recibidos A: ${all_new_traps_A}
    # Log To Console    Traps nuevos recibidos B: ${all_new_traps_B}
    # **************************************************************
    # Generamos los informes finales FUNCIONAL y DESARROLLO combinando los datos del RPI (${rpi_logs}) y los traps SNMP (${FULL_SNMP_DATA_LIST})
    Log To Console    Generando informe de rendimiento Desarrollo
    ${csv_path}    ${t3_traps_count}    ${t4_traps_count}=    Generate Burst Performance Report    ${rpi_logs}    ${all_new_traps_A}    ${all_new_traps_B}
    Log To Console    Informe Dev generado: ${csv_path}
    
    
    Log To Console    Generando informe funcional de rendimiento
    ${func_csv_path}=    Generate Functional Report    ${rpi_logs}    ${all_new_traps_A}    ${all_new_traps_B}    ${MAX_LATENCY_THRESHOLD}
    Log To Console    \n *** REPORTE FUNCIONAL CREADO: ${func_csv_path} ***
    Log To Console    Puede revisar la tasa de exito y el jitter en el .csv generado
Escenario 4: Prueba de Sensibilidad PWM
    [Documentation]    Barrido descendente del ancho de pulso empoleado. De esta manera logramos encontrar el pulso de corte en el que la IPTU deja de detectar la señal.
    Log To Console    \n *** INICIANDO PRUEBA DE SENSIBILIDAD PWM EN CANALES ${CHANNELS_TO_TEST} ***
    
    [Setup]       Setup Con Control de Red
    [Teardown]    Teardown Con Cierre de VNC
    
    ${csv_path}    Init Pwm Step Test
    Log To Console    Init del informe generado en: ${csv_path}
    
    FOR    ${pulse_width}    IN RANGE    ${START}    ${END}    -1
        ${duration_s}=    Evaluate    ${pulse_width} / 1000.0    # A segundos

        Log To Console    \n  *** Enviado pulso de ${pulse_width} ms

        Hil Start Performance Log    ${RASPBERRY_PI_IP}    ${CHANNELS_TO_TEST}

        Send Hil Command    ${RASPBERRY_PI_IP}    BURST_BATCH,10,${duration_s},0.05,${CHANNELS_TO_TEST}    ${HIL_PORT}    5

        Sleep    2s

        ${rpi_logs}=    Hil Stop Performance Log    ${RASPBERRY_PI_IP}    ${HIL_PORT}

        # Generamos el informe parcial
        ${success_rate}    ${t0_count}    ${t5_count}    Pwm Step Test Analizer    ${rpi_logs}

        Log To Console    Resultados para pulso ${pulse_width} ms: T0 detectados=${t0_count}, T5 detectados=${t5_count}, Tasa de éxito=${success_rate}%

        # Guardamos los resultados en el informe
        Log Pwm Step Test Result    ${csv_path}    ${pulse_width}    ${t0_count}    ${t5_count}    ${success_rate}
        
        # Si tenemos tasa de exito 0%, ¿salimos del bucle?
        Run Keyword If    '${success_rate}' == '0'    Exit For Loop
    END

    Log To Console    \n *** BARRIDO COMPLETADO. REvisa el .csv con ruta: ${csv_path} ***
Ejecutar Rafaga GUI
    Log To Console    \n *** INICIANDO RÁFAGA desde la GUI DE ${NUM_PULSES} PULSOS EN LOS CANALES: ${CHANNELS_STR} ***

    [Setup]       Setup Con Control de Red
    [Teardown]    Teardown Con Cierre de VNC

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

Setup Con Control de Red
    [Documentation]    Si se pide perfil de red, conecta al Netstorm y aplica el perfil.
    ...                Si NETWORK_PROFILE es NONE, no hace nada (comportamiento clásico).
    
    Run Keyword If    '${NETWORK_PROFILE}' != 'NONE'    Log To Console    \n>>> [SETUP] Activando Control de Red: ${NETWORK_PROFILE}
    
    # Nos conectamos en caso de que nos lo pidan
    Run Keyword If    '${NETWORK_PROFILE}' != 'NONE'    Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    
    # Cargamos el perfil (CLEAN o NOISE)
    Run Keyword If    '${NETWORK_PROFILE}' != 'NONE'    Set Network Profile    ${NETWORK_PROFILE}
    
    # Si es NOISE, aseguramos el Toggle (activar inyección)
    # Run Keyword If    '${NETWORK_PROFILE}' == 'NOISE'   Toggle Noise    # Comentado porque dejamos activado el toggle en el mismo .cfg 0X_NOISE que cargamos en el Netstorm

Teardown Con Cierre de VNC
    [Documentation]    Cierra la conexión VNC al terminar, si se abrió.
    Run Keyword If    '${NETWORK_PROFILE}' != 'NONE'    Set Network Profile    CLEAN
    Run Keyword If    '${NETWORK_PROFILE}' != 'NONE'    Disconnect From Netstorm