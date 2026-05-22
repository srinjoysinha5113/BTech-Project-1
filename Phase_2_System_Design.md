# Phase 2: System Design

## Project Title: Post-Quantum Secure Web API Using Lattice-Based Cryptography

---

### 1. SYSTEM ARCHITECTURE OVERVIEW

The system architecture for the "Post-Quantum Secure Web API" is designed to be a robust, modular, and scalable client-server model. It bridges the gap between classical cryptographic protocols and the future of quantum-resistant communications. 

The architecture follows a strict decoupled approach, ensuring that the frontend presentation layer is completely isolated from the backend cryptographic logic and the database persistence layer.

*   **Frontend/Backend Interaction:** The React-based frontend communicates with the FastAPI backend exclusively via RESTful HTTP APIs. All sensitive data exchanged during these API calls is secured at the payload level using our custom hybrid cryptographic workflow.
*   **Cryptographic Workflow:** The system abstracts cryptographic operations into a dedicated Service Layer. This layer handles the lifecycle of classical (RSA) and post-quantum (Kyber) operations independently, allowing for side-by-side comparison without cross-contamination of keys.
*   **Hybrid Encryption Flow:** To emulate real-world migration strategies, the actual secure communication does not rely solely on Post-Quantum Cryptography (PQC). Instead, it uses Kyber as a Key Encapsulation Mechanism (KEM) to securely exchange a session key, which is then used by AES-256-GCM to encrypt the bulk payload.
*   **Communication Lifecycle:** 
    1. The client requests a public key (RSA or Kyber).
    2. The server responds with the requested key.
    3. The client encapsulates a secret/encrypts the payload and sends it back.
    4. The server decapsulates the secret, derives the AES key, and decrypts the payload.
    5. The decrypted data is processed and persisted to the MySQL database.

---

### 2. HIGH LEVEL ARCHITECTURE DIAGRAM

The following represents the layered architecture of the system:

`	ext
[ Presentation Layer ]
      |
      v
+-----------------------------+
|        User Browser         |  <-- Initiates requests, displays visualizations
+-----------------------------+
      | (HTTP/JSON/Encrypted Payloads)
      v
+-----------------------------+
|       React Frontend        |  <-- State management, UI rendering, Axios API client
+-----------------------------+
      | (Axios HTTP Requests)
      v
[ Application / API Layer ]
      |
      v
+-----------------------------+
|    API Communication Layer  |  <-- FastAPI Routing, Input Validation (Pydantic)
+-----------------------------+
      |
      v
+-----------------------------+
|       FastAPI Backend       |  <-- Core application controller, Request orchestration
+-----------------------------+
      |
      v
[ Business Logic & Service Layer ]
      |
      v
+-----------------------------+
|        Service Layer        |  <-- Business rules, Database bridging, Orchestration
+-----------------------------+
      |
      v
+-----------------------------+
| Cryptographic Service Layer |  <-- Abstract factory for crypto operations
+-----------------------------+
      |
      +--------+----------------+
      |        |                |
      v        v                v
+----------+ +-----------+ +----------+
|   RSA    | |   Kyber   | |   AES    | <-- Concrete cryptographic implementations
|  Module  | |  Module   | |  Module  |
+----------+ +-----------+ +----------+
      |
      v
[ Persistence Layer ]
      |
      v
+-----------------------------+
|       Database Layer        |  <-- SQLAlchemy ORM, Session management, Connection Pooling
+-----------------------------+
      | (SQL/TCP)
      v
+-----------------------------+
|       MySQL Database        |  <-- Relational data storage, indexing, ACID compliance
+-----------------------------+
`

**Layer Explanation:**
*   **Presentation Layer:** Handles all user interactions, visual feedback, and cryptographic educational animations.
*   **Application/API Layer:** The FastAPI entry point. Responsible for endpoint routing, request validation, and HTTP response formatting.
*   **Business Logic & Service Layer:** Contains the core intelligence of the application. It acts as a mediator between the API layer, the cryptographic engines, and the database ORM.
*   **Persistence Layer:** Utilizes SQLAlchemy to translate Python objects into relational database rows, abstracting raw SQL queries and managing concurrent connections to the MySQL server.

---

### 3. MODULE DESIGN

