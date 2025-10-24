*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
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
${PASS}    Passwd%4002

${URL_BASE}    https://


# ${terminal_title}    EUT Setup 2
${IP_ADDRESS}    10.212.43.87

# ${terminal_title}    EUT Setup 1
# ${IP_ADDRESS}    10.212.43.87

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
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]
${TP1}    IBTU
${TP2}    IDTU

#Time Zones
${UTC}    0
${LISBON}    1
${MADRID}    2
${PARIS}    3
${OSLO}    4
${WARSAW}    5
${STOCKHOLM}    6
${HELSINKI}    7
${ATHENS}    8
${MOSCOW}    9
${JAKARTA}    10
${PERTH}    11
${ADELAIDE}    12
${SYDNEY}    13
${WELLINGTON}    14
${HONOLULU}    15
${BUENOS_AIRES}    16
${BOGOTA}    17
${ANCHORAGE}    18

#Command Assignments
${tx_matrix_str}    ${EMPTY}
${rx_matrix_str}    ${EMPTY}
${tx_list_str}    ${EMPTY}
${rx_list_str}    ${EMPTY}

*** Test Cases ***

#Assign Inputs
#   [Arguments]    ${input_output}    ${num_input_output}    ${Teleprotection_1/2}    ${Command_Interval_List}
# Assign Commands: Invalid Input Number 
#     Assign Teleprotection Commands    input    0    1    ${teleprotection_commands_list}     #Expect to fail due to an invalid input number

# Assign Commands: Input 1 Telep 1
#     Assign Teleprotection Commands    input    1    1    ${teleprotection_commands_list}

# Assign Commands: Input 1 Telep 2
#     # Assign Teleprotection Commands    input    1    2    ${teleprotection_commands_list}
#     Assign Teleprotection Commands    input    1    2    ${teleprotection_commands_list}

# Assign Commands: Input 2 Telep 1
#     Assign Teleprotection Commands    input    2    1    ${teleprotection_commands_list}

# Assign Commands: Input 2 Telep 2
#     # Assign Teleprotection Commands    input    2    2    ${teleprotection_commands_list}
#     Assign Teleprotection Commands    input    2    2    ${teleprotection_commands_list}

# Assign Commands: Invalid Teleprotection Number 
#     Assign Teleprotection Commands    input    1    3    ${teleprotection_commands_list}



# # Assign Outputs
# #    [Arguments]    ${input_output}    ${num_input_output}    ${Teleprotection_1/2}    ${Command_Interval_List}
# Assign Commands: Invalid Output Number
#     Assign Teleprotection Commands    output    0    1    ${teleprotection_commands_list}     #Expect to fail due to an invalid input number

# Assign Commands: Output 1 Telep 1
#     Assign Teleprotection Commands    output    1    1    ${teleprotection_commands_list}

# Assign Commands: Output 1 Telep 2
#     # Assign Teleprotection Commands    output    1    2    ${teleprotection_commands_list}
#     Assign Teleprotection Commands    output    1    2    ${teleprotection_commands_list}

# Assign Commands: Output 2 Telep 1
#     Assign Teleprotection Commands    output    2    1    ${teleprotection_commands_list}

# Assign Commands: Output 2 Telep 2
#     # Assign Teleprotection Commands    output    2    2    ${teleprotection_commands_list}
#     Assign Teleprotection Commands    output    2    2    ${teleprotection_commands_list}
# Assign Commands: Invalid Output Teleprotection Number 
#     Assign Teleprotection Commands    output    1    3    ${teleprotection_commands_list}
# # Invalid input_output text selection
# Assign Commands: Invalid input_output text selection
#     Assign Teleprotection Commands    outçzsd    0    1    ${teleprotection_commands_list}

# Program Inputs and Outputs
#     Program    sInpAssign






# Program Outputs
#     Program    sOutAssign


#Assign Command INPUT Logic OR (state=1)/AND (state=0)
# Activate Input OR
#     OR_AND Selection    1    input    7    ${teleprotection_commands_list}
#     Program    sInpAssign
# Activate Input AND
#     OR_AND Selection    0    input    7    ${teleprotection_commands_list}
#     Program    sInpAssign
# Activate Output OR
#     OR_AND Selection    1    output    3    ${teleprotection_commands_list}
#     Program    sOutAssign
# Activate Output AND
#     OR_AND Selection    0    output    3    ${teleprotection_commands_list}
#     Program    sOutAssign

#Assign Command OUTPUT Logic OR (state=1)/AND (state=0)

#*************************************************************************************************************************
#*************************************************************************************************************************

#TESTCASES PARA GUI
Log and Save Teleprotection Commands and Inputs/Outputs
    Setup Folder Section
    ${local_teleprotection_commands_list}    Log Teleprotections Commands
    Log To Console    List Format of Teleprotection Commands Assigned: tp1_name, tp2_name, tp1_commands_min_input, tp1_commands_max_input, tp1_commands_min_output, tp1_commands_max_output, tp2_commands_min_input, tp2_commands_max_input, tp2_commands_min_output, tp2_commands_max_output   
    Log To Console    ${local_teleprotection_commands_list}
    Set Suite Variable    ${teleprotection_commands_list}    ${local_teleprotection_commands_list}
    Log Available Inputs
    Log Available Outputs

Program Command Assignments
    Setup Folder Section
    Log To Console    Lógica TX (OR/AND): ${tx_list_str}
    Log To Console    Lógica RX (OR/AND): ${rx_list_str}
    Process Command Assignments    ${tx_matrix_str}    ${rx_matrix_str}
    Process Or_And Assignments    ${tx_list_str}    ${rx_list_str}
    Program Old    sInpAssign
    
# 
#*************************************************************************************************************************

*** Keywords ***
Setup Folder Section
    Click Open Folder    /
    Click Open Folder    EQUIPMENT
    Click Open Folder    Command assignment
    Open Section    Inputs >> Commands >> Outputs
    Sleep    3s

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
    Sleep    1s

Assign input/output to command
    [Arguments]    ${input}    ${command}
    #//div[contains(text(), "${input}")]:primero encuentra el texto input para cualquier <div> y seguidamente 
    #/ancestor-or-self::tr:  Busca el elemento <tr> (fila de tabla) más cercano, subiendo en la jerarquía del DOM.
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Select Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s

