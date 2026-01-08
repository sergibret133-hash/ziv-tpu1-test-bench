*** Settings ***
Documentation       Pruebas de Robustez Analógica. Verifica el comportamiento del TPU-1 bajo condiciones de Ruido Analógico Blanco.
Resource            HIL_Analog_Noise_Control.robot
Library             MyKeywords.py
Library             BuiltIn

# Setup y Teardown general para asegurar que siempre conectamos y desconectamos
# Suite Setup         
# Suite Teardown      

*** Variables ***
${CMD_DURATION}     0.1     # Duración del pulso de disparo (s)
${RELAY_T0}         1       # ID del Relé que simula el disparo (Input TPU)
${CHANNEL_T5}       1       # ID del Canal que lee la salida T5 (Output TPU)

${NOISE_AMPLITUDE}    0.8     # Amplitud del ruido para la prueba de seguridad

${PRE_NOISE_DELAY}    1.0     # Tiempo de espera antes de iniciar la inyección de ruido (s)
${NOISE_DURATION}    5.0     # Duración de la inyección de ruido (s)
${POST_NOISE_DELAY}   1.0     # Tiempo de espera después de detener la inyección de ruido (s)

${RASPBERRY_PI_IP}    10.212.42.42
*** Test Cases ***
# *** ESCENARIO A: SEGURIDAD (SECURITY) ***
# Objetivo: Inyectar ruido analógico y verificar que el sistema no dispare falsos positivos.
Verify Security Against Spurious Noise
    [Documentation]    Ineycta ruido de alto nivel (0.8) sin enviar comandos. Verifica que no se detectan disparos (T5 permanece bajo).
    # Aseguramos que T5 está bajo antes de iniciar y limpiamos logs
    Stop Analog Noise Injection
    Send Hil Command    ${RASPBERRY_PI_IP}    RESET

    # Configuramos Logs en el servidor para detectar eventos en T5
    Send Hil Command    ${RASPBERRY_PI_IP}    CONFIG_LOG,T5,${CHANNEL_T5}
    Send Hil Command    ${RASPBERRY_PI_IP}    START_LOG

    Sleep    ${PRE_NOISE_DELAY}

    # Iniciamos inyección de ruido
    Start Analog Noise Injection    ${NOISE_AMPLITUDE}

    # Esperamos tiempo de prueba. Para la demo dejaremos 10s
    Sleep    ${NOISE_DURATION}

    # Detenemos inyección de ruido
    Stop Analog Noise Injection

    Sleep    ${POST_NOISE_DELAY}

    # Detenemos logs
    Send Hil Command    ${RASPBERRY_PI_IP}    STOP_LOG

    # Obtenemos logs y verificamos que no hay eventos en T5
    ${logs}=    Send Hil Command    ${RASPBERRY_PI_IP}    GET_LOGS

    # Verificamos que no hay eventos en T5
    Should Not Contain    ${logs}    "t5_ns": [    msg=Se detectaron disparos falsos durante la inyección de ruido!    # El patron que buscamos es "t5_ns": [ seguido de cualquier cosa


    # *** ESCENARIO B: OBEDIENCIA (DEPENDABILITY) ***
    # Objetivo: Enviar comandos de disparo bajo ruido analógico y verificar que se detectan correctamente.
Verify Dependability Under Degraded SNR
    [Documentation]    Lleva a cabo un barrido de niveles de ruido (0.1 a 0.9). En cada nivel, se envia un disparo y se verifica la recepción correcta (T5 alto).

    # Iteramos por diferentes niveles de amplitud (0.1 a 0.9)
    FOR    ${noise_level}    IN    0.1    0.3    0.5    0.7    0.9
        Log To Console    \n Probando con Nivel de Ruido: ${noise_level}

        # Ejecutamos la verificación para el nivel de la iteracion correspondiente
        Run Dependability Check    ${noise_level}
    END


*** Keywords ***
Run Dependability Check
    [Arguments]    ${noise_level}

    # Iniciamos el ruido
    Start Analog Noise Injection    ${noise_level}
    # Configuramos logs en el servidor para detectar eventos en T5
    Send Hil Command    ${RASPBERRY_PI_IP}    CONFIG_LOG,ALL,${RELAY_T0}
    Send Hil Command    ${RASPBERRY_PI_IP}    START_LOG

    # Enviamos el pulso de disparo
    Send Hil Command    ${RASPBERRY_PI_IP}    PULSE,${RELAY_T0},${CMD_DURATION}

    # Esperamos un poco mas del tiempo del pulso
    ${wait_time}=    Evaluate    ${CMD_DURATION} + 0.4
    Sleep    ${wait_time}s

    # Detenemos los logs
    Send Hil Command    ${RASPBERRY_PI_IP}    STOP_LOG
    # Detenemos la inyección de ruido
    Stop Analog Noise Injection

    # Obtenemos los logs
    ${logs}=    Send Hil Command    ${RASPBERRY_PI_IP}    GET_LOGS

    # Validamos que el log contenga eventos en T5
    Should Contain    ${logs}    "t5_ns": [1    msg=El comando se perdió con nivel de ruido ${noise_level}!

    Log    Prueba superada a nivel ${noise_level} de ruido.
    