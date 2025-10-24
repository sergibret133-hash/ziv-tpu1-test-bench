*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    DateTime
Library    Screenshot
Library    BrowserManager.py

Resource    Keep_Alive.robot


Suite Setup    Run Keyword    Conectar A Navegador Existente    ${SESSION_ALIAS}    ${SESSION_FILE_PATH}
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

*** Variables ***
# SESSION VARIABLES
${SESSION_ALIAS}
${SESSION_FILE_PATH}
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

# ${terminal_title}    EUT Setup 1
${IP_ADDRESS}    10.212.43.87

${URL_COMPLETA}=    ${URL_BASE}${USER}:${PASS}@${IP_ADDRESS}
#popup login method
${TPU_WelcomeTitle_Type}    css=div.text-center.headerCenter.col h4
# ${TerminalTitle}    Terminal 1
#Section title

# ${Section_Type}    css=div.text-center.headerCenter.col h2

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
${BROWSER}          chrome
${LOGOUT_BUTTON}   xpath=//button[contains(@class, 'p-button p-component p-button-rounded p-button-danger p-button-text p-button-icon-only')]
${LOGOUT_SURE}   xpath=//button[contains(@class, 'p-button p-component p-confirm-dialog-accept')]
${TPU_IMG}    xpath=//img[contains(@src, './static/media/tpu-1-300x130.868f04f7.jpg')]
# ${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content  --disable-component-update  --disable-features=Gcm  --disable-dev-shm-usage  --no-sandbox

${commands}    Input/Output Alias

#************************************************************************************************************************
# INPUT ACTIVATION
# ${INPUT_INFO}    ${EMPTY}

${ACTIVATE_DEACTIVATE}    1
${DURATION}    0
# ${INPUTS_LIST}    ${EMPTY}
@{inputs_lii}    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1]
# ${INPUTS_LIST}    @{inputs_lii}
${INPUTS_LIST}    ${EMPTY}


*** Test Cases ***
# INPUT ASSIGNMENT TESTCASES:
Retrieve Inputs Activation State
    Setup Folder Section
    ${Current_State}    Current Activation_Desactivaton State
    ${INPUT_INFO}    Retrieve Inputs    ${Current_State}
    Log To Console    ${INPUT_INFO}
    # Set Suite Variable    ${INPUT_INFO}
Input Activation
    Setup Folder Section
    Input Activation/desactivation    ${ACTIVATE_DEACTIVATE}    ${DURATION}    ${INPUTS_LIST}


#*************************************************************************************************************************

*** Keywords ***
#INPUT ACTIVATION
Retrieve Inputs
    [Documentation]    Retrieve the Inputs State List ONLY when Inputs are ACTIVATED
    [Arguments]    ${Current_State}
    ${inputs}=    Create List

    # Run Keyword If    '${Current_State}' == '0'    Return From Keyword    ${inputs}
    ${checkboxs_xpath}=    Set Variable    xpath=//input[@name='dtpuMgmtTpuIoActivationMask']
    ${checkbox_elements}    Get WebElements    ${checkboxs_xpath}
    ${inputs_length}    Get Length    ${checkbox_elements}
    ${inputs_length}=    Evaluate    ${inputs_length} + 1

    FOR    ${index}    IN RANGE    1    ${inputs_length}
        ${input_xpath}=      Set Variable    xpath=(${checkboxs_xpath})[${index}]
        ${is_checked}=             Run Keyword And Return Status    Checkbox Should Be Selected    ${input_xpath}
        ${input_state}=            Set Variable If    ${is_checked}    1    0
        Append To List    ${inputs}    ${input_state}
    END

    Return From Keyword    ${inputs}

