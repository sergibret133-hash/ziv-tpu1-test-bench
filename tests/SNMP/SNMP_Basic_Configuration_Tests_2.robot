*** Settings ***
Documentation                This is a basic test
Library    SeleniumLibrary
Library    String
Library    Collections
Library    OperatingSystem    #for file operations
Library    BuiltIn
Library    XML
Library    Screenshot    ${OUTPUTDIR}/screenshots
# Suite Setup    Setup Command_Assignments Pretests
# Suite Teardown    Close Browser

*** Variables ***
#VALID LOGIN & ACCES TO WEBPAGE
${USER}    admin
${PASS}    Passwd%4002

${URL_BASE}    https://


${terminal_title}    EUT Setup 1
${IP_ADDRESS}    10.212.43.87

# ${terminal_title}    EUT Setup 2
# ${IP_ADDRESS}    10.212.43.21

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
${options}=  Create List  --ignore-certificate-errors  --disable-web-security  --allow-running-insecure-content
${commands}    Input/Output Alias

#************************************************************************************************************************
#BASIC CONFIGURATION TESTS
${SELECT_BUTTON}    xpath=//button[contains(text(),'Select')]

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


# *** Test Cases ***
# Open_BasicConfiguration+RestartModules
#     Open Broswer to Login page
#     Wait Title    EUT Setup 2
#     Click Open Folder    /
#     Click Open Folder    EQUIPMENT
#     Open Section    Basic Configuration
#     Wait Section Title    BASIC CONFIGURATION
#     RestartModules
#     Retrieve Module Arrengement
#     Sleep    10s

# Open_BasicConfiguration+RestartModules+Assign Module To Slot
    # Open Broswer to Login page
    # Wait Title    EUT Setup 2
    # Click Open Folder    /
    # Click Open Folder    EQUIPMENT
    # Open Section    Basic Configuration
    # Wait Section Title    BASIC CONFIGURATION

    # RestartModules

    # #Asignamos el modulo IBTU (112) al slot 0 y con #2 de teleproteccion.
    # Assign Module To Slot    0    112    2

    # #Asignamos el modulo IRTU (96) al slot 2 y con #4 de modulo.
    # Assign Module To Slot    2    96    4

    # Retrieve Module Arrengement
    # Sleep    10s

# Open_BasicConfiguration+RestartModules+Assign Module To Slot+Configure Module
#     Open Broswer to Login page
#     Wait Title    EUT Setup 2
#     Click Open Folder    /
#     Click Open Folder    EQUIPMENT
#     Open Section    Basic Configuration
#     Wait Section Title    BASIC CONFIGURATION

#     RestartModules

#     #Assign the IBTU module to slot 1 & with #1 teleprotection ID.
#     Assign Module To Slot    1    ${IBTU}    1
#     #Configure the recently added teleprotection module (1) with 4 transmission commands & 4 reception commands
#     Configure Teleprotection Module    1    1    4
#     Configure Teleprotection Module    1    0    4

#     #Assign the IDTU module to slot 0 & with #2 teleprotection ID.
#     Assign Module To Slot    0    ${IDTU}    2
#     #Configure the recently added teleprotection module (2) with 8 transmission commands 
#     Configure Teleprotection Module    2    1    8
#     Configure Teleprotection Module    2    0    8

#     # Retrieve Module Arrengement

#     # #Test to check the Validate Number In Range keyword
#     # Configure Teleprotection Module    1    1    9
#     # Configure Teleprotection Module    2    0    a

#     # Configure Teleprotection disabled at start-up checkbox
#     Assign Module To Slot    3    ${IPTU.10}    1
#     Configure IPTU.10 Module    1

#     # Retrieve Module Arrengement
#     Sleep    10s

# Open_BasicConfiguration+Configure Display Time Zone
#     Open Broswer to Login page
#     Wait Title    EUT Setup 2
#     Click Open Folder    /
#     Click Open Folder    EQUIPMENT
#     Open Section    Basic Configuration
#     Wait Section Title    BASIC CONFIGURATION


#     Configure Display Time Zone    ${MADRID}
#     Sleep    5s
#     Retrieve Display

# Open_BasicConfiguration+RestartModules+List detected Modules
#     Open Broswer to Login page
#     Wait Title    ${terminal_title}
#     Click Open Folder    /
#     Click Open Folder    EQUIPMENT
#     Open Section    Basic Configuration
#     Wait Section Title    BASIC CONFIGURATION

#     ${Detected_Module_List}    List detected Modules
#     Log To Console    ${Detected_Module_List}

