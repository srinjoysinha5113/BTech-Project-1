# Phase 1: Requirement Analysis

## Project Title: Post-Quantum Secure Web API Using Lattice-Based Cryptography

---

### 1. INTRODUCTION

#### 1.1 Background of Cryptography
Cryptography serves as the cornerstone of digital trust, ensuring confidentiality, integrity, and authenticity across global networks. From early substitution ciphers to modern asymmetric algorithms, the field has evolved to protect sensitive data against increasingly sophisticated adversarial capabilities. In the contemporary era, the security of the internet relies heavily on public-key infrastructure (PKI) to facilitate secure key exchanges and digital signatures.

#### 1.2 Importance of Web Security
As the global economy and social infrastructure migrate to the web, the security of Web APIs has become paramount. APIs facilitate the exchange of sensitive information, including financial transactions, personal identity data, and healthcare records. Any compromise in the underlying cryptographic protocols could lead to catastrophic data breaches and loss of systemic trust.

#### 1.3 RSA and Modern Internet Security
The RSA (Rivest-Shamir-Adleman) algorithm is the most widely deployed asymmetric cryptographic system. Its security is predicated on the mathematical difficulty of the integer factorization problem. Currently, RSA-2048 and RSA-4096 are considered secure against classical computational attacks, forming the basis of TLS/SSL protocols that secure most web traffic.

#### 1.4 Emergence of Quantum Computing
Quantum computing represents a paradigm shift in computational physics. Unlike classical bits, quantum bits (qubits) can exist in superpositions, allowing quantum computers to perform certain calculations exponentially faster than the most powerful classical supercomputers. While still in the developmental stage, the rapid advancement in qubit stability and error correction brings the \"Q-Day\"—the day quantum computers can break modern encryption—closer to reality.

#### 1.5 Threat of Shor's Algorithm
In 1994, mathematician Peter Shor developed a quantum algorithm that can factorize large integers and compute discrete logarithms in polynomial time. This means that a sufficiently powerful cryptographically relevant quantum computer (CRQC) could break RSA and Elliptic Curve Cryptography (ECC) almost instantaneously, rendering current web security protocols obsolete.

#### 1.6 Need for Post-Quantum Cryptography (PQC)
Post-Quantum Cryptography refers to cryptographic algorithms—usually public-key algorithms—that are thought to be secure against an attack by a quantum computer. As the transition to new standards takes years, it is critical to implement and test these algorithms now to ensure a \"quantum-safe\" future.

#### 1.7 Introduction to Lattice-Based Cryptography
Lattice-based cryptography is a leading candidate for PQC. It relies on the hardness of lattice problems, such as the Shortest Vector Problem (SVP) and the Learning With Errors (LWE) problem. These problems are conjectured to be resistant to both classical and quantum algorithmic attacks, offering a robust foundation for secure communication.

#### 1.8 Selection of Kyber by NIST
The National Institute of Standards and Technology (NIST) conducted a multi-year global competition to standardize PQC algorithms. CRYSTALS-Kyber was selected as the primary standard for general encryption (Key Encapsulation Mechanism or KEM). Kyber is favored for its high efficiency, relatively small key sizes, and strong security proofs based on the Module-LWE problem.

---

### 2. PROBLEM STATEMENT

#### 2.1 Vulnerability of RSA in the Quantum Era
The fundamental security assumption of RSA—the hardness of factoring the product of two large primes—is invalidated by Shor's algorithm. In a post-quantum world, RSA-based certificates and key exchanges will offer zero protection, allowing attackers to intercept and read encrypted traffic.

#### 2.2 \"Harvest Now, Decrypt Later\" Attacks
A critical and immediate threat is the \"Harvest Now, Decrypt Later\" strategy. Adversaries are currently intercepting and storing encrypted high-value data from the web. Although they cannot decrypt it today, they intend to hold this data until quantum computers become available, at which point they will retroactively decrypt the stored information. This makes the migration to PQC an urgent priority for data with long-term sensitivity.

#### 2.3 Risks to Web APIs
Modern microservices and mobile applications rely on APIs for data persistence and logic execution. If these APIs continue to use classical key exchange mechanisms, the entire ecosystem remains vulnerable to quantum-enabled interception, leading to systemic failure in sectors like banking and national security.

#### 2.4 Necessity for Migration and PQC Architecture
There is a lack of practical, integrated demonstrations showing how legacy systems (RSA) can be migrated to quantum-resistant architectures. This project addresses the need for a hybrid cryptographic system that bridges the gap between classical reliability and post-quantum resilience, specifically focusing on the Kyber-AES integration for secure API communication.

