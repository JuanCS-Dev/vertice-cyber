# VERTICE CYBER - DIAGRAMAS MERMAID DOS AGENTES

> **Versão:** 1.0.0  
> **Data:** 17 Janeiro 2026  
> **Uso:** Copy/paste no Mermaid Live Editor ou geradores de imagem

---

## 🏛️ AGENT 01: ETHICAL MAGISTRATE

### Diagrama 1.1 - Fluxo de Validação Ética (7 Fases)

```mermaid
flowchart TD
    Start([Ação Solicitada]) --> Emit[Emite Evento:<br/>VALIDATION_REQUESTED]
    Emit --> Phase1{Fase 1:<br/>Governance Check}
    
    Phase1 -->|Dangerous Keywords| HumanReview[🚨 HUMAN REVIEW<br/>REQUIRED]
    Phase1 -->|Clean| Phase2{Fase 2:<br/>Always Require<br/>Approval?}
    
    Phase2 -->|Yes| HumanReview
    Phase2 -->|No| Phase3{Fase 3:<br/>Privacy Check}
    
    Phase3 -->|Has PII| Conditional[✅ APPROVED WITH<br/>CONDITIONS<br/>- Mask PII in logs<br/>- Privacy safeguards]
    Phase3 -->|No PII| Phase4{Fase 4:<br/>Fairness Check}
    
    Phase4 -->|Bias Detected| Rejected1[❌ REJECTED<br/>BY_ETHICS]
    Phase4 -->|Fair| Phase5{Fase 5:<br/>Transparency<br/>Check}
    
    Phase5 -->|Not Transparent| Rejected2[❌ REJECTED<br/>BY_GOVERNANCE]
    Phase5 -->|Transparent| Phase6{Fase 6:<br/>Accountability<br/>Check}
    
    Phase6 -->|No Audit Trail| Rejected3[❌ REJECTED<br/>BY_GOVERNANCE]
    Phase6 -->|Has Audit| Phase7{Fase 7:<br/>Security Check}
    
    Phase7 -->|Insecure| Rejected4[❌ REJECTED<br/>BY_SECURITY]
    Phase7 -->|Secure| Approved[✅ APPROVED]
    
    HumanReview --> Wait[⏳ Aguarda Aprovação<br/>Timeout: 5-60s]
    Wait -->|Approved| Approved
    Wait -->|Rejected| Rejected1
    Wait -->|Timeout| Rejected2
    
    Approved --> Store[💾 Store Decision<br/>in Memory]
    Conditional --> Store
    Rejected1 --> Store
    Rejected2 --> Store
    Rejected3 --> Store
    Rejected4 --> Store
    
    Store --> EmitComplete[Emite Evento:<br/>VALIDATION_COMPLETED]
    EmitComplete --> End([Return Decision])
    
    style HumanReview fill:#ff6b6b
    style Approved fill:#51cf66
    style Conditional fill:#4dabf7
    style Rejected1 fill:#ff6b6b
    style Rejected2 fill:#ff6b6b
    style Rejected3 fill:#ff6b6b
    style Rejected4 fill:#ff6b6b
```

### Diagrama 1.2 - Arquitetura do Magistrate

```mermaid
graph TB
    subgraph "Ethical Magistrate Agent"
        Input[MCP Tool Call:<br/>ethical_validate] --> Validator[EthicalMagistrate<br/>Validator]
        
        Validator --> Pipeline[7-Phase Pipeline]
        
        Pipeline --> Identity[Identity<br/>Validation]
        Pipeline --> ATLAS[MITRE ATLAS<br/>Check]
        Pipeline --> Anomaly[Behavioral<br/>Anomaly Detection]
        Pipeline --> RateLimit[Rate Limiting<br/>Per Agent]
        
        Identity --> Decision{Decision<br/>Engine}
        ATLAS --> Decision
        Anomaly --> Decision
        RateLimit --> Decision
        
        Decision --> Memory[(Agent<br/>Memory)]
        Decision --> EventBus[Event Bus]
        
        EventBus --> Listeners[Event Listeners:<br/>- OSINT Hunter<br/>- Threat Prophet<br/>- Immune System]
    end
    
    subgraph "External Systems"
        Decision -->|Human Review| Slack[Slack/Email<br/>Notification]
        Decision -->|Audit| AuditLog[(Audit Log<br/>Immutable)]
    end
    
    style Input fill:#4dabf7
    style Decision fill:#ffd43b
    style Memory fill:#ff6b6b
    style EventBus fill:#51cf66
```

### Diagrama 1.3 - Sequência de Validação com Identity

```mermaid
sequenceDiagram
    participant Agent as Calling Agent
    participant MCP as MCP Server
    participant EM as Ethical Magistrate
    participant Identity as Identity Validator
    participant ATLAS as MITRE ATLAS
    participant Human as Human Reviewer
    
    Agent->>MCP: ethical_validate(action, context, actor)
    MCP->>EM: validate(action, context, actor)
    
    EM->>Identity: verify_agent_identity(actor)
    
    alt Identity Invalid
        Identity-->>EM: IDENTITY_MISMATCH
        EM-->>MCP: REJECT - Identity Invalid
        MCP-->>Agent: Decision: REJECTED
    else Identity Valid
        Identity-->>EM: VERIFIED
        
        EM->>ATLAS: check_techniques(action)
        ATLAS-->>EM: Matched: T1078, T1190
        
        alt High Severity ATLAS Technique
            EM->>Human: Request Approval (Slack)
            Human-->>EM: Approved/Rejected
        end
        
        EM->>EM: Calculate Risk Score
        EM-->>MCP: Decision + Risk Score
        MCP-->>Agent: Decision: APPROVED/REJECTED
    end
```

---

## 🔍 AGENT 02: OSINT HUNTER

### Diagrama 2.1 - Pipeline de Investigação OSINT

