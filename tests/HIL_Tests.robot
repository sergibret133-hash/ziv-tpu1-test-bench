*** Settings ***
Library    MyKeywords.py
Documentation    Tests para controlar el Hardware-in-the-Loop (Raspberry Pi).

*** Variables ***
${RASPBERRY_PI_IP}    10.212.40.14      # IP por defecto, será sobrescrita por la GUI
${HIL_PORT}           65432          # Puerto del servidor HIL
${COMMAND_STR}    default

*** Test Cases ***
Send Input Command
    Send Hardware Input Command    ${COMMAND_STR}


*** Keywords ***
Send Hardware Input Command
    [Documentation]    Envía un comando genérico al servidor HIL.
    [Arguments]        ${command_str}
    # Llama a la keyword de Python que acabamos de crear
    ${response}=    Send HIL Command    ${RASPBERRY_PI_IP}    ${command_str}    port=${HIL_PORT}
    Log    Respuesta del servidor HIL: ${response}