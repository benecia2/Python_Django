from django.shortcuts import render, redirect
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from myapp01.models import Board, Comment
from django.db.models import Q

import urllib.parse
import math

# Create your views here.

# 업로드 파일위치
UPLOAD_DIR = 'D:/DJANGOWORK/upload/'
# write_form
def write_form(request):
    return render(request, 'board/write.html')

# insert 추가하기
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0
    if 'file' in request.FILES :
        file = request.FILES['file']
        fsize = file.size
        fname = file.name
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer = request.POST['writer'],
                title = request.POST['title'],
                content = request.POST['content'],
                filename = fname,
                filesize = fsize
                )
    dto.save()

    # return render(request, 'board/write.html') <-- 추가할때만 list할때는 이거 사용x
    return redirect("/list/")

# list 전체보기(기본)    --> list.html로      검색기능이 없는 list
# def list(request):
#     boardList = Board.objects.all()
#     boardCount = Board.objects.all().count
#     context ={'boardList': boardList, 'boardCount': boardCount}
#     return render(request, 'board/list.html', context)


# list(검색추가)
def list(request):
    page = request.GET.get('page',1)
    word = request.GET.get('word','')
    field = request.GET.get('field', 'title')
    # count
    if field == 'all':
        boardCount = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count

    # page
    pageSize = 5
    blockPage = 3
    currentPage = int(page)
    # 123[다음]    [이전]456[다음]      [이전]7(89) 
    totPage = math.ceil(boardCount/pageSize) # 총 페이지 수(7)
    startPage = math.floor((currentPage-1)/blockPage)*blockPage+1
    endPage = startPage+blockPage-1 #( 현재 페이지가 7이라면 )
    if  endPage > totPage :
        endPage = totPage

    start = (currentPage-1)*pageSize

    # 내용
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word)|
                                        Q(title__contains=word)|
                                        Q(content__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(Q(writer__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(Q(title__contains=word)).order_by('-idx')[start:start+pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(Q(content__contains=word)).order_by('-idx')[start:start+pageSize]
    else:
        boardList = Board.objects.all().order_by('-idx')[start:start+pageSize]


    context = {'boardList' : boardList,
                'boardCount' : boardCount,
                'field' : field,
                'word' : word,
                'startPage' : startPage,
                'blockPage' : blockPage,
                'endPage' : endPage,
                'totPage': totPage,
                'range': range(startPage,endPage+1),
                'currentPage' : currentPage}
    return render(request, 'board/list.html', context)





# detail : 상세보기     /detail/1" ==> detail/<int:board_idx>
def detail(request, board_idx):
    # print('board_idx : ',board_idx)
    dto = Board.objects.get(idx=board_idx)
    # 조회수 1증가
    dto.hit_up()
    dto.save()
    # comment list
    commentList = Comment.objects.filter(board_idx = board_idx).order_by('-idx')
    commentCnt = Comment.objects.filter(board_idx=board_idx).count
    print('commentList sql : ', commentList.query)
    return render(request, 'board/detail.html',{'dto':dto,  'commentList': commentList})


# detail_idx : 상세보기     /detail_idx?idx=1" 
def detail_idx(request):
    id = request.GET['idx'] #'idx' 값을 id에 담겠다.
    # print("id:",id)
    dto = Board.objects.get(idx=id)
    # 조회수 1증가
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail1.html', {'dto':dto})


# delete : 삭제
def delete(request,board_idx):
    Board.objects.get(idx=board_idx).delete()
    return redirect("/list/")


# download_count
def download_count(request):
    id = request.GET['idx']
    print('id : ',id)
    dto = Board.objects.get(idx = id)
    dto.down_up()   # 다운로드 수 증가
    dto.save()
    count = dto.down    # 다운로드 수
    print('count : ', count)
    return JsonResponse({'idx' : id, 'count': count})

# download
def download(request):
    id = request.GET['idx']
    dto = Board.objects.get(idx = id)
    path = UPLOAD_DIR + dto.filename
    # filename = urllib.parse.quote(dto.filename)
    filename = dto.filename

    with open(path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition']="attachment;filename*=UTF-8''{0}".format(filename)

        return response
    
# update_form
def update_form(request, board_idx):
    dto = Board.objects.get(idx=board_idx)
    context = {'dto':dto}
    return render(request, 'board/update.html', context)
    
# update
@csrf_exempt
def update(request):
    id = request.POST['idx']
    dto = Board.objects.get(idx = id)
    fname = dto.filename
    fsize = dto.filesize
    # file 수정
    if 'file' in request.FILES :
        file = request.FILES['file']
        fsize = file.size
        fname = file.name
        fp = open('%s%s' %(UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto_update = Board(id,
                writer = request.POST['writer'],
                title = request.POST['title'],
                content = request.POST['content'],
                filename = fname,
                filesize = fsize
               )
    dto_update.save()
    return redirect("/list/")

# comment
@csrf_exempt
def comment_insert(request):
    id = request.POST['idx']
    cdto = Comment(board_idx = id, writer = 'aa', content = request.POST['content'])

    cdto.save()

    # return redirect("detail_idx?idx="+id)
    return redirect("/detail/"+id)