Unassign input/ouptut to command
    [Arguments]    ${input}    ${command}
    Scroll Element Into View Softly    xpath=//div[contains(text(), "${input}")]/ancestor::tr//following::input[contains(@type, 'checkbox')][${command}]
    Unselect Checkbox    xpath=//div[contains(text(), "${input}")]/ancestor-or-self::tr//following::input[contains(@type, 'checkbox')][${command}]
    # Sleep    0.1s
 

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
    Wait Until Element Contains    ${TPU_WelcomeTitle_Type}    ${TerminalTitle}    90s

Wait Section Title
    [Arguments]    ${SectionTitle}    
    ${normalized_title}=    Evaluate    "${SectionTitle}".lower()
    Element Should Be Visible    xpath=//h2[translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${normalized_title}"]

#************************************************************************************************************************
#************************************************************************************************************************

#BASIC CONFIGURATION TESTS

RestartModules
    Select Module   0    0
    Sleep    0.2s
    FOR    ${slot}    IN RANGE    0    10
        ${xpath}=    Set Variable    //input[@name='dclientModulesView'][@var_index='${slot}']
        ${module_present}=    Run Keyword And Return Status    Page Should Contain Element    ${xpath}  #gather boolean value if xpath is present in the page 
        IF    ${module_present}  #check if there's an element in the slot
            ${value}=    SeleniumLibrary.Get Element Attribute    ${xpath}    value
            #If there's a module assigned
            # Run Keyword If    '${value}' != ''    Log    Slot ${slot}: Present Module with value "${value}"
            Run Keyword If    '${value}' != ''    Remove Module From Slot    ${slot}
            #If there's no module assigned
            # Run Keyword If    '${value}' == ''    Log    Slot ${slot}: Empty Module
        ELSE
            Log    Slot ${slot} not present
        END
    END

Assign Module To Slot
    [Arguments]    ${slot}   ${module}    ${id_module}
    Select Slot    ${slot}

    Select Module    ${module}    ${id_module}

    Click Element    xpath=//span[contains(@class,'p-button-label') and normalize-space(text())='Select']

    Sleep    0.3s


Remove Module From Slot
    [Arguments]    ${slot} 
    Select Slot    ${slot}
    Click Element    xpath=//span[contains(@class,'p-button-label') and normalize-space(text())='Select']
    Sleep    0.3s
    Run Keyword And Return Status    Handle Alert    ACCEPT
    Sleep    0.2s


Select Slot
    [Arguments]    ${slot} 
    ${xpath_slot}=    Set Variable    //select[@var_name='dclientSlotSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_slot}    timeout=5s    
    Select From List By Value    ${xpath_slot}    ${slot}

Select Module
    [Arguments]    ${module}   ${id_module}
    # Module order&assigment: 
    # 0: None, 112: IBTU, 32: IDTU, 64: IETU, 80: IOTU, 128: ICTU, 16: IPTU, 272: IPTU.10, 96: IRTU, 144: DSTU, 160: MCTU, 176: IOCT, 192: IPIT, 224: IEPT, 256: IOCS, 288: ICPT
    ${xpath_module}=    Set Variable    //select[@var_name='dclientModuleTypeSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_module}    timeout=5s    
    Select From List By Value    ${xpath_module}    ${module}

    Run Keyword If    '${id_module}' != '0'    Select Value Module    ${id_module}    

Select Value Module
    [Arguments]    ${id}
    ${xpath_number_module}=    Set Variable    //select[@var_name='dclientModuleNumberSelect'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_number_module}    timeout=5s    
    Select From List By Value    ${xpath_number_module}    ${id}
    #We need to select Module number depending on the module type selected: 
    # THIS WILL BE ESTABLISHED IN THE TEST PROGRAM INTERFACE. WE'LL ONLY GATHER THE VALUE OF THE MODULE TYPE SELECTED PASSED AS AN ARGUMENT
        #IBTU, IDTU, IETU, IOTU, IOCT, IPIT, IOCS, ICPT: 2 posible Teleprotection
        #IPTU.10: 1 posible Module number
        #DSTU: 2 posible Module number
        #MCTU: 3 posible Module number
        #IRTU: 4 posible Module number
        #ICTU, IPTU, IEPT: 8 posible Module number    

# ******************************************************************************************************************************


# IBTU, IDTU, IETU, IOTU, IOCT, IPIT, IOCS, ICPT: Number of commands: 2 gaps to fill -> Number of commands in transmission & Number of commands in reception
# ICTU, IPTU, IRTU, DSTU, MCTU, IEPT: Blank operation mode (not necessary to select it)
# IPTU.10: Activate or desactivate option "Teleprotection disabled at start-up"


Configure Teleprotection Module
    [Arguments]    ${identifier}    ${message}    ${value}     
    # identifier could be '1' or '2'. It's the identifier of each of the 2 available teleprotection modules. It comes from the interface as an argument.
    # 1º Assign ONE Module -> 2º Configure the module. 
    # message = '0': rx; message = '1': tx 
    # value will be the number of commands to be assigned to the module. It will be passed as an argument from the interface.
    
    #Convert message (tx or rx) to the corresponding value (tx = 1, rx = 0)

    Validate Number In Range    ${identifier}    1    2
    Validate Number In Range    ${message}    0    1
    Validate Number In Range    ${value}    0    8
 
    IF    ${message} == 0
        ${command_name}    Set Variable    dtproCfgNumReceiveCommands
    ELSE IF    ${message} == 1
        ${command_name}    Set Variable    dtproCfgNumTransmitCommands        
    END

    IF    ${identifier} == 1
        ${var_index}    Set Variable    0
    ELSE IF    ${identifier} == 2
        ${var_index}    Set Variable    1
    END

    ${command_name}    Convert To String    ${command_name}
    ${var_index}    Convert To String    ${var_index}

    ${Command}=    Get Command    ${command_name}    ${var_index}
 
    Sleep    0.2s

    # Write the new value
    Press Keys    ${Command}    ${value}
    Sleep         0.3s

Get Command
    [Arguments]    ${name}    ${var_index}
    ${command}    Set Variable    //input[@name='${name}' and @var_index='${var_index}']
    Return From Keyword    ${command}

Configure IPTU.10 Module
    [Arguments]    ${StartupIPTU}
    Checkbox Selection    dtproCfgEnedisDisabledAtStartUp    1


