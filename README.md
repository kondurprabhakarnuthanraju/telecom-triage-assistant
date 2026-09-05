# 🚨 Network Incident Triage Assistant

**TRACK_ID: PS07**

An AI-powered **Telecom Network Incident Triage Assistant** that automatically groups network alerts into meaningful incidents, retrieves relevant troubleshooting procedures from runbooks using **RAG (Retrieval-Augmented Generation)**, prioritizes incidents based on impact, recommends actionable remediation steps, and escalates incidents when no reliable runbook match is available.

Built for **NexusTiQ 24**.

---

## 📌 Overview

Modern telecom and network environments generate thousands of alerts every day. Many of these alerts are duplicates, correlated symptoms, or low-priority noise.

The **Network Incident Triage Assistant** helps network operations teams reduce alert fatigue by transforming raw network alerts into structured incidents and providing grounded troubleshooting recommendations.

The system combines:

* 🤖 **Google Gemini** for reasoning and recommendations
* 🔎 **RAG** for retrieving relevant troubleshooting procedures
* 🧠 **Gemini Embeddings** for semantic search
* ⚡ **FAISS** for fast vector similarity search
* 🚨 **Intelligent Alert Grouping** for incident creation
* 📊 **Impact-Based Prioritization**
* 📚 **Runbook Citations** for grounded recommendations
* 👨‍💻 **Human Escalation** when no reliable runbook is available
* 🌐 **Web-Based Dashboard** for incident visualization

The goal is simple:

> **Turn noisy network alerts into actionable, explainable, and prioritized incidents.**

---

# ✨ Key Features

## 1. 🚨 Intelligent Alert Grouping

The system analyzes incoming alerts and groups related alerts into a single incident.

Alerts can be correlated using:

* Device
* Alert type
* Time window
* Network context
* Related symptoms

This prevents multiple alerts caused by the same underlying problem from being treated as independent incidents.

### Example

Instead of treating:

```text
Router R01 - Link Down
Router R01 - Interface Down
Router R01 - Device Unreachable
Router R01 - Packet Loss
```

as four independent incidents, the system can recognize that they are likely related and create a single incident:

```text
INC-001
Router R01 Connectivity Failure
```

This reduces alert noise and helps operators focus on the underlying problem.

---

# 2. 📊 Incident Prioritization

Every incident receives an **impact score from 1–10**.

The prioritization helps operators determine which incidents require immediate attention.

| Impact Score | Priority | Meaning                            |
| -----------: | -------- | ---------------------------------- |
|          1–3 | Low      | Limited or localized impact        |
|          4–6 | Medium   | Noticeable service degradation     |
|          7–8 | High     | Significant network/service impact |
|         9–10 | Critical | Major outage or widespread impact  |

The system uses incident information and alert characteristics to determine the appropriate priority.

---

# 3. 🔎 Retrieval-Augmented Generation (RAG)

The assistant does not rely solely on the LLM's general knowledge.

Instead, it retrieves relevant troubleshooting information from the provided network runbooks.

### RAG Pipeline

```text
Runbooks
   │
   ▼
Document Chunking
   │
   ▼
Gemini Embeddings
   │
   ▼
FAISS Vector Index
   │
   ▼
Semantic Retrieval
   │
   ▼
Relevant Runbook Chunks
   │
   ▼
Gemini
   │
   ▼
Grounded Recommendation
```

This makes recommendations more reliable and traceable.

---

# 4. 📚 Runbook-Grounded Recommendations

For every incident, the system retrieves the most relevant troubleshooting procedures.

The LLM generates recommendations using the retrieved runbook information.

Recommendations include citations to the source runbook.

For example:

```text
Recommendation:

1. Verify the physical connection to the affected interface.
2. Check the interface administrative and operational status.
3. Review recent interface errors.
4. If the interface remains down, follow the link recovery procedure.

Source:
link_down.txt
```

This allows an operator to understand **where the recommendation came from**.

---

# 5. 👨‍💻 Intelligent Escalation

The system does not force every incident into an existing runbook.

If no sufficiently relevant runbook is retrieved, the assistant recommends escalation to a human network engineer.

Example:

```text
No sufficiently relevant runbook was found.

Recommended Action:
Escalate this incident to the Network Operations team.

Reason:
The available runbooks do not provide sufficient guidance
for the observed alert pattern.
```

