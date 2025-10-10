import asyncio
import httpx
import ssl
import certifi
from selectolax.parser import HTMLParser

async def test_crawl(url):
    # Configurar SSL para verificar certificados
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # Configurar o cliente HTTP com mais opções
    transport = httpx.AsyncHTTPTransport(retries=3, verify=ssl_context)
    
    # Configurar headers para parecer um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    async with httpx.AsyncClient(
        timeout=30.0, 
        follow_redirects=True,
        transport=transport,
        headers=headers
    ) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            # Primeiro, vamos verificar se conseguimos acessar a URL
            print(f"Acessando {url}...")
            
            # Primeiro, tente com HTTPS
            try:
                response = await client.get(url, headers=headers)
                print(f"Conexão HTTPS bem-sucedida!")
            except Exception as https_error:
                print(f"Erro ao acessar via HTTPS: {https_error}")
                # Se falhar, tente com HTTP
                http_url = url.replace('https://', 'http://')
                print(f"Tentando acessar via HTTP: {http_url}")
                response = await client.get(http_url, headers=headers)
                print(f"Conexão HTTP bem-sucedida!")
            
            print(f"Status code: {response.status_code}")
            print(f"Headers da resposta: {dict(response.headers)}")
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            # Verificar se é HTML
            if 'text/html' in response.headers.get('content-type', ''):
                # Tentar analisar o HTML
                try:
                    parser = HTMLParser(response.text)
                    title = parser.css_first('title')
                    print(f"Título da página: {title.text(strip=True) if title else 'Não encontrado'}")
                    
                    # Contar links
                    links = parser.css('a')
                    print(f"Número de links encontrados: {len(links)}")
                    
                    # Mostrar alguns links (apenas os 5 primeiros para não poluir a saída)
                    print("\nAlguns links encontrados:")
                    for i, link in enumerate(links[:5]):
                        href = link.attributes.get('href', '')
                        text = link.text(strip=True)[:50] + '...' if link.text(strip=True) else ''
                        print(f"  {i+1}. {href} - {text}")
                    
                    # Verificar se há algum formulário
                    forms = parser.css('form')
                    print(f"\nNúmero de formulários encontrados: {len(forms)}")
                    
                    for i, form in enumerate(forms, 1):
                        action = form.attributes.get('action', 'N/A')
                        method = form.attributes.get('method', 'GET')
                        print(f"  Formulário {i}: method={method}, action={action}")
                        
                except Exception as e:
                    print(f"Erro ao analisar HTML: {e}")
            else:
                print("A resposta não é HTML. Conteúdo:")
                print(response.text[:500])  # Mostrar apenas os primeiros 500 caracteres
                
        except httpx.HTTPStatusError as e:
            print(f"Erro de status HTTP: {e}")
            print(f"Resposta: {e.response.text[:500]}..." if e.response else "Sem resposta")
        except httpx.RequestError as e:
            print(f"Erro na requisição: {e}")
            print(f"Tipo de erro: {type(e).__name__}")
        except ssl.SSLError as e:
            print(f"Erro de SSL: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")
            import traceback
            traceback.print_exc()

# Executar o teste
if __name__ == "__main__":
    # Tentando com www. para ver se resolve o problema de redirecionamento
    url = "http://www.rosasdoparto.com.br"
    asyncio.run(test_crawl(url))