---

### 3. PROJECT OBJECTIVES

#### A. Primary Objectives
1.  **Implement Classical RSA Communication:** Develop a baseline module using RSA to demonstrate current web security standards. This includes key generation (2048-bit), encryption, and decryption processes.
2.  **Simulate Quantum Vulnerability:** Provide an educational visualization and theoretical demonstration of how Shor’s algorithm reduces the complexity of integer factorization, thereby compromising RSA-based security.
3.  **Integrate CRYSTALS-Kyber:** Implement Kyber-based Key Encapsulation Mechanism (KEM) for secure session key exchange, following the NIST Level 1 (Kyber-512) or Level 3 (Kyber-768) security parameters.
4.  **Develop Hybrid Encryption System:** Design an architecture that combines Kyber (for secure key exchange) with AES-256 (for efficient bulk data encryption), ensuring that the API payload is protected against both classical and quantum adversaries.
5.  **Build a Secure Web API:** Create a robust backend using FastAPI that handles quantum-resistant requests and provides a secure interface for data exchange with the frontend.

#### B. Secondary Objectives
1.  **Performance Benchmarking Suite:** Develop a module to quantitatively compare RSA and Kyber in terms of key generation time, encapsulation/decapsulation latency, and communication overhead (key/ciphertext sizes).
2.  **Educational Visualization Dashboard:** Design an interactive React-based dashboard to explain quantum threats, the principles of lattice-based cryptography, and the mechanics of the Learning With Errors (LWE) problem.
3.  **Data Persistence and Management:** Implement a secure SQLite database to manage user data and logs, ensuring that all stored sensitive information was processed via the post-quantum secure pipeline.
4.  **Comparative Analysis and Reporting:** Generate graphical reports using Matplotlib and Pandas to provide a visual comparison of the performance metrics, making the research findings accessible for academic presentation.

---

### 4. PROJECT SCOPE

#### IN SCOPE
*   **Secure Message Transfer:** A functional web application allowing users to send encrypted messages via a PQC-secured API.
*   **API Encryption:** Middleware implementation for encrypting/decrypting API payloads using a Kyber-derived AES key.
*   **RSA Simulation:** A dedicated module to demonstrate the mathematical steps of RSA and its theoretical breakdown.
*   **Kyber Implementation:** Integration of the oqs-python libraries for NIST-standardized lattice-based KEM.
*   **Benchmarking Suite:** Tools to measure CPU time and memory usage for various cryptographic operations.
*   **Visualization Dashboard:** A React-based UI displaying real-time cryptographic statistics and educational content.

#### OUT OF SCOPE
*   **Real TLS Replacement:** The project does not aim to replace the browser's native HTTPS/TLS stack at the kernel or browser level.
*   **Real Quantum Hardware:** No access to or implementation on physical quantum computers.
*   **Production-Grade PKI:** The system will not include a full-scale Certificate Authority (CA) or revocation infrastructure.
*   **Custom Mathematics Implementation:** The project will use verified cryptographic libraries rather than implementing the underlying lattice math from scratch.

---

### 5. PROJECT ACTORS

#### 5.1 User
*   **Description:** The primary consumer of the web application.
*   **Capabilities:** Interacts with the frontend dashboard, initiates RSA and PQC demonstrations, sends encrypted messages to the API, and triggers performance benchmarking tests.

#### 5.2 Administrator
*   **Description:** The system overseer responsible for maintenance and monitoring.
*   **Capabilities:** Accesses detailed system logs, monitors API performance metrics, and configures experimental cryptographic parameters (e.g., changing Kyber security levels).

#### 5.3 Backend API System
*   **Description:** The automated engine that drives the project's logic.
*   **Capabilities:** Manages cryptographic key lifecycle, handles session key decapsulation, performs bulk data encryption/decryption, interacts with the SQLite database, and serves JSON responses to the frontend.

---

### 6. FUNCTIONAL REQUIREMENTS

#### A. User Interface Module
*   **REQ-UI-01: Dashboard Overview**
*   **REQ-UI-02: Cryptographic Visualization**

#### B. RSA Module
*   **REQ-RSA-01: RSA Key Generation**
*   **REQ-RSA-02: RSA Encryption/Decryption**

#### C. PQC Module
*   **REQ-PQC-01: Kyber Key Pair Generation**
*   **REQ-PQC-02: Shared Secret Encapsulation**
*   **REQ-PQC-03: AES Hybrid Encryption**

