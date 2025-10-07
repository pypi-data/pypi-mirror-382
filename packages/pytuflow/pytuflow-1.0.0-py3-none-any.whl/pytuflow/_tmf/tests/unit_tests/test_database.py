from pathlib import Path

import pandas as pd
import pytest

from tmf.tuflow_model_files.inp.inputs import Inputs
from tmf.tuflow_model_files.db.bc_dbase import BCDatabase
from tmf.tuflow_model_files.db.soil import SoilDatabase
from tmf.tuflow_model_files.db.pit_inlet import PitInletDatabase
from tmf.tuflow_model_files.db.rf import RainfallDatabase
from tmf.tuflow_model_files.db.db_build_state import DatabaseBuildState
from tmf.tuflow_model_files.scope import Scope, ScopeList
from tmf.tuflow_model_files.context import Context
from tmf.tuflow_model_files.utils.commands import Command
from tmf.tuflow_model_files.inp.get_input_class import get_input_class
from tmf.tuflow_model_files.settings import TCFConfig
from tmf.tuflow_model_files.event import EventDatabase
from tmf.tuflow_model_files.db.mat import get_material_database_class


def test_bcdbase_init_empty():
    db = BCDatabase()
    assert db.fpath is None
    assert db.df.columns.tolist() == ['Source', 'Column 1', 'Column 2', 'Add Col 1', 'Mult Col 2', 'Add Col 2', 'Column 3', 'Column 4']


def test_database_init():
    p = Path(__file__).parent / 'csv_database.csv'
    with p.open('w') as f:
        f.write('a,b,c\n1,2,3')
    try:
        db = BCDatabase(p.resolve())
        assert db._driver is not None
        assert db.df is not None
    except Exception as e:
        raise e
    finally:
        p.unlink()


def test_bc_dbase_init():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001.csv'
    db = BCDatabase(p, None, None)
    assert len(db.entries['fc01'].files) == 1
    assert len(db.entries['fc01'].files[0].parts) > 1


def test_bc_dbase_events_init():
    p = './tests/unit_tests/test_datasets/models/bc_dbase_events/bc_dbase_EG11_004.csv'
    event_db = EventDatabase()
    event_db['Q100'] = {'_event1_': '100yr'}
    event_db['PMF'] = {'_event1_': 'PMFyr'}
    event_db['2hr'] = {'_event2_': '2hr'}
    event_db['4hr'] = {'_event2_': '4hr'}
    config = TCFConfig(event_db=event_db)
    db = BCDatabase(p, config, None)
    source = Path('./tests/unit_tests/test_datasets/models/bc_dbase_events/EG16_100yr2hr.csv').resolve()
    assert len(sum([x.files for x in db.entries.values()], [])) == 4
    assert not any(x.has_missing_files for x in db.entries.values())
    assert db.entries['fc01'].file_scope(source) == ScopeList([Scope('Event Define', '100yr', '_event1_'), Scope('Event Define', '2hr', '_event2_')])


def test_database_file_scope():
    p = './tests/unit_tests/test_datasets/models/bc_dbase_variables/bc_dbase_EG11_004.csv'
    db = BCDatabase(p)
    source = Path('./tests/unit_tests/test_datasets/models/bc_dbase_variables/EG16_100yr2hr.csv').resolve()
    assert len(sum([x.files for x in db.entries.values()], [])) == 2
    assert db.entries['fc01'].file_scope(source) == ScopeList([Scope('Variable', '<<EVENT>>')])


def test_bc_dbase_value():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001.csv'
    db = BCDatabase(p, None, None)
    val = db.value('fc01')
    assert not val.empty
    assert val.columns.tolist() == ['inflow_FC01']
    assert val.index.name == 'inflow_time_hr'
    val = db.value('fc02')
    assert val == 10.


def test_bc_dbase_value_time_add():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001_Time_Add.csv'
    db = BCDatabase(p, None, None)
    val = db.value('fc01')
    assert val.index.min() == 100