```mermaid
flowchart LR
    Start([Target:<br/>Email/Domain/IP]) --> Detect{Detect<br/>Target Type}
    
    Detect -->|Email| EmailFlow[Email Investigation]
    Detect -->|Domain| DomainFlow[Domain Investigation]
    Detect -->|IP| IPFlow[IP Investigation]
    
    subgraph "Email Investigation"
        EmailFlow --> HIBP[HaveIBeenPwned<br/>Breach Check]
        EmailFlow --> ExtractDomain[Extract Domain<br/>from Email]
        HIBP --> BreachData[(Breach Data)]
        ExtractDomain --> DomainFlow
    end
    
    subgraph "Domain Investigation"
        DomainFlow --> Shodan[Shodan Search<br/>Exposed Services]
        DomainFlow --> Censys[Censys Search<br/>SSL Certificates]
        DomainFlow --> DNS[DNS Recon<br/>Subdomains]
        DomainFlow --> WebRecon[Web Recon<br/>Wayback, Github]
        DomainFlow --> Dorks[Google Dorking<br/>6 Categories]
        
        Shodan --> Findings1[(IoT Devices<br/>Open Ports)]
        Censys --> Findings2[(SSL Certs<br/>Expired Certs)]
        DNS --> Findings3[(Subdomains<br/>MX Records)]
        WebRecon --> Findings4[(Historical Data<br/>Code Leaks)]
        Dorks --> Findings5[(Sensitive Files<br/>Exposed Dirs)]
    end
    
    subgraph "IP Investigation"
        IPFlow --> Geolocation[IP Geolocation<br/>AS Lookup]
        IPFlow --> Reputation[IP Reputation<br/>Blocklists]
        
        Geolocation --> Findings6[(Location<br/>ISP Info)]
        Reputation --> Findings7[(Blacklist Status<br/>Abuse Reports)]
    end
    
    BreachData --> Correlate[Correlation Engine<br/>Attack Path Analysis]
    Findings1 --> Correlate
    Findings2 --> Correlate
    Findings3 --> Correlate
    Findings4 --> Correlate
    Findings5 --> Correlate
    Findings6 --> Correlate
    Findings7 --> Correlate
    
    Correlate --> RiskScore{Calculate<br/>Risk Score}
    RiskScore --> Report[OSINT Report<br/>with Findings]
    Report --> Cache[(Cache 1h<br/>in Memory)]
    Cache --> End([Return Report])
    
    style HIBP fill:#ff6b6b
    style Shodan fill:#ffd43b
    style Censys fill:#4dabf7
    style Correlate fill:#51cf66
```

### Diagrama 2.2 - Continuous Monitoring Loop

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Scanning: New Target Added
    Scanning --> Processing: Data Collected
    Processing --> Correlation: Parse Results
    Correlation --> Alerting: Risk > Threshold
    Correlation --> Sleeping: Risk < Threshold
    
    Alerting --> EventEmit: Emit OSINT_BREACH_DETECTED
    EventEmit --> Sleeping
    
    Sleeping --> Idle: Wait 1 hour
    
    state Scanning {
        [*] --> HIBP_Check
        HIBP_Check --> Shodan_Scan
        Shodan_Scan --> Censys_Scan
        Censys_Scan --> DNS_Enum
        DNS_Enum --> [*]
    }
    
    state Processing {
        [*] --> Parse_Breaches
        Parse_Breaches --> Parse_Services
        Parse_Services --> Parse_Subdomains
        Parse_Subdomains --> [*]
    }
    
    note right of Alerting
        Alert Triggers:
        - New breach detected
        - New exposed service
        - Risk score increased
    end note
```

### Diagrama 2.3 - Correlation Engine (Attack Path)

```mermaid
graph TD
    subgraph "Input: Multiple OSINT Findings"
        F1[Email in Breach:<br/>LinkedIn 2021]
        F2[GitHub Leak:<br/>API Keys]
        F3[Subdomain:<br/>dev.example.com]
        F4[Exposed Port:<br/>SSH on 22]
        F5[Weak SSL Cert:<br/>Self-signed]
    end
    
    F1 --> Graph[NetworkX<br/>Directed Graph]
    F2 --> Graph
    F3 --> Graph
    F4 --> Graph
    F5 --> Graph
    
    Graph --> Paths{Find Attack<br/>Chains}
    
    Paths --> Chain1[Chain 1:<br/>Email → GitHub → API → Dev Server]
    Paths --> Chain2[Chain 2:<br/>Subdomain → Weak SSL → MITM]
    Paths --> Chain3[Chain 3:<br/>Port 22 → SSH Brute Force]
    
    Chain1 --> Score1[Risk: 85/100<br/>Critical]
    Chain2 --> Score2[Risk: 65/100<br/>High]
    Chain3 --> Score3[Risk: 45/100<br/>Medium]
    
    Score1 --> Final[Composite Risk:<br/>85/100]
    Score2 --> Final
    Score3 --> Final
    
    Final --> Map[Threat Map:<br/>Graph + Paths + Score]
    
    style F1 fill:#ff6b6b
    style F2 fill:#ff6b6b
    style Chain1 fill:#ff6b6b
    style Score1 fill:#ff6b6b
    style Map fill:#51cf66
