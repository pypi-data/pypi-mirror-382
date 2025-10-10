from ddi_fw.ml.model_wrapper import Result
from ddi_fw.ml.pytorch_wrapper import PTModelWrapper
from ddi_fw.ml.tensorflow_wrapper import TFModelWrapper
from ddi_fw.utils.package_helper import get_import
import numpy as np
from ddi_fw.ml.evaluation_helper import evaluate

# import tf2onnx
# import onnx

import itertools
import ddi_fw.utils as utils

# tf.random.set_seed(1)
# np.random.seed(2)
# np.set_printoptions(precision=4)


class MultiModalRunner:
    # todo model related parameters to config
    def __init__(self, library, multi_modal, default_model, tracking_service):
        self.library = library
        self.multi_modal = multi_modal
        self.default_model = default_model
        self.tracking_service = tracking_service
        self.result = Result()

    # def _mlflow_(self, func: Callable):
    #     if self.use_mlflow:
    #         func()

    def set_data(self, items, train_idx_arr, val_idx_arr, y_test_label):
        self.items = items
        self.train_idx_arr = train_idx_arr
        self.val_idx_arr = val_idx_arr
        self.y_test_label = y_test_label

    def __create_model(self, library):
        if library == 'tensorflow':
            return TFModelWrapper
        elif library == 'pytorch':
            return PTModelWrapper
        else:
            raise ValueError(
                "Unsupported library type. Choose 'tensorflow' or 'pytorch'.")

    # TODO check single_results, 1d,2d ...
    def __predict(self, single_results):
        item_dict = {t[0]: t for t in self.items}
        if self.default_model is None and not self.multi_modal:
            raise Exception(
                "Default model and multi modal cannot be None at the same time")

        if self.multi_modal:
            for m in self.multi_modal:
                name = m.get('name')
                # input_type = m.get('input_type')
                input = m.get('input')
                inputs = m.get('inputs')
                if m.get("model_type") is None:
                    model_type = self.default_model.get("model_type")
                    kwargs = self.default_model.get('params')
                else:
                    model_type = get_import(m.get("model_type"))
                    kwargs = m.get('params')

                if model_type is None:
                    raise Exception(
                        "model_type cannot be None, it should be defined in multi_modal or default_model")

                T = self.__create_model(self.library)
                single_modal = T(self.date, name, model_type,
                                 tracking_service=self.tracking_service,  **kwargs)

                if input and inputs:
                    raise ValueError(
                        "Only one of 'input' or 'inputs' should be defined.")
                if not input and not inputs:
                    raise ValueError(
                        "At least one of 'input' or 'inputs' must be defined.")
                    
                if input and not isinstance(input, str):
                    raise ValueError(
                        "'input' should be a single string. For multiple inputs, use 'inputs'.")

                # Get stacking and reshaping config
                processor_type = m.get("processor", "ddi_fw.datasets.processor.DefaultInputProcessor")
                processor = get_import(processor_type)  # Ensure the processor type is valid
                force_stack = m.get("force_stack", True)
                reshape_dims = m.get("reshape")
                train_data, train_label, test_data, test_label = None, None, None, None
                
                # Prepare processing config with all context
                processing_config = {
                    "force_stack": force_stack,
                    "reshape": reshape_dims
                }
                
                # --- SINGLE INPUT CASE ---
                if input:
                    item = item_dict[input]
                    train_data = item[1]
                    train_label = item[2]
                    test_data = item[3]
                    test_label = item[4]
                   

                    # # Optional: force stack single input to simulate extra dimension
                    # if force_stack:
                    #     train_data = np.expand_dims(train_data, axis=1)
                    #     test_data = np.expand_dims(test_data, axis=1)

                # --- MULTIPLE INPUTS CASE ---
                elif inputs:
                    filtered_dict = {k: item_dict[k]
                                     for k in inputs if k in item_dict}
                    if not filtered_dict:
                        raise ValueError(
                            f"No matching inputs found in item_dict for: {inputs}")

                    first_input = next(iter(filtered_dict.values()))
                    train_data = [f[1] for f in filtered_dict.values()]
                    test_data = [f[3] for f in filtered_dict.values()]
                    train_label = first_input[2]
                    test_label = first_input[4]

                    # # Stack across inputs
                    # if len(train_data_list) == 1:
                    #     train_data = train_data_list[0]
                    #     test_data = test_data_list[0]
                   
                    # if force_stack:
                    #     train_data = np.stack(train_data_list, axis=1)
                    #     test_data = np.stack(test_data_list, axis=1)
                        
                    # else:
                    #     # train_data = np.concatenate(train_data_list, axis=0)
                    #     # test_data = np.concatenate(test_data_list, axis=0)
                    #     train_data = np.array(train_data_list).T
                    #     test_data = np.array(test_data_list).T
                else:
                    raise Exception("check configurations")


                train_data = processor().process2(train_data, processing_config)
                test_data = processor().process2(test_data, processing_config)
                # # --- OPTIONAL: Reshape if needed ---
                # if reshape_dims:
                #     train_data = train_data.reshape((-1, *reshape_dims))
                #     test_data = test_data.reshape((-1, *reshape_dims))

           
                # --- Finalize ---
                single_modal.set_data(
                    self.train_idx_arr, self.val_idx_arr,
                    train_data, train_label,
                    test_data, test_label
                )

                logs, metrics, prediction = single_modal.fit_and_evaluate()
                self.result.add_metric(name, metrics)
                single_results[name] = prediction
        else:  # TODO default model maybe?
            print("Default model will be used")
            if self.default_model is None:
                raise Exception(
                    "Default model cannot be None if multi_modal is not defined")
            if self.default_model.get("model_type") is None:
                raise Exception(
                    "model_type cannot be None, it should be defined in default_model")

            model_type = get_import(self.default_model.get("model_type"))
            kwargs = self.default_model.get('params')
            for item in self.items:
                name = item[0]
                T = self.__create_model(self.library)
                single_modal = T(self.date, name, model_type,
                                 tracking_service=self.tracking_service,  **kwargs)
                single_modal.set_data(
                    self.train_idx_arr, self.val_idx_arr, item[1], item[2], item[3], item[4])

                logs, metrics, prediction = single_modal.fit_and_evaluate()
                self.result.add_metric(name, metrics)
                single_results[name] = prediction

    def predict(self, combinations: list = [], generate_combinations=False):
        self.prefix = utils.utc_time_as_string()
        self.date = utils.utc_time_as_string_simple_format()
        # sum = np.zeros(
        #     (self.y_test_label.shape[0], self.y_test_label.shape[1]))
        single_results = dict()

        if generate_combinations:
            l = [item[0] for item in self.items]
            combinations = []
            for i in range(2, len(l) + 1):
                combinations.extend(list(itertools.combinations(l, i)))  # all

        def _f():
            self.__predict(single_results)
            if combinations:
                self.evaluate_combinations(single_results, combinations)

        if self.tracking_service:
            self.tracking_service.run(
                run_name=self.prefix, description="***", func=_f, nested_run=False)
        else:
            self.__predict(single_results)
            if combinations:
                self.evaluate_combinations(single_results, combinations)
        # TODO: sum'a gerek yok
        return self.result

    def evaluate_combinations(self, single_results, combinations):
        for combination in combinations:
            combination_descriptor = '-'.join(combination)
            if self.tracking_service:
                def evaluate_combination(artifact_uri=None):
                    self.__evaluate_combinations(
                        single_results, combination, combination_descriptor, artifact_uri
                    )

                self.tracking_service.run(run_name=combination_descriptor,
                                          description="***",
                                          nested_run=True,
                                          func=evaluate_combination)

                # with mlflow.start_run(run_name=combination_descriptor, description="***", nested=True) as combination_run:
                #     self.__evaluate_combinations(
                #         single_results, combination, combination_descriptor, combination_run.info.artifact_uri)
            else:
                self.__evaluate_combinations(
                    single_results, combination, combination_descriptor, None)

    def __evaluate_combinations(self, single_results, combination, combination_descriptor, artifact_uri):
        prediction = np.zeros(
            (self.y_test_label.shape[0], self.y_test_label.shape[1]))
        for item in combination:
            prediction = prediction + single_results[item]
        prediction = utils.to_one_hot_encode(prediction)
        logs, metrics = evaluate(
            actual=self.y_test_label, pred=prediction, info=combination_descriptor)
        if self.tracking_service:
            self.tracking_service.log_metrics(logs)
        metrics.format_float()
        # TODO path bulunamadı hatası aldık
        if artifact_uri:
            print(
                f'combination_artifact_uri:{artifact_uri}')
            utils.compress_and_save_data(
                metrics.__dict__, artifact_uri, f'{self.date}_metrics.gzip')
        # self.result.add_log(combination_descriptor,logs)
        # self.result.add_metric(combination_descriptor,metrics)
