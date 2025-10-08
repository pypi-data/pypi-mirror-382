import win32com.client
import win32gui
import win32con
import win32process
import win32api
import ctypes
import time
import os
import subprocess
import psutil
import re

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="manipula_sap.log", logger=logger)


class SAP():
    """Faz conexões com o sistema SAP e minupula suas telas"""

    def __init__(self):
        pass

    def start_sap_logon(self, sap_path, sap_system, username, password, language):
        """
        Conectar e realiza login no SAP GUI Scripting (Automação Desktop).

        :param sap_path: Caminho onde esta instalado o executaval do sistema.
        :type sap_path: str
        :param sap_system: Opção de login no sistema (produção ou teste).
        :type sap_system: str
        :param username: Nome do usuário SAP.
        :type username: str
        :param password: Senha do usuário SAP.
        :type password: str
        :param language: Idioma do sistema.
        :type language: str

        :returns: se a conexão e o login for bem sucedido retorna a sessão no SAP que foi conectada.
        :rtype: str
        """
        if not os.path.exists(sap_path):
            module_logger.warning(f"❌ SAP Logon não encontrado em: {sap_path}")
            raise FileNotFoundError(f"❌ SAP Logon não encontrado em: {sap_path}")

        try:
            subprocess.Popen(sap_path)
            # print("SAP Logon iniciado...")
            module_logger.info("SAP Logon iniciado...")
            time.sleep(5)

            # Conectar ao SAP GUI
            SapGuiAuto = win32com.client.GetObject("SAPGUI")

            if not SapGuiAuto:
                module_logger.warning("ℹ️ SAP GUI não está rodando.")
                raise Exception("ℹ️ SAP GUI não está rodando.")

            application = SapGuiAuto.GetScriptingEngine
            connection = application.OpenConnection(sap_system, True)
            self.session = connection.Children(0)

            # print("✅ SAP Logon conectado.")
            module_logger.info("✅ SAP Logon conectado.")
        except Exception as e:
            # print("Erro ao conectar no SAP:", e)
            module_logger.error(f"❌ Erro ao conectar no SAP: {e}")
            self.fechar_sessao_sap(self.session)
            raise Exception(f"❌ Erro ao conectar no SAP: {e}")

        try:

            # print("Iniciando login no SAP...")
            module_logger.info("Iniciando login no SAP...")

            self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = username
            self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
            self.session.findById("wnd[0]/usr/txtRSYST-LANGU").text = language
            self.session.findById("wnd[0]").sendVKey(0)
            # session.findById("wnd[0]/tbar[0]/btn[0]").press()  # Enter

            time.sleep(2)
            if "O nome ou a senha não está correto" in self.verificar_mensagem_status(self.session).lower():
                return None

            # Verificar se apareceu a janela de "logon múltiplo"
            if self.session.Children.Count > 1:
                for i in range(self.session.Children.Count):
                    wnd = self.session.Children(i)
                    if "logon múltiplo" in wnd.Text.lower():
                        module_logger.info("⚠️ Logon múltiplo detectado — login não realizado.")
                        self.fechar_sessao_sap(self.session)
                        return None

            # Verificar se o menu principal foi carregado (transação inicial)
            if not self.session.findById("wnd[0]/tbar[0]/okcd", False):
                # print("❌ Login não chegou à tela principal do SAP.")
                module_logger.info("❌ Login não chegou à tela principal do SAP.")
                return None
        
            # print("✅ Login realizado.")
            module_logger.info("✅ Login realizado.")

            return self.session
        except Exception as e:
            # print("Erro ao realizar o login no SAP:", e)
            module_logger.error(f"❌ Erro ao realizar o login no SAP: {e}")
            self.fechar_sessao_sap(self.session)
            raise Exception(f"❌ Erro ao realizar o login no SAP: {e}")

    def procurar_campos(self, session_sap, campos_ids=None):
        """
        Verifica se algum dos campos existem na sessao do sap.

        :param campos_ids: Lista de IDs de campos únicos na tela (ex: ["wnd[0]/usr/ctxtLFA1-STCD1"]).
        :type campos_ids: list

        :returns: True se a janela estiver aberta, False caso contrário.
        :rtype: bool
        """
        try:
            algum_campo_encontrado = False
            if campos_ids:
                for campo_id in campos_ids:
                    try:
                        session_sap.findById(campo_id)
                        algum_campo_encontrado = True
                        return algum_campo_encontrado
                    except:
                        continue
                return algum_campo_encontrado

        except Exception as e:
            # print(f"❌ Erro ao verificar os campos: {e}")
            module_logger.error(f"❌ Erro ao verificar os campos: {e}")
            raise Exception(f"❌ Erro ao verificar os campos: {e}")

        # Exemplo: Verificar pela existência de campos (ex: CNPJ ou IE)
        # campos_fiscais = [
        #     "wnd[0]/usr/ctxtLFA1-STCD1",  # CNPJ/CPF
        #     "wnd[0]/usr/ctxtLFA1-STCD2",  # Inscrição Estadual
        # ]

        # procurar_campos(session, campos_ids=campos_fiscais):

    def procurar_janela(self, session_sap, titulo_procurado, usar_regex=False):
        """
        Verifica se existe alguma janela ativa no SAP tem o título informado.
        Ou Verifica se algum dos campos únicos existe.

        :param session_sap: Sessão SAP ativa
        :type session_sap: win32com session
        :param titulo_procurado: Título da janela ou padrão regex. (ex: "Domicílio Fiscal").
        :type titulo_procurado: str
        :param usar_regex : Se True, trata titulo_procurado como expressão regular.
        :type usar_regex : bool

        :returns: True se a janela estiver ativa, False caso contrário.
        :rtype: bool
        """
        try:
            idx = 0
            while True:
                janela_id = f"wnd[{idx}]"
                try:
                    janela = session_sap.findById(janela_id)
                    titulo = janela.Text.strip()

                    if usar_regex:
                        if re.search(titulo_procurado, titulo, re.IGNORECASE):
                            module_logger.info(f'✅ Janela com regex encontrada: {titulo}')
                            return True
                    else:
                        if titulo_procurado.lower() in titulo.lower():
                            module_logger.info(f'✅ Janela encontrada: {titulo}')
                            return True

                    idx += 1
                except:
                    break  # Não há mais janelas
            return False
        except Exception as e:
            module_logger.error(f"❌ Erro ao verificar janelas SAP: {e}")
            # print(f"❌ Erro ao verificar janelas SAP: {e}")
            return False

    def verificar_mensagem_status(self, session_sap):
        """
        Verifica a última mensagem de status exibida no SAP GUI.

        :param session_sap: objeto Session (SAP GUI) já conectado.
        :type session_sap: win32com.client

        :returns: Mensagem de status atual
        :rtype: str
        """
        try:
            barra_status = session_sap.findById("wnd[0]/sbar")
            if barra_status:
                mensagem = barra_status.Text.strip()

                if mensagem:
                    # print(f"📣 Mensagem SAP: {mensagem}")
                    module_logger.info(f"📣 Mensagem SAP: {mensagem}")

                return mensagem
            else:
                module_logger.info(f"⚠️ Nenhuma mensagem SAP obtida.")
        except Exception as e:
            module_logger.error(f"❌ Erro ao acessar a barra de status: {e}")
            raise Exception(f"❌ Erro ao acessar a barra de status: {e}")

    def fechar_sessao_sap(self, session_sap):
        """
        Fecha uma sessão SAP aberta via SAP GUI Scripting.

        :param session_sap: Objeto da sessão SAP (Session)
        :type session_sap: win32com.client

        Exemplo de obtenção do objeto:
            sap_gui = win32com.client.GetObject("SAPGUI")
            app = sap_gui.GetScriptingEngine
            connection = app.Children(0)
            session = connection.Children(0)
        """
        try:
            if session_sap and session_sap.Info.IsLowSpeedConnection is False:
                # print("🔒 Fechando sessão SAP...")
                module_logger.info("🔒 Fechando sessão SAP...")

                session_sap.EndTransaction()
                session_sap = None  # limpa referência
                # print("✅ Sessão SAP encerrada com sucesso.")
                module_logger.info("✅ Sessão SAP encerrada com sucesso.")
            else:
                # print("⚠️ Sessão SAP inválida ou já encerrada.")
                module_logger.warning("⚠️ Sessão SAP inválida ou já encerrada.")
                return False
        except Exception as e:
            module_logger.error(f"❌ Erro ao fechar a sessão SAP: {e}")
            raise Exception(f"❌ Erro ao fechar a sessão SAP: {e}")


        try:
            # print("🧹 Encerrando processo saplogon.exe...")
            module_logger.info("🧹 Encerrando processo saplogon.exe...")

            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == 'saplogon.exe':
                    proc.terminate()
                    proc.wait(timeout=5)
                    # print("✅ Processo SAP GUI finalizado.")
                    module_logger.info("✅ Processo SAP GUI finalizado.")
                    break
            else:
                # print("ℹ️ Processo saplogon.exe não encontrado.")
                module_logger.warning("ℹ️ Processo saplogon.exe não encontrado.")
                return False
        except Exception as e:
            # print(f"❌ Erro ao encerrar o processo SAP GUI: {e}")
            module_logger.error(f"❌ Erro ao encerrar o processo SAP GUI: {e}")
            raise Exception(f"❌ Erro ao encerrar o processo SAP GUI: {e}")

        return True

    def run_transaction(self, session_sap, transacao):
        """
        Acessa uma transação SAP via SAP GUI Scripting.

        :param session_sap: Objeto de conexão SAP
        :type session_sap: win32com.client
        :param transacao: Código da transação
        :type transacao: str

        """
        try:
            # Entra com a transação
            session_sap.findById("wnd[0]/tbar[0]/okcd").text = f"/n{transacao}"
            # session_sap.findById("wnd[0]/tbar[0]/btn[0]").press()
            session_sap.findById("wnd[0]").sendVKey(0)

            # Espera um pouco para a transação carregar (opcional)
            time.sleep(1)

            # print(f"Transação {transacao} acessada com sucesso.")
            module_logger.info(f"✅ Transação {transacao} acessada com sucesso.")

        except Exception as e:
            # print(f"Erro ao executar a transação {transacao}: {e}")
            module_logger.error(f"❌ Erro ao executar a transação {transacao}: {e}")
            raise Exception(f"❌ Erro ao executar a transação {transacao}: {e}")

    def anexar_sessao_sap(self, session_sap, wnd=0):
        """
        Recebe uma sessão SAP GUI, foca e traz a janela correspondente para o primeiro plano.

        :param session_sap: Objeto de conexão SAP
        :type session_sap: win32com.client
        """
        try:
            janela_id = f"wnd[{wnd}]"

            # Obtém o título da janela SAP atual
            titulo_janela = session_sap.findById(janela_id).Text
            module_logger.info(f"Janela encontrada {titulo_janela}.")

            # Procura a janela com esse título
            hwnd = win32gui.FindWindow(None, titulo_janela)

            if not hwnd or hwnd == 0:
                module_logger.info("Janela SAP não encontrada.")
                raise Exception("Janela SAP não encontrada.")

            # Traz a janela para o primeiro plano
            # win32gui.ShowWindow(hwnd, 5)
            # win32gui.SetForegroundWindow(hwnd)

            # Se estiver minimizada, restaura
            # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

            # Força o foco (workaround para SetForegroundWindow falhar em alguns casos)
            foreground_thread_id = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
            target_thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]

            # Anexa os threads de entrada
            if foreground_thread_id != target_thread_id:
                ctypes.windll.user32.AttachThreadInput(foreground_thread_id, target_thread_id, True)

            # Traz para frente
            win32gui.SetForegroundWindow(hwnd)

            # foca
            try:
                win32gui.SetFocus(hwnd)
            except Exception as focus_error:
                # print("⚠️ SetFocus falhou, tentando fallback...")
                module_logger.warning("⚠️ SetFocus falhou, tentando fallback...")
                win32gui.BringWindowToTop(hwnd)

            # Desanexa os threads após o foco
            if foreground_thread_id != target_thread_id:
                ctypes.windll.user32.AttachThreadInput(foreground_thread_id, target_thread_id, False)

            # print("✅ Janela SAP trazida para frente com foco.")
            module_logger.info("✅ Janela SAP trazida para frente com foco.")

        except Exception as e:
            # print(f"❌ Erro ao tentar focar a janela SAP: {e}")
            module_logger.info(f"❌ Erro ao tentar focar a janela SAP: {e}")
