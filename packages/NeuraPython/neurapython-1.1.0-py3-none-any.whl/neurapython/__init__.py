from ftplib import FTP as FTPClient
import os
import qrcode
import torch
import tensorflow as tf
import types
import threading
import base64
import binascii
import urllib.parse
import codecs
import numpy as np
import pandas as pd
import joblib
from math import *
from sklearn import (
    datasets, preprocessing, model_selection, metrics,
    linear_model, tree, neighbors, svm, ensemble, cluster,
    decomposition
)
from flask import *
import numpy as np
import sqlite3
import webbrowser
import pyttsx3
import matplotlib.pyplot as plt
import speech_recognition as sr
import pandas as pd
import pygame 
from PIL import Image
import cv2
import math
import calendar
import datetime
import requests
from docx import Document
import json
import pdfplumber
from bs4 import BeautifulSoup
import pdf2docx
import docx2pdf
import fitz
from fpdf import FPDF
import markdown
from sympy import symbols, Function, diff, integrate, limit, series, summation, Eq, dsolve, sympify, Matrix
from sympy.vector import CoordSys3D, divergence, curl

#__________________________Web searches___________________________

def search_chrome(thing):
    webbrowser.open(rf"https://www.google.com/search?q={thing}")
def search_youtube(thing):
    webbrowser.open(fr"https://www.youtube.com/results?search_query={thing}")
def open_whatsapp():
    webbrowser.open("https://wa.me/")
def open_whatsapp_chat(phone_number:str,message:str="Hi"):
    webbrowser.open(fr"https://wa.me/{phone_number}?text={message}")
def open_other(link):
    webbrowser.open(f"https://www.google.com/search?q={link}")

#________________________Graph Plot_______________________________
class Visualizer2D():
    def __init__(self,x:list=[],y:list=[],title="NeuraPy Graphs",x_label="X-Axis",y_label="Y-Axis"):
        self.x=x
        self.y=y
        self.title=title
        self.x_label=x_label
        self.y_label=y_label
    def bar_graph(self):
        plt.bar(self.x,self.y)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
    def pie_chart(self):
        plt.pie(self.y,labels=self.x,radius=1)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
    def line_graph(self):
        plt.plot(self.x,self.y)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
    def scatter_graph(self):
        plt.scatter(self.x, self.y)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
    def HorizontalBar_chart(self):
        plt.barh(self.x, self.y)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
    def show(self):
        plt.show()


#____________________________3D Graphs_____________________________
class Visualizer3D():
    def __init__(self,x=[],y=[],z=[],title="NeuraPy 3D",x_label="X-Axis",y_label="Y-Axis",z_label="Z-Axis"):
        self.x=x
        self.y=y
        self.z=z
        self.title=title
        self.x_label=x_label
        self.y_label=y_label
        self.z_label=z_label
    def plot(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(self.x, self.y, self.z)
        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        ax.set_zlabel(self.z_label)
    def show(self):
        plt.show()
#_______________________Speech____________________________________
def speak(text="Hi I am Neura Python"):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    
    
def voice_input(message="Please say Something: "):
    r = sr.Recognizer()

    
    with sr.Microphone() as source:
        print(message)
        r.adjust_for_ambient_noise(source) 
        audio = r.listen(source)

    try:
        
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand your voice.")
    except sr.RequestError:
        print("Could not request results; check your internet connection.")




class WebServer:
    def __init__(self):
        self.app = Flask(__name__)

# -------------------------------------------------------------------
# Basic Route Handler
# -------------------------------------------------------------------
    def simple_route(self, route='/', code="NeuraPy web app", html_file_path=""):
        @self.app.route(route)
        def webpage():
            if html_file_path:
                if os.path.exists(html_file_path):
                    with open(html_file_path, "r", encoding="utf-8") as f:
                        return f.read()
                else:
                    return "No file found"
            else:
                return code or "No content provided"

# -------------------------------------------------------------------
# Error Handler
# -------------------------------------------------------------------
    def error_handler(self, error_code, code="NeuraPy Error Page", error_page_html=""):
        @self.app.errorhandler(error_code)
        def error(e):
            if error_page_html and os.path.exists(error_page_html):
                with open(error_page_html, "r", encoding="utf-8") as f:
                    return f.read(), error_code
            else:
                return code or f"Error {error_code}", error_code

# -------------------------------------------------------------------
# JSON Verification (for API login/auth routes)
# -------------------------------------------------------------------
    def verify_details(self, route='/', user_data=[], verify_data_from=[]):
        @self.app.route(route, methods=['POST'])
        def verify():
            data = request.get_json(force=True)
            if not data:
                return jsonify({"response": False, "error": "No JSON received"})
            
            if len(user_data) != len(verify_data_from):
                return jsonify({"response": False, "error": "Mismatch in data length"})
            
            validation = []
            for i in range(len(user_data)):
                received = data.get(user_data[i])
                expected = verify_data_from[i]
                validation.append(received == expected)
            
            if all(validation):
                return jsonify({"response": True})
            else:
                return jsonify({"response": False})

# -------------------------------------------------------------------
# SQLite Database Setup
# -------------------------------------------------------------------
    def DataBase(self, db_path="neurapy.db", query=None):
        if not query:
            query = """
                CREATE TABLE IF NOT EXISTS NeuraPy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    email TEXT UNIQUE
                );
            """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

# -------------------------------------------------------------------
# Database Operations
# -------------------------------------------------------------------
    def insert_data(self, db_path, table, data: dict):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cols = ', '.join(data.keys())
        vals = tuple(data.values())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cursor.execute(query, vals)
        conn.commit()
        conn.close()
        return jsonify({"status": "Data inserted successfully"})

    def retrieve_data_from_db(self, db_path, query):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)

    def delete_data(self, db_path, table, condition):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"DELETE FROM {table} WHERE {condition}"
        cursor.execute(query)
        conn.commit()
        conn.close()
        return jsonify({"status": "Record deleted"})

# -------------------------------------------------------------------
# File Upload Endpoint
# -------------------------------------------------------------------
    def file_upload(self, route='/upload', upload_folder='uploads'):
        os.makedirs(upload_folder, exist_ok=True)

        @self.app.route(route, methods=['POST'])
        def upload():
            if 'file' not in request.files:
                return jsonify({"error": "No file part"})
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"})
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            return jsonify({"success": True, "path": file_path})

# -------------------------------------------------------------------
# Serve Static Files
# -------------------------------------------------------------------
    def serve_file(self, route='/file', file_path=""):
        @self.app.route(route)
        def serve():
            if os.path.exists(file_path):
                return send_file(file_path)
            return "File not found", 404

# -------------------------------------------------------------------
# Run Server
# -------------------------------------------------------------------
    def run(self, live_refresh: bool = True, port=5200):
        self.app.run(debug=live_refresh, host='0.0.0.0', port=port)
    
    
    
    