#### A. Frontend Module
*   **Responsibilities:** Render the user interface, manage client-side state, construct encrypted API payloads, and visualize cryptographic processes.
*   **Components:** Dashboard, RSA Visualization, PQC Visualization, Benchmark UI, Educational UI.
*   **Inputs:** User interactions (clicks, form data), API responses (JSON, ciphertexts).
*   **Outputs:** DOM updates, animated graphs, HTTP requests to backend.
*   **Dependencies:** React, Vite, TailwindCSS, Axios, Chart.js (or similar for benchmarks).

#### B. Backend API Module
*   **Responsibilities:** Expose RESTful endpoints, validate incoming JSON payloads, route requests to appropriate services, and handle HTTP errors.
*   **Inputs:** HTTP GET/POST requests containing plaintext or ciphertext payloads.
*   **Outputs:** HTTP JSON responses containing status codes, decrypted echoes, or public keys.
*   **Dependencies:** FastAPI, Pydantic, Uvicorn.
*   **Interactions:** Calls the Service Layer for business logic; returns data to the Frontend.

#### C. RSA Module (Classical)
*   **Responsibilities:** Generate 2048-bit keys, perform standard RSA encryption and decryption for demonstration purposes.
*   **Inputs:** Key generation triggers, plaintext for encryption, ciphertext for decryption.
*   **Outputs:** Public/Private key pairs, RSA ciphertexts, decrypted plaintexts.
*   **Dependencies:** pycryptodome.

#### D. Kyber Module (Post-Quantum)
*   **Responsibilities:** Generate Kyber-512 key pairs, encapsulate shared secrets against public keys, and decapsulate ciphertexts to retrieve secrets.
*   **Inputs:** Security level configuration, remote public keys, encapsulated ciphertexts.
*   **Outputs:** Kyber public keys, encapsulated ciphertexts, raw 32-byte shared secrets.
*   **Dependencies:** oqs-python (liboqs).

#### E. AES Module (Symmetric)
*   **Responsibilities:** Provide authenticated encryption with associated data (AEAD) using AES-256-GCM, utilizing the secret derived from Kyber.
*   **Inputs:** 32-byte session key, plaintext payload, ciphertext + authentication tag + nonce.
*   **Outputs:** AES ciphertexts, decrypted plaintexts.
*   **Dependencies:** pycryptodome.

#### F. Benchmarking Module
*   **Responsibilities:** Execute looped cryptographic operations, record CPU timing and memory consumption, calculate key/ciphertext sizes, and format data for visualization.
*   **Inputs:** Benchmark configuration (algorithm choice, iteration count).
*   **Outputs:** Aggregated metrics (latency in ms, sizes in bytes) formatted as JSON or Pandas DataFrames.
*   **Dependencies:** Python time, sys, pandas.

#### G. Database Module
*   **Responsibilities:** Persist secure message logs, user data, and historical benchmark results with ACID properties.
*   **Inputs:** ORM model instances (User, Message, BenchmarkResult).
*   **Outputs:** Database commit success, queried records.
*   **Dependencies:** SQLAlchemy, pymysql (or mysqlclient), MySQL Server.
*   **Interactions:** Called by the Service Layer upon successful decryption or benchmark completion.

---

### 4. DATA FLOW DIAGRAMS (DFD)

#### Context Level DFD (Level 0)
`	ext
          +-------------------+
          |                   |
[User] -> |  Post-Quantum     | -> [Visual Feedback / Metrics]
          |  Secure Web API   |
[Data] -> |  System           | -> [Stored Encrypted Logs (MySQL)]
          +-------------------+
`
**Description:** The user interacts with the system by providing data. The system processes this data securely using hybrid encryption and outputs visual feedback, benchmark metrics, and stores transaction logs.

#### Level 1 DFD (Major Subsystems)
`	ext
[User] ---> (1.0 UI & Visualization) ---> [API Requests]
                    |
                    v
             (2.0 API Gateway)
                    |
          +---------+---------+
          |                   |
          v                   v
(3.0 Classical Flow)   (4.0 Hybrid PQC Flow)
      [RSA]              [Kyber + AES]
          |                   |
          +---------+---------+
                    |
                    v
            (5.0 Storage Engine)
                    |
                    v
             [MySQL Database]
`
**Description:** Data flows from the UI to the API Gateway. Depending on the requested demonstration, it is routed to either the Classical (RSA) or Hybrid PQC workflow. The resulting decrypted data or benchmark metric is then passed to the Storage Engine.

