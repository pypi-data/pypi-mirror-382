from flask import Flask
from flask import send_file
from .templates import template_index
from .templates import template_author_list
from .templates import template_display
from .templates import template_article
from .database import session
from .database import table_author
from .database import table_article
from .database import name_map
from .database import table_name_next
from .database import name2object

app = Flask(__name__)

@app.route('/')
def index():
    return template_index.render()

@app.route('/author')
def display():
    authors = session.query(table_author).all()
    return template_author_list.render(authors=authors)

@app.route('/article/<int:article_id>')
def article_display(article_id):
    article = session.query(table_article).filter_by(id=article_id).one()
    return template_article.render(article=article)

@app.route('/<string:flag>/<int:flag_id>')
def item_display(flag, flag_id):
    table_name = name2object[f'table_{flag}']
    title = session.query(table_name).filter_by(id=flag_id).one()
    flag_next = table_name_next[f'table_{flag}'][6:]
    table_next = name2object[f'table_{flag_next}']
    items = session.query(table_next).filter_by(**{name_map[flag]: flag_id}).all()
    return template_display.render(title=title, flag_next=flag_next, items=items)

@app.route('/favicon.ico')
def favicon():
    return send_file('favicon.ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)