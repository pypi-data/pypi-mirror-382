# tuflow-model-files

## Installation

Install the package using git clone. Note that there are submodules so the repository must be cloned recursively. In Windows, it is also best to use git bash as the submodule repository links use SSH paths.

Submodules:

* `convert_tuflow_model_gis_format`<br>
  (used to parse control files and write inputs with retained comments)

`git clone --recurse-submodules --remote-submodules git@gitlab.com:tuflow/public/tuflow-model-files.git`

Navigate into the repository:

`cd tuflow-model-files`

Git submodules checkout specific commits, but we want to use the `tuflow-model-files' branch. Navigate to the submodule directory:

`cd tmf/convert_tuflow_model_gis_format`

`git switch tuflow-model-files`

`cd ../..`

If you run `git status` it will complain that stuff has been changed, but this is expected and I'm not sure of a better way.

## Dependencies

Python 3.9 or later. The following packages are required:

* `numpy`
* `pandas`

Recommended packages:

* `gdal` (for Windows, pre-compiled wheels can be found at https://github.com/cgohlke/geospatial-wheels/releases)
* `netCDF4`

For testing:

* `pytest`

## Running the Tests

This repository uses `pytest` for testing which will require installing (`pip install pytest`). To run the tests, navigate to the repository root (above the 'tests' folder) and run the following commands.

To run all the tests:

`pytest tests/unit_tests/`

To run a specific module:

`pytest tests/unit_tests/test_control_file.py`

To run a specific test:

`pytest tests/unit_tests/test_control_file.py::test_control_file_init`

### Coverage

With pytest, coverage can be obtained using `pytest-cov`. Install the package (`pip install pytest-cov`) and run the following command to obtain coverage:

`pytest --cov=tmf.tuflow_model_files --cov-report=html tests/unit_tests/`

This will generate a folder called `htmlcov` which contains an `index.html` file. Open this file in a web browser to see the coverage report.

## Building a Wheel

Install the latest `setuptools`, `wheel`, and `build` packages (`pip install --upgrade setuptools wheel build`) and run the following command to build a wheel:

`python -m build --wheel`

This project is not intended to be published to PyPi, the wheel is intended to make it easier to install the package on other machines. The wheel will not install dependencies.

## Library Structure

The following diagram tries to demonstrate the class and inheritance structure of the repository:

![](docs/assets/images/tmf_class_structure_diagram.png)

## Usage

The following section acts as interim documentation until a proper documentation page is created. For more information, search for the method within the code and view the docstring.

### Control File - BuildState (TCF, TGC, TBC, ECF, etc)

`class TCF(fpath: PathLike, settings: Settings = None, parent: ControlFile = None, scope: ScopeList = None)`

**Properties**
* `tcf`: returns the TCF control file class (from the TCF returns self, from any other control file, will recursively search through parents until it finds a TCF)
* `inputs`: list of inputs in the order they appear in the control file
* `dirty`: returns True if the control file has been modified
* `parent`: returns the parent control file
* *dynamic properties - inputs are assigned to the control file as properties. If a given input is mentioned more than once, the property value will be changed to a list type.*

**Methods**

`def load(self, path: PathLike, settings: Settings = None) -> None`

`def figure_out_file_scopes(self, scope_list: ScopeList) -> None`

`def input(self, uuid: UUID | str) -> Input`

`def find_input(self, filter: str = None, command: str = None, value: str = None, regex: bool = False, regex_flags: int = 0, tags: SearchTagLike = (), callback: typing.Callable = None) -> list[InputBuildState]`

`def get_files(self, recursive: bool = True) -> list[PathLike]`

`def gis_inputs(self, recurisive: bool = True) -> list[InputBuildState]`

`def grid_inputs(self, recurisive: bool = True) -> list[InputBuildState]`

`def tin_inputs(self, recurisive: bool = True) -> list[InputBuildState]`

`def get_inputs(self, recursive: bool = False) -> list[InputBuildState]`

`def output_folder_1d(self, context: Context = None) -> PathLike`

`def output_folder_2d(self) -> PathLike`

`def tgc(self, context: Context = None) -> ControlFileBuildState`

`def ecf(self, context: Context = None) -> ControlFileBuildState`

`def tbc(self, context: Context = None) -> ControlFileBuildState`

`def tef(self, context: Context = None) -> ControlFileBuildState`

`def bc_dbase(self, context: Context = None) -> BcDatabase`

`def mat_file(self, context: Context = None) -> MatDatabase`

`def event_database(self, context: Context = None) -> EventDatabase`

`def input_to_loaded_value(self, input: InputBuildState) -> any`

`def undo(self, reset_children: bool = False) -> InputBuildState`

`def reset(self, reset_children: bool = False) -> None`

`def remove_input(self, inp: InputBuildState) -> None`

`def append_input(self, input_text: str, gap: int = 0) -> InputBuildState`

`def insert_input(self, inp: InputBuildState, input_text: str, after: bool = False, gap: int = 0) -> InputBuildState`

`def write(self, inc: str = 'auto') -> ControlFileBuildState`

`def preview(self) -> None`

`def context(self, context: ContextLike) -> RunState`

#### find_input()

A little bit more on `find_input`:

This method finds particular input(s) by using a filter. The filter can be for the entire input (`filter=`), or localised to the command (`command=`) or value (`value=`) side of the input. The filter can be a string or a regular expression (determined by using paremeter `regex=True/False` (`False` is default). 

The `tags` parameter can be used to filter the input by the input attributes. A `tag` is considered a `(key, value)` tuple, however if no `value` is passed in, it will default to `True`. The `tags` can be a list of tags or a single tag. E.g. `tags='multi_layer'` will return inputs that are have the attribute `mutli_layer = True`. This is the same as `tags=('multi_layer', True)`. Multiple tags can be used in a list `tags=[('multi_layer'), ('has_vector', True)]`. When multiple tags are used, each tag must be inside a `tuple/list` object. The value side can be any object or even a callable.

The `callback` parameter can be used to give a custom callback function that takes one `Input` argument and is expected to return a `bool`. This can be used if a complex filter is required.

The parameters are not mutually exclusive, so a filter string counld be provided as well as a number of tags.

Some example of using the `find_input` method:

```python
import re
from tmf.tuflow_model_files import TCF
from tmf.tuflow_model_files.abc.input import Input  # likely to make this easier in future

