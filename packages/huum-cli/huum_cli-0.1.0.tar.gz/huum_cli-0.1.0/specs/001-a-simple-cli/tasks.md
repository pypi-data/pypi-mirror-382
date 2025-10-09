# Tasks: Huum Sauna CLI Manager

**Input**: Design documents from `/specs/001-a-simple-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not included - no TDD approach requested in specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Exact file paths included in descriptions

## Path Conventions
- Single project structure: `src/huum_cli/`, `tests/` at repository root
- Package manager: uv
- Language: Python 3.11+

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] **T001** Initialize uv project structure with `uv init` in repository root
- [x] **T002** Create `pyproject.toml` with project metadata, dependencies (typer, httpx, keyring, tenacity, pydantic, rich), dev dependencies (pytest, pytest-mock, mypy, ruff), and entry point `huum = "huum_cli.cli:app"`
- [x] **T003** [P] Create directory structure: `src/huum_cli/{api,commands,utils}/` with `__init__.py` files
- [x] **T004** [P] Create test directory structure: `tests/{unit,integration,fixtures}/` with `__init__.py` files
- [x] **T005** [P] Create `.gitignore` for Python (venv, __pycache__, *.pyc, .pytest_cache, .mypy_cache, .ruff_cache)
- [x] **T006** [P] Install dependencies with `uv add typer httpx keyring tenacity pydantic rich`
- [x] **T007** [P] Install dev dependencies with `uv add --dev pytest pytest-mock mypy ruff`

**Checkpoint**: Project structure created, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] **T008** [P] Create Pydantic models for `SaunaDevice` in `src/huum_cli/api/models.py` with validation (device_id, name, online, current_temperature, target_temperature, heating_state, session_active, last_updated)
- [x] **T009** [P] Create Pydantic model for `AuthCredentials` in `src/huum_cli/api/models.py` (session, user_id, email, created_at)
- [x] **T010** [P] Create Pydantic model for `Session` in `src/huum_cli/api/models.py` (session_id, device_id, start_time, end_time, target_temperature, state, duration_minutes)
- [x] **T011** Implement credential storage functions in `src/huum_cli/utils/storage.py`: `store_credentials()`, `get_credentials()`, `delete_credentials()` using keyring library with service name "huum-cli"
- [x] **T012** Implement session validation helper in `src/huum_cli/utils/storage.py`: `should_validate_session()` to check if session is older than 24 hours
- [x] **T013** Create `HuumAPIClient` class in `src/huum_cli/api/client.py` with base URL `https://sauna.huum.eu`, `__init__()` accepting session_token, `_request()` helper method for POST requests with session in body, and retry logic using tenacity
- [x] **T014** Implement custom exception classes in `src/huum_cli/api/client.py`: `AuthenticationError`, `APIError`, `DeviceOfflineError`, `SessionAlreadyActiveError`
- [x] **T015** Create Typer app instance in `src/huum_cli/cli.py` with global options (--format for json/human output, --verbose for debug)
- [x] **T016** [P] Create base output formatters in `src/huum_cli/utils/formatters.py`: `format_json()` for JSON output, `format_error()` for error messages

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 6 - Initial Authentication Setup (Priority: P1) 🎯 MVP Prerequisite

**Goal**: Enable users to authenticate with Huum account and store session securely

**Independent Test**: Run `huum auth` with valid credentials, verify session stored in keyring, verify subsequent commands can access API

### Implementation for User Story 6

