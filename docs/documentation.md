# Argos Documentation

## Architecture & Workflow

Argos is structured into four modular asynchronous components:

- **Scraper (`src/scraper.py`):** Handles core asynchronous fetching, recursive crawling, and raw data aggregation.
  
- **Anti-Bot (`src/antiBotBypassing.py`):** Integrates Camoufox and Tor rotation to maintain a low digital footprint and bypass modern detection mechanisms.
  
- **Tools (`src/tools.py`):** Contains utility functions, HTTP header parsing logic, and helper features (such as downloading tools).
  
- **AI Analyzer (`src/AI_analyzer.py`):** Structures extracted raw data into standardized JSON formats and interfaces with LLM APIs for automated intelligence analysis.

- **Argos.py:** Script to lauch the script with options on a single line: python3 argos.py --url <URL> [OPTIONS]
