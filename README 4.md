# Lesson 3: Paul Graham Essays RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that can discuss Paul Graham's essays with context awareness.

## Requirements
- Python 3.11 (required)
- Pinecone account
- OpenAI API key

## Installation

1. Create a Python 3.11 virtual environment:
   ```bash
   python3.11 -m venv venv311
   source venv311/bin/activate  # On macOS/Linux
   # or
   .\venv311\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENV=your_environment
   PINECONE_INDEX=your_index_name
   ```

## Usage

1. First, process the PDFs (place your PDFs in the `pdfs/` directory):
   ```bash
   # To start fresh (recommended first time)
   python process_pdfs.py --reset

   # To add to existing index
   python process_pdfs.py
   ```

2. Run the chatbot:
   ```bash
   python pdf_agent_context.py
   ```

## Project Structure
- `pdf_agent_context.py` - Main chatbot with context handling
- `process_pdfs.py` - PDF processing and vectorization
- `pdfs/` - Directory for Paul Graham's essays (PDFs)
- `requirements.txt` - Project dependencies

## Troubleshooting
- If you get import errors, make sure you're using Python 3.11
- If the chatbot can't find documents, run `process_pdfs.py` first
- If you get API errors, check your environment variables 