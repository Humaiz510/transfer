The data appears to show a matrix where different **Funds** (Private, Public, etc.), **Actions**, and **Activity Types** are associated with specific point values. There are separate columns for **Task Types** (yellow side) and **Event Types** (blue side), each linked to points based on the combination of fund and activity type.

### **Key Structure of the Matrix:**
1. **Funds Discussed**:
   - Private Fund, Public Fund, Legacy Fund, etc.

2. **Actions**:
   - Scheduled Webinar Attendee, Scheduled RD/CPM Meeting, Left Voicemail, etc.

3. **Task Types**:
   - Email, Inbound/Outbound Call, Sales Presentation, etc.

4. **Event Types**:
   - One-on-One Meeting, Group Meeting, Virtual Sales Presentation, etc.

5. **Points**:
   - Each combination of a fund + action + type results in a specific point value.

### **Plan for the Test Case**:
To validate that the point values are correct based on the fund, action, and type, we will:
1. **Test all combinations** of funds, actions, and types.
2. **Validate** that the correct point value is displayed in Salesforce for each combination.

### **Test Case: Activity Points Validation Based on Fund, Action, and Type**

#### **Objective**
Validate that point values are correct based on different funds, actions, and types, using the matrix provided.

---

### **Step 1: Log in to Salesforce with FS – Sales Profile**

1. **Action**: Use Testim TTA to log in as a user with the **FS – Sales** profile.
2. **Steps**:
   - Start recording a new test case.
   - Navigate to the Salesforce login page.
   - Enter the username and password of a user with the **FS – Sales** profile.
   - Click **Login**.
3. **Expected Result**: The user is successfully logged into Salesforce and directed to the homepage.

---

### **Step 2: Navigate to the Activities Tab**

1. **Action**: Navigate to the **Activities** tab.
2. **Steps**:
   - Click on the **App Launcher** (9 dots in the top left corner).
   - Search for **"Activities"** and click on the **Activities** tab.
3. **Expected Result**: You are on the **Activities** page, where a list of current activities is displayed.

---

### **Step 3: Create a New Activity**

1. **Action**: Create a new activity based on a specific combination of **Fund**, **Action**, and **Type**.
2. **Steps**:
   - Click the **New Activity** button.
   - Select the following fields based on the matrix:
     - **Fund**: Choose **Private Fund**.
     - **Action**: Choose **Scheduled RD/CPM Meeting**.
     - **Type**: Choose **Sales Presentation** (for Task) or **Meeting** (for Event).
   - Click **Save**.
3. **Expected Result**: A new activity is created with a point value assigned based on the combination.

---

### **Step 4: Capture the Point Value for the Activity**

1. **Action**: Capture the point value assigned to the activity.
2. **Steps**:
   - On the activity details page, locate the **Point Value** field.
   - Use **Get Property** in Testim to capture the point value.
   - Store the captured point value in a variable (e.g., `activityPointValue`).
3. **Expected Result**: The correct point value is displayed based on the combination of fund, action, and type.

---

### **Step 5: Validate the Point Value Based on the Matrix**

1. **Action**: Validate that the captured point value matches the point value from the matrix.
2. **Steps**:
   - Based on the matrix, manually calculate or obtain the correct point value for the selected combination.
   - Use a validation step in Testim (e.g., **Text Equals**) to compare the captured point value with the expected value.
   - Example: If the combination of **Private Fund + Scheduled RD/CPM Meeting + Sales Presentation** results in **28 points**, use **Text Equals** to validate that the **Point Value** is 28.
3. **Expected Result**: The **Point Value** is correct according to the matrix.

---

### **Step 6: Repeat for Different Combinations of Fund, Action, and Type**

1. **Action**: Repeat the process for multiple combinations to ensure that all point values are correct based on the matrix.
2. **Steps**:
   - Create new activities using different combinations of **Fund** (Private, Public, etc.), **Action**, and **Type**.
   - Capture the point values for each combination and validate them using the matrix.
3. **Expected Result**: The point values are validated for all combinations.

---

### **Step 7: Log Out (Optional)**

1. **Action**: Log out of Salesforce.
2. **Steps**:
   - Click on the user profile icon in the top right corner.
   - Select **Logout**.
3. **Expected Result**: The user is logged out successfully.

---

### **Key Assertions for Validation:**

1. **Correct Point Assignment**: Ensure the points assigned match the matrix based on the fund,