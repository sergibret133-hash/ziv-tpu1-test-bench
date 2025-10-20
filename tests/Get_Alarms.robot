
*** Settings ***
Library    SeleniumLibrary
Library    Collections
Library    String
Library    OperatingSystem

Library    BuiltIn
Library    XML
Library    Screenshot
Library    BrowserManager.py

Resource    Keep_Alive.robot


Suite Setup    Conectar A Navegador Existente    session_file=${ALARMS_SESSION_FILE}
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

*** Variables ***
${ALARMS_SESSION_FILE}    alarms_session.json
${ALARMS_DATA}    ${EMPTY}


*** Test Cases ***
Scrape And Return Alarms
    ${ALARMS_DATA}=    Get All Alarms

    ${alarms_json}=    Evaluate    json.dumps(${ALARMS_DATA})    json
    # Log    GUI_ALARMS::${alarms_json}
    Log To Console    GUI_ALARMS::${alarms_json}
    
    [Teardown]    Click Open Monitoring Folder
    
*** Keywords ***
Get All Alarms
    [Documentation]    Navega a la sección de alarmas y extrae el texto de las 3 tablas.

# 
# STATE OF THE ALARMS OF THE SYSTEM
    Setup Folder Section    System Alarms    STATE OF THE ALARMS OF THE SYSTEM
    ${system_alarms}=    Get System Alarms
    Setup Folder Section    Alarms Tp(1)    STATE OF THE ALARMS OF TELEPROTECTION (1)
    ${tp1_alarms}=       Get System Alarms
    Setup Folder Section    Alarms Tp(2)    STATE OF THE ALARMS OF TELEPROTECTION (2)
    ${tp2_alarms}=       Get System Alarms

    ${all_alarms}=    Create Dictionary
    ...    system=${system_alarms}
    ...    tp1=${tp1_alarms}
    ...    tp2=${tp2_alarms}

    RETURN    ${all_alarms}

Get System Alarms
    [Documentation]    Extrae el texto de todas las alarmas de sistema que están activas, gestionando posibles errores.
    # 0. Localizamos si hay Alarma de Falla de Modulo Activa
    ${xpath_module_failure_on}=    Set Variable    xpath=//div[@class='infoDatInpLab_content' and normalize-space()='THE ALARM OF MODULE FAILURE IS ACTIVATED.']
    # 1. Localizamos todos los iconos de alarma 'On'.
    ${xpath_alarmas_on}=    Set Variable    //img[contains(@src, 'ComAlarmOn.gif')]
    ${elementos_alarma}=    Get WebElements    ${xpath_alarmas_on}
    ${list_length}=    Get Length    ${elementos_alarma}
    # 2. Creamos una lista para guardar los nombres de las alarmas activas.
    @{alarmas_activas}=    Create List
    
    # Comprobamos que no haya falla general en el modulo
    ${module_failure_text}=    Set Variable    MODULE FAILURE ALARM ACTIVATED. CONSULT THE CHRONOLOGICAL REGISTER.
    ${module_failure_status}    ${nombre_alarma}=    Run Keyword And Ignore Error    Page Should Contain Element    ${xpath_module_failure_on}  

    IF    '${module_failure_status}' == 'PASS'        # Comprobamos si hay texto de falla general del modulo.
        Append To List    ${alarmas_activas}    ${module_failure_text}
        Log    Fallo General del Modulo.    WARN

    ELSE
        # 3. Iteramos sobre cada icono 'On' que hemos encontrado.
        FOR    ${index}    IN RANGE    0    ${list_length}
            ${xpath_img}=    Set Variable    (//img[contains(@src, 'ComAlarmOn.gif')])[${index + 1}]
            ${xpath_alarma}=    Set Variable    ${xpath_img}/ancestor::tr/td[@class='tDatInpLab']//div
        
            # 4. Intentamos obtener el texto de la alarma de forma segura.
            ${status}    ${nombre_alarma}=    Run Keyword And Ignore Error    Get Text    ${xpath_alarma}
        
            # 5. Si falla la lectura, ponemos un marcador claro.
            IF    '${status}' == 'FAIL'
                Log    No se pudo obtener el texto de una alarma (índice ${index + 1}).    WARN
                ${nombre_alarma}=    Set Variable    (alarma sin nombre)
            END
            # 6. Añadimos el nombre (o marcador) a la lista.
            Append To List    ${alarmas_activas}    ${nombre_alarma}
        END
    END
    # 7. Preparamos el texto final para mostrarlo en la GUI o logs.
    IF    ${alarmas_activas}
        ${texto_final}=    Catenate    SEPARATOR=\n    @{alarmas_activas}
    ELSE
        ${texto_final}=    Set Variable    No hay alarmas de sistema activas.
    END

    Log    Texto final de alarmas:\n${texto_final}
    RETURN    ${texto_final}




    # *********************************************************************************************************************
Setup Folder Section
    [Arguments]    ${section_name}    ${section_title}
    Click Open Folder    /
    Click Open Folder    MONITORING
    Open Section    ${section_name}
    Wait Section Title    ${section_title}
    Sleep    3s

Click Open Folder
    [Arguments]    ${folderName}
    # Check if the folder is already open
    ${is_open}    Run Keyword And Return Status    Page Should Contain Element    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0') and contains(@aria-expanded, 'true') and not(contains(@style, 'display: none;'))]
    IF    ${is_open}
    # If the folder is already open, log a message and do nothing. 
        Log To Console    Folder "${folderName}" is already open.
    ELSE
        Scroll Element Into View Softly    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
        ${button}  Get WebElement  xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
        Click Element  ${button}
        Sleep    0.3s
    END
Click Open Monitoring Folder
    Scroll Element Into View Softly    xpath=//span[contains(text(), "MONITORING")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
    ${monitoring_xpath}=    Set Variable    xpath=//span[@class='p-treenode-label' and normalize-space()='MONITORING']
    Click Element  ${monitoring_xpath}
    Sleep    0.3s
Open Section
    [Arguments]    ${section}
    ${locator}    Set Variable    xpath=//span[@class='p-treenode-label' and translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Scroll Element Into View Softly    ${locator}
 
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Click Element    ${locator}
    Sleep    0.1s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "${normalized_title}")]

Scroll Element Into View Softly
    [Arguments]    ${locator}
    ${element}=    Get WebElement    ${locator}
    Execute JavaScript    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});    ARGUMENTS    ${element}
    Sleep    0.5s
