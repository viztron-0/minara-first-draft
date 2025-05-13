# Minara Backend MVP - Known Issues

This document lists the known issues and limitations for the current MVP of the Minara backend.

1.  **Community Creation (Critical):**
    *   **Symptom:** Attempting to create a new community via `POST /api/personal/communities/` results in a 500 Internal Server Error.
    *   **Impact:** This prevents the creation of new communities, which is a core part of the "Communities Function".
    *   **Status:** Needs urgent investigation and fixing.

2.  **Personal Profile Update (Minor/Uncertain):**
    *   **Symptom:** The API test script reported a failure when attempting to update the personal profile via `PUT /api/users/personal-profile/`. The exact nature of the failure (e.g., 4xx error, 500 error, or incorrect data update) needs to be re-verified from the test script output details.
    *   **Impact:** Users may not be able to update their personal profile information (full name, bio).
    *   **Status:** Needs re-verification and potential fix.

3.  **User ID Format in API Responses (Inconsistency):**
    *   **Symptom:** The `user` field in some API responses (e.g., when fetching a personal profile) returns a direct integer user ID, while in other related serializers or contexts, it might be a nested user object (e.g., `{"id": 1, "email": "..."}`).
    *   **Impact:** Client applications need to be aware of this and handle both formats or the backend needs to be standardized.
    *   **Status:** Documented. Standardization would be a future improvement.

4.  **Limited Test Coverage:**
    *   **Symptom:** Only a basic API test script (`api_test_script.py`) was used for validation. No comprehensive unit or integration tests exist.
    *   **Impact:** Potential for undiscovered bugs and regressions.
    *   **Status:** Test coverage should be significantly increased for a production application.

5.  **Scalability & Production Readiness:**
    *   **Symptom:** Uses SQLite, Django development server settings (`DEBUG=True`).
    *   **Impact:** Not suitable for production deployment due to performance, security, and scalability limitations.
    *   **Status:** Standard production deployment practices (PostgreSQL, Gunicorn/Daphne, `DEBUG=False`, etc.) are required before going live.

6.  **Security Hardening:**
    *   **Symptom:** Basic security measures are in place (Django/DRF defaults). Advanced security features like rate limiting, comprehensive input sanitization, and detailed permission checks for all edge cases are not fully implemented.
    *   **Impact:** Potential vulnerabilities if deployed to a hostile environment.
    *   **Status:** Requires a thorough security review and hardening for production.

7.  **Incomplete Feature Aspects:**
    *   **Communities - Location/Age/Gender Sorting:** The detailed hierarchical location-based community structure with age/gender specifics is not implemented in the API logic for community creation or filtering. Models might need extension.
    *   **Chat - Call Functionality:** Backend support for actual voice/video calls is not implemented (only text-based chat rooms).
    *   **Home Page (Instagram-like) - Relevant Content:** The personal feed currently only shows posts from followed users. The "relevant content" (algorithmic suggestions) part is not implemented.
    *   **Professional - LinkedIn Import:** Functionality to import a LinkedIn profile is not implemented.
    *   **Professional - News Segment:** The news segment on the professional home page is not implemented.
    *   **Professional - Content Sorting:** Advanced content sorting on the professional feed (religious, educational by topic) is not implemented.

This list should be used as a reference for future development and bug fixing efforts.

