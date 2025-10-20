***Settings***
Library    trapReceiver_Robot_4.py
# Library    SeleniumLibrary
# Library    String
# Library    Collections
# Library    OperatingSystem    #for file operations
# Library    BuiltIn
# Library    XML
# Library    DateTime

Resource    Alignment_Section.robot

Suite Setup    Setup Command_Assignments_SNMP
Suite Teardown    Alignment_Section.Close Browser


***Variables***
${MIB_DIRS}    file:///C:/Users/sergio.bret/Documents/SNMP/compiled_mibs
${LISTEN_IP}    10.212.42.4
${LISTEN_PORT}    162

${WAIT_DURATION}     5s  # Tiempo de espera para recibir traps (ej. 120 segundos)
#*************************************************************************************************************************

#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002    #Login PASS
${INTERNAL_PASS}    Passwd@02    
${URL_BASE}    https://


# ${terminal_title}    EUT Setup 1
# ${IP_ADDRESS}    10.212.43.11

# ${terminal_title}    AUX Setup 1
# ${IP_ADDRESS}    10.212.43.12

# ${terminal_title}    EUT Setup 2
# ${IP_ADDRESS}    10.212.43.21

${terminal_title}    EUT Setup 1
${IP_ADDRESS}    10.212.43.87

${URL_COMPLETA}=    ${URL_BASE}${USER}:${PASS}@${IP_ADDRESS}

${TPU_WelcomeTitle_Type}    css=div.text-center.headerCenter.col h4


#*************************************************************************************************************************
# MODULES
${IBTU}    112
${IDTU}    32
${IETU}    64
${IOTU}    80
${ICTU}    128
${IPTU}    16
${IPTU.10}    272
${IRTU}    96
${DSTU}    144
${MCTU}    160
${IOCT}    176
${IPIT}    192
${IEPT}    224
${IOCS}    256
${ICPT}    288
@{Teleprotection_list}        ${IBTU}    ${IDTU}    ${IETU}    ${IOTU}    ${IOCT}    ${IPIT}    ${IOCS}    ${ICPT}    ${DSTU}
@{ICTU_IPTU_IEPT_list}        ${ICTU}    ${IPTU}    ${IEPT}
#*************************************************************************************************************************

#OPEN AND CLOSE BROWSER PARAMETERS
${BROWSER}    chrome
${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content

#************************************************************************************************************************
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]


***Test Cases***
#TEST1: Inicio del listener, carga de MIBs y generación de traps de activación/desactivación de entradas y recepción y activación de salidas (segun escenerario).
# Dos escenarios:
#IP Terminal 1: 10.212.43.21
#IP Terminal 2: 10.212.43.87
# 1. Activación de entradas (y envío de ordenes) desde la terminal 1. Listener en la terminal 1, captando traps de activación de inputs y transmisión de ordenes 
# 2. Activación de entradas (y envío de ordenes) desde la terminal 2. Listener en la terminal 1, captando traps de recepción de ordenes y activación de outputs.
Test Verificar Multiples Traps
    # Iniciar el listener
    Log To Console    Iniciando listener en ${LISTEN_IP}:${LISTEN_PORT}
    
    Start Trap Listener    listen_ip=${LISTEN_IP}    listen_port=${LISTEN_PORT}    mib_dirs_string=${MIB_DIRS}

    #Load SNMP MIBs    DIMAT-BASE-MIB    DIMAT-TPU1C-MIB

    Load Mibs    DIMAT-BASE-MIB    DIMAT-TPU1C-MIB
    
    # Show Listener Status
    Log To Console    Listener iniciado. Esperando traps en ${LISTEN_IP}:${LISTEN_PORT}...
    Log To Console    (La clasificación se basa en SNMPv2-MIB::snmpTrapOID.0 por defecto)

    Log To Console    \nFin del periodo de espera.

##############################################################################################################################
Start TPU Actions 1
    Log To Console    \n--- Realizando acciones de TPU para generar traps ---\n
    Log To Console    \n--- Enviando Inputs ---\n
    ${input_numbers_list}=    Create List

    Append To List    ${input_numbers_list}    1
    Append To List    ${input_numbers_list}    2

    Input Activation/desactivation    1    0    ${input_numbers_list}

    Sleep    2s

    #END of TPU Actions
##############################################################################################################################
Wait Until WAIT_DURATION Reaches 0
    Wait For Traps To Arrive    ${WAIT_DURATION}

    Log To Console    \nFin del periodo de espera.

