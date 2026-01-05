*** Settings ***
Documentation       Control de Inyección de Ruido Analógico. Se comunica con el hil_server.py mediante sockets TCP para activar/desactivar el hilo de audio DSP.
Library             MyKeywords.py
Library             Collections

*** Variables ***
${RASPBERRY_PI_IP}    10.212.42.42      # IP por defecto, la GUI la reemplazará por la que el usuario indique
${HIL_PORT}           65432          # Puerto del servidor HIL
${NOISE_STABILIZATION_TIME}    0.5s    # Tiempo para estabilizar el buffer de audio (ALSA)

*** Keywords ***
Start Analog Noise Injection
    [Documentation]    Inicia la generación de ruido blanco en el DAC de la RPi.
    [Arguments]    ${amplitude}
    
    # Validamos que sea un número
    Convert To Number    ${amplitude}
    
    # Enviamos comando al servidor HIL (definido en hil_server.py)
    ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    NOISE_START,${amplitude}    ${HIL_PORT}
    # Verificamos que el servidor haya respondido ACK
    Should Contain    ${response}    ACK    msg=Fallo al iniciar ruido analógico: ${response}
    
    Log    Inyección de ruido iniciada al nivel: ${amplitude}
    
    # Esperamos a que el buffer de audio se llene y estabilice
    Sleep    ${NOISE_STABILIZATION_TIME}

Stop Analog Noise Injection
    [Documentation]    Detiene la generación de ruido y libera el recurso de audio.
        ${response}=    Send Hil Command    ${RASPBERRY_PI_IP}    NOISE_STOP    ${HIL_PORT}
    Should Contain    ${response}    ACK    msg=Fallo al detener ruido analógico
    Log    Inyección de ruido detenida.

Set Signal To Noise Ratio
    [Documentation]    Calcula la amplitud necesaria para una SNR dada (Opcional/Avanzado).
    ...                Requiere calibración previa (V_signal / V_noise).
    [Arguments]    ${target_snr_db}
    # Aquí podremos implementar la fórmula matemática si tenemos la calibración
    # Por ahora, usamos amplitud directa en los tests.
    Log    Setting SNR to ${target_snr_db} (Not implemented yet, using raw amplitude)