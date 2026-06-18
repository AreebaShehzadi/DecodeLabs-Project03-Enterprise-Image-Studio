## **Enterprise Multimodal Image Studio**



This project is part of the DecodeLabs Internship (Project 3). It is an enterprise-grade multimodal AI application designed to translate natural language prompts into high-quality digital artwork using a visual generation API.



Unlike basic scripts, this project focuses heavily on resilience, memory safety, and file integrity to simulate a production-ready environment.



### **Key Architecture \& Features**



**Exact Aspect Ratio Mapping:** Dynamically translates user intent (e.g., "16:9", "1:1") into exact pixel payloads required by the API.



**Split-Timeout Timeline:** Implements a strict (3.05s, 60s) connection and read timeout to prevent the system from hanging on dead connections.



**Resilience via Exponential Backoff:** Uses Tenacity to gracefully handle server errors and network drops by retrying with randomized delays (jitter).



**Memory-Safe Streaming:** Uses chunked HTTP streaming (iter\_content) to write binary data directly to the disk, preventing RAM overflow with large high-resolution images.



**Rigorous Pixel-Level Decode:** Wraps the Pillow library's .load() method in a try-except block to force a complete pixel decode. This guarantees that corrupted or partially downloaded data streams are instantly detected and discarded.



### **Technologies Used**



Python 3.x



Requests (Chunked HTTP Streaming)



Pillow / PIL (Binary Integrity Verification)



Tenacity (Retry Logic)



Argparse (CLI Input)



### **How to Run**



Clone this repository to your local machine.



Install the required dependencies:



**pip install -r requirements.txt**





Run the generator from the terminal using custom arguments:



**python studio.py --prompt "A majestic lion wearing a golden crown sitting on a throne in a futuristic sci-fi palace, 8k resolution, cinematic lighting" --ratio "9:16" --output "royal\_lion.png"**





##### **Available Aspect Ratios**



16:9 (Landscape)



1:1 (Square)



9:16 (Vertical)

