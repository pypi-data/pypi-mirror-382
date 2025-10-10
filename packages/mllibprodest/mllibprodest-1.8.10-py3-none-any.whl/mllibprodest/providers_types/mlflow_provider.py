# ----------------------------------------------------------------------------------------------------
# Provider para obtenção de modelos e artefatos registrados no Mlflow
# ----------------------------------------------------------------------------------------------------
import mlflow
import pickle
import requests
from os import getenv
from pathlib import Path
from mlflow.exceptions import RestException, MlflowException
from shutil import rmtree
from ..utils import make_log

# Para facilitar, define um logger único para todas as funções
LOGGER = make_log("LOG_MLLIB.log")


def load_model_mlflow(model_name: str, artifacts_destination_path: str = "temp_area"):
    """
    Carrega o modelo que está em produção e baixa os artefatos necessários utilizando o MLflow.
        :param model_name: Nome do modelo que será carregado.
        :param artifacts_destination_path: Caminho local para onde os artefatos serão baixados.
        :return: Modelo carregado.
    """
    artefatos_obrigatorios = ["TrainingParams.pkl", "TrainingDatasetsNames.pkl", "BaselineMetrics.pkl"]
    caminho_artefatos = Path(artifacts_destination_path) / model_name

    # Antes de carregar o modelo, faz uma limpeza em alguns artefatos antigos. Obs.: Isso é necessário para evitar que,
    # caso o usuário esqueça de salvar um artefato obrigatório, seja carregado um artefato antigo salvo localmente.
    if artifacts_destination_path == "temp_area":
        rmtree(caminho_artefatos, ignore_errors=True)
    else:
        for artefato in artefatos_obrigatorios:
            Path.unlink(caminho_artefatos / artefato, missing_ok=True)

    try:
        Path.mkdir(caminho_artefatos, parents=True, exist_ok=True)
    except PermissionError:
        msg = f"Não foi possível criar a pasta de destino dos artefatos '{artifacts_destination_path}'. Permissão " \
              f"de escrita negada."
        LOGGER.error(msg)
        raise PermissionError(msg) from None

    alias = 'production'

    # Carrega o modelo que está em produção
    try:
        modelo = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}@{alias}")
    except RestException:
        msg = f"O modelo '{model_name}' com o alias '{alias}' não foi encontrado."
        LOGGER.error(msg)
        raise RuntimeError(msg) from None
    except MlflowException as e:
        msg = f"Não foi possível carregar o modelo '{model_name}'. Mensagem do MLFlow: '{e}'."
        LOGGER.error(msg)
        raise RuntimeError(msg) from None

    # Baixa todos os artefatos com base no 'run_id' do modelo
    endereco_base_artefatos = f"runs:/{modelo.metadata.run_id}/"

    try:
        mlflow.artifacts.download_artifacts(artifact_uri=endereco_base_artefatos, dst_path=str(caminho_artefatos))
    except MlflowException as e:
        msg = f"Não foi possível carregar os artefatos no endereço '{endereco_base_artefatos}'. " \
              f"Mensagem do MLFlow: '{e}'."
        LOGGER.error(msg)
        raise RuntimeError(msg) from None

    return modelo


def load_production_params_mlflow(model_name: str) -> dict:
    """
    Carrega os parâmetros utilizados para treinar o modelo que está em produção no MLflow.
        :param model_name: Nome do modelo que está em produção.
        :return: Dicionário contendo os parâmetros carregados.
    """
    modelo = load_model_mlflow(model_name, artifacts_destination_path='temp_area')
    LOGGER.info(f"Utilizando os parâmetros de produção do modelo '{model_name}' (run_id: {modelo.metadata.run_id})")
    parametros = None
    nome_arq = str(Path("temp_area") / model_name / "TrainingParams.pkl")
    arq = None
    msg = ""

    try:
        arq = open(nome_arq, 'rb')
    except FileNotFoundError:
        msg += f"O arquivo '{nome_arq}' não foi encontrado. "
    except PermissionError:
        msg += f"Permissão de leitura negada para o arquivo '{nome_arq}'. "

    if arq is not None:
        try:
            parametros = pickle.load(arq)
        except pickle.UnpicklingError as e:
            msg += f"Não foi possível carregar os parâmetros através do arquivo '{nome_arq}' com o Pickle (mensagem " \
                   f"Pickle: {e}). "

        arq.close()

    if parametros is not None and type(parametros) is dict:
        return parametros
    else:
        msg += f"Não foi possível carregar os parâmetros de produção do modelo '{model_name}'. Certifique-se que o " \
               f"modelo exista e que possua os parâmetros persistidos num dicionário, através do Pickle, com o nome " \
               f"'TrainingParams.pkl'."
        LOGGER.error(msg)
        raise RuntimeError(msg)


