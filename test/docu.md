In the workflow you described, the part of the automation that would require signatures using DocuSign typically occurs after the cash flow notice has been reviewed and is ready for final approval. Specifically, this is the stage where important documents are finalized and need to be signed off by a key stakeholder, such as the Managing Director, before the process can proceed or be completed.

### Steps in the Workflow Requiring DocuSign:

#### **1. Preparing the Confirmation Letter (Step 7)**
   - **Process:** After compiling the distribution breakdown and verifying all details, the employee handling the notice prepares the confirmation letter that accompanies the cash flow notice.
   - **DocuSign Involvement:** This confirmation letter might need to be signed electronically before being attached to the cash flow notice. At this point, the document (cash flow notice + confirmation letter) can be sent to DocuSign for the necessary signatures.

#### **2. Final Review and Approval by Managing Director (Step 9)**
   - **Process:** After the confirmation letter is prepared and the cash flow notice is verified, the document is sent for final review and approval.
   - **DocuSign Involvement:** The Managing Director needs to sign the final document electronically via DocuSign. This is a critical step where the final document (which now includes the confirmation letter) is sent to DocuSign for the Managing Director's signature.

### Implementing DocuSign in the Workflow Automation:

1. **Condition Trigger for DocuSign:**
   - **Trigger:** When the ticket reaches the status "Ready for Signature" (or any status indicating that the document is ready for final approval and needs to be signed).
   - **Action:** Send the attached document (cash flow notice and confirmation letter) to DocuSign for signature.

   **How to Set This Up:**
   - In Workflow Automator, add an action that triggers when the ticket status is updated to "Ready for Signature."
   - If integrated, select the option to "Send Document to DocuSign" with the correct recipient details (e.g., the Managing Director’s email).

2. **Monitoring Signature Completion:**
   - **Trigger:** When the document has been signed via DocuSign.
   - **Action:** Update the ticket status to "Signed" or "Awaiting Final Review."

   **How to Set This Up:**
   - This may require setting up a webhook or using the DocuSign API to notify Freshservice when the document has been signed.
   - Once signed, the ticket can be automatically updated, and a notification can be sent to the relevant team members.

3. **Final Steps Post-Signature:**
   - **Condition:** Once the document is signed and the ticket status is updated to "Signed."
   - **Action:** Reassign the ticket to the final reviewer or the person responsible for dispatching the document to the custodian bank.
   - **Additional Actions:** Attach the signed document to the ticket and update the status to indicate that the document is "Finalized" or "Ready for Dispatch."

### Summary:
- **DocuSign is primarily involved** in the stages where documents need to be reviewed and signed by key stakeholders, such as after the preparation of the confirmation letter and during the final approval by the Managing Director.
- **Integration in Workflow:** The DocuSign steps should be integrated as actions within your Freshservice Workflow Automator, triggered by specific status changes in the ticket (e.g., "Ready for Signature").

By including DocuSign in these parts of the workflow, you ensure that critical documents are signed electronically in a secure and trackable manner, which is especially important for legal or compliance reasons.