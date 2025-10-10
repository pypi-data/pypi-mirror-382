import abc
from collections import defaultdict
import glob
import logging
from typing import Any, Dict, List, Optional, Type
# import chromadb
# from chromadb.api.types import IncludeEnum
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, computed_field
from ddi_fw.datasets.dataset_splitter import DatasetSplitter
from ddi_fw.langchain.faiss_storage import BaseVectorStoreManager
from ddi_fw.utils.utils import create_folder_if_not_exists


try:
    from ddi_fw.vectorization import SimilarityMatrixGenerator, VectorGenerator
except ImportError:
    raise ImportError(
        "Failed to import vectorization module. Ensure that the module exists and is correctly installed. ")

try:
    from ddi_fw.langchain.embeddings import PoolingStrategy
except ImportError:
    raise ImportError(
        "Failed to import langchain.embeddings module. ")


def stack(df_column):
    return np.stack(df_column.values)


def generate_vectors(df, columns):
    vectorGenerator = VectorGenerator(df)
    generated_vectors = vectorGenerator.generate_feature_vectors(
        columns)
    return generated_vectors


def generate_sim_matrices_new(df, generated_vectors, columns, key_column="id"):
    jaccard_sim_dict = {}
    sim_matrix_gen = SimilarityMatrixGenerator()

    for column in columns:
        # key = '2D_'+column
        key = column
        jaccard_sim_dict[column] = sim_matrix_gen.create_jaccard_similarity_matrices(
            generated_vectors[key])

    similarity_matrices = {}
    keys = df[key_column].to_list()
    new_columns = {}
    for idx in range(len(keys)):
        new_columns[idx] = keys[idx]
    for column in columns:
        new_df = pd.DataFrame.from_dict(jaccard_sim_dict[column])
        new_df = new_df.rename(index=new_columns, columns=new_columns)
        similarity_matrices[column] = new_df
    return similarity_matrices


