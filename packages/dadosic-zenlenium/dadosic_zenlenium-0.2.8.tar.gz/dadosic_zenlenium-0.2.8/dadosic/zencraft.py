from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from zenpy import Zenpy
from zenpy.lib.api_objects import CustomField, Ticket, Comment, User

from zenpy.lib.exception import APIException
from requests.exceptions import RequestException, ConnectionError, Timeout
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException

from dataclasses import dataclass
from typing import Optional, Dict, Any, Iterable, List
import traceback
import logging
from zoneinfo import ZoneInfo
import datetime
import json

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = True

#Timeout padrão selenium
TIMEOUT = 300

#Status do heartbeat
execucao = 'EM EXECUÇÃO'
aguardando = 'AGUARDANDO CASOS'
erro = 'ERRO'
manutencao = 'EM MANUTENÇÃO'
desligado = 'DESLIGADO'

__all__ = [
        #Exceções
           'APIException', 'RequestException', 'ConnectionError', 'Timeout', 'WebDriverException', 
           'NoSuchElementException', 'StaleElementReferenceException', 'TimeoutException',
        #Bibliotecas
           'sleep', 'requests', 'urllib3',
        #Selenium
           'webdriver', 'ChromeOptions', 'FirefoxOptions', 'Service', 'By', 'WebDriverWait', 'EC', 'Select',
           'ActionChains', 'Keys',
        #Zenpy
           'Zenpy', 'CustomField', 'Ticket', 'Comment',
           'User',
        #Classes
           'Heartbeat', 'Driver_Selenium', 'Zendesk_Selenium', 'Zendesk_Zenpy', 'BotsLogger',
        #Variaveis
           'execucao', 'aguardando', 'erro', 'manutencao', 'desligado'
           ]

class Heartbeat():
    """Destinada a enviar atualizações via API para o painel de bots."""
    def __init__(self, bot_id, endpoint, token):
        if not all([bot_id, endpoint, token]):
            raise ValueError("bot_id, endpoint, e token são obrigatórios para o Heartbeat.")
        self.bot_id = bot_id
        self.endpoint = endpoint
        self.token = token
    

    def alertas(self, alertas=None, status=None, warning=None, ticket_id=None):
        """Envia alertas via gchat, status para o painel e registro de casos realizados.

        Args:
            alertas: Envia notificação do status do RPA via GCHAT.
            status: Envia o status atual do bot para o painel de acompanhamento.
            warning: Envia uma notificação do erro do RPA via GCHAT.
            ticket_id: Envia o ticket para registro no banco e contagem de casos.
        """
        url_todos_status = self.endpoint
        headers = {
            'Token': self.token, 
            "Content-Type": "application/json"
        }
        payload = {
            "bot_id": self.bot_id,
        }
        campos_opcionais = [
            ("alertas", alertas),
            ("status", status),
            ("warning", warning),
            ("ticket_id", ticket_id),
        ]

        for campo, valor in campos_opcionais:
            if valor:
                payload[campo] = valor

        try:
            alert = requests.put(url_todos_status, json=payload, headers=headers, timeout=10, verify=False)
            print(f"--- Resposta da API Alerta ---\nCódigo de Status: {alert.status_code}")

        except Exception as e:
            print(f"Um erro geral e inesperado ocorreu: {e}")


