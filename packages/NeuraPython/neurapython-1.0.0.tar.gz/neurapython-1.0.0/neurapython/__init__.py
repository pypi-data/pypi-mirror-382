import os
import threading
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



#______________________________Website__________________________

class WebServer:
    def __init__(self):
        self.app = Flask(__name__)

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

    def error_handler(self, error_code, code="NeuraPy Error page", error_page_html=""):
        @self.app.errorhandler(error_code)
        def error(e):  
            if error_page_html.strip() and os.path.exists(error_page_html):
                with open(error_page_html, "r", encoding="utf-8") as f:
                    return f.read(), error_code
            else:
                return code or f"Error {error_code}", error_code

    def run(self, live_refresh: bool = True):
        self.app.run(debug=live_refresh, host='0.0.0.0', port=5200)
        
#_________________________More website functionality______________________________
    def verify_details(self,route='/',user_data=[],verify_data_from=[]):
        if (len(user_data)==len(verify_data_from)):
            data=request.get_json()
            collected_info=[]
            for i in range(0,len(data)):
                collected_info.append(data[user_data[i]])
            validation=[]
            for j in range(0,len(collected_info)):
                if (collected_info[j] == verify_data_from[j]):
                    validation.append(True)
                else:
                    validation.append(False)
            if False in validation:
                return jsonify({"response":False})
            else:
                return jsonify({"response":True})
        else:
            return jsonify({"response":False})     
    def DataBase(self,db=r"E:\neurapy.db",query=f"""
                CREATE TABLE IF NOT EXISTS NeuraPy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT UNIQUE
            )
                """):
        conn=sqlite3.connect(db)
        cursor=conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()

    def retrieve_data_from_db(self,path_to_db,query):
        conn=sqlite3.connect(path_to_db)
        cursor=conn.cursor()
        cursor.execute(query)
        data=cursor.fetchall()
        conn.commit()
        conn.close()
        return jsonify(data)
    
    
    
    
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
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                pdf.multi_cell(0, 10, line.strip())
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
