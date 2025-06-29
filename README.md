# 14,000+ Company Logos Scraper with Metadata

This repository contains a Python web scraping script that collects approximately **14,000 company logos** along with associated **metadata** (such as filename, title, description, keywords.).

---

## 📦 Features

- Scrapes high-resolution logo images
- Collects metadata (name, industry, etc.)
- Saves data in structured format (JSON or CSV)
- Can be extended to include additional fields

---

## 🛠️ Setup Instructions

### 1. Use Miniconda (Recommended)

For best compatibility and isolation, use [Miniconda](https://docs.conda.io/en/latest/miniconda.html):

```bash
# Create environment
conda create -n logoscraper python=3.10

# Activate environment
conda activate logoscraper

# Install dependencies
pip install -r requirements.txt
