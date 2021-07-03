from zipfile import ZipFile
from glob import glob
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark.sql.functions import lit
import shutil
import os
import pandas as pd

def extract_all(src, dest, metadata_dir):
    zipfiles = glob(f'{src}/*.zip')
    for zipfile in zipfiles:
        year = zipfile.split('_')[-1].split('.')[0]
        with ZipFile(zipfile) as f:
            f.extractall(src)

        _dirs = glob(os.path.join(src, "*"))
        for d in _dirs:
            if 'DADOS' in d:
                data = os.path.join(d, '*.csv')
                data_file = glob(data)[0]
                if not os.path.exists(dest):
                    os.mkdir(dest)
                shutil.move(data_file, os.path.join(dest, f'dados_{year}.csv'))
            
            elif 'DOC' in d:
                metadata = os.path.join(d, '*.xls')
                metadata_file = glob(metadata)[0]
                if not os.path.exists(metadata_dir):
                    os.mkdir(metadata_dir)
                shutil.move(metadata_file, os.path.join(metadata_dir, f'dicionario_dados_{year}.xls'))


class Dataset:
    def __init__(self, path, catalog, year, merge_mapping=None):
        '''Returns a Censo Ensino Superior dataset.
        
        :param path: path of dataset
        :param catalog: path of data catalog following the pattern path#sheet_name
        :param year: year of the census.
        '''
        self.path = path
        self.catalog = catalog
        self.year = year
        self.merge_mappinng = merge_mapping
        #self.schema = self._schema()
        self.data = self._build_spark_df()
        
    def __str__(self):
        return self.data.show()
    
    def __repr__(self):
        return self.data.show()
    
    def _extract_metadata_from_excel(self):
        '''Returns dataset metadata from an excel file.
        '''
        path, sheet = self.catalog.split('#')
        print(path)
        print(sheet)
        current_names = ['NOME DA VARIÁVEL', 'TIPO']
        new_names = ['nome_variavel', 'tipo']
        columns = dict(zip(current_names, new_names))
        
        df = pd.read_excel(path, header=1)#, sheet_name=sheet)
        df = df.rename(columns=columns)
        df = df[['nome_variavel', 'tipo']].apply(lambda val: val.str.upper())
        df = df.dropna()
        return df

    def _schema_from_pandas(self, metadata):
        '''Returns a spark dataframe schema from pandas dataframe
        '''
        schema_draft = {'type': 'struct'}
        
        fields = []
        for _, row in metadata.iterrows():
            field = {}
            field['name'] = row['nome_variavel']
            field['type'] = 'integer' if row['tipo'] == 'NUM' else 'string'
            field['nullable'] = True
            field['metadata'] = {}
            fields.append(field)
        
        schema_draft['fields'] = fields
        schema = StructType.fromJson(schema_draft)
        return schema
    
    def _schema(self):
        '''Returns the schema of dataset.
        '''
        metadata = self._extract_metadata_from_excel()
        schema = self._schema_from_pandas(metadata)
        return schema

    def _get_spark_session(self):
        '''Returns a spark session.
        '''
        spark = SparkSession.builder.getOrCreate()
        return spark
    
    def _build_spark_df(self):
        '''Build the dataset as a spark dataframe.
        '''
        spark = self._get_spark_session()
        df = spark.read.csv(self.path, header=True, sep=';', encoding='ISO-8859-1')#, schema=self.schema)
        return df
    
    def _rename_columns(self):
        if self.year != 2010:
            if self.merge_mapping:
                pass
            else:
                print('')
    
    def _create_columns(self):
        if 'NU_ANO' not in self.data.columns:
            self.data = self.data.withColumn('NU_ANO', lit(self.year))
            
    def _normalize(self):
        self._create_columns()
        #self._rename_columns()
    
    def _to_parquet(self, path, partition_by, mode):
        '''Write dataset as parquet.
        '''
        if partition_by:
            self.data.write.partitionBy(partition_by).mode(mode).parquet(path)
        else:
            self.data.write.mode(mode).parquet(path)
    
    def save(self, path, partition_by=None, mode='append', _format='parquet'):
        '''Save dataset.
        '''
        formats = {
            'parquet': self._to_parquet,
        }
        save_as = formats[_format]
        
        self._normalize()
        save_as(path, partition_by, mode)


def parse(path, catalog, year, dest):
    dataset = Dataset(path, catalog, year)
    dataset.save(os.path.join(dest, 'enade/' + str(year)), 'NU_ANO')