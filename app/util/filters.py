from flask import current_app


# @current_app.template_filter()
# def format_title(title):
#     return title.lower().title()


@current_app.context_processor
def utility_processor():
    def format_title(title):
        if title is None:
            return None
        return title.lower().title()

    return dict(format_title=format_title)
