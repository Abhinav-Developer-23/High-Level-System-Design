"""
The sample circulars: what OCR + Claude extraction would hand to the ingest step.

[Real] Textract reads the PDF (text, tables, layout); Claude splits it into clauses and fills the
metadata (products, rule_key, effective_from); a human checks every NEW rule_key before it's used.

Each clause is a tuple: (clause_path, page, text, rule_key). rule_key is set when the clause states a
looked-up rule (a limit, a window, a list); None for everything else. Two clauses with the same rule_key
compete, and nodes.latest_wins decides which one is in force on a given date.

The UPI Lite circulars OC-L1 / OC-L2 and their dates are SYNTHETIC placeholders for the ₹500 -> ₹1,000
example. OC-229 is reconstructed from what OC-229A says about it. The other four are excerpts of the
real circulars.
"""

# Product codes (what is stored) -> names (what the user sees).
PRODUCTS = {
    "UPI_LITE": "UPI Lite",
    "TAP_AND_PAY": "UPI Tap & Pay",
    "NRI_INTL_MOBILE": "NRI / international mobile numbers",
    "URCS_GST": "URCS back-office GST / ISD",
    "DISPUTES_MCC": "MCC misclassification disputes",
}

# Rule parameter codes (the part of rule_key after the product) -> readable names for answers.
LABELS = {"per_txn_limit": "per transaction limit", "min_claim_amount": "minimum claim amount",
          "response_days": "response time", "isd_section": "ISD sections",
          "isd_update_window": "ISD update window", "permitted_country": "permitted countries"}

NPCI = "https://www.npci.org.in/uploads/"

