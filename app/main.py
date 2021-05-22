from flask import Flask, flash, request, redirect, url_for,render_template,send_file


from werkzeug.utils import secure_filename
import os
import shutil
import textract
import datetime
import nltk
from collections import Counter
import jinja2
env = jinja2.Environment()


UPLOAD_FOLDER = 'app/uploads/'
DOWLOAD_FOLDER= 'app/downloads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc','docx'}

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWLOAD_FOLDER
CORPUS_FOLDER = 'app/corpuses'


def get_chains():
    with open('app/chains.txt','r') as file:
        return file.readlines()

def get_uploaded_files():
    global UPLOAD_FOLDER
    uploaded_files = os.listdir(UPLOAD_FOLDER)
    if not uploaded_files:
        uploaded_files = ['No uploaded files']
    return uploaded_files

def get_corpuses():
    global CORPUS_FOLDER
    uploaded_files = os.listdir(CORPUS_FOLDER)
    all_corpuses = [corpus for corpus in uploaded_files if corpus.endswith(".txt")]
    if not all_corpuses:
        all_corpuses = ['No corpus found']
    return all_corpuses




def find_relevant_files(filenames):
    all_files = filenames.split()
    uploaded_files = get_uploaded_files()
    relevant_files = list(set(uploaded_files).intersection(set(all_files)))
    return relevant_files

def find_relevant_corpuses(filenames):
    all_files = filenames.split()
    global CORPUS_FOLDER
    all_corpuses = os.listdir(CORPUS_FOLDER)
    all_corpuses = [corpus for corpus in all_corpuses if corpus.endswith(".txt")]
    relevant_corpuses = list(set(all_corpuses).intersection(set(all_files)))
    return relevant_corpuses

