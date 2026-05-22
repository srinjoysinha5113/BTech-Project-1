“Post-Quantum Secure Web API Using Lattice-Based Cryptography”

The project follows the Waterfall Software Development Model.

==================================================
PROJECT OVERVIEW
================
==================================

The goal of this project is to design and develop a secure web communication system that demonstrates:

1. Traditional RSA-based secure communication
2. The vulnerability of RSA against quantum computing attacks
3. The use of post-quantum lattice-based cryptography (Kyber) as a replacement
4. Secure API communication using Kyber + AES hybrid encryption

The system should simulate how future websites and APIs can protect sensitive data from quantum attacks.

The project should include:
- Frontend web application
- Backend API server
- RSA demonstration module
- Post-Quantum Cryptography module
- Performance comparison and benchmarking
- Educational visualization of quantum threats

==================================================
TECH STACK
==================================================

Frontend:
- React + Vite
- TailwindCSS
- Axios

Backend:
- Python FastAPI

Cryptography:
- pycryptodome
- oqs-python / liboqs
- RSA
- AES
- Kyber512

Database:
- SQLite

Benchmarking:
- matplotlib
- pandas

==================================================
IMPORTANT PROJECT CONCEPTS
==================================================

The project architecture should use:

Kyber → Secure Session Key Exchange
AES → Actual Data Encryption

RSA should only be used in the classical demonstration module.

The project DOES NOT:
- replace HTTPS completely
- build a real quantum computer
- implement lattice mathematics from scratch

The project DOES:
- demonstrate migration from RSA to post-quantum cryptography
- simulate secure communication against future quantum attacks
- compare RSA and Kyber performance

==================================================
GENERATE THE FOLLOWING SECTIONS IN DETAIL
==================================================

1. INTRODUCTION
- Background of cryptography
- Importance of web security
- RSA and modern internet security
- Emergence of quantum computing
- Threat of Shor’s algorithm
- Need for post-quantum cryptography
- Introduction to lattice-based cryptography
- Why Kyber was selected by NIST

==================================================

2. PROBLEM STATEMENT
Clearly explain:
- Why RSA becomes vulnerable in the quantum era
- Harvest Now, Decrypt Later attacks
- Risks to current web APIs and secure communication
- Why existing systems need migration
- Need for a quantum-resistant API architecture

==================================================

3. PROJECT OBJECTIVES

Divide into:
A. Primary Objectives
B. Secondary Objectives

Include objectives such as:
- Implement RSA secure communication
- Demonstrate quantum threat
- Implement Kyber-based key exchange
- Secure API data transfer using AES
- Compare RSA and Kyber performance
- Build educational visualizations

==================================================

4. PROJECT SCOPE

Explain:
IN SCOPE:
- Secure message transfer
- API encryption
- RSA simulation
- Kyber implementation
- Benchmarking
- Visualization dashboard

OUT OF SCOPE:
- Real TLS replacement
- Real quantum hardware
- Production-grade PKI infrastructure
- Custom lattice mathematics implementation

==================================================

5. FUNCTIONAL REQUIREMENTS

Generate detailed functional requirements.

Include modules such as:

A. User Interface Module
- Dashboard
- Encryption visualization
- RSA demo
- PQC demo
- Benchmark display

B. RSA Module
- RSA key generation
- Encryption/decryption
- API endpoints

C. PQC Module
- Kyber public key generation
- Shared secret encapsulation
- AES session encryption
- API communication

D. Benchmarking Module
- Time measurements
- Key size analysis
- Ciphertext size analysis
- Graph generation

E. Educational Module
- Quantum threat explanation
- Shor’s algorithm explanation
- Lattice cryptography explanation

For each requirement include:
- Requirement ID
- Description
- Input
- Process
- Output

==================================================

6. NON-FUNCTIONAL REQUIREMENTS

Include:
- Security
- Scalability
- Maintainability
- Performance
- Reliability
- Portability
- Modularity
- Usability

Explain each in detail.

==================================================

7. SYSTEM REQUIREMENTS

A. Hardware Requirements
- CPU
- RAM
- Storage
- Network

B. Software Requirements
- Python version
- Node.js
- React
- FastAPI
- Libraries
- Operating systems

==================================================

8. FEASIBILITY STUDY

Generate:
A. Technical Feasibility
B. Economic Feasibility
C. Operational Feasibility

Explain why the project is practical for a B.Tech implementation.

==================================================

9. TECHNOLOGY STACK JUSTIFICATION

Explain WHY each technology is selected:
- React
- FastAPI
- AES
- RSA
- Kyber
- oqs-python
- SQLite

==================================================

10. LIMITATIONS OF THE SYSTEM

Explain limitations such as:
- Experimental PQC libraries
- No real quantum attack execution
- Simplified secure communication model
- Educational simulation limitations

==================================================

11. FUTURE SCOPE

Include:
- Hybrid PQC-TLS
- Dilithium signatures
- HTTPS integration
- Cloud deployment
- WebSocket encryption
- Enterprise security integration

==================================================

12. WATERFALL MODEL JUSTIFICATION

Explain:
- Why Waterfall is suitable
- Sequential development benefits
- Fixed requirements
- Modular cryptographic implementation

==================================================

13. EXPECTED OUTCOMES

Clearly explain:
- What the final system will demonstrate
- Security benefits
- Educational value
- Research contribution

==================================================

14. CONCLUSION

Generate a professional conclusion summarizing:
- quantum threat
- migration necessity
- role of lattice cryptography
- practical implementation goals