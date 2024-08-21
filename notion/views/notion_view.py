
from notion.models.entity.notion import Notion
from notion.serializer.serializers import NotionSerializer
from rest_framework import generics
from dotenv import load_dotenv
import os


load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
banco_notion = os.getenv("ID_DO_BANCO")

if not notion_token and banco_notion:
    raise ValueError(
        "Token de acesso ao Notion não encontrado no arquivo .env")

# Criar Dados


class NotionCreateView(generics.CreateAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer

# Atualizar e Deletar Dados


class NotionUpdateAndDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer

# Listar Dados


class NotionList(generics.ListCreateAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer
