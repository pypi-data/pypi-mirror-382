# Cakemail API MCP Server Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Eliminate AI hallucination of Cakemail API endpoints, parameters, and authentication mechanisms
- Enable AI coding assistants to generate correct Cakemail integration code on first attempt
- Reduce developer integration time by 50% for AI-assisted workflows
- Position Cakemail as a leader in AI-ready developer experience
- Achieve 85%+ first-call accuracy for AI-generated API calls
- Deploy production-ready MCP server within 4-6 weeks

### Background Context

Developers using AI coding assistants (Claude, Cursor, GitHub Copilot) to build Cakemail integrations currently face a critical accuracy problem: AI agents guess API details rather than reference authoritative specifications, resulting in hallucinated endpoints, invalid parameters, and broken authentication flows. While Cakemail maintains comprehensive OpenAPI documentation at docs.cakemail.com and an `openapi.json` specification, AI agents have no direct access to this authoritative source during code generation. This creates a frustrating cycle where every AI-generated API call requires manual verification and correction, breaking developer trust and making Cakemail integrations slower and more error-prone than competitors.

The Cakemail API MCP Server solves this by leveraging the Model Context Protocol (MCP) standard to expose Cakemail's OpenAPI specification directly to AI agents as queryable tools. Instead of guessing, AI tools can retrieve exact endpoint specifications, parameter schemas, and authentication details on-demand. This positions Cakemail as one of the first email marketing APIs to support AI-assisted development natively, capturing the fast-growing segment of developers who rely on AI coding tools (55% of developers according to Stack Overflow 2024).

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-10-05 | 1.0 | Initial PRD creation from project brief | John (PM) |
| 2025-10-05 | 1.1 | Updated technical assumptions: Python/FastMCP instead of TypeScript/Node.js based on architecture validation | Winston (Architect) |

## Requirements

### Functional

- **FR1:** The MCP server SHALL load and parse Cakemail's OpenAPI specification from a local `openapi.json` file or remote URL
- **FR2:** The MCP server SHALL expose an "endpoint discovery" tool that returns a list of all available Cakemail API endpoints with descriptions when queried by AI agents
- **FR3:** The MCP server SHALL expose an "endpoint details" tool that returns complete specifications for a specific endpoint including URL, HTTP method, parameters (with types, validation rules, required/optional flags), request schema, response schema, and authentication requirements
- **FR4:** The MCP server SHALL expose authentication documentation including API key format, required headers, and token usage patterns
- **FR5:** The MCP server SHALL validate the loaded OpenAPI specification on startup and report any parsing errors or schema validation failures
- **FR6:** The MCP server SHALL communicate with AI agents via the Model Context Protocol using stdio transport
- **FR7:** The MCP server SHALL respond to tool queries within 500ms for spec lookups under normal operating conditions
- **FR8:** The MCP server SHALL provide clear error messages when queries reference non-existent endpoints or malformed requests
- **FR9:** The installation documentation SHALL provide step-by-step configuration instructions for Claude Desktop, Cursor, and generic MCP-compatible tools
- **FR10:** The MCP server SHALL support reloading the OpenAPI specification without full server restart (manual trigger for MVP)

### Non Functional

- **NFR1:** The MCP server SHALL be implemented in Python 3.11+ with strict type hints for type safety and maintainability
- **NFR2:** The MCP server SHALL use the FastMCP framework as the foundation for MCP protocol compliance
- **NFR3:** The MCP server SHALL require Python 3.11+ as the runtime environment
- **NFR4:** The MCP server SHALL be cross-platform compatible (macOS, Windows, Linux)
- **NFR5:** The MCP server SHALL have minimal memory footprint (<50MB under typical operation)
- **NFR6:** The codebase SHALL include unit tests with >80% code coverage for core MCP tool implementations
- **NFR7:** The project SHALL be distributed as a PyPI package for easy installation
- **NFR8:** The project SHALL be open source under MIT license to encourage adoption and community contributions
- **NFR9:** The documentation SHALL include troubleshooting guides for common installation and configuration issues
- **NFR10:** The MCP server SHALL log all tool invocations and errors for debugging purposes

## Technical Assumptions

### Repository Structure: Monorepo

The project will use a single repository containing the MCP server implementation, documentation, tests, and example configurations. This is appropriate for the MVP scope as we have a focused, cohesive deliverable without complex multi-service orchestration needs.

