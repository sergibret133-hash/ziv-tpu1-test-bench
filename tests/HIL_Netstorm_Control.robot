*** Settings ***
Library    MyKeywords.py
Library   netstorm_controller.py
Library   Collections

Documentation    Tests para controlar el equipo Netstorm, de Albedo.


*** Variables ***
${NETSTORM_IP}    10.212.42.85
${NETSTORM_VNC_PASS}    Passwd@02

*** Test Cases ***
# ********************** TESTS CON INYECCIÓN DE RUIDO *********************** 
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
    
*** Keywords ***
