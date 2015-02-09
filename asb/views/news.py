import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

from asb import db
import asb.forms

class NewsForm(asb.forms.CSRFTokenForm):
    """A form for a new news post."""

    title = wtforms.StringField('Title',
        [wtforms.validators.Required('Please enter a title')])
    text = wtforms.TextAreaField('Post',
        [wtforms.validators.Required('Your post is empty')])
    preview = wtforms.SubmitField('Preview')
    post = wtforms.SubmitField('Post')

@view_config(route_name='news', renderer='/indices/news.mako')
def news(context, request):
    """The entire news archive."""

    return {
        'news':
            db.DBSession.query(db.NewsPost)
            .order_by(db.NewsPost.post_time.desc())
            .all()
    }

@view_config(route_name='news.post', renderer='/news_post.mako',
  request_method='GET', permission='news.post')
def post_news(context, request):
    """A page for posting a news post."""

    return {'form': NewsForm(csrf_context=request.session)}

@view_config(route_name='news.post', renderer='/news_post.mako',
  request_method='POST', permission='news.post')
def post_news_commit(context, request):
    """Create a news post."""

    form = NewsForm(request.POST, csrf_context=request.session)

    if not form.validate() or form.preview.data:
        return {'form': form, 'now': datetime.datetime.now()}

    post = db.NewsPost(
        post_time=datetime.datetime.now(),
        posted_by_trainer_id=request.user.id,
        title=form.title.data,
        text=form.text.data
    )

    db.DBSession.add(post)
    return httpexc.HTTPSeeOther('/#news')