- [x] **T017** [US6] Implement `authenticate()` function in `src/huum_cli/api/client.py` that POSTs to `/action/login` with username/password, returns session token, user_id, and email
- [x] **T018** [US6] Implement `validate_session()` method in `src/huum_cli/api/client.py` that POSTs to `/action/loginwithsession` to check session validity
- [x] **T019** [US6] Create `auth` command in `src/huum_cli/commands/auth.py` with options --username, --password, --interactive (default), using Typer prompts for interactive mode with hidden password input
- [x] **T020** [US6] Implement authentication flow in `auth` command: call `authenticate()`, store credentials via `store_credentials()`, verify by calling `validate_session()`, display success message with device count
- [x] **T021** [US6] Add error handling for authentication failures (401 → invalid credentials, network errors, keyring unavailable) with user-friendly messages and correct exit codes
- [x] **T022** [US6] Register `auth` command in `src/huum_cli/cli.py` Typer app
- [x] **T023** [US6] Implement `logout` command in `src/huum_cli/commands/auth.py` with --force flag, confirmation prompt, calling `delete_credentials()`
- [x] **T024** [US6] Register `logout` command in `src/huum_cli/cli.py` Typer app

**Checkpoint**: At this point, users can authenticate and subsequent commands have access to Huum API

---

## Phase 4: User Story 1 - Start Sauna Session (Priority: P1) 🎯 MVP Core

**Goal**: Enable users to start sauna heating from command line

**Independent Test**: Run `huum start --temperature 85`, verify sauna begins heating via status check or Huum mobile app

### Implementation for User Story 1

- [x] **T025** [US1] Implement `get_status()` method in `src/huum_cli/api/client.py` that POSTs to `/action/status`, parses response, maps to list of `SaunaDevice` entities
- [x] **T026** [US1] Implement `start_session()` method in `src/huum_cli/api/client.py` that POSTs to `/action/start` with device_id, target_temperature, duration (default 90 minutes)
- [x] **T027** [US1] Implement temperature validation function in `src/huum_cli/utils/validators.py`: `validate_temperature()` checking 40-110°C range
- [x] **T028** [US1] Create `start` command in `src/huum_cli/commands/start.py` with argument device_id (optional), option --temperature/-t (default 85°C)
- [x] **T029** [US1] Implement device auto-selection logic in `start` command: if no device_id and single device exists, auto-select; if multiple devices, error with message to specify device
- [x] **T030** [US1] Implement start flow: get credentials → validate temperature → get devices → select device → call `start_session()` → display confirmation with estimated time
- [x] **T031** [US1] Add error handling for start command: not authenticated (exit 1), device not found (exit 1), device offline (exit 2), session already active (exit 1), invalid temperature (exit 1), API errors (exit 2)
- [x] **T032** [US1] Create human-readable output formatter `format_start_success()` in `src/huum_cli/utils/formatters.py` showing device name, target/current temps, estimated time with Rich formatting
- [x] **T033** [US1] Register `start` command in `src/huum_cli/cli.py` Typer app

**Checkpoint**: At this point, User Story 1 (auth + start) should be fully functional and testable independently - this is the minimal MVP

---

## Phase 5: User Story 2 - Stop Sauna Session (Priority: P1) 🎯 MVP Safety

**Goal**: Enable users to stop sauna heating from command line

**Independent Test**: Start a sauna, then run `huum stop`, verify heating stops and session ends

### Implementation for User Story 2

- [x] **T034** [US2] Implement `stop_session()` method in `src/huum_cli/api/client.py` that POSTs to `/action/stop_sauna` with device_id
- [x] **T035** [US2] Create `stop` command in `src/huum_cli/commands/stop.py` with argument device_id (optional)
- [x] **T036** [US2] Implement stop flow: get credentials → get devices → select device (auto-select if single) → call `stop_session()` → display confirmation with session summary
- [x] **T037** [US2] Add error handling for stop command: not authenticated (exit 1), device not found (exit 1), no active session (warning, exit 0), device offline (exit 2), API errors (exit 2)
- [x] **T038** [US2] Create human-readable output formatter `format_stop_success()` in `src/huum_cli/utils/formatters.py` showing session duration and max temperature with Rich formatting
- [x] **T039** [US2] Register `stop` command in `src/huum_cli/cli.py` Typer app

