from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from . import serializers
from . import models


class UserRegisterView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    model = get_user_model()
    serializer_class = serializers.UserSerializer


class UserPrefView(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.UserPref.objects.all()
    serializer_class = serializers.UserPrefSerializer

    @list_route(methods=['get', 'put'])
    def preferences(self, request, pk=None):
        pref = models.UserPref.objects.filter(
            user_id=request.user.id)[:1].get()

        if request.method == 'PUT':
            pref.age = request.data.get('age')
            pref.gender = request.data.get('gender')
            pref.size = request.data.get('size')
            pref.save()

        serializer = serializers.UserPrefSerializer(pref)
        return Response(serializer.data)


class DogView(viewsets.ModelViewSet):
    queryset = models.Dog.objects.all()
    serializer_class = serializers.DogSerializer

    @detail_route(methods=['put'], url_path="(?P<dl>[^/.]+)")
    def changed(self, request, pk=None, dl=None):
        user = request.user
        models.UserDog.objects.filter(user=user, dog_id=pk).delete()

        if dl == 'liked':
            models.UserDog.objects.create(user=user, dog_id=pk, status='l')

        elif dl == 'disliked':
            models.UserDog.objects.create(user=user, dog_id=pk, status='d')

        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['get'], url_path="(?P<dl>[^/.]+)/next")
    def liked(self, request, pk=None, dl=None):
        user = request.user
        user_pref = models.UserPref.objects.get(user=user)

        age_range = []
        if 'b' in user_pref.age:
            for i in range(10):
                age_range.append(i)

        if 'y' in user_pref.age:
            for i in range(10, 19):
                age_range.append(i)

        if 'a' in user_pref.age:
            for i in range(19, 49):
                age_range.append(i)

        if 's' in user_pref.age:
            for i in range(49, 100):
                age_range.append(i)

        bqs = models.Dog.objects.filter(Q(gender__in=user_pref.gender),
                                        Q(age__in=age_range),
                                        Q(size__in=user_pref.size))

        if dl == 'liked':
            dog = bqs.filter(Q(id__gt=pk),
                             Q(userdog__status='l'),
                             Q(userdog__user=user.id))[:1]

            if not dog and int(pk) > 0:
                dog = bqs.filter(Q(id__gt=-1),
                                 Q(userdog__status='l'),
                                 Q(userdog__user=user.id))[:1]

        elif dl == 'disliked':
            dog = bqs.filter(Q(id__gt=pk),
                             Q(userdog__status='d'),
                             Q(userdog__user=user.id))[:1]

            if not dog and int(pk) > 0:
                dog = bqs.filter(Q(id__gt=-1),
                                 Q(userdog__status='d'),
                                 Q(userdog__user=user.id))[:1]

        else:
            dog = bqs.filter(Q(id__gt=pk), ~Q(userdog__user=user.id))[:1]

            if not dog and int(pk) > 0:
                dog = bqs.filter(Q(id__gt=-1), ~Q(userdog__user=user.id))[:1]

        if dog:
            serializer = serializers.DogSerializer(dog.get())
            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)
