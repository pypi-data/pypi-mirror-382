# ----------------------------------------------------------------------------------------------------
# Funções para prover o acesso aos modelos persistidos e aos datasets
# ----------------------------------------------------------------------------------------------------
from .utils import make_log
from .providers_types.minio_provider import load_datasets_minio
from .providers_types.local_provider import load_datasets_local
from .providers_types.mlflow_provider import load_production_params_mlflow, load_production_datasets_names_mlflow, \
    load_production_baseline_mlflow, load_model_mlflow, get_models_versions_mlflow

# Para facilitar, define um logger único para todas as funções
LOGGER = make_log("LOG_MLLIB.log")


class Provider:
    """
    Classe para prover o acesso aos modelos persistidos e aos datasets.
    """
    @staticmethod
    def load_datasets(datasets_filenames: dict, provider: str = 'minio') -> dict:
        """
        Carrega os datasets necessários para o modelo.
            :param datasets_filenames: Dicionário contendo os tipos de datasets e os nomes dos respectivos arquivos.
                                       Exemplo: {'features': 'nome_arquivo_features', 'targets': 'nome_arquivo_targets'}
            :param provider: Nome do provedor que fornecerá os datasets. Tipos de provider: 'minio' e 'local'.
            :return: Dicionário com os datasets carregados.
        """
        if provider == "minio":
            return load_datasets_minio(datasets_filenames)
        elif provider == "local":
            return load_datasets_local(datasets_filenames)
        else:
            msg = f"Não foi possível carregar os datasets. O provider '{provider}' não foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)

    @staticmethod
    def load_production_params(model_name: str, provider: str = 'mlflow') -> dict:
        """
        Carrega os parâmetros utilizados para treinar o modelo que está em produção.
            :param model_name: Nome do modelo que está em produção.
            :param provider: Nome do provedor que fornecerá os parâmetros do modelo em produção. Tipos de provider:
                             'mlflow'.
            :return: Dicionário contendo os parâmetros carregados.
        """
        if provider == "mlflow":
            return load_production_params_mlflow(model_name)
        else:
            msg = f"Não foi possível carregar os parâmetros do modelo '{model_name}'. O provider '{provider}' não " \
                  f"foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)

    @staticmethod
    def load_production_datasets_names(model_name: str, provider: str = 'mlflow') -> dict:
        """
        Carrega os nomes dos datasets que foram utilizados para treinar o modelo que está em produção.
            :param model_name: Nome do modelo que está em produção.
            :param provider: Nome do provedor que fornecerá os nomes dos datasets do modelo em produção. Tipos de
                             provider: 'mlflow'.
            :return: Dicionário contendo os nomes dos datasets carregados.
        """
        if provider == "mlflow":
            return load_production_datasets_names_mlflow(model_name)
        else:
            msg = f"Não foi possível carregar os nomes dos datasets do modelo '{model_name}'. O provider " \
                  f"'{provider}' não foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)

    @staticmethod
    def load_production_baseline(model_name: str, provider: str = 'mlflow') -> dict:
        """
        Carrega as métricas do modelo que está em produção que serão utilizadas como baseline para avaliação
        automatizada do modelo.
            :param model_name: Nome do modelo que está em produção.
            :param provider: Nome do provedor que fornecerá o baseline do modelo em produção. Tipos de provider:
                             'mlflow'.
            :return: Dicionário contendo as métricas de baseline.
        """
        if provider == "mlflow":
            return load_production_baseline_mlflow(model_name)
        else:
            msg = f"Não foi possível carregar o baseline do modelo '{model_name}'. O provider '{provider}' não " \
                  f"foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)

    @staticmethod
    def load_model(model_name: str, provider: str = 'mlflow', artifacts_destination_path: str = 'temp_area'):
        """
        Carrega o modelo que está em produção e baixa os artefatos necessários.
            :param model_name: Nome do modelo que será carregado.
            :param provider: Nome do provedor que fornecerá o modelo. Tipos de provider: 'mlflow'.
            :param artifacts_destination_path: Caminho para onde os artefatos serão baixados.
            :return: Modelo carregado.
        """
        if provider == "mlflow":
            return load_model_mlflow(model_name, artifacts_destination_path)
        else:
            msg = f"Não foi possível carregar o modelo '{model_name}'. O provider '{provider}' não foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)

    @staticmethod
    def get_models_versions(models_names: list, provider: str = 'mlflow') -> dict:
        """
        Obtém as versões de alguns modelos que estão sendo providos pelo provider.
            :param models_names: Lista com os nomes dos modelos para obtenção das versões.
            :param provider: Provedor para obtenção das versões dos modelos.
            :return: Dicionário com o nome de cada modelo como chave e a respectiva versão como valor.
        """
        if type(models_names) is not list:
            msg = f"Não foi possível obter as versões para os modelos. '{models_names}' não é uma lista de modelos."
            LOGGER.error(msg)
            raise TypeError(msg)

        if provider == "mlflow":
            return get_models_versions_mlflow(models_names)
        else:
            msg = f"Não foi possível obter as versões para os modelos: {models_names}. O provider '{provider}' não " \
                  f"foi encontrado."
            LOGGER.error(msg)
            raise ValueError(msg)
