*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    Collections
Library    String
Library    BuiltIn
Library    JSONLibrary


*** Variables ***
# MODIFICACIÓN: La ruta del fichero de sesión ahora se pasa como una variable desde la GUI.
# Ya no se define aquí.
${USER}            admin
${PASS}            Passwd%4002

${URL_COMPLETA}    https://${USER}:${PASS}@${IP_ADDRESS}

#OPEN AND CLOSE BROWSER PARAMETERS
${BROWSER}          chrome
${LOGOUT_BUTTON}    xpath=//button[contains(@class, 'p-button p-component p-button-rounded p-button-danger p-button-text p-button-icon-only')]
${LOGOUT_SURE}      xpath=//button[contains(@class, 'p-button p-component p-confirm-dialog-accept')]
${TPU_IMG}          xpath=//img[contains(@src, './static/media/tpu-1-300x130.868f04f7.jpg')]
${commands}         Input/Output Alias

${IP_ADDRESS}      default_ip
${SESSION_FILE_PATH}    ${EMPTY}
${SESSION_ALIAS}=    default_alias  # 'A' o 'B'

*** Test Cases ***
Open And Keep Browser Alive
    [Documentation]    Abre el navegador, inicia sesión, guarda los detalles de la sesión y espera.
    Log To Console    Iniciando sesión para ${SESSION_ALIAS} en IP ${IP_ADDRESS}

    Setup Chromium Options
    Open Broswer to Login page    ${URL_COMPLETA}    ${BROWSER}    ${SESSION_ALIAS}
    Wait Until Page Contains Element    xpath=//span[contains(@class, 'p-button-icon p-c pi pi-sign-out')]    timeout=50s
    Save Session Details
    Log To Console    El navegador está abierto y la sesión está activa. Esperando acciones...
    Sleep    2h  # Mantiene el proceso vivo durante 2 horas

*** Keywords ***
Open Broswer to Login page
    [Arguments]    ${url}    ${brows}    ${alias}
    # Crea un objeto de opciones de Chrome
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver

    # Añade todos los argumentos de tu lista @{options}
    FOR    ${option}    IN    @{options}
        Call Method    ${chrome_options}    add_argument    ${option}
    END

    Open Browser    ${url}    browser=${brows}    options=${chrome_options}    alias=${alias}
    Maximize Browser Window

Setup Chromium Options
    # Create chromium options list dynamically 
    @{options_list}=    Create List
    ...    --no-sandbox    
    # ...    --disable-gpu    
    ...    --disable-dev-shm-usage    
    ...    --disable-features=Gcm    
    # ...    --disable-component-update    
    # ...    --log-level=0    
    ...    --ignore-certificate-errors    
    # ...    --disable-web-security    
    ...    --allow-running-insecure-content
    Set Suite Variable    @{options}    @{options_list}

Save Session Details
    [Documentation]    Obtiene los detalles de la sesión de Selenium y los guarda en un fichero JSON.
    # Obtenemos la instancia de la librería SeleniumLibrary para acceder a sus propiedades internas
    ${selenium_lib}=    Get Library Instance    SeleniumLibrary
    
    # Usamos Evaluate para acceder a los atributos del objeto driver de forma segura
    ${session_id}=      Evaluate    $selenium_lib.driver.session_id
    ${executor_url}=    Evaluate    $selenium_lib.driver.service.service_url
    # # ${executor_url}=    Evaluate    $selenium_lib.driver.command_executor._url
    # ${executor_url}=    Evaluate    $selenium_lib.driver.command_executor.url 
    Log To Console    Session ID Obtenido: ${session_id}
    Log To Console    Executor URL Obtenido: ${executor_url}

    # Creamos el diccionario y lo guardamos en el fichero JSON
    ${session_data}=    Create Dictionary    session_id=${session_id}    executor_url=${executor_url}
    ${json_string}=     Evaluate    json.dumps(${session_data})    modules=json


    # Usamos la variable ${SESSION_FILE_PATH} que viene de la GUI
    Create File    ${SESSION_FILE_PATH}    ${json_string}
    Log    Detalles de sesión guardados en ${SESSION_FILE_PATH}