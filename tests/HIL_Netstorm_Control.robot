*** Settings ***
Library    MyKeywords.py
Library    netstorm_controller.py
Library    Collections
Library    String

Documentation    Tests para controlar el equipo Netstorm, de Albedo.


*** Variables ***
${NETSTORM_IP}    10.212.42.85
${NETSTORM_VNC_PASS}    Passwd@02


# ******** VARIABLES QUE SE PUEDEN CONFIGURAR EN LOS PERFILES DE RUIDO ********
${PROFILE_NAME}    IGNORE
${NOISE_PORT}    A
# PERDIDA DE PAQUETES
${LOSS_MODE}    IGNORE
${LOSS_PROBABILITY}    IGNORE
${BURST_LENGTH}    IGNORE
${BURST_SEPARATION}    IGNORE
${ALTERNATIVE_LOSS_PROB}    IGNORE
${MEAN_LENGTH}    IGNORE
${MEAN_ALTERNATIVE_LENGTH}    IGNORE

# RETARDO Y JITTER
${DELAY_MODE}    IGNORE
${FIXED_DELAY}    IGNORE
${MIN_DELAY}    IGNORE
${MAX_DELAY}    IGNORE
${AVG_DELAY}    IGNORE
${REORDENING}    IGNORE

# ANCHO DE BANDA
${BANDWIDTH_MODE}    IGNORE
${FRAME_RATE}    IGNORE
${MAX_BURST_SIZE}    IGNORE
${BIT_RATE}    IGNORE

# DUPLICACIÓN DE TRAMAS
${DUPLICATION_MODE}    IGNORE
${DUPLICATION_PROBABILITY}    IGNORE

# CORRUPCION DE TRAMAS (Frame Errors / FCS)
${ERROR_MODE}    IGNORE
${ERROR_PROBABILITY}    IGNORE



*** Test Cases ***
# ********************** TESTS CON INYECCIÓN DE RUIDO (OLD - AHORA ESTÁN IMPLEMENTADAS DIRECTAMENTE JUNTO A LOS TESTS DE RAFAGAS EN HIL_TEST.ROBOT) *********************** 
Escenario WP3: Activar Perfil NOISE en Netstorm
    Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    #  Configuramos el perfil de red con ruido
    Log To Console    Cargando Perfil NOISE
    Set Network Profile    NOISE
    [Teardown]    Disconnect From Netstorm
Escenario WP3: Activar Perfil CLEAN en Netstorm
    Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    #  Configuramos el perfil de red limpio
    Log To Console    Cargando Perfil CLEAN
    Set Network Profile    CLEAN
    [Teardown]    Disconnect From Netstorm

Escenario WP3: Togglear Ruido en Netstorm
    Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    #  Hacemos toggle de Ruido
    Log To Console    Haciendo Toggle de Ruido
    Toggle Noise
    [Teardown]    Disconnect From Netstorm
    

# ********************************* CONFIGURACIÓN DE NET.STORM *********************************
Configurar Perfil Personalizado (Universal)
    [Documentation]    Configura el NetStorm basándose en las variables inyectadas desde el Planificador.
    ...                Nos conectamos al equipo.
    ...                Revisamos los bloques (Loss, DelayJitter..) que tienen un modo definido.
    ...                Aplicamos  configuración solo a estos bloques
    ...                Guardamos el perfil si se nos especifica el nombre
    
    [Setup]       Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    [Teardown]    Disconnect From Netstorm

    Log To Console    \n=********** INICIANDO CONFIGURACIÓN NETSTORM **********
    # ********************************************************************
    # ANTES DE CONFIGURAR NINGUN PARAMETRO DE RUIDO, CARGAMOS EL PERFIL DE CLEAN PARA EMPEZAR CON TODOS LOS PARAM DE RUIDO DESACTIVADOS
    # ********************************************************************
    Set Network Profile    CLEAN
    
    # ********************************************************************
    # CONFIGURAMOS PÉRDIDAS (LOSS)
    # ********************************************************************
    # Solo entramos a configurar si el usuario ha definido un modo diferente de IGNORE
    Run Keyword If    '${LOSS_MODE}' != 'IGNORE'    
    ...    Configurar Loss Wrapper    ${NOISE_PORT}    ${LOSS_MODE}    ${LOSS_PROBABILITY}    ${BURST_LENGTH}    ${BURST_SEPARATION}    ${ALTERNATIVE_LOSS_PROB}    ${MEAN_LENGTH}    ${MEAN_ALTERNATIVE_LENGTH}

    # ********************************************************************
    # CONFIGURAMOS RETARDO (DELAY & JITTER)
    # ********************************************************************
    Run Keyword If    '${DELAY_MODE}' != 'IGNORE'
    ...    Configurar Delay Wrapper    ${NOISE_PORT}    ${DELAY_MODE}    ${FIXED_DELAY}    ${MIN_DELAY}    ${MAX_DELAY}    ${AVG_DELAY}    ${REORDENING}

    # ********************************************************************
    # CONFIGURAMOS DUPLICACIÓN
    # ********************************************************************
    Run Keyword If    '${DUPLICATION_MODE}' != 'IGNORE'
    ...    Configurar Duplication Wrapper    ${NOISE_PORT}    ${DUPLICATION_MODE}    ${DUPLICATION_PROBABILITY}

    # ********************************************************************
    # CONFIGURAMOS CORRUPCIÓN (ERRORS)
    # ********************************************************************
    Run Keyword If    '${ERROR_MODE}' != 'IGNORE'
    ...    Configurar Corruption Wrapper    ${NOISE_PORT}    ${ERROR_MODE}    ${ERROR_PROBABILITY}

    # ********************************************************************
    # CONFIGURAMOS EL ANCHO BANDA
    # ********************************************************************
    Run Keyword If    '${BANDWIDTH_MODE}' != 'IGNORE'
    ...    Configurar Bandwidth Wrapper    ${NOISE_PORT}    ${BANDWIDTH_MODE}    ${FRAME_RATE}    ${MAX_BURST_SIZE}    ${BIT_RATE}


    # ********************************************************************
    # GUARDAMOS EL PERFIL
    # ********************************************************************
    # ANTES HACEMOS UN TOGGLE NOISE PARA QUE EL RUIDO ESTE ACTIVADO CUANDO SE ACTIVE EL PERFIL
    Toggle Noise
    # GUARDAMOS EL PERFIL
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    
    ...    Save Config    ${PROFILE_NAME}

    Log To Console    ========== CONFIGURACIÓN FINALIZADA ==========





