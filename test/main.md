For Mac users, using Outlook via VBA is not supported. Instead, we can use Apple Mail for sending emails via VBA on Mac. Below are the updated steps to create a solution compatible with both Windows and Mac, utilizing Apple Mail for Mac.

### Step 1: Create the Centralized Script

1. **Open Excel** and press `ALT + F11` to open the VBA editor.
2. **Insert a New Module** in the personal macro workbook (`PERSONAL.XLSB`).
3. **Add the Send Email Script** to the module. This script will handle both Windows and Mac environments:

   ```vba
   ' Centralized script in the personal macro workbook
   Sub CentralizedSendEmail()
       #If Mac Then
           Call SendEmailMac
       #Else
           Call SendEmailWindows
       #End If
   End Sub

   ' Subroutine for Windows (using Outlook)
   Sub SendEmailWindows()
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

   ' Subroutine for Mac (using Apple Mail)
   Sub SendEmailMac()
       Dim script As String
       Dim EmailTo As String
       Dim EmailSubject As String
       Dim EmailBody As String
       
       ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
       EmailTo = ActiveWorkbook.Sheets("Sheet1").Range("A1").Value
       EmailSubject = ActiveWorkbook.Sheets("Sheet1").Range("A2").Value
       EmailBody = ActiveWorkbook.Sheets("Sheet1").Range("A3").Value

       ' AppleScript to send email using Apple Mail
       script = "tell application ""Mail""" & vbCrLf & _
                "set newMessage to make new outgoing message with properties {subject:""" & EmailSubject & """, content:""" & EmailBody & """ & vbCrLf & _
                "tell newMessage" & vbCrLf & _
                "make new to recipient at end of to recipients with properties {address:""" & EmailTo & """}" & vbCrLf & _
                "send" & vbCrLf & _
                "end tell" & vbCrLf & _
                "end tell"

       MacScript (script)
   End Sub
   ```

4. **Save and Close** the personal macro workbook.

### Step 2: Create the Add-In to Add the Button

1. **Open a New Workbook** and press `ALT + F11` to open the VBA editor.
2. **Insert a New Module** and add the following code to add a Form Control button dynamically:

   ```vba
   Private Sub Workbook_Open()
       Dim ws As Worksheet
       Dim btn As Button
       Dim btnText As String
       
       ' Check if the workbook name starts with "Expense Report"
       If Left(ThisWorkbook.Name, 14) = "Expense Report" Then
           ' Add the button to the first worksheet
           Set ws = ThisWorkbook.Sheets(1)
           Set btn = ws.Buttons.Add(10, 10, 100, 30)
           btn.OnAction = "PERSONAL.XLSB!CentralizedSendEmail"
           btnText = "Send Email"
           ws.Shapes(btn.Name).TextFrame2.TextRange.Characters.Text = btnText
       End If
   End Sub
   ```

3. **Save the Workbook as an Add-In**:
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

**Centralized Script in PERSONAL.XLSB:**

```vba
' Centralized script in the personal macro workbook
Sub CentralizedSendEmail()
    #If Mac Then
        Call SendEmailMac
    #Else
        Call SendEmailWindows
    #End If
End Sub

' Subroutine for Windows (using Outlook)
Sub SendEmailWindows()
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

' Subroutine for Mac (using Apple Mail)
Sub SendEmailMac()
    Dim script As String
    Dim EmailTo As String
    Dim EmailSubject As String
    Dim EmailBody As String
    
    ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
    EmailTo = ActiveWorkbook.Sheets("Sheet1").Range("A1").Value
    EmailSubject = ActiveWorkbook.Sheets("Sheet1").Range("A2").Value
    EmailBody = ActiveWorkbook.Sheets("Sheet1").Range("A3").Value

    ' AppleScript to send email using Apple Mail
    script = "tell application ""Mail""" & vbCrLf & _
             "set newMessage to make new outgoing message with properties {subject:""" & EmailSubject & """, content:""" & EmailBody & """ & vbCrLf & _
             "tell newMessage" & vbCrLf & _
             "make new to recipient at end of to recipients with properties {address:""" & EmailTo & """}" & vbCrLf & _
             "send" & vbCrLf & _
             "end tell" & vbCrLf & _
             "end tell"

    MacScript (script)
End Sub
```

**Workbook_Open Event in ExpenseReportButtonAddIn.xlam:**

```vba
Private Sub Workbook_Open()
    Dim ws As Worksheet
    Dim btn As Button
    Dim btnText As String
    
    ' Check if the workbook name starts with "Expense Report"
    If Left(ThisWorkbook.Name, 14) = "Expense Report" Then
        ' Add the button to the first worksheet
        Set ws = ThisWorkbook.Sheets(1)
        Set btn = ws.Buttons.Add(10, 10, 100, 30)
        btn.OnAction = "PERSONAL.XLSB!CentralizedSendEmail"
        btnText = "Send Email"
        ws.Shapes(btn.Name).TextFrame2.TextRange.Characters.Text = btnText
    End If
End Sub
```

This approach ensures that the "Send Email" button is added dynamically to any "Expense Report" workbook and points to the centralized script, working on both Windows and Mac.