from django.conf.urls import url
from . import views
from django.urls import path
urlpatterns = [
    path('index/', views.index), # 主页，啥都木有
    path('chengji/', views.chengji), # 将学生新信息加入到查询队列
    path('kaowei/', views.kaowei), # 将考位加到查询队列
    path('neea/', views.neea), # 验证用户密码是否正确
    path('weixin/', views.weixin), # 被动-群成员信息回调
    path('robotmass/', views.robotmass), # 群发消息
    path('kick/', views.kick), # 匹配准备踢人的昵称和群
    path('kicking/', views.kicking), # 踢人
]
