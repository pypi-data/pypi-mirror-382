<p align="left">
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e4/Robot-framework-logo.png" alt="RB Logo" width="200">
  <img src="https://upload.wikimedia.org/wikipedia/commons/7/77/Qgis-icon-3.0.png?20180304175057" alt="QGIS 3.0 Logo" width="120">
</p>

---


# QGISLibrary

A **QGIS** library for **Robot Framework** providing reusable keywords for QGIS UI Automation and QGIS UI Testing.

---

## Installation

Install via pip:

```bash
pip install QGISLibrary
```


---


## Features

- Automate QGIS UI actions using section *** Tasks *** in robot file
- Test QGIS UI behaviours using section *** Test Cases *** in robot file
- Generate clear HTML report of task/test execution
- Capture screenshots and logs for test validation  
- Integrates with Robot Framework for robust automated tests  
- Supports Windows (via PyWinAuto) and cross-platform (via PyAutoGUI)  


---


## Example of Robot Framework file
```robot
# File: qgis_sample.robot
*** Settings ***
Documentation    This is an example QGIS Robot Framework file
Library    QGISLibrary
Library    Screenshot
Suite Setup       Set Metadata From Variables
Suite Teardown    Log    End of Suite
Metadata    Author    Michal Pilarski
Metadata    Version   1.0.0
Metadata    Environment   TEST
Metadata    QGIS Version   3.40.7-Bratislava


*** Variables ***
${QGIS_FILEPATH}    C:\\Program Files\\QGIS 3.40.7\\bin\\qgis-ltr-bin.exe
${QGIS_PROFILE}    default


*** Tasks ***
QGIS Init Task
    [Documentation]    Sample of QGIS Init Task
    [Tags]    dev    qgis
    [Setup]    Log    Start Task
    [Teardown]    Log    End Task
    Start Qgis    ${QGIS_FILEPATH}    ${QGIS_PROFILE}
#    Connect Qgis    ${QGIS_FILEPATH}
    ${MAIN_WINDOW}    Main Window
    ${OPEN_PROJECT_BUTTON}    Get Locator By Parent    ${MAIN_WINDOW}    title=Otwórz…    control_type=Button
    Mouse Click Locator   ${OPEN_PROJECT_BUTTON}    1
    Take Screenshot    qgis_screenshot.jpg
#    Kill Qgis


*** Keywords ***
Set Metadata From Variables
    [Documentation]    Set Suite Metadata
    Set Suite Metadata    QGIS FILEPATH    ${QGIS_FILEPATH}
    Set Suite Metadata    QGIS PROFILE    ${QGIS_PROFILE}
```


---


## Usage
- Run command via terminal
```bash
robot qgis_sample.robot
```
- For help run via terminal
```bash
robot --help
```
- Open HTML Reports: **report.html** or **log.html**


---


## QGIS UI Locators
- Use **Inspect.exe** or **UISpy.exe** (located on: [QGISLibrary on GitLab](https://gitlab.com/michpil/qgis_library/-/tree/main)) to detect UI locators


---


## Robot Framework Editor
- Use **RIDE** to edit `.robot` files:
- Run command via terminal
```bash
pip install robotframework-ride
ride
```


---


## Links
[Robot Framework Documentation](https://robotframework.org/robotframework/#user-guide)

[QGISLibrary Documentation](https://gitlab.com/michpil/qgis_library/-/blob/main/QGISLibrary.html)