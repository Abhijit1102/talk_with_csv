from flask import Flask, render_template, request, redirect, url_for
import os

from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize global variables
OPENAI_API_KEY = None
file_path = None

@app.route("/get", methods=["GET", "POST"])
def chat():
    try:
        question = request.form["msg"]
        print("question : ", question)
        llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.5)
        agent_executer = create_csv_agent(llm, file_path, verbose=True)
        result = agent_executer.invoke(str(question))     
        print(result)                       
        return str(result["output"])
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    global OPENAI_API_KEY, file_path
    try:
        if request.method == 'POST':
            OPENAI_API_KEY = request.form['apiKey']
            file_upload = request.files['fileUpload']
            if file_upload and allowed_file(file_upload.filename):
                file_upload.save(os.path.join(app.config['UPLOAD_FOLDER'], file_upload.filename))
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_upload.filename)
                return render_template("chat.html", OPENAI_API_KEY=OPENAI_API_KEY, file_path=file_path)
            else:
                return "File not allowed"  # or redirect to an error page
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
