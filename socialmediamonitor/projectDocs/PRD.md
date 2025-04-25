Product Requirements Document (PRD - YouTube-Only MVP)
Version: 1.0
Date: April 21, 2025
Status: Draft
Author/Owner: [Your Name/Team Lead]
Stakeholders: [List relevant stakeholders, e.g., Engineering Lead, Design Lead, CEO/Founder]
1. Introduction
1.1. Problem: Parents are increasingly concerned about the content their children consume and the creators they follow on YouTube. It's difficult for parents to stay informed about potential exposure to harmful ideologies, dangerous trends, explicit content, or other risks propagated through subscribed channels, especially given the sheer volume of content. Existing parental controls often focus on screen time or broad category blocking, lacking insight into specific channel risks.
1.2. Vision: To empower parents with clear, actionable insights into their children's online environment, starting with YouTube, fostering safer online experiences and facilitating open family communication about digital citizenship.
1.3. Solution (MVP): GuardianLens MVP is a web and mobile (Flutter-based) application that allows parents, with their child's informed consent, to link their child's YouTube account. The service analyzes the public text metadata (channel descriptions, recent public video titles/descriptions) of channels the child subscribes to, flags channels associated with predefined risk categories (e.g., hate speech, self-harm content), and presents these findings with context on a simple, intuitive dashboard for the parent.
1.4. Scope (MVP): YouTube Only. Focus on analyzing subscribed channel metadata (text only). Core deliverable is the parent dashboard. Real-time alerts and analysis of other platforms are out of scope for MVP.
2. Goals
2.1. User Goals:
Provide parents with awareness of potentially harmful YouTube channels their child subscribes to.
Offer clear, contextual information about why a channel was flagged.
Enable parents to easily review findings and access flagged channels for their own assessment.
Build trust through transparent consent processes and clear communication about data usage.
2.2. Business Goals:
Successfully launch a stable and valuable MVP focused on YouTube within the target timeframe.
Validate the core value proposition with early adopters.
Achieve target user activation and retention rates for the MVP cohort.
Establish a foundation for future platform expansion and feature enhancements.
Secure necessary YouTube API Quota increase for service viability.
3. Target Audience
3.1. Primary Persona: Concerned Parent/Guardian
Demographics: Parents/guardians of children/teens (primarily focusing on ages ~8-17) who actively use YouTube. Likely digitally literate but may not be deeply technical. Resides in the initial target market (e.g., USA, considering Arizona specifics).
Needs/Pains: Worried about hidden risks online (radicalization, dangerous trends, mental health impacts, explicit content). Feels overwhelmed trying to monitor manually. Wants peace of mind and tools to facilitate safety conversations. Values privacy but seeks awareness.
Motivations: Proactively protect their child, stay informed, build trust through communication.
3.2. Secondary Persona: Child/Teenager User
Role: Primarily involved during the consent/account linking process.
Needs: Understand what the app does and what data it accesses. Feel respected and not spied upon. Easy, standard login/consent flow (Google Sign-In).
4. Use Cases & User Stories
4.1. Parent Onboarding & Setup:
As a new parent user, I want to easily create an account for GuardianLens.
As a parent, I want to create a profile for my child within the app.
As a parent, I want clear instructions on how to link my child's YouTube account, including guidance on involving my child in the consent process.
As a parent, I want to understand exactly what data GuardianLens will access before initiating the linking process.
4.2. Child Consent & Account Linking (YouTube):
As a parent, I want to initiate the YouTube linking process for my child's profile.
As a child (with parental guidance), I want to log in securely using my Google account when prompted.
As a child, I want the Google consent screen to clearly show that GuardianLens is requesting read-only access to my subscriptions and public channel/video info.
As a parent, I want confirmation once the YouTube account is successfully linked.
4.3. Reviewing the Dashboard:
As a parent, I want to log in and see a dashboard summarizing the status for my child's linked YouTube account.
As a parent, I want to quickly see if any new potentially harmful channels have been flagged since my last visit.
As a parent, I want to view a list of all channels my child subscribes to.
As a parent, I want channels flagged for potential risks to be clearly highlighted.
As a parent, I want to be able to sort or filter the list of subscribed channels (e.g., by flag status, subscriber count).
4.4. Investigating Flagged Channels:
As a parent, I want to click on a flagged channel to see more details.
As a parent, viewing details, I want to see the channel name, thumbnail, subscriber count, the reason(s) it was flagged (risk category), and potentially the text snippet that triggered the flag.
As a parent, viewing details, I want a direct link to easily visit the channel on YouTube for my own review.
4.5. Providing Feedback:
As a parent, if I review a flagged channel and believe it's safe, I want to easily mark it as "Not Harmful".
As a parent, I expect marking a channel as "Not Harmful" to hide it from my primary flagged list and provide feedback to the GuardianLens team.
4.6. Managing Accounts:
As a parent, I want to easily unlink my child's YouTube account from GuardianLens at any time.
As a parent, I want to manage my own account settings (e.g., password, email).
5. Features & Requirements (MVP - YouTube Only)
5.1. Parent Account Management:
REQ-P01: Ability for parents to register using Email/Password.
REQ-P02: Secure parent login with password reset functionality.
REQ-P03: Ability for parents to manage their account settings.
REQ-P04: Ability for parents to delete their GuardianLens account.
5.2. Child Profile Management:
REQ-C01: Ability for parents to add one or more child profiles (internal identifier/name, age).
REQ-C02: Ability for parents to edit/remove child profiles.
5.3. YouTube Account Linking & Consent:
REQ-L01: Initiate linking flow for a specific child profile and YouTube.
REQ-L02: Provide clear, age-appropriate explanations (for parent & child viewing) about the process, data accessed (subscriptions, public channel/video metadata - read-only), and purpose before redirecting to Google OAuth.
REQ-L03: Use Google OAuth 2.0 flow requesting only the youtube.readonly scope.
REQ-L04: Securely handle and store OAuth tokens upon successful authorization.
REQ-L05: Display confirmation of successful linking on the dashboard.
REQ-L06: Implement robust handling for OAuth errors or consent denial.
REQ-L07: Implement Verifiable Parental Consent mechanism for children under 13 (as per COPPA).
REQ-L08: Ensure child consent/login (via Google) is part of the flow for users 13+.
REQ-L09: Ability for parents to unlink a YouTube account, triggering token revocation/deletion and stopping monitoring.
5.4. Data Fetching & Processing (Backend):
REQ-D01: Perform a daily background scan for each linked YouTube account.
REQ-D02: Fetch the list of subscribed channel IDs using the YouTube Data API.
REQ-D03: For each subscribed channel, fetch public metadata: channel snippet (title, desc), statistics (sub count), topic details.
REQ-D04: For each subscribed channel, fetch public metadata for the 10 most recent videos: video snippet (title, desc).
REQ-D05: Implement aggressive caching for fetched channel/video metadata to optimize API quota usage.
REQ-D06: Handle YouTube API errors, rate limits, and quota issues gracefully (log errors, potentially notify parent of scan issues).
5.5. Risk Analysis Engine (Backend):
REQ-A01: Analyze fetched text data (channel title/desc, recent video titles/desc) using keyword/pattern matching.
REQ-A02: Maintain internal, updatable lists defining keywords/patterns for MVP risk categories (Hate Speech, Self-Harm, Violence, Explicit, Bullying, Dangerous Challenges, Misinformation). Include YouTube-specific terms.
REQ-A03: Assign flags/categories to channels based on matches found. Store results.
REQ-A04: Analysis is text-only; no image/video/audio/transcript analysis.
5.6. Parent Dashboard (Web & Mobile UI - Flutter):
REQ-UI01: Display overview of linked child profiles and their linked YouTube accounts.
REQ-UI02: Prominently display summary of scan status and newly flagged channels since last review.
REQ-UI03: List all subscribed channels for a selected child account.
REQ-UI04: Clearly indicate flagged channels using visual cues (icons, badges).
REQ-UI05: Display channel thumbnail and name for each subscribed channel.
REQ-UI06: Allow sorting/filtering of the subscribed channel list (by name, flag status, subscriber count).
REQ-UI07: Provide a detail view upon clicking a channel (flagged or unflagged).
REQ-UI08: Detail view must show: Channel Name, Thumbnail, Subscriber Count, Risk Category(ies) if flagged, Direct Link to YouTube Channel.
REQ-UI09: Detail view should attempt to show the text snippet(s) that triggered the flag (requires careful implementation for clarity/context).
REQ-UI10: Implement the "Mark as Not Harmful" feedback button on the detail view for flagged channels.
5.7. Notifications (MVP):
REQ-N01: Provide an optional setting for parents to receive a notification (e.g., daily email, simple in-app push) when a scan is complete and new high-priority risks are found.
REQ-N02: No real-time alerting per flag in MVP.
5.8. Parent Onboarding & Support:
REQ-H01: Include an initial onboarding tour explaining the app's purpose, features, and limitations.
REQ-H02: Provide context help (tooltips, info icons) within the dashboard.
REQ-H03: Include an FAQ section addressing common concerns (accuracy, privacy, data).
REQ-H04: Offer links to external online safety resources and basic guidance on starting conversations.
6. Design & UX Requirements
6.1. Principles: Clean, simple, intuitive, reassuring, trustworthy, non-alarmist.
6.2. UI/UX:
Design should be responsive (Flutter web/mobile).
Prioritize clarity of information, especially around flagged content.
Consent flows must be transparent and easy to understand.
Onboarding should build confidence and set correct expectations.
Visual design should feel professional and secure.
6.3. Deliverables: Wireframes, high-fidelity mockups, interactive prototypes (to be created by the design team based on this PRD).
7. Release Criteria (MVP)
All MVP features (Section 5) are implemented, tested (unit, integration, E2E) according to the [Comprehensive Testing Plan](../documentation/development-progress.md#comprehensive-testing-plan), and meet quality standards.
YouTube account linking via OAuth is functional and reliable.
Data fetching and analysis pipeline operates correctly on a daily schedule.
Parent dashboard displays subscribed channels and flags accurately.
YouTube API quota management (caching, optimization) is implemented, and status of quota increase request is known/mitigation plan exists.
Compliance requirements (COPPA VPC, Consent flows, Privacy Policy) are implemented and reviewed by legal counsel (including AZ specifics).
Security testing (internal review, potentially external scan) completed.
Performance meets defined NFR targets under simulated load.
Key accessibility standards (WCAG AA where applicable) are considered.
Successful closed beta testing phase completed with feedback incorporated.
Parent onboarding and support documentation are ready.
8. Success Metrics (Post-Launch)
Activation: % of registered parents who successfully link a child's YouTube account.
Engagement: % of active users logging in weekly/monthly; % of users clicking into flagged channel details; Usage rate of "Mark as Not Harmful" button.
Retention: Weekly/Monthly user retention rates.
API Usage: Monitor YouTube API quota consumption vs. limits; Success rate of daily scans.
Qualitative Feedback: User surveys, support tickets, beta feedback analysis.
Technical Performance: Dashboard load times, API response times, error rates.
9. Future Considerations (Post-MVP)
Support for additional platforms (Instagram, TikTok, etc. - requires significant R&D).
Real-time/more frequent alerting.
Deeper analysis (Image/Video, LLM for nuance, sentiment, trends).
Analysis of child's own public content.
Enhanced reporting and summaries.
Parent customization options.
Child-facing transparency/educational features.
B2B versions (schools, therapists).
10. Open Issues & Questions
Critical Dependency: Confirmation of YouTube Data API quota increase or successful implementation of mitigation strategies to operate within existing/lower limits. Project viability hinges on this.
Legal Review: Completion of AZ-specific and general legal review for compliance.
Keyword List Refinement: Ongoing effort required to build and maintain effective keyword/pattern lists for analysis.
Flagged Snippet Display: Technical feasibility and UX design for reliably showing the correct triggering text snippet needs confirmation during implementation.