Input Activation/desactivation
    [Arguments]    ${Activate_Desactivate}    ${duration}=0    ${inputs_list}=[]
    [Documentation]    ${Activate_Desactivate}=1: Activate    ${Activate_Desactivate}=0: Desactivate inputs. Available duration values: 0 (Permanently), 5(s), 10(s), 30(s), 60(s), 600(s).
    ${current_state}    Current Activation_Desactivaton State

    # Validate Activate_Desactivate

    IF    ${current_state} == ${False} and '${Activate_Desactivate}' == '0'
        Log To Console    GUI_ERROR: ¡Las entradas ya están desactivadas!
        Return From Keyword

    ELSE IF    ${current_state} == ${False} and '${Activate_Desactivate}' == '1'
        # Restart Inputs Activation
        Input Activation Duration    ${duration}
        @{inputs_list_eval}=    Evaluate    ${inputs_list}
        FOR    ${input_state}    IN ENUMERATE    @{inputs_list_eval}
            ${index}=    Set Variable    ${input_state[0]}
            ${num_input}=    Evaluate    ${index} + 1
            Input Checkbox Selection    ${num_input}    ${input_state[1]}
        END
        Program    sInputAct_ON
        Enter Password Credentials
        Wait Until Progress Bar Reaches 100

    ELSE IF    ${current_state} == ${True} and '${Activate_Desactivate}' == '0'
        Program    sInputAct_OFF
        Wait Until Progress Bar Reaches 100

    ELSE IF    ${current_state} == ${True} and '${Activate_Desactivate}' == '1'
        Log To Console    GUI_ERROR: ¡Las entradas ya están activadas!
        Return From Keyword

    ELSE IF    ${current_state} == ${False} and '${Activate_Desactivate}' == '1' and '${inputs_list}' == '[]'
        Log To Console    GUI_ERROR: Para activar, se debe seleccionar al menos una entrada.
        Return From Keyword

    ELSE
        Log To Console    GUI_ERROR: Error inesperado al evaluar el estado de activación.
        Return From Keyword
    END
Current Activation_Desactivaton State
    [Documentation]    Return ${current_state}=1 if there are inputs active. Return ${current_state}=0 if there are NOT inputs activate.
    Sleep    2s
    ${current_state_xpath}=    Set Variable    xpath=//div[@class='infoDatInpLab_content' and text()='Deactivate']
    # Wait Until Element Is Visible    ${current_state_xpath}    timeout=5s    
    ${current_state}=    Run Keyword And Return Status    Element Should Be Visible    ${current_state_xpath}
    Log To Console    El estado detectado es: ${current_state}
    Return From Keyword    ${current_state}

Restart Inputs Activation
    # First we must count the max number of inputs
    ${rows_locator}=    Set Variable    xpath=//tr[@class="numCols_2 maxCols_3 numMustShow_3"]
    ${row_elements}=    Get WebElements    ${rows_locator}
    ${row_count}=    Get Length    ${row_elements}
    ${row_count}=    Evaluate    ${row_count} + 1
    FOR    ${num_inp}    IN RANGE    1    ${row_count}
        Input Checkbox Selection    ${num_inp}    0
    END

Input Checkbox Selection
    [Arguments]    ${num_input}    ${value}
    ${checkbox}=    Set Variable    xpath=(//tr[contains(@class, "numCols_2 maxCols_3 numMustShow_3")])[${num_input}]//input[@type='checkbox']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s
    Scroll Element Into View    ${checkbox}   
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}


Input Activation Duration
    [Arguments]    ${Duration}
    Validate Input Duration Value    ${Duration}
    
    ${locator}=    Set Variable    xpath=//select[@var_name='dtpuMgmtTpuIoActivationTime'][@var_index='0'] 
    Select From List By Value    ${locator}    ${Duration}



Validate Input Duration Value
    [Arguments]    ${Duration}
    [Documentation]    Only the following value numbers are available: 5(s), 10(s), 30(s), 60(s), 600(s) and 0 (Permanently)
    ${allowed_values}=    Evaluate    ['0', '5', '10', '30', '60', '600']

    # Convert the input duration to a string to ensure consistent comparison
    ${duration_as_string}=    Convert To String    ${Duration}

    # Check if the provided duration is in the list of allowed values
    ${duration_match}    Evaluate    any('${duration_as_string}' == word for word in @{allowed_values})
    IF    ${duration_match}
        Log    Duration '${duration_as_string}' is valid.
    ELSE
        Fail    Invalid duration: '${duration_as_string}'. Allowed numeric values are: 0 (Permanently), 5(s), 10(s), 30(s), 60(s), 600(s).
    END

