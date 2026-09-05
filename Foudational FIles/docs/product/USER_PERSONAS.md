# User Personas

Purpose: Defines the people MediKiosk must serve and their needs; read before making product, workflow, accessibility, or access-control decisions.

## Primary personas

| Persona | Context and need | Product implication |
| --- | --- | --- |
| Patient | Often elderly, rural, low-literacy, non-tech-savvy, or first-time visitor carrying fragmented paper records | Zero-training, icon-driven voice/touch interface; local-language audio; no smartphone requirement |
| Allopathic physician | Works in high-throughput OPD with limited consultation time and needs structured history before consult | Concise, editable, physician-ready draft with HPI, ROS, history, documents, and provenance |
| AYUSH practitioner | Needs deeper Ayurvedic history that is difficult to capture manually during OPD flow | Configured AYUSH workflow for Trividha, Ashtavidha, Dashavidha, and Ahara-Vihara capture; no automated interpretation |
| Triage/nursing staff | Must identify possible emergencies among high patient volume | Visible staff alert for configured red flags, minimum necessary context, acknowledgement/escalation controls |

## Operational/support personas

| Persona | Need | Boundary |
| --- | --- | --- |
| Hospital administrator | Operational configuration, adoption, and governance visibility | No default access to clinical content; access policy/audit applies |
| Healthcare IT/platform team | Secure deployment, integration, availability, and incident response | Operational access by default; no broad clinical-content access |

## Shared design requirements

- Every patient question is answerable through speech or touch.
- The patient can choose from English, Hindi, Bengali, Marathi, Telugu, and Tamil, subject to approved provider/language support.
- The clinician—not the system—owns final review of the clinical draft.
- Triage staff—not the system—own the clinical response to an alert.

→ For detailed flows, see `docs/product/USER_STORIES.md`.

## Open Questions

- Persona research, local-language usability findings, hospital staffing flow, accessibility accommodations, and support-access policy require validation with target users and hospitals.
