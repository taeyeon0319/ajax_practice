from django.shortcuts import render,redirect,get_object_or_404
from .models import * #여기 *로 바꾸어주기!!!!!!!!!!
from django.contrib.auth.decorators import login_required #login_required = 로그인이 되어있는지 여부 확인
from django.views.decorators.http import require_POST # require_POST = http의 형식에서만 실행해라. 
from django.http import HttpResponse # HttpResponse : html 파일, 이미지 등 다양항 응답을 함.
import json #딕셔너리를 json형식으로 바꿈.
from django.template.loader import render_to_string

def main(request):
    items = Post.objects.all()
    return render(request, 'items/home.html', {'items':items})

def new(request):
    return render(request, 'items/new.html')

def create(request):
    if request.method=="POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        user = request.user
        Post.objects.create(title=title, content=content, image=image,user=user)
    return redirect('main')

def show(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.view_count = post.view_count+1
    post.save()
    user = request.user
    context = {
        'post':post,
        'user':user,
        'comments': post.comments.all().order_by('-created_at')
    }
    return render(request, 'items/show.html', context)
    return render(request, 'items/show.html', {'post':post})


#삭제하기
def delete(request,post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.delete()
    return redirect('main')

#좋아요!
@require_POST
@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_like, post_like_created = Like.objects.get_or_create(user=request.user, post=post)

    if not post_like_created:
        post_like.delete()
        result="like_cancel"
    else:
        result="like"
    context={
        "like_count":post.like_count,
        "result":result
    }
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required
@require_POST
def dislike_toggle(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_dislike, post_dislike_created = Dislike.objects.get_or_create(user=request.user, post=post)

    if not post_dislike_created:
        post_dislike.delete()
        result ="dislike_cancel"
    else:
        result = "dislike"

    context = {
        "dislike_count": post.dislike_count,
        "result": result
    }
    return HttpResponse(json.dumps(context), content_type="application/json")

@login_required
@require_POST
def create_comment(request, post_id):
    user = request.user
    post = get_object_or_404(Post, pk=post_id)
    content = request.POST.get('content')
    comment = Comment.objects.create(writer=user, post=post, content=content)
    rendered = render_to_string('comments/_comment.html', { 'comment': comment, 'user': request.user})
    context = {
        'comment' : rendered
    }
    return HttpResponse(json.dumps(context), content_type="application/json")

def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    context = {
        'comment_id': comment_id,
    } 
    return HttpResponse(json.dumps(context), content_type="application/json")  