**Checkpoint**: At this point, User Stories 6, 1, and 2 (auth + start + stop) form complete MVP - users have full sauna control

---

## Phase 6: User Story 3 - Check Sauna Status (Priority: P2)

**Goal**: Enable users to view sauna status from command line

**Independent Test**: Run `huum status` while sauna is in various states (idle, heating, ready), verify accurate information displayed

### Implementation for User Story 3

- [x] **T040** [US3] Create `status` command in `src/huum_cli/commands/status.py` with basic display (device_id optional)
- [x] **T041** [US3] Implement status display logic: get credentials → get devices → display all devices in Rich table
- [x] **T042** [US3] Create Rich table formatter showing Device ID, Name, Online status, Current temp, Target temp, and State
- [ ] **T043** [US3] Implement watch mode in status command: continuous refresh every N seconds until Ctrl+C (handle SIGINT gracefully)
- [ ] **T044** [US3] Add progress bar calculation in formatter: `(current_temp / target_temp) * 100` with visual bar using Rich progress
- [x] **T045** [US3] Add error handling for status command: not authenticated (exit 1), no devices (exit 0 with helpful message), API errors (exit 2)
- [x] **T046** [US3] Register `status` command in `src/huum_cli/cli.py` Typer app

**Checkpoint**: At this point, User Stories 6, 1, 2, and 3 complete - users can control and monitor sauna

---

## Phase 7: User Story 4 - Set Target Temperature (Priority: P2)

**Goal**: Enhance start command to accept custom target temperatures

**Independent Test**: Run `huum start --temperature 75`, verify sauna heats to 75°C (not default 85°C)

### Implementation for User Story 4

- [ ] **T047** [US4] Update validation in `src/huum_cli/utils/validators.py` to include clear error messages showing acceptable range (40-110°C)
- [ ] **T048** [US4] Enhance start command error handling to display temperature range on validation failure
- [ ] **T049** [US4] Add temperature validation test cases in start command: test boundary values (40, 110), test invalid values (39, 111, -10, 200)
- [ ] **T050** [US4] Update start command help text to document temperature range and default value

**Checkpoint**: Temperature customization complete - start command fully enhanced

---

## Phase 8: User Story 5 - List Available Devices (Priority: P3)

**Goal**: Enable users to see all their sauna devices

**Independent Test**: Run `huum list`, verify all associated devices displayed with names and online status

### Implementation for User Story 5

- [ ] **T051** [US5] Create `list` command in `src/huum_cli/commands/list.py` with no arguments
- [ ] **T052** [US5] Implement list flow: get credentials → call `get_status()` (reuse from US1) → extract device list → display
- [ ] **T053** [US5] Create human-readable formatter `format_device_list()` in `src/huum_cli/utils/formatters.py` with Rich table showing numbered list, device name, ID, online status, last seen timestamp
- [ ] **T054** [US5] Add error handling for list command: not authenticated (exit 1), no devices found (exit 0 with message about Huum app), API errors (exit 2)
- [ ] **T055** [US5] Register `list` command in `src/huum_cli/cli.py` Typer app

