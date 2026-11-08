# How To Use Argos

This guide covers everything you need to know to run and use efficiently Argos.py.

---

## 1. Setting up the environment

Make sure you are using Python 3.10 through 3.14.

Install the required dependencies:
pip install -r requirements.txt

---

## 2. First Execution 

By default, Argos leverages a proxy to ensure anonymity and IP rotation. Ensure your local Tor or proxy service is running, then launch the main script:
python src/scraper.py
or easier:
# Launch a basic script with claude analyzing
python argos.py --url https://example.com --tor --ai_model claude

# More specified analyze
python argos.py --url https://example.com --depth 5 --json test.json --images images
 
---

## 3. Configuration 

Depending on your operational requirements, you can adjust your setup using the templates provided in the examples/ directory:

- Without Authentication (Open Proxies): Configure your network parameters following examples/example_proxy_no_auth.json.
- With Authentication (Paid / Secured Proxies): Use examples/example_proxy_auth.json by providing your custom username and password.
- Session Persistence: Load and save your browser cookies and storage states using the structure defined in examples/example_session.json. Every time you visit a page, the cookies will be saved in session.json and if this file doesn't exist, it'll be created automatically.
