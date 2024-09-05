Here’s a step-by-step test case for validating the **Client Relations case approval** process in **Testim TTA**, ensuring that cases are sent for approval to the correct groups at the correct times.

### **Test Case: Client Relations Case Approval Process Validation**

#### **Objective**
Validate that the approval processes for client relations cases work as expected. This includes verifying that the case is sent for approval to the correct group and at the appropriate stage.

---

### **Step 1: Log in to Salesforce with FS Client Relations Profile**

1. **Action**: Use Testim TTA to log in as a user with the **FS Client Relations** profile.
2. **Steps**:
   - Start recording a new test case.
   - Navigate to the Salesforce login page.
   - Enter the username and password of a user with the **FS Client Relations** profile.
   - Click **Login**.
3. **Expected Result**: The user is successfully logged into Salesforce and directed to the homepage with the appropriate profile.

---

### **Step 2: Navigate to the Cases Tab**

1. **Action**: Navigate to the **Cases** tab to create a new client relations case.
2. **Steps**:
   - Click on the **App Launcher** (9 dots in the top left corner).
   - Search for **"Cases"** and click on the **Cases** tab.
3. **Expected Result**: You are on the **Cases** page, with a list of current cases displayed.

---

### **Step 3: Create a New Client Relations Case**

1. **Action**: Create a new client relations case to initiate the approval process.
2. **Steps**:
   - Click the **New** button on the Cases page.
   - Select the **Client Relations** case record type, if applicable.
   - Fill in the case details:
     - **Case Subject**: "Client Relations - Approval Test"
     - **Description**: "Testing case approval process for client relations"
     - **Priority**: High
     - **Origin**: Email
     - **Assigned To**: Set the appropriate initial assignment.
   - Click **Save** to create the case.
3. **Expected Result**: A new client relations case is created, and you are redirected to the case details page.

---

### **Step 4: Submit the Case for Approval**

1. **Action**: Submit the newly created case for approval.
2. **Steps**:
   - On the case details page, locate the **Submit for Approval** button (this might be under the **Actions** section or a dropdown menu).
   - Click **Submit for Approval**.
   - Choose the appropriate approval process (if there are multiple) and ensure it aligns with the **FS Client Relations** approval process.
   - Click **Submit** to send the case for approval.
3. **Expected Result**: The case is successfully submitted for approval, and the status of the case is updated accordingly (e.g., **Pending Approval**).

---

### **Step 5: Validate the Case is Sent to the Correct Group for Approval**

1. **Action**: Validate that the case has been sent to the correct group for approval.
2. **Steps**:
   - Locate the **Approval History** section on the case details page.
   - Verify that the **Approver** listed is the correct group (e.g., **Client Relations Approval Team**).
   - Use **Text Equals** validation in Testim to confirm that the approval request was sent to the correct group.
3. **Expected Result**: The case is sent to the correct approval group based on the approval process configured for the **FS Client Relations** profile.

---

### **Step 6: Validate Approval Timing**

1. **Action**: Validate that the case is sent for approval at the correct time (immediately after submission or after certain criteria are met).
2. **Steps**:
   - Check the **Approval History** timestamps to ensure that the case was sent for approval promptly after submission.
   - Use **Text Contains** or **Text Equals** to validate the timestamps and confirm they align with the expected timeline.
3. **Expected Result**: The case is sent for approval at the correct stage and time as defined by the approval process.

---

### **Step 7: Approve or Reject the Case as an Approver**

1. **Action**: Log in as an approver or use an automation to approve/reject the case.
2. **Steps**:
   - Navigate to the **Approval Requests** (either through the approver’s email notification or directly within Salesforce).
   - Open the case approval request.
   - Click **Approve** or **Reject**, depending on the test scenario.
   - Add any comments, if required, and click **Submit**.
3. **Expected Result**: The case is either approved or rejected, and the case status is updated accordingly (e.g., **Approved** or **Rejected**).

---

### **Step 8: Validate the Case Status and Approval Outcome**

1. **Action**: Verify that the case status is updated correctly after approval/rejection.
2. **Steps**:
   - Check the **Case Status** field on the case details page.
   - Use **Text Equals** to validate that the status has been updated to **Approved** or **Rejected**, based on the outcome.
   - Verify that the **Approval History** section reflects the correct approval outcome.
3. **Expected Result**: The case status is updated correctly, and the approval history accurately reflects the decision.

---

### **Step 9: Log Out (Optional)**

1. **Action**: Log out of Salesforce if necessary.
2. **Steps**:
   - Click on the user profile icon in the top right corner.
   - Select **Logout** to exit Salesforce.
3. **Expected Result**: The user is logged out successfully.

