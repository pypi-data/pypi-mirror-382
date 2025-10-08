import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="enviar_email.log", logger=logger)


class ConetarSMTP():
    """realiza conexões smtp para enviou de email"""

    def __init__(self):
        pass

    def conectar_smtp_server(
            self,
            host,
            porta,
            usuario=None,
            senha=None,
            usar_ssl=False
    ):
        """
        Estabelece uma conexão com um servidor SMTP com ou sem SSL e, opcionalmente, realiza autenticação.

        :param host: Endereço do servidor SMTP.
        :type host: str
        :param porta: Porta do servidor SMTP
        :type porta: int
        :param usuario: (Opcional): Nome de usuário para autenticação SMTP.
        :type usuario: str
        :param senha: (Opcional): Senha correspondente ao usuário.
        :type senha: str
        :param usar_ssl: Define se a conexão deve ser feita via SSL.
        :type usar_ssl: bool

        :returns: Objeto de conexão SMTP pronto para uso, ou None em caso de erro.
        :rtype usar_ssl: smtplib.SMTP or smtplib.SMTP_SSL
        """
        try:
            if usar_ssl:
                conexao = smtplib.SMTP_SSL(host, porta)
            else:
                conexao = smtplib.SMTP(host, porta)
                conexao.ehlo()

            if usuario and senha:
                conexao.login(usuario, senha)

            # print("✅ Conexão com o servidor SMTP realizada com sucesso.")
            module_logger.info("✅ Conexão com o servidor SMTP realizada com sucesso.")

            return conexao
        except Exception as e:
            # print(f"❌ Erro ao conectar ao servidor SMTP: {e}")
            module_logger.error(f"❌ Erro ao conectar ao servidor SMTP: {e}")
            module_logger.error("❌ Verifique a conexão com a rede/VPN")

            return None

    def enviar_email(
            self,
            conexao,
            remetente="automation@nagem.com.br",
            destinatario="",
            cc=None,
            assunto="RPA",
            corpo="",
            corpo_html=False,
            dados_html={
                "MensagemEmail": "",
                },
            anexos=None
    ):
        """
        Envia um e-mail utilizando uma conexão SMTP existente, com suporte a corpo de texto e anexos.

        :param conexao: Objeto de conexão SMTP previamente estabelecido.
        :type conexao: smtplib.SMTP or smtplib.SMTP_SSL
        :param remetente: Endereço de e-mail do remetente.
        :type remetente: str
        :param destinatario: Endereço(s) de e-mail dos destinatários.
        :type destinatario: str ou list
        :param assunto: Assunto do e-mail.
        :type assunto: str
        :param corpo: Corpo do e-mail no formato texto simples ou um caminho para o arquivo .html
        :type corpo: str
        :param corpo_html: Define se o parametro corpo é um caminho para um arquivo .html.
        :type corpo_html: bool
        :param dados_html: Dicionário com os valores da chaves para serem substituidas no html.
        :type dados_html: str
        :param anexos: (Opcional) Caminho(s) para os arquivos a serem anexados ao e-mail.
        :type anexos: str ou list

        :returns: True se o e-mail for enviado com sucesso, False em caso de erro.
        :rtype usar_ssl: bool
        """
        try:
            if conexao is None:
                module_logger.warning("❌ Objeto de conexão SMTP é None. Verifique a conexão antes de enviar o e-mail.")
                raise ValueError("Objeto de conexão SMTP é None. Verifique a conexão antes de enviar o e-mail.")

            # Formatar destinatários
            if isinstance(destinatario, str):
                destinatario = [email.strip() for email in destinatario.split(",")]

            if cc:
                if isinstance(cc, str):
                    cc = [email.strip() for email in cc.split(",")]
            else:
                cc = []

            # Criar a mensagem
            mensagem = MIMEMultipart()
            mensagem["From"] = remetente
            mensagem["To"] = ", ".join(destinatario)
            if cc:
                mensagem["Cc"] = ", ".join(cc)
            mensagem["Subject"] = assunto

            # Anexar corpo em texto e/ou HTML
            if corpo_html:
                subtype = "html"

                # Lê o HTML do arquivo
                with open(corpo, "r", encoding="utf-8") as arquivo_html:
                    corpo = arquivo_html.read()

                # Dicionário com os dados para substituir os placeholders
                dados_html['DataEmail'] = datetime.now().strftime("%d/%m/%Y")

                # Substitui os placeholders no HTML
                for chave, valor in dados_html.items():
                    # substitui {{chave}} por valor
                    corpo = corpo.replace(f"{{{{{chave}}}}}", str(valor))
            else:
                subtype = "plain"

            mensagem.attach(MIMEText(corpo, subtype))

            # Adicionar anexos
            if anexos:
                if isinstance(anexos, str):
                    anexos = [anexos]  # Converte para lista se for string

                for caminho in anexos:
                    if not os.path.isfile(caminho):
                        # print(f"📣 Arquivo não encontrado: {caminho}")
                        module_logger.warning(f"📣 Arquivo não encontrado: {caminho}")
                        continue

                    try:
                        with open(caminho, "rb") as f:
                            parte = MIMEBase("application", "octet-stream")
                            parte.set_payload(f.read())
                            encoders.encode_base64(parte)
                            parte.add_header(
                                "Content-Disposition",
                                f'attachment; filename="{os.path.basename(caminho)}"'
                            )
                            mensagem.attach(parte)
                    except Exception as e:
                        module_logger.error(f"❌ Erro ao anexar arquivo {caminho}: {e}")
                        continue

            # Enviar e-mail
            todos_destinatarios = destinatario + cc
            conexao.sendmail(remetente, todos_destinatarios, mensagem.as_string())
            # conexao.quit()

            # print("✅ E-mail enviado com sucesso.")
            module_logger.info("✅ E-mail enviado com sucesso.")
            return True

        except Exception as e:
            # print(f"❌ Erro ao enviar o e-mail: {e}")
            module_logger.error(f"❌ Erro ao enviar o e-mail: {e}")
            return False
        finally:
            try:
                conexao.quit()
            except Exception:
                pass