### Service Architecture

**Standalone MCP Server Process (Monolithic)**

The MCP server will be implemented as a single Python process that:
- Loads and parses the OpenAPI specification on startup
- Exposes MCP tools via stdio transport for AI agent communication
- Handles all tool invocations (discovery, detail queries, auth docs) within a single process
- Runs locally on developer machines (no remote hosting required for MVP)

This monolithic approach fits the MVP perfectly - we're building a developer tool that runs client-side, not a distributed system. The FastMCP framework handles MCP protocol compliance, and we layer our OpenAPI parsing logic on top.

**IMPORTANT ARCHITECTURE DECISION:** After technical validation, the project will use **Python + FastMCP** instead of TypeScript/Node.js. Rationale:
- FastMCP provides native OpenAPI integration via `FastMCP.from_openapi()` - eliminates 70%+ of custom code
- Production-ready MCP protocol implementation out of the box
- Faster time-to-market for MVP (4-6 week timeline)
- Python 3.11+ excellent for data parsing and transformation
- See `docs/architecture.md` for complete technical specification

### Testing Requirements

**Unit + Integration Testing**

- **Unit tests:** Core OpenAPI parsing, tool response formatting, error handling (target: >80% coverage)
- **Integration tests:** End-to-end MCP server startup, tool invocation simulation, OpenAPI spec validation
- **Manual testing:** Real-world validation with Claude Desktop and Cursor to ensure AI agents can successfully query the server
- **No E2E UI tests needed:** This is a command-line/background service, not a web application

Testing focus: Ensure MCP server correctly interprets OpenAPI spec and returns accurate data to AI agents. The "user interface" is the AI agent interaction, so integration tests that simulate MCP tool calls are critical.

### Additional Technical Assumptions and Requests

- **Language & Runtime:** Python 3.11+ (performance improvements, modern type hints)
- **Framework:** FastMCP 0.2.0+ (native OpenAPI support, production-ready MCP protocol)
- **Package Manager:** uv (FastMCP recommended, 10-100x faster than pip)
- **OpenAPI Parser:** Built into FastMCP via `FastMCP.from_openapi()` (no external library needed)
- **Logging:** Python `logging` stdlib (sufficient for MVP, familiar to Python developers)
- **Configuration:** `python-dotenv` for `.env` file loading (OPENAPI_SPEC_PATH configuration)
- **Testing Framework:** pytest 8.0+ (industry standard, excellent fixtures and parametrization)
- **Code Quality Tools:**
  - `black` for code formatting (line length 100)
  - `ruff` for linting (10-100x faster than flake8, Rust-based)
  - `mypy` for static type checking
- **Build Tooling:** `hatch` (modern Python build system, PEP 517/518 compliant)
- **CI/CD:** GitHub Actions for automated testing on push/PR (run tests on Python 3.11, 3.12)
- **Distribution:** Publish to PyPI as `cakemail-api-docs-mcp` (installable via `pip install`)
- **Versioning:** Follow semantic versioning (SemVer) with automated changelog generation

## Epic List

**Epic 1: Foundation & Core MCP Infrastructure**
Establish project setup with Python, FastMCP integration, OpenAPI spec loading, and a basic "health check" MCP tool to validate the infrastructure works end-to-end.

**Epic 2: API Discovery & Documentation Tools**
Build the core MCP tools (endpoint discovery, endpoint details, authentication docs) that solve the AI hallucination problem by providing authoritative API specifications.

**Epic 3: Developer Experience & Release Readiness**
Create comprehensive installation guides, testing validation, troubleshooting documentation, and prepare for npm publication and community adoption.

## Epic 1: Foundation & Core MCP Infrastructure

**Epic Goal:** Establish a working Python project with FastMCP framework integration, OpenAPI specification loading capabilities, and a minimal "health check" MCP tool that validates end-to-end MCP communication. This epic proves technical feasibility and sets up all foundational infrastructure (repo, dependencies, CI/CD, logging) while delivering a simple but deployable MCP server that AI agents can successfully invoke.

### Story 1.1: Project Scaffolding and Repository Setup

As a **developer**,
I want **a properly configured Python project with all build tooling and dependencies**,
so that **I have a solid foundation to build the MCP server with modern development practices**.

**Acceptance Criteria:**

