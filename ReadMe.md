# Project Submission Document

## Project Title
**Diverciphy**

## Type
Distributed Stealth Network for Secure Data Transmission

## Course
CENG465 – Distributed Systems

## Course Lecturer
Dr. Hüseyin Temuçin

## Project Authors
* Ali Özen
* Said Berk

## Project Summary

In the contemporary cybersecurity landscape, traditional point-to-point encryption methods (such as
standard VPNs or TLS tunnels) present a static attack surface. Even when data is encrypted, the
transmission relies on a singular, traceable path, making it vulnerable to traffic analysis, Man-in-the-
Middle (MitM) attacks, and brute-force decryption attempts upon interception. This project proposes a
novel "Distributed Fragmented Data Transmission" architecture that fundamentally redefines endpoint
security by combining cryptographic payload shreding with multi-path topology obfuscation.
Unlike conventional solutions that merely encapsulate data, this architecture introduces a strict
"Intranet-to-Internet-to-Intranet" bridge protocol. The core innovation lies in the physical and logical
isolation of the source and destination endpoints. In this model, the source node (Endpoint A) never
interacts directly with the public internet. Instead, it resides within a secure local intranet,
communicating exclusively with a cluster of specialized "Proxy Gateway Nodes."


## Operational Mechanism

The data transmission process executes a "Cryptographic Atomization" strategy. Before leaving the
secure intranet perimeter, the source payload is encrypted and subsequently fragmented into discrete,
mathematically interdependent shreds. These shreds are distributed across distinct gateway nodes
(A1 through A5). Each gateway node operates on an independent operating system with a unique public
IP address, effectively decoupling the data stream from a single origin point.
Upon entering the public internet, these shreds are routed via disparate, randomized network paths to a
corresponding set of receiver gateways (B1 through B5). This approach mimics the principles of Spread
Spectrum radio technology applied to IP networks. A malicious actor intercepting a single transmission
line would capture only a fraction of the payload—a meaningless binary segment that is mathematically
impossible to decrypt without the remaining components. This enforces a "Strict Aggregation
Dependency," where the compromise of even  − 1 nodes fails to yield any intelligible data, rendering
brute-force attacks computationally futile.

The primary purpose of the Diverciphy is to provide developers with a seamless interface to
implement disjointed, multi-path data transmission without requiring deep expertise in complex
network topology management. The API functions as a secure bridge between the client application
(residing within a protected Intranet) and the external, hostile public network.
Upon receiving a data payload from the client application, the API performs a synchronous
cryptographic atomization process. Instead of encapsulating the data in a single packet, the API
executes a shreding algorithm that splits the encrypted payload into  distinct fragments (defaultingto a 5-node configuration). Crucially, the API manages the orchestration of sending these fragments to
a pre-authenticated cluster of local proxy nodes (A1 through A5). It handles the handshake protocols,
error checking, and routing logic required to disperse these fragments across divergent IP addresses
and operating systems. The API effectively decouples the data source from the transmission medium,
ensuring that the originating endpoint remains invisible to the public internet—a concept referred to
as the "Dark Node" architecture.



## System Architecture

The Diverciphy architecture is based on a multi-layered communication model:

- A **Dark Node** operating entirely within a secure intranet
- Multiple **Proxy Gateway Nodes** that act as controlled bridges to the public internet
- Fragmented, encrypted data shreds transmitted over heterogeneous paths

The Dark Node never directly communicates with the public internet. All outgoing and incoming data is handled through gateway nodes, each of which uses a different operating system, network configuration, and public IP address.

![alt text](figure1.png)
Figure 1: Architectural Design Scheme

---

## Data Fragmentation and Transmission

Before transmission, the payload is encrypted within the intranet. The encrypted payload is then divided into multiple mathematically dependent fragments. Each fragment alone is insufficient to reconstruct the original data.

These fragments are distributed across multiple gateway nodes and transmitted over separate network paths. On the receiving side, fragments are reassembled only after all required components are securely collected.

---

## Security Advantages

The proposed system provides several security benefits:

- Resistance to traffic analysis attacks
- Reduced effectiveness of man-in-the-middle attacks
- Obfuscation of source and destination endpoints
- Increased difficulty of long-term data harvesting attacks

Even if an adversary captures one or more fragments, the lack of complete fragment sets and dependency relationships prevents meaningful data recovery.

---

## Limitations

While Diverciphy improves stealth and resilience, it introduces additional latency and system complexity. The requirement for multiple gateway nodes and synchronized fragment management increases infrastructure overhead and operational costs.

![alt text](figure2.png)

Figure 2. Architectural Data Diagram

---

## Result

Diverciphy presents a novel approach to secure data transmission by combining encryption with distributed, multi-path network obfuscation. Rather than relying solely on cryptographic secrecy, the system leverages architectural and topological uncertainty to enhance overall security. This approach is particularly suitable for high-risk communication environments where metadata exposure poses a significant threat.

---

## Deployment

### Docker (Local Development)

To run the complete distributed system (Master Shredder, Master Assembler, and  Workers) locally:

```bash
docker-compose up --build
```

### Kubernetes (Production)

The system is designed to run on K8s with a StatefulSet for workers to ensure data persistence and stable network identities.

```bash
# 1. Build Image
docker build -t diverciphy:latest .

# 2. Apply Manifests
kubectl apply -f k8s/config_secret.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/statefulset.yaml
```

---