#_____________________________Databases_______________________________
class Database():
    def create(self,path_of_db,name_of_table="Default_Table",columns=[{"name":"ID","datatype":"INT","constraint":""},{"name":"Name","datatype":"TEXT","constraint":""}]):
        conn=sqlite3.connect(fr"{path_of_db}")
        cursor=conn.cursor()
        cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {name_of_table} ({columns[0].get("name")} {columns[0].get("datatype")} {columns[0].get("constraint")});
                """)
        for i in range(1,len(columns)):
            conn.execute(f"""
                        
                        ALTER TABLE {name_of_table}
                        ADD {columns[i].get("name")} {columns[i].get("datatype")} {columns[i].get("constraint")};
                        """)
        conn.commit()
        conn.close()
    def retrieve_data(self,path_of_db,name_of_table):
        conn=sqlite3.connect(path_of_db)
        cursor=conn.cursor()
        cursor.execute(f"""
                    SELECT * FROM {name_of_table}
                    """)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        result = [dict(zip(column_names, row)) for row in rows]
        conn.close()
        return result
    

        
    def run_query(self,path_of_db,name_of_table,query):
        conn=sqlite3.connect(path_of_db)
        cursor=conn.cursor()
        cursor.execute(f"""
                    
                    {query.format(table=name_of_table)}
                    """)
        conn.commit()
        conn.close()
    
    
    def insert_data(self, path_of_db, name_of_table,data={"ID": [1, 2, 3, 4, 5],"Name": ["Name1", "Name2", "Name3", "Name4", "Name5"]}):
    
        conn = sqlite3.connect(path_of_db)
        cursor = conn.cursor()
        
        columns = list(data.keys())
        rows = len(data[columns[0]])  # Number of entries
        
        for j in range(rows):
            # Collect row values
            values = []
            for col in columns:
                val = data[col][j]
                if isinstance(val, str):
                    val = f'"{val}"'  # Add quotes for strings
                values.append(str(val))
            
            cursor.execute(f"""
                INSERT INTO {name_of_table} ({', '.join(columns)})
                VALUES ({', '.join(values)});
            """)
        
        conn.commit()
        conn.close()
        
#________________________________Media_____________________________________

class Media():
    def image(self,path_of_image,width,height,title="NeuraPy Image"):
        img = Image.open(path_of_image)
        img = img.resize((width, height))
        plt.imshow(img)
        plt.title(title)
        plt.axis('off')
        plt.show()
        
    def audio(self,path_of_audio):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(path_of_audio)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing audio: {e}")
    def video(self,path_of_video,width,height):
        cap = cv2.VideoCapture(path_of_video)
        if not cap.isOpened():
            print("Error: Cannot open video.")
            return
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (width, height))
            cv2.imshow('Video', frame)
            
            # 'q' to quit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()




#________________________________Machine Learning_________________________

#__________________________________AI_________________________________________
class AI:
    def google_gemini(self, api_key, model, prompt):
        """
        Send a prompt to Google Gemini API and return the reply.
        """
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error (Gemini): {e}"

    def openai_chatgpt(self, api_key, model, prompt):
        """
        Send a prompt to OpenAI ChatGPT API and return the reply.
        """
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error (ChatGPT): {e}"

#___________________________________Vectors______________________________________



class Vector2D:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"
    def to_list(self):
        return [self.x,self.y]

    def add(self, *vectors):
        new_x, new_y = self.x, self.y
        for v in vectors:
            new_x += v.x
            new_y += v.y
        return Vector2D(new_x, new_y)

    def subtract(self, *vectors):
        new_x, new_y = self.x, self.y
        for v in vectors:
            new_x -= v.x
            new_y -= v.y
        return Vector2D(new_x, new_y)


    @staticmethod
    def dot_product(v1, v2):
        return v1.x * v2.x + v1.y * v2.y


    @staticmethod
    def cross_product(v1, v2):
        return v1.x * v2.y - v1.y * v2.x

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit_vector(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot compute unit vector of zero vector.")
        return Vector2D(self.x / mag, self.y / mag)

    @staticmethod
    def angle_between(v1, v2 ,angle:bool=True):
        dot = Vector2D.dot_product(v1, v2)
        mag1 = v1.magnitude()
        mag2 = v2.magnitude()
        if mag1 == 0 or mag2 == 0:
            raise ValueError("Cannot compute angle with zero-length vector.")
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(-1, min(1, cos_theta))
        if angle:
            return math.degrees(math.acos(cos_theta))
        else:
            return math.acos(cos_theta)
    
    @classmethod
    def from_list(cls, data):
        if len(data) != 2:
            raise ValueError("List must contain exactly 2 values.")
        return cls(data[0], data[1])




class Vector3D:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"


    def add(self, *vectors):
        new_x, new_y, new_z = self.x, self.y, self.z
        for v in vectors:
            new_x += v.x
            new_y += v.y
            new_z += v.z
        return Vector3D(new_x, new_y, new_z)


    def subtract(self, *vectors):
        new_x, new_y, new_z = self.x, self.y, self.z
        for v in vectors:
            new_x -= v.x
            new_y -= v.y
            new_z -= v.z
        return Vector3D(new_x, new_y, new_z)

    @staticmethod
    def dot_product(v1, v2):
        return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z

    @staticmethod
    def cross_product(v1, v2):
        cx = v1.y * v2.z - v1.z * v2.y
        cy = v1.z * v2.x - v1.x * v2.z
        cz = v1.x * v2.y - v1.y * v2.x
        return Vector3D(cx, cy, cz)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit_vector(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("Cannot compute unit vector of zero vector.")
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    @staticmethod
    def angle_between(v1, v2, degrees=True):
        dot = Vector3D.dot_product(v1, v2)
        mag1 = v1.magnitude()
        mag2 = v2.magnitude()
        if mag1 == 0 or mag2 == 0:
            raise ValueError("Cannot compute angle with zero-length vector.")
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(-1, min(1, cos_theta))
        angle = math.acos(cos_theta)
        return math.degrees(angle) if degrees else angle

    def to_list(self):
        return [self.x, self.y, self.z]

    @classmethod
    def from_list(cls, data):
        if len(data) != 3:
            raise ValueError("List must contain exactly 3 values.")
        return cls(data[0], data[1], data[2])
        
#_____________________________Calender_________________________________
def Calender(year=None, month=None):
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    cal = calendar.month(year, month)
    print(cal)


#_________________________Readers_____________________________________
class Reader():
    def html_reader(self,path):
        with open(rf"{path}","r",encoding="utf-8") as html:
            content=html.read()
        return content
    
    def excel_reader(self,path):
        data=pd.read_excel(rf"{path}")
        return data.to_string()
    
    def docx_reader(self,path):
        doc = Document(path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def json_reader(self,path):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)  
        return data
    
    def csv_reader(self,path):
        data=pd.read_csv(rf"{path}")
        return data.to_string()
    
    def text_reader(self,path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()  
        return content
    
    def pdf_reader(self,path):
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    def markdown_reader(self,path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()  # Read as plain text
        return content
    def xml_reader(self,path):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'xml')
        return soup.prettify()
#___________________________Converters_____________________________
class Converter():
    def pdf_to_docx(self,pdf_path,docx_path):
        cv = pdf2docx.Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
    
    def docx_to_pdf(self,docx_path,pdf_path):
        docx2pdf.convert(docx_path, pdf_path)

    def pdf_to_text(self,pdf_path,txt_path):
        pdf = fitz.open(pdf_path)
        text = ""

        for page in pdf:
            text += page.get_text("text") + "\n"

        pdf.close()

        if txt_path:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
    
    def text_to_pdf(self,txt_path,pdf_path):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        pdf.multi_cell(0, 10, text)
        pdf.output(pdf_path)
        
    def excel_to_csv(self,excel_path,csv_path):
        df = pd.read_excel(excel_path)
        df.to_csv(csv_path, index=False)
        
    def csv_to_excel(self,csv_path,xlsx_path):
        df = pd.read_csv(csv_path)
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        
    def json_to_csv(self,json_path,csv_path):
        df = pd.read_json(json_path)
        df.to_csv(csv_path, index=False)
        
    def json_to_excel(self,json_path,excel_path):
        data = pd.read_json(json_path)
        data.to_excel(excel_path, index=False)
        
    def csv_to_json(self,csv_path,json_path):
        data = pd.read_csv(csv_path)
        data.to_json(json_path, orient="records", indent=4)
        
    def excel_to_json(self,excel_path,json_path):
        data = pd.read_excel(excel_path)
        data.to_json(json_path, orient="records", indent=4)
    def markdown_to_html(self,markdown_path,html_path):
        with open(markdown_path, "r", encoding="utf-8") as md_file:
            md_content = md_file.read()

        html_content = markdown.markdown(md_content, extensions=[
        "fenced_code",  # ``` code blocks ```
        "tables",       # Markdown tables
        "attr_list"     # Attributes like {: .class }
        ])

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{markdown_path}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            background-color: #fafafa;
        }}
        pre, code {{
            background: #f5f5f5;
            padding: 5px;
            border-radius: 4px;
        }}
        table {{
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        with open(html_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_template)

#__________________________Calculus_______________________________
class Calculus:
    def __init__(self):
        from sympy import symbols, sin, cos

    # 1️⃣ Derivative
    def derivative(self, expr, var='x', order=1):
        x = symbols(var)
        expr = sympify(expr)
        return diff(expr, x, order)

    # 2️⃣ Integral
    def integral(self, expr, var='x', lower=None, upper=None):
        x = symbols(var)
        expr = sympify(expr)
        if lower is not None and upper is not None:
            return integrate(expr, (x, lower, upper))
        return integrate(expr, x)

    # 3️⃣ Limit
    def calc_limit(self, expr, var='x', point=0):
        x = symbols(var)
        expr = sympify(expr)
        return limit(expr, x, point)

    # 4️⃣ Partial Derivative
    def partial_derivative(self, expr, var):
        expr = sympify(expr)
        return diff(expr, symbols(var))

    # 5️⃣ Gradient
    def gradient(self, expr, vars_list):
        vars = symbols(vars_list)
        expr = sympify(expr)
        return Matrix([diff(expr, v) for v in vars])


    # 7️⃣ Curl
    def calc_curl(self, Fx, Fy, Fz):
        N = CoordSys3D('N')
        Fx, Fy, Fz = sympify(Fx), sympify(Fy), sympify(Fz)
        F = Fx * N.i + Fy * N.j + Fz * N.k
        return curl(F)

    # 8️⃣ Taylor / Maclaurin Series
    def taylor_series(self, expr, var='x', point=0, n=5):
        x = symbols(var)
        expr = sympify(expr)
        return series(expr, x, point, n)

    # 9️⃣ Summation
    def summation_func(self, expr, var='n', start=1, end=10):
        n = symbols(var)
        expr = sympify(expr)
        return summation(expr, (n, start, end))

    # 🔟 Differential Equation Solver (fixed)
    def solve_diff_eq(self, equation, var='x'):
        x = symbols(var)
        y = Function('y')
        expr = sympify(equation)  # ✅ FIXED: parse string to symbolic expression
        eq = Eq(y(x).diff(x), expr)
        return dsolve(eq)

    # 11️⃣ Jacobian Matrix
    def jacobian_matrix(self, funcs, vars_list):
        vars = symbols(vars_list)
        f = Matrix([sympify(fn) for fn in funcs])
        return f.jacobian(vars)

    # 12️⃣ Hessian Matrix
    def hessian_matrix(self, expr, vars_list):
        vars = symbols(vars_list)
        f = sympify(expr)
        return Matrix([[diff(f, vi, vj) for vj in vars] for vi in vars])

#__________________________Matrices_____________________________
class Matrices:
    def __init__(self, data: list):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0]) if data else 0

    def shape(self):
        return (self.rows, self.cols)

    def size(self):
        return self.rows * self.cols

    def copy(self):
        return Matrices([row[:] for row in self.data])

    def add(self, other):
        # Element-wise addition
        return Matrices([
            [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def subtract(self, other):
        return Matrices([
            [self.data[i][j] - other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def multiply(self, other):
        # Matrix multiplication (not element-wise)
        result = [
            [sum(self.data[i][k] * other.data[k][j] for k in range(self.cols))
             for j in range(other.cols)]
            for i in range(self.rows)
        ]
        return Matrices(result)

    def scalar_multiply(self, value):
        return Matrices([
            [self.data[i][j] * value for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def transpose(self):
        return Matrices([
            [self.data[j][i] for j in range(self.rows)]
            for i in range(self.cols)
        ])

    def determinant(self):
        if self.rows != self.cols:
            raise ValueError("Determinant only defined for square matrices")
        if self.rows == 1:
            return self.data[0][0]
        if self.rows == 2:
            return self.data[0][0]*self.data[1][1] - self.data[0][1]*self.data[1][0]
        det = 0
        for c in range(self.cols):
            minor = [row[:c] + row[c+1:] for row in self.data[1:]]
            det += ((-1)**c) * self.data[0][c] * Matrices(minor).determinant()
        return det

    def inverse(self):
        det = self.determinant()
        if det == 0:
            raise ValueError("Matrix is singular and cannot be inverted")
        if self.rows == 2:
            a, b = self.data[0]
            c, d = self.data[1]
            inv = [[d, -b], [-c, a]]
            return Matrices(inv).scalar_multiply(1/det)
        cofactors = []
        for r in range(self.rows):
            cofactor_row = []
            for c in range(self.cols):
                minor = [row[:c] + row[c+1:] for i, row in enumerate(self.data) if i != r]
                cofactor_row.append(((-1)**(r+c)) * Matrices(minor).determinant())
            cofactors.append(cofactor_row)
        cofactors = Matrices(cofactors).transpose()
        return cofactors.scalar_multiply(1/det)

    def is_square(self):
        return self.rows == self.cols

    def flatten(self):
        return [x for row in self.data for x in row]

    def trace(self):
        return sum(self.data[i][i] for i in range(min(self.rows, self.cols)))

    def rank(self):
        import numpy as np
        return np.linalg.matrix_rank(self.data)

    def power(self, n):
        if not self.is_square():
            raise ValueError("Matrix must be square for power operation")
        result = Matrices.identity(self.rows)
        for _ in range(n):
            result = result.multiply(self)
        return result

    @staticmethod
    def identity(n):
        return Matrices([[1 if i == j else 0 for j in range(n)] for i in range(n)])

    def __str__(self):
        return '\n'.join(['\t'.join(map(str, row)) for row in self.data])
#____________________________________Machine Learning_________________________________________
# ===========================================================
# ⚙️ NeuraPython_ML — Unified Scikit-learn Wrapper
# Author: Ibrahim Shahid
# ===========================================================

import numpy as np
import pandas as pd
import joblib

from sklearn import (
    datasets, preprocessing, model_selection, metrics,
    linear_model, tree, neighbors, svm, ensemble, cluster,
    decomposition
)

class NeuraPython_ML:
    def __init__(self):
        print("🧠 NeuraPython_ML initialized ")
        self.models = {}
        self.scaler = None
        self.encoder = None

# -----------------------------------------------------------
# 📥 DATASET LOADING
# -----------------------------------------------------------
    def load_builtin_dataset(self, name="iris"):
        name = name.lower()
        if name == "iris": data = datasets.load_iris()
        elif name == "digits": data = datasets.load_digits()
        elif name == "wine": data = datasets.load_wine()
        elif name == "breast_cancer": data = datasets.load_breast_cancer()
        else: raise ValueError("❌ Unknown dataset name.")
        return pd.DataFrame(data.data, columns=data.feature_names), data.target

# -----------------------------------------------------------
# 🔢 DATA PREPROCESSING
# -----------------------------------------------------------
    def normalize(self, X):
        self.scaler = preprocessing.Normalizer()
        return self.scaler.fit_transform(X)

    def standardize(self, X):
        self.scaler = preprocessing.StandardScaler()
        return self.scaler.fit_transform(X)

    def minmax_scale(self, X):
        self.scaler = preprocessing.MinMaxScaler()
        return self.scaler.fit_transform(X)

    def encode_labels(self, y):
        self.encoder = preprocessing.LabelEncoder()
        return self.encoder.fit_transform(y)

    def one_hot_encode(self, X):
        return preprocessing.OneHotEncoder().fit_transform(X).toarray()

# -----------------------------------------------------------
# 📊 TRAIN/TEST SPLIT
# -----------------------------------------------------------
    def split(self, X, y, test_size=0.2, random_state=42):
        return model_selection.train_test_split(X, y, test_size=test_size, random_state=random_state)

# -----------------------------------------------------------
# 🤖 MODEL CREATION (Unified Interface)
# -----------------------------------------------------------
    def create_model(self, model_name, **kwargs):
        name = model_name.lower()
        if name == "linear_regression": model = linear_model.LinearRegression(**kwargs)
        elif name == "logistic_regression": model = linear_model.LogisticRegression(**kwargs)
        elif name == "decision_tree": model = tree.DecisionTreeClassifier(**kwargs)
        elif name == "random_forest": model = ensemble.RandomForestClassifier(**kwargs)
        elif name == "svm": model = svm.SVC(**kwargs)
        elif name == "knn": model = neighbors.KNeighborsClassifier(**kwargs)
        elif name == "gradient_boosting": model = ensemble.GradientBoostingClassifier(**kwargs)
        elif name == "naive_bayes": 
            from sklearn.naive_bayes import GaussianNB
            model = GaussianNB(**kwargs)
        elif name == "kmeans": model = cluster.KMeans(**kwargs)
        elif name == "pca": model = decomposition.PCA(**kwargs)
        else:
            raise ValueError(f"❌ Unsupported model: {model_name}")
        
        self.models[model_name] = model
        print(f"✅ Model '{model_name}' created.")
        return model

# -----------------------------------------------------------
# 🧩 MODEL TRAINING & PREDICTION
# -----------------------------------------------------------
    def train(self, model_name, X_train, y_train):
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"❌ Model '{model_name}' not found.")
        model.fit(X_train, y_train)
        print(f"🚀 Model '{model_name}' trained successfully.")
        return model

    def predict(self, model_name, X_test):
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"❌ Model '{model_name}' not found.")
        return model.predict(X_test)

# -----------------------------------------------------------
# 📈 MODEL EVALUATION
# -----------------------------------------------------------
    def evaluate(self, y_true, y_pred):
        return {
            "accuracy": metrics.accuracy_score(y_true, y_pred),
            "precision": metrics.precision_score(y_true, y_pred, average='weighted', zero_division=0),
            "recall": metrics.recall_score(y_true, y_pred, average='weighted', zero_division=0),
            "f1_score": metrics.f1_score(y_true, y_pred, average='weighted', zero_division=0)
        }

    def confusion_matrix(self, y_true, y_pred):
        return metrics.confusion_matrix(y_true, y_pred)

    def classification_report(self, y_true, y_pred):
        return metrics.classification_report(y_true, y_pred)

# -----------------------------------------------------------
# 🧮 DIMENSIONALITY REDUCTION
# -----------------------------------------------------------
    def apply_pca(self, X, n_components=2):
        pca = decomposition.PCA(n_components=n_components)
        return pca.fit_transform(X)

# -----------------------------------------------------------
# 💾 MODEL SAVING & LOADING
# -----------------------------------------------------------
    def save_model(self, model_name, path):
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"❌ Model '{model_name}' not found.")
        joblib.dump(model, path)
        print(f"💾 Model '{model_name}' saved at {path}")

    def load_model(self, path, model_name="loaded_model"):
        model = joblib.load(path)
        self.models[model_name] = model
        print(f"📂 Model '{model_name}' loaded from {path}")
        return model

# -----------------------------------------------------------
# 🧠 CROSS VALIDATION & GRID SEARCH
# -----------------------------------------------------------
    def cross_validate(self, model, X, y, cv=5):
        scores = model_selection.cross_val_score(model, X, y, cv=cv)
        return {"mean": np.mean(scores), "scores": scores}

    def grid_search(self, model, params, X, y, cv=5):
        search = model_selection.GridSearchCV(model, params, cv=cv)
        search.fit(X, y)
        return search.best_estimator_, search.best_params_, search.best_score_

# -----------------------------------------------------------
# 🔍 CLUSTERING UTILITIES
# -----------------------------------------------------------
    def kmeans_cluster(self, X, n_clusters=3):
        model = cluster.KMeans(n_clusters=n_clusters)
        y_pred = model.fit_predict(X)
        return model, y_pred

# -----------------------------------------------------------
# 🧩 FEATURE SELECTION
# -----------------------------------------------------------
    def feature_importances(self, model_name, feature_names=None):
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"❌ Model '{model_name}' not found.")
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            if feature_names is not None:
                return dict(zip(feature_names, imp))
            return imp
        else:
            raise AttributeError("⚠️ Model has no feature_importances_ attribute.")

# -----------------------------------------------------------
# 🧾 SUMMARY
# -----------------------------------------------------------
    def summary(self):
        print("=== NeuraPython_ML Models ===")
        for name, model in self.models.items():
            print(f"• {name}: {type(model).__name__}")

#_______________________________________Neural Network________________________________________


class NeuralNetwork:
    def __init__(self, backend='torch', device=None):
        self.backend = backend.lower()
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None

        if self.backend not in ['torch', 'tf']:
            raise ValueError("Backend must be 'torch' or 'tf'")

        # dynamically attach all functions and submodules
        self._attach_backend()

    # -------------------------------------------------------------------------
    # Attach backend attributes dynamically
    # -------------------------------------------------------------------------
    def _attach_backend(self):
        """Attach TensorFlow or Torch modules as attributes for universal access."""
        if self.backend == 'torch':
            self.tensor_lib = torch
            self.nn = torch.nn
            self.optim = torch.optim
            self.utils = torch.utils
            self.vision = None
        else:
            self.tensor_lib = tf
            self.nn = tf.keras.layers
            self.optim = tf.keras.optimizers
            self.losses = tf.keras.losses
            self.metrics = tf.keras.metrics

    # -------------------------------------------------------------------------
    # Universal tensor creator
    # -------------------------------------------------------------------------
    def tensor(self, data, dtype=None, requires_grad=False):
        if self.backend == 'torch':
            return torch.tensor(data, dtype=dtype or torch.float32, requires_grad=requires_grad).to(self.device)
        elif self.backend == 'tf':
            return tf.convert_to_tensor(data, dtype=dtype or tf.float32)

    # -------------------------------------------------------------------------
    # Universal model creation
    # -------------------------------------------------------------------------
    def Sequential(self, layers_list):
        """Create a simple sequential model compatible with backend."""
        if self.backend == 'torch':
            seq_layers = []
            for i in range(len(layers_list) - 1):
                seq_layers.append(torch.nn.Linear(layers_list[i], layers_list[i + 1]))
                if i < len(layers_list) - 2:
                    seq_layers.append(torch.nn.ReLU())
            self.model = torch.nn.Sequential(*seq_layers).to(self.device)
        else:
            self.model = tf.keras.Sequential()
            for i in range(len(layers_list) - 1):
                self.model.add(tf.keras.layers.Dense(
                    layers_list[i + 1],
                    input_dim=layers_list[i] if i == 0 else None,
                    activation='relu' if i < len(layers_list) - 2 else None
                ))

    # -------------------------------------------------------------------------
    # Universal compile/train/predict
    # -------------------------------------------------------------------------
    def compile(self, optimizer='adam', loss='mse'):
        if self.backend == 'torch':
            self.loss_fn = torch.nn.MSELoss() if loss == 'mse' else loss
            self.optimizer = torch.optim.Adam(self.model.parameters()) if optimizer == 'adam' else optimizer
        else:
            self.model.compile(optimizer=getattr(tf.keras.optimizers, optimizer.capitalize())(),
                               loss=loss)

    def fit(self, X, y, epochs=5):
        if self.backend == 'torch':
            X = self.tensor(X)
            y = self.tensor(y)
            for epoch in range(epochs):
                self.optimizer.zero_grad()
                preds = self.model(X)
                loss = self.loss_fn(preds, y)
                loss.backward()
                self.optimizer.step()
                print(f"[Torch] Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        else:
            self.model.fit(X, y, epochs=epochs, verbose=1)

    def predict(self, X):
        if self.backend == 'torch':
            with torch.no_grad():
                preds = self.model(self.tensor(X))
            return preds.cpu().numpy()
        else:
            return self.model.predict(X)

    # -------------------------------------------------------------------------
    # Dynamic universal access
    # -------------------------------------------------------------------------
    def __getattr__(self, name):
        """Dynamic universal access to backend functions and submodules."""
        try:
            if hasattr(self.tensor_lib, name):
                return getattr(self.tensor_lib, name)
            elif self.backend == 'torch' and hasattr(torch.nn, name):
                return getattr(torch.nn, name)
            elif self.backend == 'tf':
                # check keras modules
                if hasattr(tf.keras.layers, name):
                    return getattr(tf.keras.layers, name)
                if hasattr(tf.keras.optimizers, name):
                    return getattr(tf.keras.optimizers, name)
                if hasattr(tf.keras.losses, name):
                    return getattr(tf.keras.losses, name)
        except Exception:
            pass
        raise AttributeError(f"'{self.backend}' backend has no attribute '{name}'")



#___________________________________________QR code_____________________________________


class QR_Code:
    @staticmethod
    def generator(data, file_path="qrcode.png", box_size=10, border=4):
        """
        Generate a QR code image from the given data.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return f"QR code saved as {file_path}"

    @staticmethod
    def reader(file_path):
        """
        Read and decode a QR code from an image.
        """
        img = cv2.imread(file_path)
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(img)
        if data:
            return f"Decoded data: {data}"
        else:
            return "No QR code detected or unable to decode."
        
