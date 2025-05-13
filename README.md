# CSV-Analysing-Tool
This CSV file contains the structured dataset used in this project. It was curated, cleaned, and analyzed to support data-driven insights and model development. The dataset has been processed using Python libraries such as Pandas, NumPy, and Matplotlib for efficient analysis and visualization.This project is an intelligent data assistant system built using Python, designed to help users upload, clean, and explore CSV files. It supports natural language queries in both text and audio, and generates visualizations and reports using advanced AI tools and libraries.

🔧 Key Features
📤 CSV Upload: Users can upload their dataset in .csv format.

🧹 Data Cleaning: Automated data cleaning using Pandas, including handling missing values, duplicates, and formatting issues.

📄 File Description: The system provides an auto-generated overview of the uploaded file, including column types and summary statistics.

🗣️ Natural Language Querying:

Supports both text and audio queries.

Accepts queries in any language using OpenAI Whisper for speech-to-text and translation.

📊 Data Visualization: Automatically visualizes data using Matplotlib, with charts like histograms, bar plots, and line graphs based on user queries.

🧾 Report Generation:

Generates a clean, structured PDF report using PyPDF2.

Includes data insights, visualizations, and query responses.

🤖 AI-Powered Query Responses:

Uses OpenAI GPT to understand and answer user queries based on the uploaded dataset.

Delivers responses in a clear, human-readable format.

🛠️ Tech Stack
Python

Pandas – Data handling and cleaning

OpenAI Whisper – Audio transcription and multilingual support

Matplotlib – Data visualization

OpenAI GPT – Query understanding and smart responses

PyPDF2 – PDF report generation

📌 How It Works
User uploads a CSV file

The system cleans and describes the data

User can ask questions in text or audio

Whisper handles speech-to-text; GPT handles query logic

Results are visualized and displayed

A final report is generated as a downloadable PDF