This is an important safety mechanism because an unsupported AI-generated troubleshooting procedure could potentially make a network incident worse.

---

# 6. 🧠 Noise Handling

Not every alert represents a genuine incident.

The system attempts to distinguish between:

```text
Meaningful Incident
        vs.
Alert Noise
```

Low-value or isolated alerts can remain classified as noise instead of being artificially grouped into an incident.

This helps reduce unnecessary investigation and alert fatigue.

---

# 7. ⚡ Fast Startup

The FAISS vector index is created when the application starts.

The runbooks are:

```text
Loaded
   ↓
Chunked
   ↓
Embedded
   ↓
Indexed in FAISS
```

This keeps retrieval fast and allows the application to operate within the **90-second execution constraint**.

---

# 🖥️ Web Interface

The project includes a lightweight web interface built using:

* HTML
* CSS
* JavaScript

The dashboard provides a simple way to:

* View incidents
* Review alert groups
* Inspect impact scores
* View recommended actions
* Review runbook citations
* Identify escalation cases

---

# 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │   Network Alerts    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Alert Processor    │
                 │                     │
                 │ Group related       │
                 │ alerts into         │
                 │ incidents           │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Triage Engine     │
                 │                     │
                 │ Impact Assessment   │
                 │ Incident Analysis   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    RAG Engine       │
                 │                     │
                 │ Gemini Embeddings   │
                 │ + FAISS Search      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Relevant Runbooks   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Google Gemini    │
                 │                     │
                 │ Generate grounded   │
                 │ recommendation      │
                 └──────────┬──────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
          ┌────────────────┐  ┌────────────────┐
          │ Recommendation │  │   Escalation   │
          │ + Citations     │  │  to Engineer   │
          └────────────────┘  └────────────────┘
```

---

# 🔄 How the System Works

The complete workflow consists of five major stages.

## Step 1 — Alert Ingestion

The application receives network alerts containing information such as:

* Device
* Alert type
* Timestamp
* Severity
* Description
* Network context

Example:

```json
{
  "device": "R01",
  "alert_type": "LINK_DOWN",
  "severity": 8,
  "timestamp": "2024-01-15T10:30:00",
  "description": "Interface Gi0/1 is down"
}
```

---

## Step 2 — Alert Correlation

The alert processor identifies alerts that are likely related.

Correlation considers:

```text
Device
Alert Type
Time Window
Related Symptoms
```

Related alerts are grouped into an incident.

---

## Step 3 — Incident Prioritization

The incident is analyzed and assigned an impact score between **1 and 10**.

Higher-impact incidents receive higher priority.

This allows operators to investigate the most important network problems first.

---

## Step 4 — Runbook Retrieval

The incident information is converted into a semantic search query.

The RAG engine then:

1. Generates an embedding using Gemini.
2. Searches the FAISS vector database.
3. Retrieves the most relevant runbook chunks.
4. Passes the retrieved context to Gemini.

This provides the LLM with relevant operational knowledge before generating a recommendation.

---

## Step 5 — Recommendation or Escalation

If relevant runbook information is found:

```text
Incident
   ↓
Relevant Runbook
   ↓
Recommended Actions
   ↓
Runbook Citation
```

If no sufficiently relevant information is found:

```text
Incident
   ↓
No Reliable Runbook Match
   ↓
Human Escalation
   ↓