#### Level 2 DFD (Hybrid PQC Flow - Process 4.0)
`	ext
[Client Request for Key] -> (4.1 Generate Kyber Keys) -> [Kyber Public Key to Client]
                                  |
                                  v (Client Side via API)
[Client Encapsulates Secret] -> (4.2 KEM Encapsulation) -> [Kyber Ciphertext]
[Client Encrypts Payload]    -> (4.3 AES-GCM Encrypt)   -> [AES Ciphertext + Tag]
                                  |
                                  v (Server Side)
[Receive Ciphertexts]        -> (4.4 KEM Decapsulation) -> [Shared Secret]
                                  |
                                  v
[Shared Secret + AES Data]   -> (4.5 AES-GCM Decrypt)   -> [Plaintext Payload]
                                  |
                                  v
                            (4.6 Persist Payload) -> [MySQL]
`

---

### 5. UML DIAGRAMS

#### A. Use Case Diagram
*   **Actors:** 
    *   **User:** Interacts with the web dashboard.
    *   **Administrator:** Monitors system logs and benchmark histories.
    *   **Backend System:** The automated FastAPI server.
*   **Use Cases:**
    *   *User:* "View Educational Content", "Run RSA Demo", "Run Kyber Demo", "Send Secure Message", "Execute Benchmarks".
    *   *Administrator:* "View Benchmark History", "Analyze Cryptographic Logs".
    *   *Backend System:* "Generate Keys", "Encapsulate Secret", "Decrypt Payload", "Store Data".
*   **Relationships:** "Run Kyber Demo" *includes* "Generate Keys" and "Encapsulate Secret".

#### B. Sequence Diagram (Kyber Secure Communication)
`	ext
User/Browser              FastAPI Backend               Crypto Service           MySQL DB
     |                           |                            |                     |
     |--- 1. GET /pqc/pubkey --->|                            |                     |
     |                           |--- 2. Generate KyberKey -->|                     |
     |                           |<-- 3. Return PubKey -------|                     |
     |<-- 4. HTTP 200 (PubKey) --|                            |                     |
     |                           |                            |                     |
     | (Client encapsulates      |                            |                     |
     |  secret and encrypts      |                            |                     |
     |  data with AES)           |                            |                     |
     |                           |                            |                     |
     |--- 5. POST /secure/send ->|                            |                     |
     |    (Kyber CT + AES CT)    |                            |                     |
     |                           |--- 6. Decapsulate Kyber -->|                     |
     |                           |<-- 7. Shared Secret -------|                     |
     |                           |--- 8. Decrypt AES Payload->|                     |
     |                           |<-- 9. Plaintext -----------|                     |
     |                           |                            |                     |
     |                           |--- 10. Store Message --------------------------->|
     |                           |<-- 11. DB Commit Success ------------------------|
     |<-- 12. HTTP 200 Success --|                            |                     |
`

#### C. Activity Diagram (Secure Message Transmission)
1.  **Start:** User initiates message send.
2.  **Action:** Frontend requests PQC public key.
3.  **Action:** Server returns Kyber-512 public key.
4.  **Action:** Frontend encapsulates a 32-byte secret using the public key.
5.  **Action:** Frontend encrypts the actual message using AES-GCM with the encapsulated secret.
6.  **Action:** Frontend sends both the Kyber Ciphertext and AES Ciphertext to the backend.
7.  **Action:** Server decapsulates Kyber Ciphertext to retrieve the shared secret.
8.  **Decision:** Did decapsulation succeed?
    *   *No:* Log failure, return HTTP 400.
    *   *Yes:* Proceed to AES decryption.
9.  **Action:** Server decrypts AES Ciphertext using the shared secret.
10. **Action:** Server stores plaintext to database.
11. **End:** Return success response to user.

#### D. Component Diagram
*   **Client Component:** React Application (UI, API Client, State Manager).
*   **Server Component:** FastAPI Application (Router, Middleware, Pydantic Schemas).
*   **Service Component:** Crypto Manager (RSA Handler, Kyber Handler, AES Handler).
*   **Data Component:** SQLAlchemy ORM, MySQL Driver, MySQL Server.

---

