import jinja2
from ._template import base
from ._template import index
from ._template import author_list
from ._template import display
from ._template import article

def render(template_base, template_extends):
    loader = jinja2.DictLoader(
        {
            'base': template_base,
            'extends': template_extends,
        }
    )
    env = jinja2.Environment(loader=loader)
    template = env.get_template('extends')
    return template

template_index = render(base, index)
template_author_list = render(base, author_list)
template_display = render(base, display)
template_article = render(base, article)