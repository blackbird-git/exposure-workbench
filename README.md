
# Exposure and Remediation Workbench

A hands-on infrastructure operations and security lab for assessing Linux configurations, collecting diagnostic evidence, investigating operational issues, and validating remediation without unnecessarily disrupting application functionality.

The project combines traditional Linux systems engineering with local AI-assisted infrastructure analysis using Python, Ollama, and Qwen3.

## Project Goals

- Develop repeatable methods for investigating Linux infrastructure and security configurations.
- Collect diagnostic evidence across services, file permissions, and networking.
- Identify potential configuration weaknesses and validate remediation.
- Apply AI to infrastructure troubleshooting while maintaining human oversight.
- Build practical experience with AI integration, automation, security controls, and reliability engineering.

## Architecture

```text
WSL Ubuntu (management environment)
    |
    | SSH
    v
Ubuntu Server VM (lab target)
    |
    | Read-only diagnostic scripts
    v
Service / File / Network Evidence
    |
    | Report collection
    v
report.txt
    |
    | Python validation and sanitization
    v
Local Ollama API
    |
    | Qwen3 4B
    v
Structured AI Diagnostic Findings
    |
    v
Human Review and Verification
```

AI-generated recommendations are advisory. The AI integration does not execute remediation commands.

## Technologies

**Infrastructure and networking**
- Ubuntu Linux
- systemd
- SSH
- TCP/IP
- Linux file permissions
- `ss`, `tcpdump`, `nc`, and `iptables`

**Automation and development**
- Bash
- Python 3
- Git and GitHub
- GitHub Actions
- Python unittest

**AI integration**
- Ollama
- Qwen3 4B
- Local HTTP API
- Structured JSON responses
- Diagnostic report sanitization

## Completed Work

### Linux Infrastructure and Security

- Created a dedicated Ubuntu Server VM on a host-only network.
- Demonstrated unnecessary root execution in a static web service.
- Moved the service to a dedicated nonlogin account.
- Enabled systemd `NoNewPrivileges`.
- Verified process identity and successful HTTP responses after remediation.
- Examined SSH privilege separation as an example of legitimate root usage.
- Investigated file-permission changes that prevented a service from serving content.
- Restored file access and verified application functionality.

### Diagnostic Automation

- Developed a read-only service assessment script.
- Developed a file ownership and permissions assessment script.
- Developed a network interface and listener inventory script.
- Built an SSH-based report collector.
- Added Python report validation.
- Added diagnostic report sanitization.
- Added automated Python tests.
- Configured GitHub Actions to run tests on pushes and pull requests.

### AI Infrastructure Analysis

- Installed Ollama locally in WSL Ubuntu.
- Configured Qwen3 4B with NVIDIA GPU acceleration.
- Integrated Python diagnostic analysis with Ollama's local HTTP API.
- Added structured diagnostic findings containing evidence, severity, confidence, and verification guidance.
- Preserved a read-only analysis workflow.
- Added mocked API tests that do not require a running AI model.

## Project Structure

```text
exposure-workbench/
├── .github/
│   └── workflows/
│       └── tests.yml
├── ai/
│   ├── __init__.py
│   ├── analyze.py
│   ├── ollama_client.py
│   └── sanitize.py
├── docs/
│   └── tcp-troubleshooting.md
├── scenarios/
│   ├── service-privileges/
│   │   └── README.md
│   └── file-permissions/
│       └── README.md
├── scripts/
│   ├── check-service.sh
│   ├── check-file.sh
│   ├── check-listeners.sh
│   └── collect-report.sh
├── tests/
│   ├── test_ai.py
│   └── test_sanitize.py
├── .gitignore
├── AI_INTEGRATION.md
└── README.md
```

Generated diagnostic reports are excluded from version control.

## Infrastructure Assessment

### Service Assessment

Run from WSL against the Ubuntu lab VM:

```bash
ssh user@lab-vm 'bash -s' < scripts/check-service.sh
```

The default service is `exposure-demo.service`.

To assess another service:

```bash
ssh user@lab-vm \
  'bash -s -- ssh.service' < scripts/check-service.sh
```

The script reports:

- systemd service state
- Configured service user
- Main process identity
- Process ownership

The script collects evidence without automatically determining whether a service's privileges are appropriate.

### File Permissions Assessment

Run:

```bash
ssh user@lab-vm 'bash -s' < scripts/check-file.sh
```

The default target is:

```text
/opt/exposure-demo/index.html
```

To inspect another path:

```bash
ssh user@lab-vm \
  'bash -s -- /opt/exposure-demo' < scripts/check-file.sh
```

The script reports file ownership, numeric permissions, and permissions along the directory path.

Permissions must be evaluated in the context of the application's intended behavior.

### Network Listener Inventory

Run:

```bash
ssh user@lab-vm 'bash -s' < scripts/check-listeners.sh
```

The script collects network interface addresses and listening TCP and UDP sockets.

Process information may be incomplete without elevated privileges.

A listening socket does not necessarily mean a service is externally reachable. Firewall rules, routing, interface bindings, and network topology must also be considered.

## Collect a Diagnostic Report

From the project root:

```bash
bash scripts/collect-report.sh
```

Or specify a target, service, and file path:

```bash
bash scripts/collect-report.sh user@host ssh.service /tmp
```

Arguments are positional:

1. SSH target
2. systemd service name
3. Remote file path

The collector writes its output to:

```text
report.txt
```

The collector continues collecting evidence when an individual check fails and returns a nonzero exit status if any check fails.

The generated report is excluded from Git.

## Python Report Validation

Validate a collected diagnostic report:

```bash
python3 ai/analyze.py report.txt
```

