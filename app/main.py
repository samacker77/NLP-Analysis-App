from flask import Flask, flash, request, redirect, url_for,render_template,send_file
from werkzeug.utils import secure_filename
import os
import shutil
import textract
import datetime

UPLOAD_FOLDER = 'app/uploads/'
DOWLOAD_FOLDER= 'app/downloads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc','docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWLOAD_FOLDER
app.secret_key = "jhkafshjkfhfsd"
CORPUS_FOLDER = 'app/corpuses'
import time
@app.route('/',methods=['POST','GET'])
def home():
    try:
        uploaded_files = os.listdir(UPLOAD_FOLDER)
    except:
        uploaded_files = ['No uploaded files']
    if len(uploaded_files)==0:
        uploaded_files=['No uploaded files']
    if request.method == 'POST' and request.form.get('upload'):
        file = request.files['file']
        if request.form['filename']!="":
            filename=request.form['filename']
        else:
            filename=file.filename
        if file and allowed_file(filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File Uploaded")
            uploaded_files = os.listdir(UPLOAD_FOLDER)
        else:
            flash("File cannot be uploaded")
    if request.method == 'POST' and request.form.get('download'):
        if request.form['downloadfilename'] !="":
            filename=request.form['downloadfilename']
            if filename in uploaded_files:
                path = 'uploads/'+ filename
                return send_file(path, as_attachment=True)
            else:
                flash("No such file exists")
        else:
            flash("Please mention filename")

    return render_template('index.html',uploaded_files=uploaded_files)

@app.route('/<page>',methods=['POST','GET'])
def gotoNextPage(page):
    print(page)
    if page == 'functionality2':

        uploaded_files = os.listdir(UPLOAD_FOLDER)
        corpus_generation_status = ""
        if request.method == 'POST' and request.form.get('generateCorpus'):
            print(">>" * 50)
            file = request.form['getFileNames']
            all_files = file.split()
            relevant_files = list(set(uploaded_files).intersection(set(all_files)))
            corpus_text = []
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads',f)))
                text = "\n"+f+"#########\n"+text[1:]
                if text:
                    corpus_text.append(text)

            file_name = "corpus_"+datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")+".txt"
            with open(os.path.join(CORPUS_FOLDER,file_name),'w') as file:
                for text in corpus_text:
                    file.write(text)
                    corpus_generation_status="Corpus generated successfully"

        if request.method == 'POST' and request.form.get('downloadCorpus'):
            all_corpuses = os.listdir(CORPUS_FOLDER)
            all_corpuses = [corpus for corpus in all_corpuses if corpus.endswith(".txt")]
            if len(all_corpuses) > 0:
                sorted_corpuses = sorted(all_corpuses)
                latest = sorted_corpuses[-1]
                path = os.path.join('corpuses',latest)
                return send_file(path, as_attachment=True)
            else:
                flash("No corpuses found")






        return render_template('functionality2.html',uploaded_files=uploaded_files,corpus_generation_status=corpus_generation_status)
    return render_template(str(page)+'.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




if __name__ == '__main__':
    app.run(debug=True)

