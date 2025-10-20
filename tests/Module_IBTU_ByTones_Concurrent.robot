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


Suite Setup    Conectar A Navegador Existente
Test Setup        Check And Handle Session Expired Popup
Suite Teardown

*** Variables ***
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
# ${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content
${commands}    Input/Output Alias

#************************************************************************************************************************
# MODULE CONFIG VARIABLES
#1st Section
${RX_OPERATION_MODE}    0
${LOCAL_PERIODICITY}    0
${REMOTE_PERIODICITY}    0
${SNR_THRESHOLD_ACTIVATION}    0
${SNR_THRESHOLD_DEACTIVATION}    3

#2nd Section
${TX_SCHEME}    0
${TX_GUARD_FREQUENCY}    0
${TX_APPLICATION_TYPE_LIST_STR}    ${EMPTY}
${TX_FREQUENCY_LIST_STR}    ${EMPTY}

${RX_SCHEME}    0
${RX_GUARD_FREQUENCY}    0
${RX_APPLICATION_TYPE_LIST_STR}    ${EMPTY}
${RX_FREQUENCY_LIST_STR}    ${EMPTY}

#3rd Section
${BY_TONES_INPUT_LEVEL}    -8
${BY_TONES_OUTPUT_LEVEL}    -2
${BY_TONES_POWER_BOOSTING}    1

*** Test Cases ***
#*************************************************************************************************************************
# 1st Section
Program IBTU ByTones S1 General
    Setup Folder Section

    Assign Reception Operation Mode    ${RX_OPERATION_MODE}    #Telesignalling
    LOCAL Automatic Link Test Periodicity Assign    ${LOCAL_PERIODICITY}
    REMOTE Automatic Link Test Periodicity Assign    ${REMOTE_PERIODICITY}
    Activation Threshold Assign for low Snr Ratio Alarm    ${SNR_THRESHOLD_ACTIVATION}
    Deactivation Threshold Assign for low Snr Ratio Alarm    ${SNR_THRESHOLD_DEACTIVATION}
    Program Old    sCOM

#*************************************************************************************************************************
# 2nd Section
Retrieve IBTU ByTones Full Configuration
    Setup Folder Section

    Retrieve Tones and Activated Command associated    1
    Retrieve Tones and Activated Command associated    0

Program IBTU ByTones S2 Frequencies
    Setup Folder Section

# TX
    Reset TX Frequency Selection

    Assign Scheme    1    ${TX_SCHEME}

# RX
    Reset RX Frequency Selection

    Assign Scheme    0    ${RX_SCHEME}

#******************************************************************
    Process Tone Application and Freq    ${TX_APPLICATION_TYPE_LIST_STR}    ${RX_APPLICATION_TYPE_LIST_STR}    ${TX_FREQUENCY_LIST_STR}    ${RX_FREQUENCY_LIST_STR}

    ${Tx_Guard_tone_frequencies}    Open Guard Tone Frequencies and Show them    1
    Frequency Selection    ${TX_GUARD_FREQUENCY}    ${Tx_Guard_tone_frequencies}

    ${Rx_Guard_tone_frequencies}    Open Guard Tone Frequencies and Show them    0
    Frequency Selection    ${RX_GUARD_FREQUENCY}    ${Rx_Guard_tone_frequencies}
    
    Program Old    sCOM

#*************************************************************************************************************************
# 3rd Section
Program IBTU ByTones S3 Levels
    Setup Folder Section

    Input Level    ${BY_TONES_INPUT_LEVEL}

    Power Boosting    ${BY_TONES_POWER_BOOSTING}

    Output Level    ${BY_TONES_OUTPUT_LEVEL}

    Program Old    sCOM
    Check If Alert Appears and Handle It

#*************************************************************************************************************************

*** Keywords ***
Setup Folder Section
    Click Open Folder    /
    Click Open Folder    EQUIPMENT
    Open Section    Basic Configuration
    Wait Section Title    BASIC CONFIGURATION
    Sleep    1s
    Check if Telep available and Open Section
    Open Line Interface Section

Clean Ghost Windows
    [Documentation]    Busca la ventana principal (la de la TPU) y cierra todas las demás.
    ${main_handle}=    Set Variable    ${None}
    ${all_handles}=    Get Window Handles
    
    # Primero, iteramos para encontrar el "handle" de nuestra ventana principal
    FOR    ${handle}    IN    @{all_handles}
        Switch Window    ${handle}
        ${url}=    Get Location
        # Usamos la variable ${IP_ADDRESS} para identificar la ventana correcta
        IF    "${IP_ADDRESS}" in "${url}"
            ${main_handle}=    Set Variable    ${handle}
            BREAK
        END
    END

    # Si por alguna razón no encontramos la ventana principal, detenemos el test
    Run Keyword If    '${main_handle}' == '${None}'    Fail    No se encontró la ventana principal de la TPU.

    # Ahora, cerramos todas las demás ventanas que no sean la principal
    FOR    ${handle}    IN    @{all_handles}
        IF    "${handle}" != "${main_handle}"
            Switch Window    ${handle}
            Close Window
        END
    END
    
    # Finalmente, nos aseguramos de que el foco vuelve a la ventana principal
    Switch Window    ${main_handle}