#_______________________________Advance Maths________________________________
import math
import statistics as stats
import random

class Advanced_Maths:
    def __init__(self):
        print("🧮 Advanced_Maths initialized — arithmetic, algebra, and statistics toolkit.")

# -----------------------------------------------------------
# 🔢 BASIC ARITHMETIC (MULTIPLE ARGUMENTS)
# -----------------------------------------------------------
    def add(self, *args):
        """Add all numbers together."""
        return sum(args)

    def subtract(self, *args):
        """Subtract all numbers in sequence."""
        if len(args) < 2:
            raise ValueError("Need at least two numbers to subtract.")
        result = args[0]
        for num in args[1:]:
            result -= num
        return result

    def multiply(self, *args):
        """Multiply all numbers together."""
        result = 1
        for num in args:
            result *= num
        return result

    def divide(self, *args):
        """Divide numbers in sequence (a / b / c / ...)."""
        if len(args) < 2:
            raise ValueError("Need at least two numbers to divide.")
        result = args[0]
        for num in args[1:]:
            if num == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            result /= num
        return result

    def power(self, base, exponent): return base ** exponent
    def sqrt(self, x): return math.sqrt(x)
    def mod(self, a, b): return a % b

# -----------------------------------------------------------
# 🔣 NUMBER THEORY
# -----------------------------------------------------------
    def factorial(self, n): return math.factorial(n)
    def combination(self, n, r): return math.comb(n, r)
    def permutation(self, n, r): return math.perm(n, r)
    def gcd(self, a, b): return math.gcd(a, b)
    def lcm(self, a, b): return math.lcm(a, b)
    def is_prime(self, n):
        if n < 2: return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

