# Oracle® Banking Payments
## India Unified Payment Interface (UPI) User Guide

**Release 14.8.1.0.0**
**G44886-01**
**October 2025**

---

Oracle Banking Payments India Unified Payment Interface (UPI) User Guide, Release 14.8.1.0.0

G44886-01

Copyright © 2017, 2025, Oracle and/or its affiliates.

---

## Contents

1. [India Unified Payments Interface - UPI](#1-india-unified-payments-interface---upi)
   - 1.1 [Overview of UPI](#11-overview-of-upi)
     - 1.1.1 [Bank UPI Switch Financial APIs](#111-bank-upi-switch-financial-apis)
     - 1.1.2 [Bank UPI Switch Non – Financial APIs](#112-bank-upi-switch-non--financial-apis)
     - 1.1.3 [PSP UPI Switch Financial APIs](#113-psp-upi-switch-financial-apis)
     - 1.1.4 [PSP UPI Switch Non – Financial APIs](#114-psp-upi-switch-non--financial-apis)
     - 1.1.5 [UPI International / Foreign Inward Remittance / Foreign Outward Remittance APIs](#115-upi-international--foreign-inward-remittance--foreign-outward-remittance-apis)
     - 1.1.6 [UPI Lite](#116-upi-lite)
     - 1.1.7 [UPI Reconciliation Extraction](#117-upi-reconciliation-extraction)

---

## Preface

### Purpose

This guide is designed to help acquaint you with the Oracle Banking Payments application. This guide provides answers to specific features and procedures that the user need to be aware of the module to function successfully.

### Audience

This manual is intended for the following User/User Roles:

| Role | Function |
|------|----------|
| Implementation & IT Staff | Implementation & Maintenance of the Software |

### Documentation Accessibility

For information about Oracle's commitment to accessibility, visit the Oracle Accessibility Program website at http://www.oracle.com/pls/topic/lookup?ctx=acc&id=docacc.

**Access to Oracle Support**

Oracle customers that have purchased support have access to electronic support through My Oracle Support. For information, visit http://www.oracle.com/pls/topic/lookup?ctx=acc&id=info or visit http://www.oracle.com/pls/topic/lookup?ctx=acc&id=trs if you are hearing impaired.

### Critical Patches

Oracle advises customers to get all their security vulnerability information from the Oracle Critical Patch Update Advisory, which is available at Critical Patches, Security Alerts and Bulletins. All critical patches should be applied in a timely manner to make sure effective security, as strongly recommended by Oracle Software Security Assurance.

### Diversity and Inclusion

Oracle is fully committed to diversity and inclusion. Oracle respects and values having a diverse workforce that increases thought leadership and innovation. As part of our initiative to build a more inclusive culture that positively impacts our employees, customers, and partners, we are working to remove insensitive terms from our products and documentation. We are also mindful of the necessity to maintain compatibility with our customers' existing technologies and the need to ensure continuity of service as Oracle's offerings and industry standards evolve. Because of these technical constraints, our effort to remove insensitive terms is ongoing and will take time and external cooperation.

### Conventions

The following text conventions are used in this document:

| Convention | Meaning |
|------------|---------|
| **boldface** | Boldface type indicates graphical user interface elements associated with an action, or terms defined in text. |
| *italic* | Italic type indicates book titles, emphasis, or placeholder variables for which you supply particular values. |
| `monospace` | Monospace type indicates commands within a paragraph, URLs, code in examples, text that appears on the screen, or text that you enter. |

### Related Resources

For more information on any related features, refer to the following documents:

- *Getting Started User Guide*
- *Oracle Banking Security Management System User Guide*
- *Oracle Banking Microservices Platform Foundation User Guide*
- *Routing Hub Configuration User Guide*
- *Oracle Banking Common Core User Guide*
- *Interest and Charges User Guide*
- *Oracle Banking Liquidity Management Configuration Guide*
- *Oracle Banking Liquidity Management File Upload User Guide*

### Screenshot Disclaimer

Personal information used in the interface or documents is dummy and does not exist in the real world. It is only for reference purposes.

### Acronyms and Abbreviations

The list of the acronyms and abbreviations that are used in this guide are as follows:

| Abbreviation | Description |
|--------------|-------------|
| DDA | Demand Deposit Accounts |
| ECA | External Credit Approval |
| EOD | End of Day |
| IBAN | International Bank Account Number |

### Basic Actions

The basic actions performed in the screens are as follows:

| Actions | Description |
|---------|-------------|
| **New** | Click **New** to add a new record. The system displays a new record to specify the required data. The fields marked with asterisk are mandatory.<br>- This button is displayed only for the records that are already created. |
| **Save** | Click **Save** to save the details entered or selected in the screen. |
| **Unlock** | Click **Unlock** to update the details of an existing record. The system displays an existing record in editable mode.<br>- This button is displayed only for the records that are already created. |
| **Authorize** | Click **Authorize** to authorize the record created. A maker of the screen is not allowed to authorize the same. Only a checker can authorize a record.<br>- This button is displayed only for the already created records. For more information on the process, refer Authorization Process. |
| **Approve** | Click **Approve** to approve the initiated record.<br>- This button is displayed once the user click **Authorize**. |
| **Audit** | Click **Audit** to view the maker details, checker details of the particular record.<br>- This button is displayed only for the records that are already created. |
| **Close** | Click **Close** to close a record. This action is available only when a record is created. |
| **Confirm** | Click **Confirm** to confirm the action performed. |
| **Cancel** | Click **Cancel** to cancel the action performed. |
| **Compare** | Click **Compare** to view the comparison through the field values of old record and the current record.<br>- This button is displayed in the widget once the user click **Authorize**. |
| **View** | Click **View** to view the details in a particular modification stage.<br>- This button is displayed in the widget once the user click **Authorize**. |
| **View Difference only** | Click **View Difference only** to view a comparison through the field element values of old record and the current record, which has undergone changes.<br>- This button is displayed once the user click **Compare**. |
| **Expand All** | Click **Expand All** to expand and view all the details in the sections.<br>- This button is displayed once the user click **Compare**. |
| **Collapse All** | Click **Collapse All** to hide the details in the sections.<br>- This button is displayed once the user click **Compare**. |
| **OK** | Click **OK** to confirm the details in the screen. |

### Symbols, Definitions and Abbreviations

The following are some of the Symbols you are likely to find in the manual:

**Symbols**

| Icons | Function |
|-------|----------|
| ❌ | Exit |
| ➕ | Add row |
| ➖ | Delete row |
| 🔍 | Option List |

**Common Icons and its Definitions**

| Icon Names | Applicable Stages | Operation |
|------------|-------------------|-----------|
| Minimize | Initiation, Approval and Hand-off Retry | Users can minimize the transaction input screen. When the screen is minimized, it appears as to a separate tab within the same web page. |
| Maximize | Initiation, Approval and Hand-off Retry | User can maximize the transaction input screen. |
| Close | Initiation, Approval and Hand-off Retry | Users can close the transaction input screen. The system displays a warning message to the user that any unsaved data would be lost. User can either choose to ignore the message and close the screen or choose to 'save and close' the transaction. |

---

# 1 India Unified Payments Interface - UPI

## 1.1 Overview of UPI

This chapter covers the following topics:

- Bank UPI Switch Financial APIs
- Bank UPI Switch Non – Financial APIs
- PSP UPI Switch Financial APIs
- PSP UPI Switch Non – Financial APIs
- UPI International / Foreign Inward Remittance / Foreign Outward Remittance APIs — Enables secure cross-border payments, allowing users to send (outward remittance) or receive (inward remittance) funds internationally through the UPI platform, in compliance with RBI guidelines.
- UPI Lite — This topic gives information on UPI Lite application.
- UPI Reconciliation Extraction — This topic gives information on extraction of UPI Reconciliation.

---

### 1.1.1 Bank UPI Switch Financial APIs

Following are all supported APIs:

| API | Description |
|-----|-------------|
| ReqPay | NPCI sends this API to Remitter / Beneficiary bank to perform Debit / Credit transaction on the customer bank account for the UPI payment. |
| ReqBalEnq | NPCI sends this API to Bank for enquiring the account balance. |
| ReqChkTxn | NPCI sends this API to Bank for enquiring the transaction status. |
| ReqComplaint | NPCI sends this API to Bank for raising the complaint for a financial transaction. |
| ReqHbt | Both NPCI and Bank send this API to each other to check the connectivity. |

---

### 1.1.2 Bank UPI Switch Non – Financial APIs

Following are all supported APIs:

| API | Description |
|-----|-------------|
| ReqListAccount | NPCI sends this API to Bank for retrieving the list of account numbers associated with the mobile number sent in the request. |
| ReqOtp | NCPI sends this API to Bank for issuance of OTP (One Time Password) which would be sent to customer through SMS (Short Message Service). |
| ReqRegMob | NPCI sends this API to Bank to register the account number for the UPI services. |
| ReqSetCre | NPCI sends this API to Bank for maintenance of the UPI PIN. |
| ReqValAdd | NPCI sends this API to Bank for resolution of global address i.e., the combination of Account Number + IFSC code. |
| ReqMandate | NPCI sends this API to Remitter Bank for maintenance of the onetime / recurring mandate. |
| ReqMandateConfirmation | NPCI sends this API to Payee Bank for informing the mandate maintenance status. |
| ReqValCust | NPCI sends this API to Remitter Bank to validate the PAN number maintained against the account. |

---

### 1.1.3 PSP UPI Switch Financial APIs

Following are all supported APIs:

| API | Description |
|-----|-------------|
| ReqPay | This API is used to initiate a Pay/Collect transaction from the PSP UPI switch to the NPCI UPI switch. If the Payer PSP and Remitter Bank are the same entity, the request from the Payer PSP UPI switch to the NPCI UPI switch will be pre-approved, meaning the customer's account is debited before the request is sent to the NPCI UPI switch. |
| ReqBalEnq | PSP UPI switch sends this request to NPCI for enquiring the account balance. |
| ReqHbt | This API is a mechanism for monitoring the UPI system, including tracking connections with PSPs and sending End-of-Day (EOD) reports to PSPs. |
| ReqChkTxn | PSP UPI switch sends this API to NPCI for enquiring the transaction status. |
| ReqTxnConfirmation | NPCI sends this API to the Payee PSP for Pay transaction / Payer PSP for collect transaction to update the transaction status. |
| ReqAuthDetails | The API is used to authorize a payment and convert PSP-specific payment addresses into common global addresses (such as Aadhaar number, mobile number, or account and provider ID) that NPCI can recognize. This API is called to translate the PSP address and obtain the necessary authorization details. |
| ReqComplaint | PSP UPI switch sends this API to NPCI for raising a complaint against a financial transaction. |

---

### 1.1.4 PSP UPI Switch Non – Financial APIs

Following are all supported APIs:

| API | Description |
|-----|-------------|
| ReqListAccount | PSP UPI switch sends this request to NPCI for retrieving the list of account number associated against a mobile number. |
| ReqOtp | PSP UPI switch sends this API to NPCI for issuance of OTP (One Time Password) which would be sent to customer through SMS (Short Message Service). |
| ReqRegMob | PSP UPI switch sends this API to NPCI to register the account number for the UPI services. |
| ReqListPsp | NPCI maintains a list of all registered PSPs and their details. PSPs use this API to retrieve the list for local caching. Use this data to validate the payment address before initiating a transaction. |
| ReqListAccPvd | NPCI maintains a list of all account providers connected through the Unified Interface. This list is made available to the PSP UPI switch and should be provided to the PSP app to verify registered account providers before registering a customer account. PSP UPI switch sends this API to NPCI for retrieving the list of account providers. |
| ReqListKeys | PSP UPI switch sends this API to NPCI for retrieving the list of public keys for account providers and other entities in the UPI ecosystem. |
| ReqManageVae | NPCI provides a mechanism to protect customers from spoofing attempts involving well-known merchants such as LIC, Indian Railways, e-commerce platforms, telecom providers, and bill payment entities. This mechanism is implemented through an API that enables PSPs to manage and access a shared collection of verified address entries. NPCI, in collaboration with PSPs, defines the process for managing these entries. |
| ReqValCust | This API is used to validate unique identifier [PAN] of customer maintained at the customer bank. |
| ReqAuthValCust | The NPCI UPI switch triggers this API to the payer PSP UPI switch when VPA address translation is required. |
| ReqValAdd | This API is used by PSPs when their customers want to add a beneficiary within the PSP application for sending and receiving money. |
| ReqListVae | PSP UPI switch sends this API to NPCI for retrieving the list of verified address entities. |
| ReqMandate | This API allows the corporate/customer to create a mandate request via UPI. |
| ReqAuthMandate | This API is used to authorize a payment and translate PSP-specific payment addresses into common global addresses (such as Aadhaar number, mobile number, or account number with IFSC) that NPCI can understand. This API translates the PSP address and provides the necessary authorization details. |
| ReqMandateConfirmation | NPCI sends this API to PSP UPI switch informing the status of mandate maintenance. |

---

### 1.1.5 UPI International / Foreign Inward Remittance / Foreign Outward Remittance APIs

Enables secure cross-border payments, allowing users to send (outward remittance) or receive (inward remittance) funds internationally through the UPI platform, in compliance with RBI guidelines.

**UPI International** – Enables users to make UPI payments abroad (outside India) directly from their domestic bank accounts held in India.

**Foreign Inward Remittance (FIR)** – UPI facilitates crediting the domestic leg of foreign inward remittances to the member's account.

**Foreign Outward Remittance (FOR)** – UPI facilitates debiting the domestic leg of foreign outward remittances from the member's account.

The UPI International, FIR and FOR requirements are achieved through the following APIs:

**Table 1-1 UPI International, FIR and FOR APIs**

| API | Description |
|-----|-------------|
| ReqValQr Rest API | From Third-Party Application Provider (TPAP) to PSP UPI switch, to validate the QR code. |
| Query Service | The TPAP will fetch the response of ReqValQr from PSP UPI switch. |
| ReqValQr | The request from PSP UPI switch to NPCI UPI switch, to validate the QR code. |
| RespValQr | From NPCI UPI switch to PSP UPI switch, the response of ReqValQr. |
| ReqActivation Rest API | From TPAP to PSP UPI switch. |
| Query Service | The TPAP will fetch the response of ReqActivation from PSP UPI switch. |
| ReqValCust | From TPAP to PSP UPI switch, to support the parameter **type** with value **verifyUser**. |
| ReqValCust | From PSP to NPCI UPI switch, to support the parameter **type** with value **verifyUser**. |
| RespValCus | From NPCI to PSP UPI switch, to support the parameter **type** with value **verifyUser**. |
| Query Service | The TPAP will fetch the response of RespValCust from PSP UPI switch. |
| ReqActivation | The request is from PSP UPI switch to NPCI UPI switch, to Activate or Deactivate the customer account for international inward and outward transactions. |
| RespActivation | From NPCI UPI switch to PSP UPI switch, the response of ReqActivation request. |
| ReqActivation | The request is from NPCI UPI switch to Bank UPI switch, to Activate / Deactivate the customer account for international inward and outward transactions. |
| RespActivation | From Bank UPI switch to NPCI UPI switch, the response of ReqActivation request. |
| ReqPay | During financial transaction posting, the ReqPay API validates the Activate or Deactivate flag when the **Purpose Code** is 11 or the **Initiation Mode** is 12 with an institution block. |

---

### 1.1.6 UPI Lite

This topic gives information on UPI Lite application.

A UPI App user can choose to enable **UPI Lite**, an on-device wallet feature. Once **UPI Lite** is enabled, the user can allocate funds from the user's bank account to UPI Lite. These funds are held by the user's bank in an escrow, pool, or designated account, while the wallet balance is maintained on-device within the UPI app using the common library (CL).

The UPI Lite functionality allows a user to perform debit transactions from the On-Device Wallet up to the allowed per-transaction limit without entering the UPI PIN. There is a maximum UPI Lite balance that can be maintained in the On-Device Wallet at any time.

Replenishment of funds in UPI Lite can only be done online with **Additional Factor Authentication (AFA)** or through a registered UPI AutoPay setup by the user in online mode with AFA.

The **UPI Lite** requirements are implemented by making the following changes to the APIs:

**Table 1-2 UPI Lite APIs**

| API | Description |
|-----|-------------|
| ReqListKeys | ReqListKeys API from the PSP UPI switch to the NPCI UPI switch will be updated to support the following parameters:<br>- **Type**: GetLite<br>- **Account Address Type (Ac addrType)**: ACCOUNT<br>- **Detail Name**: IFSC<br>- **Value**: Blank |
| ReqPay | ReqPay API from the PSP UPI switch to the NPCI UPI switch has been updated with the following parameters:<br>- **Purpose**: 41 \| 42 \| 43 \| 44<br>- **Detail Name**: LRN<br>- **Value**: Blank<br>- **Cred Type**: Authorization Request Cryptogram (ARQC)<br>- **Subtype**: Initial |
| ReqPay | ReqPay API from the NPCI UPI switch to the Bank UPI switch has been updated with the following parameters:<br>- **Purpose**: 41 \| 42 \| 43 \| 44<br>- **Detail Name**: LRN<br>- **Value**: Blank |
| ReqChkTxn | ReqChkTxn API from the PSP UPI switch to the NPCI UPI switch will be updated with the following parameters:<br>- **Type**: LiteSync<br>- **Purpose**: 50 |
| ReqTxnConfirmation | ReqTxnConfirmation API from the NPCI UPI switch to the Bank UPI switch will be updated with the following parameters:<br>- **Purpose**: 50<br>- **acNum**: LRN |

---

### 1.1.7 UPI Reconciliation Extraction

This topic gives information on extraction of UPI Reconciliation.

From a reconciliation perspective, UPI will provide extracts containing details of transactions processed within a settlement cycle. Similarly, the Bank UPI Switch is expected to generate corresponding extracts for transactions executed during the same cycle. Additionally, from the Bank's Core Banking System (CBS) similar extracts should be generated. This enables the bank to perform reconciliation using information from the Bank, the UPI Switch, and the data received from NPCI.

The following files should be generated from Bank UPI Switch for the reconciliation:

**Table 1-3 UPI Reconciliation Extraction**

| API | Description |
|-----|-------------|
| P2P - Remitter | Includes all the transactions received as P2P with DR type. |
| P2P - Beneficiary | Includes all the transactions received as P2P with CR type. |
| P2M - Remitter | Includes all the transactions received as P2M with DR type. |
| P2M - Beneficiary | Includes all the transactions received as P2M with CR type. |

---

*India Unified Payment Interface (UPI) User Guide*
*G44886-01*
*Copyright © 2017, 2025, Oracle and/or its affiliates.*