Incident Context Provided
```

---

# 📚 Available Runbooks

The project currently contains four troubleshooting runbooks.

| Runbook                  | Purpose                                         |
| ------------------------ | ----------------------------------------------- |
| `link_down.txt`          | Troubleshooting network/interface link failures |
| `device_unreachable.txt` | Troubleshooting unreachable network devices     |
| `high_latency.txt`       | Investigating network latency problems          |
| `auth_failure.txt`       | Troubleshooting authentication failures         |

These runbooks are used as the knowledge source for the RAG pipeline.

---

# 🛠️ Tech Stack

| Component            | Technology                    |
| -------------------- | ----------------------------- |
| Backend              | FastAPI                       |
| Programming Language | Python                        |
| LLM                  | Google Gemini                 |
| Embeddings           | Gemini `gemini-embedding-001` |
| Vector Database      | FAISS                         |
| Frontend             | HTML, CSS, JavaScript         |
| Configuration        | `.env`                        |
| API                  | REST                          |

---

# 📂 Project Structure

```text
telecom-triage-assistant/
│
├── app.py
│   └── Main FastAPI application
│
├── requirements.txt
│   └── Python dependencies
│
├── README.md
│   └── Project documentation
│
├── data/
│   └── runbooks/
│       ├── link_down.txt
│       ├── device_unreachable.txt
│       ├── high_latency.txt
│       └── auth_failure.txt
│
├── src/
│   ├── rag_engine.py
│   │   └── RAG pipeline, embeddings and FAISS retrieval
│   │
│   ├── alert_processor.py
│   │   └── Alert correlation and grouping logic
│   │
│   ├── triage_engine.py
│   │   └── Incident analysis and recommendations
│   │
│   └── models.py
│       └── Application data models
│
└── templates/
    └── index.html
        └── Web dashboard
```

---

# 🚀 Getting Started

## Prerequisites

Make sure the following are installed:

* Python 3.9+
* pip
* A Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/kondurprabhakarnuthanraju/telecom-triage-assistant.git
```

Navigate into the project:

```bash
cd telecom-triage-assistant
```

---

## 2. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

---

## 3. Configure API Keys

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your-api-key-here
GOOGLE_API_KEY=your-api-key-here
```

Replace the placeholder values with your actual API keys.

> ⚠️ **Security:** Never commit your `.env` file or API keys to GitHub.

Add the following to `.gitignore` if it is not already present:

```gitignore
.env
__pycache__/
*.pyc
```

---

# ▶️ Running the Application

Start the FastAPI application:

```bash
python app.py
```

The application will start on:

```text
http://localhost:8000
```

Open the URL in your browser:

```text
http://localhost:8000
```

---

# 🧪 Sample Alerts

The application provides an endpoint for generating sample network alerts:

```text
/api/generate-sample-alerts
```

This can be used to demonstrate the system without requiring a live network monitoring platform.

The generated alerts can be processed through the same incident grouping and triage pipeline.

---

# 🔌 API Overview

The FastAPI backend exposes endpoints for interacting with the incident triage system.

### Generate Sample Alerts

```http
GET /api/generate-sample-alerts
```

Generates sample network alerts for demonstration and testing.

### Web Application

```http
GET /
```

Loads the web-based network incident triage dashboard.

> Additional endpoints can be added as the project evolves.

---

# 🧩 Core Components

## `alert_processor.py`

Responsible for transforming raw alerts into meaningful incident groups.

Main responsibilities include:

* Alert correlation
* Duplicate detection
* Time-window analysis
* Device-based grouping
* Noise identification

---

## `rag_engine.py`

Implements the Retrieval-Augmented Generation pipeline.

Responsibilities include:

* Loading runbooks
* Splitting runbooks into chunks
* Generating embeddings
* Building the FAISS index
* Performing semantic search
* Returning relevant runbook content

---

## `triage_engine.py`

Responsible for analyzing incidents and generating recommendations.

Responsibilities include:

* Incident prioritization
* Runbook context processing
* Gemini-based reasoning
* Recommendation generation
* Citation generation
* Escalation decisions

---

## `models.py`

Contains the application's data models used for:

* Alerts
* Incidents
* Recommendations
* Runbook results
* API responses

---

# 🔐 Grounding and Reliability

One of the main design principles of this project is **grounded AI reasoning**.

Instead of allowing the LLM to independently invent troubleshooting procedures, the system first retrieves relevant operational knowledge.

```text
                    ┌───────────────┐
                    │    Incident   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ RAG Retrieval │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Runbooks    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Gemini     │
                    └───────┬───────┘
                            │
                            ▼
                  Grounded Recommendation
```

This approach improves explainability and reduces unsupported recommendations.

---

# 🎯 Why This Approach Works

## 1. Grounding

Every recommendation is based on retrieved runbook information and provides a source citation.

This makes recommendations easier for network engineers to verify.

---

## 2. Noise Reduction

Duplicate and related alerts are grouped into incidents instead of overwhelming the operator with individual alerts.

---

## 3. Intelligent Escalation

The system does not pretend to know the answer when the available runbooks do not contain sufficient information.

Instead, it escalates the incident with relevant context.

---

## 4. Explainability

Operators can see:

```text
Incident
   ↓
