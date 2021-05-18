from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/<page>')
def gotoNextPage(page):
    return render_template(str(page)+'.html')

if __name__ == '__main__':
    app.run(debug=True)