# -----------------------------------------------------------
# 📊 STATISTICS
# -----------------------------------------------------------
    def mean(self, data): return stats.mean(data)
    def median(self, data): return stats.median(data)
    def mode(self, data): return stats.mode(data)
    def variance(self, data): return stats.variance(data)
    def stdev(self, data): return stats.stdev(data)
    def data_range(self, data): return max(data) - min(data)

# -----------------------------------------------------------
# 🎲 PROBABILITY & RANDOM
# -----------------------------------------------------------
    def random_choice(self, data): return random.choice(data)
    def random_sample(self, data, k): return random.sample(data, k)
    def random_int(self, a, b): return random.randint(a, b)
    def random_float(self, a=0.0, b=1.0): return random.uniform(a, b)
    def probability(self, favorable, total):
        return favorable / total if total > 0 else 0

# -----------------------------------------------------------
# 🔢 SEQUENCES AND SERIES
# -----------------------------------------------------------
    def arithmetic_series(self, a1, d, n):
        """Sum of arithmetic progression."""
        return n / 2 * (2 * a1 + (n - 1) * d)

    def geometric_series(self, a1, r, n):
        """Sum of geometric progression."""
        if r == 1:
            return a1 * n
        return a1 * (1 - r ** n) / (1 - r)

# -----------------------------------------------------------
# 📏 CONVERSIONS & MISC
# -----------------------------------------------------------
    def deg_to_rad(self, deg): return math.radians(deg)
    def rad_to_deg(self, rad): return math.degrees(rad)
    def absolute(self, x): return abs(x)

#________________________________Physics (Beginer to Advanced)______________________


class Physics:
    def __init__(self):
        print("⚛️ Physics module initialized — classical, relativity, and quantum toolkit.")

# -----------------------------------------------------------
# ⚙️ CONSTANTS
# -----------------------------------------------------------
    G = 6.67430e-11   # Gravitational constant (N·m²/kg²)
    g = 9.81          # Acceleration due to gravity (m/s²)
    c = 3.0e8         # Speed of light (m/s)
    R = 8.314         # Gas constant (J/mol·K)
    k = 1.380649e-23  # Boltzmann constant (J/K)
    e = 1.602176634e-19  # Elementary charge (C)
    h = 6.62607015e-34   # Planck constant (J·s)
    h_bar = h / (2 * math.pi)  # Reduced Planck’s constant (ħ)

# -----------------------------------------------------------
# 🧭 MECHANICS
# -----------------------------------------------------------
    def velocity(self, distance, time):
        return distance / time

    def acceleration(self, v_final, v_initial, time):
        return (v_final - v_initial) / time

    def force(self, mass, acceleration):
        return mass * acceleration

    def weight(self, mass):
        return mass * self.g

    def momentum(self, mass, velocity):
        return mass * velocity

    def kinetic_energy(self, mass, velocity):
        return 0.5 * mass * velocity ** 2

    def potential_energy(self, mass, height):
        return mass * self.g * height

    def power(self, work, time):
        return work / time

    def work_done(self, force, distance, angle=0):
        return force * distance * math.cos(math.radians(angle))

# -----------------------------------------------------------
# 🌌 RELATIVITY
# -----------------------------------------------------------
    def mass_energy_equivalence(self, mass):
        """E = mc²"""
        return mass * (self.c ** 2)

    def relativistic_mass(self, rest_mass, velocity):
        """m = m₀ / sqrt(1 - v²/c²)"""
        if velocity >= self.c:
            raise ValueError("Velocity cannot reach or exceed speed of light.")
        return rest_mass / math.sqrt(1 - (velocity ** 2 / self.c ** 2))

    def time_dilation(self, time_interval, velocity):
        """t' = t / sqrt(1 - v²/c²)"""
        if velocity >= self.c:
            raise ValueError("Velocity cannot reach or exceed speed of light.")
        return time_interval / math.sqrt(1 - (velocity ** 2 / self.c ** 2))

    def length_contraction(self, proper_length, velocity):
        """L = L₀ * sqrt(1 - v²/c²)"""
        if velocity >= self.c:
            raise ValueError("Velocity cannot reach or exceed speed of light.")
        return proper_length * math.sqrt(1 - (velocity ** 2 / self.c ** 2))

    def relativistic_momentum(self, mass, velocity):
        """p = γ * m * v"""
        gamma = 1 / math.sqrt(1 - (velocity ** 2 / self.c ** 2))
        return gamma * mass * velocity

    def lorentz_factor(self, velocity):
        """γ = 1 / sqrt(1 - v²/c²)"""
        if velocity >= self.c:
            raise ValueError("Velocity cannot reach or exceed speed of light.")
        return 1 / math.sqrt(1 - (velocity ** 2 / self.c ** 2))