### 6. API DESIGN

#### RSA APIs
*   **GET /api/v1/rsa/public-key**
    *   **Purpose:** Fetches the server's classical RSA public key.
    *   **Response:** { "n": "...", "e": "65537" }
*   **POST /api/v1/rsa/encrypt**
    *   **Purpose:** Client asks server to encrypt data (demo).
    *   **Request:** { "message": "hello" }
    *   **Response:** { "ciphertext": "hex_string" }
*   **POST /api/v1/rsa/decrypt**
    *   **Purpose:** Client sends RSA encrypted data to server.
    *   **Request:** { "ciphertext": "hex_string" }
    *   **Response:** { "plaintext": "hello" }

#### PQC APIs
*   **GET /api/v1/pqc/public-key**
    *   **Purpose:** Fetches the Kyber-512 public key for KEM.
    *   **Response:** { "public_key": "hex_string" }
*   **POST /api/v1/pqc/encapsulate**
    *   **Purpose:** Educational endpoint to show encapsulation without payload.
    *   **Request:** { "public_key": "hex_string" }
    *   **Response:** { "ciphertext": "hex", "shared_secret": "hex" }

#### Secure Messaging APIs (Hybrid)
*   **POST /api/v1/secure/send**
    *   **Purpose:** The core hybrid endpoint. Receives payload secured by PQC.
    *   **Request:** 
        `json
        {
          "kem_ciphertext": "hex_string_from_kyber",
          "aes_nonce": "hex_string",
          "aes_tag": "hex_string",
          "aes_ciphertext": "hex_string"
        }
        `
    *   **Process:** Decapsulate kem_ciphertext to get AES key. Decrypt es_ciphertext using AES-GCM. Save to DB.
    *   **Response:** { "status": "success", "saved_message_id": 123 }
    *   **Error Handling:** Returns 400 Bad Request if AES authentication tag fails (tampering detected).

#### Benchmark APIs
*   **GET /api/v1/benchmark/run**
    *   **Purpose:** Executes load tests on the server CPU.
    *   **Query Params:** iterations=100
    *   **Response:** JSON object detailing average KeyGen, Encaps, Decaps times for RSA and Kyber.

---

### 7. DATABASE DESIGN (MySQL)

The system uses MySQL via SQLAlchemy ORM to ensure robust, production-like data persistence, offering better concurrency handling than SQLite for API environments.

#### A. Users Table (users)
*   **Attributes:** id (PK, Integer, Auto-increment), username (String, Unique), created_at (DateTime).
*   **Purpose:** Tracks users participating in the demonstration.

#### B. Messages Table (messages)
*   **Attributes:** 
    *   id (PK, Integer)
    *   user_id (FK to users.id)
    *   plaintext_content (Text) - *Stored for demo validation.*
    *   crypto_method (Enum: 'RSA', 'Kyber-AES')
    *   processing_time_ms (Float)
    *   	imestamp (DateTime)
*   **Purpose:** Stores successfully decrypted messages to prove the API workflow functioned correctly.

#### C. Benchmark Results Table (enchmark_results)
*   **Attributes:**
    *   id (PK, Integer)
    *   lgorithm (String)
    *   operation (String: 'KeyGen', 'Encaps', 'Decaps')
    *   vg_time_ms (Float)
    *   	imestamp (DateTime)
*   **Purpose:** Historical tracking of performance data for dashboard visualization.

#### D. Logs Table (system_logs)
*   **Attributes:** id (PK), level (String), event_description (Text), 	imestamp (DateTime).
*   **Purpose:** Security auditing and error tracking (e.g., "Failed AES decryption attempt").

**Database Architecture Rationale:** 
MySQL is utilized instead of SQLite because a Web API is inherently concurrent. FastAPI handles asynchronous requests rapidly; a production-grade RDBMS like MySQL with proper connection pooling (via SQLAlchemy) ensures that concurrent cryptographic requests and subsequent database writes do not result in database locks or race conditions.

---

### 8. CRYPTOGRAPHIC WORKFLOW DESIGN

#### A. RSA Workflow
1.  **Key Generation:** Server uses pycryptodome to generate large primes (p, q), computes modulus (n = p*q), and derives public exponent (e) and private exponent (d).
2.  **Encryption:** Client fetches public key (n, e). Computes Ciphertext C = M^e mod n.
3.  **Decryption:** Server receives C. Computes Message M = C^d mod n.

