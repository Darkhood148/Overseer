# Overseer

**Overseer** is a command-line tool that searches Google using SerpAPI and analyzes the AI Overview block for mentions of a specified company. It reports whether the company is mentioned in headings, snippets, or references, and can print detailed metrics.

---

## Features

- Searches Google via SerpAPI with your query and (optionally) location.
- Extracts and analyzes the AI Overview block for company mentions.
- Reports presence and counts of company mentions in headings and references.
- Prints detailed metrics about the mentions.

---

## Setup

### 1. Clone the Repository

```
git clone https://github.com/Darkhood148/Overseer
cd overseer
```

### 2. Create and Activate a Virtual Environment
```
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Rename `.sample.env` to `.env`

Rename `.sample.env` to `.env` and specify your SerpAPI Key

## Usage

Run the Overseer CLI:

```
python overseer.py -q "your search query" -c "Company Name" [-l "Location"] [--metrics]


Arguments:

- `-q`, `--query` (required): The search query.
- `-c`, `--company` (required): The company name to look for.
- `-l`, `--location` (optional): Location for the search (e.g., "United States").
- `--metrics` (optional): Print detailed metrics of company mentions.
```

### Example:
![image](https://github.com/user-attachments/assets/f89bf899-0397-4492-9538-b6e1e559e0fd)