Impact
   ↓
Retrieved Runbook
   ↓
Recommended Actions
   ↓
Source Citation
```

This provides transparency into why an action was recommended.

---

## 5. Speed

FAISS provides efficient vector similarity search, while the index is prepared during application startup.

This allows the system to perform rapid runbook retrieval during incident processing.

---

# 💡 Example Use Case

Consider the following incoming alerts:

```text
10:30:01  R01  Interface Gi0/1 Down
10:30:04  R01  Link Failure
10:30:08  R01  Packet Loss
10:30:15  R01  Device Unreachable
```

A traditional monitoring system might display four separate alerts.

The Network Incident Triage Assistant can correlate these alerts into:

```text
INC-001

Title:
R01 Connectivity Failure

Impact:
9/10

Related Alerts:
- Interface Gi0/1 Down
- Link Failure
- Packet Loss
- Device Unreachable
```

The RAG engine searches the available runbooks and retrieves relevant troubleshooting procedures.

Gemini then produces a grounded recommendation such as:

```text
Recommended Actions:

1. Verify the physical connectivity of the affected interface.
2. Check the operational state of the interface.
3. Review recent interface errors.
4. Validate device reachability after restoring the link.

Source:
link_down.txt
device_unreachable.txt
```

If no relevant runbook is available, the system instead produces an escalation recommendation.

---

# 🎥 Demo Video

A 5-minute demonstration video showing the complete workflow will be provided here:

**[Demo Video – Coming Soon]**

The demo will cover:

1. Starting the application
2. Generating sample alerts
3. Alert grouping
4. Incident creation
5. Impact prioritization
6. RAG retrieval
7. Runbook-grounded recommendations
8. Citations
9. Escalation when no runbook matches

---

# 🏆 Project Highlights

| Capability          | Implementation                              |
| ------------------- | ------------------------------------------- |
| Alert correlation   | Device, type and time-window based grouping |
| Incident management | Automatic incident creation                 |
| Prioritization      | 1–10 impact scoring                         |
| Semantic retrieval  | Gemini embeddings                           |
| Vector search       | FAISS                                       |
| Knowledge grounding | Network runbooks                            |
| AI reasoning        | Google Gemini                               |
| Explainability      | Runbook citations                           |
| Unknown scenarios   | Human escalation                            |
| User interface      | HTML/CSS/JavaScript                         |
| Backend             | FastAPI                                     |

---

# 🔮 Future Improvements

Potential improvements include:

* Real-time integration with network monitoring systems
* SNMP/syslog integration
* Prometheus/Grafana integration
* Historical incident learning
* More advanced alert correlation
* Network topology awareness
* Automated remediation with approval workflows
* Role-based access control
* Authentication and authorization
* Persistent incident storage
* PostgreSQL integration
* Redis-based event processing
* Advanced observability and logging
* Incident timeline visualization
* Feedback-based recommendation improvement

---

# ⚠️ Limitations

This project is designed as a prototype/demo for network incident triage.

Current limitations include:

* The runbook knowledge base is limited to four runbooks.
* Alert correlation is based on predefined attributes and rules.
* The system does not directly modify network devices.
* Recommendations should be reviewed by a qualified network operator before execution.
* Sample alerts are used for demonstration.
* Production deployment would require additional authentication, monitoring, security controls, persistence, and operational safeguards.

---

# 📋 Submission Details

**Track:** PS07 – Telecom Network Incident Triage Assistant

**Event:** NexusTiQ 24

**Project:** Network Incident Triage Assistant

**Repository:**

https://github.com/kondurprabhakarnuthanraju/telecom-triage-assistant

---

# 👨‍💻 Built For

**NexusTiQ 24**

Built with:

* Python
* FastAPI
* Google Gemini
* Gemini Embeddings
* FAISS
* HTML
* CSS
* JavaScript

---

## ⭐ Project Philosophy

> **Reduce alert noise. Ground recommendations in operational knowledge. Prioritize what matters. Escalate when the system does not know.**

The Network Incident Triage Assistant is designed around these four principles to help network operations teams move from **raw alerts → meaningful incidents → actionable and explainable decisions**.