#******************************************************************************************************************************************************************************
#******************************************************************************************************************************************************************************

Setup Folder Section
    Click Open Folder    /
    Click Open Folder    ALIGNMENT
    Open Section    Input activation
    Wait Section Title    INPUT CIRCUITS ACTIVATION

Open Broswer to Login page
    [Arguments]    ${url}    ${brows}
    # Crea un objeto de opciones de Chrome
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver

    # Añade todos los argumentos de tu lista @{options}
    FOR    ${option}    IN    @{options}
        Call Method    ${chrome_options}    add_argument    ${option}
    END

    Open Browser    ${url}    browser=${brows}    options=${chrome_options}
    Maximize Browser Window
Close Browser
    Close All Browsers
Type In Username
    [Arguments]    ${username}
    Maximize Browser Window
    Input Text    id=Username    ${username}

Type In Password
    [Arguments]    ${password}
    Input Text    id=Password    ${password}
Submit Credentials
    Click Button   name=toIniciar

Wait Login
    Wait Until Element Is Not Visible    ${TPU_IMG}    timeout=30s


Logout
    Execute JavaScript    window.scrollBy(0, -1000)
    Sleep    1s
    Click Element    ${LOGOUT_BUTTON}

Sure_LogOut 
    Click Element    ${LOGOUT_SURE}


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


Open Section
    [Arguments]    ${section}
    ${locator}    Set Variable    xpath=//li[contains(@class,'p-treenode p-treenode-leaf') and not(contains(@style, 'display: none;'))]//span[@class='p-treenode-label' and translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    Scroll Element Into View Softly    ${locator}
 
    Wait Until Element Is Visible    ${locator}    timeout=10s
    Click Element    ${locator}
    Sleep    0.1s
Scroll Until Visible
    [Arguments]    ${locator}
    # Check if the button is visible
    ${visible}    Run Keyword And Return Status    Element Should Be Visible    ${locator}
    WHILE    '${visible}' == 'False'
        Execute JavaScript    window.scrollBy(0, window.innerHeight / 1.5)
        Sleep    0.2s
        ${visible}    Run Keyword And Return Status    Element Should Be Visible    ${locator}
    END
    # Sleep    1s

Assign input/output to command
    [Arguments]    ${input}    ${command}
    #//div[contains(text(), "${input}")]:primero encuentra el texto input para cualquier <div> y seguidamente 
    #/ancestor-or-self::tr:  Busca el elemento <tr> (fila de tabla) más cercano, subiendo en la jerarquía del DOM.
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Select Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    Sleep    0.1s

Unassign input/ouptut to command
    [Arguments]    ${input}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Unselect Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    Sleep    0.1s
 

Scroll Element Into View Softly
    [Arguments]    ${locator}
    ${element}=    Get WebElement    ${locator}
    Execute JavaScript    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});    ARGUMENTS    ${element}
    Sleep    0.5s


Button
    [Arguments]    ${path_name}    ${button_name}    
    ${xpath_button}    Set Variable    xpath=//button[@name='${path_name}']//span[normalize-space(text())='${button_name}']
    Scroll Element Into View Softly    ${xpath_button}
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    Sleep    0.7s
ButtonNoSleep
    [Arguments]    ${path_name}    ${button_name}    
    ${xpath_button}    Set Variable    xpath=//button[@name='${path_name}']//span[normalize-space(text())='${button_name}']
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    # Sleep    0.7s

Retrieve
    [Arguments]    ${name}
    Button    ${name}    Retrieve
    Wait Until Progress Bar Reaches 100 V2
