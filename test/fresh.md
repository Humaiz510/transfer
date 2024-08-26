To create a Freshservice workflow that automatically creates a ticket based on an email (with a .docx attachment) and assigns a person to that ticket, follow these steps:

### Prerequisites:
1. **Freshservice Access:** You need administrative access to your Freshservice account.
2. **Email Setup:** Ensure that your Freshservice instance is connected to the email where the trigger will be received.

### Step-by-Step Guide:

#### Step 1: Configure Email to Ticket Conversion
Freshservice automatically converts emails into tickets by default. Ensure this is set up:
1. **Admin → Email Settings:** Verify that the email you want to use to create tickets is added here.
2. **Ticket Settings:** Ensure that new emails are automatically converted into tickets.

#### Step 2: Create a Workflow Automation
1. **Go to Admin → Workflow Automator:**
   - In Freshservice, click on the Admin tab and navigate to the Workflow Automator.

2. **Create a New Workflow:**
   - Click on "New Ticket Workflow."

3. **Define Trigger:**
   - Select the trigger for the workflow: "When a Ticket is Created."
   - You can further refine the conditions by adding a filter such as "Ticket contains an email with attachment" or "Attachment is of type .docx."

4. **Set Conditions (Optional):**
   - Add conditions to further filter the workflow based on specific criteria. For instance, you can check if the ticket contains a `.docx` attachment by using the "Ticket Attachment Type" condition.

5. **Add Actions:**
   - **Assign Agent:** After the ticket is created, use the action "Assign to Agent" to assign the ticket to a specific person or agent group.
   - **Attach Document:** Ensure that the `.docx` attachment remains attached to the ticket.

#### Step 3: Save and Activate Workflow
1. **Save the Workflow:** Once you have set the trigger, conditions, and actions, save the workflow.
2. **Activate the Workflow:** Make sure the workflow is active so that it will run whenever a ticket is created from an email.

### Sample Workflow Steps Overview:
1. **Trigger:** Email with .docx attachment received → Ticket is created.
2. **Conditions:** (Optional) Check if attachment is .docx.
3. **Actions:** Assign the ticket to a specified agent or group.

This workflow ensures that any incoming email with a `.docx` attachment creates a ticket and assigns it to the appropriate person.

Let me know if you need more detailed steps for any of these parts!