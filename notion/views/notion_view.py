from asyncio.log import logger
from notion.serializer.serializers import NotionSerializer
from notion.models.entity.notion import Notion
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from dotenv import load_dotenv
import logging
import openpyxl
import requests
import json
import os

load_dotenv()

# Defina o nível de logging como INFO ou DEBUG
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

notion_token = os.getenv("NOTION_TOKEN")
headers = {
    'Authorization': f"Bearer {notion_token}",
    'Content-Type': 'application/json',
    'Notion-Version': '2022-02-22'
}
banco_notion = os.getenv("ID_DO_BANCO")

if not notion_token or not banco_notion:
    raise ValueError(
        "Token de acesso ao Notion ou ID do banco não encontrado no arquivo .env"
    )

# Buscar dados no Notion


def get_data_from_notion():
    url = f"https://api.notion.com/v1/database/{banco_notion}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return data['results']

# Função para salvar ou atualizar dados em uma planilha de Excel


def save_or_update_in_sheet(notion_data):
    file_path = "./planilhas/Tarefas.xlsx"
    sheet_name = "Tarefas"

    # Tente abrir o arquivo, ou crie um novo workbook se não existir
    if os.path.exists(file_path):
        workbook = openpyxl.load_workbook(file_path)
    else:
        workbook = openpyxl.Workbook()

    # Verifique se a worksheet já existe, senão crie uma nova
    if sheet_name in workbook.sheetnames:
        worksheet = workbook[sheet_name]
    else:
        worksheet = workbook.active
        worksheet.title = sheet_name
        # Cabeçalho correto
        worksheet.append(["Title", "Status", "Priority", "Notion Page ID"])

    # Verifique se o ID já existe para atualizar a linha correspondente
    id_exists = False
    for row in worksheet.iter_rows(min_row=2, values_only=False):
        if row[3].value == notion_data["notion_page_id"]:  # Notion Page ID está na 4ª coluna
            # Atualize a linha existente
            row[0].value = notion_data["title"]
            row[1].value = notion_data["status"]
            row[2].value = notion_data["priority"]
            id_exists = True
            break

    # Se o ID não existir, adicione uma nova linha
    if not id_exists:
        worksheet.append([
            notion_data["title"],              # Title na 1ª coluna
            notion_data["status"],             # Status na 2ª coluna
            notion_data["priority"],           # Priority na 3ª coluna
            notion_data["notion_page_id"]     # Notion Page ID na 4ª coluna
        ])

    # Salve a planilha
    workbook.save(file_path)
    logger.info(f"Planilha atualizada e salva em: {file_path}")

# Criar Dados


class NotionCreateView(generics.CreateAPIView):
    serializer_class = NotionSerializer

    def create(self, request, *args, **kwargs):
        try:
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

                # Atualizar a planilha
                notion_data = {
                    "notion_page_id": notion_id,
                    "title": data["title"],
                    "status": data["status"],
                    "priority": data["priority"]
                }
                save_or_update_in_sheet(notion_data)

                # Registrar os dados no log em formato JSON
                logger.info(json.dumps(serialized_notion,
                            indent=4, ensure_ascii=False))

            # Retornar os dados criados na resposta
            return Response({"message": "Tarefa criada com sucesso", "data": serialized_notion}, status=status.HTTP_201_CREATED)
        except Exception as erro:
            logger.error("Erro ao criar Notion: %s", erro)
            return Response({"message": "Erro ao criar tarefa"}, status=status.HTTP_400_BAD_REQUEST)

# Atualizar e Deletar Dados


class NotionUpdateAndDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        try:
            # Obter o objeto do banco de dados
            instance = self.get_object()
            data = request.data

            # Atualizar no banco de dados
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            updated_notion = serializer.instance

            # Atualizar a página no Notion
            notion_update_data = {
                "properties": {
                    "title": {  # Nome da propriedade no Notion
                        "title": [
                            {
                                "text": {
                                    "content": data.get("title", updated_notion.title),
                                },
                            },
                        ],
                    },
                    "Prioridade": {  # Nome da propriedade no Notion
                        "select": {
                            "name": data.get("priority", updated_notion.priority),
                        },
                    },
                    "Status": {  # Nome da propriedade no Notion
                        "status": {
                            "name": data.get("status", updated_notion.status),
                        },
                    },
                },
            }

            url = f"https://api.notion.com/v1/pages/{
                updated_notion.notion_page_id}"
            response = requests.patch(
                url, json=notion_update_data, headers=headers)

            if response.status_code not in [200, 202]:
                logger.error(
                    "Erro ao atualizar a página no Notion: %s", response.text)
                raise Exception("Erro ao atualizar a página no Notion")

            # Atualizar a planilha de Excel
            notion_data = {
                "notion_page_id": updated_notion.notion_page_id,
                "title": data.get("title", updated_notion.title),
                "status": data.get("status", updated_notion.status),
                "priority": data.get("priority", updated_notion.priority)
            }
            save_or_update_in_sheet(notion_data)

            # Serializar o objeto atualizado e os dados da resposta
            serialized_notion = NotionSerializer(updated_notion).data
            response_data = {
                "message": "Tarefa atualizada com sucesso", "data": serializer.data}

            # Registrar os dados no log em formato JSON
            logger.info("Dados Atualizados: %s", json.dumps(
                serialized_notion, indent=4, ensure_ascii=False))
            logger.info("Resposta: %s", json.dumps(
                response_data, indent=4, ensure_ascii=False))

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as erro:
            logger.error("Erro ao atualizar Notion: %s", erro)
            return Response({"message": "Erro ao atualizar tarefa"}, status=status.HTTP_400_BAD_REQUEST)

# Listar Dados


class NotionList(generics.ListCreateAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer

# Buscar dados no banco pelo ID


class NotionFindById(generics.RetrieveAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer
    lookup_field = 'pk'


class FindIdByNotion(generics.RetrieveAPIView):
    queryset = Notion.objects.all()
    serializer_class = NotionSerializer
    lookup_field = 'notion_page_id'