class Driver_Selenium():
    """Destinada a criação e gerenciamento de drivers do selenium."""

    def __init__(self, ipselenoid, browser='chrome', local=False, timeout='5m', headless=True, options=None):
        self.browser = browser
        self.local = local
        self.timeout = timeout
        self.headless = headless
        self.ipselenoid = ipselenoid
        self.options = options

    def criar_driver(self):
        """
        Cria um driver para Chrome ou Firefox, local ou remoto.

        Args:
            browser (str): O navegador a ser usado ('chrome' ou 'firefox'). Padrão: 'chrome'.
            local (bool): False (padrão) para Selenoid, True para local.
            timeout (str): Timeout de inatividade da sessão no Selenoid.
            headless (bool): True (padrão) para executar em modo headless.

        Returns:
            WebDriver: A instância do driver do Selenium.
        """
        browser = self.browser.lower()
        print(f"Criando driver para '{browser}' em modo {'local' if self.local else 'remoto'}...")
        options = self.options

        if browser == 'chrome':
            browser_name = "chrome"
            if not options:
                options = ChromeOptions()
                options.add_argument("--disable-notifications") #Desabilita notificações como "Aceitar cookies"
                options.add_argument("--no-default-browser-check") #Desabilita a verificação se o chrome é o navegador padrão
                options.add_argument("--disable-infobars") #desabilita a mensagem "Esse chrome está sendo controlado por um testo automatizado"
                options.add_argument("--disable-save-password-bubble") #não salva as senhas
                options.add_argument("--disable-popup-blocking") #desabilita pop-ups (nao influencia em alerts())
                options.add_argument("--disable-extensions") #desabilita extensões
                options.add_argument("--incognito")  # modo anônimo
                options.add_experimental_option("prefs", {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False
                })
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--blink-settings=imagesEnabled=false") # Específico do Chrome
        
        elif browser == 'firefox':
            browser_name = "firefox"
            if not options:
                options = FirefoxOptions()
            if self.headless:
                options.add_argument("-headless")
        
        else:
            raise ValueError(f"Navegador '{browser}' não suportado. Use 'chrome' ou 'firefox'.")

        if self.local:
            if browser == 'chrome':
                driver = webdriver.Chrome(options=options)
            elif browser == 'firefox':
                options.binary_location = r'/usr/bin/firefox'
                driver = webdriver.Firefox(options=options)
        else: # Remoto (Selenoid)
            options.browser_version = "latest"
            options.set_capability("browserName", browser_name)
            options.set_capability(
                "selenoid:options", {
                    "enableVNC": True,
                    "sessionTimeout": self.timeout
                }
            )
            driver = webdriver.Remote(
                command_executor=self.ipselenoid,
                options=options
            )
        
        if self.headless:
            driver.set_window_size(1920, 1080)
        else:
            driver.maximize_window()
        
            
        return driver

    def validar_driver(driver):
        """Verifica se o driver está ativo. Se não, cria um novo e o retorna."""
        if driver:
            try:
                _ = driver.title
                print("Sessão do driver está ativa.")
                return driver 
            except Exception:
                print("Sessão do driver inativa. Recriando...")
                try:
                    driver.quit()
                except Exception:
                    pass

        novo_driver = Driver_Selenium.criar_driver()
        return novo_driver