# TEST AUTOMATIZACIÓN NET.STORM INDEPENDIENTES
Configurar Perfil Loss Netstorm
    [Setup]       Connect To Netstorm    ${NETSTORM_IP}    ${NETSTORM_VNC_PASS}
    [Teardown]    Disconnect From Netstorm

    Log To Console    INICIANDO CONFIGURACIÓN LOSS NETSTORM

    # CONFIG PERDIDAS (LOSS)
    Apply Config Loss    ${NOISE_PORT}    ${LOSS_MODE}    ${LOSS_PROBABILITY}    ${BURST_LENGTH}    ${BURST_SEPARATION}    ${ALTERNATIVE_LOSS_PROB}    ${MEAN_LENGTH}    ${MEAN_ALTERNATIVE_LENGTH}

    # Guardado de Perfil
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    Save Config    ${PROFILE_NAME}

# CONFIG RETARDO Y JITTER
Configurar Perfil Delay Jitter
    Apply Config Delay Jitter    ${NOISE_PORT}    ${DELAY_MODE}    ${FIXED_DELAY}    ${MIN_DELAY}    ${MAX_DELAY}    ${AVG_DELAY}    ${REORDENING}

    # Guardado de Perfil
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    Save Config    ${PROFILE_NAME}


# CONFIG DUPLICACIÓN DE TRAMAS
Configurar Perfil Duplicacion de Tramas
    Apply Config Duplication    ${NOISE_PORT}    ${DUPLICATION_MODE}    ${DUPLICATION_PROBABILITY}

    # Guardado de Perfil
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    Save Config    ${PROFILE_NAME}

    # CONFIG CORRUPCION DE TRAMAS (Frame Errors / FCS)
Configurar Perfil Corrupcion de Tramas
    Apply Config Corruption    ${NOISE_PORT}    ${ERROR_MODE}    ${ERROR_PROBABILITY}

    # Guardado de Perfil
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    Save Config    ${PROFILE_NAME}

    # CONFIG ANCHO DE BANDA
Configurar Perfil Ancho de Banda
    Apply Config Bandwidth    ${NOISE_PORT}    ${BANDWIDTH_MODE}    ${FRAME_RATE}    ${MAX_BURST_SIZE}    ${BIT_RATE}
    # Guardado de Perfil
    Run Keyword If    '${PROFILE_NAME}' != 'IGNORE'    Save Config    ${PROFILE_NAME}


*** Keywords ***
# ********************************* CONFIGURACIÓN DE NET.STORM *********************************
Configurar Loss Wrapper
    [Arguments]    ${port}    ${mode}    ${prob}    ${burst_len}    ${burst_sep}    ${alternative_loss_prob}    ${mean_length}    ${mean_alternative_lenth}
    Log To Console    >>> Aplicando Configuración LOSS: Mode=${mode}
    Apply Config Loss    ${port}    ${mode}    ${prob}    ${burst_len}    ${burst_sep}    ${alternative_loss_prob}    ${mean_length}    ${mean_alternative_lenth}


Configurar Delay Wrapper
    [Arguments]    ${port}    ${mode}    ${fixed}    ${min}    ${max}    ${avg}    ${reorder}
    Log To Console    >>> Aplicando Configuración DELAY: Mode=${mode}
    Apply Config Delay Jitter    ${port}    ${mode}    ${fixed}    ${min}    ${max}    ${avg}    ${reorder}

Configurar Duplication Wrapper
    [Arguments]    ${port}    ${mode}    ${prob}
    Log To Console    >>> Aplicando Configuración DUPLICATION: Mode=${mode}
    Apply Config Duplication    ${port}    ${mode}    ${prob}

Configurar Corruption Wrapper
    [Arguments]    ${port}    ${mode}    ${prob}
    Log To Console    >>> Aplicando Configuración BIT ERRORS: Mode=${mode}
    Apply Config Corruption    ${port}    ${mode}    ${prob}

Configurar Bandwidth Wrapper
    [Arguments]    ${port}    ${mode}    ${frame_rate}    ${max_burst_size}    ${bit_rate}
    Log To Console    >>> Aplicando Configuración BANDWIDTH: Mode=${mode}
    Apply Config Bandwidth    ${port}    ${mode}    ${frame_rate}    ${max_burst_size}    ${bit_rate}
