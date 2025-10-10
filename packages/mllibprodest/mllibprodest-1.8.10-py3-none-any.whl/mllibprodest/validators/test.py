# ---------------------------------------------------------------------------------------------------------
# Classes e funções para realização de testes.
#
# Obs.: Não tem nada a ver com 'Unit testing framework' (https://docs.python.org/3/library/unittest.html)
# ---------------------------------------------------------------------------------------------------------
import hashlib
import time
import os
from pathlib import Path
from shutil import copytree, rmtree
from ..utils import make_log
from ..initiators.model_initiator import InitModels

# Códigos para impressão de mensagens coloridas no terminal
BLUE = "\033[1;34m"
RED = "\033[1;31m"
GREEN = "\033[0;32m"
BOLD = "\033[;1m"
RESET = "\033[0;0m"


class Test:
    """
    Classe para realização de testes para validação da implementação das interfaces da lib. Obs.: Não tem nada a ver
    com 'Unit testing framework' (https://docs.python.org/3/library/unittest.html).
    """
    def __init__(self):
        self.__logger = make_log("LOG_TESTS.log")

        h = hashlib.md5()
        h.update(str(time.time()).encode())
        self.__test_id = h.hexdigest()

        msg = f"------------------> Instanciando o teste com o ID: {self.__test_id} <------------------"
        self.__logger.info(msg)
        print(f"\n\n      {BOLD}{BLUE}{msg}{RESET}")

        pasta_corrente = Path.cwd().name

        if pasta_corrente == "worker_pub":
            self.__nome_pasta_worker = "worker_pub"
            self.__nome_mytest = "mytest_pub.py"
        elif pasta_corrente == "worker_retrain":
            self.__nome_pasta_worker = "worker_retrain"
            self.__nome_mytest = "mytest_retrain.py"
        else:
            msg = "Não foi possível encontrar a pasta 'worker_pub' ou 'worker_retrain'. Verifique se estas pastas " \
                  "existem ou se você está rodando os testes na pasta correta. Teste abortado!"
            self.__logger.error(msg)
            print(f"\n\n{msg}")
            print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
            exit(1)

        if Path.exists(Path("requirements.txt")):
            try:
                arq = open("requirements.txt", "r")
            except PermissionError:
                msg = f"Não foi possível ler o arquivo 'requirements.txt' dentro da pasta " \
                      f"'{self.__nome_pasta_worker}'. Permissão de leitura negada. Teste abortado!"
                self.__logger.error(msg)
                print(f"\n\n{msg}")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

            reqs = arq.readlines()
            arq.close()
            vazio = True

            for r in reqs:
                linha = r.rstrip('\n')

                if len(linha) >= 1:
                    vazio = False
                    break

            if not vazio:
                msg = f"O arquivo 'requirements.txt' foi encontrado na pasta '{self.__nome_pasta_worker}' e NÃO " \
                      f"está vazio!"
                self.__logger.info(msg)
                print(f"\n\n{msg}")
            else:
                msg = f"O arquivo 'requirements.txt' foi encontrado na pasta '{self.__nome_pasta_worker}' mas está " \
                      f"vazio. Teste abortado!"
                self.__logger.error(msg)
                print(f"\n\n{msg}")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)
        else:
            msg = f"O arquivo 'requirements.txt' não foi encontrado na pasta '{self.__nome_pasta_worker}'. Por favor," \
                  f" gere este arquivo com a lista de pacotes que foram utilizados na construção do(s) modelo(s). " \
                  f"Teste abortado!"
            self.__logger.error(msg)
            print(f"\n\n{msg}")
            print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
            exit(1)

        # Howto para informar como passar uma função personalizada para realização dos testes
        self.__howto_msg = f"1. Edite o script '{self.__nome_mytest}' (está na pasta '{self.__nome_pasta_worker}')" \
                           f" para implementar a função 'test()';\n2. Crie os testes adicionais que você julgar " \
                           f"necessários para testar o código do worker.\n   REGRAS: Esta função não deve receber " \
                           f"parâmetros adicionais. Não pode retornar valores. Todos os dados para rodá-la devem ser " \
                           f"obtidos de dentro dela.\n   A responsabilidade de criar os testes personalizados e " \
                           f"verificar se passaram é do desenvolvedor do modelo."

        # Artefatos obrigatórios que devem ter os tipos de valores de retorno testados
        self.__mandatory_artifacts = {
            'TrainingParams.pkl': dict,
            'TrainingDatasetsNames.pkl': dict,
            'BaselineMetrics.pkl': dict
        }

        # Métodos que devem ter os tipos de valores de retorno testados
        self.__methods_to_test = {
            'ModeloCLF': {
                'ModeloCLF.get_model_name': str,
                'ModeloCLF.get_model_provider_name': str,
                'ModeloCLF.get_model_info': dict,
                'ModeloCLF.get_model_version': str
            },
            'ModeloRETRAIN': {
                'ModeloRETRAIN.get_model_name': str,
                'ModeloRETRAIN.get_model_provider_name': str,
                'ModeloRETRAIN.get_experiment_name': str,
                'ModeloRETRAIN.get_dataset_provider_name': str
            }
        }

        # Guarda os modelos instanciados
        self.__modelos = None

        # Instancia os scripts de testes personalizados
        self.__validation_function = None

        if Path.exists(Path(self.__nome_mytest)):
            try:
                if self.__nome_mytest == "mytest_pub.py":
                    from mytest_pub import test
                    self.__validation_function = test
                elif self.__nome_mytest == "mytest_retrain.py":
                    from mytest_retrain import test
                    self.__validation_function = test
            except ImportError:
                msg = "AVISO: A função para realização do teste personalizado pelo usuário não foi encontrada." \
                      "\n       Caso deseje criar um teste personalizado, faça o seguinte:\n"
                self.__logger.info(msg + self.__howto_msg)
                print(f"\n\n{msg + self.__howto_msg}\n")
        else:
            msg = f"AVISO: O arquivo '{self.__nome_mytest}' não foi encontrado na pasta '{self.__nome_pasta_worker}'" \
                  f". Caso deseje criar um teste personalizado, crie\n       um arquivo chamado " \
                  f"'{self.__nome_mytest}' e faça o seguinte:\n"
            self.__logger.info(msg + self.__howto_msg)
            print(f"\n\n{msg + self.__howto_msg}\n")

    def __validate_methods(self, model, class_name: str) -> bool:
        """
        Valida os métodos definidos no construtor da classe através do atributo 'self.__methods_to_test'.
            :param model: Modelo de onde os métodos serão chamados.
            :param class_name: Nome da classe que possui os métodos que serão validados.
            :return: True, se todos os métodos foram validados. False, caso algum método não tenha sido validado.
        """
        validado = True

        for method_name, return_type in self.__methods_to_test[class_name].items():
            nome_metodo_aux = method_name.split(".")[1]
            msg = f"=> Testando o método '{nome_metodo_aux}'..."
            self.__logger.info(msg)
            print(f"\n\n{msg}\n")

            retorno = None

            try:
                if method_name == "ModeloCLF.get_model_name":
                    retorno = model.get_model_name()
                elif method_name == "ModeloCLF.get_model_provider_name":
                    retorno = model.get_model_provider_name()
                elif method_name == "ModeloCLF.get_model_info":
                    retorno = model.get_model_info()
                elif method_name == "ModeloCLF.get_model_version":
                    retorno = model.get_model_version()
                elif method_name == "ModeloRETRAIN.get_model_name":
                    retorno = model.get_model_name()
                elif method_name == "ModeloRETRAIN.get_model_provider_name":
                    retorno = model.get_model_provider_name()
                elif method_name == "ModeloRETRAIN.get_experiment_name":
                    retorno = model.get_experiment_name()
                elif method_name == "ModeloRETRAIN.get_dataset_provider_name":
                    retorno = model.get_dataset_provider_name()
            except AttributeError as e:
                msg = f"A chamada ao método '{nome_metodo_aux}' falhou: {str(e)}."
                self.__logger.error(msg)
                print(f"\n{RED}***ERRO***: {msg}{RESET}\n")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

            tipo_retorno = type(retorno)

            if tipo_retorno is return_type:
                msg = f"Tipo de retorno da chamada ao método '{nome_metodo_aux}' OK: {retorno}"
                self.__logger.info(msg)
                print(f"   {msg}\n")
            else:
                validado = False
                msg = f"O método '{nome_metodo_aux}' deve retornar o tipo '{return_type.__name__}', porém retornou " \
                      f"'{tipo_retorno.__name__}'."
                self.__logger.error(msg)
                print(f"{RED}***ERRO***: {msg}{RESET}\n")

        return validado

    def __validate_mandatory_artifacts(self, model) -> bool:
        """
        Valida se os artefatos obrigatórios definidos para o modelo foram implementados pelo usuário.
            :param model: Modelo de onde será chamada a função utilitária 'convert_artifact_to_object'.
            :return: True, se todos os artefatos obrigatórios foram encontrados. False, caso algum artefato obrigatório
                     não tenha sido encontrado.
        """
        validado = True

        for nome_artefato_obrigatorio, tipo_artefato_obrigatorio in self.__mandatory_artifacts.items():
            msg = f"=> Procurando pelo artefato obrigatório '{nome_artefato_obrigatorio}'..."
            self.__logger.info(msg)
            print(f"\n{msg}\n")

            artefato_lido = model.convert_artifact_to_object(model_name=model.get_model_name(),
                                                             file_name=nome_artefato_obrigatorio)
            tipo_artefato_lido = type(artefato_lido)

            if tipo_artefato_lido is tipo_artefato_obrigatorio:
                if len(artefato_lido) > 0:
                    msg = f"Conteúdo do artefato obrigatório '{nome_artefato_obrigatorio}': '{artefato_lido}'"
                    self.__logger.info(msg)
                    print(f"  {msg}\n")
                else:
                    validado = False
                    msg = f"O artefato obrigatório '{nome_artefato_obrigatorio}' deve ter o tamanho maior que 0 (zero)."
                    self.__logger.error(msg)
                    print(f"{RED}***ERRO***: {msg}{RESET}\n")
            else:
                validado = False
                msg = f"O artefato obrigatório '{nome_artefato_obrigatorio}' deve ser do tipo " \
                      f"'{tipo_artefato_obrigatorio.__name__}', porém é do tipo: '{tipo_artefato_lido.__name__}'."
                self.__logger.error(msg)
                print(f"{RED}***ERRO***: {msg}{RESET}\n")

        return validado

    def __validate_pub(self):
        """
        Valida os scripts para publicação do modelo utilizando a classe ModeloCLF.
        """
        msg = "Scripts para publicação do modelo utilizando a classe 'ModeloCLF'..."
        self.__logger.info(msg)
        print(f"\n\n # {msg}")

        for nome_modelo, modelo in self.__modelos.items():
            print(f"\n{GREEN} ### MODELO: {nome_modelo} ### {RESET}\n")

            if not self.__validate_methods(modelo, "ModeloCLF"):
                msg = "Erro ao validar os métodos obrigatórios. Verifique as mensagens de validação acima."
                self.__logger.error(msg)
                print(f"\n\n{RED} *** {msg}{RESET}\n")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

        msg = "AVISO: Os métodos 'predict', 'evaluate' e 'get_feedback' não serão testados porque necessitam de " \
              "dados que são específicos para cada implementação.\nCaso deseje testar estes métodos, faça o seguinte:\n"
        self.__logger.info(msg + self.__howto_msg)
        print(f"\n\n{msg + self.__howto_msg}\n")

    def __validate_retrain(self):
        """
        Valida os scripts para publicação do modelo utilizando a classe ModeloRETRAIN.
        """
        msg = "Scripts para publicação do modelo utilizando a classe 'ModeloRETRAIN'..."
        self.__logger.info(msg)
        print(f"\n\n # {msg}")

        for nome_modelo, modelo in self.__modelos.items():
            print(f"\n{GREEN} ### MODELO: {nome_modelo} ### {RESET}\n")

            if not self.__validate_methods(modelo, "ModeloRETRAIN"):
                msg = "Erro ao validar os métodos obrigatórios. Verifique as mensagens de validação acima."
                self.__logger.error(msg)
                print(f"\n\n{RED} *** {msg}{RESET}\n")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

            # Testa o carregamento do modelo e verifica se os artefatos obrigatórios estão de acordo
            model_name = modelo.get_model_name()
            provider_name = modelo.get_model_provider_name()

            try:
                modelo.load_model(model_name=model_name, provider=provider_name)
            except AttributeError as e:
                msg = f"A chamada ao método 'load_model' falhou: {str(e)}."
                self.__logger.error(msg)
                print(f"\n\n{msg}\n")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

            if not self.__validate_mandatory_artifacts(modelo):
                msg = "Erro ao validar os artefatos obrigatórios. Verifique as mensagens de validação acima."
                self.__logger.error(msg)
                print(f"\n\n{RED} *** {msg}{RESET}\n")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)

        msg = "AVISO: Os métodos 'evaluate' e 'retrain' não serão testados porque necessitam de dados que " \
              "são específicos para cada implementação.\nCaso deseje testar estes métodos, faça o seguinte:\n"
        self.__logger.info(msg + self.__howto_msg)
        print(f"\n\n{msg + self.__howto_msg}\n")

    def __validate_params_returns(self):
        """
        Valida alguns parâmetros e valores de retorno solicitados pelas interfaces que foram implementados. Porém, não
        é escopo desta função validar os dados que estão sendo utilizados pelas funções implementadas.
        """
        msg = f"=> INICIO: Test ID={self.__test_id}. Teste padrão da lib."
        self.__logger.info(msg)
        print(f"\n\n{BOLD}{BLUE}{msg}{RESET}\n")

        if self.__nome_pasta_worker == "worker_pub":
            self.__validate_pub()
        elif self.__nome_pasta_worker == "worker_retrain":
            self.__validate_retrain()

        msg = f"=> FIM: Test ID={self.__test_id}. Teste padrão da lib."
        self.__logger.info(msg)
        print(f"\n\n{BOLD}{BLUE}{msg}{RESET}\n")

    def __run_validation_function(self):
        """
        Executa a função de validação criada e personalizada pelo usuário.
        """
        msg = f"=> INICIO: Test ID={self.__test_id}. Testes personalizados pelo usuário. Dados da função utilizada: " \
              f"{str(self.__validation_function)}."
        self.__logger.info(msg)
        print(f"\n\n{BOLD}{BLUE}{msg}{RESET}\n")

        type_validation_function = type(self.__validation_function).__name__

        if type_validation_function != 'function':
            msg = f"O parâmetro 'validation_function' deve receber uma função mas recebeu " \
                  f"'{type_validation_function}'. Verifique a implementação da função 'test' no arquivo " \
                  f"'{self.__nome_mytest}'."
            self.__logger.error(msg)
            print(f"\n\n{msg}")
            print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
            exit(1)

        self.__validation_function(self.__modelos)

        msg = f"=> FIM: Test ID={self.__test_id}. Testes personalizados pelo usuário."
        self.__logger.info(msg)
        print(f"\n\n{BOLD}{BLUE}{msg}{RESET}\n")

    def validate(self, mlruns_path: str = ""):
        """
        Valida a implementação das interfaces da lib através das chamadas de funções específicas para este fim. Além do
        conjunto de testes padrões executados pela lib, se os arquivos 'mytest_pub.py' e 'mytest_retrain.py' existirem
        nas pastas de cada worker respectivamente, a função 'test()' será procurada e, caso exista, será carregada e
        utilizada para rodar os testes personalizados pelo usuário.
            :param mlruns_path: Caminho completo da pasta 'mlruns'. Esta pasta é criada na pasta local onde o servidor
                                do MLflow, utilizado para registrar o modelo, foi iniciado. Se o valor padrão for
                                mantido, tenta utilizar as variáveis de ambiente 'MLFLOW_TRACKING_URI', para encontrar
                                o endereço do servidor MLflow, e 'MLFLOW_S3_ENDPOINT_URL' para obter o endereço do
                                endpoint utilizado para a persistência dos artefatos gerados nos experimentos.
        """
        # Verifica se as variáveis de ambiente para o MLflow funcionar remotamente e com os artefatos via s3 existem.
        # Se não existirem, prepara o ambiente para rodar os testes com o MLflow local.
        if os.getenv("MLFLOW_TRACKING_URI") is None and os.getenv("MLFLOW_S3_ENDPOINT_URL") is None:
            if mlruns_path != "":
                if "mlruns" in str(Path(mlruns_path)):
                    caminho_mlruns = str(Path(mlruns_path))
                else:
                    caminho_mlruns = str(Path(mlruns_path) / "mlruns")

                try:
                    copytree(caminho_mlruns, "mlruns", dirs_exist_ok=True)
                except FileNotFoundError:
                    msg = "O caminho para a pasta 'mlruns' está incorreto. Teste abortado!"
                    self.__logger.error(msg)
                    print(f"\n\n{msg}")
                    print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                    exit(1)
                except PermissionError:
                    msg = f"Permissão de leitura na pasta de origem ('{caminho_mlruns}') ou gravação na pasta de " \
                          f"destino ('mlruns') negada. Teste abortado!"
                    self.__logger.error(msg)
                    print(f"\n\n{msg}")
                    print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                    exit(1)

                os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"

                msg = "=> Instanciando os modelos definidos no arquivo 'params.conf'..."
                self.__logger.info(msg)
                print(f"\n\n{msg}\n")

                # Não tratei as exceções para preservar o traceback e facilitar a procura da origem do erro.
                self.__modelos = InitModels.init_models()

                # Roda os testes padrões da lib
                self.__validate_params_returns()

                # Se foi criada uma função para o teste, utiliza
                if self.__validation_function is not None:
                    self.__run_validation_function()

                # Atualiza a pasta 'mlruns'
                try:
                    copytree("mlruns", caminho_mlruns, dirs_exist_ok=True)
                except PermissionError:
                    msg = f"Permissão de leitura na pasta de origem ('mlruns') ou gravação na pasta de destino " \
                          f"('{caminho_mlruns}') negada. Teste abortado!"
                    self.__logger.error(msg)
                    print(f"\n\n{msg}")
                    print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                    exit(1)

                # Limpa os arquivos criados na execução dos testes
                for path in Path("temp_area").glob("**/*"):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        rmtree(path)

                rmtree("mlruns", ignore_errors=True)
            else:
                msg = "Informe o parâmetro '--mlruns_path=<caminho completo para a pasta mlruns>' ao rodar o script. " \
                      "A pasta 'mlruns' é criada na pasta local onde o servidor do MLflow, utilizado para registrar " \
                      "o modelo, foi iniciado. Teste abortado!"
                self.__logger.error(msg)
                print(f"\n\n{msg}")
                print(f"\n{RED}  *** O TESTE FALHOU! ***{RESET}\n")
                exit(1)
        else:  # Encontrou as variáveis de ambiente e vai rodar com o MLflow remoto
            msg = "=> Instanciando os modelos definidos no arquivo 'params.conf'..."
            self.__logger.info(msg)
            print(f"\n\n{msg}\n")

            # Não tratei as exceções para preservar o traceback e facilitar a procura da origem do erro.
            self.__modelos = InitModels.init_models()

            self.__validate_params_returns()

            if self.__validation_function is not None:
                self.__run_validation_function()