class Zendesk_Selenium:
    """Destinada à facilitar a automação UI da zendesk junto ao selenium."""
    def __init__(self, driver, usuario, senha, instancia):
        """Chamada inicial para configurar o ambiente.

        Args:
            driver: Driver criado na classe Driver Selenium.
            usuario: Usuario para realizar o login na zendesk.
            senha: Senha para realizar o login na zendesk.
            instancia: Instancia da zendesk para que o login possa ser efetuado corretamente.
        """
        self.driver = driver
        self.usuario = usuario
        self.senha = senha
        self.instancia = instancia


    def login(self):
        """Realiza o login na plataforma zendesk."""
        link = self.instancia
        link = f'https://{link}.zendesk.com/access/normal'
        self.driver.get(link)
        try:
            login_zendesk = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, 'user_email'))
            )
            login_zendesk.send_keys(self.usuario)

            pass_zendesk = self.driver.find_element(By.ID, 'user_password')
            pass_zendesk.send_keys(self.senha)

            entrar_zendesk = self.driver.find_element(By.ID, 'sign-in-submit-button')
            entrar_zendesk.click()
        except:
            pass

        WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="home_icon"]'))
        )


    def play(self, fila:int):
        """Inicia o play automatico de uma visualização da zendesk.

        Args:
            fila (int): Número da visualização da zendesk.
        """
        self.driver.get(self.fila)
        play = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="views_views-header-play-button"]'))
                )
        play.click()
        sleep(5)

    def fechar_dois_pacotes(self):
        """Procura e fecha o MODAL de 2 pacotes dentro do ticket na zendesk.
        
        Returns:
            True quando modal foi encontrado e fechado, False quando o modal não foi encontrado no ticket.
        """
        try:
            dois_pacotes = WebDriverWait(self.driver, 30).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'header.modal-header a.close'))
                        )
            dois_pacotes.click()
            return True
        except:
            return False
        
    def selecionar_dropdown(self, id: int, valor_campo: str):
        """ Seleciona a opção desejada dentro de um campo dropdown na zendesk.

        Args:
            id (int): Identificador único do custom field na zendesk.
            valor_campo (str): Exato valor a ser preenchido nas opções do dropdown.
        """
        seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id}"] [data-garden-id="typography.ellipsis"]'
        campo = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, seletor))
        )
        campo.click()

        menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="ticket-form-field-dropdown-menu"]'))
        )

        opcao = WebDriverWait(menu, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'.//li[.//span[normalize-space()="{valor_campo}"]]'))
        )
        opcao.click()
    
    def obter_valores_input(self, ids:dict):
        """Verifica e retorna os valores preenchidos dentro campos input.

        Args:
            ids (dict): Dicionario com Nome do campo e ID unico do campo input.

        Returns:
            Dicionario com Nome dos campos e valor dentro dele.
        """
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'.custom_field_{id_campo} input[data-test-id="ticket-fields-text-field"]'
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                valor_elemento = elemento.get_attribute("value")
                valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
            
        return valores_campos
        
    def obter_valores_dropdown(self, ids:dict):
        """Realiza a captura de todos os valores dentro de campos dropdown na zendesk.

        Args:
            ids (dict): Dicionario contendo o nome do campo e ID unico do campo dropdown.

        Returns:
            dict: Dicionario contendo o nome do campo e o valor dentro do dropdown que está selecionado.
        """
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id_campo}"] [data-garden-id="typography.ellipsis"]'
                for _ in range(15):
                    elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                    valor_elemento = elemento.text
                    if valor_elemento != '-':
                        valores_campos[nome_campo] = valor_elemento
                        break
                    sleep(1)
                else:
                    valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
        return valores_campos
        
    def preencher_input(self, id:int, valor:str):
        """Preenche com um valor o campo input pre-determinado.

        Args:
            id (int): ID unico do custom field da zendesk.
            valor (str): Valor a ser preenchido no campo.

        Returns:
            None em caso de falha ao não conseguir localizar o elemento.
        """
        seletor = f'.custom_field_{id} input[data-test-id="ticket-fields-text-field"]'
        try:
            campo = self.driver.find_element(By.CSS_SELECTOR, seletor)
            campo.send_keys(valor)

        except NoSuchElementException:
            print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
            return None
        
    def enviar_ticket(self, status:str):
        """Encerra o ticket enviando ele como resolvido, aberto, pendente ou em espera.

        Args:
            status (str): Nome do status que o ticket precisa ser enviado.
        """
        actions = ActionChains(self.driver)
        status_ajustado = status.lower()
        if status_ajustado == 'aberto':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'resolvido':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('s').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'espera' or status_ajustado == 'em espera':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('d').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'pendente':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('p').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
        elif status_ajustado == 'mesmo' or status_ajustado == 'mesmo status':
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('u').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()

    def fechar_ticket_atual(self):
        """Fecha o ticket atual para evitar cacheamento no driver durante as iterações em cada ticket."""
        for i in range(3):
            try:
                fechar_ticket = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="close-button"]'))
                )
                fechar_ticket.click()
                # fechar_aba = WebDriverWait(self.driver,10).until(
                #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="ticket-close-confirm-modal-confirm-btn"]'))
                # )
                # fechar_aba.click()
                print('Ticket fechado.')
                break
            except (StaleElementReferenceException, TimeoutException):
                print(f"Tentando fechar ticket.. Elemento obsoleto... (tentativa {i+1})")
                sleep(2)
    
    def esperar_carregamento(self):
        """Ao enviar o ticket como aberto ou outro status, é necessario aguardar o carregamento do ticket para fecha-lo."""
        try:
            seletor_de_carregamento = (By.CSS_SELECTOR, "section.main_panes.ticket.working")
            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(seletor_de_carregamento)
            )
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.invisibility_of_element_located(seletor_de_carregamento)
            )
            sleep(2)

        except TimeoutException:
            print("Nenhum círculo de carregamento detectado, continuando...")
            pass
    
    def enviar_mensagem(self, mensagem: str, publica=False):
        """Envia mensagem dentro do ticket como obs. interna ou pública.

        Args:
            mensagem (str): Mensagem a ser enviada no ticket.
            publica (bool, optional): True para enviar mensagem ao cliente, False para adicionar observação interna, o padrão é False.
        """
        try:
            actions = ActionChains(self.driver)
            if publica:
                actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('c').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
                try:
                    sleep(2)
                    ok = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']")))
                    ok.click()
                except:
                    ...
            else:
                actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('x').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()
                
            caixa_texto = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="omnicomposer-rich-text-ckeditor"]'))
            )
            caixa_texto.send_keys(mensagem)

        except Exception as e:
            print(e)

    def status_ticket(self):
        """Método para obter o status atual do ticket."""
        try:
            status_locator = (By.CSS_SELECTOR, '[data-test-id="tabs-section-nav-item-ticket"] .ticket_status_label')
            status_element = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located(status_locator)
            )
            status_text = status_element.text
            return status_text
        except:
            print('Erro ao obter o status do ticket.')
            return 'Resolvido'

    def aplicar_macro(self, macro:str):
        """Aplica uma macro no ticket.

        Args:
            macro (str): Caminho da macro que consta no zendesk (ATENÇÃO: Necessario ser exatamente caminho da macro com :: e NÃO o nome dela )
        """
        try:
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('m').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()

            input_macro = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='ticket-footer-macro-menu-autocomplete-input'] input"))
            )
            input_macro.send_keys(macro)
            sleep(4)
            actions.send_keys(Keys.ENTER).perform()
        except Exception as e:
            print(e)



