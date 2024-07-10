To ensure that the button and script appear in every Excel file or at least in files starting with "Expense Report," you can create an Excel Add-In with an `Workbook_Open` event that checks the workbook name and adds the button dynamically. Below are the steps to achieve this:

### Step 1: Create the VBA Script

1. **Open Excel and Press `ALT + F11`** to open the VBA editor.
2. **Insert a New Module** by clicking `Insert > Module`.
3. **Add the Send Email Script** to the module:

   ```vba
   Sub SendEmail()
       Dim OutlookApp As Object
       Dim OutlookMail As Object
       Dim EmailTo As String
       Dim EmailSubject As String
       Dim EmailBody As String
       
       ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
       EmailTo = ThisWorkbook.Sheets("Sheet1").Range("A1").Value
       EmailSubject = ThisWorkbook.Sheets("Sheet1").Range("A2").Value
       EmailBody = ThisWorkbook.Sheets("Sheet1").Range("A3").Value

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

### Step 2: Create the Add-In with Workbook_Open Event

1. **Insert Another Module** for the Workbook_Open event.
2. **Add the Workbook_Open Event** to check the workbook name and add the button:

   ```vba
   Private Sub Workbook_Open()
       Dim ws As Worksheet
       Dim button As Object
       
       ' Check if the workbook name starts with "Expense Report"
       If Left(ThisWorkbook.Name, 14) = "Expense Report" Or ThisWorkbook.Name = "MyWorkbook.xlsx" Then
           ' Add the button to the first worksheet
           Set ws = ThisWorkbook.Sheets(1)
           Set button = ws.OLEObjects.Add(ClassType:="Forms.CommandButton.1", _
                                          Left:=10, Top:=10, Width:=100, Height:=30)
           button.Object.Caption = "Send Email"
           button.Object.OnAction = "SendEmail"
       End If
   End Sub
   ```

### Step 3: Save as an Add-In

1. **Save the Workbook as an Add-In**: 
   - Go to `File > Save As`.
   - Choose `Excel Add-In (*.xlam)` from the `Save as type` dropdown.
   - Give it a name, like `EmailButtonAddIn.xlam`, and save it.

### Step 4: Install the Add-In

1. **Load the Add-In**:
   - Go to `File > Options > Add-Ins`.
   - In the `Manage` dropdown at the bottom, select `Excel Add-ins` and click `Go`.
   - Click `Browse`, find your Add-In file (`EmailButtonAddIn.xlam`), and select it.
   - Ensure the Add-In is checked in the list and click `OK`.

### Step 5: Testing the Add-In

1. **Open an Excel Workbook** whose name starts with "Expense Report" or the specific name you want to test.
2. **Verify the Button**: 
   - Check that the "Send Email" button appears on the first worksheet.
   - Click the button to ensure it runs the VBA script and sends the email.

### Complete VBA Code Example

Here's the complete VBA code for the Add-In:

```vba
' Module for sending email
Sub SendEmail()
    Dim OutlookApp As Object
    Dim OutlookMail As Object
    Dim EmailTo As String
    Dim EmailSubject As String
    Dim EmailBody As String
    
    ' Assuming data is in cells A1 (To), A2 (Subject), A3 (Body)
    EmailTo = ThisWorkbook.Sheets("Sheet1").Range("A1").Value
    EmailSubject = ThisWorkbook.Sheets("Sheet1").Range("A2").Value
    EmailBody = ThisWorkbook.Sheets("Sheet1").Range("A3").Value

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

' Module for Workbook_Open event
Private Sub Workbook_Open()
    Dim ws As Worksheet
    Dim button As Object
    
    ' Check if the workbook name starts with "Expense Report"
    If Left(ThisWorkbook.Name, 14) = "Expense Report" Or ThisWorkbook.Name = "MyWorkbook.xlsx" Then
        ' Add the button to the first worksheet
        Set ws = ThisWorkbook.Sheets(1)
        Set button = ws.OLEObjects.Add(ClassType:="Forms.CommandButton.1", _
                                       Left:=10, Top:=10, Width:=100, Height:=30)
        button.Object.Caption = "Send Email"
        button.Object.OnAction = "SendEmail"
    End If
End Sub
```

This approach ensures that every time you open an Excel workbook with a name starting with "Expense Report" or a specific name, a "Send Email" button is added to the first worksheet, and clicking the button runs the script to send an email.