**Checkpoint**: All user stories (US1-US6) should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] **T056** [P] Create configuration file management in `src/huum_cli/commands/config.py`: `get_config_path()`, `load_config()`, `save_config()` using platform-specific directories (~/.config/huum-cli/config.json on Linux/Mac, %APPDATA%\huum-cli\config.json on Windows)
- [ ] **T057** [P] Implement `config` command in `src/huum_cli/commands/config.py` with subcommands: show (display all), get <key>, set <key> <value>, reset (restore defaults)
- [ ] **T058** [P] Define configurable settings: default_device (device_id), default_temperature (int), output_format (human/json), auto_refresh (bool)
- [ ] **T059** Update start command to use default_temperature from config if not specified via --temperature
- [ ] **T060** Update all commands to use default_device from config if device_id not specified and multiple devices exist
- [ ] **T061** Register `config` command in `src/huum_cli/cli.py` Typer app
- [ ] **T062** [P] Add global --format flag support: when --format=json, use `format_json()` for all commands instead of human formatters
- [ ] **T063** [P] Add global --verbose flag support: enable debug logging to stderr when specified
- [ ] **T064** [P] Implement retry logic with exponential backoff in API client using tenacity for network errors and 429 rate limits
- [ ] **T065** [P] Add HTTP status code handling: 401 → re-authenticate, 403 → permission denied, 404 → resource not found, 429 → rate limited, 503 → service unavailable
- [ ] **T066** [P] Create README.md with installation instructions (uv install), basic usage examples for all commands, authentication setup, troubleshooting section
- [ ] **T067** [P] Add docstrings to all functions and classes following Google style
- [ ] **T068** [P] Run mypy type checking: `uv run mypy src/` and fix any type errors
- [ ] **T069** [P] Run ruff linting: `uv run ruff check src/` and fix any issues
- [ ] **T070** [P] Create mock API responses in `tests/fixtures/mock_responses.py` for testing without real API
- [ ] **T071** [P] Add unit tests for storage functions in `tests/unit/test_storage.py` (test store/get/delete credentials with mocked keyring)
- [ ] **T072** [P] Add unit tests for validators in `tests/unit/test_validators.py` (test temperature validation boundary cases)
- [ ] **T073** [P] Add unit tests for formatters in `tests/unit/test_formatters.py` (test output formatting functions)
- [ ] **T074** [P] Add integration test for authentication flow in `tests/integration/test_auth.py` (mock httpx responses)
- [ ] **T075** [P] Add integration test for start/stop flow in `tests/integration/test_sauna_control.py` (mock httpx responses)
- [ ] **T076** Final manual testing: run through all commands in sequence (auth → list → start → status → stop → logout) and verify correct behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 6 - Auth (Phase 3)**: Depends on Foundational - BLOCKS all other user stories (auth is prerequisite)
- **User Story 1 - Start (Phase 4)**: Depends on US6 - Can proceed once auth works
- **User Story 2 - Stop (Phase 5)**: Depends on US6 - Can proceed once auth works (can work in parallel with US1)
- **User Story 3 - Status (Phase 6)**: Depends on US6 - Can proceed once auth works (can work in parallel with US1, US2)
- **User Story 4 - Temperature (Phase 7)**: Depends on US1 - Enhances start command
- **User Story 5 - List (Phase 8)**: Depends on US6 - Can proceed once auth works (can work in parallel with US1, US2, US3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 6 (Auth) - P1**: Must complete FIRST - blocks all other stories
- **User Story 1 (Start) - P1**: Can start after US6 - independent of other stories
- **User Story 2 (Stop) - P1**: Can start after US6 - independent of US1 (can run parallel)
- **User Story 3 (Status) - P2**: Can start after US6 - independent of US1/US2 (can run parallel)
- **User Story 4 (Temperature) - P2**: Depends on US1 - enhances start command
- **User Story 5 (List) - P3**: Can start after US6 - independent of all others (can run parallel)

### Within Each User Story

- Models created in Foundational phase before any story
- API client methods before command implementation
- Core implementation before error handling
- Error handling before registration in CLI app
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: Tasks T003, T004, T005, T006, T007 can run in parallel
- **Phase 2 (Foundational)**: Tasks T008, T009, T010, T016 can run in parallel (different files)
- **After US6 completes**: US1, US2, US3, US5 can all start in parallel (different command files)
- **Phase 9 (Polish)**: Most tasks (T056-T057-T058, T062-T063-T064-T065, T066-T067-T068-T069, T070-T071-T072-T073-T074-T075) can run in parallel as they affect different files

---

## Parallel Example: After Authentication (US6) Complete

```bash
# These user stories can be developed in parallel by different developers:

Developer A: Tasks T025-T033 (User Story 1 - Start)
Developer B: Tasks T034-T039 (User Story 2 - Stop)
Developer C: Tasks T040-T046 (User Story 3 - Status)
Developer D: Tasks T051-T055 (User Story 5 - List)

# All depend only on US6 (auth) being complete
```

## Parallel Example: Foundational Phase

```bash
# These foundational tasks can run simultaneously:

Task T008: Create SaunaDevice model in src/huum_cli/api/models.py
Task T009: Create AuthCredentials model in src/huum_cli/api/models.py (same file, sequential)
Task T010: Create Session model in src/huum_cli/api/models.py (same file, sequential)
Task T016: Create formatters in src/huum_cli/utils/formatters.py

# Note: T008, T009, T010 must be sequential (same file), but T016 parallel
```

---

## Implementation Strategy

### MVP First (User Stories 6 + 1 + 2 Only)

**Minimum Viable Product - Full Sauna Control**

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T016) - CRITICAL
3. Complete Phase 3: User Story 6 - Auth (T017-T024) - BLOCKS everything
4. Complete Phase 4: User Story 1 - Start (T025-T033)
5. Complete Phase 5: User Story 2 - Stop (T034-T039)
6. **STOP and VALIDATE**: Test auth → start → stop workflow
7. Deploy/demo basic sauna control