#### B. Kyber + AES Hybrid Workflow
1.  **Kyber Public Key Retrieval:** Client requests KEM public key. Server generates Kyber-512 keypair and sends the public key (pk).
2.  **Session Key Encapsulation:** Client uses oqs to encapsulate a 32-byte shared secret (ss) against the public key (pk). This produces a Kyber ciphertext (ct).
3.  **AES Key Derivation:** The shared secret (ss) is mapped directly as the 256-bit key for AES.
4.  **Encrypted Payload Transfer:** Client encrypts the actual message using AES-GCM with the derived key, producing an AES ciphertext, a nonce, and an authentication tag.
5.  **Transmission:** Client sends the Kyber ciphertext (ct), AES ciphertext, nonce, and tag to the server.
6.  **Decapsulation:** Server uses its Kyber secret key to decapsulate the Kyber ciphertext (ct), recovering the exact same 32-byte shared secret (ss).
7.  **Decryption:** Server uses the recovered shared secret as the AES key to decrypt the payload, verifying the authentication tag to ensure data integrity.

**Workflow Justification:**
Asymmetric algorithms (like RSA and Kyber) are computationally expensive and have severe size limitations on what they can encrypt directly. Therefore, AES (a symmetric algorithm) is used for bulk data. Kyber's role is strictly to protect the AES session key during transit against quantum interception, mirroring how TLS 1.3 currently operates with ECDHE and AES.

---

### 9. SECURITY ARCHITECTURE

*   **AES-GCM Authentication:** AES is used in Galois/Counter Mode (GCM). This provides Authenticated Encryption with Associated Data (AEAD). The server strictly verifies the authentication tag before decryption, preventing ciphertext tampering.
*   **Session Security:** The shared secret is ephemeral. A new Kyber encapsulation (and thus a new AES key) is generated for every request, enforcing Perfect Forward Secrecy (PFS) conceptually for the API payload.
*   **API Security Assumptions:** 
    *   Input validation is rigorously enforced using FastAPI's Pydantic models. Malformed ciphertexts are rejected before cryptographic processing begins.
    *   SQL Injection is prevented entirely by using SQLAlchemy's parameterized queries via the ORM.
*   **Secure Error Handling:** Cryptographic failures (e.g., tag mismatch) return a generic "400 Bad Request" or "401 Unauthorized" without detailing *why* the cryptography failed, preventing padding oracle or timing attacks.

---

### 10. FRONTEND DESIGN ARCHITECTURE

*   **Page Hierarchy:**
    *   / - Home/Dashboard (System Overview)
    *   /rsa - Classical Cryptography Sandbox
    *   /kyber - Post-Quantum Hybrid Sandbox
    *   /benchmarks - Performance Analytics
    *   /learn - Educational visualizer for Quantum threats.
*   **Component Hierarchy:** Modular design (e.g., <KeyDisplay />, <EncryptForm />, <MetricsChart />).
*   **State Management:** React useState and useEffect hooks handle transient cryptographic states (e.g., storing the public key in memory during a session).
*   **API Integration:** Axios instances configured with interceptors to handle loading states and catch global backend errors gracefully.

---

### 11. BACKEND DESIGN ARCHITECTURE

*   **Folder Structure:**
    `	ext
    /app
      /api           # FastAPI route definitions
      /core          # Configuration and DB connection
      /models        # SQLAlchemy database models
      /schemas       # Pydantic validation schemas
      /services      # Cryptographic logic (crypto_service.py)
      main.py        # Application entry point
    `
*   **Service Layer Design:** The CryptoService class abstracts the underlying libraries. The API route simply calls CryptoService.process_hybrid_payload(payload). This prevents API routers from becoming bloated with complex lattice math logic.
*   **Asynchronous Request Handling:** FastAPI utilizes sync def for API endpoints. While cryptographic operations are CPU-bound, database I/O is I/O-bound. This architecture allows the server to handle database writes asynchronously while freeing the event loop.

---

### 12. BENCHMARKING SYSTEM DESIGN