# -----------------------------------------------------------
# ⚛️ QUANTUM PHYSICS
# -----------------------------------------------------------
    def photon_energy(self, frequency):
        """E = h * f"""
        return self.h * frequency

    def photon_energy_wavelength(self, wavelength):
        """E = h * c / λ"""
        return (self.h * self.c) / wavelength

    def de_broglie_wavelength(self, mass, velocity):
        """λ = h / (m * v)"""
        return self.h / (mass * velocity)

    def heisenberg_uncertainty(self, delta_x=None, delta_p=None):
        """
        Δx * Δp ≥ ħ / 2
        Provide one to calculate the other.
        """
        if delta_x is None and delta_p is None:
            raise ValueError("Provide at least one value (Δx or Δp).")
        if delta_x is not None:
            return self.h_bar / (2 * delta_x)
        elif delta_p is not None:
            return self.h_bar / (2 * delta_p)

    def energy_level_hydrogen(self, n):
        """Eₙ = -13.6 eV / n²"""
        return -13.6 / (n ** 2)

    def particle_energy(self, mass, velocity):
        """E = (γ - 1)mc²"""
        if velocity >= self.c:
            raise ValueError("Velocity cannot reach or exceed speed of light.")
        gamma = 1 / math.sqrt(1 - (velocity ** 2 / self.c ** 2))
        return (gamma - 1) * mass * (self.c ** 2)

# -----------------------------------------------------------
# ⚡ ELECTRICITY & MAGNETISM
# -----------------------------------------------------------
    def ohms_law(self, voltage=None, current=None, resistance=None):
        if voltage is None:
            return current * resistance
        elif current is None:
            return voltage / resistance
        elif resistance is None:
            return voltage / current
        else:
            raise ValueError("Provide only two parameters to find the third.")

    def electric_power(self, voltage, current):
        return voltage * current

    def charge(self, current, time):
        return current * time

    def coulomb_force(self, q1, q2, r):
        return (8.99e9 * q1 * q2) / (r ** 2)

# -----------------------------------------------------------
# 🌊 WAVES & LIGHT
# -----------------------------------------------------------
    def wave_speed(self, frequency, wavelength):
        return frequency * wavelength

    def frequency(self, wave_speed, wavelength):
        return wave_speed / wavelength

    def period(self, frequency):
        return 1 / frequency

# -----------------------------------------------------------
# 🌍 GRAVITATION
# -----------------------------------------------------------
    def gravitational_force(self, m1, m2, r):
        return self.G * m1 * m2 / (r ** 2)

# -----------------------------------------------------------
# 🔄 CONVERSIONS
# -----------------------------------------------------------
    def joule_to_electronvolt(self, joules):
        return joules / self.e

    def electronvolt_to_joule(self, ev):
        return ev * self.e

    def joule_to_calorie(self, joules):
        return joules / 4.184

    def calorie_to_joule(self, calories):
        return calories * 4.184

