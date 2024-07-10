Yes, following the steps provided will ensure that the button and script are automatically added to every workbook with a name starting with "Expense Report" when you open it. Here's a summary of how it works:

1. **Create and Save the Add-In**:
   - You create an Excel Add-In (`.xlam`) that contains the VBA script to send an email and the `Workbook_Open` event that adds the button to the worksheet if the workbook name meets the criteria.

2. **Load the Add-In in Excel**:
   - You load this Add-In in Excel so that it is always active.

3. **Automatic Button Addition**:
   - When you open any workbook, the `Workbook_Open` event is triggered. 
   - The event checks if the workbook's name starts with "Expense Report".
   - If the condition is met, it adds a button to the first worksheet of the workbook and assigns the email-sending macro to it.

### Detailed Steps and Final Code

**1. Create the Add-In:**

1. **Open Excel** and press `ALT + F11` to open the VBA editor.
2. **Insert a New Module** by clicking `Insert > Module` and add the email-sending script:

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

3. **Insert Another Module** for the `Workbook_Open` event by clicking `Insert > Module` and add the following code:

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
           button.Object.OnAction = "SendEmail"
       End If
   End Sub
   ```

4. **Save the Workbook as an Add-In**:
   - Go to `File > Save As`.
   - Choose `Excel Add-In (*.xlam)` from the `Save as type` dropdown.
   - Give it a name, like `ExpenseReportAddIn.xlam`, and save it.

**2. Load the Add-In in Excel**:

1. **Go to `File > Options > Add-Ins`**.
2. **In the `Manage` dropdown at the bottom**, select `Excel Add-ins` and click `Go`.
3. **Click `Browse`**, find your Add-In file (`ExpenseReportAddIn.xlam`), and select it.
4. **Ensure the Add-In is checked in the list** and click `OK`.

**3. Testing**:

1. **Open an Excel Workbook** whose name starts with "Expense Report".
2. **Verify the Button**:
   - Check that the "Send Email" button appears on the first worksheet.
   - Click the button to ensure it runs the VBA script and sends the email.

### Complete VBA Code Example

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
    If Left(ThisWorkbook.Name, 14) = "Expense Report" Then
        ' Add the button to the first worksheet
        Set ws = ThisWorkbook.Sheets(1)
        Set button = ws.OLEObjects.Add(ClassType:="Forms.CommandButton.1", _
                                       Left:=10, Top:=10, Width:=100, Height:=30)
        button.Object.Caption = "Send Email"
        button.Object.OnAction = "SendEmail"
    End If
End Sub
```

By following these steps, you ensure that the button and script are automatically added to any workbook with a name starting with "Expense Report" upon opening, streamlining the process and making it consistent across all such files.