*   **Timing Measurement:** Python's 	ime.perf_counter() is used for high-resolution timing of CPU-bound tasks.
*   **Latency Analysis:** The benchmark module executes N iterations of KeyGen, Encaps, and Decaps in a loop, capturing the raw time.
*   **Memory/Size Measurement:** sys.getsizeof() is used to compare the byte lengths of RSA public keys (usually ~256 bytes) versus Kyber-512 public keys (~800 bytes).
*   **Comparative Reporting:** The raw arrays of execution times are passed to pandas to calculate mean, median, and standard deviation, which are then served to the frontend for chart generation.

---

### 13. DEPLOYMENT ARCHITECTURE

*   **Local Deployment:** Managed via Python virtual environments (env) and npm.
*   **Database Deployment:** A local instance of MySQL Server 8.0+.
*   **Configuration Management:** Secrets, database URIs, and port configurations are strictly managed via a .env file loaded by python-dotenv.
*   **Production Considerations (Simulated):** The backend utilizes Uvicorn as the ASGI server. Connection pooling is configured in SQLAlchemy to maintain a stable number of connections to MySQL, preventing connection exhaustion under heavy API load.

---

### 14. ERROR HANDLING DESIGN

*   **Invalid Ciphertext Handling:** If the client sends a corrupted Kyber ciphertext, the decapsulation process will yield an incorrect shared secret. Consequently, the AES-GCM tag verification will fail. The system catches the ValueError from pycryptodome and raises an HTTP Exception.
*   **Database Rollback Strategy:** If an error occurs during the persistence phase (e.g., database constraint violation), SQLAlchemy's session management is configured to automatically call session.rollback(), ensuring no partial records exist.
*   **Secure Logging:** Errors are logged internally to the console/file with stack traces, but the API returns sanitized JSON error messages to the client.

---

### 15. SYSTEM CONSTRAINTS

*   **Computational Overhead:** Lattice-based cryptography requires specific mathematical operations (polynomial multiplication) that present a different CPU profile than RSA modular exponentiation.
*   **Key Size Overhead:** PQC fundamentally requires larger key sizes and ciphertext sizes. Kyber-512 ciphertexts are significantly larger than RSA ciphertexts, increasing network bandwidth usage slightly.
*   **PQC Library Limitations:** oqs-python is a wrapper around a C library. This introduces cross-platform compilation constraints, requiring correct C-compilers to be present on the host deployment machine.

---

### 16. DESIGN JUSTIFICATION

*   **FastAPI:** Chosen for its asynchronous capabilities, exceptional speed, and automatic validation via Pydantic, which is vital for parsing complex JSON cryptographic payloads.
*   **React:** Provides a highly reactive DOM, necessary for visualizing step-by-step cryptographic animations smoothly.
*   **MySQL & SQLAlchemy:** Chosen over NoSQL or SQLite to demonstrate enterprise-grade persistence, enforcing schema integrity and handling concurrent transactional loads typical of a real Web API.
*   **Kyber & AES-GCM:** Selected because this combination is the exact blueprint being recommended by NIST and major tech organizations (like Cloudflare and Google) for migrating TLS protocols.
*   **Waterfall Model:** System design must be fully finalized before implementation because cryptographic systems require rigid architectures; retrofitting security into an agile, loosely-defined architecture often leads to fatal vulnerabilities.

---

### 17. EXPECTED SYSTEM BEHAVIOR

During normal operation, the system will seamlessly accept payload requests from the frontend. The user will experience a standard web interface, unaware of the complex lattice mathematics occurring underneath. The backend will rapidly decapsulate the PQC session keys, decrypt the AES payloads, commit the data to MySQL, and return a success response in under 200ms. Benchmark executions will monopolize the CPU temporarily, generating statistically significant data sets comparing classical vs. post-quantum paradigms, visually demonstrating the efficiency of Kyber despite its larger key sizes.

---

### 18. CONCLUSION

The system design for the Post-Quantum Secure Web API presents a highly modular, secure, and academically rigorous architecture. By strictly separating the presentation, API, cryptographic, and persistence layers, the system achieves excellent maintainability and scalability. The integration of FastAPI and MySQL ensures enterprise-grade request handling, while the hybrid Kyber-AES cryptographic workflow provides a practical, real-world demonstration of how modern web infrastructure can seamlessly transition to quantum-resistant security models. This Phase 2 design provides a flawless blueprint for the subsequent implementation phase.

---
**End of Phase 2: System Design**