Check if Telep available and Open Section
    ${Telep_name_to_config}=    Set Variable    IBTU
    ${available_modules}=    Detect Available Modules
    ${available_modules_names}=    Set Variable    ${available_modules}[0]    # It's a list!
    ${available_modules_commands}=    Set Variable    ${available_modules}[1]    # It's a list!

    ${Telep_number_to_config}    Check if Telep available and Return TP ID    ${Telep_name_to_config}    ${available_modules_names}
    Set Suite Variable    ${available_modules_commands}
    Set Suite Variable    ${Telep_number_to_config}

Open Line Interface Section
    Open Line Interface Section Associated To Teleprotection    ${Telep_number_to_config}

Get Full Matching Element
    [Arguments]    ${substring_to_find}    ${list_to_search}
    ${full_element}=    Evaluate    next((word for word in @{list_to_search} if '${substring_to_find}' in word), None)
    Return From Keyword    ${full_element}

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



Scroll Element Into View Softly
    [Arguments]    ${locator}
    ${element}=    Get WebElement    ${locator}
    Execute JavaScript    arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});    ARGUMENTS    ${element}
    Sleep    0.5s


Button
    [Arguments]    ${path_name}    ${button_name}    
    ${xpath_button}    Set Variable    xpath=//button[@name='${path_name}']//span[normalize-space(text())='${button_name}']
    # Sleep    0.5s
    Wait Until Page Contains Element    ${xpath_button}
    Scroll Element Into View Softly    ${xpath_button}
    Wait Until Element Is Visible    ${xpath_button}    timeout=5s
    Click Element    ${xpath_button}
    Sleep    1s
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
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.3s
    Log To Console    ${Handle_Alert_Detail}
    Wait Until Progress Bar Reaches 100 V2
Program Old
    [Arguments]    ${button_name}
    Button    ${button_name}    Program
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.5s
    Log To Console    ${Handle_Alert_Detail}
    Wait Until Progress Bar Reaches 100

Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.3s
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
#************************************************************************************************************************
# ******************************************************************************************************************************
Get Command
    [Arguments]    ${name}    ${var_index}
    ${command}    Set Variable    //input[@name='${name}' and @var_index='${var_index}']
    Return From Keyword    ${command}

Checkbox Selection
    [Arguments]    ${checkbox}    ${value}
    #Checkbox = 0: Teleprotection disabled at start-up; Checkbox = 1: Teleprotection enabled at start-up
    ${checkbox}    Set Variable    //input[@name='dtproCfgEnedisDisabledAtStartUp']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s    
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}
    Sleep    0.1s
# <input type="checkbox" name="dtpuMgmtTpuIoActivationMask">
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

#COMMAND ASSIGNMENTS KEYWORDS
Get Text If Locator Exists
    [Arguments]    ${locator}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${locator}
    # ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    timeout=1s # Pequeño timeout

    IF    ${status}
        ${text}=    Get Text    ${locator}
        Return From Keyword    ${text}
    ELSE
        Log    Element with locator '${locator}' not found. Returning default value '${default_value}'.    WARN
        Return From Keyword    ${default_value}
    END
 
Get Attribute If Locator Exists
    [Arguments]    ${locator}    ${Attr_name}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Page Should Contain Element    ${locator}
    # ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    timeout=1s # Pequeño timeout

    IF    ${status}
        ${text}=    SeleniumLibrary.Get Element Attribute    ${locator}    ${Attr_name}
        Return From Keyword    ${text}
    ELSE
        Log    Element with locator '${locator}' not found. Returning default value '${default_value}'.    WARN
        Return From Keyword    ${default_value}
    END

Get Text If Element Exists
    [Arguments]    ${element}    ${default_value}='N/A'
    ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${element}

    IF    ${status}
        ${text}=    Get Text    ${element}
        Return From Keyword    ${text}
    ELSE
        Log    Element with locator '${element}' not found. Returning default value '${default_value}'.    WARN
        Return From Keyword    ${default_value}
    END




