from django.urls import path

from notion.views.notion_view import NotionCreateView, NotionList, NotionUpdateAndDelete


urlpatterns = [
    path('notion/create/', NotionCreateView.as_view(), name='create'),
    path('notion/list',  NotionList.as_view(), name='list'),
    path('notion/update/<pk>', NotionUpdateAndDelete.as_view(), name='update'),
    path('notion/delete/<pk>', NotionUpdateAndDelete.as_view(), name='delete'),
]
