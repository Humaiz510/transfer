To add a button in your spreadsheet to run a VBA script that sends an email using data from the spreadsheet, follow these steps:

1. **Open the Developer Tab**: 
   - If the Developer tab is not visible in Excel, you need to enable it. 
   - Go to `File` > `Options`.
   - In the Excel Options window, select `Customize Ribbon`.
   - Check the `Developer` checkbox on the right panel and click `OK`.

2. **Insert a Button**:
   - Go to the `Developer` tab.
   - In the `Controls` group, click `Insert`.
   - Under `Form Controls`, click the `Button (Form Control)` button.
   - Click and drag on the worksheet where you want to place the button.

3. **Assign a Macro to the Button**:
   - After placing the button, the `Assign Macro` dialog box will appear.
   - Select the macro (your VBA script that sends the email) from the list or create a new one by clicking `New`.

4. **Write or Select Your VBA Script**:
   - If you clicked `New`, the VBA editor will open. Write your script in the newly created subroutine.
   - If you already have a script, you can assign it to the button by selecting it in the `Assign Macro` dialog box.

5. **Example VBA Script**:
   Here’s an example of a simple VBA script that sends an email using data from the spreadsheet:

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

6. **Save and Test**:
   - Save your workbook as a macro-enabled workbook (`*.xlsm`).
   - Click the button you added to test if it correctly runs the VBA script and sends the email.

By following these steps, you should be able to add a button to your Excel spreadsheet that runs your email-sending VBA script.