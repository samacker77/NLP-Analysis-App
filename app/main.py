from flask import Flask, flash, request, redirect, url_for,render_template,send_file
from werkzeug.utils import secure_filename
import os
import shutil

UPLOAD_FOLDER = 'app/uploads/'
DOWLOAD_FOLDER= 'app/downloads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc','docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWLOAD_FOLDER
app.secret_key = "jhkafshjkfhfsd"


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

@app.route('/<page>')
def gotoNextPage(page):
    print(page)
    return render_template(str(page)+'.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




if __name__ == '__main__':
    app.run(debug=True)