Program
    [Arguments]    ${button_name}
    Button    ${button_name}    Program
    Wait Until Progress Bar Reaches 100 V2

Program Old
    [Arguments]    ${button_name}
    Button    ${button_name}    Program
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.3s
    Log To Console    ${Handle_Alert_Detail}
    Wait Until Progress Bar Reaches 100
Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.5s
    Log    Waiting for the progress bar to reach 100%...
    Wait Until Keyword Succeeds
    ...    ${timeout}
    ...    ${poll_interval}
    ...    Element Attribute Value Should Be    xpath=//div[@role="progressbar"]    aria-valuenow    100
    Sleep    2s
Wait Until Progress Bar Reaches 100 V2_OLD
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, 'titulo_progress modal-title h4') and normalize-space(text())='Operation in progress...']
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

Wait Until Progress Bar Reaches 100 V2
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.3s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, "p-progressbar-label")]
    # Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
    Wait Until Page Does Not Contain    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario

#************************************************************************************************************************
#"Popup login" method Scripts 


Wait Title
    [Arguments]    ${TerminalTitle}    
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    120s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${normalized_title}"]

Enter Password Credentials
    Wait Until Element Is Visible    id=ModGetPassword    timeout=10s
    ${password_input_locator}=    Set Variable    xpath=//div[@id='DvUPassInput']//input[@id='PassInput' and @type='password' and @name='PassInput']
    Wait Until Element Is Visible    ${password_input_locator}    timeout=5s
    Input Text    ${password_input_locator}    ${INTERNAL_PASS}
    # Click Accept Button
    ${Accept_xpath}=    Set Variable    xpath=//div[@class='dvModGetPasswordCtrl']//input[@id='passBtnOK' and @type='button' and @value='Accept']
    Click Element    ${Accept_xpath}

Check If an Error Popup Appeared & Skip It
    ${Error_popup_button_xpath}=    Set Variable    xpath=//button[contains(@class, 'p-toast-icon-close p-link')]
    ${Error_popup_error_xpath}=    Set Variable    xpath=//div[contains(@class, 'p-toast-message-error')]
    ${Error_popup_error_detail_xpath}=    Set Variable    xpath=//div[contains(@class, 'p-toast-detail')]
    ${error_appeared}    Run Keyword And Return Status    Wait Until Element Is Visible    ${Error_popup_error_xpath}    1s
    IF    ${error_appeared}
        ${Error_Detail}    Get Text     ${Error_popup_error_detail_xpath}
        Log To Console    ${Error_Detail}
        Click Element    ${Error_popup_button_xpath}
        Return From Keyword    ${Error_Detail}
        Sleep    0.5s
    END
Check If Alert Appears and Handle It
    ${alert_present}=    Run Keyword And Return Status    Alert Should Be Present    timeout=1s
    IF    ${alert_present}
        ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=1s
        Log To Console    ${Handle_Alert_Detail}
        Return From Keyword    ${alert_present}
        Sleep    0.5s
    END
Print Table In The Console
    [Arguments]    @{table_for_print}

    ${separator}=         Set Variable    ========================================================
    ${header}=            Format String    | {:<10} | {:<20} | {:<22} |    Tone    Command activated    Command transmitted

    Log To Console    ${separator}
    Log To Console    ${header}
    Log To Console    ${separator}

    FOR    ${row}    IN    @{table_for_print}
        ${line_to_log}=    Format String    | {:<10} | {:<20} | {:<22} |    ${row}[0]    ${row}[1]    ${row}[2]
        Log To Console    ${line_to_log}
    END
    Log To Console    ${separator}

Checkbox Selection
    [Arguments]    ${checkbox}    ${value}
    #Checkbox = 0: Teleprotection disabled at start-up; Checkbox = 1: Teleprotection enabled at start-up
    ${checkbox}    Set Variable    //input[@name='${checkbox}']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s    
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}
    Sleep    0.1s