def test_bc_dbase_value_add():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001_Value_Add.csv'
    db = BCDatabase(p, None, None)
    val = db.value('fc01')
    assert val.loc[:,'inflow_FC01'].min() == 100
    val = db.value('fc02')
    assert val == 110.


def test_bc_dbase_value_factor():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001_Value_Factor.csv'
    db = BCDatabase(p, None, None)
    val = db.value('fc01')
    assert val.loc[:,'inflow_FC01'].max() > 900
    val = db.value('fc02')
    assert val == 1000.


def test_bc_dbase_events_value_fail():
    p = './tests/unit_tests/test_datasets/models/bc_dbase_events/bc_dbase_EG11_004.csv'
    event_db = EventDatabase()
    event_db['Q100'] = {'_event1_': '100yr'}
    event_db['PMF'] = {'_event1_': 'PMFyr'}
    event_db['2hr'] = {'_event2_': '2hr'}
    event_db['4hr'] = {'_event2_': '4hr'}
    config = TCFConfig(event_db=event_db)
    db = BCDatabase(p, config, None)
    with pytest.raises(ValueError):
        db.value('fc01')


def test_bc_dbase_variable_value_fail():
    p = './tests/unit_tests/test_datasets/models/bc_dbase_variables/bc_dbase_EG11_004.csv'
    db = BCDatabase(p)
    with pytest.raises(ValueError):
        db.value('fc01')


def test_bc_dbase_value_ts1_group():
    p = './tests/unit_tests/test_datasets/ts1/bc_dbase.csv'
    db = BCDatabase(p)
    df = db.value('TP01|local')
    assert not df.empty


def test_bc_dbase_modify_df():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001.csv'
    db = BCDatabase(p)

    db._df.loc['FC01', 'Source'] = 'EG17_001.csv'
    assert not db.dirty
    db._df.loc['FC01', 'Source'] = 'EG00_001.csv'

    db.df.loc['FC01', 'Source'] = 'EG17_001.csv'
    assert db.df.loc['FC01', 'Source'] == 'EG17_001.csv'
    assert db.entries['fc01'][1].value == 'EG17_001.csv'
    assert db.dirty

    db.df.loc['FC01', 'Source'] = 'EG11_001.csv'
    assert db.df.loc['FC01', 'Source'] == 'EG11_001.csv'
    assert db.entries['fc01'][1].value == 'EG11_001.csv'
    assert db.dirty

    db.undo()
    assert db.df.loc['FC01', 'Source'] == 'EG17_001.csv'
    assert db.entries['fc01'][1].value == 'EG17_001.csv'
    assert db.dirty

    db.undo()
    assert db.df.loc['FC01', 'Source'] == 'EG00_001.csv'
    assert db.entries['fc01'][1].value == 'EG00_001.csv'
    assert not db.dirty


def test_bc_dbase_write():
    p = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_001.csv'
    db = BCDatabase(p)
    db.df.loc['FC01', 'Source'] = 'EG17_001.csv'
    db.write('002')
    p2 = './tests/unit_tests/test_datasets/models/shp/bc_dbase/bc_dbase_EG00_002.csv'
    assert Path(p2).exists()
    Path(p2).unlink()
    assert not db.dirty


def test_mat_database():
    p = './tests/unit_tests/test_datasets/models/shp/model/Materials.csv'
    db = get_material_database_class(Path(p))(p)
    assert db.df.shape == (8, 3)
    assert db.value(2) == 0.022
    val = db.value(1)
    assert isinstance(val, pd.DataFrame)
    assert val.shape == (4, 2)
    val = db.value(99)
    assert isinstance(val, pd.DataFrame)
    assert val.shape == (4, 2)
    val = db.value(100)
    assert isinstance(val, pd.DataFrame)
    assert val.shape == (2, 1)


def test_mat_tmf_with_header():
    p = './tests/unit_tests/test_datasets/with_header.tmf'
    db = get_material_database_class(Path(p))(p)
    assert db.df.shape == (9, 1)
    assert db.df.index.name == 'Material ID'
    assert db.df.columns.tolist() == ['Manning\'s n']


