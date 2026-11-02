# Argos Documentation

## Architecture & Workflow
Argos is structured into modular asynchronous components:
- **Scraper (`src/scraper.py`):** Handles core asynchronous fetching and recursive navigation.
- **Anti-Bot (`src/antiBotBypassing.py`):** Integrates Camoufox and Tor rotation.
- **Tools (`src/tools.py`):** Utility functions, phone geolocation, and header parsing.
- **AI Analyzer (`src/AI_analyzer.py`):** Formats output data into JSON and sends it to LLM APIs.