The analyzer verifies that the report is nonempty and checks for the following sections:

- Service
- File permissions
- Network listeners

This mode does not invoke an AI model.

## Report Sanitization

Sanitize a report before AI-assisted analysis:

```bash
python3 ai/sanitize.py report.txt
```

The sanitizer performs first-pass redaction of selected information, including:

- Private and non-global IP addresses
- Certain usernames
- Email addresses
- Hostname fields
- Common secret assignment patterns

Consistent placeholders preserve some relationships between repeated values.

Loopback and unspecified IP addresses are retained because they provide important diagnostic context.

**Security limitation:** Sanitization is not guaranteed to remove all sensitive information. Public IP addresses, arbitrary command arguments, and some other identifying details may remain. Review reports before sharing them outside the lab.

## Local AI Infrastructure Analysis

The project uses Ollama and Qwen3 4B to analyze collected diagnostic evidence.

### Prerequisites

- Python 3
- Ollama
- Qwen3 4B model
- Running local Ollama service

Install the model:

```bash
ollama pull qwen3:4b
```

Confirm the local API is accessible:

```bash
curl http://127.0.0.1:11434/api/tags
```

### Run AI Analysis

From the project root:

```bash
python3 ai/analyze.py report.txt --ai
```

The workflow:

1. Loads and validates the diagnostic report.
2. Sanitizes report content.
3. Sends the sanitized report to the configured local Ollama API.
4. Requests structured diagnostic findings.
5. Validates the model response.
6. Displays findings for human review.

The output includes diagnostic observations, supporting evidence, severity, confidence, and suggested verification steps.

### Example Findings

A service listening on `127.0.0.1:8080` may produce an observation that the application is accessible only through the loopback interface.

This is not automatically a vulnerability.

The configuration may be intentional if the application is accessed through a reverse proxy or is intended to remain local.

Similarly, a root-owned static file with `644` permissions is not inherently insecure. Readability and write access must be evaluated against application requirements.

These examples demonstrate why AI findings require technical validation rather than automatic remediation.

### Safety and Limitations

- The AI integration is read-only.
- Model-generated commands are not executed automatically.
- Ollama inference runs locally.
- Diagnostic content is treated as untrusted input.
- AI-generated findings may be incomplete or incorrect.
- Severity and confidence ratings are model-generated assessments, not verified risk measurements.
- Human review is required before making configuration changes.

## Automated Testing

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Tests cover report sanitization and AI integration behavior using mocked responses.

GitHub Actions runs the automated tests on repository pushes and pull requests.

The automated tests do not require Ollama, an NVIDIA GPU, or access to the lab VM.

## Networking Troubleshooting Lab

Completed a hands-on TCP connectivity troubleshooting exercise using WSL Ubuntu and an Ubuntu Server VM.

Practiced:

- Inspecting listening and established TCP connections with `ss`
- Capturing TCP handshakes and retransmissions using `tcpdump`
- Testing connectivity with `nc`
- Diagnosing connection refusals versus timeouts
- Creating and removing temporary firewall DROP rules using `iptables`
- Correlating packet captures with firewall counters
- Investigating routing and NAT behavior

Reproduced and diagnosed three TCP connection outcomes:

1. Successful connection
2. Connection refused
3. Connection timeout

See [TCP Connectivity Troubleshooting Lab](docs/tcp-troubleshooting.md) for commands, observations, and methodology.

## Security Scenarios

- [Service Privileges](scenarios/service-privileges/README.md)
- [File Permissions](scenarios/file-permissions/README.md)

The target VM is an isolated lab system containing intentionally configured test scenarios and no production credentials.

## Future Roadmap

### Phase 1 — AI Diagnostic Reliability

- Build a dataset of known-good and intentionally misconfigured Linux environments.
- Establish expected findings for each scenario.
- Evaluate false positives, missed issues, and unsupported conclusions.
- Improve evidence-based severity classification.
- Add regression tests for diagnostic quality.

### Phase 2 — Retrieval-Augmented Generation (RAG)

- Add retrieval from local documentation and runbooks.
- Ground AI recommendations in known configuration standards.
- Reference relevant documentation in findings.
- Evaluate whether retrieval improves diagnostic accuracy.

### Phase 3 — MCP and Tool Integration

- Introduce a Model Context Protocol interface.
- Expose narrowly scoped, read-only diagnostic tools.
- Validate tool inputs and permissions.
- Add audit logging and safeguards against prompt injection.

### Phase 4 — Infrastructure and Observability Integration

- Integrate diagnostic analysis with containerized workloads.
- Explore Kubernetes troubleshooting scenarios.
- Connect diagnostic evidence to monitoring and observability data.
- Evaluate deployment options using Terraform and AWS.

### Phase 5 — Security Integration Scenarios

- Simulate infrastructure security findings.
- Correlate service, network, and configuration evidence.
- Develop documented investigation and remediation workflows.
- Demonstrate secure AI-assisted operations in a realistic enterprise environment.

## Key Engineering Principles

**Evidence before conclusions:** Findings should be supported by observed configuration or diagnostic data.

**Context matters:** A configuration is not inherently insecure simply because it differs from a common default.

**Read-only by default:** Diagnostic collection and AI analysis must not silently modify infrastructure.

**Human oversight:** AI recommendations require verification before implementation.

**Repeatability:** Tests, documented scenarios, and version-controlled tooling make investigations reproducible.

## Project Status

**Current milestone:** Local AI-assisted infrastructure analysis is operational.

The next milestone is building a diagnostic evaluation dataset to measure the model's ability to distinguish normal infrastructure configurations from actionable problems.