class Zendesk_Zenpy:
    """Destinada a facilitar as automações via zenpy na zendesk."""
    def __init__(self, zlogin, zpass, instancia):
        self.zlogin = zlogin
        self.zpass = zpass
        self.instancia = instancia
        self.zenpy_client = None
        self.auth_zenpy()


    def auth_zenpy(self):
        """Realiza a autenticação na API."""
        creds = {
            'email': self.zlogin,
            'token': self.zpass,
            'subdomain': self.instancia
        }
        try:
            print("Autenticando cliente Zenpy...")
            self.zenpy_client = Zenpy(session=session, **creds)
            print("Cliente Zenpy autenticado com sucesso.")
        except Exception as e:
            print(f"Erro na autenticação do Zenpy: {e}")

    def _zenpy_client(self):
        return self.zenpy_client
            
    def pegar_tickets(self, fila:int, minimo=1, invertido=False):
        """Captura todos os tickets dentro de uma visualização na zendesk.

        Args:
            fila (int): ID da visualização.
            minimo (int, optional): Minimo de casos que a visualização precisa para retornar. Padrão setado em 1.
            invertido (bool, optional): False para retornar os pedidos em ordem crescente, True para retornar os pedidos em ordem decrescente. Padrão setado em False.

        Returns:
            None em casos de erros ou quantidade minima não atingida. Lista com todos os tickets para caso de sucesso.
        """
        print('Verificando tickets na fila...')
        
        if not self.zenpy_client:
            print("Erro: Cliente Zenpy não foi autenticado. Verifique as credenciais.")
            return None
        
        todos_os_tickets = []
        try:
            for ticket in self.zenpy_client.views.tickets(view=fila):
                todos_os_tickets.append(ticket.id)
            if len(todos_os_tickets) >= minimo:
                print(f'A visualização conta com {len(todos_os_tickets)} tickets.')
                todos_os_tickets = sorted(todos_os_tickets, reverse=invertido)
                return todos_os_tickets
            else:
                print(f'A visualização não tem o minimo de tickets para inicializar. (Minimo: {minimo} Fila: {len(todos_os_tickets)})')
                return None
        except Exception as e:
            print(f"Erro ao buscar tickets: {str(e)}")
            return None
        
    def _valores_customfield(self, ticket: Any) -> Dict[int, Any]:
        
        if not hasattr(ticket, 'custom_fields') or not ticket.custom_fields:
            return {}

        field_objects: Iterable[Any]
        if hasattr(ticket.custom_fields, 'values'):
            field_objects = ticket.custom_fields.values()
        else:
            field_objects = ticket.custom_fields

        parsed_fields = {}
        for field in field_objects:
            field_id = None
            field_value = None

            if isinstance(field, dict):
                field_id = field.get('id')
                field_value = field.get('value')
            elif hasattr(field, 'id') and hasattr(field, 'value'):
                field_id = field.id
                field_value = field.value
            
            if field_id is not None:
                parsed_fields[field_id] = field_value
        
        return parsed_fields
    
    def extrair_customfields(self, ticket_id:int, lista_campos: Dict[str, int]) -> Optional[Dict[str, Any]]:
        try:
            ticket = self.zenpy_client.tickets(id=ticket_id)

            todos_os_valores = self._valores_customfield(ticket)

            resultado = {}
            for nome, id_campo in lista_campos.items():
                valor = todos_os_valores.get(id_campo)
                resultado[nome] = valor

            return resultado
        except APIException as e:
            print(f"Erro de API ao buscar ticket {ticket_id}: {e}")
            return None
        except Exception:
            print(f"Erro inesperado ao processar ticket {ticket_id}:")
            traceback.print_exc()
            return None

