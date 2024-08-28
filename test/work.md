Great! Here’s a step-by-step guide to create an automation workflow in Freshservice that converts an email (with a .docx attachment) into a ticket and assigns it to a specific agent or group.

### Step 1: Configure Email to Ticket Conversion

1. **Navigate to Admin → Email Settings:**
   - Log in to Freshservice and go to the Admin panel.
   - Under “Support Channels,” click on “Email.”

2. **Add an Email Address:**
   - Click “New Email Address” to add the email address that Freshservice will monitor.
   - Enter the email address (e.g., support@yourdomain.com) and select the department or group that should handle these tickets.
   - Set the default priority, type, and status for tickets created from this email address.
   - Save your settings.

3. **Verify Email Configuration:**
   - Ensure that the email is correctly configured to convert incoming emails into tickets. Freshservice will automatically create a ticket for every email received at this address.

### Step 2: Create a Workflow in Workflow Automator

1. **Navigate to Admin → Workflow Automator:**
   - Go back to the Admin panel.
   - Under “Helpdesk Productivity,” click on “Workflow Automator.”

2. **Create a New Workflow:**
   - Click on “New Ticket Workflow.”
   - Name your workflow something descriptive, like “Docx Attachment Ticket Assignment.”

3. **Set the Trigger:**
   - In the “When” section, select the trigger as “When a Ticket is Created.”

4. **Add Conditions:**
   - Click on “+ Add Condition.”
   - Select "Ticket Attachment" from the list.
   - Set the condition to “Attachment Name contains .docx” to ensure this workflow only triggers when a .docx file is attached to the email.
   - You can add additional conditions if necessary (e.g., check if the ticket comes from a specific email address or has specific keywords in the subject).

5. **Add Actions:**
   - Click on “+ Add Action.”
   - Choose “Assign to Agent” or “Assign to Group” based on how you want to assign the ticket.
     - If assigning to an agent, select the specific agent from the dropdown.
     - If assigning to a group, choose the appropriate group.
   - Optionally, you can add more actions, such as sending notifications or adding tags to the ticket.

6. **Save and Activate the Workflow:**
   - Once you have set the trigger, conditions, and actions, click “Save.”
   - Ensure that the workflow is activated so it will run whenever a new ticket is created.

### Step 3: Test the Workflow

1. **Send a Test Email:**
   - Send a test email to the configured address with a .docx attachment to ensure that the workflow functions as expected.

2. **Verify Ticket Creation:**
   - Check Freshservice to see if the ticket was created and correctly assigned according to your workflow rules.

### Summary of Workflow Steps:
- **Trigger:** When a ticket is created.
- **Conditions:** Ticket contains a .docx attachment.
- **Actions:** Assign the ticket to a specific agent or group.

By following these steps, your Freshservice instance will automatically create tickets from emails with .docx attachments and assign them to the designated person or team, streamlining your support process.