base = """
{% macro title_block() %}
    {% block title %}{% endblock %}
{% endmacro %}
{% macro content_block() %}
    {% block content %}{% endblock %}
{% endmacro %}
<html>
<head>
	<meta charset="utf-8"/>
	<title>{{ title_block() }}</title>
</head>
<body style="text-align:center;">
	<div style="display:inline-block;width:50%;text-align:left;">
	<h1>{{ title_block() }}</h1>
	<hr/>
	{{ content_block() }}
	<hr/>
	<h6>{{ title_block() }}</h6>
	</div>
</body>
</html>
"""

index = """
{% extends 'base' %}
{% block title %}
    index
{% endblock %}
{% block content %}
    <p><a href="/author">进入作者列表</a></p>
{% endblock %}
"""

author_list = """
{% extends 'base' %}
{% block title %}
    作者名单
{% endblock %}
{% block content %}
    {% for author in authors %}
        <p><a href="/author/{{ author.id }}">{{ author.name }}</a></p>
    {% endfor %}
{% endblock %}
"""

display = """
{% extends 'base' %}
{% block title %}
    {{ title.name }}
{% endblock %}
{% block content %}
    {% for item in items %}
        <p><a href="/{{ flag_next }}/{{ item.id }}">{{ item.name or item.title }}</a></p>
    {% endfor %}
{% endblock %}
"""

article = """
{% extends 'base' %}
{% block title %}
    {{ article.title }}
{% endblock %}
{% block content %}
    {{ article.content }}
{% endblock %}
"""