#__________________________________Chemistry_____________________________________
class Chemistry:
    def __init__(self):
        print("⚗️ Chemistry module initialized — includes classical and quantum functions.")

    # -----------------------------------------------------------
    # 🌍 CONSTANTS
    # -----------------------------------------------------------
    R = 8.314           # Gas constant (J/mol·K)
    NA = 6.022e23       # Avogadro's number (1/mol)
    h = 6.626e-34       # Planck constant (J·s)
    c = 3.0e8           # Speed of light (m/s)
    e = 1.602e-19       # Charge of electron (C)
    me = 9.109e-31      # Mass of electron (kg)
    kB = 1.38e-23       # Boltzmann constant (J/K)
    _elements = [
    {
        "number": 1,
        "symbol": "H",
        "name": "Hydrogen",
        "mass": 1.008,
        "group": 1,
        "period": 1,
        "type": "Nonmetal"
    },
    {
        "number": 2,
        "symbol": "He",
        "name": "Helium",
        "mass": 4.0026,
        "group": 18,
        "period": 1,
        "type": "Noble gas"
    },
    {
        "number": 3,
        "symbol": "Li",
        "name": "Lithium",
        "mass": 6.94,
        "group": 1,
        "period": 2,
        "type": "Alkali metal"
    },
    {
        "number": 4,
        "symbol": "Be",
        "name": "Beryllium",
        "mass": 9.0122,
        "group": 2,
        "period": 2,
        "type": "Alkaline earth metal"
    },
    {
        "number": 5,
        "symbol": "B",
        "name": "Boron",
        "mass": 10.81,
        "group": 13,
        "period": 2,
        "type": "Metalloid"
    },
    {
        "number": 6,
        "symbol": "C",
        "name": "Carbon",
        "mass": 12.011,
        "group": 14,
        "period": 2,
        "type": "Nonmetal"
    },
    {
        "number": 7,
        "symbol": "N",
        "name": "Nitrogen",
        "mass": 14.007,
        "group": 15,
        "period": 2,
        "type": "Nonmetal"
    },
    {
        "number": 8,
        "symbol": "O",
        "name": "Oxygen",
        "mass": 15.999,
        "group": 16,
        "period": 2,
        "type": "Nonmetal"
    },
    {
        "number": 9,
        "symbol": "F",
        "name": "Fluorine",
        "mass": 18.998,
        "group": 17,
        "period": 2,
        "type": "Halogen"
    },
    {
        "number": 10,
        "symbol": "Ne",
        "name": "Neon",
        "mass": 20.180,
        "group": 18,
        "period": 2,
        "type": "Noble gas"
    },
    {
        "number": 11,
        "symbol": "Na",
        "name": "Sodium",
        "mass": 22.990,
        "group": 1,
        "period": 3,
        "type": "Alkali metal"
    },
    {
        "number": 12,
        "symbol": "Mg",
        "name": "Magnesium",
        "mass": 24.305,
        "group": 2,
        "period": 3,
        "type": "Alkaline earth metal"
    },
    {
        "number": 13,
        "symbol": "Al",
        "name": "Aluminum",
        "mass": 26.982,
        "group": 13,
        "period": 3,
        "type": "Post-transition metal"
    },
    {
        "number": 14,
        "symbol": "Si",
        "name": "Silicon",
        "mass": 28.085,
        "group": 14,
        "period": 3,
        "type": "Metalloid"
    },
    {
        "number": 15,
        "symbol": "P",
        "name": "Phosphorus",
        "mass": 30.974,
        "group": 15,
        "period": 3,
        "type": "Nonmetal"
    },
    {
        "number": 16,
        "symbol": "S",
        "name": "Sulfur",
        "mass": 32.06,
        "group": 16,
        "period": 3,
        "type": "Nonmetal"
    },
    {
        "number": 17,
        "symbol": "Cl",
        "name": "Chlorine",
        "mass": 35.45,
        "group": 17,
        "period": 3,
        "type": "Halogen"
    },
    {
        "number": 18,
        "symbol": "Ar",
        "name": "Argon",
        "mass": 39.948,
        "group": 18,
        "period": 3,
        "type": "Noble gas"
    },
    {
        "number": 19,
        "symbol": "K",
        "name": "Potassium",
        "mass": 39.098,
        "group": 1,
        "period": 4,
        "type": "Alkali metal"
    },
    {
        "number": 20,
        "symbol": "Ca",
        "name": "Calcium",
        "mass": 40.078,
        "group": 2,
        "period": 4,
        "type": "Alkaline earth metal"
    },
    {
        "number": 21,
        "symbol": "Sc",
        "name": "Scandium",
        "mass": 44.956,
        "group": 3,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 22,
        "symbol": "Ti",
        "name": "Titanium",
        "mass": 47.867,
        "group": 4,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 23,
        "symbol": "V",
        "name": "Vanadium",
        "mass": 50.942,
        "group": 5,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 24,
        "symbol": "Cr",
        "name": "Chromium",
        "mass": 51.996,
        "group": 6,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 25,
        "symbol": "Mn",
        "name": "Manganese",
        "mass": 54.938,
        "group": 7,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 26,
        "symbol": "Fe",
        "name": "Iron",
        "mass": 55.845,
        "group": 8,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 27,
        "symbol": "Co",
        "name": "Cobalt",
        "mass": 58.933,
        "group": 9,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 28,
        "symbol": "Ni",
        "name": "Nickel",
        "mass": 58.693,
        "group": 10,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 29,
        "symbol": "Cu",
        "name": "Copper",
        "mass": 63.546,
        "group": 11,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 30,
        "symbol": "Zn",
        "name": "Zinc",
        "mass": 65.38,
        "group": 12,
        "period": 4,
        "type": "Transition metal"
    },
    {
        "number": 31,
        "symbol": "Ga",
        "name": "Gallium",
        "mass": 69.723,
        "group": 13,
        "period": 4,
        "type": "Post-transition metal"
    },
    {
        "number": 32,
        "symbol": "Ge",
        "name": "Germanium",
        "mass": 72.630,
        "group": 14,
        "period": 4,
        "type": "Metalloid"
    },
    {
        "number": 33,
        "symbol": "As",
        "name": "Arsenic",
        "mass": 74.922,
        "group": 15,
        "period": 4,
        "type": "Metalloid"
    },
    {
        "number": 34,
        "symbol": "Se",
        "name": "Selenium",
        "mass": 78.971,
        "group": 16,
        "period": 4,
        "type": "Nonmetal"
    },
    {
        "number": 35,
        "symbol": "Br",
        "name": "Bromine",
        "mass": 79.904,
        "group": 17,
        "period": 4,
        "type": "Halogen"
    },
    {
        "number": 36,
        "symbol": "Kr",
        "name": "Krypton",
        "mass": 83.798,
        "group": 18,
        "period": 4,
        "type": "Noble gas"
    },
    {
        "number": 37,
        "symbol": "Rb",
        "name": "Rubidium",
        "mass": 85.468,
        "group": 1,
        "period": 5,
        "type": "Alkali metal"
    },
    {
        "number": 38,
        "symbol": "Sr",
        "name": "Strontium",
        "mass": 87.62,
        "group": 2,
        "period": 5,
        "type": "Alkaline earth metal"
    },
    {
        "number": 39,
        "symbol": "Y",
        "name": "Yttrium",
        "mass": 88.906,
        "group": 3,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 40,
        "symbol": "Zr",
        "name": "Zirconium",
        "mass": 91.224,
        "group": 4,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 41,
        "symbol": "Nb",
        "name": "Niobium",
        "mass": 92.906,
        "group": 5,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 42,
        "symbol": "Mo",
        "name": "Molybdenum",
        "mass": 95.95,
        "group": 6,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 43,
        "symbol": "Tc",
        "name": "Technetium",
        "mass": 98,
        "group": 7,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 44,
        "symbol": "Ru",
        "name": "Ruthenium",
        "mass": 101.07,
        "group": 8,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 45,
        "symbol": "Rh",
        "name": "Rhodium",
        "mass": 102.91,
        "group": 9,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 46,
        "symbol": "Pd",
        "name": "Palladium",
        "mass": 106.42,
        "group": 10,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 47,
        "symbol": "Ag",
        "name": "Silver",
        "mass": 107.87,
        "group": 11,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 48,
        "symbol": "Cd",
        "name": "Cadmium",
        "mass": 112.41,
        "group": 12,
        "period": 5,
        "type": "Transition metal"
    },
    {
        "number": 49,
        "symbol": "In",
        "name": "Indium",
        "mass": 114.82,
        "group": 13,
        "period": 5,
        "type": "Post-transition metal"
    },
    {
        "number": 50,
        "symbol": "Sn",
        "name": "Tin",
        "mass": 118.71,
        "group": 14,
        "period": 5,
        "type": "Post-transition metal"
    },
    {
        "number": 51,
        "symbol": "Sb",
        "name": "Antimony",
        "mass": 121.76,
        "group": 15,
        "period": 5,
        "type": "Metalloid"
    },
    {
        "number": 52,
        "symbol": "Te",
        "name": "Tellurium",
        "mass": 127.60,
        "group": 16,
        "period": 5,
        "type": "Metalloid"
    },
    {
        "number": 53,
        "symbol": "I",
        "name": "Iodine",
        "mass": 126.90,
        "group": 17,
        "period": 5,
        "type": "Halogen"
    },
    {
        "number": 54,
        "symbol": "Xe",
        "name": "Xenon",
        "mass": 131.29,
        "group": 18,
        "period": 5,
        "type": "Noble gas"
    },
    {
        "number": 55,
        "symbol": "Cs",
        "name": "Cesium",
        "mass": 132.91,
        "group": 1,
        "period": 6,
        "type": "Alkali metal"
    },
    {
        "number": 56,
        "symbol": "Ba",
        "name": "Barium",
        "mass": 137.33,
        "group": 2,
        "period": 6,
        "type": "Alkaline earth metal"
    },
    {
        "number": 57,
        "symbol": "La",
        "name": "Lanthanum",
        "mass": 138.91,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 58,
        "symbol": "Ce",
        "name": "Cerium",
        "mass": 140.12,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 59,
        "symbol": "Pr",
        "name": "Praseodymium",
        "mass": 140.91,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 60,
        "symbol": "Nd",
        "name": "Neodymium",
        "mass": 144.24,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 61,
        "symbol": "Pm",
        "name": "Promethium",
        "mass": 145,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 62,
        "symbol": "Sm",
        "name": "Samarium",
        "mass": 150.36,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 63,
        "symbol": "Eu",
        "name": "Europium",
        "mass": 151.96,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 64,
        "symbol": "Gd",
        "name": "Gadolinium",
        "mass": 157.25,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 65,
        "symbol": "Tb",
        "name": "Terbium",
        "mass": 158.93,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 66,
        "symbol": "Dy",
        "name": "Dysprosium",
        "mass": 162.50,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 67,
        "symbol": "Ho",
        "name": "Holmium",
        "mass": 164.93,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 68,
        "symbol": "Er",
        "name": "Erbium",
        "mass": 167.26,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 69,
        "symbol": "Tm",
        "name": "Thulium",
        "mass": 168.93,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 70,
        "symbol": "Yb",
        "name": "Ytterbium",
        "mass": 173.05,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 71,
        "symbol": "Lu",
        "name": "Lutetium",
        "mass": 174.97,
        "group": 3,
        "period": 6,
        "type": "Lanthanide"
    },
    {
        "number": 72,
        "symbol": "Hf",
        "name": "Hafnium",
        "mass": 178.49,
        "group": 4,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 73,
        "symbol": "Ta",
        "name": "Tantalum",
        "mass": 180.95,
        "group": 5,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 74,
        "symbol": "W",
        "name": "Tungsten",
        "mass": 183.84,
        "group": 6,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 75,
        "symbol": "Re",
        "name": "Rhenium",
        "mass": 186.21,
        "group": 7,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 76,
        "symbol": "Os",
        "name": "Osmium",
        "mass": 190.23,
        "group": 8,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 77,
        "symbol": "Ir",
        "name": "Iridium",
        "mass": 192.22,
        "group": 9,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 78,
        "symbol": "Pt",
        "name": "Platinum",
        "mass": 195.08,
        "group": 10,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 79,
        "symbol": "Au",
        "name": "Gold",
        "mass": 196.97,
        "group": 11,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 80,
        "symbol": "Hg",
        "name": "Mercury",
        "mass": 200.59,
        "group": 12,
        "period": 6,
        "type": "Transition metal"
    },
    {
        "number": 81,
        "symbol": "Tl",
        "name": "Thallium",
        "mass": 204.38,
        "group": 13,
        "period": 6,
        "type": "Post-transition metal"
    },
    {
        "number": 82,
        "symbol": "Pb",
        "name": "Lead",
        "mass": 207.2,
        "group": 14,
        "period": 6,
        "type": "Post-transition metal"
    },
    {
        "number": 83,
        "symbol": "Bi",
        "name": "Bismuth",
        "mass": 208.98,
        "group": 15,
        "period": 6,
        "type": "Post-transition metal"
    },
    {
        "number": 84,
        "symbol": "Po",
        "name": "Polonium",
        "mass": 209,
        "group": 16,
        "period": 6,
        "type": "Metalloid"
    },
    {
        "number": 85,
        "symbol": "At",
        "name": "Astatine",
        "mass": 210,
        "group": 17,
        "period": 6,
        "type": "Halogen"
    },
    {
        "number": 86,
        "symbol": "Rn",
        "name": "Radon",
        "mass": 222,
        "group": 18,
        "period": 6,
        "type": "Noble gas"
    },
    {
        "number": 87,
        "symbol": "Fr",
        "name": "Francium",
        "mass": 223,
        "group": 1,
        "period": 7,
        "type": "Alkali metal"
    },
    {
        "number": 88,
        "symbol": "Ra",
        "name": "Radium",
        "mass": 226,
        "group": 2,
        "period": 7,
        "type": "Alkaline earth metal"
    },
    {
        "number": 89,
        "symbol": "Ac",
        "name": "Actinium",
        "mass": 227,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 90,
        "symbol": "Th",
        "name": "Thorium",
        "mass": 232.04,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 91,
        "symbol": "Pa",
        "name": "Protactinium",
        "mass": 231.04,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 92,
        "symbol": "U",
        "name": "Uranium",
        "mass": 238.03,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 93,
        "symbol": "Np",
        "name": "Neptunium",
        "mass": 237,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 94,
        "symbol": "Pu",
        "name": "Plutonium",
        "mass": 244,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 95,
        "symbol": "Am",
        "name": "Americium",
        "mass": 243,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 96,
        "symbol": "Cm",
        "name": "Curium",
        "mass": 247,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 97,
        "symbol": "Bk",
        "name": "Berkelium",
        "mass": 247,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 98,
        "symbol": "Cf",
        "name": "Californium",
        "mass": 251,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 99,
        "symbol": "Es",
        "name": "Einsteinium",
        "mass": 252,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 100,
        "symbol": "Fm",
        "name": "Fermium",
        "mass": 257,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 101,
        "symbol": "Md",
        "name": "Mendelevium",
        "mass": 258,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 102,
        "symbol": "No",
        "name": "Nobelium",
        "mass": 259,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 103,
        "symbol": "Lr",
        "name": "Lawrencium",
        "mass": 266,
        "group": 3,
        "period": 7,
        "type": "Actinide"
    },
    {
        "number": 104,
        "symbol": "Rf",
        "name": "Rutherfordium",
        "mass": 267,
        "group": 4,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 105,
        "symbol": "Db",
        "name": "Dubnium",
        "mass": 268,
        "group": 5,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 106,
        "symbol": "Sg",
        "name": "Seaborgium",
        "mass": 269,
        "group": 6,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 107,
        "symbol": "Bh",
        "name": "Bohrium",
        "mass": 270,
        "group": 7,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 108,
        "symbol": "Hs",
        "name": "Hassium",
        "mass": 277,
        "group": 8,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 109,
        "symbol": "Mt",
        "name": "Meitnerium",
        "mass": 278,
        "group": 9,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 110,
        "symbol": "Ds",
        "name": "Darmstadtium",
        "mass": 281,
        "group": 10,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 111,
        "symbol": "Rg",
        "name": "Roentgenium",
        "mass": 282,
        "group": 11,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 112,
        "symbol": "Cn",
        "name": "Copernicium",
        "mass": 285,
        "group": 12,
        "period": 7,
        "type": "Transition metal"
    },
    {
        "number": 113,
        "symbol": "Nh",
        "name": "Nihonium",
        "mass": 286,
        "group": 13,
        "period": 7,
        "type": "Post-transition metal"
    },
    {
        "number": 114,
        "symbol": "Fl",
        "name": "Flerovium",
        "mass": 289,
        "group": 14,
        "period": 7,
        "type": "Post-transition metal"
    },
    {
        "number": 115,
        "symbol": "Mc",
        "name": "Moscovium",
        "mass": 290,
        "group": 15,
        "period": 7,
        "type": "Post-transition metal"
    },
    {
        "number": 116,
        "symbol": "Lv",
        "name": "Livermorium",
        "mass": 293,
        "group": 16,
        "period": 7,
        "type": "Post-transition metal"
    },
    {
        "number": 117,
        "symbol": "Ts",
        "name": "Tennessine",
        "mass": 294,
        "group": 17,
        "period": 7,
        "type": "Halogen"
    },
    {
        "number": 118,
        "symbol": "Og",
        "name": "Oganesson",
        "mass": 294,
        "group": 18,
        "period": 7,
        "type": "Noble gas"
    }
]      # Blank element list (can be filled later)

    # -----------------------------------------------------------
    # 🧪 BASIC CHEMISTRY
    # -----------------------------------------------------------
    def molar_mass(self, mass, moles):
        """M = m / n"""
        return mass / moles if moles != 0 else float('inf')

    def moles_from_mass(self, mass, molar_mass):
        """n = m / M"""
        return mass / molar_mass if molar_mass != 0 else float('inf')

    def mass_from_moles(self, moles, molar_mass):
        """m = n * M"""
        return moles * molar_mass

    def concentration(self, moles, volume):
        """C = n / V (mol/L)"""
        return moles / volume if volume != 0 else float('inf')

    def percent_yield(self, actual, theoretical):
        """% yield = (actual / theoretical) * 100"""
        return (actual / theoretical) * 100 if theoretical != 0 else 0

    # -----------------------------------------------------------
    # 🌡️ GAS LAWS & THERMODYNAMICS
    # -----------------------------------------------------------
    def ideal_gas_pressure(self, n, V, T):
        """P = (nRT) / V"""
        return (n * self.R * T) / V if V != 0 else float('inf')

    def ideal_gas_volume(self, n, P, T):
        """V = (nRT) / P"""
        return (n * self.R * T) / P if P != 0 else float('inf')

    def ideal_gas_temperature(self, P, V, n):
        """T = (PV) / (nR)"""
        return (P * V) / (n * self.R) if n != 0 else float('inf')

    def heat_energy(self, mass, specific_heat, delta_T):
        """Q = m * c * ΔT"""
        return mass * specific_heat * delta_T

    def gibbs_free_energy(self, delta_H, delta_S, T):
        """ΔG = ΔH - TΔS"""
        return delta_H - T * delta_S

    def equilibrium_constant(self, delta_G, T):
        """K = e^(-ΔG / RT)"""
        return math.exp(-delta_G / (self.R * T))

    # -----------------------------------------------------------
    # ⚛️ ATOMIC & QUANTUM CHEMISTRY
    # -----------------------------------------------------------
    def energy_level_hydrogen(self, n):
        """Eₙ = -13.6 eV / n²"""
        return -13.6 / (n ** 2)

    def photon_energy(self, wavelength):
        """E = h * c / λ"""
        return (self.h * self.c) / wavelength

    def wavelength_from_energy(self, energy):
        """λ = h * c / E"""
        return (self.h * self.c) / energy

    def de_broglie_wavelength(self, mass, velocity):
        """λ = h / (m * v)"""
        return self.h / (mass * velocity)

    def uncertainty(self, delta_x):
        """Δp ≥ h / (4πΔx)"""
        return self.h / (4 * math.pi * delta_x)

    def particle_energy(self, frequency):
        """E = h * f"""
        return self.h * frequency

    def bohr_radius(self, n=1):
        """rₙ = (ε₀ * h² * n²) / (π * me * e²)"""
        ε0 = 8.854e-12
        return (ε0 * self.h**2 * n**2) / (math.pi * self.me * self.e**2)

    def ionization_energy(self, n1, n2):
        """ΔE (eV) = 13.6 * (1/n1² - 1/n2²)"""
        return 13.6 * ((1 / (n1 ** 2)) - (1 / (n2 ** 2)))

    # -----------------------------------------------------------
    # 🧮 STOICHIOMETRY
    # -----------------------------------------------------------
    def limiting_reactant(self, moles_A, ratio_A, moles_B, ratio_B):
        """Return limiting reactant based on stoichiometric ratios"""
        if (moles_A / ratio_A) < (moles_B / ratio_B):
            return "Reactant A is limiting"
        elif (moles_B / ratio_B) < (moles_A / ratio_A):
            return "Reactant B is limiting"
        else:
            return "Reactants are in perfect ratio"

    def percent_purity(self, pure_mass, impure_mass):
        """% Purity = (pure_mass / impure_mass) * 100"""
        return (pure_mass / impure_mass) * 100 if impure_mass != 0 else 0

    # -----------------------------------------------------------
    # 🔥 SPECTROSCOPY & ENERGY TRANSITIONS
    # -----------------------------------------------------------
    def frequency_from_wavelength(self, wavelength):
        """f = c / λ"""
        return self.c / wavelength

    def wavelength_from_frequency(self, frequency):
        """λ = c / f"""
        return self.c / frequency

    def photon_wavenumber(self, wavelength):
        """ν̃ = 1 / λ (in m⁻¹)"""
        return 1 / wavelength

    # -----------------------------------------------------------
    # 🔄 CONVERSIONS
    # -----------------------------------------------------------
    def joule_to_ev(self, joules):
        """Convert Joules to electronvolts"""
        return joules / self.e

    def ev_to_joule(self, ev):
        """Convert electronvolts to Joules"""
        return ev * self.e

    # -----------------------------------------------------------
    # 🧫 ELEMENT INFORMATION
    # -----------------------------------------------------------
    def atom_info(self, query):
        """
        Get atomic details by number, symbol, or name.
        Example:
            atom_info(8)
            atom_info('O')
            atom_info('Oxygen')
        """
        query_str = str(query).capitalize().strip()
        for element in self._elements:
            if (
                str(element["number"]) == str(query)
                or element["symbol"].lower() == str(query).lower()
                or element["name"].lower() == str(query).lower()
            ):
                return {
                    "Atomic Number": element["number"],
                    "Symbol": element["symbol"],
                    "Name": element["name"],
                    "Atomic Mass (u)": element["mass"],
                    "Group": element["group"],
                    "Period": element["period"],
                    "Type": element["type"]
                }
        return f"No element found for '{query}'"