```

---

## 🔮 AGENT 03: THREAT PROPHET

### Diagrama 3.1 - Predictive Threat Analysis

```mermaid
flowchart TD
    Start([Telemetry Events<br/>from System]) --> Detect[Detection Layer]
    
    subgraph "Multi-Layer Detection"
        Detect --> Layer1[Layer 1:<br/>Signature-Based<br/>YARA, Snort Rules]
        Detect --> Layer2[Layer 2:<br/>Anomaly-Based<br/>ML Model]
        Detect --> Layer3[Layer 3:<br/>Behavioral Analysis<br/>UEBA]
        Detect --> Layer4[Layer 4:<br/>Agent Compromise<br/>Memory Poisoning]
        
        Layer1 --> Known[Known Threats]
        Layer2 --> Unknown[Unknown Threats]
        Layer3 --> APT[APT Campaigns]
        Layer4 --> AgentThreats[Compromised Agents]
    end
    
    Known --> Map[MITRE Mapping]
    Unknown --> Map
    APT --> Map
    AgentThreats --> Map
    
    subgraph "MITRE Dual Framework"
        Map --> ATT&CK[ATT&CK v18<br/>Enterprise Techniques]
        Map --> ATLAS[ATLAS<br/>AI/ML Techniques]
        
        ATT&CK --> TTP1[T1078: Valid Accounts<br/>T1190: Exploit Public App]
        ATLAS --> TTP2[AML.T0043: Memory Poisoning<br/>AML.T0051: LLM Jailbreak]
    end
    
    TTP1 --> Predict[ML Prediction Model<br/>LSTM Neural Network]
    TTP2 --> Predict
    
    Predict --> NextTechniques[Predicted Next Techniques:<br/>1. T1059: Command Injection<br/>2. T1071: App Layer Protocol<br/>3. T1048: Exfiltration]
    
    NextTechniques --> IOC[IOC Generator]
    
    subgraph "IOC Generation"
        IOC --> YARA[YARA Rules]
        IOC --> Sigma[Sigma Rules<br/>SIEM]
        IOC --> Suricata[Suricata Rules<br/>Network IDS]
        IOC --> Custom[Custom Indicators]
    end
    
    YARA --> Deploy[Deploy to<br/>Detection Systems]
    Sigma --> Deploy
    Suricata --> Deploy
    Custom --> Deploy
    
    Deploy --> Hunt[Automated<br/>Threat Hunting]
    Hunt --> End([Continuous Loop])
    
    style Layer4 fill:#ff6b6b
    style AgentThreats fill:#ff6b6b
    style ATLAS fill:#ffd43b
    style Predict fill:#51cf66
```

### Diagrama 3.2 - LSTM Threat Sequence Prediction

```mermaid
graph LR
    subgraph "Training Data: APT Campaigns"
        C1[APT29 Campaign:<br/>T1078 → T1003 → T1021 → T1071]
        C2[APT28 Campaign:<br/>T1566 → T1204 → T1059 → T1048]
        C3[Lazarus Campaign:<br/>T1190 → T1505 → T1053 → T1567]
    end
    
    C1 --> LSTM[LSTM Model<br/>128 units, 2 layers]
    C2 --> LSTM
    C3 --> LSTM
    
    LSTM --> Train[Training:<br/>50 epochs<br/>Validation Split: 20%]
    
    Train --> Model[(Trained Model<br/>Accuracy: 87%)]
    
    subgraph "Real-time Prediction"
        Current[Current Sequence:<br/>T1078 → T1003]
        Current --> Model
        Model --> Predict[Predicted Next:<br/>T1021 (80% prob)<br/>T1059 (65% prob)]
        
        Predict --> Proactive[Proactive Defense:<br/>- Enable T1021 detection<br/>- Monitor lateral movement<br/>- Alert SOC team]
    end
    
    style LSTM fill:#4dabf7
    style Model fill:#51cf66
    style Proactive fill:#ffd43b
```

### Diagrama 3.3 - ATT&CK Navigator Integration

```mermaid
flowchart TD
    Start([Detected Techniques]) --> Coverage[Calculate Detection<br/>Coverage]
    
    Coverage --> Layer[Generate ATT&CK<br/>Navigator Layer]
    
    subgraph "ATT&CK Matrix Heatmap"
        Layer --> TA0001[Initial Access<br/>🟢 90% Coverage]
        Layer --> TA0002[Execution<br/>🟡 70% Coverage]
        Layer --> TA0003[Persistence<br/>🔴 40% Coverage]
        Layer --> TA0004[Privilege Escalation<br/>🟢 85% Coverage]
        Layer --> TA0005[Defense Evasion<br/>🟡 60% Coverage]
        Layer --> TA0006[Credential Access<br/>🟢 95% Coverage]
        Layer --> TA0007[Discovery<br/>🟡 75% Coverage]
        Layer --> TA0008[Lateral Movement<br/>🔴 35% Coverage]
        Layer --> TA0009[Collection<br/>🟡 65% Coverage]
        Layer --> TA0010[Exfiltration<br/>🔴 30% Coverage]
        Layer --> TA0011[C&C<br/>🟢 80% Coverage]
    end
    
    TA0001 --> Gaps{Identify<br/>Coverage Gaps}
    TA0002 --> Gaps
    TA0003 --> Gaps
    TA0004 --> Gaps
    TA0005 --> Gaps
    TA0006 --> Gaps
    TA0007 --> Gaps
    TA0008 --> Gaps
    TA0009 --> Gaps
    TA0010 --> Gaps
    TA0011 --> Gaps
    
    Gaps --> Priority[Prioritize Gaps:<br/>1. Lateral Movement<br/>2. Exfiltration<br/>3. Persistence]
    
    Priority --> Recommend[Recommend:<br/>- New detection rules<br/>- Purple team tests<br/>- Tool improvements]
    
    Recommend --> End([Export Layer JSON])
    
    style TA0001 fill:#51cf66
    style TA0003 fill:#ff6b6b
    style TA0008 fill:#ff6b6b
    style TA0010 fill:#ff6b6b
