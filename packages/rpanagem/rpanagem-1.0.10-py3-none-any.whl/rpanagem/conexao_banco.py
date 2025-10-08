import pyodbc

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="conexao_banco.log", logger=logger)


class ODBC():
    """Classe para conexõe com bancos de dados e execuções de qurerys"""

    def __init__(self):
        pass

    def conectar_odbc(self, driver, system, usuario, senha, database):
        """
        Cria uma conexão ODBC com um banco de dados.

        :param driver: Nome do driver ODBC instalado (ex: 'ODBC Driver 17 for SQL Server')
        :type driver: str
        :param system: Nome ou IP do servidor do banco de dados
        :type system: str
        :param usuario: Nome do usuário
        :type usuario: str
        :param senha: Senha do usuário
        :type senha: str
        :param database: Nome do banco de dados
        :type database: str

        :returns: Objeto de conexão pyodbc
        :rtype: pyodbc.Connection
        """
        try:
            conexao = pyodbc.connect(f"Driver={driver};"
                                    f"System={system};"
                                    "Uid=" + f'{usuario}' +
                                    ";Pwd=" + f'{senha}' +
                                    f";DefaultLibraries={database}")

            # print("✅ Conexão ODBC bem-sucedida!")
            module_logger.info("✅ Conexão ODBC bem-sucedida!")
            return conexao
        except pyodbc.Error as e:
            # print("❌ Erro ao conectar ao banco:", e)
            module_logger.error(f"❌ Erro ao conectar ao banco: {e}")
            module_logger.error("❌ Verifique a conexão com a rede/VPN")
            raise pyodbc.Error(f"❌ Erro ao conectar ao odbc: {e}")

    def executar_select(self, conexao, query):
        """
        Executa uma query SQL usando uma conexão ODBC e retorna os resultados como uma lista de dicionários.

        :param conexao: Objeto de conexao
        :type conexao: pyodbc.Connection
        :param query: Query SQL
        :type query: str

        :returns: Lista de dicionários (cada dicionário representa uma linha com os nomes das colunas como chaves)
        :rtype: list
        """
        try:
            cursor = conexao.cursor()
            cursor.execute(query)

            # Pega os nomes das colunas
            colunas = [desc[0] for desc in cursor.description]

            # Constrói lista de dicionários
            resultados = [dict(zip(colunas, linha)) for linha in cursor.fetchall()]

            for registro in resultados:
                for chave, valor in registro.items():
                    if valor is None:
                        registro[chave] = ""

            module_logger.info("✅ SELECT executado com sucesso.")

            return resultados

        except Exception as e:
            # print(f"❌ Erro ao executar a query: {e}")
            module_logger.error(f"❌ Erro ao executar a query SELECT: {e}")
            raise pyodbc.Error(f"❌ Erro ao executar a query SELECT: {e}")

    def conectar_sqlserver(self, driver, server, database, usuario, senha):
        """
        Função para conectar a um banco SQL Server.

        :param driver: Nome do driver ODBC instalado (ex: 'ODBC Driver 17 for SQL Server')
        :type driver: str
        :param server: endereço do servidor
        :type server: str
        :param database: nome do banco de dados
        :type database: str
        :param usuario: usuário do banco
        :type usuario: str
        :param senha: senha do banco
        :type senha: str

        :returns: Objeto de conexão pyodbc
        :rtype: pyodbc.Connection
        """
        try:
            conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={usuario};PWD={senha}'
            conexao = pyodbc.connect(conn_str)
            # print("✅ Conexão SQL Server bem-sucedida!")
            module_logger.info("✅ Conexão SQL Server bem-sucedida!")

            return conexao
        except pyodbc.Error as e:
            # print("❌ Erro ao conectar ao banco:", e)
            module_logger.error(f"❌ Erro ao conectar ao banco: {e}")
            module_logger.error("❌ Verifique a conexão com a rede/VPN")
            raise pyodbc.Error(f"❌ Erro ao conectar sqlserver: {e}")

    def executar_update_insert_delete(self, conexao, query):
        """
        Executa uma query de UPDATE, INSERT ou DELETE e faz um commit usando uma conexão pyodbc.

        :param conexao: objeto de conexão pyodbc já aberto.
        :type conexao: pyodbc.Connection
        :param query: Instrução SQL de UPDATE ou INSERT.
        :type query: str

        :returns: Objeto de conexão pyodbc
        :rtype: pyodbc.Connection
        """

        if 'UPDATE' in query or 'update' in query or 'Update' in query:
            acao_executada = 'UPDATE'
        elif 'INSERT' in query or 'insert' in query or 'Insert' in query:
            acao_executada = 'INSERT'
        elif 'DELETE' in query or 'delete' in query or 'Delete' in query:
            acao_executada = 'DELETE'
            
        try:
            cursor = conexao.cursor()
            cursor.execute(query)
            conexao.commit()

            module_logger.info(f"✅ {acao_executada} executado com sucesso.")

            return True
        except pyodbc.Error as e:
            # print("❌ Erro ao executar o UPDATE:", e)
            module_logger.error(f"❌ Erro ao executar {acao_executada}: {e}")
            conexao.rollback()
            raise pyodbc.Error(f"❌ Erro ao executar {acao_executada}: {e}")
        finally:
            cursor.close()

    def atualizar_monitoramento(self, conexao, id_robo):
        """
        Atualiza o campo DATULTPRE da tabela de monitoramento com a data do ultimo processamento.

        :param conexao: objeto de conexão pyodbc já aberto.
        :type conexao: pyodbc.Connection
        :param id_robo: ID do robo na tabela NAGINTEGRA.NGMOND00
        :type id_robo: int
        """
        module_logger.info("Atualizando monitoramento...")
        query = f"""
                    SELECT *
                    FROM NAGINTEGRA.NGMOND00
                    WHERE 1=1
                    AND NOMSEV LIKE 'RPA%'
                    AND NUMSQC = {id_robo}
                """

        resultado_select = self.executar_select(conexao, query)

        if resultado_select:
            query_update = f"""
                            UPDATE NAGINTEGRA.NGMOND00 SET DATULTPRE = CURRENT_TIMESTAMP 
                            WHERE 1=1
                            AND NUMSQC = {id_robo}
                            """

            self.executar_update_insert_delete(conexao, query_update)

            module_logger.info("✅ TABELA DE MONITORAMENTO ATUALIZADA COM SUCESSO")

        else:
            module_logger.info(f"⚠️ Registro do robô com id {id_robo} não encontrado na tabela de monitoramento")
            module_logger.info("⚠️ Campo DATULTPRE não atualizado")
            module_logger.info("⚠️ Verifique se a conexão esta em produção")
