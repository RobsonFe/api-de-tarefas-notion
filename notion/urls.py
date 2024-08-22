from django.urls import path

from notion.views.notion_view import NotionCreateView, NotionFindById, NotionList, NotionUpdateAndDelete, FindIdByNotion

urlpatterns = [
    path('notion/create/', NotionCreateView.as_view(), name='create'),
    path('notion/list',  NotionList.as_view(), name='list'),
    path('notion/findby/<uuid:pk>', NotionFindById.as_view(), name='findbyid'),
    path('notion/findnotion/<str:notion_page_id>/',
         FindIdByNotion.as_view(), name='findNotionId'),
    path('notion/update/<uuid:pk>', NotionUpdateAndDelete.as_view(), name='update'),
    path('notion/delete/<uuid:pk>', NotionUpdateAndDelete.as_view(), name='delete'),
]