```

---

## 🛡️ AGENT 05-07: IMMUNE SYSTEM TRIO

### Diagrama 5.1 - Biological Immune System Architecture

```mermaid
graph TB
    subgraph "Threat Entry Point"
        Antigen[Antigen:<br/>Malware, Intrusion,<br/>Agent Compromise]
    end
    
    Antigen --> Sentinel[Sentinel Prime<br/>T-Cells - Detection]
    
    subgraph "Sentinel Prime - T-Cell Detection"
        Sentinel --> Recognize{Recognize<br/>Antigen?}
        
        Recognize -->|Known Threat| Memory[Query Memory Cells:<br/>Past Response]
        Recognize -->|Unknown Threat| Analyze[Analyze Threat<br/>via Watcher]
        
        Memory --> MemoryDB[(Memory Coordinator:<br/>Past Attacks DB)]
        MemoryDB --> Response1[Immediate Response<br/>Based on History]
    end
    
    Analyze --> Watcher[The Watcher<br/>B-Cells - Analysis]
    
    subgraph "The Watcher - B-Cell Analysis"
        Watcher --> Classify{Classify<br/>Threat Type}
        
        Classify --> T1[Type 1:<br/>Malware]
        Classify --> T2[Type 2:<br/>Network Intrusion]
        Classify --> T3[Type 3:<br/>Agent Compromise]
        Classify --> T4[Type 4:<br/>Data Exfiltration]
        
        T1 --> Antibody1[Generate Antibody:<br/>Isolate Endpoint]
        T2 --> Antibody2[Generate Antibody:<br/>Block IP/Port]
        T3 --> Antibody3[Generate Antibody:<br/>Killswitch Agent]
        T4 --> Antibody4[Generate Antibody:<br/>Revoke Credentials]
    end
    
    Antibody1 --> Coordinator[Immune Coordinator<br/>Orchestration]
    Antibody2 --> Coordinator
    Antibody3 --> Coordinator
    Antibody4 --> Coordinator
    Response1 --> Coordinator
    
    subgraph "Immune Coordinator - Orchestration"
        Coordinator --> Confidence{Confidence<br/>> 80%?}
        
        Confidence -->|Yes| AutoResponse[Autonomous Response<br/>< 100ms]
        Confidence -->|No| Escalate[Escalate to Human<br/>SOC Team]
        
        AutoResponse --> Execute[Execute Mitigation]
        Escalate --> HumanDecision{Human<br/>Decision}
        HumanDecision -->|Approve| Execute
        HumanDecision -->|Reject| Log
    end
    
    Execute --> Verify[Verify Mitigation<br/>Successful?]
    
    Verify -->|Success| Learn[Memory Cells:<br/>Learn Response]
    Verify -->|Failure| Adapt[Adapt Response]
    
    Learn --> MemoryDB
    Adapt --> Coordinator
    
    Verify --> Log[(Audit Log:<br/>Immutable Trail)]
    
    style Sentinel fill:#4dabf7
    style Watcher fill:#ffd43b
    style Coordinator fill:#51cf66
    style AutoResponse fill:#ff6b6b
```

### Diagrama 5.2 - Agent Compromise Detection (< 100ms)

```mermaid
sequenceDiagram
    participant Agent as Suspicious Agent
    participant Sentinel as Sentinel Prime
    participant Watcher as The Watcher
    participant Coordinator as Immune Coordinator
    participant Action as Autonomous Action
    
    rect rgb(255, 200, 200)
        Note over Agent: Anomalous Behavior Detected
        Agent->>Sentinel: Tool Call: access_sensitive_data()
    end
    
    rect rgb(200, 220, 255)
        Note over Sentinel: T-Cell Detection (< 20ms)
        Sentinel->>Sentinel: Check Behavioral Baseline
        Sentinel->>Sentinel: Detect Drift: +450%
        Sentinel->>Sentinel: Memory Poisoning Patterns
    end
    
    Sentinel->>Watcher: Analyze: Possible Compromise
    
    rect rgb(255, 255, 200)
        Note over Watcher: B-Cell Analysis (< 30ms)
        Watcher->>Watcher: Check Recent Tool Chain:<br/>unusual_sequence()
        Watcher->>Watcher: Check Access Patterns:<br/>after_hours + new_resources
        Watcher->>Watcher: Calculate Threat Score: 0.92
    end
    
    Watcher->>Coordinator: Threat Confirmed:<br/>Agent Compromise (92%)
    
    rect rgb(200, 255, 200)
        Note over Coordinator: Orchestration (< 50ms)
        Coordinator->>Coordinator: Query Memory: Similar Attack?
        Coordinator->>Coordinator: Found: APT29 Pattern
        Coordinator->>Coordinator: Confidence: 92% > 80%
        Coordinator->>Coordinator: Decision: AUTONOMOUS
    end
    
    Coordinator->>Action: Execute: Killswitch Agent
    
    rect rgb(255, 100, 100)
        Note over Action: Autonomous Response
        Action->>Agent: REVOKE all credentials
        Action->>Agent: TERMINATE active sessions
        Action->>Agent: ISOLATE from network
        Action->>Agent: FREEZE agent state
    end
    
    Action->>Coordinator: Mitigation Complete
    Coordinator->>Coordinator: Store in Memory Cells
    Coordinator->>Coordinator: Log to Audit Trail
    
    Note over Sentinel,Coordinator: Total Time: 87ms ✅
```

### Diagrama 5.3 - Self-Healing Process

```mermaid
stateDiagram-v2
    [*] --> Healthy: System Normal
    
    Healthy --> Infected: Threat Detected
    
    state Infected {
        [*] --> Isolate
        Isolate --> Analyze
        Analyze --> Remediate
        
        state Analyze {
            [*] --> IdentifyRoot
            IdentifyRoot --> FindVectors
            FindVectors --> [*]
        }
        
        state Remediate {
            [*] --> RemoveMalware
            RemoveMalware --> PatchVuln
            PatchVuln --> RestoreConfig
            RestoreConfig --> [*]
        }
        
        Remediate --> Verify
    }
    
    Verify --> Healthy: Verification Passed
    Verify --> Infected: Verification Failed
    
    Healthy --> Learning: Store Pattern
    Learning --> [*]
    
    note right of Infected
        Autonomous Actions:
        - Isolate affected systems
        - Kill malicious processes
        - Revoke compromised creds
        - Restore from backup
    end note
    
    note right of Learning
        Memory Cells Store:
        - Attack signature
        - Response that worked
        - Time to remediate
        - Lessons learned
    end note
