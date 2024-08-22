from notion.serializer.serializers import NotionSerializer
from notion.models.entity.notion import Notion
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

notion_token = os.getenv("NOTION_TOKEN")
headers = {
    'Authorization': f"Bearer {notion_token}",
    'Content-Type': 'application/json',
    'Notion-Version': '2022-02-22'
}
banco_notion = os.getenv("ID_DO_BANCO")

if not notion_token and banco_notion:
    raise ValueError(
        "Token de acesso ao Notion não encontrado no arquivo .env"
    )


def get_data_from_notion():
    url = f"https://api.notion.com/v1/database/{banco_notion}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return data['results']

# Criar Dados


class NotionCreateView(generics.CreateAPIView):
    serializer_class = NotionSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": banco_notion},
            "properties": {
                "title": {"title": [{"text": {"content": data["title"]}}]},
                "Prioridade": {"select": {"name": data["priority"]}},
                "Status": {"status": {"name": data["status"]}},
            }
        }
        response = requests.post(url, json=payload, headers=headers)

        # Verificação se a resposta foi bem-sucedida
        if response.status_code in [200, 201]:
            # Salvar a tarefa no banco de dados
            notion_id = response.json()["id"]
            notion = Notion.objects.create(
                title=data["title"],
                status=data["status"],
                priority=data["priority"],
                notion_page_id=notion_id
            )

            # Serializar os dados do objeto criado para retorno das respostas
            serialized_notion = NotionSerializer(notion).data

            # Registrar os dados no log em formato JSON
            print(json.dumps(serialized_notion, indent=4, ensure_ascii=False))

            # Retornar os dados criados na resposta
            return Response({"message": "Tarefa criada com sucesso", "data": serialized_notion}, status=status.HTTP_201_CREATED)
        else:
            print("Erro ao criar Notion:", response.text)
            return Response({"message": "Error creating Notion"}, status=status.HTTP_400_BAD_REQUEST)


# Atualizar e Deletar Dados


class NotionUpdateAndDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer

# Listar Dados


class NotionList(generics.ListCreateAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer

# Buscar dados no banco pelo ID


class NotionFindById(generics.RetrieveAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer
    lookup_field = 'pk'