# Open_BasicConfiguration+RestartModules+Assign Detected Modules: Lista 1 prioridad valida
#     RestartModules
#     ${Detected_Module_List}    List detected Modules
#     Log To Console    ${Detected_Module_List} 
#     ${prioritized_1}=    Create List    IOCS    ICPT
#     Assign Detected Modules V3    ${Detected_Module_List}    ${prioritized_1}
#     Program    sTproConf

# Open_BasicConfiguration+RestartModules+Assign Detected Modules: Lista 2 prioridad valida
#     RestartModules
#     ${Detected_Module_List}    List detected Modules
#     Log To Console    ${Detected_Module_List} 
#     ${prioritized_2}=    Create List    IOCS    ICPT
#     Assign Detected Modules V3    ${Detected_Module_List}    ${prioritized_2}
#     Program    sTproConf

# Open_BasicConfiguration+RestartModules+Assign Detected Modules: Lista 3 prioridad valida
#     RestartModules
#     ${Detected_Module_List}    List detected Modules
#     Log To Console    ${Detected_Module_List} 
#     ${prioritized_3}=    Create List    IOCS    IDTU
#     Assign Detected Modules V3    ${Detected_Module_List}    ${prioritized_3}
#     Program    sTproConf

# Open_BasicConfiguration+RestartModules+Assign Detected Modules: Lista NO VALIDA
#     RestartModules
#     ${Detected_Module_List}    List detected Modules
#     Log To Console    ${Detected_Module_List} 
#     ${prioritized_2}=    Create List    IOCS    FDKS
#     Assign Detected Modules V3    ${Detected_Module_List}    ${prioritized_2}
#     Program    sTproConf
#*************************************************************************************************************************

*** Keywords ***
Setup Command_Assignments Pretests
    # Test Screenshot Config
    ${ruta_screenshots}    Set Variable    ${CURDIR}/screenshots
    Set Screenshot Directory    ${ruta_screenshots}
    Log    El directorio para las capturas de pantalla es: ${ruta_screenshots}
    Open Broswer to Login page    ${URL_COMPLETA}    ${BROWSER}
    Wait Title    ${terminal_title}
    Click Open Folder    /
    Click Open Folder    EQUIPMENT
    Open Section    Basic Configuration
    Wait Section Title    BASIC CONFIGURATION

    # Set Suite Variable    ${teleprotection_commands_list}    ${local_teleprotection_commands_list}

Open Broswer to Login page
    [Arguments]    ${url}    ${brows}
    Open Browser    ${url}    ${brows}    options=add_argument("--ignore-certificate-errors")
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
    Scroll Element Into View Softly    xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
    ${button}  Get WebElement  xpath=//span[contains(text(), "${folderName}")]/ancestor-or-self::div[contains(@tabindex, '0')]//button[contains(@class, 'p-tree-toggler')]
    Click Element  ${button}
    Sleep    0.1s

Open Section
    [Arguments]    ${section}
    #Scroll Element Into View Softly    xpath=//span[@class='p-treenode-label' and text()="${section}"]
    Scroll Element Into View Softly    xpath=//span[@class='p-treenode-label' and translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]
    #Not necessary to establish a new variable (like "button" variable from scrpt before)-> GET WEBELEMENT IS NOT NECESSARY
    #Click Element  xpath=//span[@class='p-treenode-label' and text()="${section}"]
    Click Element    xpath=//span[@class='p-treenode-label' and translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = "${section.lower()}"]

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

Wait Until Progress Bar Reaches 100
    [Arguments]    ${timeout}=30s    ${poll_interval}=0.5s
    Log    Waiting for the progress bar to reach 100%...
    Wait Until Keyword Succeeds
    ...    ${timeout}
    ...    ${poll_interval}
    ...    Element Attribute Value Should Be    xpath=//div[@role="progressbar"]    aria-valuenow    100
    Sleep    0.3s


