from operator import itemgetter
from itertools import groupby
from collections import Counter 

from django.shortcuts import render, get_object_or_404
from django.db.models.functions import TruncDate

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TagListSerializer, PhotoListSerializer, PhotoDetailSerializer, PhotoCommentSerializer, SimplePhotoListSerializer, AlbumListSerializer, AlbumDetailSerializer

from accounts.models import Group, UserBabyRelationship
from .models import Tag, Photo, PhotoComment, PhotoTag, PhotoGroup, Album, AlbumPhotoRelationship, AlbumTag
# Create your views here.

class TagListView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data) 

class BabyTagView(APIView):
    def get(self, request):
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=cb)
        if relationship.rank_id == 3:
            if relationship.group:
                photos_guest = Photo.objects.filter(baby=cb, photo_scope=2, permitted_groups=relationship.group)
                photos_all = Photo.objects.filter(baby=cb, photo_scope=0)
                photos = (photos_guest | photos_all).distinct()
            else:
                photos = Photo.objects.filter(baby=cb, photo_scope=0)
        else:
            photos = Photo.objects.filter(baby=cb)
        tags = Tag.objects.none()
        for photo in photos:
            tags = tags | photo.photo_tags.all()
        tags = list(tags)
        tag_count = Counter(tags).most_common(5)
        tags = [tag[0] for tag in tag_count]
        # print(tag_count)
        # tags = sorted(tags, key = tags.count, reverse = True) 
        # print(tags)
        # tags = list(set(tags))
        serializer = TagListSerializer(tags, many=True)
        return Response(serializer.data)



class PhotoListView(APIView):
    # 아기의 전체 사진 조회
    def get(self, request):
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=cb)
        if relationship.rank_id == 3:
            if relationship.group:
                photos_guest = Photo.objects.filter(baby=cb, photo_scope=2, permitted_groups=relationship.group)
                photos_all = Photo.objects.filter(baby=cb, photo_scope=0)
                photos = (photos_guest | photos_all).distinct().values('id', 'last_modified', 'image_url').order_by('-last_modified').annotate(last_modified_date=TruncDate('last_modified'))
            else:
                photos = Photo.objects.filter(baby=cb, photo_scope=0).values('id', 'last_modified', 'image_url').order_by('-last_modified').annotate(last_modified_date=TruncDate('last_modified'))
        else:
            photos = Photo.objects.filter(baby=cb).values('id', 'last_modified', 'image_url').order_by('-last_modified').annotate(last_modified_date=TruncDate('last_modified'))

        key = itemgetter('last_modified_date')
        rows = groupby(photos, key=key)

        return_data = []
        for date, items in rows:
            items = list(items)
            daily_photo = {
                "date": date,
                "photos": items
            }
            return_data.append(daily_photo)

        return Response(return_data)


    # 아기 사진 업로드
    def post(self, request):
        cb = request.user.current_baby.id
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        new_photos = request.data
        for photo in new_photos:
            photo["baby"] = cb
            serializer = PhotoDetailSerializer(data=photo)
            if serializer.is_valid(raise_exception=True):
                created_photo = serializer.save(creator=request.user, modifier=request.user)
                # tag
                for tag_name in photo['tags']:
                    try:
                        tag = Tag.objects.get(tag_name=tag_name)
                    except:
                        tag = Tag(tag_name=tag_name)
                        tag.save()
                    PhotoTag(tag=tag, photo=created_photo).save()
                    for album in tag.tagged_albums.all().filter(baby=cb):
                        album_photo = AlbumPhotoRelationship(album=album, photo=created_photo)
                        album_photo.save()
                        if not album.cover_photo:
                            album.cover_photo = created_photo.image_url
                            album.save()

                # groups
                if photo['photo_scope'] == 2:
                    for group_id in photo['groups']:
                        PhotoGroup(group=get_object_or_404(Group, pk=group_id), photo=created_photo).save()
        return Response({"message":"사진이 등록되었습니다."})