#### D. Benchmarking Module
*   **REQ-BM-01: Latency Measurement**
*   **REQ-BM-02: Data Size Analysis**

#### E. Educational Module
*   **REQ-ED-01: Quantum Threat Explainer**

#### F. API Module
*   **REQ-API-01: RSA Public Key Endpoint**
*   **REQ-API-02: Kyber Public Key Endpoint**
*   **REQ-API-03: Secure Message Transfer Endpoint**
*   **REQ-API-04: Benchmark Execution Endpoint**

---

### 7. NON-FUNCTIONAL REQUIREMENTS

#### 7.1 Security
The system must ensure that the PQC implementation follows NIST guidelines. **AES-256 provides strong symmetric encryption security, while Kyber secures session key exchange against quantum attacks.** The system must also protect against common web vulnerabilities (XSS, CSRF).

---

### 8. SECURITY ASSUMPTIONS

*   **AES-256 Resistance:** It is assumed that AES-256 remains quantum-resistant for the duration of the data's sensitivity, provided 256-bit keys are used.
*   **Kyber Standard Security:** The implementation of Kyber is assumed to be mathematically secure as per NIST standardization (FIPS 203).
*   **Trusted Endpoints:** It is assumed that the server environment and the client device (frontend) are not compromised; the security focus is primarily on protecting the communication channel against interception.
*   **Adversary Capability:** The adversary is assumed to have full interception capabilities (Harvest Now, Decrypt Later) and access to a future cryptographically relevant quantum computer.

---

### 9. SYSTEM REQUIREMENTS

#### A. Hardware Requirements
*   **CPU:** Dual-core 2.4GHz or higher.
*   **RAM:** 8GB Minimum.
*   **Storage:** 1GB of free space.

#### B. Software Requirements
*   **Python Version:** 3.10+.
*   **Node.js:** 18.x+.
*   **Backend Framework:** FastAPI.
*   **Frontend Framework:** React with Vite.
*   **Database:** SQLite 3.

---

### 10. PROJECT CONSTRAINTS

*   **Hardware Resources:** The system is developed and tested on consumer-grade hardware; benchmarking results may vary significantly based on CPU architecture.
*   **Quantum Access:** No physical quantum computer is available for real-world testing; all quantum threats are simulated based on theoretical models.
*   **Experimental Libraries:** Reliance on oqs-python, which is a research-grade wrapper and may have performance or stability limitations compared to production-hardened classical libraries.
*   **Development Timeline:** The project must be completed within the B.Tech final semester academic calendar, limiting the depth of custom lattice mathematics implementation.

---

### 11. PROJECT SUCCESS CRITERIA

*   **Successful RSA Demo:** Baseline module correctly demonstrates classical encryption and theoretical vulnerability to Shor's algorithm.
*   **Secure Kyber Communication:** Verification of successful Kyber KEM handshake and establishment of a shared AES-256 session key.
*   **Integrated System:** Seamless end-to-end data flow between the React frontend and the FastAPI backend with no unhandled cryptographic errors.
*   **Visual Evidence:** Generation of comparative benchmark graphs that clearly illustrate the trade-offs between RSA and Kyber.
*   **Performance Targets:** API latency for a secure PQC-based message round-trip remains within an acceptable user-experience threshold (<200ms).

---

### 12. PROJECT RISKS

*   **Library Dependencies:** Potential breaking changes or security vulnerabilities in experimental PQC libraries during the development cycle.
*   **Mathematical Complexity:** Technical challenges in synchronizing client-side and server-side cryptographic states (e.g., encoding/decoding inconsistencies).
*   **Performance Overhead:** Risk of high CPU utilization on the host machine during intensive benchmarking affecting the responsiveness of the visualization dashboard.
*   **Cross-Platform Compatibility:** Potential issues running binary components of liboqs on different Windows versions or architectures.

---

### 13. FEASIBILITY STUDY

#### 13.1 Technical Feasibility
#### 13.2 Economic Feasibility
#### 13.3 Operational Feasibility

---

### 14. TECHNOLOGY STACK JUSTIFICATION

*   React + Vite
*   FastAPI
*   AES-256 (GCM Mode)
*   Kyber512
*   oqs-python
*   SQLite

---

### 15. LIMITATIONS OF THE SYSTEM

---

### 16. FUTURE SCOPE

---

### 17. WATERFALL MODEL JUSTIFICATION

---

### 18. EXPECTED OUTCOMES

---

### 19. CONCLUSION

---
**End of Phase 1: Requirement Analysis**
