## Future Features & Ideas

Ideas listed here are NOT in current scope. They exist so the architecture is built to accommodate them later without requiring a rewrite. Do not implement anything here unless explicitly moved to PRD.md and approved.

### Idea Template

#### [Feature Name]

- What it does:
- Why it matters:
- Rough module it would plug into:
- Status: Idea / Considered / Approved for next phase

---

#### Voice UI Navigation

- What it does: Lets a patient navigate permitted kiosk pages and controls by voice, such as opening consent, language, document-upload, or intake sections.
- Why it matters: Improves zero-training accessibility for elderly, low-literacy, and hands-busy users while preserving touch as a fallback.
- Rough module it would plug into: A new frontend accessibility/navigation plugin. It should map recognized commands to an allow-listed `data-voice-action` identifier on approved UI controls; it must not execute arbitrary script or use patient voice as a direct DOM selector.
- Status: Idea

---

(Ideas will be added here by the team over time)