##############################################################################################################################
Mostrar tipos de eventos específicos
    Log To Console    \n--- Resumen de Traps Esperados (entradas, salidas y transmisión y recepción de órdenes) ---
    ${Input_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyInputCircuits
    Show Specific Event Types    ${Input_Event}    consume_traps=False

    ${Command_Tx_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx
    Show Specific Event Types    ${Command_Tx_Event}    consume_traps=False

    ${Input_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyOutputCircuits
    Show Specific Event Types    ${Input_Event}    consume_traps=False

    ${Command_Tx_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyCommandRx
    Show Specific Event Types    ${Command_Tx_Event}    consume_traps=False   

Reset All Received Traps
    Clear All Received Traps

Mostrar todos los traps almacenados
    # Mostramos todos los traps almacenados en la cola general después de haber borrado todos los traps.
    Show All Traps in the Queue    consume_traps=False
##############################################################################################################################
##############################################################################################################################
Start TPU Actions 2
    Log To Console    \n--- Realizando acciones de TPU para generar traps ---\n
    Log To Console    \n--- Desactivando Inputs ---\n
    Input Activation/desactivation    0
    Sleep    2s

    #END of TPU Actions
##############################################################################################################################
Wait Until WAIT_DURATION Reaches 0
    Wait For Traps To Arrive    ${WAIT_DURATION}

    Log To Console    \nFin del periodo de espera.

##############################################################################################################################
# Resumen de traps almacenados
#     Show All Traps in the Queue    consume_traps=False

Mostrar tipos de eventos específicos
    Log To Console    \n--- Resumen de Traps Esperados (entradas, salidas y transmisión y recepción de órdenes) ---
    ${Input_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyInputCircuits
    Show Specific Event Types    ${Input_Event}    consume_traps=False

    ${Command_Tx_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyCommandTx
    Show Specific Event Types    ${Command_Tx_Event}    consume_traps=False

    ${Input_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyOutputCircuits
    Show Specific Event Types    ${Input_Event}    consume_traps=False

    ${Command_Tx_Event}=    Set Variable    DIMAT-TPU1C-MIB::tpu1cNotifyCommandRx
    Show Specific Event Types    ${Command_Tx_Event}    consume_traps=False   

Mostrar todos los traps almacenados
    # Mostramos todos los traps almacenados en la cola general después de haber borrado todos los traps.
    Show All Traps in the Queue    consume_traps=False

#DETENEMOS EL LISTENER Y REGISTRAMOS ERRORES
Detener Listener y Registrar Errores
    Log To Console    \n--- Deteniendo el listener ---\n
    Stop Trap Listener And Log Errors


##############################################################################################################################
##############################################################################################################################
##############################################################################################################

# ->> Lo haré en un script .robot a parte, importando el archivo .robot de configuración de modulos de la sección BASIC CONFIGURATION TESTS.
# Redactaremos estos tests en la sección de pruebas completas funcionales del report!
#TEST2: Resumen de todos los traps almacenados (Y NO BORRADOS) en la cola general y Tipos de eventos recibidos.
#Escenario: Provocamos una perdida de sincronización entre las terminales despues de configurar un nuevo modulo y asignar nuevas ordenes.

# Configuracion de Modulos Diferentes
# Objetivo: Provocar una perdida de sincronización entre las terminales despues de configurar un nuevo modulo y asignar nuevas ordenes. 
# Captar los traps de sincronización y de asignación de ordenes. Apuntaremos el nombre de estos eventos en la actual lista de eventos que disponemos en el report.


Test Resumen de Traps Almacenados
    Show All Traps in the Queue    consume_traps=False    

Test Tipos de Eventos Recibidos
    Summary Event Type Traps Received

#DETENEMOS EL LISTENER Y REGISTRAMOS ERRORES
Detener Listener y Registrar Errores
    Log To Console    \n--- Deteniendo el listener ---\n
    Stop Trap Listener And Log Errors



*** Keywords ***
Setup Command_Assignments_SNMP
    Alignment_Section.Open Broswer to Login page    ${URL_COMPLETA}    ${BROWSER}
    # Wait Title    ${terminal_title}
    # Sleep    3s
    # Wait Until Progress Bar Reaches 100 V2
    Wait Until Page Contains Element    xpath=//span[contains(@class, 'p-button-icon p-c pi pi-sign-out')]    timeout=50s
    Click Open Folder    /
    Click Open Folder    ALIGNMENT
    Open Section    Input activation

Load SNMP MIBs
    [Arguments]    ${mib_module_1}=${None}    ${mib_module_2}=${None}
 # Cargar MIBs personalizadas
    Log To Console    Cargando MIBs personalizadas: ${mib_module_1}, ${mib_module_2}
    ${status}=    Run Keyword And Ignore Error    Load Mibs    ${mib_module_1}    ${mib_module_2}
    IF    '${status[0]}' == 'FAIL'    Log To Console    ADVERTENCIA: Error cargando MIBs personalizadas: ${status[1]}. Los OIDs podrían no resolverse a nombres.

Stop Trap Listener And Log Errors
    ${status}=    Run Keyword And Ignore Error    Stop Trap Listener
    IF    '${status[0]}' == 'FAIL'
        Log To Console    Error al detener el listener: ${status[1]}
    ELSE
        Log To Console    \nListener detenido.
    END

Wait For Traps To Arrive
    [Arguments]    ${duration}
    Log To Console    Esperando ${duration}...
    ${end_time}=    Evaluate    time.time() + float($duration[:-1])    modules=time    # Remove 's' and convert
    ${last_dot_time}=    Set Variable    ${0}
    WHILE    time.time() < ${end_time}
        ${current_time}=    Evaluate    time.time()    modules=time
        IF    ${current_time} - ${last_dot_time} >= 5
            Log To Console    .    no_newline=True
            ${last_dot_time}=    Set Variable    ${current_time}
        END
        Sleep    200ms
    END
    Log To Console    \nFin de la espera de ${duration}.

Log Dictionary
    [Arguments]    ${dictionary}
    ${items}=    Get Dictionary Items    ${dictionary}
    FOR    ${key}    ${value}    IN    @{items}
        Log To Console    \t${key}: ${value}
    END

Show All Traps in the Queue
    [Arguments]    ${consume_traps}=${True}
    Log To Console    \n--- Todos los Traps en Cola General (Estructura Mínima) ---
    ${all_traps_raw}=    Get All Raw Received Traps    ${consume_traps}
    # Log To Console    Total de traps en la cola general (_received_traps): ${LEN(${all_traps_raw})}
    IF    ${all_traps_raw}
        FOR    ${trap_data}    IN    @{all_traps_raw}
            Log To Console    \nTrap Almacenado en cola general:
            Log Dictionary    ${trap_data}
        END
    ELSE
        Log To Console    No hay traps en la cola general.
    END

Show Specific Event Types
    [Arguments]    ${SPECIFIC_EVENT_KEY}    ${consume_traps}=${True}
        # Visualización específica de traps tpu1cNotifyCommandTx
    Log To Console    \n--- Visualización específica de traps '${SPECIFIC_EVENT_KEY}' (si existen) ---
    ${event_types_again}=    Get Event Types     # Obtener de nuevo por si acaso

    FOR    ${event_type}    IN    @{event_types_again}
        ${comparison_result} =    Evaluate    "${event_type}" == "${SPECIFIC_EVENT_KEY}"
        IF    ${comparison_result}
            Log To Console    Obteniendo traps para el tipo de evento: '${SPECIFIC_EVENT_KEY}'
            ${tpu1c_traps}=    Get Traps By Event Type    event_type=${SPECIFIC_EVENT_KEY}    consume_traps=${consume_traps}
            IF    ${tpu1c_traps}
                # Log To Console    Se encontraron ${LEN(${tpu1c_traps})} traps del tipo '${SPECIFIC_EVENT_KEY}'. Su contenido almacenado es:
                FOR    ${trap_data}    IN    @{tpu1c_traps}
                    Log To Console    \nTrap Almacenado (${SPECIFIC_EVENT_KEY}):
                    Log Dictionary    ${trap_data}    # Log Dictionary formatea bien en el log.html
                    # Para consola, podrías necesitar algo más simple o iterar claves si es muy largo
                END
            ELSE
                Log To Console    No se encontraron traps para '${SPECIFIC_EVENT_KEY}' en este momento (aunque el tipo existe).
            END
        END    
    END


Summary Event Type Traps Received
    # Resumen de Traps Almacenados
    Log To Console    \n--- Resumen de Traps Almacenados (Estructura Mínima) ---
    ${event_types}=    Get Event Types
    IF    not ${event_types}
        Log To Console    No se recibieron traps clasificados.
    ELSE
        Log To Console    Tipos de evento (sanitizados) recibidos: ${event_types}
        FOR    ${etype}    IN    @{event_types}
            ${count}=    Count Traps By Event Type    event_type=${etype}
            Log To Console    \t- Tipo: '${etype}', Cantidad: ${count}
        END
    END



Clear All Traps
    Log To Console    \n--- Limpiando todos los traps recibidos ---\n
    ${status}=    Run Keyword And Ignore Error    Clear All Received Traps
    IF    '${status[0]}' == 'FAIL'
        Log To Console    Error al limpiar los traps: ${status[1]}
    ELSE
        Log To Console    Todos los traps han sido limpiados.
    END

Clear Traps By Event Type
    [Arguments]    ${event_type}
    Log To Console    \n--- Limpiando traps del tipo '${event_type}' ---\n
    ${status}=    Run Keyword And Ignore Error    Clear Traps By Event Type    event_type=${event_type}
    IF    '${status[0]}' == 'FAIL'
        Log To Console    Error al limpiar traps del tipo '${event_type}': ${status[1]}
    ELSE
        Log To Console    Traps del tipo '${event_type}' han sido limpiados.
    END