```

---

## ⚔️ AGENT 08: WARGAME EXECUTOR (Purple Team)

### Diagrama 8.1 - Continuous Purple Teaming Cycle

```mermaid
flowchart TD
    Start([24/7 Loop Start]) --> Select[Select Adversary<br/>to Emulate]
    
    subgraph "Adversary Selection"
        Select --> DB[(Adversary DB:<br/>APT29, APT28,<br/>Lazarus, etc)]
        DB --> Profile[Load TTP Profile]
    end
    
    Profile --> RedTeam[Red Team Phase]
    
    subgraph "Red Team - Attack Execution"
        RedTeam --> Atomic[Atomic Red Team<br/>Test Selection]
        
        Atomic --> T1[Execute: T1078<br/>Valid Accounts]
        Atomic --> T2[Execute: T1003<br/>Credential Dumping]
        Atomic --> T3[Execute: T1021<br/>Remote Services]
        
        T1 --> Results1[Capture Results:<br/>- Success/Fail<br/>- Artifacts<br/>- IOCs]
        T2 --> Results2[Capture Results]
        T3 --> Results3[Capture Results]
    end
    
    Results1 --> BlueTeam[Blue Team Phase]
    Results2 --> BlueTeam
    Results3 --> BlueTeam
    
    subgraph "Blue Team - Validation"
        BlueTeam --> Check1{Was T1078<br/>Detected?}
        BlueTeam --> Check2{Was T1003<br/>Detected?}
        BlueTeam --> Check3{Was T1021<br/>Detected?}
        
        Check1 -->|Yes| Detected1[✅ Detection OK]
        Check1 -->|No| Gap1[❌ Detection Gap]
        
        Check2 -->|Yes| Detected2[✅ Detection OK]
        Check2 -->|No| Gap2[❌ Detection Gap]
        
        Check3 -->|Yes| Detected3[✅ Detection OK]
        Check3 -->|No| Gap3[❌ Detection Gap]
        
        Check1 --> Prevent1{Was T1078<br/>Prevented?}
        Check2 --> Prevent2{Was T1003<br/>Prevented?}
        Check3 --> Prevent3{Was T1021<br/>Prevented?}
        
        Prevent1 -->|Yes| Prevented1[✅ Prevention OK]
        Prevent1 -->|No| GapP1[❌ Prevention Gap]
        
        Prevent2 -->|Yes| Prevented2[✅ Prevention OK]
        Prevent2 -->|No| GapP2[❌ Prevention Gap]
        
        Prevent3 -->|Yes| Prevented3[✅ Prevention OK]
        Prevent3 -->|No| GapP3[❌ Prevention Gap]
    end
    
    Gap1 --> Gaps[Consolidate Gaps]
    Gap2 --> Gaps
    Gap3 --> Gaps
    GapP1 --> Gaps
    GapP2 --> Gaps
    GapP3 --> Gaps
    
    Gaps --> AutoFix{Can Auto-Fix?}
    
    AutoFix -->|Yes| Deploy[Deploy Fix:<br/>- New Sigma rule<br/>- Update firewall<br/>- Patch system]
    AutoFix -->|No| Ticket[Create Ticket<br/>for SOC Team]
    
    Deploy --> Metrics[Generate Metrics]
    Ticket --> Metrics
    
    subgraph "Threat Resilience Metrics"
        Metrics --> Coverage[Detection Coverage:<br/>78/100 techniques]
        Metrics --> MTTD[Mean Time to Detect:<br/>3.2 minutes]
        Metrics --> MTTR[Mean Time to Respond:<br/>12.5 minutes]
        Metrics --> FP[False Positive Rate:<br/>2.1%]
    end
    
    Coverage --> Report[Purple Team Report]
    MTTD --> Report
    MTTR --> Report
    FP --> Report
    
    Report --> Wait[Wait 1 hour]
    Wait --> Start
    
    style Gap1 fill:#ff6b6b
    style Gap2 fill:#ff6b6b
    style Gap3 fill:#ff6b6b
    style Detected1 fill:#51cf66
    style Detected2 fill:#51cf66
    style Detected3 fill:#51cf66
```

### Diagrama 8.2 - CALDERA Integration (MITRE)

```mermaid
graph TB
    subgraph "CALDERA Platform"
        Operator[Purple Team<br/>Operator]
        Operator --> Planner[AI Planner:<br/>Autonomous Adversary]
        
        Planner --> KB[(Knowledge Base:<br/>ATT&CK Techniques)]
        KB --> Abilities[Abilities:<br/>500+ TTPs]
    end
    
    subgraph "Target Environment"
        Abilities --> Agent1[CALDERA Agent<br/>Windows Server]
        Abilities --> Agent2[CALDERA Agent<br/>Linux Server]
        Abilities --> Agent3[CALDERA Agent<br/>Kubernetes Pod]
        
        Agent1 --> Execute1[Execute T1078:<br/>Valid Accounts]
        Agent2 --> Execute2[Execute T1059:<br/>Command Injection]
        Agent3 --> Execute3[Execute T1610:<br/>Container Escape]
    end
    
    Execute1 --> Observe[Observation<br/>& Detection]
    Execute2 --> Observe
    Execute3 --> Observe
    
    subgraph "Blue Team Validation"
        Observe --> SIEM[SIEM Analysis:<br/>Splunk, ELK]
        Observe --> EDR[EDR Detection:<br/>CrowdStrike, etc]
        Observe --> IDS[Network IDS:<br/>Suricata, Zeek]
        
        SIEM --> Timeline[Attack Timeline<br/>Reconstruction]
        EDR --> Timeline
        IDS --> Timeline
    end
    
    Timeline --> Compare[Compare with<br/>Expected Detections]
    
    Compare --> Gaps[Gap Analysis]
    Gaps --> Feedback[Feedback to<br/>Immune System]
    
    Feedback --> Improve[Improve Detections:<br/>- New Sigma rules<br/>- Tuned ML models<br/>- Updated IOCs]
    
    Improve --> Planner
    
    style Planner fill:#4dabf7
    style Gaps fill:#ff6b6b
    style Improve fill:#51cf66
