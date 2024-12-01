from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, StudentViewSet, QuestaoViewSet, SimuladoViewSet, test_connection, user_info

router = DefaultRouter()
router.register(r'classes', ClassViewSet)
router.register(r'students', StudentViewSet)
router.register(r'questoes', QuestaoViewSet)
router.register(r'simulados', SimuladoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/test-connection/', test_connection, name='test_connection'),
    path('user-info/', user_info, name='user_info'),
]
