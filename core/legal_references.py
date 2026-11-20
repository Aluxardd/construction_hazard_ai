"""Official sources reviewed on 20 November 2026; applicability requires human review."""

REVIEWED = "2026-11-20"

REFERENCES = [
    {
        "id": "ppe-1992-4",
        "title": "Personal Protective Equipment at Work Regulations 1992",
        "section": "Regulation 4",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/1992/2966/regulation/4",
        "summary": "Suitable PPE must be provided for relevant risks unless equally or more effective measures adequately control them.",
        "applicability": "Great Britain; depends on the work, risk, dutyholder and applicable exclusions.",
        "tags": ["ppe"],
    },
    {
        "id": "ppe-1992-10",
        "title": "Personal Protective Equipment at Work Regulations 1992",
        "section": "Regulation 10",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/1992/2966/regulation/10",
        "summary": "Addresses proper use of PPE provided under the regulations.",
        "applicability": "Great Britain; whether PPE was provided under the regulations requires verification.",
        "tags": ["ppe"],
    },
    {
        "id": "ppe-2022-6",
        "title": "Personal Protective Equipment at Work (Amendment) Regulations 2022",
        "section": "Regulation 6",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/2022/8/regulation/6/made",
        "summary": "Amends terminology in regulations 4 to 11 of the 1992 regulations.",
        "applicability": "Great Britain; consult the amended 1992 regulations and confirm worker status.",
        "tags": ["ppe"],
    },
    {
        "id": "hse-ppe-2022",
        "title": "Extended scope of the Personal Protective Equipment at Work Regulations",
        "section": "2022 amendment and hierarchy of controls",
        "source_organisation": "Health and Safety Executive",
        "source_type": "guidance",
        "url": "https://www.hse.gov.uk/ppe/ppe-regulations-2022.htm",
        "summary": "Explains the 2022 amendment, worker scope and the hierarchy of controls.",
        "applicability": "Great Britain; employment status and exclusions require review.",
        "tags": ["ppe"],
    },
    {
        "id": "hse-hierarchy",
        "title": "Using PPE to control risks at work",
        "section": "Managing risk using PPE",
        "source_organisation": "Health and Safety Executive",
        "source_type": "guidance",
        "url": "https://www.hse.gov.uk/ppe/managing-risk-using-ppe.htm",
        "summary": "Consider elimination, substitution, engineering and administrative controls before PPE.",
        "applicability": "Risk assessment guidance, not a finding that a particular control is adequate.",
        "tags": ["ppe"],
    },
    {
        "id": "hse-construction-ppe",
        "title": "Construction personal protective equipment",
        "section": "Head protection, footwear and high-visibility clothing",
        "source_organisation": "Health and Safety Executive",
        "source_type": "guidance",
        "url": "https://www.hse.gov.uk/construction/faq-ppe.htm",
        "summary": "Explains context-dependent head, footwear and high-visibility protection on construction sites.",
        "applicability": "Construction; depends on risks, site rules and applicable exemptions.",
        "tags": ["construction"],
    },
    {
        "id": "hswa-1974-2",
        "title": "Health and Safety at Work etc. Act 1974",
        "section": "Section 2",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/ukpga/1974/37/section/2",
        "summary": "Sets out general employer duties to employees, so far as reasonably practicable.",
        "applicability": "Applicability depends on the employer, worker and circumstances.",
        "tags": ["work"],
    },
    {
        "id": "cdm-2015-15",
        "title": "Construction (Design and Management) Regulations 2015",
        "section": "Regulation 15",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/2015/51/regulation/15",
        "summary": "Sets out contractor duties, including planning and relevant construction phase plan provisions.",
        "applicability": "Construction projects; exact duties depend on contractor roles and circumstances.",
        "tags": ["construction"],
    },
    {
        "id": "height-2005-6",
        "title": "Work at Height Regulations 2005",
        "section": "Regulation 6",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/2005/735/regulation/6",
        "summary": "Addresses avoiding work at height where reasonably practicable and preventing falls.",
        "applicability": "Great Britain; depends on whether work at height and relevant duties apply.",
        "tags": ["height"],
    },
    {
        "id": "coshh-2002-7",
        "title": "Control of Substances Hazardous to Health Regulations 2002",
        "section": "Regulation 7",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/2002/2677/regulation/7",
        "summary": "Addresses prevention or adequate control of exposure to hazardous substances.",
        "applicability": "Great Britain; depends on substances, exposure and regulatory exclusions.",
        "tags": ["substances"],
    },
    {
        "id": "noise-2005-6",
        "title": "Control of Noise at Work Regulations 2005",
        "section": "Regulation 6",
        "source_organisation": "legislation.gov.uk",
        "source_type": "legislation",
        "url": "https://www.legislation.gov.uk/uksi/2005/1643/regulation/6",
        "summary": "Addresses elimination or control of exposure to workplace noise.",
        "applicability": "Great Britain; depends on exposure and applicable action values.",
        "tags": ["noise"],
    },
]


def relevant_references(context):
    """Return possible sources based on user-supplied context, not inferred hazards."""
    if context.get("jurisdiction") != "great_britain":
        return []
    tags = {"ppe", "work"}
    if context.get("activity") == "construction":
        tags.add("construction")
    tags.update(context.get("hazards", []))
    return [
        {**reference, "date_reviewed": REVIEWED, "last_verified": REVIEWED}
        for reference in REFERENCES if tags.intersection(reference["tags"])
    ]