#___________________________FTP_______________________________________
class FTP:
    def __init__(self, host="", user="", password="", port=21, timeout=30):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.timeout = timeout
        self.ftp = None

    # -----------------------------------------------------------
    # 🔌 CONNECTION HANDLING
    # -----------------------------------------------------------
    def connect(self):
        """Connect to the FTP server."""
        try:
            self.ftp = FTPClient()
            self.ftp.connect(self.host, self.port, timeout=self.timeout)
            self.ftp.login(self.user, self.password)
            print(f"✅ Connected to {self.host}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

    def disconnect(self):
        """Close FTP connection."""
        if self.ftp:
            self.ftp.quit()
            print("🔌 Disconnected from FTP server.")

    # -----------------------------------------------------------
    # 📁 DIRECTORY MANAGEMENT
    # -----------------------------------------------------------
    def current_dir(self):
        """Return current working directory."""
        if self.ftp:
            return self.ftp.pwd()

    def change_dir(self, path):
        """Change working directory."""
        if self.ftp:
            self.ftp.cwd(path)
            print(f"📂 Changed directory to: {path}")

    def make_dir(self, dirname):
        """Create a new directory."""
        if self.ftp:
            self.ftp.mkd(dirname)
            print(f"📁 Directory created: {dirname}")

    def remove_dir(self, dirname):
        """Remove a directory."""
        if self.ftp:
            self.ftp.rmd(dirname)
            print(f"🗑️ Directory removed: {dirname}")

    # -----------------------------------------------------------
    # 📜 FILE LISTING & INFO
    # -----------------------------------------------------------
    def list_files(self):
        """List files in current directory."""
        if self.ftp:
            files = self.ftp.nlst()
            for f in files:
                print(f"📄 {f}")
            return files

    def file_info(self, filename):
        """Get file size and modification time."""
        if self.ftp:
            size = self.ftp.size(filename)
            print(f"📏 Size of {filename}: {size} bytes")
            return size

    # -----------------------------------------------------------
    # ⬆️ UPLOAD & ⬇️ DOWNLOAD
    # -----------------------------------------------------------
    def upload_file(self, local_path, remote_path=None):
        """Upload a local file to the FTP server."""
        if not remote_path:
            remote_path = os.path.basename(local_path)
        if self.ftp and os.path.exists(local_path):
            with open(local_path, "rb") as f:
                self.ftp.storbinary(f"STOR {remote_path}", f)
            print(f"⬆️ Uploaded: {local_path} → {remote_path}")
        else:
            print("⚠️ Local file not found or not connected.")

    def download_file(self, remote_path, local_path=None):
        """Download a file from the FTP server."""
        if not local_path:
            local_path = os.path.basename(remote_path)
        if self.ftp:
            with open(local_path, "wb") as f:
                self.ftp.retrbinary(f"RETR {remote_path}", f.write)
            print(f"⬇️ Downloaded: {remote_path} → {local_path}")

    # -----------------------------------------------------------
    # ⚙️ FILE OPERATIONS
    # -----------------------------------------------------------
    def rename_file(self, old_name, new_name):
        """Rename file on the FTP server."""
        if self.ftp:
            self.ftp.rename(old_name, new_name)
            print(f"✏️ Renamed: {old_name} → {new_name}")

    def delete_file(self, filename):
        """Delete a file from the FTP server."""
        if self.ftp:
            self.ftp.delete(filename)
            print(f"🗑️ Deleted: {filename}")

    # -----------------------------------------------------------
    # 🧩 UTILITY
    # -----------------------------------------------------------
    def is_connected(self):
        """Check if the FTP connection is active."""
        try:
            self.ftp.voidcmd("NOOP")
            return True
        except:
            return False
#_____________________________Encoder______________________________
class Encoding:
    def __init__(self):
        print("🔐 Encoding module initialized — supports Base64, Hex, Binary, URL, and Unicode operations.")

    # ---------------------------------------------------------
    # 🧩 BASE64 ENCODING / DECODING
    # ---------------------------------------------------------
    def base64_encode(self, text: str) -> str:
        """Encodes text into Base64."""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    def base64_decode(self, encoded_text: str) -> str:
        """Decodes Base64 text into normal string."""
        return base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')

    # ---------------------------------------------------------
    # 🧱 HEX ENCODING / DECODING
    # ---------------------------------------------------------
    def hex_encode(self, text: str) -> str:
        """Encodes text into hexadecimal representation."""
        return text.encode('utf-8').hex()

    def hex_decode(self, hex_text: str) -> str:
        """Decodes hexadecimal text into normal string."""
        return bytes.fromhex(hex_text).decode('utf-8')

    # ---------------------------------------------------------
    # 💾 BINARY ENCODING / DECODING
    # ---------------------------------------------------------
    def binary_encode(self, text: str) -> str:
        """Encodes text into binary representation."""
        return ' '.join(format(ord(char), '08b') for char in text)

    def binary_decode(self, binary_text: str) -> str:
        """Decodes binary string into normal text."""
        return ''.join(chr(int(b, 2)) for b in binary_text.split())

    # ---------------------------------------------------------
    # 🌐 URL ENCODING / DECODING
    # ---------------------------------------------------------
    def url_encode(self, text: str) -> str:
        """Encodes URL or text safely for web transmission."""
        return urllib.parse.quote(text)

    def url_decode(self, encoded_text: str) -> str:
        """Decodes URL-encoded text back to original."""
        return urllib.parse.unquote(encoded_text)

    # ---------------------------------------------------------
    # 🔡 UTF ENCODING / DECODING
    # ---------------------------------------------------------
    def utf_encode(self, text: str, encoding='utf-8') -> bytes:
        """Encodes text using given UTF format (utf-8, utf-16, utf-32)."""
        return text.encode(encoding)

    def utf_decode(self, data: bytes, encoding='utf-8') -> str:
        """Decodes bytes using given UTF format."""
        return data.decode(encoding)

    # ---------------------------------------------------------
    # 📁 FILE ENCODING / DECODING
    # ---------------------------------------------------------
    def file_to_base64(self, file_path: str) -> str:
        """Encodes a file into Base64 string."""
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def base64_to_file(self, encoded_data: str, output_path: str):
        """Decodes Base64 string and writes binary file."""
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(encoded_data))

    # ---------------------------------------------------------
    # 🧮 ASCII CONVERSION
    # ---------------------------------------------------------
    def text_to_ascii(self, text: str) -> list:
        """Converts text to list of ASCII codes."""
        return [ord(c) for c in text]

    def ascii_to_text(self, ascii_list: list) -> str:
        """Converts list of ASCII codes to text."""
        return ''.join(chr(i) for i in ascii_list)

    # ---------------------------------------------------------
    # 🔄 UNICODE CONVERSION
    # ---------------------------------------------------------
    def text_to_unicode(self, text: str) -> list:
        """Converts text to list of Unicode code points."""
        return [f"U+{ord(c):04X}" for c in text]

    def unicode_to_text(self, unicode_list: list) -> str:
        """Converts list of Unicode code points to text."""
        return ''.join(chr(int(u.replace('U+', ''), 16)) for u in unicode_list)

    # ---------------------------------------------------------
    # 🔏 ROT13 ENCODING
    # ---------------------------------------------------------
    def rot13_encode(self, text: str) -> str:
        """Encodes/decodes text using ROT13 cipher."""
        return codecs.encode(text, 'rot_13')

    # ---------------------------------------------------------
    # 🧬 MORSE CODE ENCODING / DECODING
    # ---------------------------------------------------------
    def morse_encode(self, text: str) -> str:
        """Encodes text into Morse code."""
        morse = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
            'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
            'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
            'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....',
            '7': '--...', '8': '---..', '9': '----.', '0': '-----',
            ' ': '/'
        }
        return ' '.join(morse.get(c.upper(), '?') for c in text)

    def morse_decode(self, code: str) -> str:
        """Decodes Morse code into text."""
        morse = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D',
            '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
            '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P',
            '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6',
            '--...': '7', '---..': '8', '----.': '9', '-----': '0',
            '/': ' '
        }
        return ''.join(morse.get(c, '?') for c in code.split())

