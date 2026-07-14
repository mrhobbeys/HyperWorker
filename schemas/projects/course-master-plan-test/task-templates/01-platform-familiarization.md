---
id: T-001
kind: task
schema: course-master-plan-test
phase: A
phase_step: 2
risk_level: standard
required_tools: [browser_navigate, browser_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Browser pick captured: operator selected the admin-pre-authenticated browser before the first navigation. Selection recorded as a finding."
  - "Platform admin nav walked at section level (Classroom, Calendar, Members, Leaderboards, About, Settings — adjust per platform)."
  - "<platform>-site-guide.md created at <project root>/<platform>-site-guide.md with the canonical sections: Quick Start, Site Overview, Navigation Map, URL Reference, Key Workflows, Form Field Catalog, Status Taxonomy, Naming Conventions, Interaction Patterns & Gotchas, Verification Signatures, Site Intelligence."
  - "No actuation occurred — only read-only navigation. (Operator-confirmed; no platform state changed during T-001.)"
  - "Guide hash recorded; downstream L2 actuation tasks consume by [SITE-GUIDE#hash]-equivalent citation."
---

# Task T-001: Platform Familiarization

## Objective

Walk the platform's admin nav once, document it, and produce `<project root>/<platform>-site-guide.md` — a one-time-per-cycle artifact that L2 actuation tasks consume by hash. Read-only walk; no actuation.

## Step-by-Step Instructions

1. Read OR-001. Note `platform`, `course_url`, `admin_user`, `platform_actuation.browser_codename`, `platform_actuation.guide_path`.

2. **Operator browser pick.** If multiple paired browser-automation agents are available (e.g., a work profile + a personal profile, or separate Claude-in-Chrome-equivalent instances), surface the list and ask operator to select. Record the selection as a Finding artifact (`F-NNN: browser-selected: <codename>`) so future tasks reference the same browser.

3. **Navigate to the platform admin URL** as the admin user (operator pre-authenticated). Confirm the platform recognizes admin-level access (e.g., a Settings link visible that members don't see).

4. **Walk the primary nav.** For each top-level section, navigate, observe, and note:
   - URL pattern (template form, e.g., `/community/<slug>/classroom/<module-slug>`).
   - Page-level controls visible at admin (create / edit / delete / publish).
   - Admin-only vs. member-visible sections.

5. **Document module-creation flow.** Navigate to wherever a new module/lesson/section is created. Note every form field, every dropdown, every implicit default. Take screenshots / read the page DOM at section level. Do NOT submit any forms.

6. **Document tier-gate UI.** How does the platform express free vs. paid (or open vs. gated)? Is it a per-module flag? A per-classroom setting? A subscription tier definition? Document the actual UI mechanism, not assumptions.

7. **Document asset upload.** For each asset type the platform supports (image, video, audio, attachment), document the upload flow — entry point, supported formats, max sizes if visible, post-upload state.

8. **Document member-view differences.** Navigate as the test_member account if available (per OR-001.test_member; null acceptable). Note differences between admin and member views.

9. **Document URL patterns + any non-obvious naming conventions** the platform uses (slug rules, URL collision behavior, automatic redirects).

10. **Write `<platform>-site-guide.md`** at `<project root>/<platform>-site-guide.md` with these canonical sections:
    - Quick Start
    - Site Overview
    - Navigation Map
    - URL Reference
    - Key Workflows (module create, tier gate, asset upload, member-view diff)
    - Form Field Catalog
    - Status Taxonomy (what statuses exist for modules, lessons, members, etc.)
    - Naming Conventions
    - Interaction Patterns & Gotchas (what surprised you; what's idiosyncratic about this platform)
    - Verification Signatures (how to confirm an action landed — what to read-back)
    - Site Intelligence (anything else worth recording for future L2 actuation tasks)

11. **Compute the guide's SHA-256.** Record it as a finding (`F-NNN: site-guide-hash: <sha256-12-hex>`) so L2 actuation tasks cite the guide by hash.

12. **No actuation pledge.** Confirm in the completion report that no platform state was changed during T-001.

13. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Browser selected:** <codename> (recorded as F-NNN)
- **Pages walked:** <list of section names + URLs>
- **Site guide produced:** `<project root>/<platform>-site-guide.md` (hash: <sha256-12>)
- **Tier-gate UI mechanism:** <brief — per-module flag / classroom setting / subscription tier / other>
- **Asset upload entry points:** <list>
- **Member-view differences observed:** <brief; null if no test_member account>
- **Surprises / gotchas:** <bullet list — feed these into Friction log if they imply harness-level patches>
- **No actuation:** confirmed (no platform state changed during T-001)
- **Recommended follow-up:** "L2 actuation tasks should cite [F-NNN: site-guide-hash#hash] as a consumed input."
