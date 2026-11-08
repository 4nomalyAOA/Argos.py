import argparse
import asyncio
import sys
import os

# Add the 'src' directory to the path so it can find the others scripts
sys.path.append('src')
import scraper


def main():
    
    # Defining command lines arguments 
    parser.add_argument(
        "-u", "--url", 
        required = True, 
        help = "URL to scrape (e.g.: https://example.com)"
    )

    parser.add_argument(
        "-d", "--depth", 
        type = int, 
        default = 10, 
        help = "Number of others URLs found to scrape (default: 10)"
    )

    parser.add_argument(
        "--ai_model", 
        choices = ["chatgpt", "claude", "gemini", "mistral", "deepseek", "grok", "qwen", "grok", "ollama"],  
        help = "LLM model to export and analyze the JSON file"
    )

    parser.add_argument(
        "--tor", 
        action = "store_true", 
        help = "Enable Tor circuit rotation and tor proxy"
    )

    parser.add_argument(
        "--proxy",
        action = "store_true",
        help = "Use your own proxy for anonymity"
    )

    parser.add_argument(
        "-j", "--json", 
        default = "argos_report.json", 
        help = "Filename to save the JSON report"
    )

    parser.add_argument(
        "-i", "--images",
        help = "Your choice about saving the images found on the page"
    )


    args = parser.parse_args()
    print(f"[*] Starting Argos.py...")
    print(f"[*] Target: {args.url}")


    asyncio.run(scraper.main(args))
    print("[+] Argos scan simulation completed successfully!")