1. Repository is initialized with Git, `.gitignore` excludes `__pycache__/`, `.pytest_cache/`, `.env`, `.mypy_cache/`, and common IDE files
2. `pyproject.toml` is configured with Python 3.11+, FastMCP, python-dotenv, and development dependencies (pytest, pytest-cov, black, ruff, mypy, hatch)
3. Project follows `src/` layout with `src/cakemail_mcp/` package directory
4. `README.md` includes basic project description and placeholder installation instructions
5. MIT license file is present in repository root
6. `ruff.toml` and `mypy.ini` configuration files are present
7. Running `uv pip install -e .` successfully installs package in editable mode without errors
8. Project structure follows architecture specification in `docs/architecture.md`

### Story 1.2: MCP Server Initialization with FastMCP

As a **developer**,
I want **a minimal MCP server that initializes FastMCP framework and establishes stdio communication**,
so that **AI agents can connect to the server and discover available tools**.

**Acceptance Criteria:**

1. `src/cakemail_mcp/server.py` implements MCP server entry point using FastMCP framework
2. Server initializes stdio transport for communication with AI agents (per MCP protocol spec)
3. Server logs startup message with version, timestamp, and configuration summary using Python `logging`
4. Server gracefully handles shutdown signals (SIGINT, SIGTERM) and logs clean exit
5. `src/cakemail_mcp/__main__.py` provides entry point for `python -m cakemail_mcp`
6. Running `python -m cakemail_mcp` launches the MCP server without errors
7. Server exposes MCP server metadata (name: "Cakemail API MCP Server", version from pyproject.toml)
8. Server implements error handling for uncaught exceptions and logs errors before exit

### Story 1.3: OpenAPI Specification Loading

As a **developer**,
I want **the MCP server to load and parse Cakemail's OpenAPI specification from a configurable source**,
so that **API endpoint data is available for MCP tools to query**.

**Acceptance Criteria:**

1. `.env.example` file documents `OPENAPI_SPEC_PATH` environment variable (supports local file path or URL)
2. Server reads `OPENAPI_SPEC_PATH` from environment on startup, defaults to `./openapi.json` if not set
3. Server uses FastMCP's `from_openapi()` method to load and validate the OpenAPI specification
4. Server logs successful spec loading with count of endpoints parsed
5. Server validates OpenAPI spec conforms to OpenAPI 3.x standard and logs validation errors if spec is invalid
6. Server halts startup and exits with error code if OpenAPI spec fails to load or validate
7. Parsed OpenAPI spec is stored in memory and accessible to MCP tool handlers via `OpenAPIRepository`
8. Unit tests verify spec loading from both local file and URL sources (mocked HTTP for URL test)

### Story 1.4: Health Check MCP Tool

As a **developer using an AI agent**,
I want **a basic "health check" MCP tool to verify the server is responsive**,
so that **I can confirm end-to-end MCP communication is working before building complex tools**.

**Acceptance Criteria:**

1. Server exposes MCP tool named `cakemail_health` with description "Check if Cakemail MCP server is operational"
2. Tool accepts no input parameters
3. Tool returns JSON response with: `{ status: "ok", serverVersion: "<version>", endpointCount: <number>, timestamp: "<ISO date>" }`
4. AI agent can successfully invoke `cakemail_health` tool and receive correct response
5. Tool invocation is logged with timestamp and tool name
6. Integration test simulates MCP tool call and validates response structure
7. Tool execution completes within 100ms under normal conditions
8. Manual test: AI agent (Claude Desktop or Cursor) can invoke tool and display health status

### Story 1.5: CI/CD Pipeline and Automated Testing

As a **developer**,
I want **automated testing and build validation on every code push**,
so that **we maintain code quality and catch regressions early**.

**Acceptance Criteria:**

1. `.github/workflows/ci.yml` GitHub Actions workflow runs on push to main and on all pull requests
2. CI workflow runs on Python 3.11 and 3.12 matrix to ensure cross-version compatibility
3. CI workflow installs dependencies with `uv pip install -e .[dev]`
4. CI workflow runs `pytest` with coverage and fails build if tests fail or coverage <80%
5. CI workflow runs `ruff check` for linting and fails build if linting errors
6. CI workflow runs `black --check` for formatting and fails build if formatting issues
7. CI workflow runs `mypy` for type checking and fails build if type errors
8. Test coverage report is generated and displayed in CI logs
9. CI status badge is added to README.md showing build pass/fail status