CIRCULARS = [
    {   # SYNTHETIC placeholder: the older UPI Lite limit
        "id": "OC-L1", "subject": "UPI Lite: transaction limits", "issue_date": "2023-10-01",
        "effective_from": "2023-10-01", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Guidelines > 3", 1, "The per transaction limit for UPI Lite shall be ₹500.", "UPI_LITE.per_txn_limit"),
            ("Guidelines > 4", 1, "UPI Lite payments up to the per transaction limit shall not require UPI PIN.",
             None),
        ],
    },
    {   # SYNTHETIC placeholder: issued 2 Dec, effective 16 Dec -> issue date != effective date.
        # Same rule_key as OC-L1's clause 3: these two compete, and latest_wins picks one.
        "id": "OC-L2", "subject": "UPI Lite: enhancement of per transaction limit", "issue_date": "2024-12-02",
        "effective_from": "2024-12-16", "products": ["UPI_LITE"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "With reference to circular OC-L1, the UPI Lite per transaction limit is revised.", None),
            ("Guidelines > 2(a)", 1, "The per transaction limit for UPI Lite is enhanced from ₹500 to ₹1,000, "
                                     "effective 16 December 2024.", "UPI_LITE.per_txn_limit"),
        ],
    },
    {
        "id": "UPI-OC-186A-2026-27", "subject": "Enhancement - UPI Tap & Pay on Point of Sale (PoS)",
        "issue_date": "2026-09-10", "effective_from": "2026-09-10", "products": ["TAP_AND_PAY"],
        "pdf_url": NPCI + "UPI_I_OC_No_186_A_I_Enhancement_UPI_Tap_and_Pay_on_Point_of_Sale_Po_S_e695625b85.pdf",
        "clauses": [
            ("Main", 1, "With reference to UPI Operating Circular NPCI/UPI/OC-186/2023-24 dated 19th December 2023, "
                        "UPI Tap & Pay through NFC on QR was introduced. UPI Tap & Pay shall now be extended to "
                        "Point of Sale (PoS) terminals.", None),
            ("Key Guidelines > 1", 1, "Members and UPI Application Providers shall ensure that UPI Tap & Pay "
                                      "transactions on PoS terminals are accepted only for Person-to-Merchant (P2M) "
                                      "transactions.", None),
            # a new SCOPE (PoS) gets its own rule key, so it never competes with the QR rules
            ("Key Guidelines > 3", 1, "Members and UPI Application Providers shall ensure that per transaction limit "
                                      "is capped at ₹5000, up to which additional factor of authentication shall "
                                      "not be required.", "TAP_AND_PAY.per_txn_limit.PoS"),
            ("UPI Application Provider > 2", 2, "UPI Application Providers shall ensure that device lock is enabled "
                                                "as a prerequisite for activating UPI Tap & Pay. The device shall be "
                                                "in an unlocked state at the time of initiating a transaction.", None),
        ],
    },
    {   # RECONSTRUCTED from OC-229A's own summary of it (we don't have the OC-229 PDF)
        "id": "UPI-OC-229-2025-26", "subject": "ISD/GSTIN option in URCS (reconstructed)",
        "issue_date": "2025-11-12", "effective_from": "2025-11-17", "products": ["URCS_GST"], "pdf_url": None,
        "clauses": [
            ("Main", 1, "The Input Service Distributor (ISD)/GSTIN option would be enabled in the URCS system for "
                        "both payable and receivable sections.", "URCS_GST.isd_section"),
        ],
    },
    {
        "id": "UPI-OC-229A-2026-27", "subject": "Implementation of Revised ISD-GSTIN Option in URCS Back-Office System",
        "issue_date": "2026-08-24", "effective_from": "2026-09-15", "products": ["URCS_GST"],
        "pdf_url": NPCI + "UPI_OC_229_A_ISD_GSTIN_Input_Service_Distributor_Option_in_UPI_URCS_898c087730.pdf",
        "clauses": [
            ("Main > a", 1, "The receivable section has been removed from the ISD functionality. Users will now be "
                            "able to update ISD details only for the payable section.", "URCS_GST.isd_section"),
            ("Main > c", 1, "Users are permitted to update only one GSTIN or ISD per product per bank in a month.",
             None),
            ("Main > d", 1, "ISD/GSTIN update should be submitted in URCS between the 15th and 31st or last day of "
                            "every month. Back Office system will not permit users to update ISD/GSTIN details "
                            "between the 1st to 14th of every month.", "URCS_GST.isd_update_window"),
            ("Go-Live", 1, "Revised ISD-GSTIN functionality will be made live on Sep 15, 2026.", None),
        ],
    },
    {
        "id": "UPI-OC-239-2026-27", "subject": "UPI - Process for Resolution of MCC Misclassification related disputes",
        "issue_date": "2026-10-14", "effective_from": "2026-10-14", "products": ["DISPUTES_MCC"],
        "pdf_url": NPCI + "UPI_OC_239_UPI_Process_for_Resolution_of_MCC_Misclassification_related_disputes_"
                          "7770320097.pdf",
        "clauses": [
            ("2.3 Claim Eligibility > a(i)", 5, "Amount Threshold for a Claim: Minimum aggregate Claim amount must "
                                                "be INR 10,00,000 (Ten Lakhs rupees only).",
             "DISPUTES_MCC.min_claim_amount"),
            ("4.2 Pre-Compliance Response > a", 8, "Responding Party must submit response in 23 calendar days. On "
                                                   "expiry of 23rd day, if no response is received, responding party "
                                                   "will have a period of 7 calendar days as grace period.",
             "DISPUTES_MCC.response_days"),
            ("4.4 Panel for Resolution of Disputes > b", 10, "Panel shall endeavor to review the Claim and resolve "
                                                             "the same within 90 calendar days from Panel Reference "
                                                             "Date.", None),
        ],
    },
    {
        "id": "UPI-OC-161A-2026-27", "subject": "Addition of New Countries to the List of Permitted International "
                                               "Mobile Numbers in UPI",
        "issue_date": "2026-10-01", "effective_from": "2026-10-01", "products": ["NRI_INTL_MOBILE"],
        "pdf_url": NPCI + "UPI_OC_161_A_Digital_cc63c6c44f.pdf",
        "clauses": [
            ("Main", 1, "With reference to NPCI/UPI/OC-161/2022-23, international mobile numbers of 12 countries "
                        "were permitted. Now, international mobile numbers from the following 19 countries are being "
                        "added: Bahrain, Bhutan, Brazil, Germany, Greece, Ireland, Italy, Japan, Kuwait, Maldives, "
                        "Nepal, Netherlands, New Zealand, Philippines, Portugal, South Africa, Spain, Sweden, "
                        "Thailand. All compliance requirements shall remain as is.", "NRI_INTL_MOBILE.permitted_country"),
        ],
    },
]