def test_mat_tmf_no_header():
    p = './tests/unit_tests/test_datasets/no_header.tmf'
    db = get_material_database_class(Path(p))(p)
    assert db.df.shape == (9, 1)
    assert db.df.index.name == 'Material ID'
    assert db.df.columns.tolist() == ['Manning\'s n']


def test_mat_tmf_tough():
    p = './tests/unit_tests/test_datasets/tough.tmf'
    db = get_material_database_class(Path(p))(p)
    assert db.df.shape == (17, 1)
    assert db.df.index.name == 'Material ID'
    assert db.df.columns.tolist() == ['Manning\'s n']


def test_mat_tmf_final_boss():
    p = './tests/unit_tests/test_datasets/the_final_boss.tmf'
    db = get_material_database_class(Path(p))(p)
    assert db.df.shape == (22, 7)
    assert db.df.index.name == 'Material ID'
    assert db.df.columns.tolist() == ['Manning\'s n', 'IL', 'CL', 'y1', 'n1', 'y2', 'n2']
    assert db.value(6) == 0.03
    val = db.value(22)
    assert isinstance(val, pd.DataFrame)
    assert val.shape == (2, 2)


def test_mat_tmf_write():
    p = './tests/unit_tests/test_datasets/with_header.tmf'
    db = get_material_database_class(Path(p))(p)
    db.write('001')
    assert Path('./tests/unit_tests/test_datasets/with_header_001.tmf').exists()
    try:
        with Path('./tests/unit_tests/test_datasets/with_header_001.tmf').open() as f:
            line = f.readline().strip()
            assert line == '! Material ID,Manning\'s n'
    except Exception as e:
        raise e
    finally:
        Path('./tests/unit_tests/test_datasets/with_header_001.tmf').unlink()


def test_soil_db_init_ILCL():
    p = './tests/unit_tests/test_datasets/EG05_ILCL_017.tsoilf'
    db = SoilDatabase(p)
    assert db.df.shape == (2, 6)


def test_soil_db_value_ILCL():
    p = './tests/unit_tests/test_datasets/EG05_ILCL_017.tsoilf'
    db = SoilDatabase(p)
    val = db.value(1)
    assert val['method'] == 'ILCL'
    assert val['IL'] == 6.0
    assert val['CL'] == 1.2
    val = db.value(2)
    assert val['method'] == 'CO'


def test_soil_db_value_GA_USDA():
    p = './tests/unit_tests/test_datasets/EG05_GA_008.tsoilf'
    db = SoilDatabase(p)
    val = db.value(1)
    assert val['method'] == 'GA'
    assert val['usda soil type'] == 'CLAY'
    assert val['initial moisture'] == 0.2
    assert val['max ponding depth'] == 0.2


def test_soil_db_value_GA():
    p = './tests/unit_tests/test_datasets/EG05_GA_011.tsoilf'
    db = SoilDatabase(p)
    val = db.value(5)
    assert val['method'] == 'GA'
    assert val['suction'] == 273.
    assert val['hydraulic conductivity'] == 1.0
    assert val['porosity'] == 0.432


def test_soil_db_value_HO():
    p = './tests/unit_tests/test_datasets/EG05_HO_014.tsoilf'
    db = SoilDatabase(p)
    val = db.value(2)
    assert val['method'] == 'HO'
    assert val['il'] == 6.8


def test_pit_inlet_dbase():
    p = './tests/unit_tests/test_datasets/models/shp/model/csv/pit_inlet_dbase.csv'
    db = PitInletDatabase(p)
    assert db.df.shape == (3, 5)
    val = db.value('AA')
    assert isinstance(val, pd.DataFrame)
    assert val.shape == (13, 1)


def test_rf_dbase():
    p = './tests/unit_tests/test_datasets/rf/EG03_008_rf_index.csv'
    db =  RainfallDatabase(p)
    assert db.df.shape == (7, 1)