# ******************************************************************************************************************************
# ******************************************************************************************************************************
# CONFIG MODULES KEYWORDS
Detect Available Modules
    [Documentation]    Detects the available teleprotection modules in the "Number of commands" table. Morover, it returns a list of the available modules' names and a list of the available modules' commands. This keyword only can be used in the "Basic Configuration" section. It returns 2 lists. The first one contains the names of the available modules, and the second one contains the number of commands for each module (Tx_Tp1_Comm, Tx_Tp2_Comm, Rx_Tp1_Comm, Rx_Tp2_Comm). 
    
    ${available_modules_names}=    Create List
    ${available_modules_commands}=    Create List

    #############################################################################################################################
    # Locate "Teleprotection modules" in the "Number of commands" table by its input name and var_index (TP1 or TP2).
    ${teleprotection_modules_xpath}=    Set Variable    //div[contains(text(), 'Teleprotection modules')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Teleprotection modules" row.
    ${Tp1_xpath}=    Set Variable    xpath=${teleprotection_modules_xpath}//ancestor::tr//input[contains(@name, 'dclientComAssignView') and contains(@var_index, '0')]
    ${Tp2_xpath}=    Set Variable    xpath=${teleprotection_modules_xpath}//ancestor::tr//input[contains(@name, 'dclientComAssignView') and contains(@var_index, '1')]

    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_text}=    Get Attribute If Locator Exists    ${Tp1_xpath}    value
    ${Tp2_text}=    Get Attribute If Locator Exists    ${Tp2_xpath}    value

    # Add them to the list.
    Append To List    ${available_modules_names}    ${Tp1_text}
    Append To List    ${available_modules_names}    ${Tp2_text}
    # Log the available modules.
    Log To Console    \nAvailable modules detected: ${available_modules_names}\n

    #############################################################################################################################
    # Locate "Number of commands in transmission" in the "Number of commands" table.
    ${num_Tx_commands_xpath}=    Set Variable    //div[contains(text(), 'Number of commands in transmission')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Number of commands in transmission" row.
    ${Tp1_tx_commands_xpath}=    Set Variable    xpath=${num_Tx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumTransmitCommands') and contains(@var_index, '0')]
    ${Tp2_tx_commands_xpath}=    Set Variable    xpath=${num_Tx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumTransmitCommands') and contains(@var_index, '1')]

    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_tx_commands_text}=    Get Attribute If Locator Exists    ${Tp1_tx_commands_xpath}    value
    ${Tp2_tx_commands_text}=    Get Attribute If Locator Exists    ${Tp2_tx_commands_xpath}    value


    # Locate "Number of commands in reception" in the "Number of commands" table.
    ${num_Rx_commands_xpath}=    Set Variable    //div[contains(text(), 'Number of commands in reception')]
    #  Get the Tp1 and Tp2 XPaths relative to the "Number of commands in reception" row.
    ${Tp1_rx_commands_xpath}=    Set Variable    xpath=${num_Rx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumReceiveCommands') and contains(@var_index, '0')]
    ${Tp2_rx_commands_xpath}=    Set Variable    xpath=${num_Rx_commands_xpath}//ancestor::tr//input[contains(@name, 'dtproCfgNumReceiveCommands') and contains(@var_index, '1')]
    
    # Get the text of the Tp1 and Tp2 elements.
    ${Tp1_rx_commands_text}=    Get Attribute If Locator Exists    ${Tp1_rx_commands_xpath}    value
    ${Tp2_rx_commands_text}=    Get Attribute If Locator Exists    ${Tp2_rx_commands_xpath}    value

    # Add them to the list.
    Append To List    ${available_modules_commands}    ${Tp1_tx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp2_tx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp1_rx_commands_text}
    Append To List    ${available_modules_commands}    ${Tp2_rx_commands_text}
    # Log the available modules.
    Log To Console    \nAvailable modules commands: ${available_modules_commands}\n

    # Return the list of available modules.
    Return From Keyword    ${available_modules_names}    ${available_modules_commands}
    

Check if Telep available and Return TP ID
    [Arguments]    ${Telep_name_to_config}    ${available_TPs}
    [Documentation]    Checks if the specified teleprotection module is available in the list of available modules. If it is, it opens the corresponding section. Morover, it returns de TP ID associated to the module.
    ${index}=    Set Variable    ${-1}  # Initialize to -1 in case the module is not found
    ${telep-match}    Evaluate    any('${Telep_name_to_config}' in word for word in @{available_TPs})
    IF    ${telep-match}
        Log    Teleprotection module ${Telep_name_to_config} is available.
        ${Full_Tp_Name}    Get Full Matching Element    ${Telep_name_to_config}    ${available_TPs}
        Log To Console    Full Teleprotection module name: ${Full_Tp_Name}
        ${index}=    Evaluate    ${available_TPs}.index('${Full_Tp_Name}')
        ${Telep_number_to_config}=    Evaluate    ${index} + 1
        Log    Modulo indicado (${Telep_name_to_config}) pertenece a TP${Telep_number_to_config}
    ELSE
        Fail    Teleprotection module ${Telep_name_to_config} is not available in the detected modules: ${available_TPs}
    END
    Return From Keyword    ${Telep_number_to_config}

Open Line Interface Section Associated To Teleprotection
    [Arguments]    ${Telep_number_to_config}
    [Documentation]    Opens the Line Interface section associated to the specified teleprotection module.
    Click Open Folder    Line Interfaces
    Open Section    Teleprotection(${Telep_number_to_config}) 

Open INV_CMD Conditions Section Associated To Teleprotection
    [Arguments]    ${Telep_number_to_config}
    [Documentation]    Opens the INV_CMD Conditions section associated to the specified teleprotection module.
    Click Open Folder    Line Interfaces
    Open Section    INV_CMD Conditions TP${Telep_number_to_config}

# ******************************************************************************************************************************
# ************************************************************************************************************************
#IBTU_ByTones MODULE CONFIG
#1st Section
LOCAL Automatic Link Test Periodicity Assign
    [Arguments]    ${link_test_periodicity_hours}
    ${is_in_range}    Validate Number In Range    ${link_test_periodicity_hours}    0    24
    IF    ${is_in_range}
        ${link_test_periodicity_hours_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproTestMgmtAutomaticTestPeriodicityHours')]
        # Click Element    ${link_test_periodicity_hours_xpath}
        Clear Element Text    ${link_test_periodicity_hours_xpath}
        Press Keys    ${link_test_periodicity_hours_xpath}    ${link_test_periodicity_hours}
        Press Key     ${link_test_periodicity_hours_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    link_test_periodicity_hours is not a valid number. Value should be btw 0 - 24h
    END
    
REMOTE Automatic Link Test Periodicity Assign
    [Arguments]    ${link_test_periodicity_hours}
    ${is_in_range}    Validate Number In Range    ${link_test_periodicity_hours}    0    24
    IF    ${is_in_range}
        ${link_test_periodicity_hours_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproTestMgmtAutomaticTestRemote')]
        # Click Element    ${link_test_periodicity_hours_xpath}
        Clear Element Text    ${link_test_periodicity_hours_xpath}
        Press Keys    ${link_test_periodicity_hours_xpath}    ${link_test_periodicity_hours}
        Press Key     ${link_test_periodicity_hours_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    link_test_periodicity_hours is not a valid number. Value should be btw 0 - 24h
    END
    
Activation Threshold Assign for low Snr Ratio Alarm
    [Documentation]    Deactivation threshold for low signal-to-noise ratio alarm (0 to 18 dB). It is recommended first configuring the Deactivation Threshold.
    [Arguments]    ${Snr_Threshold}
    ${is_in_range}    Validate Number In Range    ${Snr_Threshold}    0    18
    IF    ${is_in_range}
        ${Snr_Threshold_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproLowSnrThreshold')]
        # Click Element    ${Snr_Threshold_xpath}
        Clear Element Text    ${Snr_Threshold_xpath}
        Press Keys    ${Snr_Threshold_xpath}    ${Snr_Threshold}
        Press Key     ${Snr_Threshold_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    Threshold is not a valid number. Value should be btw 0 - 18dB.
    END

Deactivation Threshold Assign for low Snr Ratio Alarm
    [Documentation]    Deactivation threshold for low signal-to-noise ratio alarm (2 to 20 dB).
    [Arguments]    ${Snr_Threshold}
    ${is_in_range}    Validate Number In Range    ${Snr_Threshold}    2    20
    IF    ${is_in_range}
        ${Snr_Threshold_xpath}=    Set Variable    xpath=//input[contains(@name, 'dtproHighSnrThreshold')]
        # Click Element    ${Snr_Threshold_xpath}
        Clear Element Text    ${Snr_Threshold_xpath}
        Press Keys    ${Snr_Threshold_xpath}    ${Snr_Threshold}
        Press Key     ${Snr_Threshold_xpath}    \\09
        ${error}    Check If an Error Popup Appeared & Skip It
        Log To Console    ${error}
    ELSE
        Fail    Threshold is not a valid number. Value should be btw 2 - 20dB.
    END
    
Assign Reception Operation Mode
    [Documentation]    Assign to the Command Number passed as an argument the Reception Operation Mode Selected. ${Reception_Operation_Mode} = 0 : Normal. ${Reception_Operation_Mode} = 1 : Telesignalling
    [Arguments]    ${Reception_Operation_Mode}
    # ${Command_Letter}    Convert Command Num To Letter    ${Command}
    # ${Mode_box_xpath}=    Set Variable    xpath=//select[contains(@var_name,'dtproFskRx${Command_Letter}Mode')]
    ${Mode_box_xpath}=    Set Variable    xpath=//div[text()= 'Reception operation mode']/ancestor-or-self::tr//div[@class='infoInpSelect']/select[@var_name='dtproRxMode']
    Select From List By Value    ${Mode_box_xpath}    ${Reception_Operation_Mode}
    Check If Alert Appears and Handle It

#*************************************************************************************************************************************************************

#2nd Section
Retrieve Tones and Activated Command associated
    [Arguments]    ${TX_RX_type}
    [Documentation]    TX_RX_type is passed considering: '1': TX ; '0': RX.

    # Retrieve Scheme and Guard Tone Data
    ${TX_Scheme_xpath}=    Set Variable    xpath=//select[@var_name='dtproTxSchema']
    ${RX_Scheme_xpath}=    Set Variable    xpath=//select[@var_name='dtproRxSchema']
    
    ${TX_Scheme}    SeleniumLibrary.Get Element Attribute    ${TX_Scheme_xpath}    value
    ${RX_Scheme}    SeleniumLibrary.Get Element Attribute    ${RX_Scheme_xpath}    value 

    ${TX_GUARD_TONE_FREQ_xpath}=    Set Variable    xpath=//input[@name='dtproCommand0CfgTransmitFreq']
    ${TX_GUARD_TONE_FREQ}    SeleniumLibrary.Get Element Attribute    ${TX_GUARD_TONE_FREQ_xpath}    value
    ${RX_GUARD_TONE_FREQ_xpath}=    Set Variable    xpath=//input[@name='dtproCommand0CfgReceiveFreq']
    ${RX_GUARD_TONE_FREQ}    SeleniumLibrary.Get Element Attribute    ${RX_GUARD_TONE_FREQ_xpath}    value

    # Print current Scheme and Guard Tone Frequency
    IF    ${TX_RX_type} == 1
        Log    \${IBTU_TX_SCHEME} = ${TX_Scheme}
        Log    \${IBTU_TX_GUARD_TONE_FREQ} = ${TX_GUARD_TONE_FREQ}
    ELSE
        Log    \${IBTU_RX_SCHEME} = ${RX_Scheme}
        Log    \${IBTU_RX_GUARD_TONE_FREQ} = ${RX_GUARD_TONE_FREQ}
    END

    #Retrieve Tone	Command activated	Command transmitted	Columns
    # Obtain row xpath
    IF    ${TX_RX_type} == 1 
        ${rows_xpaths}=    Set Variable    (//h6[text()='Local transmission frequencies and remote reception times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
        # ${rows_xpaths}=    Set Variable    xpath=//h6[contains(text(), 'Local transmission frequencies and remote reception times')]

    ELSE IF    ${TX_RX_type} == 0
        ${rows_xpaths}=    Set Variable    (//h6[text()='Local reception frequencies and transmission times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
        # ${rows_xpaths}=    Set Variable    xpath=//h6[text()='Local reception frequencies and transmission times']

    ELSE
        Fail    TX_RX_type introduced is not valid. TX_RX_type is passed considering: '1': TX ; '0': RX
    END
    Wait Until Element Is Visible    xpath=${rows_xpaths}
    ${row_elements}=    Get WebElements    xpath=${rows_xpaths}
    @{command_table}=    Create List
    ${row_count}=    Get Length    ${row_elements}
    ${row_count}=    Evaluate    ${row_count} + 1
    # We iterate and obtain the data
    FOR    ${tr_index}    IN RANGE    2    ${row_count}
        ${tone_num}=    Evaluate    ${tr_index} - 1
        # First, we have to locate the <td> element within the current element_tr
        ${cell_tone_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[2]//div[@class='infoDatInpLab_content']
        ${cell_activated_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[3]//div[@class='infoDatInpLab_content']
        ${cell_transmitted_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[4]//div[@class='infoUsrTxtPart']
        IF    ${TX_RX_type} == 1 
            ${application_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[5]//select[@var_name='dtproCommand${tone_num}CfgTransmitTime']
            ${frequency_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[6]//input[@name='dtproCommand${tone_num}CfgTransmitFreq']
        ELSE
            ${application_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[5]//select[@var_name='dtproCommand${tone_num}CfgReceiveTime']
            ${frequency_xpath}=    Set Variable    xpath=((${rows_xpaths})[${tr_index}]/td)[6]//input[@name='dtproCommand${tone_num}CfgReceiveFreq']
        END
        ${tone}=          Get Text    ${cell_tone_xpath}
        ${activated}=     Get Text    ${cell_activated_xpath}
        ${transmitted}=   Get Text    ${cell_transmitted_xpath}
        ${application}=    SeleniumLibrary.Get Element Attribute    ${application_xpath}    value
        ${frequency}=     SeleniumLibrary.Get Element Attribute    ${frequency_xpath}    value

        ${current_row}=    Create List    ${tone}    ${activated}    ${transmitted}    ${application}    ${frequency}
        Append To List    ${command_table}    ${current_row}
    END


    IF    ${TX_RX_type} == 1
        Log    \${IBTU_TX_TONES} = ${command_table}
    ELSE
        Log    \${IBTU_RX_TONES} = ${command_table}
    END

    Return From Keyword    @{command_table}
Assign Scheme
    [Documentation]    Assign the scheme passed as an argument. Possible option are: '0': 2+2 (1) ; '4': 2+2 (2) ; '1': 3+1 (1) ; '2': 3+1 (2). TX_RX_type is passed considering: '1': TX ; '0': RX
    [Arguments]    ${TX_RX_type}    ${Scheme}
    IF    ${TX_RX_type} == 0
        ${Scheme_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproRxSchema']
    ELSE IF    ${TX_RX_type} == 1
        ${Scheme_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproTxSchema']
    ELSE
        Fail    TX_RX_type introduced is not valid. TX_RX_type is passed considering: '1': TX ; '0': RX
    END

    Wait Until Element Is Visible    ${Scheme_xpath}    timeout=5s
    Scroll Element Into View Softly    ${Scheme_xpath}

    Select From List By Value    ${Scheme_xpath}    ${Scheme}
    
    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=1s
    Log To Console    ${Handle_Alert_Detail}

Open Guard Tone Frequencies and Show them
    [Arguments]    ${TX_RX}
        Button    sFrT_0    Frequency selection
        ${frequencies_list}    Show and Return Available frequencies List
        Return From Keyword    ${frequencies_list}

Assign TX Application Type To Tone
    [Documentation]    Assign for the Tone & Command Activated associated passed as an argument the Application Type Selected. ${Application_Operation_Mode} = 0 : Blocking. ${Application_Operation_Mode} = 1 : Permissive. ${Application_Operation_Mode} = 2 : Direct. 
    [Arguments]    ${Tone}    ${Application_Operation_Mode}
    ${Application_box_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproCommand${Tone}CfgTransmitTime']
    Wait Until Element Is Visible    ${Application_box_xpath}    timeout=3s
    Scroll Element Into View Softly    ${Application_box_xpath}
    Select From List By Value    ${Application_box_xpath}    ${Application_Operation_Mode}

    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.5s
    Log To Console    ${Handle_Alert_Detail}

Assign RX Application Type To Tone
    [Documentation]    Assign to the Command Number passed as an argument the Application Type Selected. ${Application_Operation_Mode} = 0 : Blocking. ${Application_Operation_Mode} = 1 : Permissive. ${Application_Operation_Mode} = 2 : Direct. 
    [Arguments]    ${Tone}    ${Application_Operation_Mode}
    ${Application_box_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproCommand${Tone}CfgReceiveTime']
    Wait Until Element Is Visible    ${Application_box_xpath}    timeout=3s
    Scroll Element Into View Softly    ${Application_box_xpath}
    Select From List By Value    ${Application_box_xpath}    ${Application_Operation_Mode}

    ${Handle_Alert_Detail}    Run Keyword And Return Status    Handle Alert    action=ACCEPT    timeout=0.5s
    Log To Console    ${Handle_Alert_Detail}

Autoconfig Apllication Type
    [Documentation]    It is recommended making a TX or RX Reset Frequency Selection BEFORE USING THIS KEYWORD. Autoconfig the same Application Operation Mode to all available channels. TX_RX_type is passed considering: '1': TX ; '0': RX. ${Application_Operation_Mode} = 0 : Blocking. ${Application_Operation_Mode} = 1 : Permissive. ${Application_Operation_Mode} = 2 : Direct. 
    [Arguments]    ${TX_RX_type}    ${Application_Operation_Mode}
    # Obtain row xpath
    IF    ${TX_RX_type} == 1 
        ${rows_xpaths}=    Set Variable    (//h6[text()='Local transmission frequencies and remote reception times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
        # ${rows_xpaths}=    Set Variable    xpath=//h6[contains(text(), 'Local transmission frequencies and remote reception times')]

    ELSE IF    ${TX_RX_type} == 0
        ${rows_xpaths}=    Set Variable    (//h6[text()='Local reception frequencies and transmission times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
        # ${rows_xpaths}=    Set Variable    xpath=//h6[text()='Local reception frequencies and transmission times']
    ELSE
        Fail    TX_RX_type introduced is not valid. TX_RX_type is passed considering: '1': TX ; '0': RX
    END

    Wait Until Element Is Visible    xpath=${rows_xpaths}
    ${row_elements}=    Get WebElements    xpath=${rows_xpaths}
    ${row_count}    Get Length    ${row_elements}

    FOR    ${tone}    IN RANGE    1    ${row_count}
        IF    ${TX_RX_type} == 1
            Assign TX Application Type To Tone    ${tone}    ${Application_Operation_Mode}
        ELSE IF    ${TX_RX_type} == 0
            Assign RX Application Type To Tone    ${tone}    ${Application_Operation_Mode}
        ELSE
            Fail    TX_RX_type introduced is not valid. TX_RX_type is passed considering: '1': TX ; '0': RX
        END
    END

Process Tone Application and Freq
    [Arguments]    ${TX_application_type_list_str}    ${RX_application_type_list_str}    ${TX_Frequency_List_str}    ${RX_Frequency_List_str}
    # Convertir las matrices de texto a listas de Robot Framework
    ${TX_application_type_list}=    Evaluate    ${TX_application_type_list_str}
    ${RX_application_type_list}=    Evaluate    ${RX_application_type_list_str}

    ${TX_Frequency_List}=    Evaluate    ${TX_Frequency_List_str}
    ${RX_Frequency_List}=    Evaluate    ${RX_Frequency_List_str}

    # Recorrer y programar la lista de frecuencias (TX).
    ${tx_length}    Get Length    ${TX_application_type_list}
    ${tx_length}=    Evaluate    ${tx_length} + 1
    FOR    ${tx_tone_num}    IN RANGE    1    ${tx_length}
        ${list_index}=    Evaluate    ${tx_tone_num} - 1
        ${application_state}=    Get From List    ${TX_application_type_list}    ${list_index}
        Assign TX Application Type To Tone    ${tx_tone_num}    ${application_state}
        Open TX Frequencies and Show Them    ${tx_tone_num}

        ${frequency}=    Get From List    ${TX_Frequency_List}    ${list_index}
        Frequency Selection    ${frequency}    ${TX_Frequency_List}
    END

    # Recorrer y programar la lista de frecuencias (RX)
    ${rx_length}    Get Length    ${RX_application_type_list}
    ${rx_length}=    Evaluate    ${rx_length} + 1
    FOR    ${rx_tone_num}    IN RANGE    1    ${rx_length}
        ${list_index}=    Evaluate    ${rx_tone_num} - 1
        ${application_state}=    Get From List    ${RX_application_type_list}    ${list_index}
        Assign RX Application Type To Tone    ${rx_tone_num}    ${application_state}
        Open TX Frequencies and Show Them    ${rx_tone_num}

        ${frequency}=    Get From List    ${RX_Frequency_List}    ${list_index}
        Frequency Selection    ${frequency}    ${RX_Frequency_List}
    END

Reset TX Frequency Selection
    [Documentation]    Change the value of "Scheme" to a different one from the actual. This way, all the frequencies will be reset to none.
    ${Scheme_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproTxSchema']
    Wait Until Element Is Visible    ${Scheme_xpath}    timeout=5s
    ${current_label}=    Get Selected List Label    ${Scheme_xpath}
    ${current_value}=    Get Selected List Value    ${Scheme_xpath}

    Log To Console    Texto visible actual: ${current_label}
    Log To Console    Valor interno ('value') actual: ${current_value}

    ${selected_value}=    Set Variable    0
    # '0': 2+2 (1) ; '4': 2+2 (2) ; '1': 3+1 (1) ; '2': 3+1 (2)
    IF    ${current_value} == 0
        ${selected_value}=    Set Variable    1
    ELSE IF    ${current_value} == 4
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 1
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 2
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 3
        ${selected_value}=    Set Variable    0
    ELSE
        Fail    current_value introduced is not valid. Available values to select:  '0': 2+2 (1) ; '4': 2+2 (2) ; '1': 3+1 (1) ; '2': 3+1 (2)
    END
    
    Assign Scheme    1    ${selected_value}

Reset RX Frequency Selection
    [Documentation]    Change the value of "Scheme" to a different one from the actual. This way, all the frequencies will be reset to none.
    ${Scheme_xpath}=    Set Variable    xpath=//div[@class='infoInpSelect']/select[@var_name= 'dtproRxSchema']
    Wait Until Element Is Visible    ${Scheme_xpath}    timeout=5s

    ${current_label}=    Get Selected List Label    ${Scheme_xpath}
    ${current_value}=    Get Selected List Value    ${Scheme_xpath}

    
    Log To Console    Texto visible actual: ${current_label}
    Log To Console    Valor interno ('value') actual: ${current_value}

    ${selected_value}=    Set Variable    0
    # '0': 2+2 (1) ; '4': 2+2 (2) ; '1': 3+1 (1) ; '2': 3+1 (2)
    IF    ${current_value} == 0
        ${selected_value}=    Set Variable    1
    ELSE IF    ${current_value} == 4
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 1
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 2
        ${selected_value}=    Set Variable    0
    ELSE IF    ${current_value} == 3
        ${selected_value}=    Set Variable    0
    ELSE
        Fail    current_value introduced is not valid. Available values to select:  '0': 2+2 (1) ; '4': 2+2 (2) ; '1': 3+1 (1) ; '2': 3+1 (2)
    END
    
    Assign RX Application Type To Tone    1    ${selected_value}

Open TX Frequencies and Show Them
    [Documentation]    Crucial to Make a "Reset TX Frequency Selection" before! Crucial to Make frequency assignment in ascendent channel order (C1,C2,C3,...). 
    [Arguments]    ${Tone}
    # Obtain row xpath
    ${rows_xpaths}=    Set Variable    (//h6[text()='Local transmission frequencies and remote reception times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
    Wait Until Element Is Visible    xpath=${rows_xpaths}
    ${row_elements}=    Get WebElements    xpath=${rows_xpaths}
    ${row_count}    Get Length    ${row_elements}
    ${available_tones}=    Evaluate    ${row_count} - 1
    ${available_tone}    Evaluate    ${Tone} <= ${available_tones}
    IF    ${available_tone}
        Button    sFrT_${Tone}    Frequency selection
        ${frequencies_list}    Show and Return Available frequencies List
        # Log To Console    ${frequencies_list}
        Return From Keyword    ${frequencies_list}
    ELSE
        Fail    Tone not available within the maximum number.
    END

Open RX Frequencies and Show Them
    [Documentation]    Crucial to Make a "Reset RX Frequency Selection" before! Crucial to Make frequency assignment in ascendent channel order (C1,C2,C3,...). 
    [Arguments]    ${Tone}

    # Obtain row xpath
    ${rows_xpaths}=    Set Variable    (//h6[text()='Local reception frequencies and transmission times']/ancestor-or-self::div[@class='infoExtTable_Content']//div[@class='infoExtRow'])[4]//tr
    Wait Until Element Is Visible    xpath=${rows_xpaths}
    ${row_elements}=    Get WebElements    xpath=${rows_xpaths}
    ${row_count}    Get Length    ${row_elements}
    ${available_tones}=    Evaluate    ${row_count} - 1

    ${available_tone}    Evaluate    ${Tone} <= ${available_tones}
    IF    ${available_tone}
        Button    sFrR_${Tone}    Frequency selection
        ${frequencies_list}    Show and Return Available frequencies List
        # Log To Console    ${frequencies_list}
        Return From Keyword    ${frequencies_list}
    ELSE
        Fail    Tone not available within the maximum number.
    END

Frequency Selection
    [Arguments]    ${frequency}    ${frequencies_list}
    ${Frequency_Is_Available}    Run Keyword And Return Status    List Should Contain Value    ${frequencies_list}    ${frequency}
    IF    ${Frequency_Is_Available}
        Log To Console    Frequency is available. Proceed to Select it.
        ${Frequency_xpath}=    Set Variable    xpath=//span[@class='dvModalFreqListOpt' and text()='${frequency}']
        Click Element    ${Frequency_xpath}
    ELSE
        ${Cancel_Button}=    Set Variable    xpath=//div[@class='dvModalFreqControl']/input[@value="Cancelar"]
        Click Element    ${Cancel_Button}
        Fail    Frequency is not available. Available Frequencies are: ${frequencies_list}
    END

Show and Return Available frequencies List
    ${frequencies_list}    Create List    
    ${frequencies_xpath}=    Set Variable    xpath=//div[@class='dvModalFreqListDivOpt']/span[@class= 'dvModalFreqListOpt']
    Wait Until Element Is Visible    ${frequencies_xpath}    3s
    ${frequency_elements}    Get WebElements    ${frequencies_xpath}
    FOR    ${frequency}    IN    @{frequency_elements}
        ${frequency_text}=    Get Text    ${frequency}
        Append To List    ${frequencies_list}    ${frequency_text}
    END
    Log To Console    Available Frequencies to select:
    Log To Console    ${frequencies_list}
    Return From Keyword     ${frequencies_list}

Copy From Reception Frequencies
    Button    copyRxToTx    Copy
Copy From Transmission Frequencies
    Button    copyTxToRx    Copy



# 3ª Seccion
Input Level
    [Documentation]    Input Level Should between -40 - 0 dBm.
    [Arguments]    ${input_level}
    ${is_in_range}    Validate Number In Range - NEW    ${input_level}    -40    0
    IF    ${is_in_range}
        ${input_level_xpath}=    Set Variable    xpath=//input[@name= 'dclientTproInputGainFloatView']
        Scroll Element Into View Softly    ${input_level_xpath}
        Press Keys    ${input_level_xpath}    ${input_level}
        Press Keys   ${input_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Fail    ${error}
    ELSE
        Fail    input_level is not a valid number. Value should be btw -40 - 0dBm
    END

Output Level
    [Documentation]    Output Level Should between -30 - 0 dBm. Start configuring Power Boosting Level First IS CRUCIAL!
    [Arguments]    ${output_level}
    ${is_in_range}    Validate Number In Range - NEW    ${output_level}    -30    0
    IF    ${is_in_range}
        ${output_level_xpath}=    Set Variable    xpath=//input[@name= 'dclientTproOutputGainFloatView']
        Scroll Element Into View Softly    ${output_level_xpath}
        Press Keys    ${output_level_xpath}    ${output_level}
        Press Keys   ${output_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Fail    ${error}
    ELSE
        Fail    input_level is not a valid number. Value should be btw -30 - 0dBm
    END

Power Boosting
    [Documentation]    Power Boosting Should between 0 - 6 dB. Start configuring Power Boosting Level First IS CRUCIAL!
    [Arguments]    ${Power_Boosting}
    ${is_in_range}    Validate Number In Range - NEW    ${Power_Boosting}    0    6
    IF    ${is_in_range}
        ${powerboosting_level_xpath}=    Set Variable    xpath=//input[@name= 'dtproPowerIncrement']
        Scroll Element Into View Softly    ${powerboosting_level_xpath}
        Press Keys    ${powerboosting_level_xpath}    ${Power_Boosting}
        Press Keys   ${powerboosting_level_xpath}    TAB
        ${error}    Check If an Error Popup Appeared & Skip It
        Run Keyword If    '${error}' != '${None}'   Fail    ${error}
    ELSE
        Fail    input_level is not a valid number. Value should be btw 0 - 6dB
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
