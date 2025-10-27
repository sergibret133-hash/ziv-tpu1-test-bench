*** Settings ***
Library    SeleniumLibrary
Library    BrowserManager.py

Resource    Keep_Alive.robot


# Test Setup    Conectar a Navegador Existente    session_file=${SESSION_FILE}    # No podemos hacer esto aqui porque Settings no acepta variables dinámicas:(
# Creamos una Keyword intermedia para poder pasar la variable dinámica ${SESSION_FILE_PATH} desde la GUI
Test Setup    Connect To The Right Session
*** Variables ***
# SESSION VARIABLES
${SESSION_ALIAS}
${SESSION_FILE_PATH}

${SESSION_FILE}    session.json


*** Test Cases ***
Close All Browser Windows
    Cerrar Sesion Principal Y Salir    ${SESSION_ALIAS}

*** Keywords ***
Connect To The Right Session
    [Documentation]    Keyword intermedia que se usa como test_Setup para poder pasar la variable dinámica ${SESSION_FILE_PATH} desde la GUI y conectar a la sesión existente para posteriormente ejecutar el testcase que cierra la sesion del navegador pasado como variable.
    Conectar A Navegador Existente    ${SESSION_ALIAS}    ${SESSION_FILE_PATH}
