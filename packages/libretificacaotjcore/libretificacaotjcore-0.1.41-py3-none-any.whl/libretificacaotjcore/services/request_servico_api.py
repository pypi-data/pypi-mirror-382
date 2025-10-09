import httpx


class RequestServicoApi:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.client = httpx.AsyncClient(timeout=120, verify=False)

    async def handler(self, *, mensagem_atualizacao: dict):
        print(self.token)
        response = await self.client.post(self.url, json=mensagem_atualizacao)

        if response.status_code != 200:
            raise Exception(f"Erro ao fazer request ao servico de API: {response.status_code}")
        
        await self.close()

    async def close(self):
        await self.client.aclose()