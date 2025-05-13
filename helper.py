from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from openai import OpenAI
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO
import os
from pathlib import Path
import json
from send_mail import SendMail
from dotenv import load_dotenv
load_dotenv('.env')

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
client = OpenAI()
sender_email = os.environ.get("SENDER_EMAIL_ADDRESS")
sender_password = os.environ.get("SENDER_EMAIL_PASSWORD")

def get_email_by_username(username):
    with open('_secret_auth_.json') as f:
        json_data = json.load(f)
    for user in json_data:
        if user.get("username") == username:
            return user.get("email")
    return None

def send_pdf_email(receiver_email_id, pdf_file_path):
    new_mail = SendMail(
        [receiver_email_id], 
        'Report',
        'Detail report has been attached', 
        sender_email
    )
    new_mail.attach_files([pdf_file_path])
    new_mail.send(sender_password)

def add_text_and_image_to_pdf(pdf_path, text, image_path):
    # Create a buffer for the new content
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    # Add multiline text to the PDF
    text_x, text_y = 100, 450  # Starting position for the text
    text_object = can.beginText(text_x, text_y)
    text_object.setFont("Helvetica", 12)
    
    # Split the text into lines and add each line to the text object
    for line in text.splitlines():
        text_object.textLine(line)
    can.drawText(text_object)
    
    if Path(image_path).exists():
        image_x, image_y = 150, 700  # Position for the image
        image_width, image_height = 300, 450  # Size for the image
        can.drawImage(image_path, image_x, image_y, width=image_width, height=image_height)
    
    # Finalize the page content
    can.showPage()
    can.save()
    
    # Move the buffer content to a new PDF page
    packet.seek(0)
    new_pdf_page = PdfReader(packet)

    # Check if the PDF file exists
    if os.path.exists(pdf_path):
        # Append to existing PDF
        existing_pdf = PdfReader(pdf_path)
        output_pdf = PdfWriter()
        
        # Add all pages of the existing PDF
        for page_num in range(len(existing_pdf.pages)):
            output_pdf.add_page(existing_pdf.pages[page_num])
        
        # Add the new page with text and image
        output_pdf.add_page(new_pdf_page.pages[0])
    else:
        # Create a new PDF with the new page only
        output_pdf = PdfWriter()
        output_pdf.add_page(new_pdf_page.pages[0])

    # Write to the PDF file
    with open(pdf_path, "wb") as output_stream:
        output_pdf.write(output_stream)

def read_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        return None

def get_english_transcription(audio_file_path):
    audio_file= open(audio_file_path, "rb")
    translation = client.audio.translations.create(
    model="whisper-1", 
    file=audio_file
    )
    return translation.text

def create_agent(csv_file_path):
    agent_executor = create_csv_agent(
        llm,
        csv_file_path,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True,allow_dangerous_code=True
    )
    
    return agent_executor

if __name__ == '__main__':
    agent_executor = create_agent("titanic.csv")
    response = agent_executor.run("What is the average age of people in the dataset. Save the graph locally and return file name in double quotes?")
    print(response)