tcf = TCF('path/to/control_file.tcf')

# using a filter
inps = tcf.find_input('Read GIS')  # returns all inputs that have 'Read GIS' in the input

# using a command filter
inps = tcf.find_input(command='Read GIS')  # returns all inputs that have 'Read GIS' in the command

# using a value filter
inps = tcf.find_input(value='.shp')  # returns all inputs that have a value that ends with '.shp' (not case-sensitive)

# using regex
inps = tcf.find_input(value=r'\.(shp|mif)', regex=True,
                      regex_flags=re.IGNORECASE)  # returns all inputs that have a value that ends with '.shp' or '.mif' (not case-sensitive)

# using tags
inps = tcf.find_input(attrs=('missing_files', True))  # returns all inputs that have missing files

inps = tcf.find_input(
    attrs=('geoms', lambda x: ogr.wkbPoint in x))  # returns all inputs that reference a point geometry vector layer


# using a callback
def callback(inp: Input) -> bool:
    try:
        return inp.layer_count != inp.file_count
    except AttributeError:  # not all inputs will have a layer_count or file_count attribute
        return False


inps = tcf.find_input(
    callback=callback)  # returns all inputs that do not have the same number of input layers as files found
```

### Control File - RunState

Class cannot be initialised by the user. It should be created using the `context` method of the BuildState class. It inherits most of the same methods as the ControlFile class referenced above. Where the class methods differ are listed below.

**Not included from BuildState**

* `load`
* `figure_out_file_scopes`
* `undo`
* `reset`
* `remove_input`
* `append_input`
* `insert_input`
* `write`
* `preview`
* `context` (a completely different method with the same name is present)

**Additional Methods**

`def run(self, tuflow_bin: PathLike, prec: str = 'single', add_tf_flags: list[str] = (), *args, **kwargs) -> subprocess.Popen`

`def run_test(self, tuflow_bin: PathLike, prec: str) -> tuple[str, str]`

`def result_name(self) -> str`

`def tpc(self) -> PathLike`

`def context(self) -> ScopeList`

### Database - BuildState (BcDatabase, MatDatabase, PitDatabase etc)

`class BcDatabase(path: PathLike, scope: ScopeList = None, var_names: list[str] = ())`

**Properties**

* `dirty` returns True if the database has been modified

**Methods**

`def load(self, path: PathLike) -> None`

`def load_variables(self, var_names: list[str]) -> None`

`def figure_out_file_scopes(self, scope_list: ScopeList) -> None`

`def file_scope(self, file: PathLike) -> ScopeList`

`def value(self, item: str | int, **kwargs) -> any`

`def get_files(self) -> list[PathLike]`

`def write(self, fpath: PathLike) -> None`

`def db(self) -> pd.DataFrame`

`def index_to_file(self, index: str | int) -> list[PathLike]`

`def context(self, context: ContextLike) -> RunState`

### Database - RunState

Class cannot be initialised by the user. It should be created using the `context` method of the BuildState class. It inherits most of the same methods as the ControlFile class referenced above. Where the class methods differ are listed below.

**Not included from BuildState**

* `load`
* `figure_out_file_scopes`
* `load_variables`
* `file_scope`
* `write`
* `context` (a completely different method with the same name is present)

**Additional Methods**

`def context(self) -> ScopeList`

### Input - BuildState

`class InputBuildState(parent: BuildState, command: Command)`

**Properties**

* `parent`
* `trd` Path to the trd file if the input sits within one, otherwise None
* `dirty`
* `command` LHS of the input
* `value` RHS of the input
* `expanded_value` If the value is a file, returns the expanded path
* `files` If the value is a file, returns the file path(s)
* `missing_files` True if the input references a file that does not exist
* `user_def_index` If the file is a vector layer, returns the user defined attribute index if one is present
* `has_vector` If the input is referencing at least one vector layer
* `has_raster` If the input is referencing at least one raster layer
* `has_tin` If the input is referencing at least one tin layer
* `has_number` If the input contains a number
* `layer_count` The number of layers referenced in the input value (not including wildcard expanded values)
* `file_count` The number of files referenced in the input value (includes wildcard expanded values)
* `geom_count` The number of vector geometry types referenced in the input value
* `geoms` List of geometry types referenced in the input value
* `multi_layer` True if the input references more than one layer (or value e.g. a number)
* `numeric_type` The numeric type if a number is present (`int`, `float`)

**Methods**

`def figure_out_file_scopes(self, scope_list: ScopeList) -> None`

`def scope(self) -> ScopeList`

`def is_start_block(self) -> bool`

`def is_end_block(self) -> bool`

`def raw_command_obj(self) -> Command`

`def set_raw_command_obj(self, command: Command) -> None`

`def get_files(self) -> list[PathLike]`

`def write(self, fo: TextIO, scope_writer: ScopeWriter) -> str`

`def update_value(self, value: PathLike) -> InputBuildState`

`def update_command(self, command: str) -> InputBuildState`

`def set_scope(self, scope: list[tuple[str, str]]) -> InputBuildState`

`def context(self, context: ContextLike) -> RunState`

### Input - RunState

Class cannot be initialised by the user. It should be created using the `context` method of the BuildState class. It inherits most of the same methods as the ControlFile class referenced above. Where the class methods differ are listed below.

**Not included from BuildState**

* `figure_out_file_scopes`
* `write`
* `set_raw_command_obj`
* `update_value`
* `update_command`
* `set_scope`
* `context` (a completely different method with the same name is present)

**Additional Methods**

`def context(self) -> ScopeList`

### Scope

`class Scope(type: str, name: str = '', var: str = None`

Generally scope objects are initialised using their type and name:

`scope = Scope('Scenario', 'D01')`

A Scope object can have multiple values:

`scope = Scope('Scenario', 'D01 | D02')`

Scope comparison can be performed by checking the type only. The below will return `True` as in this case only the type is being compared.

`Scope('Scenario') == Scope('Scenario', 'D01')`

Checking for a specific scope name can be performed by supplying a name to the scope object. The below will return `False` as the names are different.

`Scope('Scenario', 'D01') == Scope('Scenario', 'D02')`

When checking if a Scope object is in a list of Scope objects, the ScopeList class should be used.

**Properties**

* `name`

**Methods**

`def known(self) -> bool`

`def is_neg(self) -> bool`

`def is_else(self) -> bool`

`def resolvable(self) -> bool`

`def explode(self) -> list[Scope]`

`def var(self) -> str`

`def to_string_start(self) -> str`

`def to_string_end(self) -> str`

`def supports_else_if(self) -> bool`

`def from_string(string: str, event_var: list[str]) -> ScopeList`  (static method)

`def resolve_scope(req_scope_list: ScopeList, var_string: str, compare_string: str, test_scopes: ScopeList) -> None`  (static method)

### ScopeList

`class ScopeList(scopes: list[Scope] = None)`

Subclasses python's list object, so methods likes `append`, `extend`, `remove`, `pop` etc are available.

### Context

`class Context(context: ContextLike, var_map: VariableMap = None)`

**Properties**

* `context_args`
* `var_loaded`
* `events_loaded`
* `available_scopes`
* *Dynamic properties - the context object will store scenario, event, and variable properties as attributes.*

**Methods**

`def is_empty(self) -> bool`

`def load_context_from_dict(self, context: dict) -> None`

`def load_context_from_args(self, context: list[str]) -> None`

`def load_variables(self, var_map: VariableMap) -> None`

`def load_events(self, event_db: EventDatabase) -> None`

`def in_context_by_scope(self, req_scope: ScopeList) -> bool`

`def translate(self, item: any) -> any`

`def translate_result_name(self, tcf_name: str) -> str`

`def is_resolved(self, item: any) -> bool`

### Other Utilities

#### Register TUFLOW Binary

`def register_tuflow_binary(version_name: str, version_path: PathLike) -> None`

Example:

```python
from tmf import register_tuflow_binary

register_tuflow_binary('2023-03-AD', 'C:/TUFLOW/releases/2023-03-AD/TUFLOW_iSP_w64.exe')
```

#### Register TUFLOW Binary Folder

`def register_tuflow_binary_folder(folder: PathLike) -> None`

A folder location that will automatically be searched for TUFLOW binaries.

Example:

```python
from tmf import register_tuflow_binary_folder

register_tuflow_binary_folder('C:/TUFLOW/Releases')
```

##### Short TUFLOW Type

`def short_tuflow_type(tuflow_type: str) -> str`

Example:

```python
from tmf import short_tuflow_type

tcf = TCF('path/to/control_file.tcf')
print(short_tuflow_type(tcf.TUFLOW_TYPE))
'TCF'
```

### Logging

Logging to console for warnings and above is enabled by default. To control the logging level you can pass the `log_level` keyword to the `ControlFileBuildState` class (TCF, TGC, etc) constructor.

Valid values for the log_level are `"DEBUG"`, `"INFO"`, `"WARNING"`, and `"ERROR"`

Example:
```python
tcf = TCF(log_level="INFO")
``` 

Logs can also be written to file with the `log_to_file` keyword. Useful if you want to track lower level log outputs more closely, or to provide more information when submitting a bug report.

```python
# log outputs to file (uses default level of "WARNING")
log_folder = "C:/logging/output/folder"
tcf = TCF(log_to_file=log_folder)

# Set level to "DEBUG" and log to file
tcf = TCF(log_level="DEBUG", log_to_file=log_folder)
```

Default logging will not be configured if any existing Python logging library handlers are found. To override the built in logging, configure a logger before importing any of the tmf modules. The TUFLOW API will still log outputs, but will be controlled by your custom configuration.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