## Epic 2: API Discovery & Documentation Tools

**Epic Goal:** Implement the core MCP tools that solve the AI hallucination problem by providing authoritative Cakemail API specifications. AI agents will be able to discover available endpoints, query detailed specifications including parameters and schemas, and access authentication documentation - all from the OpenAPI spec loaded in Epic 1. This epic delivers the primary value proposition of the project.

### Story 2.1: Endpoint Discovery Tool

As a **developer using an AI agent**,
I want **to discover all available Cakemail API endpoints with descriptions**,
so that **my AI assistant understands what API capabilities exist before generating code**.

**Acceptance Criteria:**

1. Server exposes MCP tool named `cakemail_list_endpoints` with description "List all available Cakemail API endpoints"
2. Tool accepts optional filter parameter `tag` (string) to filter endpoints by OpenAPI tag
3. Tool returns array of endpoints, each with: `{ path: string, method: string, summary: string, tags: string[], operationId: string }`
4. Endpoints are sorted alphabetically by path, then by HTTP method
5. If `tag` filter is provided, only endpoints matching that tag are returned
6. Tool returns empty array if no endpoints match filter (not an error)
7. Unit tests verify correct parsing of OpenAPI paths and operations
8. Integration test validates tool returns expected endpoint count from test OpenAPI spec
9. Manual test: AI agent can list all endpoints and filter by tag (e.g., "campaigns")

### Story 2.2: Endpoint Detail Query Tool

As a **developer using an AI agent**,
I want **to retrieve complete specifications for a specific API endpoint**,
so that **my AI assistant generates code with correct URLs, parameters, request bodies, and response handling**.

**Acceptance Criteria:**

1. Server exposes MCP tool named `cakemail_get_endpoint` with description "Get detailed specification for a specific Cakemail API endpoint"
2. Tool accepts required parameters: `path` (string, e.g., "/campaigns/{id}") and `method` (string, e.g., "GET")
3. Tool returns detailed endpoint specification including:
   - Full URL path with path parameters clearly marked
   - HTTP method
   - Description and summary
   - All parameters (path, query, header) with: name, type, required flag, description, example values
   - Request body schema (if applicable) with content type and full JSON schema
   - Response schemas for success (200, 201, etc.) and common errors (400, 401, 404) with full JSON schemas
   - Authentication requirements (security schemes from OpenAPI)
4. Tool dereferences all `$ref` pointers in schemas to provide complete, inline schemas
5. Tool returns clear error message if endpoint path/method combination doesn't exist
6. Unit tests verify schema dereferencing and parameter extraction
7. Integration test validates tool returns complete spec for sample endpoint
8. Manual test: AI agent can query endpoint details and use them to generate correct API client code

### Story 2.3: Authentication Documentation Tool

As a **developer using an AI agent**,
I want **to access Cakemail API authentication requirements and format**,
so that **my AI assistant generates code with correct authentication headers and token handling**.

**Acceptance Criteria:**

1. Server exposes MCP tool named `cakemail_get_auth` with description "Get Cakemail API authentication documentation"
2. Tool accepts no parameters
3. Tool returns authentication documentation extracted from OpenAPI `securitySchemes`, including:
   - Authentication type (e.g., "HTTP Bearer", "API Key", "OAuth2")
   - Required headers (e.g., "Authorization: Bearer {token}")
   - Token format and location (header, query, cookie)
   - Description of how to obtain credentials (from OpenAPI description field)
4. If multiple security schemes exist, all are returned with clear labels
5. Tool returns human-readable format suitable for AI agent consumption
6. Unit tests verify correct extraction of security schemes from OpenAPI spec
7. Integration test validates auth documentation matches test OpenAPI spec
8. Manual test: AI agent can retrieve auth docs and generate code with correct authentication

### Story 2.4: Error Handling and Validation

As a **developer using an AI agent**,
I want **clear error messages when MCP tools are invoked incorrectly or data is unavailable**,
so that **I can quickly understand and fix problems without debugging server internals**.

**Acceptance Criteria:**

