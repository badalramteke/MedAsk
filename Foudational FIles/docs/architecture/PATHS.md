# MediKiosk — Application Routes & Element Attribute Catalog (`PATHS.md`)

> **Architectural Rule:** Whenever any frontend screen, component, or interactive element is created or modified, it **must** adhere to this route registry and element attribute specification. All new page routes and interactive elements must be registered in this document.

---

## 1. Mandatory Frontend Element Attribute Specification

Every interactive, input, or voice-navigable element in the MediKiosk frontend **MUST** include the following standardized HTML attributes:

| Attribute | Required | Description | Example |
| :--- | :--- | :--- | :--- |
| `data-element` | **Mandatory** | Canonical semantic identifier of the element | `data-element="auth-otp-submit-btn"` |
| `data-voice-action` | **Mandatory for interactive** | Permitted voice command mapping action ID | `data-voice-action="confirm-otp"` |
| `data-testid` | **Mandatory** | Deterministic end-to-end and unit testing selector | `data-testid="auth-otp-submit-btn"` |
| `id` | **Mandatory** | Unique DOM identifier per page | `id="kiosk-auth-otp-submit"` |
| `aria-label` | **Mandatory** | Accessible screen-reader & TTS label (multilingual fallback) | `aria-label="Confirm OTP and Proceed"` |

### Example Component Markup Pattern

```tsx
<button
  id="kiosk-consent-agree-btn"
  data-element="consent-agree-btn"
  data-voice-action="consent-agree"
  data-testid="consent-agree-btn"
  aria-label="I agree to share my health data for clinical consultation"
  className="btn-primary-kiosk"
  onClick={handleConsentAgree}
>
  <span className="icon">✓</span>
  <span className="label">सहमत हैं / Agree</span>
</button>
```

---

## 2. Kiosk Patient-Facing Route Registry

| Route Path | Screen / View Name | Purpose & Flow Description | Key Registered `data-element` Attributes | Voice Triggers (`data-voice-action`) |
| :--- | :--- | :--- | :--- | :--- |
| `/` | **Landing / Attractor Screen** | Welcome screen with visual call-to-action to begin intake | `welcome-start-btn`, `language-quick-select`, `help-audio-btn` | `start-intake`, `help`, `select-language` |
| `/language` | **Language Selection** | Icon & voice-guided language chooser (Hindi, English, Marathi, Bengali, Tamil, Telugu) | `lang-hindi-card`, `lang-english-card`, `lang-marathi-card`, `lang-bengali-card`, `lang-tamil-card`, `lang-telugu-card`, `lang-next-btn` | `choose-hindi`, `choose-english`, `choose-marathi`, `choose-bengali`, `choose-tamil`, `choose-telugu` |
| `/auth` | **Patient Identification** | ABHA ID / Mobile OTP / Aadhaar Scan entry mode | `auth-abha-input`, `auth-otp-input`, `auth-scan-qr-btn`, `auth-skip-guest-btn`, `auth-submit-btn` | `enter-abha`, `scan-card`, `guest-intake`, `submit-auth` |
| `/consent` | **DPDP & ABDM Consent** | Audio-guided granular consent notice with explicit accept/decline | `consent-audio-play-btn`, `consent-purpose-checkbox`, `consent-agree-btn`, `consent-decline-btn` | `play-consent-audio`, `consent-agree`, `consent-decline` |
| `/intake/mode-select` | **Intake Mode Selector** | Choose between General Allopathic OPD and Ayurvedic/AYUSH OPD | `mode-allopathic-card`, `mode-ayush-card`, `mode-proceed-btn` | `select-allopathic`, `select-ayush` |
| `/intake/symptoms` | **Chief Complaint & SOCRATES Engine** | Dual-mode voice & touch dynamic adaptive interview | `mic-record-btn`, `symptom-body-map`, `severity-slider`, `question-next-btn`, `question-prev-btn` | `start-recording`, `stop-recording`, `next-question`, `previous-question` |
| `/intake/ayush` | **Dashavidha Pariksha Module** | Specialized Ayurvedic evaluation (Prakriti, Vikriti, Agni, Ahara-Vihara) | `prakriti-selector`, `agni-status-card`, `koshtha-selector`, `ayush-submit-btn` | `select-vata`, `select-pitta`, `select-kapha`, `submit-ayush` |
| `/documents/scan` | **Document Scanner / Upload** | Physical prescription & lab report camera/scanner feed | `doc-camera-capture-btn`, `doc-file-upload-input`, `doc-type-presc-btn`, `doc-type-lab-btn`, `doc-process-btn` | `take-photo`, `upload-file`, `select-prescription`, `select-lab-report`, `process-document` |
| `/documents/timeline` | **Digitized Records Review** | OCR output preview, extracted values & chronological timeline | `timeline-item-card`, `lab-abnormal-badge`, `ocr-correction-btn`, `timeline-confirm-btn` | `confirm-documents`, `edit-ocr-record` |
| `/summary` | **Patient Confirmation & Summary** | Audio confirmation of captured history in local tongue | `summary-audio-playback-btn`, `summary-confirm-final-btn`, `summary-edit-section-btn` | `listen-summary`, `confirm-summary`, `edit-summary` |
| `/triage/alert` | **Emergency Red-Flag Bypass** | Priority triage alert overlay with immediate staff guidance | `triage-staff-ack-btn`, `triage-sos-call-btn`, `triage-exit-btn` | `call-nurse`, `triage-acknowledge` |
| `/complete` | **Intake Complete & Token** | Final queue token display, session termination countdown | `token-print-btn`, `session-exit-btn` | `print-token`, `finish-session` |

---

## 3. Clinician & Staff Route Registry

| Route Path | Screen / View Name | Purpose & Flow Description | Key Registered `data-element` Attributes |
| :--- | :--- | :--- | :--- |
| `/doctor/queue` | **OPD Patient Queue** | Clinician view of waiting patients with completed intake summaries | `patient-queue-table`, `queue-filter-select`, `open-summary-btn` |
| `/doctor/summary/[patientId]` | **Physician Review & Edit Draft** | Interactive clinical summary editor (HPI, ROS, OCR timeline, AYUSH metrics) | `clinician-hpi-edit-area`, `clinician-accept-btn`, `clinician-amend-btn`, `clinician-push-his-btn` |
| `/nurse/triage-dashboard` | **Triage & Red-Flag Monitor** | Live alerts dashboard showing patients flagged with red-flag symptoms | `red-flag-alert-card`, `emergency-action-btn`, `triage-priority-badge` |
| `/admin/status` | **Kiosk Health & Hardware Monitor** | Device status, ASR latency, OCR queue depth, ABDM sandbox connectivity | `status-mic-health`, `status-camera-health`, `status-abdm-gateway` |

---

## 4. Maintenance Guidelines
1. Any developer or AI agent adding a new page or route **must** add an entry to this table before or immediately upon creating the route file.
2. Every interactive button, input, toggle, and card **must** carry valid `data-element`, `data-voice-action`, `data-testid`, and `id` tags matching this schema.
