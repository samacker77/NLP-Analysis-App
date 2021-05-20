from flask import Flask, flash, request, redirect, url_for,render_template
from werkzeug.utils import secure_filename
import os
UPLOAD_FOLDER = 'app/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc','docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "jhkafshjkfhfsd"


@app.route('/',methods=['POST','GET'])
def home():

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File Uploaded")
    return render_template('index.html')
@app.route('/<page>')
def gotoNextPage(page):
    return render_template(str(page)+'.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




if __name__ == '__main__':
    app.run(debug=True)