Checkbox Selection
    [Arguments]    ${checkbox}    ${value}
    #Checkbox = 0: Teleprotection disabled at start-up; Checkbox = 1: Teleprotection enabled at start-up
    ${checkbox}    Set Variable    //input[@name='dtproCfgEnedisDisabledAtStartUp']
    Wait Until Element Is Visible    ${checkbox}    timeout=5s    
    Run Keyword If    '${value}' == '1'    Select Checkbox    ${checkbox}
    Run Keyword If    '${value}' == '0'    Unselect Checkbox    ${checkbox}
    Sleep    0.1s


Retrieve Module Arrengement
    Click Element    xpath=//button[@name='gTproConf']//span[normalize-space(text())='Retrieve']
    Wait Until Progress Bar Reaches 100 V2

List detected Modules
    [Documentation]    This keyword uses RestartModules, operating on a list indexed by slot number (0 - 9)
    RestartModules
    Sleep    0.5s
    Log To Console    \nDetected Modules:
    ${Second Row}=    Catenate    SEPARATOR=|    Module Name    Slot
    Log To Console   ${Second Row}
    #We need a list of the detected modules. We will asign eache position (#slot) to the corresponding module name.
    ${detected_modules_list}=    Create List
    #We need to initialize the list with the number of slots (10) to none values, to be able to assign the detected modules to the corresponding slot.
    FOR    ${slot}    IN RANGE    0    10
        Append To List    ${detected_modules_list}    None
    END

    FOR    ${column}    IN RANGE    2    12
        IF    ${column}<=6
            ${input_detected_path}=   Set Variable    xpath=//div[contains(@class, 'infoDatInpLab_content') and normalize-space(.)='Detection failure']/ancestor::tr/td[${column}]//input
            ${status_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${input_detected_path}
            IF    ${status_visible} == ${True}    #Check if is there a XPath of a detected module.
                ${elements}=    Get WebElement    ${input_detected_path}
                ${input_text}=    SeleniumLibrary.Get Element Attribute    ${elements}    value
                ${num_slot}=    Evaluate    13-2*${column}
                ${mod_name&num_slot}=    Catenate    SEPARATOR=\t|\t    ${input_text}    ${num_slot}
                Log To Console    ${mod_name&num_slot}
                Set List Value    ${detected_modules_list}    ${num_slot}    ${input_text}    #Insert the detected module into the list of detected modules.
            ELSE
                Log    No detected module in column ${column}
            END
        END

        IF    ${column}>=8
            ${input_detected_path}=   Set Variable    xpath=//div[contains(@class, 'infoDatInpLab_content') and normalize-space(.)='Detection failure']/ancestor::tr/td[${column}]//input
            ${status_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${input_detected_path}
            IF    ${status_visible} == ${True}    #Check if is there a XPath of a detected module.
                ${elements}=    Get WebElement    ${input_detected_path}
                ${input_text}=    SeleniumLibrary.Get Element Attribute    ${elements}    value
                ${num_slot}=    Evaluate    13-2*${column}
                ${mod_name&num_slot}=    Catenate    SEPARATOR=\t|\t    ${input_text}    ${num_slot}
                Log To Console    ${mod_name&num_slot}
                Set List Value    ${detected_modules_list}    ${num_slot}    ${input_text}    #Insert the detected module into the list of detected modules.

            ELSE
                Log    No detected module in column ${column}
            END
        END
    END
    # We return the list of detected modules, assigning 'None' to the positions where the Slots are empty. 
    Return From Keyword    ${detected_modules_list}

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

Assign Detected Modules V2
    [Arguments]    ${detected_modules_list}
    #IBTU, IDTU, IETU, IOTU, IOCT, IPIT, IOCS, ICPT: 2 posible Teleprotection
    #DSTU: 2 posible Module number
    ${teleprotection_modules_count}=    Set Variable    1
    ${teleprotection_modules_max}=    Set Variable    2
    #MCTU: 3 posible Module number
    ${MCTU_count}=    Set Variable    1
    ${MCTU_MAX}=    Set Variable    3
    #IRTU: 4 posible Module number
    ${IRTU_count}=    Set Variable    1
    ${IRTU_MAX}=    Set Variable    4
    #ICTU, IPTU, IEPT: 8 posible Module number 
    ${ICTU_IPTU_IEPT_count}=    Set Variable    1
    ${ICTU_IPTU_IEPT_MAX}=    Set Variable    8
    #IPTU.10: 1 posible Module number
    ${IPTU.10_count}=    Set Variable    1
    ${IPTU.10_MAX}=    Set Variable    1

    #We need to assign the detected modules to the corresponding slot. 
    #We will use the list of detected modules to do it.
    #We will use the Assign Module To Slot keyword to do it.
    Sleep    0.5s
    FOR    ${slot}    IN RANGE    0    10
        ${module_name}=    Get From List    ${detected_modules_list}    ${slot}
        
        IF    '${module_name}' != 'None'
            ${Module_int_name}=    Convert Module Text to Number    ${module_name}

            ${telep-match}    Evaluate    any('${Module_int_name}' == word for word in @{Teleprotection_list})
            ${ICTU_IPTU_IEPT-match}    Evaluate    any('${Module_int_name}' == word for word in @{ICTU_IPTU_IEPT_list})

            #We will assign the module to the slot. The module name will be the one we have in the list of detected modules.
            #we check if the module is in the list of teleprotection modules. 
            # If it is, we will assign it to the slot. 
            # Morover, we will check if the number of teleprotection modules is less than the maximum number of teleprotection modules. 
            # We will add 1 to the number of teleprotection modules assigned to each type.
            IF    ${telep-match} and (${teleprotection_modules_count} <= ${teleprotection_modules_max})
                Assign Module To Slot    ${slot}    ${Module_int_name}    ${teleprotection_modules_count}
                AutoConfigure Teleprotection    ${Module_int_name}    ${teleprotection_modules_count}
                ${teleprotection_modules_count}=    Evaluate    ${teleprotection_modules_count}+1
            
            ELSE IF    '${Module_int_name}' == ${MCTU} and (${MCTU_count} <= ${MCTU_MAX})
                Assign Module To Slot    ${slot}    ${Module_int_name}    ${MCTU_count}
                ${MCTU_count}=    Evaluate    ${MCTU_count}+1   

            ELSE IF    '${Module_int_name}' == ${IRTU} and (${IRTU_count} <= ${IRTU_MAX}) 
                Assign Module To Slot    ${slot}    ${Module_int_name}    ${IRTU_count}
                ${IRTU_count}=    Evaluate    ${IRTU_count}+1   
            
            ELSE IF    ${ICTU_IPTU_IEPT-match} and (${ICTU_IPTU_IEPT_count} <= ${ICTU_IPTU_IEPT_MAX})
                Assign Module To Slot    ${slot}    ${Module_int_name}    ${ICTU_IPTU_IEPT_count}
                ${ICTU_IPTU_IEPT_count}=    Evaluate    ${ICTU_IPTU_IEPT_count}+1

            ELSE IF    '${Module_int_name}' == ${IPTU.10} and (${IPTU.10_count} <= ${IPTU.10_MAX})
                Assign Module To Slot    ${slot}    ${Module_int_name}    ${IPTU.10_count}
                ${IPTU.10_count}=    Evaluate    ${IPTU.10_count}+1  
            ELSE
                Log    No module assigned to slot ${slot} with module name ${module_name}. Max number of modules reached.
                Log To Console     No module assigned to slot ${slot} with module name ${module_name}. Max number of modules reached.
                Return From Keyword    None
                BREAK
            END
            Sleep    0.5s
        ELSE
            Log    Slot ${slot} vacio
        END    

    END


AutoConfigure Teleprotection
    [Arguments]    ${Module_int_name}    ${identifier}
    # Check If ${Module_int_name} is a Teleprotection Module    
    ${Telep_Check}    Check If Teleprotection Module    ${Module_int_name}
    
    IF    ${Telep_Check}
        IF    ${Module_int_name} == ${IBTU}    #Analogic Teleprotection
            Configure Teleprotection Module    ${identifier}    0    4
            Configure Teleprotection Module    ${identifier}    1    4
        ELSE    #Digital Teleprotections
            Configure Teleprotection Module    ${identifier}    0    8
            Configure Teleprotection Module    ${identifier}    1    8
        END
    ELSE
    Log To Console    Cannot configure module: The provided module is not a teleprotection type.
    END
Check If Teleprotection Module
    [Arguments]    ${Module_int_name}
    ${telep-match}    Evaluate    any('${Module_int_name}' == word for word in @{Teleprotection_list})
    IF    ${telep-match}
        Return From Keyword    ${True}
    ELSE
        Return From Keyword    ${False}
    END
#************************************************************************************************************************
#Display Time Zone Configuration

Retrieve Display
    Click Element    xpath=//button[@name='gDisplay']//span[normalize-space(text())='Retrieve']
    Wait Until Progress Bar Reaches 100 V2
    Sleep    0.5s
Configure Display Time Zone
    [Arguments]    ${zone}
    ${xpath_timezone}=    Set Variable    //select[@var_name='dnmCfgSysTimeZone'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_timezone}    timeout=5s    
    Select From List By Value    ${xpath_timezone}    ${zone}


# ******************************************************************************************************************************
# ******************************************************************************************************************************

#COMMAND ASSIGNMENTS KEYWORDS

Log Teleprotections Commands
    [Documentation]    This keyword logs the teleprotection commands assigned to the modules and return a list with the command intervals in the following order: 
    ...    tp1_name  tp2_name  tp1_commands_min_input  tp1_commands_max_input   tp1_commands_min_output  tp1_commands_max_output  tp2_commands_min_input  tp2_commands_max_input
    ...  tp2_commands_min_output  tp2_commands_max_output
    #Log Teleprotections installed and number of command assigned
    Log To Console    --- Teleprotection Command Assignment ---
    ${tp1_base_xpath}=    Set Variable    //td[contains(text(), "Teleprotection (1)")]
    ${tp2_base_xpath}=    Set Variable    //td[contains(text(), "Teleprotection (2)")]

    # ${tp1_base_xpath_elements}    Get WebElements    ${tp1_base_xpath}
    # ${tp2_base_xpath_elements}    Get WebElements    ${tp2_base_xpath}

    #Initialize the variables to avoid undefined variable error
    ${tp1_name}=    Set Variable    'N/A'
    ${tp1_commands_min_input}=      Set Variable    'N/A'
    ${tp1_commands_max_input}=      Set Variable    'N/A'
    ${tp1_commands_min_output}=      Set Variable    'N/A'
    ${tp1_commands_max_output}=      Set Variable    'N/A'

    ${tp2_name}=    Set Variable    'N/A'
    ${tp2_commands_min_input}=      Set Variable    'N/A'
    ${tp2_commands_max_input}=      Set Variable    'N/A'
    ${tp2_commands_min_output}=      Set Variable    'N/A'
    ${tp2_commands_max_output}=      Set Variable    'N/A'

    # Check and process Teleprotection (1) ---
    ${tp1_exists}=    Run Keyword And Return Status    Page Should Contain Element    ${tp1_base_xpath}
    IF    ${tp1_exists}
        ${tp1_name_xpath}=        Set Variable    ${tp1_base_xpath}/following-sibling::td[2]
        ${tp1_name}=              Get Text If Locator Exists    ${tp1_name_xpath}        default_value=${tp1_name}

        FOR    ${i}    IN RANGE    1    3
            ${tp1_min_cmd_xpath}=     Set Variable    ((${tp1_base_xpath})[${i}])/following-sibling::td[5]
            ${tp1_max_cmd_xpath}=     Set Variable    ((${tp1_base_xpath})[${i}])/following-sibling::td[6]

            IF    ${i} == 1    #Input
                ${tp1_commands_max_raw_input}=      Get Text If Locator Exists    ${tp1_max_cmd_xpath}     default_value=${tp1_commands_max_input}
                ${tp1_commands_min_input}=      Get Text If Locator Exists    ${tp1_min_cmd_xpath}     default_value=${tp1_commands_min_input}
                
        # Modify tp1_commands_max_raw to tp1_comDmands_max removing the '-' before the number of commands assigned.
                IF    ${tp1_commands_max_raw_input} != 'N/A'
                    ${tp1_commands_max_input}=    Evaluate    '${tp1_commands_max_raw_input}'.split('-')[-1].strip()    modules=string
                ELSE
                    ${tp1_commands_max_input}=    Set Variable    ${tp1_commands_max_raw_input}    # Mantener "N/A"
                END

            ELSE    #Output
                ${tp1_commands_min_output}=      Get Text If Locator Exists    ${tp1_min_cmd_xpath}     default_value=${tp1_commands_min_output}
                ${tp1_commands_max_raw_output}=      Get Text If Locator Exists    ${tp1_max_cmd_xpath}     default_value=${tp1_commands_max_output}
        # Modify tp1_commands_max_raw to tp1_comDmands_max removing the '-' before the number of commands assigned.
                IF    ${tp1_commands_max_raw_output} != 'N/A'
                    ${tp1_commands_max_output}=    Evaluate    '${tp1_commands_max_raw_output}'.split('-')[-1].strip()    modules=string
                ELSE
                    ${tp1_commands_max_output}=    Set Variable    ${tp1_commands_max_raw_output}    # Mantener "N/A"
                END
            END
        END
        Log To Console    Teleprotection (1) name: ${tp1_name} \t|\t Commands assigned: INPUT: ${tp1_commands_min_input} - ${tp1_commands_max_input} \t|\t OUTPUT: ${tp1_commands_min_output} - ${tp1_commands_max_output}
    ELSE
        Log To Console    Teleprotection (1) row not found.
    END

    # Check and process Teleprotection (2) ---
    ${tp2_exists}=    Run Keyword And Return Status    Page Should Contain Element    ${tp2_base_xpath}
    IF    ${tp2_exists}
        ${tp2_name_xpath}=        Set Variable    (${tp2_base_xpath})/following-sibling::td[2]

        ${tp2_name}=    Get Text If Locator Exists    ${tp2_name_xpath}        default_value=${tp2_name}

        FOR    ${i}    IN RANGE    1    3
            ${tp2_min_cmd_xpath}=     Set Variable    (${tp2_base_xpath})[${i}]/following-sibling::td[5]
            ${tp2_max_cmd_xpath}=     Set Variable    (${tp2_base_xpath})[${i}]/following-sibling::td[6]
            
            # Modify tp1_commands_max_raw to tp1_commands_max removing the '-' before the number of commands assigned.

            IF    ${i} == 1    #Input
                ${tp2_commands_min_input}=      Get Text If Locator Exists    ${tp2_min_cmd_xpath}     default_value=${tp2_commands_min_input}
                ${tp2_commands_max_raw_input}=      Get Text If Locator Exists    ${tp2_max_cmd_xpath}     default_value=${tp2_commands_max_input}
                IF    ${tp2_commands_max_raw_input} != 'N/A'
                    ${tp2_commands_max_input}=    Evaluate    '${tp2_commands_max_raw_input}'.split('-')[-1].strip()    modules=string
                ELSE
                    ${tp2_commands_max_input}=    Set Variable    ${tp2_commands_max_raw_input}    # Mantener "N/A"
                END
            ELSE    #output
                ${tp2_commands_min_output}=      Get Text If Locator Exists    ${tp2_min_cmd_xpath}     default_value=${tp2_commands_min_output}

                ${tp2_commands_max_raw_output}=      Get Text If Locator Exists    ${tp2_max_cmd_xpath}     default_value=${tp2_commands_max_output}
                IF    ${tp2_commands_max_raw_output} != 'N/A'
                    ${tp2_commands_max_output}=    Evaluate    '${tp2_commands_max_raw_output}'.split('-')[-1].strip()    modules=string
                ELSE
                    ${tp2_commands_max_output}=    Set Variable    ${tp2_commands_max_raw_output}    # Mantener "N/A"
                END
            END
        END
        Log To Console    Teleprotection (2) name: ${tp2_name} \t|\t Commands assigned: INPUT: ${tp2_commands_min_input} - ${tp2_commands_max_input} \t|\t OUTPUT: ${tp2_commands_min_output} - ${tp2_commands_max_output}
    ELSE
        Log To Console    Teleprotection (2) rows not found.
    END
    ${Command_Interval_List}=    Create List    ${tp1_name}    ${tp2_name}    ${tp1_commands_min_input}    ${tp1_commands_max_input}    ${tp1_commands_min_output}    ${tp1_commands_max_output}    ${tp2_commands_min_input}    ${tp2_commands_max_input}    ${tp2_commands_min_output}    ${tp2_commands_max_output}   
    Return From Keyword    ${Command_Interval_List}

Log Available Inputs
    ${input_rows_xpath}=    Set Variable    xpath=(//div[@class= 'infoDatInpLab_content' and normalize-space(.)='COMMANDS:'])[1]/ancestor::tbody/tr
    ${input_rows}=    Get WebElements    ${input_rows_xpath}
    ${input_count}=    Get Length    ${input_rows}
    ${input_count}=    Evaluate   ${input_count} - 1    # Subtract 1 to exclude the header row
    Log To Console    --- Available Inputs ---
    Log To Console    Number of inputs: ${input_count}
    
Log Available Outputs
    ${output_rows_xpath}=    Set Variable    xpath=//td[@class= 'tIntCell' and normalize-space(.)='COMMANDS:']/ancestor::tbody/tr
    ${output_rows}=    Get WebElements    ${output_rows_xpath}
    ${output_count}=    Get Length    ${output_rows}
    ${output_count}=    Evaluate   ${output_count} - 2    # Subtract 2 to exclude the header row
    
    Log To Console    --- Available Outputs ---
    Log To Console    Number of outputs: ${output_count}

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

Restart Teleprotection Assignments
    [Arguments]    ${input_output}    ${num_input_output}    ${Teleprotection_1/2}    ${Command_Interval_List}
    ${tp1_name}=    Set Variable    ${Command_Interval_List}[0]
    ${tp2_name}=    Set Variable    ${Command_Interval_List}[1]

    ${tp1_commands_min_input}=    Set Variable    ${Command_Interval_List}[2]
    ${tp1_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[3]

    ${tp1_commands_min_output}=    Set Variable    ${Command_Interval_List}[4]
    ${tp1_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[5]

    ${tp2_commands_min_input}=    Set Variable    ${Command_Interval_List}[6]
    ${tp2_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[7]

    ${tp2_commands_min_output}=    Set Variable    ${Command_Interval_List}[8]
    ${tp2_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[9]
    
    IF    "${input_output}" == "input"
        ${num_input_ok}    Validate Input Output In Range    "${input_output}"    ${num_input_output}
        Run Keyword If    not ${num_input_ok}    Fail    Not a valid num_input
        IF    ${Teleprotection_1/2} == 1
            IF    ${tp1_commands_max_original_input} != "N/A"
                ${tp1_commands_max_input}=    Evaluate    int(${tp1_commands_max_original_input}) + 1
                FOR    ${command}    IN RANGE    ${tp1_commands_min_input}    ${tp1_commands_max_input}
                    Unassign input to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Unassign input to command V2    ${num_input_output}    ${tp1_commands_min_input}
            END
        ELSE IF    ${Teleprotection_1/2} == 2 and '${tp2_name}' != 'N/A'
            IF    ${tp2_commands_max_original_input} != "N/A"
                ${tp2_commands_max_input}=    Evaluate    int(${tp2_commands_max_original_input}) + 1
                FOR    ${command}    IN RANGE    ${tp2_commands_min_input}    ${tp2_commands_max_input}
                    Unassign input to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Unassign input to command V2    ${num_input_output}    ${tp2_commands_min_input}
            END
        ELSE
            Fail    Teleprotection not recognized. Please select an available teleprotection number.
        END

    ELSE IF    "${input_output}" == "output"
        ${num_output_ok}    Validate Input Output In Range    "${input_output}"    ${num_input_output}
        Run Keyword If    not ${num_output_ok}    Fail    Not a valid num_output
        IF    ${Teleprotection_1/2} == 1
            IF    ${tp1_commands_max_original_output} != "N/A"
                ${tp1_commands_max_output}=    Evaluate    int(${tp1_commands_max_original_output}) + 1
                FOR    ${command}    IN RANGE    ${tp1_commands_min_output}    ${tp1_commands_max_output}
                    Unassign output to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Unassign output to command V2    ${num_input_output}    ${tp1_commands_min_output}
            END
        ELSE IF    ${Teleprotection_1/2} == 2 and '${tp2_name}' != 'N/A'
            IF    ${tp2_commands_max_original_output} != "N/A"
                ${tp2_commands_max_output}=    Evaluate    int(${tp2_commands_max_original_output}) + 1
                FOR    ${command}    IN RANGE    ${tp2_commands_min_output}    ${tp2_commands_max_output}
                    Unassign output to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Unassign output to command V2    ${num_input_output}    ${tp2_commands_min_output}
            END
        ELSE
            Fail    Teleprotection not recognized. Please select an available teleprotection number.
        END

    ELSE
        Fail    input_output not recognized. Please select input or output.
    END


Assign Teleprotection Commands
    [Arguments]    ${input_output}    ${num_input_output}    ${Teleprotection_1/2}    ${Command_Interval_List}
    ${tp1_name}=    Set Variable    ${Command_Interval_List}[0]
    ${tp2_name}=    Set Variable    ${Command_Interval_List}[1]

    ${tp1_commands_min_input}=    Set Variable    ${Command_Interval_List}[2]
    ${tp1_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[3]

    ${tp1_commands_min_output}=    Set Variable    ${Command_Interval_List}[4]
    ${tp1_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[5]

    ${tp2_commands_min_input}=    Set Variable    ${Command_Interval_List}[6]
    ${tp2_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[7]

    ${tp2_commands_min_output}=    Set Variable    ${Command_Interval_List}[8]
    ${tp2_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[9]
    
    IF    "${input_output}" == "input"
        ${num_input_ok}    Validate Input Output In Range    "${input_output}"    ${num_input_output}
        Run Keyword If    not ${num_input_ok}    Fail    Not a valid num_input
        IF    ${Teleprotection_1/2} == 1
            IF    ${tp1_commands_max_original_input} != "N/A"
                ${tp1_commands_max_input}=    Evaluate    int(${tp1_commands_max_original_input}) + 1
                FOR    ${command}    IN RANGE    ${tp1_commands_min_input}    ${tp1_commands_max_input}
                    Assign input to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Assign input to command V2    ${num_input_output}    ${tp1_commands_min_input}
            END
        ELSE IF    ${Teleprotection_1/2} == 2 and '${tp2_name}' != 'N/A'
            IF    ${tp2_commands_max_original_input} != "N/A"
                ${tp2_commands_max_input}=    Evaluate    int(${tp2_commands_max_original_input}) + 1
                FOR    ${command}    IN RANGE    ${tp2_commands_min_input}    ${tp2_commands_max_input}
                    Assign input to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Assign input to command V2    ${num_input_output}    ${tp2_commands_min_input}
            END
        ELSE
            Fail    Teleprotection not recognized. Please select an available teleprotection number.
        END

    ELSE IF    "${input_output}" == "output"
        ${num_output_ok}    Validate Input Output In Range    "${input_output}"    ${num_input_output}
        Run Keyword If    not ${num_output_ok}    Fail    Not a valid num_output
        IF    ${Teleprotection_1/2} == 1
            IF    ${tp1_commands_max_original_output} != "N/A"
                ${tp1_commands_max_output}=    Evaluate    int(${tp1_commands_max_original_output}) + 1
                FOR    ${command}    IN RANGE    ${tp1_commands_min_output}    ${tp1_commands_max_output}
                    Assign output to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Assign output to command V2    ${num_input_output}    ${tp1_commands_min_output}
            END
        ELSE IF    ${Teleprotection_1/2} == 2 and '${tp2_name}' != 'N/A'
            IF    ${tp2_commands_max_original_output} != "N/A"
                ${tp2_commands_max_output}=    Evaluate    int(${tp2_commands_max_original_output}) + 1
                FOR    ${command}    IN RANGE    ${tp2_commands_min_output}    ${tp2_commands_max_output}
                    Assign output to command V2    ${num_input_output}    ${command}
                END
            ELSE
                Assign output to command V2    ${num_input_output}    ${tp2_commands_min_output}
            END
        ELSE
            Fail    Teleprotection not recognized. Please select an available teleprotection number.
        END

    ELSE
        Fail    input_output not recognized. Please select input or output.
    END

Process Command Assignments
    [Arguments]    ${tx_matrix_str}    ${rx_matrix_str}

    # Convertir las matrices de texto a listas de Robot Framework
    ${tx_matrix}=    Evaluate    ${tx_matrix_str}
    ${rx_matrix}=    Evaluate    ${rx_matrix_str}

    # Recorrer y programar la matriz de Entradas (TX).
    FOR    ${row_index}    IN ENUMERATE    @{tx_matrix}
        ${input_num}=    Evaluate    ${row_index[0]} + 1
        FOR    ${col_index}    IN ENUMERATE    @{row_index[1]}   #@{row_index[1]}: "entre los *¡valores!* que hay en la fila seleccionada por el primer FOR"
            ${command_num}=    Evaluate    ${col_index[0]} + 1
            IF    ${col_index[1]} == 1
                Assign input to command V2    ${input_num}    ${command_num}
            ELSE
                Unassign input to command V2    ${input_num}    ${command_num}
            END
        END
    END

    # Recorrer y programar la matriz de Salidas (RX)
    FOR    ${row_index}    IN ENUMERATE    @{rx_matrix}
        ${output_num}=    Evaluate    ${row_index[0]} + 1
        FOR    ${col_index}    IN ENUMERATE    @{row_index[1]}
            ${command_num}=    Evaluate    ${col_index[0]} + 1
            IF    ${col_index[1]} == 1
                Assign output to command V2    ${output_num}    ${command_num}
            ELSE
                Unassign output to command V2    ${output_num}    ${command_num}
            END
        END
    END
    

Process Or_And Assignments
    [Arguments]    ${tx_list_str}    ${rx_list_str}
    # Convertir las matrices de texto a listas de Robot Framework
    ${tx_list}=    Evaluate    ${tx_list_str}
    ${rx_list}=    Evaluate    ${rx_list_str}

    # Recorrer y programar la lista de Entradas (TX).
    FOR    ${col_index}    IN ENUMERATE    @{tx_list}   #@{row_index[1]}: "entre los *¡valores!* que hay en la fila seleccionada por el primer FOR"
        ${command_num}=    Evaluate    ${col_index[0]} + 1
        IF    ${col_index[1]} == 1
            Input OR_AND Selection    1    ${command_num}
        ELSE
            Input OR_AND Selection    0    ${command_num}
        END
    END

    # Recorrer y programar la matriz de Salidas (RX)
    FOR    ${row_index}    IN ENUMERATE    @{rx_list}
        ${output_num}=    Evaluate    ${row_index[0]} + 1
        IF    ${row_index[1]} == 1
            Output OR_AND Selection    1    ${output_num}
        ELSE
            Output OR_AND Selection    0    ${output_num}
        END
    END

# Input OR_AND Selection_OLD
#     [Arguments]    ${state}    ${input_output}    ${command/output}    ${Command_Interval_List}
#     [Documentation]    This keyword activates the OR or AND checkbox for the selected command. State 1 = OR, State 0 = AND.
    
#     ${Max Command_Output Available}=    Max Command/Output Available    ${input_output}    ${Command_Interval_List}
#     ${max_commands}=    Set Variable    ${Max Command_Output Available}[0]
    
#     #Max Command Number avaliable
#     IF    ${command/output} > ${max_commands}
#         Fail    Command number ${command/output} is out of range. Max input command number available is ${max_commands}.    WARN
#     END
#     ${xpath}=    Set Variable    //div[contains(text(), "OR = On; AND = Off")]/ancestor::tr/descendant::input[contains(@type, 'checkbox')][${command/output}]    #locate the input OR/AND command checkbox
#     Scroll Element Into View Softly    ${xpath}

#     IF    ${state} == 1    #OR
#         Select Checkbox    ${xpath}
#     ELSE IF    ${state} == 0    #AND
#         Unselect Checkbox    ${xpath}
#     END
# Output OR_AND Selection_OLD
#     [Arguments]    ${state}    ${input_output}    ${command/output}    ${Command_Interval_List}
#     [Documentation]    This keyword activates the OR or AND checkbox for the selected command. State 1 = OR, State 0 = AND.
    
#     ${Max Command_Output Available}=    Max Command/Output Available    ${input_output}    ${Command_Interval_List}
#     ${max_commands}=    Set Variable    ${Max Command_Output Available}[0]
    
#     ${max_outputs}=    Set Variable    ${Max Command_Output Available}[1]
#     IF    ${command/output} > ${max_outputs}
#         Fail    Output number ${command/output} is out of range. Max output number available is ${max_outputs}.    WARN
#     END
#     ${output_OR_AND_CheckboxNumber}=    Evaluate    ${max_commands} + 1
#     ${xpath}=    Set Variable    //div[contains(text(), "Out ${command/output}-")]/ancestor-or-self::tr/descendant::input[contains(@type, 'checkbox')][${output_OR_AND_CheckboxNumber}]
#     Scroll Element Into View Softly    ${xpath}

#     IF    ${state} == 1    #OR
#         Select Checkbox    ${xpath}
#     ELSE IF    ${state} == 0    #AND
#         Unselect Checkbox    ${xpath}
#     END

Input OR_AND Selection
    [Arguments]    ${state}    ${command}
    [Documentation]    This keyword activates the OR or AND checkbox for the selected command. State 1 = OR, State 0 = AND.
    #Max Command Number avaliable
    # ${xpath}=    Set Variable    //div[contains(text(), "OR = On; AND = Off")]/ancestor::tr/descendant::input[contains(@type, 'checkbox')][${command/output}]    #locate the input OR/AND command checkbox
    ${xpath}=    Set Variable    xpath=(//input[@name='dtproCfgInputToCommandLogic'])[${command}]
    Scroll Element Into View Softly    ${xpath}

    IF    ${state} == 1    #OR
        Select Checkbox    ${xpath}
    ELSE IF    ${state} == 0    #AND
        Unselect Checkbox    ${xpath}
    END

Output OR_AND Selection
    [Arguments]    ${state}    ${output}
    [Documentation]    This keyword activates the OR or AND checkbox for the selected command. State 1 = OR, State 0 = AND.
    ${xpath}=    Set Variable    xpath=(//input[@name='dtproCfgCommandToOutputLogic'])[${output}]
    Scroll Element Into View Softly    ${xpath}

    IF    ${state} == 1    #OR
        Select Checkbox    ${xpath}
    ELSE IF    ${state} == 0    #AND
        Unselect Checkbox    ${xpath}
    END

Assign input to command V2
    [Arguments]    ${input}    ${command}
    ${row_index}=    Evaluate    ${input} + 1    # Add 1 to match the XPath index (input rows starts at 2)
    ${command_index}=    Evaluate    ${command} + 2    # Add 1 to match the XPath index (command columns starts at 3)
    ${input_rows_xpath}=    Set Variable    xpath=(((//div[@class= 'infoDatInpLab_content' and normalize-space(.)='COMMANDS:'])[1]/ancestor::tbody//tr)[${row_index}]//td)[${command_index}]//input
    Scroll Element Into View Softly    ${input_rows_xpath}
    Select Checkbox    ${input_rows_xpath}

Unassign input to command V2
    [Arguments]    ${input}    ${command}
    ${row_index}=    Evaluate    ${input} + 1    # Add 1 to match the XPath index (input rows starts at 2)
    ${command_index}=    Evaluate    ${command} + 2    # Add 1 to match the XPath index (command columns starts at 3)
    ${input_rows_xpath}=    Set Variable    xpath=(((//div[@class= 'infoDatInpLab_content' and normalize-space(.)='COMMANDS:'])[1]/ancestor::tbody//tr)[${row_index}]//td)[${command_index}]//input
    Scroll Element Into View Softly    ${input_rows_xpath}
    Unselect Checkbox    ${input_rows_xpath}


Assign output to command V2
    [Arguments]    ${output}    ${command}
    ${row_index}=    Evaluate    ${output} + 2    # Add 2 to match the XPath index (output rows starts at 3)
    ${command_index}=    Evaluate    ${command} + 2    # Add 2 to match the XPath index (command columns starts at 3)
    ${output_rows_xpath}=    Set Variable    xpath=((//td[@class= 'tIntCell' and normalize-space(.)='COMMANDS:']/ancestor::tbody//tr)[${row_index}]//td)[${command_index}]//input
    Scroll Element Into View Softly    ${output_rows_xpath}
    Select Checkbox    ${output_rows_xpath}

Unassign output to command V2
    [Arguments]    ${output}    ${command}
    ${row_index}=    Evaluate    ${output} + 2    # Add 2 to match the XPath index (output rows starts at 3)
    ${command_index}=    Evaluate    ${command} + 2    # Add 2 to match the XPath index (command columns starts at 3)
    ${output_rows_xpath}=    Set Variable    xpath=((//td[@class= 'tIntCell' and normalize-space(.)='COMMANDS:']/ancestor::tbody//tr)[${row_index}]//td)[${command_index}]//input
    Scroll Element Into View Softly    ${output_rows_xpath}
    Unselect Checkbox    ${output_rows_xpath}


Max Command/Output Available
    [Arguments]    ${input_output}    ${Command_Interval_List}
    ${max_command_default}=    Set Variable    'N/A'
    ${max_outputs_default}=    Set Variable    'N/A'

    ${max_command}=            Set Variable    ${max_command_default}
    ${max_outputs}=            Set Variable    ${max_outputs_default}

#Check max input command number available
    IF    "${input_output}" == "input"
        ${tp1_commands_min_input}=    Set Variable    ${Command_Interval_List}[2]
        ${tp1_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[3]

        ${tp2_commands_min_input}=    Set Variable    ${Command_Interval_List}[6]
        ${tp2_commands_max_original_input}=    Set Variable    ${Command_Interval_List}[7]

        IF    ${tp2_commands_max_original_input} != 'N/A'
            ${max_command}=    Set Variable    ${tp2_commands_max_original_input}
        ELSE
            IF    ${tp2_commands_min_input} != 'N/A'
            ${max_command}=    Set Variable    ${tp2_commands_min_input}
            ELSE
                IF    ${tp1_commands_max_original_input} != 'N/A'
                    ${max_command}=    Set Variable    ${tp1_commands_max_original_input}
                ELSE
                    ${max_command}=    Set Variable    1
                END
            END
        END

    ELSE IF    "${input_output}" == "output"
    #Check max outputs number available
        ${max_outputs_xpath}=    Set Variable    //tr[.//div[@class='infoUsrTxtPart' and starts-with(normalize-space(.), 'Out ')]]
        ${max_outputs}=    SeleniumLibrary.Get Element Count    ${max_outputs_xpath}

    #Check max output command number available
        ${tp1_commands_min_output}=    Set Variable    ${Command_Interval_List}[4]
        ${tp1_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[5]

        ${tp2_commands_min_output}=    Set Variable    ${Command_Interval_List}[8]
        ${tp2_commands_max_original_output}=    Set Variable    ${Command_Interval_List}[9]

        IF    ${tp2_commands_max_original_output} != 'N/A'
            ${max_command}=    Set Variable    ${tp2_commands_max_original_output}
        ELSE
            IF    ${tp2_commands_min_output} != 'N/A'
                ${max_command}=    Set Variable    ${tp2_commands_min_output}
            ELSE
                IF    ${tp1_commands_max_original_output} != 'N/A'
                    ${max_command}=    Set Variable    ${tp1_commands_max_original_output}
                ELSE
                    ${max_command}=    Set Variable    1
                END
            END
        END
    END    
    Return From Keyword    ${max_command}    ${max_outputs}


Validate Input Output In Range
    [Arguments]    ${input_output}    ${num_input_output}
    # Validate Input In Range    ${num_input}    ${min}    ${max}
    ${min}    Set Variable    1
    ${input_count}    ${output_count}=    Get Displayed Input Output Counts

    IF    ${input_output} == "input"
        ${max}    Set Variable    ${input_count}
    ELSE IF    ${input_output} == "output"
        ${max}    Set Variable    ${output_count}
    ELSE
        Log    input_output not recognized. Please select input or output.
        ${max}    Set Variable    0
    END

    ${is_number_0}    Evaluate    "${num_input_output}".isdigit()
    Run Keyword If    not ${is_number_0}    Fail    No es un mínimo válido
    ${is_in_range}    Evaluate    (${min} <= ${num_input_output} <= ${max}) and (${is_number_0} == True)

    Return From Keyword    ${is_in_range}

Get Displayed Input Output Counts
    [Documentation]    Counts the visible Input and Output configuration rows on the page.
    # Count the Input labels (td starting with 'Inp ')
    ${input_count}=    SeleniumLibrary.Get Element Count    xpath=//td[starts-with(normalize-space(.), 'Inp ')]
    # Count the Output labels (td starting with 'Out ')
    ${output_count}=   SeleniumLibrary.Get Element Count    xpath=//td[starts-with(normalize-space(.), 'Out ')]

    # Log To Console    \nNumber of configurable Inputs displayed: ${input_count}
    # Log To Console    Number of configurable Outputs displayed: ${output_count}\n
    Return From Keyword    ${input_count}    ${output_count}
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


