import os
from flask import Flask, flash, request, redirect, url_for, render_template, make_response, Response
from werkzeug.utils import secure_filename
import uuid

import time

from crossref.restful import Works
import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text

UPLOAD_FOLDER = 'api/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'tsv', 'bib'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def bib2authors(bibfile):
    try:
        with open(bibfile) as bibtex_file:
           bibtex_database = bibtexparser.load(bibtex_file)
    except:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        with open(bibfile) as bibtex_file:
            bibtex_database = bibtexparser.loads(bibtex_file.read(), parser=parser)

    works = Works()
    dois = []
    for k,v in bibtex_database.entries_dict.items():
        if 'year' not in v.keys():
            continue
        if int(v['year'])>=2016:
            auth = v['author'].split('and')
            authv = [x.strip() for x in auth]
            #authv = [x.strip().split(',') for x in auth]
            if 'doi'in v.keys():
                print('Recovering info from DOI: %s...' % v['doi'])
                d = works.doi( v['doi'])
                for va in d['author']:
                    if len(va['affiliation']):
                        dois.append([LatexNodes2Text().latex_to_text(f"{va['family']}, {va['given']}"),
                                     va['affiliation'][0]['name'],
                                     v['year'], v['doi'], d['title'][0]])
                    else:
                        dois.append([LatexNodes2Text().latex_to_text(f"{va['family']}, {va['given']}"),
                                     '',
                                     v['year'], v['doi'], d['title'][0]])
            else:
                for va in authv:
                    dois.append([LatexNodes2Text().latex_to_text(va), '', v['year'], '', v['title']])
    header = [['Author', 'Affiliation', 'Year', 'Doi', 'Title']]
    return header+dois

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # If you want to save the file 
            #filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
            file.save(filename)
            info = bib2authors(filename)

            try:
                os.remove(filename)
            except:
                print("Cannot Remove File")

            #return redirect(url_for('uploaded_file',
            #                        filename=filename))
            resp = make_response('\n'.join(['\t'.join(x) for x in info]))
            resp.headers["Content-Disposition"] = "attachment; filename=formatted.tsv"
            resp.headers["Content-Type"] = "text/tsv"
            return resp

    else:
        result = None

    return render_template('view.html',
                           result=result)

if __name__ == '__main__':
    app.run(port=5010)