#=============================================================================


class BotsLogger:
    def __init__(self, heartbeat_instancia: Heartbeat):
        if not isinstance(heartbeat_instancia, Heartbeat):
            raise TypeError("A BotsLogger precisa receber uma instância da classe Heartbeat.")
        self.heartbeat = heartbeat_instancia
        self.bot_id = self.heartbeat.bot_id

    def error(self,
              error: Exception, 
              message: str, 
              ticket_id : str,
              error_type: str = 'WARNING'):
        """
        Log de erros, classificando-os e decidindo ações.
        error_type pode ser: 'WARNING', 'CRITICAL', 'API_RETURN'
        """
        error_class = error.__class__.__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()

        details = {
            "ticket_id": ticket_id,
            "error_type": error_type.upper(),
            "error_class": error_class,
            "error_message": error_message,
            "stack_trace": stack_trace
        }

        # Lógica de classificação e ação (evolução do seu BotError)
        level, action = self._classify_error(error, error_type, message)
        
        self._log(level, message, details)
        
        return action
        

    def _log(self, level: str, message: str, context: dict):
        """Método base para criar a estrutura do log."""
        SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")
        timestamp_sp = datetime.datetime.now(datetime.UTC).astimezone(SAO_PAULO_TZ)

        log_entry = {
            "level": level.upper(),
            "message": message,
            "timestamp": timestamp_sp.isoformat(),
            "service": self.bot_id,
            "context": context
        }
        # Converte para string JSON e loga
        logging.log(logging.getLevelName(level.upper()), json.dumps(log_entry, default=str))

        self._envia_alerta(log_entry)

    def _envia_alerta(self, log):
        """Metodo base para enviar alertas"""
        level = log.get('level')
        if level == 'CRITICAL':
            self.heartbeat.alertas(status=manutencao, warning=log)
        else:
            self.heartbeat.alertas(warning=log)

    def _classify_error(self, error: Exception, error_type: str, context: str):
        """Classifica o erro e retorna (level, action)."""
        error_message_lower = str(error).lower()

        # Erros Críticos (requerem intervenção imediata)
        if "invalid credentials" in error_message_lower or "acesso revogado" in error_message_lower:
            return "CRITICAL", "stop"

        # Erros de API que podem ser tentados novamente
        if isinstance(error, requests.exceptions.Timeout) or isinstance(error, requests.exceptions.ConnectionError):
            return "WARNING", "retry"
        
        if isinstance(error, requests.exceptions.HTTPError):
            status_code = error.response.status_code
            if 500 <= status_code < 600:
                # Erro no servidor (500, 502, 503...). Pode ser temporário.
                return "WARNING", "retry" 
            elif 400 <= status_code < 500:
                # Erro do cliente (401, 403, 404...). Erro nosso, não adianta tentar de novo.
                return "CRITICAL", "stop"

        # Erros do Selenium, provavelmente mudança na estrutrua do site.
        if isinstance(error, (WebDriverException, NoSuchElementException, StaleElementReferenceException, TimeoutException)):
            return "CRITICAL", "stop"

        if isinstance(error, (ConnectionError, Timeout)):
            return "WARNING", "retry"

        # Erros de Estrutura (problema de código, provavelmente não recuperável)
        if isinstance(error, (KeyError, TypeError, AttributeError, NameError)):
            return "CRITICAL", "stop"


        # Erros Funcionais (default)
        return "WARNING", "retry"