Wait Until Progress Bar Reaches 100 V2
    [Arguments]    ${timeout}=50s    ${poll_interval}=0.2s
    Log    Waiting for the progress bar to be dissapeared...
    ${progress_bar_title_xpath}=    Set Variable    xpath=//div[contains(@class, "p-progressbar-label")]
    Wait Until Element Is Not Visible    ${progress_bar_title_xpath}    timeout=50s  # Ajusta el timeout según sea necesario
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
    [RETURN]    ${command}

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
    Wait Until Progress Bar Reaches 100

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

    ${column_slot_map}=    Create Dictionary    2=9    3=7    4=5    5=3    6=1    8=0    9=2    10=4    11=6    12=8

    FOR    ${column}    IN RANGE    2    12
        ${input_detected_path}=   Set Variable    xpath=//div[contains(@class, 'infoDatInpLab_content') and normalize-space(.)='Detection failure']/ancestor::tr/td[${column}]//input
        ${status_visible}=    Run Keyword And Return Status    Element Should Be Visible    ${input_detected_path}
        IF    ${status_visible} == ${True}
            ${elements}=    Get WebElement    ${input_detected_path}
            ${input_text}=    SeleniumLibrary.Get Element Attribute    ${elements}    value
            ${column_str}=    Convert To String    ${column}
            ${num_slot}=    Get From Dictionary    ${column_slot_map}    ${column_str}
            ${mod_name_and_slot}=    Catenate    SEPARATOR=\t|\t    ${input_text}    ${num_slot}
            Log To Console    ${mod_name_and_slot}
            Set List Value    ${detected_modules_list}    ${num_slot}    ${input_text}
        ELSE
            Log    No detected module in column ${column}
        END
    END
    # We return the list of detected modules, assigning 'None' to the positions where the Slots are empty. 
    RETURN    ${detected_modules_list}

Convert Module Text to Number
    [Arguments]    ${module_name}
    #Convert the module name to the corresponding number. We will use the list of modules to do it.
    IF    "${module_name}" == "IBTU"
        RETURN    ${IBTU}
    ELSE IF    "${module_name}" == "IDTU"
        RETURN    ${IDTU}
    ELSE IF    "${module_name}" == "IETU"
        RETURN    ${IETU}
    ELSE IF    "${module_name}" == "IOTU"
        RETURN    ${IOTU}
    ELSE IF    "${module_name}" == "ICTU"
        RETURN    ${ICTU}
    ELSE IF    "${module_name}" == "IPTU"
        RETURN    ${IPTU}
    ELSE IF    "${module_name}" == "IPTU.10"
        RETURN    ${IPTU.10}
    ELSE IF    "${module_name}" == "IRTU"
        RETURN    ${IRTU}
    ELSE IF    "${module_name}" == "DSTU"
        RETURN    ${DSTU}
    ELSE IF    "${module_name}" == "MCTU"
        RETURN    ${MCTU}
    ELSE IF    "${module_name}" == "IOCT"
        RETURN    ${IOCT}
    ELSE IF    "${module_name}" == "IPIT"
        RETURN    ${IPIT}
    ELSE IF    "${module_name}" == "IEPT"
        RETURN    ${IEPT}
    ELSE IF    "${module_name}" == "IOCS"
        RETURN    ${IOCS}
    ELSE IF    "${module_name}" == "ICPT"
        RETURN    ${ICPT}
    ELSE
        RETURN    None
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
                RETURN    None
                BREAK
            END
            Sleep    0.5s
        ELSE
            Log    Slot ${slot} vacio
        END    

    END

Assign Detected Modules V3
    [Arguments]    ${detected_modules_list}    ${prioritized_list}
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
    
    # Convert the prioritized list passed as an argument to a list
    # ${prioritized_list}=    Create List    @{prioritized_list}
    # List of the prioritized modules converted to numbers
    ${prioritized_modules_converted}=    Create List
        #We convert the string module names from the prioritized_list to the corresponding number.
    FOR    ${mod}    IN    @{prioritized_list}
        ${mod_converted}=    Convert Module Text to Number    ${mod}
        Append To List    ${prioritized_modules_converted}    ${mod_converted}
    END
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
            ${prioritized_match}    Evaluate    any('${Module_int_name}' == word for word in @{prioritized_modules_converted})
            #We will assign the module to the slot. The module name will be the one we have in the list of detected modules.
            #we check if the module is in the list of teleprotection modules. 
            # If it is, we will assign it to the slot. 
            # Morover, we will check if the number of teleprotection modules is less than the maximum number of teleprotection modules. 
            # We will add 1 to the number of teleprotection modules assigned to each type.
            IF    ${telep-match} and ${prioritized_match} and (${teleprotection_modules_count} <= ${teleprotection_modules_max})
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
    RETURN    ${True}
    ELSE
    RETURN    ${False}
    END
#************************************************************************************************************************
#Display Time Zone Configuration

Retrieve Display
    Click Element    xpath=//button[@name='gDisplay']//span[normalize-space(text())='Retrieve']
    Wait Until Progress Bar Reaches 100
    Sleep    0.5s
Configure Display Time Zone
    [Arguments]    ${zone}
    ${xpath_timezone}=    Set Variable    //select[@var_name='dnmCfgSysTimeZone'][@var_index='0'] 
    Wait Until Element Is Visible    ${xpath_timezone}    timeout=5s    
    Select From List By Value    ${xpath_timezone}    ${zone}


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
    [RETURN]    ${is_in_range}
    Should Be True    ${is_in_range}


