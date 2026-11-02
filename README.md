# Argos: Asynchronous Web Data Extraction & OSINT Tool

Argos is an asynchronous web data extraction tool designed for optimized OSINT research and cybersecurity auditing[cite: 7].

### Key Features:
* **Evasion and anonymity:** Features the integration of hardened browser technologies using Camoufox[cite: 6], Tor circuit rotation (with the option to use a custom proxy configuration)[cite: 6, 7], and automated CAPTCHA detection/handling[cite: 6].
  
* **In-depth intelligence gathering:** Extracts metadata, HTTP security headers, visible and hidden links with recursive scraping capabilities[cite: 7, 8], contact details including international phone number geolocation and carrier lookup[cite: 7], and form inputs[cite: 7].
  
* **AI-powered reporting:** Seamlessly integrates generated JSON data structures with multiple LLM APIs (OpenAI, Claude, Gemini, DeepSeek, Ollama, etc.) for automated analysis and security report generation[cite: 5, 7].

### Note:
This project is currently in beta. 

### Python 3.15 Compatibility Note: 
Argos relies on low-level binary handling, C-extensions, and bytecode-dependent components (such as YAML parsers, Cdumper, and generation tools like fpgen). Due to major internal C-API modifications, memory layout updates, and bytecode instruction shifts in Python 3.15, these binary-dependent modules are currently incompatible. Please use Python 3.10 through 3.14.