**At this point you have a complete, usable CLI for basic sauna control**

### Incremental Delivery (Add User Stories Incrementally)

1. **Foundation** (Phases 1-3: T001-T024) → Auth works
2. **MVP v1** (Add Phase 4: T025-T033) → Can start sauna
3. **MVP v2** (Add Phase 5: T034-T039) → Can start and stop sauna ✅ **DEMO READY**
4. **v3** (Add Phase 6: T040-T046) → Can monitor status
5. **v4** (Add Phase 7: T047-T050) → Custom temperatures
6. **v5** (Add Phase 8: T051-T055) → List devices for multi-device users
7. **Polish** (Phase 9: T056-T076) → Config, tests, documentation

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase:

1. **Everyone together**: Phases 1-2 (Setup + Foundational)
2. **One developer**: Phase 3 (US6 - Auth) - blocks everyone
3. **Once auth done, split team**:
   - Developer A: Phase 4 (US1 - Start)
   - Developer B: Phase 5 (US2 - Stop)
   - Developer C: Phase 6 (US3 - Status)
   - Developer D: Phase 8 (US5 - List)
4. **Sequential**: Phase 7 (US4 - Temperature) after US1
5. **Everyone together**: Phase 9 (Polish)

---

## Task Summary

**Total Tasks**: 76 tasks

**Tasks per User Story**:
- Setup: 7 tasks
- Foundational: 9 tasks
- US6 (Auth): 8 tasks
- US1 (Start): 9 tasks
- US2 (Stop): 6 tasks
- US3 (Status): 7 tasks
- US4 (Temperature): 4 tasks
- US5 (List): 5 tasks
- Polish: 21 tasks

**Parallel Opportunities**: 25+ tasks marked [P] can run in parallel

**MVP Scope** (Phases 1-5): 39 tasks for complete sauna control

**Independent Test Criteria**:
- US6: Can authenticate and session is stored
- US1: Can start sauna heating via CLI
- US2: Can stop sauna heating via CLI
- US3: Can view accurate sauna status
- US4: Can specify custom temperature when starting
- US5: Can view list of all devices

---

## Notes

- All tasks include exact file paths for implementation
- Tasks within same file are sequential, different files can be parallel
- Each user story delivers independently testable value
- Stop at any checkpoint to validate and demo progress
- Error handling includes specific exit codes per CLI contract specification
- No tests included as TDD not requested in specification
- Follow quickstart.md for detailed implementation patterns
- Refer to contracts/huum-api.md for exact API endpoint specifications
- Use data-model.md for entity structure and validation rules
