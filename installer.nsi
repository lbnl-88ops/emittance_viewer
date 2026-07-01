; Emittance Viewer Installer NSIS Script

!include "MUI2.nsh"

; General
Name "Emittance Viewer"
OutFile "Emittance_Viewer_Installer.exe"
InstallDir "$PROGRAMFILES64\Emittance Viewer"
InstallDirRegKey HKLM "Software\EmittanceViewer" "Install_Dir"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Section
Section "Emittance Viewer (required)"
    SectionIn RO
    
    ; Clean swap: Check for existing installation and remove it if found
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer" "UninstallString"
    StrCmp $R0 "" skip_uninst
        ; If the uninstaller exists, run it silently
        DetailPrint "Removing previous version..."
        ; We use _?=$INSTDIR to ensure the uninstaller doesn't delete itself before finishing,
        ; and ExecWait so we don't start installing until it's done.
        ExecWait '"$INSTDIR\uninstall.exe" /S _?=$INSTDIR'
    skip_uninst:

    SetOutPath "$INSTDIR"
    
    ; Files to be installed
    File /r "dist\emittance_viewer\*.*"
    
    ; Write the installation path into the registry
    WriteRegStr HKLM "Software\EmittanceViewer" "Install_Dir" "$INSTDIR"
    
    ; Write the uninstall keys for Windows
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer" "DisplayName" "Emittance Viewer"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer" "NoRepair" 1
    WriteUninstaller "uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\Emittance Viewer"
    CreateShortcut "$SMPROGRAMS\Emittance Viewer\Emittance Viewer.lnk" "$INSTDIR\emittance_viewer.exe"
    CreateShortcut "$SMPROGRAMS\Emittance Viewer\Uninstall Emittance Viewer.lnk" "$INSTDIR\uninstall.exe"
    
SectionEnd

; Uninstaller Section
Section "Uninstall"
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\EmittanceViewer"
    DeleteRegKey HKLM "Software\EmittanceViewer"

    ; Remove files and uninstaller
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"

    ; Remove shortcuts
    Delete "$SMPROGRAMS\Emittance Viewer\Emittance Viewer.lnk"
    Delete "$SMPROGRAMS\Emittance Viewer\Uninstall Emittance Viewer.lnk"
    RMDir "$SMPROGRAMS\Emittance Viewer"

SectionEnd
