from django.shortcuts import redirect, render
from .forms import FileUploadForm
from .models import Video
from .utils.functions import *
import cv2
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import base64
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    """ 簡単な説明
    動画処理のトップページのビューを想定。request.methodによって挙動を変えています。
    POST: 動画のアップロートを処理し、再びトップページへリダイレクト
    GET:  アップロードされた動画のリストを取得し、トップページをレンダリング
    """
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            # pkを取得し要素を追加する
            # upload_byを追加
            video = Video.objects.get(pk=post.pk)
            video.upload_by = request.user.username
            # basename(フォルダ名を除いたファイル名)を追加
            video.basename = Path(video.upload.path).name
            # 一フレーム目を保存してそのURLを追加する
            pngFullPath = video.upload.path.replace(".avi", ".png")
            firstFrame = getFirstFrame(video.upload.path, gray=True)
            cv2.imwrite(pngFullPath, firstFrame)
            video.firstFrameURL = post.upload.url.replace(".avi", ".png")
            video.save()
            return redirect(reverse('processer:index'))
    else:
        objs = Video.objects.all()
        if 'upload_by' in request.GET.keys():
            objs = objs.filter(upload_by=request.GET['upload_by'])
        form = FileUploadForm()
        context = {
            'form': form, 
            'objs': objs[::-1],
        }
        if 'upload_by' in request.GET.keys():
            context['upload_by'] = request.GET['upload_by']
        return render(request, 'processer/index.html', context)


def detail(request, pk):
    """ 簡単な説明
    動画処理の詳細のビューを想定。request.methodによって挙動を変えています。
    POST: Brightnessなどのパラメタを取得して動画処理をし、ダウンロードリンクを含めて詳細ページをレンダリング
    GET: 動画の詳細をレンダリング
    """
    if request.method == "GET":
        obj = Video.objects.get(pk=pk)
        context = {
            'obj': obj, 
            'processed': None,
        }
        return render(request, 'processer/detail.html', context)
    elif request.method == "POST":
        # パラメタを取得
        brightness = int(request.POST["brightness"])
        contrast = int(request.POST["contrast"])
        diffNum = int(request.POST["diffNum"])
        # 編集するObjectを取得
        obj = Video.objects.get(pk=pk)
        fullPath = str(settings.BASE_DIR) + str(Path(obj.upload.url))
        frames, width, height, _, fps, _ = load(fullPath, gray=True)
        # 動画処理
        frames = setBrightness(frames, brightness)
        frames = setContrast(frames, contrast)
        frames = rmBackground(frames, diffNum, gray=True)
        processedFullPath = fullPath.replace(".avi", "_processed.avi")
        writeVideo(processedFullPath, fps, width, height, frames, gray=True, kernel=1)
        context = {
            'obj': obj, 
            'processedPath': obj.upload.url.replace(".avi", "_processed.avi")
        }
        return render(request, 'processer/detail.html', context)


def getFrameViaAjax(request, pk):
    """画像(動画ではない)編集用 Ajax通信 
    パラメタを取得しBASE64形式にエンコードした画像をJSONで返却する
    """
    # パラメタを取得
    brightness = int(request.POST["brightness"])
    contrast = int(request.POST["contrast"])
    # 編集する画像のURLをObjectから取得
    obj = Video.objects.get(pk=pk)
    pngPath = obj.firstFrameURL
    pngFullPath = str(settings.BASE_DIR) + str(Path(pngPath))
    # 画像を編集
    firstFrame = cv2.imread(pngFullPath, cv2.IMREAD_GRAYSCALE)
    firstFrame = setBrightness(firstFrame, brightness)
    firstFrame = setContrast(firstFrame, contrast)
    # JSONレスポンス用に画像をBASE64エンコードする
    # Array -> bytes -> base64 -> str 
    imgbytes = cv2.imencode('.png', firstFrame)[1].tobytes()
    img_b64 = base64.b64encode(imgbytes)
    img_str = img_b64.decode("utf-8")
    d = {
        "img": "data:image/png;base64," + img_str,
        "brightness": str(brightness),
        "contrast": str(contrast)
    }
    return JsonResponse(d)