class PhotoDetailView(APIView):
    # 특정 사진 디테일 정보 조회
    def get(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        if request.user.current_baby == photo.baby:
            relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=request.user.current_baby)
            if photo.photo_scope == 0 or relationship.rank_id in [1, 2]:
                serializer = PhotoDetailSerializer(photo)
                return Response(serializer.data)
            else:
                if photo.photo_scope == 1:
                    return Response({"message": "접근 권한이 없습니다."}, status=400)
                else:
                    if len(PhotoGroup.objects.filter(photo=photo, group=relationship.group)):
                        serializer = PhotoDetailSerializer(photo)
                        return Response(serializer.data)
                    else:
                        return Response({"message": "접근 권한이 없습니다."}, status=400)
        else:
            return Response({"message": "접근 권한이 없습니다."}, status=400)
    
    # 특정 사진 디테일 정보 수정
    def put(self, request, photo_id):
        data = request.data
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=request.user.current_baby)
        if relationship.rank_id == 3:
            return Response({"message": "수정할 권한이 없습니다."}, status=400)
        else:
            photo = get_object_or_404(Photo, id=photo_id)        
            # tags

            for tag in photo.photo_tags.all():
                for album in tag.tagged_albums.all().filter(baby=cb):
                    try:
                        get_object_or_404(AlbumPhotoRelationship, album=album, photo=photo).delete()
                        if album.cover_photo == photo.image_url:
                            if album.photos.first():
                                album.cover_photo = album.photos.first().image_url
                            else:
                                album.cover_photo = ''
                            album.save()
                    except:
                        pass

            photo.photo_tags.clear()
            for tag_name in data['tags']:
                try:
                    tag = Tag.objects.get(tag_name=tag_name)
                except:
                    tag = Tag(tag_name=tag_name)
                    tag.save()
                PhotoTag(tag=tag, photo=photo).save()
                for album in tag.tagged_albums.all().filter(baby=cb):
                    try:
                        get_object_or_404(AlbumPhotoRelationship, album=album, photo=photo)
                        if not album.cover_photo:
                            album.cover_photo = photo.image_url
                            album.save()
                    except:
                        album_photo = AlbumPhotoRelationship(album=album, photo=photo)
                        album_photo.save()
                        if not album.cover_photo:
                            album.cover_photo = photo.image_url
                            album.save()

            # scope
            photo.permitted_groups.clear()
            photo.photo_scope = data['photo_scope']
            if data['photo_scope'] == 2:
                for group_id in data['groups']:
                        PhotoGroup(group=get_object_or_404(Group, pk=group_id), photo=photo).save()
            photo.save()
            serializer = PhotoDetailSerializer(photo)
            return Response(serializer.data)

    # 특정 사진 삭제
    def delete(self, request, photo_id):
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=request.user.current_baby)
        if relationship.rank_id == 3:
            return Response({"message": "삭제할 권한이 없습니다."}, status=400)
        else:
            photo = get_object_or_404(Photo, id=photo_id)
            for temp_relationship in AlbumPhotoRelationship.objects.filter(photo=photo).all():
                album = temp_relationship.album
                temp_relationship.delete()
                if album.cover_photo == photo.image_url:
                    if album.photos.first():
                        album.cover_photo = album.photos.first().image_url
                    else:
                        album.cover_photo = ''
                    album.save()
            photo.delete()
            return Response({"message":"사진이 삭제되었습니다."}, status=200)

class PhotoCommentListView(APIView):
    # 사진 댓글 리스트 조회
    def get(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        serializer = PhotoCommentSerializer(photo.comments.order_by('-create_date'), many=True)
        return Response(serializer.data)

    # 사진 댓글 생성
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        serializer = PhotoCommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, photo=photo)
        return Response(serializer.data)


