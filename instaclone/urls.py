
from django.conf.urls import url
from django.contrib import admin
from myapp.views import signup_view, login_view, feed_view, post_view, like_view, comment_view, upvote_view, query_based_search_view


urlpatterns = [
    url('searchfilter/', query_based_search_view),
    url('upvote/', upvote_view),
    url('comment/',comment_view),
    url('like/',like_view),
    url('post/', post_view),
    url('feed/', feed_view),
    url('login/',login_view),
    url('',signup_view)
]