```

---

## 🔧 AGENT 09: PATCH VALIDATOR ML

### Diagrama 9.1 - Smart Vulnerability Prioritization

```mermaid
flowchart TD
    Start([Asset Scan Results]) --> Vulns[Discovered<br/>Vulnerabilities]
    
    Vulns --> Enrich[Enrich with<br/>Threat Intel]
    
    subgraph "Enrichment Sources"
        Enrich --> NVD[NVD Database:<br/>CVE Details]
        Enrich --> EPSS[EPSS API:<br/>Exploit Probability]
        Enrich --> KEV[KEV Catalog:<br/>Active Exploits]
        Enrich --> Asset[Asset Criticality:<br/>Business Impact]
        
        NVD --> Score1[CVSS v4.0<br/>Base Score]
        EPSS --> Score2[EPSS Score<br/>0-1]
        KEV --> Score3[KEV Status<br/>Boolean]
        Asset --> Score4[Criticality<br/>0-10]
    end
    
    Score1 --> Calc[Priority Calculator]
    Score2 --> Calc
    Score3 --> Calc
    Score4 --> Calc
    
    Calc --> Formula["Priority Score =<br/>(CVSS × 0.3) +<br/>(EPSS × 25) +<br/>(KEV × 30) +<br/>(Criticality) +<br/>(Exposure × 5)"]
    
    Formula --> Prioritized[Prioritized List]
    
    subgraph "Priority Tiers"
        Prioritized --> P0[P0 - Critical:<br/>Score > 80<br/>KEV + EPSS > 0.7]
        Prioritized --> P1[P1 - High:<br/>Score 60-80<br/>EPSS > 0.3]
        Prioritized --> P2[P2 - Medium:<br/>Score 40-60]
        Prioritized --> P3[P3 - Low:<br/>Score < 40]
    end
    
    P0 --> AutoPatch[Auto-Patch<br/>if ML Confidence > 0.95]
    P1 --> ValidateML[ML Validation]
    P2 --> Schedule[Schedule Patch]
    P3 --> Defer[Defer / Monitor]
    
    ValidateML --> Approve{ML Approves?}
    Approve -->|Yes| AutoPatch
    Approve -->|No| Manual[Manual Review]
    
    AutoPatch --> Verify[Verify Patch<br/>in Sandbox]
    Manual --> Verify
    
    Verify --> Deploy[Deploy to<br/>Production]
    
    style P0 fill:#ff6b6b
    style AutoPatch fill:#ffd43b
    style Deploy fill:#51cf66
```

### Diagrama 9.2 - ML Patch Compatibility Predictor

```mermaid
graph LR
    subgraph "Training Data"
        H1[Historical Patch:<br/>Success]
        H2[Historical Patch:<br/>Failed]
        H3[Historical Patch:<br/>Success]
        
        H1 --> Features1[Features:<br/>- Lines changed: 150<br/>- Files: 3<br/>- Uptime: 45 days<br/>- Vendor: Microsoft]
        
        H2 --> Features2[Features:<br/>- Lines changed: 2500<br/>- Files: 87<br/>- Uptime: 2 days<br/>- Vendor: Unknown]
        
        H3 --> Features3[Features:<br/>- Lines changed: 50<br/>- Files: 1<br/>- Uptime: 120 days<br/>- Vendor: RedHat]
    end
    
    Features1 --> XGB[XGBoost Model]
    Features2 --> XGB
    Features3 --> XGB
    
    XGB --> Train[Train:<br/>Accuracy: 94%<br/>Precision: 0.89<br/>Recall: 0.92]
    
    Train --> Model[(Trained Model)]
    
    subgraph "Real-time Prediction"
        NewPatch[New Patch:<br/>CVE-2026-12345]
        
        NewPatch --> Extract[Extract Features]
        Extract --> PatchFeatures[Features:<br/>- Lines: 200<br/>- Files: 5<br/>- System uptime: 60d<br/>- Vendor: Microsoft<br/>- Deps complexity: Low]
        
        PatchFeatures --> Model
        
        Model --> Predict[Prediction:<br/>Success Prob: 0.96]
        
        Predict --> Decision{Confidence<br/>> 0.95?}
        
        Decision -->|Yes| AutoApprove[✅ Auto-Approve<br/>& Schedule]
        Decision -->|No| HumanReview[👤 Human Review<br/>Required]
    end
    
    AutoApprove --> Sandbox[Test in Sandbox]
    HumanReview --> Sandbox
    
    Sandbox --> Production[Deploy to<br/>Production]
    
    style Model fill:#4dabf7
    style AutoApprove fill:#51cf66
```

### Diagrama 9.3 - Patch Validation Pipeline

```mermaid
sequenceDiagram
    participant Scanner as Vuln Scanner
    participant PV as Patch Validator ML
    participant NVD as NVD/EPSS/KEV
    participant ML as ML Model
    participant Sandbox as Sandbox Env
    participant Prod as Production
    
    Scanner->>PV: Found CVE-2026-12345
    
    PV->>NVD: Enrich CVE
    NVD-->>PV: CVSS: 9.8, EPSS: 0.85, KEV: True
    
    PV->>PV: Calculate Priority: 92 (P0)
    
    PV->>PV: Find available patch
    
    PV->>ML: Predict compatibility
    ML-->>PV: Success Prob: 0.97
    
    alt High Confidence (> 0.95)
        PV->>Sandbox: Deploy patch
        Sandbox->>Sandbox: Run tests (30min)
        Sandbox-->>PV: All tests passed ✅
        
        PV->>Prod: Schedule deployment
        Prod->>Prod: Apply patch
        Prod-->>PV: Patch applied successfully
        
        PV->>PV: Verify CVE is patched
        PV->>PV: Update ML model (feedback)
    else Low Confidence
        PV->>PV: Create manual review ticket
    end