class PhotoCommentDetailView(APIView):
    # 사진 댓글 수정
    def put(self, request, photo_id, comment_id):
        comment = get_object_or_404(PhotoComment, id=comment_id)
        # 여기서 권한 검증이 한 번 들어가줘야함
        if comment.user.id == request.user.id:
            serializer = PhotoCommentSerializer(comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        else:
            return Response({"message": "작성자만 수정할 수 있습니다."}, status=400)

    # 사진 댓글 삭제
    def delete(self, request, photo_id, comment_id):
        comment = get_object_or_404(PhotoComment, id=comment_id)
        if comment.user.id == request.user.id:
            comment.delete()
            return Response({"message":"댓글이 삭제되었습니다."}, status=200)
        else:
            return Response({"message": "작성자만 삭제할 수 있습니다."}, status=400)


class PhotoSearchView(APIView):
    def post(self, request):
        keyword = request.data["keyword"]
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        searched_photos = Photo.objects.none()
        tags = Tag.objects.filter(tag_name__icontains=keyword)
        for tag in tags:
            searched_photos = searched_photos | tag.tagged_photos.all()
        searched_photos = searched_photos.distinct().filter(baby=cb)

        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=cb)
        if relationship.rank_id == 3:
            if relationship.group:
                photos_guest = searched_photos.filter(photo_scope=2, permitted_groups=relationship.group)
                photos_all = searched_photos.filter(photo_scope=0)
                searched_photos = (photos_guest | photos_all).distinct().order_by('-last_modified')
            else:
                searched_photos = searched_photos.filter(photo_scope=0).order_by('-last_modified')
        else:
            searched_photos = searched_photos.order_by('-last_modified')
        
        serializer = PhotoListSerializer(searched_photos, many=True)
        return Response(serializer.data)


class PhotoEmotionView(APIView):
    def get(self, request):
        emotions = ['행복', '슬픔', '놀람', '화남', '역겹', '무섭']
        return_data = []
        for emotion in emotions:
            if Tag.objects.filter(tag_name=emotion).exists():
                emotion_tag = get_object_or_404(Tag, tag_name=emotion)
                # print(emotion_tag.tagged_photos.all())
                serializer = PhotoListSerializer(emotion_tag.tagged_photos.all().filter(baby=request.user.current_baby), many=True)
                if serializer.data:
                    return_data.append({
                        'id': emotion_tag.id,
                        'emotion': emotion,
                        'photos': serializer.data
                    })
        return Response(return_data)
                


class AlbumListView(APIView):
    # 전체 앨범 목록 가져오기
    def get(self, request):
        baby = request.user.current_baby
        albums = Album.objects.filter(baby=baby).order_by('-create_date')
        serializer = AlbumListSerializer(albums, many=True)
        return Response(serializer.data)

    # 새 앨범 생성
    def post(self, request):
        baby = request.user.current_baby
        data = {
            'album_name': request.data['album_name']
        }
        serializer = AlbumDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            created_album = serializer.save(baby=baby, creator=request.user)

            # 만약 tags들이 있는 경우 태그 정보 저장 
            if request.data['tags']:
                for tag_name in request.data['tags']:
                    try:
                        tag = Tag.objects.get(tag_name=tag_name)
                    except:
                        tag = Tag(tag_name=tag_name)
                        tag.save()
                    AlbumTag(tag=tag, album=created_album).save()

            # 만약 photos들이 있는 경우 사진 정보 저장 
            if request.data['photos']:
                for photo_id in request.data['photos']:
                    photo = get_object_or_404(Photo, id=photo_id)
                    album_photo = AlbumPhotoRelationship(album=created_album, photo=photo)
                    album_photo.save()
                # 첫번째 사진을 cover_photo로 지정
                created_album.cover_photo = get_object_or_404(Photo, id=request.data['photos'][0]).image_url
                created_album.save()
            
            # 현재 시점에서 태그가 걸려있는 사진을 앨범에 넣어줌(중복은 안됨)
            for tag in created_album.album_tags.all():
                for photo in tag.tagged_photos.all().filter(baby=baby):
                    try: # 이미 들어있는 지 확인
                        get_object_or_404(AlbumPhotoRelationship, album=created_album, photo=photo)
                    except: # 없으면 앨범에 사진 추가
                        album_photo = AlbumPhotoRelationship(album=created_album, photo=photo)
                        album_photo.save()
            
            if not created_album.cover_photo:
                if created_album.photos.first():
                    created_album.cover_photo = created_album.photos.first().image_url
                    created_album.save()

            return Response(serializer.data)
        return Response(serializer.errors)