class BaseDataset(BaseModel, abc.ABC):
    dataset_name: str
    index_path: Optional[str] = None
    dataset_splitter_type: Type[DatasetSplitter]
    class_column: str = 'class'
    dataframe: Optional[pd.DataFrame] = None
    X_train: Optional[np.ndarray] = None
    X_test: Optional[np.ndarray] = None
    y_train: Optional[np.ndarray] = None
    y_test: Optional[np.ndarray] = None
    train_indexes: Optional[pd.Index] = None
    test_indexes: Optional[pd.Index] = None
    train_idx_arr: Optional[List[np.ndarray]] = None
    val_idx_arr: Optional[List[np.ndarray]] = None
    columns: List[str] = []
    additional_config: Optional[Dict[str, Any]] = None
    input_processing: Optional[List[Dict[str, Any]]] = None

    class Config:
        arbitrary_types_allowed = True
        
    def process_input_data(self,data, processing_config=None):
        
        if not processing_config:
            return data
        if processing_config.get("flatten", False):
            print("Flattening data...")
            data = np.array(data).flatten()
            print(f"Data shape after flattening: {data.shape}")
        
        if processing_config.get("stack", False):
            print("Stacking data...")
            data = np.stack(data)
            print(f"Data shape after stacking: {data.shape}")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        # if processing_config.get("flatten", False):
        #     data = np.stack(data.flatten().tolist())
        # Ensure we start with a NumPy array
       

        # Normalize input
        if processing_config.get("normalize", False):
            data = data.astype(np.float32)
            max_val = np.max(data)
            if max_val > 1:
                data /= max_val

        # Reshape input (for images etc.)
        if "reshape" in processing_config:
            try:
                target_shape = tuple(processing_config["reshape"])
                data = data.reshape((-1, *target_shape))
            except Exception as e:
                raise ValueError(f"Reshape failed for data with shape {data.shape}: {e}")


        return data

    # TODO columns yoksa tüm feature'lar alınıyor, bu pipeline'da nasıl yapılacak?
    # TODO processor sınıfı kullanılsın
    def produce_inputs(self):
        # Grouping the list by "column" key
        grouped_data = defaultdict(dict)

        if self.input_processing:
            for item in self.input_processing:
                grouped_data[item["column"]] = item
                
        items = []
        if self.X_train is None or self.X_test is None:
            raise Exception("There is no data to produce inputs")
        y_train_label, y_test_label = np.array(
            self.y_train), np.array(self.y_test)

        if self.columns is None or len(self.columns) == 0 or len(self.columns) == 1:
            # If no columns or only one column are provided, do not change the data
            # and use the entire dataset as a single input.
            column = self.columns[0] if self.columns else 'default'
            train_data, test_data = self.X_train[:, :], self.X_test[:, :]
            processing_config = grouped_data[column]
            train_data = self.process_input_data(train_data, processing_config)
            test_data = self.process_input_data(test_data, processing_config)
            # train_data,test_data = np.stack(train_data.flatten().tolist()), np.stack(test_data.flatten().tolist())
            items.append([f'{column}', np.nan_to_num(train_data),
                          y_train_label, np.nan_to_num(test_data), y_test_label])
        else:
            for index, column in enumerate(self.columns):
                processing_config = grouped_data[column]
                train_data, test_data = self.X_train[:,
                                                     index], self.X_test[:, index]
                #TODO üstteki satır ile alttaki tek satır olsun, tolist() ile numpy array'e çevrilmesin, numpy array zaten ama uyarı verdiği için böyle
                train_data = self.process_input_data(train_data, processing_config)
                test_data = self.process_input_data(test_data, processing_config)
                # train_data,test_data = np.stack(train_data.tolist()), np.stack(test_data.tolist())
                items.append([f'{column}', np.nan_to_num(train_data),
                              y_train_label, np.nan_to_num(test_data), y_test_label])

                # items.append([f'{column}_embedding', train_data,
                #             y_train_label, test_data, y_test_label])
        return items
 

    @computed_field
    @property
    def dataset_splitter(self) -> DatasetSplitter:
        return self.dataset_splitter_type()

    def set_dataframe(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    @abc.abstractmethod
    def prep(self):
        """Prepare the dataset. This method should be overridden in subclasses."""
        

    def handle_mixins(self):
        """Handle mixin-specific logic."""
        if isinstance(self, TextDatasetMixin):
            self.process_text()
        # if isinstance(self, ImageDatasetMixin):
        #     self.process_image_data()
        # Add other mixin-specific logic here
        
    def load(self):
        """
        Load the dataset. If X_train, y_train, X_test, and y_test are already provided,
        skip deriving them. Otherwise, derive them from the dataframe and indices.
        """
        self.handle_mixins()  # Centralized mixin handling
        self.prep()  # Prepare the dataset

        if self.X_train is not None or self.y_train is not None or self.X_test is not None or self.y_test is not None:
            # Data is already provided, no need to calculate
            logging.info(
                "X_train, y_train, X_test, and y_test are already provided. Skipping calculation.")
            return
            # return self.X_train, self.X_test, self.y_train, self.y_test, self.train_indexes, self.test_indexes, self.train_idx_arr, self.val_idx_arr

        if self.index_path is None:
            raise Exception(
                "There is no index path. Please call split_dataset or provide indices.")

        if self.dataframe is None:
            raise Exception("There is no dataframe to derive data from.")

        try:
            train_idx_all, test_idx_all, train_idx_arr, val_idx_arr = self.__get_indexes__(
                self.index_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Index files not found: {e.filename}")
        
        # train = self.dataframe[self.dataframe.index.isin(train_idx_all)]
        # test = self.dataframe[self.dataframe.index.isin(test_idx_all)]
        columns = self.columns + [self.class_column] 
        train = self.dataframe.loc[self.dataframe.index.isin(train_idx_all), columns]
        test = self.dataframe.loc[self.dataframe.index.isin(test_idx_all), columns]
        X_train = train.drop(self.class_column, axis=1)
        X_train = train.drop(self.class_column, axis=1)
        y_train = train[self.class_column]
        X_test = test.drop(self.class_column, axis=1)
        y_test = test[self.class_column]

        self.X_train = np.array(X_train)
        # self.y_train = np.array(y_train)
        self.y_train = np.array(y_train.tolist())
        self.X_test = np.array(X_test)
        # self.y_test = np.array(y_test)
        self.y_test = np.array(y_test.tolist())

        self.train_indexes = X_train.index
        self.test_indexes = X_test.index
        self.train_idx_arr = train_idx_arr
        self.val_idx_arr = val_idx_arr

        # Dataframe to numpy array conversion

        # return self.X_train, self.X_test, self.y_train, self.y_test, self.train_indexes, self.test_indexes, self.train_idx_arr, self.val_idx_arr

    def __get_indexes__(self, path):
        train_index_path = path+'/train_indexes.txt'
        test_index_path = path+'/test_indexes.txt'
        train_fold_files = f'{path}/train_fold_*.txt'
        val_fold_files = f'{path}/validation_fold_*.txt'
        train_idx_arr = []
        val_idx_arr = []
        with open(train_index_path, 'r', encoding="utf8") as f:
            train_idx_all = [int(r) for r in f.readlines()]
        with open(test_index_path, 'r', encoding="utf8") as f:
            test_idx_all = [int(r) for r in f.readlines()]

        for filepath in glob.glob(train_fold_files):
            with open(filepath, 'r', encoding="utf8") as f:
                train_idx = [int(r) for r in f.readlines()]
                train_idx_arr.append(train_idx)
        for filepath in glob.glob(val_fold_files):
            with open(filepath, 'r', encoding="utf8") as f:
                val_idx = [int(r) for r in f.readlines()]
                val_idx_arr.append(val_idx)
        return train_idx_all, test_idx_all, train_idx_arr, val_idx_arr

    def __save_indexes__(self, path, filename, indexes):
        create_folder_if_not_exists(path)
        file_path = path + '/'+filename
        str_indexes = [str(index) for index in indexes]
        with open(file_path, 'w') as f:
            f.write('\n'.join(str_indexes))

    def split_dataset(self, save_indexes: bool = False):
        """
        Split the dataset into training and testing sets. This method is only available
        if a dataframe exists. If X_train, y_train, X_test, and y_test are already present,
        raise an error.
        """
        if self.X_train is not None or self.X_test is not None:
            raise Exception(
                "X_train and X_test are already present. Splitting is not allowed.")

        self.prep()
        if self.dataframe is None:
            raise Exception("There is no dataframe to split.")

        save_path = self.index_path

        X = self.dataframe.drop(self.class_column, axis=1)
        y = self.dataframe[self.class_column]

        X_train, X_test, y_train, y_test, X_train.index, X_test.index, train_idx_arr, val_idx_arr = self.dataset_splitter.split(
            X=X, y=y)
        self.X_train = np.array(X_train)
        self.X_test = np.array(X_test)
        self.y_train = np.array(y_train.tolist())
        self.y_test = np.array(y_test.tolist())
        self.train_indexes = X_train.index
        self.test_indexes = X_test.index
        self.train_idx_arr = train_idx_arr
        self.val_idx_arr = val_idx_arr

        if save_indexes:
            # train_pairs = [row['id1'].join(',').row['id2'] for index, row in X_train.iterrows()]
            self.__save_indexes__(
                save_path, 'train_indexes.txt', self.train_indexes.values)
            self.__save_indexes__(
                save_path, 'test_indexes.txt',  self.test_indexes.values)

            for i, (train_idx, val_idx) in enumerate(zip(train_idx_arr, val_idx_arr)):
                self.__save_indexes__(
                    save_path, f'train_fold_{i}.txt', train_idx)
                self.__save_indexes__(
                    save_path, f'validation_fold_{i}.txt', val_idx)

        # return X_train, X_test, y_train, y_test, folds


class TextDatasetMixin(BaseModel):
    embedding_dict: Dict[str, Any] | None = Field(
        default_factory=dict, description="Dictionary for embeddings")
    pooling_strategy: PoolingStrategy | None = None
    column_embedding_configs: Optional[List] = None
    vector_store_manager: BaseVectorStoreManager| None = None  # <-- NEW

    vector_db_persist_directory: Optional[str] = None
    vector_db_collection_name: Optional[str] = None
    _embedding_size: int

    @computed_field
    @property
    def embedding_size(self) -> int:
        return self._embedding_size

    class Config:
        arbitrary_types_allowed = True
 
    def __calculate_embedding_size(self):
        if not self.embedding_dict:
            raise ValueError("Embedding dictionary is not initialized, embedding size cannot be calculated.")
            
        key, value = next(iter(self.embedding_dict.items()))
        self._embedding_size = value[next(iter(value))][0].shape[0]

    def process_text(self):
        logging.info("Processing text data...")
 
      
        if not self.embedding_dict:
            if self.vector_store_manager is not None:
                self.embedding_dict = self.vector_store_manager.initialize_embedding_dict()
            else:
                raise ValueError("Either embedding_dict or vector_store_manager must be provided for text processing.")
        self.__calculate_embedding_size()
         


# class ImageDatasetMixin(BaseModel):
#     image_size: tuple[int, int] = Field(default=(224, 224))
#     augmentations: list[str] = Field(default_factory=list)

#     def process_image_data(self):
#         print(
#             f"Processing image data with size {self.image_size} and augmentations {self.augmentations}...")