```

---

## 🔐 AGENT 12: CYBERSEC BASIC (Pentest Automation)

### Diagrama 12.1 - Full Automated Pentest Pipeline

```mermaid
flowchart TD
    Start([Target: example.com]) --> Phase1[Phase 1:<br/>Reconnaissance]
    
    subgraph "Phase 1: Reconnaissance"
        Phase1 --> Nmap[Nmap Scan:<br/>Ports & Services]
        Phase1 --> Subfinder[Subfinder:<br/>Subdomain Enum]
        Phase1 --> Amass[Amass:<br/>Asset Discovery]
        Phase1 --> Httpx[Httpx:<br/>Web Probe]
        Phase1 --> Wayback[Wayback URLs:<br/>Historical Data]
        
        Nmap --> R1[(Open Ports:<br/>22, 80, 443, 3306)]
        Subfinder --> R2[(Subdomains:<br/>dev, api, admin)]
        Amass --> R3[(IPs:<br/>10 unique IPs)]
        Httpx --> R4[(Live Web:<br/>7 active sites)]
        Wayback --> R5[(URLs:<br/>850 historical)]
    end
    
    R1 --> Phase2[Phase 2:<br/>Vulnerability Scan]
    R2 --> Phase2
    R3 --> Phase2
    R4 --> Phase2
    R5 --> Phase2
    
    subgraph "Phase 2: Scanning"
        Phase2 --> Nuclei[Nuclei:<br/>9000+ Templates]
        Phase2 --> Ffuf[Ffuf:<br/>Directory Fuzzing]
        Phase2 --> SQLMap[SQLMap:<br/>SQL Injection]
        Phase2 --> XSS[XSS Scanner]
        
        Nuclei --> V1[(CVEs Found:<br/>- CVE-2021-44228<br/>- CVE-2023-12345)]
        Ffuf --> V2[(Exposed:<br/>/admin, /backup)]
        SQLMap --> V3[(SQLi:<br/>login.php?id=)]
        XSS --> V4[(XSS:<br/>search.php?q=)]
    end
    
    V1 --> Phase3{Phase 3:<br/>Exploitation}
    V2 --> Phase3
    V3 --> Phase3
    V4 --> Phase3
    
    subgraph "Phase 3: Safe Exploitation"
        Phase3 --> Check{Has Public<br/>Exploit?}
        
        Check -->|Yes| PoC[Run PoC<br/>Safe Mode]
        Check -->|No| Skip[Skip to Next]
        
        PoC --> Verify{Exploit<br/>Works?}
        
        Verify -->|Yes| Shell[Gain Access<br/>Reverse Shell]
        Verify -->|No| Skip
    end
    
    Shell --> Phase4[Phase 4:<br/>Post-Exploitation]
    Skip --> Report
    
    subgraph "Phase 4: Post-Exploitation"
        Phase4 --> PrivEsc[Privilege<br/>Escalation Check]
        Phase4 --> LatMove[Lateral<br/>Movement Check]
        Phase4 --> DataEx[Data<br/>Exfiltration Test]
        
        PrivEsc --> PE[Found: sudo<br/>misconfiguration]
        LatMove --> LM[Found: SSH keys<br/>to other hosts]
        DataEx --> DE[Found: DB access<br/>sensitive data]
    end
    
    PE --> Report[Phase 5:<br/>Report Generation]
    LM --> Report
    DE --> Report
    
    subgraph "Phase 5: Reporting"
        Report --> Executive[Executive Summary]
        Report --> Technical[Technical Details]
        Report --> MITRE[MITRE ATT&CK<br/>Mapping]
        Report --> Remediation[Remediation Steps]
        
        Executive --> Final[Final Report]
        Technical --> Final
        MITRE --> Final
        Remediation --> Final
    end
    
    Final --> End([Deliver Report])
    
    style V1 fill:#ff6b6b
    style Shell fill:#ffd43b
    style Final fill:#51cf66
```

### Diagrama 12.2 - Nuclei Template Automation

```mermaid
graph TB
    subgraph "Template Categories"
        All[All Templates:<br/>9000+]
        
        All --> Critical[Critical:<br/>cves/2024/, cves/2025/,<br/>exposures/configs/]
        All --> High[High:<br/>exposed-panels/,<br/>misconfigurations/]
        All --> Medium[Medium:<br/>default-logins/,<br/>exposed-tokens/]
        All --> Low[Low:<br/>technologies/,<br/>dns/]
    end
    
    Target[Target: example.com] --> Filter{Severity<br/>Filter}
    
    Filter -->|Critical Only| Critical
    Filter -->|High+| CriticalHigh[Critical + High]
    Filter -->|All| All
    
    Critical --> Nuclei[Nuclei Engine]
    CriticalHigh --> Nuclei
    All --> Nuclei
    
    Nuclei --> Execute[Execute Scan]
    
    Execute --> Results[Results:<br/>JSON Output]
    
    Results --> Parse[Parse Findings]
    
    subgraph "Categorization"
        Parse --> Cat1[Category: RCE<br/>Severity: Critical<br/>Count: 2]
        Parse --> Cat2[Category: SQLi<br/>Severity: High<br/>Count: 5]
        Parse --> Cat3[Category: XSS<br/>Severity: Medium<br/>Count: 12]
    end
    
    Cat1 --> Alert[🚨 Immediate Alert<br/>to SOC]
    Cat2 --> Ticket[Create Ticket<br/>P1 Priority]
    Cat3 --> Report[Add to Report]
    
    Alert --> Action[Automated<br/>Remediation?]
    
    Action -->|Yes| Fix[Auto-fix:<br/>- Patch<br/>- Block<br/>- Disable]
    Action -->|No| Manual[Manual<br/>Intervention]
    
    style Cat1 fill:#ff6b6b
    style Alert fill:#ff6b6b
    style Fix fill:#51cf66