Input Text By Pressing Keys
    [Arguments]    ${locator}    ${text}
    # This keyword inputs text by pressing keys, simulating a user typing.
        Clear Element Text    ${locator}
        Press Keys    ${locator}    BACKSPACE
        Press Keys    ${locator}    BACKSPACE
        Press Keys    ${locator}    BACKSPACE
        # Click Element    locator=${powerboosting_level_xpath}
        Press Keys    ${locator}    ${text}
        Press Keys   ${locator}    TAB

Convert Module Text to Number
    [Arguments]    ${module_name}
    #Convert the module name to the corresponding number. We will use the list of modules to do it.
    IF    "${module_name}" == "IBTU"
        Return From Keyword    ${IBTU}
    ELSE IF    "${module_name}" == "IDTU"
        Return From Keyword    ${IDTU}
    ELSE IF    "${module_name}" == "IETU"
        Return From Keyword    ${IETU}
    ELSE IF    "${module_name}" == "IOTU"
        Return From Keyword    ${IOTU}
    ELSE IF    "${module_name}" == "ICTU"
        Return From Keyword    ${ICTU}
    ELSE IF    "${module_name}" == "IPTU"
        Return From Keyword    ${IPTU}
    ELSE IF    "${module_name}" == "IPTU.10"
        Return From Keyword    ${IPTU.10}
    ELSE IF    "${module_name}" == "IRTU"
        Return From Keyword    ${IRTU}
    ELSE IF    "${module_name}" == "DSTU"
        Return From Keyword    ${DSTU}
    ELSE IF    "${module_name}" == "MCTU"
        Return From Keyword    ${MCTU}
    ELSE IF    "${module_name}" == "IOCT"
        Return From Keyword    ${IOCT}
    ELSE IF    "${module_name}" == "IPIT"
        Return From Keyword    ${IPIT}
    ELSE IF    "${module_name}" == "IEPT"
        Return From Keyword    ${IEPT}
    ELSE IF    "${module_name}" == "IOCS"
        Return From Keyword    ${IOCS}
    ELSE IF    "${module_name}" == "ICPT"
        Return From Keyword    ${ICPT}
    ELSE
        Return From Keyword    None
    END  

# ******************************************************************************************************************************
# ******************************************************************************************************************************

#GENERAL VALIDATIONS
Validate Number In Range
    [Arguments]    ${number}    ${min}    ${max}
    ${is_number_0}    Evaluate    "${number}".isdigit()
    ${is_number_1}    Evaluate    "${min}".isdigit()
    ${is_number_2}    Evaluate    "${max}".isdigit()
    
    #We evaluate wether max & min are numbers or not. If they are not, we fail the test.

    Run Keyword If    not ${is_number_1}    Fail    No es un mínimo válido
    Run Keyword If    not ${is_number_2}    Fail    No es un máximo válido

    ${is_in_range}    Evaluate    (${min} <= ${number} <= ${max}) and (${is_number_0} == True)
    Return From Keyword    ${is_in_range}
    Should Be True    ${is_in_range}

Validate Number In Range - NEW
    [Documentation]    Now, this Keyword will accept int numbers (in the rev before wasn't able to do it)
    [Arguments]    ${number}    ${min}    ${max}
    ${is_number}    Run Keyword And Return Status    Convert To Integer    ${number}
    ${is_min}    Run Keyword And Return Status    Convert To Integer    ${min}
    ${is_max}    Run Keyword And Return Status    Convert To Integer    ${max}    
    
    #We evaluate wether max & min are numbers or not. If they are not, we fail the test.
    Run Keyword If    not ${is_number}    Fail    El numero introducido no es válido
    Run Keyword If    not ${is_min}    Fail    No es un mínimo válido
    Run Keyword If    not ${is_max}    Fail    No es un máximo válido

    ${is_in_range}    Evaluate    (${min} <= ${number} <= ${max})
    Return From Keyword    ${is_in_range}
    Should Be True    ${is_in_range}




