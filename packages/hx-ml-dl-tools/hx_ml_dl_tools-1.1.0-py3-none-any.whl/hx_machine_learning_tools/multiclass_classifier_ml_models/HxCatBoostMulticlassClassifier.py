from hx_machine_learning_tools.ml_base_model import HxMachineLearningBaseModel
from _hx_model_evaluation_tools import EvaluateMulticlassClassifier, MulticlassClassifierMetricsCalculations
from catboost import CatBoostClassifier
from _hx_model_evaluation_tools import MlShapToolsMulticlass
from typing import Dict, Literal, List, Any, Tuple
from joblib import dump
import pandas as pd
import numpy as np
import datetime
import os


class HxCatBoostMulticlassClassifier(HxMachineLearningBaseModel):

    def __init__(self,
                 data_dict: Dict[str, pd.DataFrame],
                 hiperparams: dict,
                 metric: Literal['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 'f1_micro', 'balanced_accuracy', 'roc_auc_ovr'],
                 problem_type: Literal['multiclass'],
                 save_path: str | None = None,
                 bins: dict | None = None,
                 verbose: Literal['show_all', 'show_basics', 'dont_show'] = 'dont_show',
                 random_state: int = 42,
                 n_classes: int = 3):
        """
        Clase para construir modelos de clasificación multiclase con LightGBM
        :param data_dict: Diccionario que contiene el x_train, y_train, x_test, y_test
        :param hiperparams: Hiperparámetros del modelo
        :param metric: Métrica de evaluación para multiclase
        :param problem_type: Tipo de problema (solo multiclass)
        :param save_path: Ruta para guardar resultados
        :param bins: Bins para estratificación
        :param verbose: Nivel de verbosidad
        :param random_state: Semilla para reproducibilidad
        :param n_classes: Número de clases
        """
        super().__init__(data_dict, hiperparams, "CAT_multiclass_classifier", save_path)

        # --------------------------------------------------------------------------------------------
        # -- 0: Almaceno nombre de la clase, pinto la entrada y creo la propiedad model
        # --------------------------------------------------------------------------------------------

        # ---- 0.1: Almaceno el nombre de la clase
        self.class_name: str = f"HxCatBoostMulticlassClassifier"

        # ---- 0.2: Pinto la entrada
        self.CT.IT.intro_print(self.class_name)

        # ---- 0.3: Creo la propiedad model y la inicializo en None
        self.model = None

        # --------------------------------------------------------------------------------------------
        # -- 1: Asigno las propiedades abstractas
        # --------------------------------------------------------------------------------------------

        # ---- 1.1: Verbose
        self._verbose: Literal['show_all', 'show_basics', 'dont_show'] = verbose

        # ---- 1.2: Metric
        self._metric: Literal['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 'f1_micro', 'balanced_accuracy', 'roc_auc_ovr'] = metric

        # ---- 1.3: Problem type (solo multiclass)
        self._problem_type: Literal['multiclass'] = problem_type

        # ---- 1.4: Número de clases
        self.n_classes: int = n_classes

        # --------------------------------------------------------------------------------------------
        # -- 2: Asigno las propiedades estandar
        # --------------------------------------------------------------------------------------------

        # ---- 2.1: Si bins es None, pongo el bins por defecto, sino lo asigno
        if bins is None:
            self.bins: Dict[str, List] = {
                "bins": [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1],
                "labels": ["0-12.5", "12.5-25", "25-37.5", "37.5-50", "50-62.5", "62.5-75", "75-87.5", "87.5-100"]
            }
        else:
            self.bins = bins

        # ---- 2.2: Path donde se va a guardar la informacion del modelo
        self.model_save_path: str = self.get_save_path()

        # ---- 2.3: Random state con el que se van a inicializar los pesos, por defecto 42
        self.random_state: int = random_state

        # ---- 2.4: Verifico que el número de clases sea válido
        if self.n_classes < 2:
            raise ValueError("El número de clases debe ser al menos 2")
        elif self.n_classes == 2:
            self.CT.IT.warning_print("Se está usando clasificación multiclase con 2 clases. Considera usar binary classification")

        # --------------------------------------------------------------------------------------------
        # -- 3: Reformulo el problem_type porque CAT lo requiere
        # --------------------------------------------------------------------------------------------

        # ---- 3.2: En caso de que el problem_type sea multiclass, reformateo a multi:softmax
        if self.problem_type == 'multiclass':
            self.problem_type = 'MultiClass'

    # <editor-fold desc="Implementacion de metodos abstractos   ------------------------------------------------------------------------------------------------------------------">

    def get_save_path(self) -> str:
        """
        Metodo que hace lo siguiente:
        1: Busca dentro del path definido en la clase padre {save_path}/training_results/&Y_%m_%d/v_xxx si existe algúna carpeta llamda {self.model_name
        2: Si ya existe crea una nueva version, es decir {save_path}/training_results/&Y_%m_%d/v_xxx+1/{self.model_name y la asigna como self.save_path
        3: Si no existe, la asigna como self.save_path, es decir: {save_path}/training_results/&Y_%m_%d/v_xxx/{self.model_name
        :return: el save_path
        """

        # -- Si el path no existe, simplemente lo creo y lo asigno
        if not os.path.exists(f"{self.save_path}/{self.current_train_version}/{self.model_name}"):
            self.CT.OT.create_folder_if_not_exists(f"{self.save_path}/{self.current_train_version}/{self.model_name}")

        # -- Si el path existe, creo una nueva version y lo asigno
        else:
            self.current_train_version: str = self.new_training_version()

            self.CT.OT.create_folder_if_not_exists(f"{self.save_path}/{self.current_train_version}")
            self.CT.OT.create_folder_if_not_exists(f"{self.save_path}/{self.current_train_version}/{self.model_name}")

        # -- Actualizo las propiedades pertinentres de la clase padre
        self.day_train_versions: List[str] = self.list_versions()

        # -- Retorno el path
        return f"{self.save_path}/{self.current_train_version}/{self.model_name}"

    def fit_and_get_metrics(self, save_metrics_dict: bool) -> Dict[str, Any]:
        """
        Implementacion del metodo que entrena y devuelve el diccionario de métricas para multiclase
        :param save_metrics_dict: Boleana que indica si quieres guardar el diccionario de metricas
        :return: diccionario de metricas
        """
        # --------------------------------------------------------------------------------------------
        # -- 0: Pinto la entrada
        # --------------------------------------------------------------------------------------------
        start_date: datetime.datetime = datetime.datetime.now()
        self.CT.IT.sub_intro_print(f"{self.class_name}.fit_and_get_metrics: Inicio de entrenamiento multiclase a las {start_date}...")
        self.CT.IT.info_print(f"Número de clases: {self.n_classes}", "light_blue")

        # --------------------------------------------------------------------------------------------
        # -- 1: Instancio el modelo y entreno
        # --------------------------------------------------------------------------------------------

        # ---- 1.1: Instancio el modelo y le asigno los parámetros para multiclase
        self.model: CatBoostClassifier = CatBoostClassifier(
            loss_function=self.problem_type,
            random_state=self.random_state,
            allow_writing_files=False,
            verbose=self.verbose,
            **self.hiperparams
        )

        # ---- 1.2: Realizo el entrenamiento (y_train ya no necesita ravel() para multiclase)
        self.model.fit(X=self.x_train, y=self.y_train)

        # ---- 1.3: Pinto el fin del entrenamiento y lo que ha tardado
        self.CT.IT.info_print(f"Entrenamiento completado a las {datetime.datetime.now()}. Ha tardado {datetime.datetime.now() - start_date}", "light_magenta")

        # --------------------------------------------------------------------------------------------
        # -- 2: Realizo las predicciones, mando a evaluar y retorno el diccionario de métricas
        # --------------------------------------------------------------------------------------------

        # ---- 2.1: Realizo las predicciones
        y_pred_train: np.ndarray = self.model.predict(self.x_train_df)
        y_pred_test: np.ndarray = self.model.predict(self.x_test_df)

        # ---- 2.2. Evalúo y almaceno las metricas para multiclase
        metrics: Dict[str, Any] = EvaluateMulticlassClassifier(
            {
                "y_train": self.y_train,
                "y_eval": None,
                "y_test": self.y_test,
                "y_pred_train": y_pred_train,
                "y_pred_eval": None,
                "y_pred_test": y_pred_test,
                "target_col_name": self.target_col_name
            },
            self.model_name,
            self.metric,
            self.n_classes
        ).calculate_and_print_metrics()

        # ---- 2.3: Almaceno el diccionario de metricas como json en el path
        if save_metrics_dict:
            self.save_metrics_dict_json(metrics, self.model_save_path)

        # ---- 2.4. Pinto y retorno las métricas
        end_date = datetime.datetime.now()
        self.CT.IT.info_print(f"fit_and_get_metrics terminado a las {end_date}. Ha tardado {end_date - start_date}", "light_magenta")
        return metrics

    def fit_and_get_model_and_results(self) -> Tuple[Any, np.ndarray, np.ndarray, Dict[str, Any], List]:
        """
        Implementacion del metodo que entrena y devuelve (model, x_test_probs, x_train_probs, self.master_dict, model_weights)
        para clasificación multiclase
        """
        # --------------------------------------------------------------------------------------------
        # -- 0: Pinto la entrada
        # --------------------------------------------------------------------------------------------
        start_date: datetime.datetime = datetime.datetime.now()
        self.CT.IT.sub_intro_print(f"{self.class_name}.fit_and_get_model_and_results: Inicio de entrenamiento multiclase a las {start_date}...")
        self.CT.IT.info_print(f"Número de clases: {self.n_classes}", "light_blue")

        # --------------------------------------------------------------------------------------------
        # -- 1: Instancio el modelo y entreno
        # --------------------------------------------------------------------------------------------

        # ---- 1.1: Instancio el modelo y le asigno los parámetros para multiclase
        self.model: CatBoostClassifier = CatBoostClassifier(
            loss_function=self.problem_type,
            random_state=self.random_state,
            allow_writing_files=False,
            verbose=self.verbose,
            **self.hiperparams
        )

        # ---- 1.2: Realizo el entrenamiento
        self.model.fit(X=self.x_train, y=self.y_train)

        # ---- 1.3: Almaceno el modelo y el modulo del que proviene
        model_class_name: str = self.model.__class__.__name__
        model_module_name: str = self.model.__class__.__module__

        # ---- 1.4: Pinto el fin del entrenamiento y lo que ha tardado
        self.CT.IT.info_print(f"Entrenamiento completado a las {datetime.datetime.now()}. Ha tardado {datetime.datetime.now() - start_date}", "light_magenta")

        # --------------------------------------------------------------------------------------------
        # -- 2: Realizo las predicciones, mando a evaluar y retorno el diccionario de métricas
        # --------------------------------------------------------------------------------------------

        # ---- 2.1: Realizo las predicciones
        y_pred_train = self.model.predict(self.x_train_df)
        y_pred_test = self.model.predict(self.x_test_df)

        # ---- 2.2. Evalúo las metricas para multiclase
        EvaluateMulticlassClassifier(
            {
                "y_train": self.y_train,
                "y_eval": None,
                "y_test": self.y_test,
                "y_pred_train": y_pred_train,
                "y_pred_eval": None,
                "y_pred_test": y_pred_test,
                "target_col_name": self.target_col_name
            },
            self.model_name,
            self.metric,
            self.n_classes
        ).calculate_and_print_metrics()

        # --------------------------------------------------------------------------------------------
        # -- 3: Almaceno el modelo en su path con joblib.dump y obtengo los pesos
        # --------------------------------------------------------------------------------------------

        # ---- 3.1: Almacenamiento del modelo
        dump(self.model, f"{self.model_save_path}/{self.class_name}.joblib")

        # ---- 3.2: Obtencion de pesos (llamo al metodo polimorfeado self.get_weights)
        model_weights: List = self.get_weights(self.model)

        # ---- 3.3: Creacion de diccionario en el que asocio cada peso con su columna
        model_weights_dict: Dict[str, Any] = {
            col: weight for col, weight in zip(
                [z for z in self.x_train_df.columns],
                [float(x) for x in model_weights[0]]
            )
        }

        # --------------------------------------------------------------------------------------------
        # -- 4: Realizo las predicciones de probabilidad en test (matriz n_samples x n_classes) y las almaceno
        # --------------------------------------------------------------------------------------------

        # ---- 4.1: Obtengo una matriz con las probabilidades para cada clase de x_train y x_test
        x_train_probs: np.ndarray = self.model.predict_proba(self.x_train_df)
        x_test_probs: np.ndarray = self.model.predict_proba(self.x_test_df)

        # ---- 4.2: Creo un diccionario llamado probs_result_df en el que almaceno el y_test real y las probabilidades de cada clase
        probs_result_dict: Dict[str, Any] = {
            f'real_value_{self.target_col_name}': self.y_test[:, 0]
        }

        # Agregar probabilidades para cada clase
        for class_idx in range(self.n_classes):
            probs_result_dict[f'proba_class_{class_idx}'] = x_test_probs[:, class_idx]

        # ---- 4.3: Asigno probs_result_df a un dataframe para trabajarlo con mas facilidad
        probs_result_df: pd.DataFrame = pd.DataFrame(probs_result_dict)

        # --------------------------------------------------------------------------------------------
        # -- 5: Instancio ClassifierMetricsCalculations para obtener toda la info del resultado y rellenar el self.master_dict
        # --------------------------------------------------------------------------------------------

        # ---- 5.1: Obtengo el diccionario de metricas que proporciona ClassifierMetricsCalculations.run
        metrics_dict: dict = MulticlassClassifierMetricsCalculations(
            probs_result_df=probs_result_df,
            model_save_path=self.model_save_path,
            x_test_df=self.x_test_df,
            model=self.model,
            importances=model_weights,
            target_col_name=self.target_col_name,
            model_name=self.model_name,
            bins_dict=self.bins,
            n_classes=self.n_classes
        ).run()

        # ---- 5.2: Relleno el self.master_dict
        self.master_result_dict[f"{self.model_name}"]: dict = {}
        self.master_result_dict[f"{self.model_name}"]["columns"] = [z for z in self.x_train_df.columns]
        self.master_result_dict[f"{self.model_name}"]["target"] = self.target_col_name
        self.master_result_dict[f"{self.model_name}"]["best_params"] = self.hiperparams
        self.master_result_dict[f"{self.model_name}"]["metrics"] = metrics_dict
        self.master_result_dict[f"{self.model_name}"]["model_weights"] = model_weights_dict
        self.master_result_dict[f"{self.model_name}"]["model_class_name"] = model_class_name
        self.master_result_dict[f"{self.model_name}"]["model_module_name"] = model_module_name
        self.master_result_dict[f"{self.model_name}"]["n_classes"] = self.n_classes
        self.master_result_dict[f"{self.model_name}"]["model_version"] = f"{self.today_str_daye}_{self.current_train_version}"

        # --------------------------------------------------------------------------------------------
        # -- 6: Pinto y retorno la tupla (model, x_test_probs, x_train_probs, self.master_dict, model_weights)
        # --------------------------------------------------------------------------------------------

        # ---- 6.1: Pinto el final
        end_date = datetime.datetime.now()
        self.CT.IT.info_print(f"fit_and_get_model_and_results terminado a las {end_date}. Ha tardado {end_date - start_date}", "light_magenta")

        # ---- 6.2: Almaceno el self.master_dict
        self.save_metrics_dict_json(self.master_result_dict, self.model_save_path, "complete_train_result")

        # ---- 6.3: Retorno la tupla
        return self.model, x_test_probs, x_train_probs, self.master_result_dict, model_weights

    def get_weights(self, model) -> List:
        """
        Implementacion del metodo que devuelve una lista de ndarrays con los pesos del modelo
        """
        return [model.feature_importances_] if hasattr(model, "feature_importances_") else [None]

    def get_model_save_path(self) -> str:
        return self.model_save_path

    def execute_shap_analysis(self, sample: bool = True, num_features_to_show: int = 100, num_sample: int = 500) -> pd.DataFrame:
        """
        Metodo para ejecutar el analisis SHAP para modelos multiclase
        :return: DataFrame con análisis SHAP
        """
        try:
            return MlShapToolsMulticlass(
                self.x_test_df,
                self.model_name,
                self.model_save_path,
                self.model,
                self.n_classes,  # PARÁMETRO NUEVO CRÍTICO
                sample,
                num_features_to_show,
                num_sample
            ).run()
        except Exception as e:
            self.CT.IT.info_print(f"No se puede realizar el SHAP: {e}", "light_red")
            return pd.DataFrame()

    # </editor-fold>

    # <editor-fold desc="Implementacion de propiedades abstractas   --------------------------------------------------------------------------------------------------------------">

    @property
    def verbose(self):
        verbose_dict: dict = {'show_all': 1, 'show_basics': 0, 'dont_show': 0}
        return verbose_dict[self._verbose]

    @property
    def metric(self):
        valid_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 'f1_micro', 'balanced_accuracy', 'roc_auc_ovr']
        if self._metric not in valid_metrics:
            raise ValueError(f'Invalid metric: {self._metric}. Must be one of {valid_metrics}')
        return self._metric

    @property
    def problem_type(self):
        if self._problem_type not in ['multiclass', 'MultiClass']:
            raise ValueError(f'Invalid problem_type: {self._problem_type}. Must be multiclass, MultiClass')
        return self._problem_type

    # </editor-fold>
    @problem_type.setter
    def problem_type(self, value):
        self._problem_type = value

    # </editor-fold>

    # <editor-fold desc="Métodos específicos para multiclase   ------------------------------------------------------------------------------------------------------------------">

    def get_class_distribution(self) -> Dict[str, Any]:
        """
        Metodo específico para obtener la distribución de clases en los datos de entrenamiento y test
        :return: Diccionario con distribución de clases
        """
        train_unique, train_counts = np.unique(self.y_train, return_counts=True)
        test_unique, test_counts = np.unique(self.y_test, return_counts=True)

        distribution = {
            "train_distribution": {f"class_{int(cls)}": int(count) for cls, count in zip(train_unique, train_counts)},
            "test_distribution": {f"class_{int(cls)}": int(count) for cls, count in zip(test_unique, test_counts)},
            "n_classes": self.n_classes
        }

        self.CT.IT.info_print("Distribución de clases:", "light_blue")
        self.CT.IT.info_print(f"Entrenamiento: {distribution['train_distribution']}", "light_blue")
        self.CT.IT.info_print(f"Test: {distribution['test_distribution']}", "light_blue")

        return distribution

    def predict_proba_per_class(self, x: pd.DataFrame) -> pd.DataFrame:
        """
        Metodo para obtener probabilidades por clase con nombres de columnas descriptivos
        :param x: DataFrame con features
        :return: DataFrame con probabilidades por clase
        """
        probas = self.model.predict_proba(x)
        proba_df = pd.DataFrame(probas, columns=[f'proba_class_{i}' for i in range(self.n_classes)])
        return proba_df

    # </editor-fold>