```

---

## 🌐 ARCHITECTURE: COMPLETE SYSTEM VIEW

### Diagrama ARCH.1 - MCP Server Architecture

```mermaid
graph TB
    subgraph "External Clients"
        Claude[Claude Desktop]
        Cursor[Cursor IDE]
        Gemini[Gemini Code Assist]
        Custom[Custom Client]
    end
    
    Claude -->|stdio| MCP
    Cursor -->|stdio| MCP
    Gemini -->|SSE HTTP| MCP
    Custom -->|HTTP| MCP
    
    subgraph "MCP Server - vertice-cyber"
        MCP[FastMCP Server<br/>Port 8000]
        
        MCP --> Tools[Tools Registry]
        MCP --> Resources[Resources]
        MCP --> Prompts[Prompts]
        
        Tools --> T1[ethical_validate]
        Tools --> T2[osint_investigate]
        Tools --> T3[threat_predict]
        Tools --> T4[immune_respond]
        Tools --> T5[purple_team_run]
        Tools --> T6[patch_validate]
        Tools --> T7[pentest_scan]
        
        Resources --> R1[vertice://status]
        Resources --> R2[vertice://agents]
        Resources --> R3[vertice://metrics]
    end
    
    subgraph "Core Infrastructure"
        T1 --> Core[Core Layer]
        T2 --> Core
        T3 --> Core
        T4 --> Core
        T5 --> Core
        T6 --> Core
        T7 --> Core
        
        Core --> Settings[(Pydantic<br/>Settings)]
        Core --> EventBus[Event Bus<br/>Pub/Sub]
        Core --> Memory[(Agent<br/>Memory Pool)]
        Core --> Identity[Identity<br/>Validator]
    end
    
    subgraph "Agent Tools"
        T1 --> Magistrate[Ethical<br/>Magistrate]
        T2 --> OSINT[OSINT<br/>Hunter]
        T3 --> Threat[Threat<br/>Prophet]
        T4 --> Immune[Immune<br/>System]
        T5 --> Purple[Purple<br/>Team]
        T6 --> Patch[Patch<br/>Validator]
        T7 --> Pentest[Pentest<br/>Engine]
    end
    
    subgraph "External Services"
        Magistrate --> ATLAS[(MITRE<br/>ATLAS)]
        OSINT --> Shodan[Shodan<br/>API]
        OSINT --> HIBP[HaveIBeen<br/>Pwned]
        Threat --> ATT&CK[(MITRE<br/>ATT&CK)]
        Patch --> NVD[NVD<br/>Database]
        Patch --> EPSS[EPSS<br/>API]
        Patch --> KEV[KEV<br/>Catalog]
        Pentest --> Nuclei[Nuclei<br/>Templates]
    end
    
    style MCP fill:#4dabf7
    style Core fill:#51cf66
    style EventBus fill:#ffd43b
```

### Diagrama ARCH.2 - Event-Driven Communication

```mermaid
sequenceDiagram
    participant Client as Claude/Gemini
    participant MCP as MCP Server
    participant Tool1 as OSINT Hunter
    participant Bus as Event Bus
    participant Tool2 as Threat Prophet
    participant Tool3 as Immune System
    
    Client->>MCP: osint_investigate("hacker@evil.com")
    MCP->>Tool1: investigate()
    
    Tool1->>Bus: emit(OSINT_INVESTIGATION_STARTED)
    Note over Bus: Event published to subscribers
    
    Tool1->>Tool1: Check HIBP breaches
    Tool1->>Tool1: Shodan scan
    
    Tool1->>Bus: emit(OSINT_BREACH_DETECTED, {...})
    
    Bus->>Tool2: on(OSINT_BREACH_DETECTED)
    Bus->>Tool3: on(OSINT_BREACH_DETECTED)
    
    par Parallel Processing
        Tool2->>Tool2: Analyze breach data
        Tool2->>Tool2: Map to ATT&CK
        Tool2->>Bus: emit(THREAT_DETECTED)
    and
        Tool3->>Tool3: Calculate risk
        Tool3->>Tool3: Should auto-respond?
        Tool3->>Bus: emit(IMMUNE_RESPONSE_TRIGGERED)
    end
    
    Tool1->>Bus: emit(OSINT_INVESTIGATION_COMPLETED)
    Tool1->>MCP: return OSINTResult
    MCP->>Client: {...findings, breaches, risk_score...}
    
    Note over Bus,Tool3: Event-driven side effects continue
```

---

## 📈 METRICS & MONITORING

### Diagrama METRICS.1 - Real-time Metrics Dashboard

```mermaid
graph TB
    subgraph "Data Sources"
        S1[Ethical Magistrate:<br/>Decisions/hour]
        S2[OSINT Hunter:<br/>Breaches detected]
        S3[Threat Prophet:<br/>Predictions accuracy]
        S4[Immune System:<br/>Response time]
        S5[Purple Team:<br/>Coverage %]
        S6[Patch Validator:<br/>Auto-patch rate]
    end
    
    S1 --> Aggregator[Metrics<br/>Aggregator]
    S2 --> Aggregator
    S3 --> Aggregator
    S4 --> Aggregator
    S5 --> Aggregator
    S6 --> Aggregator
    
    Aggregator --> Dashboard[Real-time<br/>Dashboard]
    
    subgraph "Dashboard Panels"
        Dashboard --> P1[Detection Coverage:<br/>82% of ATT&CK]
        Dashboard --> P2[Mean Time to Detect:<br/>47ms]
        Dashboard --> P3[False Positive Rate:<br/>3.2%]
        Dashboard --> P4[Auto-Response Rate:<br/>76% autonomous]
        Dashboard --> P5[Agent Health:<br/>All 🟢 Healthy]
        Dashboard --> P6[Threat Level:<br/>🟡 Elevated]
    end
    
    P1 --> Alerts{Threshold<br/>Breach?}
    P2 --> Alerts
    P3 --> Alerts
    P4 --> Alerts
    
    Alerts -->|Yes| Notify[Slack/Email<br/>Notification]
    Alerts -->|No| Continue[Continue<br/>Monitoring]
    
    style P2 fill:#51cf66
    style P4 fill:#51cf66
    style P6 fill:#ffd43b
```

---

**FIM DOS DIAGRAMAS MERMAID**

Todos os diagramas acima podem ser:
1. Copiados direto para https://mermaid.live
2. Renderizados em Markdown (GitHub, Notion, etc.)
3. Exportados como PNG/SVG
4. Usados em documentação técnica

Cada diagrama ilustra aspectos diferentes dos agentes:
- **Flowcharts**: Processos e decisões
- **Sequence Diagrams**: Interações entre componentes
- **State Diagrams**: Máquinas de estado
- **Architecture Diagrams**: Visão geral do sistema