def load_production_datasets_names_mlflow(model_name: str) -> dict:
    """
    Carrega os nomes dos datasets que foram utilizados para treinar o modelo que está em produção no MLflow.
        :param model_name: Nome do modelo que está em produção.
        :return: Dicionário contendo os nomes dos datasets carregados.
    """
    modelo = load_model_mlflow(model_name, artifacts_destination_path='temp_area')
    LOGGER.info(f"Utilizando os nomes dos datasets de produção do modelo '{model_name}' (run_id: "
                f"{modelo.metadata.run_id})")
    nomes_datasets = None
    nome_arq = str(Path("temp_area") / model_name / "TrainingDatasetsNames.pkl")
    arq = None
    msg = ""

    try:
        arq = open(nome_arq, 'rb')
    except FileNotFoundError:
        msg += f"O arquivo '{nome_arq}' não foi encontrado. "
    except PermissionError:
        msg += f"Permissão de leitura negada para o arquivo '{nome_arq}'. "

    if arq is not None:
        try:
            nomes_datasets = pickle.load(arq)
        except pickle.UnpicklingError as e:
            msg += f"Não foi possível carregar os nomes dos datasets através do arquivo '{nome_arq}' com o Pickle " \
                   f"(mensagem Pickle: {e}). "

        arq.close()

    if nomes_datasets is not None and type(nomes_datasets) is dict:
        return nomes_datasets
    else:
        msg += f"Não foi possível carregar os nomes dos datasets de produção do modelo '{model_name}'. Certifique-se " \
               f"que o modelo exista e que possua os nomes dos datasets persistidos num dicionário, através do " \
               f"Pickle, com o nome 'TrainingDatasetsNames.pkl'."
        LOGGER.error(msg)
        raise RuntimeError(msg)


def load_production_baseline_mlflow(model_name: str) -> dict:
    """
    Carrega as métricas do modelo que está em produção no MLflow que serão utilizadas como baseline para avaliação
    automatizada do modelo.
        :param model_name: Nome do modelo que está em produção.
        :return: Dicionário contendo as métricas de baseline.
    """
    modelo = load_model_mlflow(model_name, artifacts_destination_path='temp_area')
    LOGGER.info(f"Utilizando o baseline de produção do modelo '{model_name}' (run_id: {modelo.metadata.run_id})")
    baseline = None
    nome_arq = str(Path("temp_area") / model_name / "BaselineMetrics.pkl")
    arq = None
    msg = ""

    try:
        arq = open(nome_arq, 'rb')
    except FileNotFoundError:
        msg += f"O arquivo '{nome_arq}' não foi encontrado. "
    except PermissionError:
        msg += f"Permissão de leitura negada para o arquivo '{nome_arq}'. "

    if arq is not None:
        try:
            baseline = pickle.load(arq)
        except pickle.UnpicklingError as e:
            msg += f"Não foi possível carregar o baseline através do arquivo '{nome_arq}' com o Pickle (mensagem " \
                   f"Pickle: {e}). "

        arq.close()

    if baseline is not None and type(baseline) is dict:
        return baseline
    else:
        msg += f"Não foi possível carregar o baseline de produção do modelo '{model_name}'. Certifique-se que o " \
               f"modelo exista e que possua o baseline persistido num dicionário, através do Pickle, com o nome " \
               f"'BaselineMetrics.pkl'."
        LOGGER.error(msg)
        raise RuntimeError(msg)


def get_models_versions_mlflow(models_names: list) -> dict:
    """
    Obtém as versões de alguns modelos que estão sendo providos pelo provider.
        :param models_names: Lista com os nomes dos modelos para obtenção das versões.
        :return: Dicionário com o nome de cada modelo como chave e a respectiva versão como valor.
    """
    # Obtém as credenciais para acesso ao MLflow
    mlflow_uri = getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        msg = "Não foi possível obter a variável de ambiente 'MLFLOW_TRACKING_URI'"
        LOGGER.error(msg)
        raise RuntimeError(msg)

    mlflow_user = getenv("MLFLOW_TRACKING_USERNAME")
    if not mlflow_user:
        msg = "Não foi possível obter a variável de ambiente 'MLFLOW_TRACKING_USERNAME'"
        LOGGER.error(msg)
        raise RuntimeError(msg)

    mlflow_password = getenv("MLFLOW_TRACKING_PASSWORD")
    if not mlflow_password:
        msg = "Não foi possível obter a variável de ambiente 'MLFLOW_TRACKING_PASSWORD'"
        LOGGER.error(msg)
        raise RuntimeError(msg)

    models_versions = {}

    # Faz a busca da versão dos modelos utilizando alias
    for model_name in models_names:
        params = {'name': model_name, 'alias': "production"}

        try:
            response = requests.get(
                f"{mlflow_uri}/api/2.0/mlflow/registered-models/alias",
                params=params,
                auth=(mlflow_user, mlflow_password)
            )
        except BaseException as e:
            msg = f"Não foi possível obter as versões para os modelos: {models_names}. Erro reportado pelo MLflow: " \
                  f"{e}."
            LOGGER.error(msg)
            raise RuntimeError(e) from None

        dados_modelo = response.json()

        if "model_version" not in dados_modelo:
            msg = f"A resposta do MLflow não contém a chave 'model_version'. Resposta do MLflow: {dados_modelo}"
            LOGGER.error(msg)
            raise KeyError(msg)

        if "version" not in dados_modelo['model_version']:
            msg = f"A resposta do MLflow não contém a chave 'version'. Resposta do MLflow: {dados_modelo}"
            LOGGER.error(msg)
            raise KeyError(msg)

        models_versions[model_name] = dados_modelo['model_version']['version']

    return models_versions