#_________________________________Number_System_Coverter_______________________
class Number_System:
    def __init__(self):
        print("🔢 Number System module initialized — supports Binary, Octal, Decimal, and Hexadecimal conversions.")

    # ---------------------------------------------------------
    # 🧮 BASIC CONVERSIONS
    # ---------------------------------------------------------
    def dec_to_bin(self, num: int) -> str:
        """Converts Decimal → Binary."""
        return bin(num)[2:]

    def dec_to_oct(self, num: int) -> str:
        """Converts Decimal → Octal."""
        return oct(num)[2:]

    def dec_to_hex(self, num: int) -> str:
        """Converts Decimal → Hexadecimal."""
        return hex(num)[2:].upper()

    def bin_to_dec(self, num: str) -> int:
        """Converts Binary → Decimal."""
        return int(num, 2)

    def oct_to_dec(self, num: str) -> int:
        """Converts Octal → Decimal."""
        return int(num, 8)

    def hex_to_dec(self, num: str) -> int:
        """Converts Hexadecimal → Decimal."""
        return int(num, 16)

    # ---------------------------------------------------------
    # 🔄 CROSS CONVERSIONS (BINARY, OCTAL, HEXADECIMAL)
    # ---------------------------------------------------------
    def bin_to_oct(self, num: str) -> str:
        """Converts Binary → Octal."""
        return oct(int(num, 2))[2:]

    def bin_to_hex(self, num: str) -> str:
        """Converts Binary → Hexadecimal."""
        return hex(int(num, 2))[2:].upper()

    def oct_to_bin(self, num: str) -> str:
        """Converts Octal → Binary."""
        return bin(int(num, 8))[2:]

    def oct_to_hex(self, num: str) -> str:
        """Converts Octal → Hexadecimal."""
        return hex(int(num, 8))[2:].upper()

    def hex_to_bin(self, num: str) -> str:
        """Converts Hexadecimal → Binary."""
        return bin(int(num, 16))[2:]

    def hex_to_oct(self, num: str) -> str:
        """Converts Hexadecimal → Octal."""
        return oct(int(num, 16))[2:]

    # ---------------------------------------------------------
    # 🧰 UNIVERSAL CONVERTER
    # ---------------------------------------------------------
    def convert(self, value: str, from_base: int, to_base: int) -> str:
        """
        Universal number converter.
        Supports bases between 2 and 36.
        Example: convert("1010", 2, 16) → 'A'
        """
        decimal_value = int(value, from_base)
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if to_base == 10:
            return str(decimal_value)
        result = ""
        while decimal_value > 0:
            result = digits[decimal_value % to_base] + result
            decimal_value //= to_base
        return result or "0"

    # ---------------------------------------------------------
    # 🧪 VALIDATION
    # ---------------------------------------------------------
    def validate(self, value: str, base: int) -> bool:
        """Validates if a number string belongs to a base system."""
        valid_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:base]
        value = value.upper()
        return all(ch in valid_chars for ch in value)

    # ---------------------------------------------------------
    # 📦 BATCH CONVERSION
    # ---------------------------------------------------------
    def convert_list(self, values: list, from_base: int, to_base: int) -> list:
        """Converts a list of numbers between any two bases."""
        return [self.convert(v, from_base, to_base) for v in values]

    # ---------------------------------------------------------
    # 🧾 FORMAT DISPLAY
    # ---------------------------------------------------------
    def format_all(self, num: int) -> dict:
        """Returns a dictionary of all equivalent representations."""
        return {
            "Decimal": num,
            "Binary": self.dec_to_bin(num),
            "Octal": self.dec_to_oct(num),
            "Hexadecimal": self.dec_to_hex(num)
        }

    # ---------------------------------------------------------
    # 🧠 AUTO DETECT BASE
    # ---------------------------------------------------------
    def detect_base(self, value: str) -> str:
        """
        Detects number system based on prefix or pattern.
        """
        value = value.strip().lower()
        if value.startswith("0b"):
            return "Binary"
        elif value.startswith("0o"):
            return "Octal"
        elif value.startswith("0x"):
            return "Hexadecimal"
        elif all(c in "01" for c in value):
            return "Binary (No Prefix)"
        else:
            return "Decimal or Custom Base"