1. All MCP tools validate required parameters and return structured error if missing or invalid type
2. Error responses follow consistent format: `{ error: string, code: string, details?: object }`
3. Error codes are documented: `MISSING_PARAMETER`, `INVALID_PARAMETER`, `ENDPOINT_NOT_FOUND`, `SPEC_LOAD_ERROR`
4. When endpoint doesn't exist, error includes suggestion of similar endpoints (Levenshtein distance matching)
5. When OpenAPI spec fails to load, tools return `SPEC_LOAD_ERROR` instead of crashing
6. All errors are logged with full context for debugging
7. Unit tests verify error handling for each tool's edge cases
8. Integration test simulates malformed tool calls and validates error responses

### Story 2.5: Performance Optimization and Caching

As a **developer using an AI agent**,
I want **fast response times (<500ms) when querying API specifications**,
so that **my development workflow isn't slowed down by MCP tool latency**.

**Acceptance Criteria:**

1. Parsed OpenAPI spec is cached in memory after initial load (no re-parsing on each tool call)
2. Endpoint list is pre-computed and cached on server startup for `cakemail_list_endpoints` performance
3. Schema dereferencing results are memoized to avoid redundant processing
4. Tool response times are measured and logged (warn if >500ms)
5. All tools complete within 500ms under normal load (tested with realistic Cakemail OpenAPI spec)
6. Memory usage remains stable after repeated tool invocations (no memory leaks)
7. Unit tests verify caching behavior reduces processing time on subsequent calls
8. Load test simulates 100 rapid tool invocations and validates consistent performance

## Epic 3: Developer Experience & Release Readiness

**Epic Goal:** Transform the working MCP server into a production-ready, easily adoptable open-source tool through comprehensive documentation, installation guides, troubleshooting resources, and npm package preparation. This epic ensures developers can discover, install, configure, and successfully use the Cakemail MCP server without extensive support, maximizing adoption and achieving the brief's goals of positioning Cakemail as a leader in AI-assisted development.

### Story 3.1: Installation and Configuration Documentation

As a **developer new to the Cakemail MCP Server**,
I want **clear, step-by-step installation instructions for my development environment**,
so that **I can get the MCP server running in under 10 minutes without troubleshooting**.

**Acceptance Criteria:**

1. README.md includes "Quick Start" section with installation for Claude Desktop, Cursor, and generic MCP clients
2. Documentation shows exact `claude_desktop_config.json` or equivalent configuration examples with copy-paste-ready code
3. Instructions cover both npm installation (`npm install -g @cakemail/mcp-server`) and local development setup
4. Environment variable configuration (`.env` file setup for `OPENAPI_SPEC_PATH`) is documented with examples
5. Prerequisites are clearly listed (Node.js 18+, pnpm installation if developing locally)
6. Screenshots or ASCII diagrams show AI agent successfully invoking MCP tools
7. Troubleshooting section addresses common issues (wrong Node version, missing OpenAPI spec, permission errors)
8. Manual test: External developer with no prior context can complete installation in <10 minutes

### Story 3.2: Usage Examples and Developer Guide

As a **developer using the Cakemail MCP Server**,
I want **practical examples showing how AI agents use MCP tools to generate code**,
so that **I understand the value and can validate it's working correctly**.

**Acceptance Criteria:**

1. `USAGE.md` or README section includes example AI agent conversations showing MCP tool usage
2. Example 1: AI agent uses `cakemail_list_endpoints` to discover campaigns API, then `cakemail_get_endpoint` to generate campaign creation code
3. Example 2: AI agent uses `cakemail_get_auth` to understand authentication, generates correct Bearer token header code
4. Example 3: AI agent handles error case (queries non-existent endpoint, receives helpful error, corrects query)
5. Each example shows both the AI agent query and the MCP tool response (formatted for readability)
6. Documentation explains "before and after" - shows AI hallucination vs. MCP-assisted correct code
7. Link to video demo or GIF showing real usage in Claude Desktop (optional but highly valuable)
8. Examples cover multiple programming languages (JavaScript/TypeScript, Python, curl for testing)

### Story 3.3: OpenAPI Specification Reload and Maintenance

As a **Cakemail internal developer maintaining the MCP server**,
I want **the ability to reload the OpenAPI specification without restarting the MCP server**,
so that **API updates are reflected quickly without disrupting active developer sessions**.

**Acceptance Criteria:**