import time
@app.route('/',methods=['POST','GET'])
def home():
    uploaded_files = get_uploaded_files()
    corpuses = get_corpuses()
    if len(uploaded_files)==0:
        uploaded_files=['No uploaded files']
    if len(corpuses)==0:
        uploaded_files=['No corpuses found']
    if request.method == 'POST' and request.form.get('upload'):
        file = request.files['file']
        if request.form['filename']!="":
            filename=request.form['filename']
        else:
            filename=file.filename
        if file and allowed_file(filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("File Uploaded")
            uploaded_files = get_uploaded_files()
        else:
            flash("File cannot be uploaded")
    if request.method == 'POST' and request.form.get('download'):
        if request.form['downloadfilename'] !="":
            filename=request.form['downloadfilename']
            if filename in uploaded_files:
                path = 'uploads/'+ filename
                return send_file(path, as_attachment=True)
            else:
                if filename in corpuses:
                    path = 'corpuses/' + filename
                    return send_file(path, as_attachment=True)
        else:
            flash("Please mention filename")

    return render_template('index.html',chain_for_UI=get_chains(),uploaded_files=get_uploaded_files(),generated_corpuses=get_corpuses())

@app.route('/<page>',methods=['POST','GET'])
def gotoNextPage(page):
    print(page)
    uploaded_files = get_uploaded_files()
    if page == 'functionality2':
        corpus_generation_status = ""
        if request.method == 'POST' and request.form.get('generateCorpus'):
            file = request.form['getFileNames']
            relevant_files=find_relevant_files(file)
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
        uploaded_files = get_uploaded_files()
        return render_template('functionality2.html',uploaded_files=uploaded_files,
                               corpus_generation_status=corpus_generation_status)
    elif page == 'functionality3':
        replace_status = ""
        deletion_status = ""
        appened_status = ""
        generated_corpuses = get_corpuses()

        if request.method == 'POST' and request.form.get('replace'):
            file = request.form['getFileNames']
            if not file:
                replace_status = "Please input filename to manipulate"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            relevant_files = find_relevant_files(file)
            relevant_corpuses = find_relevant_corpuses(file)
            if not relevant_files and not relevant_corpuses:
                flash("Error! No such file exist")
            replace=request.form['text']
            replaced_by=request.form['replace_text']
            if not replace or not replaced_by:
                replace_status = "No such file exists"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads', f)))
                final_text=text.replace(replace,replaced_by)
                with open(os.path.join("app/uploads",f.split(".")[0]+'.txt'),'w') as fin:
                    fin.write(final_text)
                    fin.close()
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join('app/corpuses', f)))
                final_text=text.replace(replace,replaced_by)
                with open(os.path.join("app/corpuses",f.split(".")[0]+'.txt'),'w') as fin:
                    fin.write(final_text)
                    fin.close()
            replace_status = "Text replaced successfully"
            uploaded_files = get_uploaded_files()
            generated_corpuses = get_corpuses()


        elif request.method == 'POST' and request.form.get('delete'):
            file = request.form['getFileNames']
            if not file:
                deletion_status = "Please input filename to manipulate"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)

            delete_this = request.form['text']
            if not delete_this:
                deletion_status = "Please input text to delete."
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            relevant_files = find_relevant_files(file)
            relevant_corpuses = find_relevant_corpuses(file)
            if not relevant_files and not relevant_corpuses:
                deletion_status = "No such file exists"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads', f)))
                final_text=text.replace(delete_this,"")
                with open(os.path.join("app/uploads",f.split(".")[0]+'.txt'),'w') as fin:
                    fin.write(final_text)
                    fin.close()
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join('app/corpuses', f)))
                final_text=text.replace(delete_this,"")
                with open(os.path.join("app/corpuses",f.split(".")[0]+'.txt'),'w') as fin:
                    fin.write(final_text)
                    fin.close()
            deletion_status = "Text deleted successfully"
            uploaded_files = get_uploaded_files()
            generated_corpuses = get_corpuses()

        elif request.method == 'POST' and request.form.get('append'):
            file = request.form['getFileNames']
            if not file:
                appened_status = "Please input filename to manipulate"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            append_this = request.form['text']
            if not append_this:
                appened_status = "Please input text to append"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            relevant_files = find_relevant_files(file)
            relevant_corpuses = find_relevant_corpuses(file)
            if not relevant_files and not relevant_corpuses:
                appened_status = "No such file exists"
                return render_template('functionality3.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, replace_status=replace_status,
                                       deletion_status=deletion_status, appened_status=appened_status)
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads', f)))
                final_text = text+" "+append_this
                with open(os.path.join("app/uploads", f.split(".")[0] + '.txt'), 'w') as fin:
                    fin.write(final_text)
                    fin.close()
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join('app/corpuses', f)))
                final_text = text+" "+append_this
                with open(os.path.join("app/corpuses", f.split(".")[0] + '.txt'), 'w') as fin:
                    fin.write(final_text)
                    fin.close()
            appened_status = "Text appended successfully"
            uploaded_files = get_uploaded_files()
            generated_corpuses = get_corpuses()
        return render_template('functionality3.html', uploaded_files=uploaded_files,
                               generated_corpuses=generated_corpuses,replace_status=replace_status,
                               deletion_status=deletion_status,appened_status=appened_status)


    elif page == 'functionality4':
        uploaded_files = get_uploaded_files()
        generated_corpuses = get_corpuses()
        status = ''
        frequency = []
        if request.method == 'POST' and request.form.get('frequency'):
            files = request.form['files']
            if not files:
                status = "Please input file name"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, frequency=frequency)
            relevant_files = find_relevant_files(files)
            relevant_corpuses = find_relevant_corpuses(files)
            if not relevant_files and not relevant_corpuses:
                status = "No such file exists"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, frequency=frequency)
            text_to_operate = request.form.get('text')
            if not text_to_operate:
                return render_template('functionality4.html',uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses,status="Please input text", frequency=frequency)

            frequency = []
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads', f)))
                frequency.append({"file":f,'token':text_to_operate,'count':text.count(text_to_operate)})
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join('app/corpuses', f)))
                frequency.append({"file":f,'token':text_to_operate,'count':text.count(text_to_operate)})
            print(frequency)
            return render_template('functionality4.html', uploaded_files=get_uploaded_files(),
                                       generated_corpuses=get_corpuses(), frequency=frequency,status=status,zip=zip)

        elif request.method == 'POST' and request.form.get('getTop'):
            uploaded_files = get_uploaded_files()
            generated_corpuses = get_corpuses()
            data = []
            files = request.form['files']
            if not files:
                status = "Please input file name"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, data=data,zip=zip)
            relevant_files = find_relevant_files(files)
            relevant_corpuses = find_relevant_corpuses(files)
            if not relevant_files and not relevant_corpuses:
                status = "No such file exists"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, data=data,zip=zip)
            top_k = request.form.get('top-k')
            if not top_k:
                status = "Please input top-k parameter"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, data=data,zip=zip)
            n_gram = request.form.get('n-value')
            if not n_gram:
                status = "Please input n-gram parameter"
                return render_template('functionality4.html', uploaded_files=uploaded_files,
                                       generated_corpuses=generated_corpuses, status=status, data=data,zip=zip)

            n_gram = int(n_gram)
            top_k = int(top_k)
            for f in relevant_files:
                text = str(textract.process(os.path.join('app/uploads',f)))
                text = text.replace("\n"," ")
                text = text.replace("\\"," ")

                nGrams = list(nltk.ngrams(text.split(),n_gram))
                nGram_list = [" ".join(i) for i in nGrams]
                freq_dict = dict(Counter(nGram_list))
                sorted_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1])}
                print(sorted_dict)
                last_k_keys = list(sorted_dict.keys())[-top_k:]
                last_k_values = list(sorted_dict.values())[-top_k:]
                data.append({"file":f,"n-grams":last_k_keys,"frequency":last_k_values})
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join('app/corpuses',f)))
                text = text.replace("\n"," ")
                text = text.replace("\\"," ")
                nGrams = list(nltk.ngrams(text.split(),n_gram))
                nGram_list = [" ".join(i) for i in nGrams]
                freq_dict = dict(Counter(nGram_list))
                sorted_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1])}
                print(sorted_dict)
                last_k_keys = list(sorted_dict.keys())[-top_k:]
                last_k_values = list(sorted_dict.values())[-top_k:]
                data.append({"file":f,"n-grams":last_k_keys,"frequency":last_k_values})

            return render_template('functionality4.html', uploaded_files=get_uploaded_files(),
                                   generated_corpuses=get_corpuses(), status="", data=data,zip=zip)


    elif page == 'functionality5':
        data = []
        if request.method == 'POST' and request.form.get('frequency'):
            files = request.form['files']
            status = ''
            print(files)

            if not files:
                status = "Please input file name"
                return render_template('functionality5.html', uploaded_files=get_uploaded_files(),
                                       generated_corpuses=get_corpuses(), status=status)

            relevant_files = find_relevant_files(files)
            relevant_corpuses = find_relevant_corpuses(files)
            if not relevant_files and not relevant_corpuses:
                status = "No such file exists"
                return render_template('functionality5.html', uploaded_files=get_uploaded_files(),
                                       generated_corpuses=get_corpuses(), status=status, zip=zip)
            comparison_text = request.form.get('text')
            if not comparison_text:
                status = "Please input text"
                return render_template('functionality5.html', uploaded_files=get_uploaded_files(),
                                       generated_corpuses=get_corpuses(), status=status, zip=zip)


            for f in relevant_files:
                text = str(textract.process(os.path.join("app/uploads",f)))
                data.append({"file":f,"token":comparison_text,"frequency":text.count(comparison_text)})
            for f in relevant_corpuses:
                text = str(textract.process(os.path.join("app/corpuses",f)))
                data.append({"file":f,"token":comparison_text,"frequency":text.count(comparison_text)})

            print(data)
            return render_template('functionality5.html', uploaded_files=get_uploaded_files(),
                               generated_corpuses=get_corpuses(), status="",data=data,zip=zip)


    elif page == 'functionality6':
        if request.method == "POST" and request.form.get("store"):
            global all_action_chains
            functionality2 = request.form.get('functionality2')
            functionality3 = request.form.get('functionality3')
            functionality4 = request.form.get('functionality4')
            functionality5 = request.form.get('functionality5')
            funtionalities_that_are_chained = []
            if functionality2 == 'on':
                funtionalities_that_are_chained.append("functionality2")
            if functionality3 == 'on':
                funtionalities_that_are_chained.append("functionality3")
            if functionality4 == 'on':
                funtionalities_that_are_chained.append("functionality4")
            if functionality5 == 'on':
                funtionalities_that_are_chained.append("functionality5")
            print(funtionalities_that_are_chained)

            chain_for_UI = ">>".join(funtionalities_that_are_chained)
            with open('app/chains.txt','a') as chain_file:
                chain_file.write(chain_for_UI+"\n")
            return render_template('functionality6.html', generated_corpuses=get_corpuses(),
                                   uploaded_files=get_uploaded_files(),chain_for_UI=get_chains())

        return render_template('functionality6.html',generated_corpuses=get_corpuses(),uploaded_files=get_uploaded_files())











    return render_template(str(page)+'.html',generated_corpuses=get_corpuses(),uploaded_files=get_uploaded_files())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




if __name__ == '__main__':
    app.run(debug=True)

