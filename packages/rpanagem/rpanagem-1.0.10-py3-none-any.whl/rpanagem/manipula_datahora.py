from datetime import datetime, timedelta, date

from rpanagem import manipula_diretorios_arquivos
import logging
logger = logging.getLogger(__name__)
log = manipula_diretorios_arquivos.Arquivos()
module_logger = log.criar_logger_diario("./log", nome_arquivo_log="manipula_datahora.log", logger=logger)


# Mapeamento fixo (sem depender do sistema)
DIAS_PT = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo"
]


class DataHora():
    """Manupila datas."""

    def __init__(self):
        pass

    def obter_incluir_valor_data(self, dias_para_subtrair=0, dias_para_adicionar=0, formato="%Y-%m-%d", datahora=False):
        """
        Retorna a data atual ajustada com base nos dias a subtrair e adicionar.

        Pode ser formatada conforme especificado.

        Caso nenhum parametro seja passado o retorno será a data atual no formato americano.

        :param dias_para_subtrair: Número de dias a subtrair da data atual.
        :type dias_para_subtrair: int
        :param dias_para_adicionar: Número de dias a adicionar à data resultante.
        :type dias_para_adicionar: int
        :param formato: Formato da data de retorno apenas para retorno str (ex: "%d/%m/%Y" ou "%Y-%m-%d").
        :type formato: str
        :param datahora: True para ser retornado data e hora no formato datetime.datetime, False retorna apenas a data no formato str (Padrão: False)
        :type datahora: bool

        :returns: A nova data ajustada no formato especificado caso o retorno seja str.
        :rtype: str
        """
        if datahora is True:
            data_atual = datetime.today()
            nova_data = data_atual - timedelta(days=dias_para_subtrair) + timedelta(days=dias_para_adicionar)
        elif datahora is False:
            data_atual = datetime.today().date()
            nova_data = (data_atual - timedelta(days=dias_para_subtrair) + timedelta(days=dias_para_adicionar)).strftime(formato)
        else:
            raise ValueError("❌ Paramentro datahora inválido. Use: True ou False.")

        return nova_data

    def converter_data(self, data=None, tipo_desejado="datetime", formato_str="%Y-%m-%d"):
        """
        Converte uma data recebida para o tipo especificado.

        :param data: A data de entrada.
        :type data: str, datetime, date ou timestamp
        :param tipo_desejado: Tipo de saída desejado. Pode ser:
            - "datetime"    2025-06-05 00:00:00
            - "date"    2025-06-05
            - "str" 2025-06-05
            - "timestamp"   1749092400
        :type tipo_desejado: str
        :param formato_str: formato que deseja ser retornado (Obrigatorio apenas se tipo_desejado for str).
        :type formato_str: str

        Retorna:
        - A data convertida no tipo especificado.
        """
        if not data:  # Trata None, '', 0
            if tipo_desejado == "str":
                return ""
            return None

        # Normaliza para datetime primeiro
        if isinstance(data, str):
            formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y%m%d", "%d%m%Y", "%d%m%Y", "%Y%m%d"]
            for fmt in formatos:
                try:
                    data = datetime.strptime(data, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Formato de data inválido: {data}")

        elif isinstance(data, date) and not isinstance(data, datetime):
            data = datetime.combine(data, datetime.min.time())
        elif isinstance(data, (int, float)):
            data = datetime.fromtimestamp(data)

        # Converte para o tipo desejado
        if tipo_desejado == "datetime":
            return data
        elif tipo_desejado == "date":
            return data.date()
        elif tipo_desejado == "str":
            return data.strftime(formato_str)
        elif tipo_desejado == "timestamp":
            return int(data.timestamp())
        else:
            raise ValueError("❌ Tipo desejado inválido. Use: 'datetime', 'date', 'str', 'timestamp'.")

    def data_hora_para_binario(self, data_hora: datetime) -> str:
        """
        Converte uma data e hora para uma string binária.

        :param data_hora: Data hora para ser convertida.
        :type data_hora: datetime

        :returns: String binária representando cada parte da data e hora.
        :rtype: str
        """
        # Converter cada parte para binário com preenchimento para garantir o número de bits
        bin_ano = format(data_hora.year, '016b') # 16 bits
        bin_mes = format(data_hora.month, '04b') # 4 bits
        bin_dia = format(data_hora.day, '05b') # 5 bits
        bin_hora = format(data_hora.hour, '05b') # 5 bits
        bin_minuto = format(data_hora.minute, '06b') # 6 bits
        bin_segundo = format(data_hora.second, '06b') # 6 bits

        # Juntar tudo
        binario_completo = f"{bin_ano}{bin_mes}{bin_dia}{bin_hora}{bin_minuto}{bin_segundo}"
        return binario_completo

    def binario_para_data_hora(self, binario: str) -> datetime:
        """
        Converte uma string binária de volta para um objeto datetime.

        :param data_hora: Espera uma string de 42 bits no seguinte formato:
        [16 bits ano][4 bits mês][5 bits dia][5 bits hora][6 bits minuto][6 bits segundo]
        :type data_hora: str

        :returns: Data e hora.
        :rtype: datetime
        """
        if len(binario) != 42:
            raise ValueError("A string binária deve conter exatamente 42 bits.")

        # Separar os campos com base nos tamanhos definidos
        ano = int(binario[0:16], 2)
        mes = int(binario[16:20], 2)
        dia = int(binario[20:25], 2)
        hora = int(binario[25:30], 2)
        minuto = int(binario[30:36], 2)
        segundo = int(binario[36:42], 2)

        # Criar e retornar o objeto datetime
        return datetime(ano, mes, dia, hora, minuto, segundo)

    def obter_ultimo_dia_do_mes(self, formato="%d"):
        """
        Retorna o último dia do mês atual, formatado como string.

        :param formato: Formato da data como string (ex: "%d/%m/%Y", "%Y-%m-%d").
                        Usa o padrão ISO "%Y-%m-%d" se não for especificado.
        :type formato: str

        :returns: Último dia do mês atual formatado ou None em caso de erro
        :rtype: str
        """
        try:
            hoje = date.today()

            if hoje.month == 12:
                proximo_mes = hoje.replace(year=hoje.year + 1, month=1, day=1)
            else:
                proximo_mes = hoje.replace(month=hoje.month + 1, day=1)

            ultimo_dia = proximo_mes - timedelta(days=1)

            return ultimo_dia.strftime(formato)
        except Exception as erro:
            module_logger.error(f"❌ Erro ao obter o ultimo de do mês atual: {erro}")
            return None

    def obter_dia_da_semana(self, data: str | None = None) -> str:
        """
        Retorna o dia da semana em português, sem depender do locale do sistema.

        Args:
            data (str | None): Data no formato 'YYYY-MM-DD'.
                            Se None, usa a data de hoje.

        Returns:
            str: Nome do dia da semana em português.
        """
        if data:
            dt = datetime.strptime(data, "%Y-%m-%d").date()
        else:
            dt = date.today()

        return DIAS_PT[dt.weekday()]





# # Exemplos de uso:

# from rpanagem import manipula_datahora

# obj = manipula_datahora.DataHora()

# print(obj.obter_dia_da_semana())  # hoje → "segunda-feira" (se hoje for segunda)s
# print(obj.obter_dia_da_semana("2025-08-30"))  # "sábado"

# # Formato padrão (YYYY-MM-DD)
# print(obj.obter_incluir_valor_data(2, 3))

# # Formato brasileiro (DD/MM/YYYY)
# print(obj.obter_incluir_valor_data(5, 0, formato="%d/%m/%Y"))

# # Apenas mês e ano
# print(obj.obter_incluir_valor_data(0, 0, formato="%m/%Y"))

# # Obtendo data atual no formato brasileiro
# print(obj.obter_incluir_valor_data(formato="%d/%m/%Y"))

# print('#'*50)


# print(obj.converter_data("05/06/2025", "datetime")) # 2025-06-05 00:00:00
# print(obj.converter_data("05/06/2025", "timestamp")) # 1749092400
# print(obj.converter_data("05/06/2025", "date")) # 2025-06-05
# print(obj.converter_data("2025/06/25", "str", "%d-%m-%Y")) # 25-06-2025
# print(obj.converter_data(date.today(), "timestamp"))  # -> 1749524400
# print(obj.converter_data(datetime.now(), "str"))      # -> "2025-06-05"
# print(obj.converter_data(1728172800, "date"))         # -> datetime.date(2024, 10, 6)

# print('#'*50)


# data_exemplo = obj.obter_incluir_valor_data(datahora=True)
# resultado_binario = obj.data_hora_para_binario(data_exemplo)
# print("Data/hora em binário:", resultado_binario)

# data_recuperada = obj.binario_para_data_hora(resultado_binario)
# print("Data/hora reconstruída:", data_recuperada)