class AlbumDetailView(APIView):
    # 특정 앨범 정보 가져오기
    def get(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        serializer = AlbumListSerializer(album)
        return Response(serializer.data)

    # 앨범 정보(앨범명, 태그) 수정
    def put(self, request, album_id):
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        album = get_object_or_404(Album, id=album_id)
        serializer = AlbumDetailSerializer(album, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            # 태그 정보 수정하는 경우
            if request.data['tags']:
                for photo in album.photos.all():
                    if len(photo.photo_tags.all() & album.album_tags.all()):
                        get_object_or_404(AlbumPhotoRelationship, album=album, photo=photo).delete()
                album.album_tags.clear()
                for tag_name in request.data['tags']:
                    try:
                        tag = Tag.objects.get(tag_name=tag_name)
                    except:
                        tag = Tag(tag_name=tag_name)
                        tag.save()
                    AlbumTag(tag=tag, album=album).save()
                    for photo in tag.tagged_photos.all().filter(baby=cb):
                        try: # 이미 들어있는 지 확인
                            get_object_or_404(AlbumPhotoRelationship, album=album, photo=photo)
                        except: # 없으면 앨범에 사진 추가
                            album_photo = AlbumPhotoRelationship(album=album, photo=photo)
                            album_photo.save()

            if not album.cover_photo:
                if album.photos.first():
                    album.cover_photo = album.photos.first().image_url
                    album.save()

            return Response(serializer.data)
        return Response(serializer.errors)

    # 앨범 삭제
    def delete(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        album.delete()
        return Response({"message":"앨범이 삭제되었습니다."})

class AlbumPhotoListView(APIView):
    def get(self, request, album_id):
        print("HELLO")
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        album = get_object_or_404(Album, id=album_id)
        photos = album.photos.order_by('-last_modified').values_list('id', flat=True)
        # serializer = SimplePhotoListSerializer(photos, many=True)
        # return Response(serializer.data)
        return Response({ 'photos': photos })

class AlbumPhotoView(APIView):
    # 앨범 사진 리스트
    def get(self, request, album_id):
        cb = request.user.current_baby
        if not cb:
            raise ValueError('아이를 생성하거나 선택해주세요.')
        album = get_object_or_404(Album, id=album_id)
        relationship = get_object_or_404(UserBabyRelationship, user=request.user, baby=cb)
        # photos_album = album.photos
        # photos_tag = Photo.objects.none()
        # tags = album.album_tags.values()
        # for tag in tags:
        #     photos_tag = photos_tag | get_object_or_404(Tag, tag_name=tag['tag_name']).tagged_photos.all()
        # temp_photos = (photos_album.all() | photos_tag.all().filter(baby=cb)).distinct()

        if relationship.rank_id == 3:
            if relationship.group:
                photos_guest = album.photos.filter(photo_scope=2, permitted_groups=relationship.group)
                photos_all = album.photos.filter(photo_scope=0)
                photos = (photos_guest.all() | photos_all.all()).distinct().order_by('-last_modified')
            else:
                photos = album.photos.filter(photo_scope=0).order_by('-last_modified')
        else:
            photos = album.photos.order_by('-last_modified')
            
        serializer = PhotoListSerializer(photos, many=True)
        return Response(serializer.data)

    # 앨범에 사진 추가
    def post(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        for photo_id in request.data['photos']:
            photo = get_object_or_404(Photo, id=photo_id)
            if AlbumPhotoRelationship.objects.filter(album=album, photo=photo).exists():
                continue
            album_photo = AlbumPhotoRelationship(album=album, photo=photo)
            album_photo.save()
            if not album.cover_photo:
                album.cover_photo = photo.image_url
                album.save()
        return Response({"message":"사진(들)이 앨범에 추가되었습니다."})

    # 앨범에서 사진 삭제
    def put(self, request, album_id):
        album = get_object_or_404(Album, id=album_id)
        for photo_id in request.data['photos']:
            photo = get_object_or_404(Photo, id=photo_id)
            album_photo = get_object_or_404(AlbumPhotoRelationship, album=album, photo=photo)
            album_photo.delete()

            if album.cover_photo == photo.image_url:
                album.cover_photo = ''
                album.save()
        if not album.cover_photo:
            if album.photos.first():
                album.cover_photo = album.photos.first().image_url
                album.save()

        # cover_photo = get_object_or_404(Photo, image_url=album.cover_photo).id

        # 커버 사진으로 지정된 사진이 삭제되는 경우
        # if cover_photo in request.data['photos']:
        #     try:
        #         new_cover_photo = AlbumPhotoRelationship.objects.filter(album=album)[0].photo.image_url
        #         album.cover_photo = new_cover_photo
        #     except:
        #         album.cover_photo = ''
        #     album.save()
        return Response({"message":"사진(들)이 앨범에서 삭제되었습니다."})

    