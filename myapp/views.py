from __future__ import unicode_literals
from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, UpvoteForm, SearchForm
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from django.contrib.auth.hashers import make_password, check_password
from instaclone.settings import BASE_DIR
from imgurpython import ImgurClient
from datetime import timedelta, datetime
from django.utils import timezone
import requests



def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            empty = len(username) == 0 and len(password) == 0
            if len(username) >= 4 and len(password) >= 3:
                user = UserModel(name=name, password=make_password(password), email=email, username=username)
                user.save()
                return render(request, 'success.html')
            text = {}
            text = "Username or password is not long enough"
            # return redirect('login/')
        else:
            form = SignUpForm()
    elif request.method == "GET":
        form = SignUpForm()
        today = datetime.now()
    return render(request, 'index.html', {'today': today, 'form': form})

    return render(request, 'index.html', {'form': form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            posts = PostModel.objects.all().order_by('-created_on')
            for post in posts:

                existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
                if existing_like:
                    post.has_liked = True

                if not existing_like:
                    LikeModel.objects.create(post_id=post_id, user=user)
                else:
                    existing_like.delete()

                return redirect('/feed/')


        else:
            return redirect('/feed/')


    else:
        return redirect('/login/')


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('created_on')
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + "\\" + post.image.url)

                client = ImgurClient('96096bbcfba4aa0', 'd2c3fd312cd45f22e0eb2e89dcd7a50020768369')
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                return redirect('/feed/')

        else:
            form = PostForm()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')

def send_response(comment_text):
    pass


def insta_clone_comment_text(args):
    pass

def comment_view(request, comment_text=None):
    #objective for review of positive or  negative  comment
    #set api_key
    api_key = "39JDDYmgIv5c1FPr54X0ozcQ6L8nnk29DejqgZ2h7aY"
    req_json = None
    # 1 is for positive comment and 0 is for negative comment
    try:
        req_json = requests.post.json()
        if req_json is not None:
             sentiment = req_json['sentiment']
             print req_json
             print req_json['confidence_score']
             if req_json['sentence_type'] == "Positive Comment":
                 #if comment is positive it is greater than 5 percent
                if req_json['confidence_score'] > 5:
                    #return positive comment
                   return 1
                else:
                    #return negative comment
                    return 0
             else:
                    return 0
    except:
                    return 0
#url for the parallel dots of sentiment
    url = "http://apis.paralleldots.com/sentiment"
    #check if user is valid
    user = check_validation(request)
    #check user exists and request post
    if user and request.method == 'POST':
       form = CommentForm(request.POST)
      #check if form is valid
       if  form.is_valid():
           #retrieve post id
            post_id = form.cleaned_data.get('post').id
           #accept comment text from the form
            comment_text = form.cleaned_data.get('comment_text')

            r = requests.get(url, params={"apikey": api_key, "comment": comment_text})
            print r
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            #comment save
            comment.save()
           #redirect to the feed page
            return redirect('/feed/')
       else:
            return redirect('/feed/')
    else:
        return redirect('/login/')


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None


def logout_view(request):
    user = check_validation(request)

    if user is not None:
        latest_sessn = SessionToken.objects.filter(user=user).last()
        if latest_sessn:
            latest_sessn.delete()
            return redirect("/login/")


# method to create upvote for comments
def upvote_view(request):
    user = check_validation(request)
    comment = None

    print ("upvote view")
    if user and request.method == 'POST':

        form = UpvoteForm(request.POST)
        if form.is_valid():

            comment_id = int(form.cleaned_data.get('id'))

            comment = CommentModel.objects.filter(id=comment_id).first()
            print ("upvoted not yet")

            if comment is not None:
                # print ' unliking post'
                print ("upvoted")
                comment.upvote_num += 1
                comment.save()
                print (comment.upvote_num)
            else:
                print ('stupid mistake')
                # liked_msg = 'Unliked!'

        return redirect('/feed/')
    else:
        return redirect('/feed/')


def query_based_search_view(request):
    user = check_validation(request)
    if user:
        if request.method == "POST":
            searchForm = SearchForm(request.POST)
            if searchForm.is_valid():
                print 'valid'
                username_query = searchForm.cleaned_data.get('searchquery')
                user_with_query = UserModel.objects.filter(username=username_query).first();
                posts = PostModel.objects.filter(user=user_with_query)
                return render(request, 'feed.html', {'posts': posts})
            else:
                return redirect('/feed/')
    else:
        return redirect('/login/')