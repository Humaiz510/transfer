To ensure that the button loads every time for every "Expense Report" and points to a script stored in a central location (like a personal macro workbook or an Add-In), follow these steps:

### Step 1: Create the Centralized Script Location

1. **Open Excel** and press `ALT + F11` to open the VBA editor.
2. **Insert a New Module** in the personal macro workbook or an Add-In workbook.
3. **Add the Send Email Script** to the module:

   ```vba
   ' Centralized script in the personal macro workbook or Add-In
   Sub CentralizedSendEmail()
       Dim OutlookApp As Object
       Dim OutlookMail As Object
       Dim EmailTo As String
       Dim EmailSubject As String
       Dim EmailBody As String
       
       ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
       EmailTo = ActiveWorkbook.Sheets("Sheet1").Range("A1").Value
       EmailSubject = ActiveWorkbook.Sheets("Sheet1").Range("A2").Value
       EmailBody = ActiveWorkbook.Sheets("Sheet1").Range("A3").Value

       ' Create the Outlook application and the email item
       Set OutlookApp = CreateObject("Outlook.Application")
       Set OutlookMail = OutlookApp.CreateItem(0)

       ' Set email parameters
       With OutlookMail
           .To = EmailTo
           .Subject = EmailSubject
           .Body = EmailBody
           .Send
       End With

       ' Cleanup
       Set OutlookMail = Nothing
       Set OutlookApp = Nothing
   End Sub
   ```

4. **Save and Close** the personal macro workbook (`PERSONAL.XLSB`) or the Add-In workbook (`*.xlam`).

### Step 2: Load the Button in Every "Expense Report" Workbook

1. **Open a New Workbook** and press `ALT + F11` to open the VBA editor.
2. **Insert a New Module** by clicking `Insert > Module`.
3. **Add the Workbook_Open Event** to check the workbook name and add the button:

   ```vba
   Private Sub Workbook_Open()
       Dim ws As Worksheet
       Dim button As Object
       
       ' Check if the workbook name starts with "Expense Report"
       If Left(ThisWorkbook.Name, 14) = "Expense Report" Then
           ' Add the button to the first worksheet
           Set ws = ThisWorkbook.Sheets(1)
           Set button = ws.OLEObjects.Add(ClassType:="Forms.CommandButton.1", _
                                          Left:=10, Top:=10, Width:=100, Height:=30)
           button.Object.Caption = "Send Email"
           button.Object.OnAction = "RunCentralizedScript"
       End If
   End Sub

   Sub RunCentralizedScript()
       Application.Run "PERSONAL.XLSB!CentralizedSendEmail"
       ' or if using an Add-In:
       ' Application.Run "YourAddInName.xlam!CentralizedSendEmail"
   End Sub
   ```

4. **Save as an Add-In**:
   - Go to `File > Save As`.
   - Choose `Excel Add-In (*.xlam)` from the `Save as type` dropdown.
   - Give it a name, like `ExpenseReportButtonAddIn.xlam`, and save it.

### Step 3: Install the Add-In

1. **Load the Add-In**:
   - Go to `File > Options > Add-Ins`.
   - In the `Manage` dropdown at the bottom, select `Excel Add-ins` and click `Go`.
   - Click `Browse`, find your Add-In file (`ExpenseReportButtonAddIn.xlam`), and select it.
   - Ensure the Add-In is checked in the list and click `OK`.

### Step 4: Testing

1. **Open an Excel Workbook** whose name starts with "Expense Report".
2. **Verify the Button**:
   - Check that the "Send Email" button appears on the first worksheet.
   - Click the button to ensure it runs the centralized script and sends the email.

### Complete VBA Code Example

**Centralized Script in PERSONAL.XLSB or Add-In:**

```vba
' Centralized script in the personal macro workbook or Add-In
Sub CentralizedSendEmail()
    Dim OutlookApp As Object
    Dim OutlookMail As Object
    Dim EmailTo As String
    Dim EmailSubject As String
    Dim EmailBody As String
    
    ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
    EmailTo = ActiveWorkbook.Sheets("Sheet1").Range("A1").Value
    EmailSubject = ActiveWorkbook.Sheets("Sheet1").Range("A2").Value
    EmailBody = ActiveWorkbook.Sheets("Sheet1").Range("A3").Value

    ' Create the Outlook application and the email item
    Set OutlookApp = CreateObject("Outlook.Application")
    Set OutlookMail = OutlookApp.CreateItem(0)

    ' Set email parameters
    With OutlookMail
        .To = EmailTo
        .Subject = EmailSubject
        .Body = EmailBody
        .Send
    End With

    ' Cleanup
    Set OutlookMail = Nothing
    Set OutlookApp = Nothing
End Sub
```

**Workbook_Open Event in ExpenseReportButtonAddIn.xlam:**

```vba
Private Sub Workbook_Open()
    Dim ws As Worksheet
    Dim button As Object
    
    ' Check if the workbook name starts with "Expense Report"
    If Left(ThisWorkbook.Name, 14) = "Expense Report" Then
        ' Add the button to the first worksheet
        Set ws = ThisWorkbook.Sheets(1)
        Set button = ws.OLEObjects.Add(ClassType:="Forms.CommandButton.1", _
                                       Left:=10, Top:=10, Width:=100, Height:=30)
        button.Object.Caption = "Send Email"
        button.Object.OnAction = "RunCentralizedScript"
    End If
End Sub

Sub RunCentralizedScript()
    Application.Run "PERSONAL.XLSB!CentralizedSendEmail"
    ' or if using an Add-In:
    ' Application.Run "YourAddInName.xlam!CentralizedSendEmail"
End Sub
```

This method ensures that every "Expense Report" workbook will automatically have a button that points to a centralized script, keeping the email-sending logic in a single, maintainable location.