1. Server exposes MCP tool named `cakemail_reload_spec` with description "Reload Cakemail OpenAPI specification"
2. Tool requires no parameters (uses same `OPENAPI_SPEC_PATH` from environment)
3. Tool triggers re-loading and re-parsing of OpenAPI spec, updating all cached data
4. Tool returns success message with new endpoint count and timestamp
5. Tool returns error if reload fails (invalid spec, network error), preserving previous valid spec
6. Reload operation completes within 2 seconds for typical OpenAPI spec size
7. Unit tests verify spec reload updates cached endpoint data
8. Manual test: Update OpenAPI spec file, invoke reload tool, verify new endpoints are discoverable

### Story 3.4: npm Package Publishing and Distribution

As a **developer wanting to install the Cakemail MCP Server**,
I want **the package available on npm registry with clear versioning**,
so that **I can install it with a simple `npm install` command like any other tool**.

**Acceptance Criteria:**

1. `package.json` is configured for npm publishing with correct metadata: name, version, description, keywords, repository, license
2. Package includes `files` field listing only necessary files for distribution (`dist/`, `README.md`, `LICENSE`, `.env.example`)
3. `.npmignore` excludes source code (`src/`), tests, and development files
4. Package has `bin` entry pointing to compiled MCP server executable
5. README includes npm installation badge and shields.io version badge
6. Publishing workflow uses semantic versioning (SemVer) and generates CHANGELOG.md automatically
7. Test installation: `npm install -g @cakemail/mcp-server` works and `cakemail-api-docs-mcp` command is available globally
8. Published package size is reasonable (<5MB) - excludes devDependencies and unnecessary files

### Story 3.5: Comprehensive Testing and Beta Validation

As a **project stakeholder**,
I want **confidence that the MCP server works reliably in real-world conditions**,
so that **we can launch with minimal risk of adoption-blocking bugs**.

**Acceptance Criteria:**

1. Test coverage reaches >80% for all core modules (OpenAPI parsing, MCP tools, error handling)
2. Integration test suite covers all MCP tools with realistic Cakemail OpenAPI spec fixture
3. Manual testing checklist is created and executed covering: Claude Desktop setup, Cursor setup, all MCP tools, error scenarios
4. At least 3 external beta testers (from target developer segment) successfully install and use MCP server
5. Beta testers provide written feedback on installation experience, tool usability, and encountered issues
6. Critical bugs identified in beta testing are fixed before public release
7. Performance validation: All tools respond within 500ms under realistic load (tested with actual Cakemail OpenAPI spec)
8. Documentation is reviewed for accuracy - all examples work as written

### Story 3.6: Launch Preparation and Community Setup

As a **developer discovering the Cakemail MCP Server**,
I want **clear project information, contribution guidelines, and support channels**,
so that **I can confidently adopt the tool and contribute improvements if desired**.

**Acceptance Criteria:**

1. Repository includes `CONTRIBUTING.md` with guidelines for reporting issues, submitting PRs, and development setup
2. GitHub repository has description, topics/tags (mcp, openapi, cakemail, ai, claude), and website link
3. Issue templates are created for bug reports and feature requests
4. `CODE_OF_CONDUCT.md` establishes community standards
5. README includes "Support" section with links to GitHub issues and any relevant community channels
6. Project has clear roadmap or "Future Plans" section mentioning post-MVP features from brief
7. All documentation is proofread for clarity, grammar, and accuracy
8. Social media announcement content is drafted (for Cakemail blog, developer Twitter, etc.)

## Next Steps

### Architect Prompt

The PRD for the Cakemail API MCP Server is complete and ready for technical architecture design. Please review the PRD at `docs/prd.md` and the Project Brief at `docs/brief.md`, then create a comprehensive architecture document that specifies:

1. **System Architecture:** Detailed technical design of the MCP server implementation using TypeScript, gofastmcp framework, and OpenAPI parsing
2. **Module Structure:** Component breakdown, interfaces, and dependencies for OpenAPI loader, MCP tool handlers, caching layer, and logging
3. **Data Flow:** How OpenAPI specs are loaded, parsed, cached, and served to AI agents via MCP protocol
4. **Technology Stack Details:** Specific library versions, build configuration, and development tooling setup
5. **Testing Strategy:** Unit and integration test architecture to achieve >80% coverage
6. **Deployment Model:** npm package structure, installation flow, and runtime requirements

Use the command `*agent architect` to enter architecture mode and create the architecture document using the project brief and this PRD as input.

