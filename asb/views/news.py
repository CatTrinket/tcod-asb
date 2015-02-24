import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

from asb import db
import asb.forms
from asb.resources import NewsIndex

class NewsForm(asb.forms.CSRFTokenForm):
    """A form for a new news post."""

    title = wtforms.StringField('Title',
        [wtforms.validators.Required('Please enter a title')])
    text = wtforms.TextAreaField('Post',
        [wtforms.validators.Required('Your post is empty')])
    preview = wtforms.SubmitField('Preview')
    post = wtforms.SubmitField('Post')

class NewsDeleteForm(asb.forms.CSRFTokenForm):
    """A form for deleting a news post."""

    confirm = wtforms.BooleanField('I really want to delete this post:',
        [wtforms.validators.Required('Please check here')])
    delete = wtforms.SubmitField('Delete')

@view_config(context=NewsIndex, renderer='/indices/news.mako')
def news_index(context, request):
    """The entire news archive."""

    return {
        'news':
            db.DBSession.query(db.NewsPost)
            .order_by(db.NewsPost.post_time.desc())
            .all()
    }

@view_config(context=db.NewsPost, renderer='/news.mako')
def news(news_post, request):
    """A single news post."""

    return {'post': news_post}

@view_config(context=NewsIndex, name='post', renderer='/news_post.mako',
  request_method='GET', permission='news.post')
def post_news(context, request):
    """A page for posting a news post."""

    return {'form': NewsForm(csrf_context=request.session), 'post': None}

@view_config(context=NewsIndex, name='post', renderer='/news_post.mako',
  request_method='POST', permission='news.post')
def post_news_commit(context, request):
    """Create a news post."""

    form = NewsForm(request.POST, csrf_context=request.session)
    now = datetime.datetime.utcnow()

    if not form.validate() or form.preview.data:
        return {'form': form, 'now': now, 'post': None}

    post = db.NewsPost(
        title=form.title.data,
        identifier='temp-{0}'.format(now),
        post_time=now,
        posted_by_trainer_id=request.user.id,
        text=form.text.data
    )

    db.DBSession.add(post)
    db.DBSession.flush()
    post.set_identifier()

    return httpexc.HTTPSeeOther('/#news')

@view_config(context=db.NewsPost, name='edit', renderer='/news_post.mako',
  request_method='GET', permission='news.edit')
def edit_news(post, request):
    """A page for editing or deleting a news post."""

    return {
        'form':
            NewsForm(obj=post, prefix='edit', csrf_context=request.session),
        'delete_form':
            NewsDeleteForm(prefix='delete', csrf_context=request.session),
        'post': post
    }

@view_config(context=db.NewsPost, name='edit', renderer='/news_post.mako',
  request_method='POST', permission='news.edit')
def edit_news_commit(post, request):
    """Save an edited news post, or delete it."""

    form = NewsForm(request.POST, prefix='edit', csrf_context=request.session)
    delete_form = NewsDeleteForm(request.POST, prefix='delete',
         csrf_context=request.session)

    if delete_form.delete.data:
        if delete_form.validate():
            db.DBSession.delete(post)
            return httpexc.HTTPSeeOther('/news')

        return {'form': form, 'delete_form': delete_form, 'post': post}
    elif not form.validate() or form.preview.data:
        return {'form': form, 'delete_form': delete_form, 'post': post}

    post.title = form.title.data
    post.text = form.text.data
    post.set_identifier()

    return httpexc.HTTPSeeOther(
        request.resource_path(post.__parent__, post.__name__)
    )
