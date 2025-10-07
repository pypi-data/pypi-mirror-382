import typing
from pathlib import Path
from osgeo import ogr

from fm_to_estry.helpers.logging import get_fm2estry_logger
from fm_to_estry.helpers.settings import get_fm2estry_settings
from fm_to_estry.helpers.gis import open_vector_ds, open_vector_lyr

if typing.TYPE_CHECKING:
    from fm_to_estry.output import Output, OutputCollection


logger = get_fm2estry_logger()


class OutputWriter:

    def __init__(self) -> None:
        self.settings = get_fm2estry_settings()
        self.open_files = []
        self.open_outputs = []
        self._key2hnd = {}
        self._key2openfile = {}
        self._ds = {}
        self._ds2lyrs = {}
        self._txt_cmds = {}

    def get_key(self, output: 'Output') -> str:
        key = str(output.fpath).lower().strip().replace('\\', '/')
        if hasattr(output, 'lyrname'):
            key = f'{key} >> {output.lyrname.lower()}'
        return key

    def finalize(self) -> None:
        for output in self.open_outputs.copy():
            self.close_output(output)

    def write(self, output_collection: 'OutputCollection') -> None:
        for output in output_collection:
            try:
                self.write_output(output)
            except Exception as e:
                logger.error(f'Error writing output type "{output.TYPE}" for "{output.id}": {e}')
                return

    def write_output(self, output: 'Output') -> bool:
        fo = self.open_output(output)
        if fo is None:
            return False
        if output.TYPE == 'FILE':
            return self.write_file_output(fo, output)
        elif output.TYPE == 'CONTROL':
            return self.write_control_output(fo, output)
        elif output.TYPE == 'GIS':
            return self.write_vector_output(fo, output)
        return False

    def write_file_output(self, fo: typing.TextIO, output: 'Output') -> bool:
        fo.write(output.content)
        return True

    def write_control_output(self, fo: typing.TextIO, output: 'Output') -> bool:
        first = False
        if fo not in self._txt_cmds:
            self._txt_cmds[fo] = []
            first = True
        content = []
        content_common = []
        for line in output.content.strip('\n').split('\n'):
            line_common = line.lower().replace('\\', '/')
            if line_common not in self._txt_cmds[fo]:
                content.append(line)
                content_common.append(line_common)
        self._txt_cmds[fo].extend(content_common)
        if content:
            if first:
                fo.write('{0}\n'.format('\n'.join(content)))
            else:
                fo.write('\n{0}\n'.format('\n'.join(content)))
        return True

    def write_vector_output(self, lyr: ogr.Layer, output: 'Output') -> bool:
        feat = ogr.Feature(lyr.GetLayerDefn())
        geom = ogr.CreateGeometryFromWkt(output.content.geom)
        feat.SetGeometry(geom)
        for k, v in output.content.attributes.items():
            if self.settings.gis_format.upper() == 'SHP':
                feat.SetField(k[:10], v)
            else:
                feat.SetField(k, v)
        lyr.CreateFeature(feat)
        return True

    def open_output(self, output: 'Output') -> typing.Union[typing.TextIO, ogr.Layer]:
        if not hasattr(output, 'fpath'):
            return  # if no file, can't open anything
        key = self.get_key(output)
        hnd = self._key2hnd.get(key)
        if hnd:
            return hnd
        if output.TYPE in ['FILE', 'CONTROL']:
            hnd = self.open_text_file(key, output)
        elif output.TYPE == 'GIS':
            hnd = self.open_vector_file(key, output)
        if hnd:
            self.open_outputs.append(output)
        return hnd

    def close_output(self, output: 'Output') -> None:
        key = self.get_key(output)
        fo = self._key2hnd.get(key)
        if fo:
            if output.TYPE in ['FILE', 'CONTROL']:
                self.close_text_file(key, fo)
            elif output.TYPE == 'GIS':
                self.close_vector_file(key, fo)
        self.open_outputs.remove(output)

    def open_text_file(self, key: str, output: 'Output') -> typing.TextIO:
        if not output.fpath.parent.exists():
            output.fpath.parent.mkdir(parents=True)
        fo = output.fpath.open('w')
        self.open_files.append(output.fpath)
        self._key2openfile[key] = output.fpath
        self._key2hnd[key] = fo
        return fo

    def close_text_file(self, key: str, fo: typing.TextIO) -> None:
        fo.close()
        self._key2hnd.pop(key)
        if fo in self._txt_cmds:
            self._txt_cmds.pop(fo)
        open_file = self._key2openfile.pop(key)
        self.open_files.remove(open_file)

    def open_vector_file(self, key: str, output: 'Output') -> ogr.Layer:
        ds = self.open_vector_ds(key, output.fpath)
        if ds is None:
            return
        lyr = self.open_vector_lyr(key, ds, output.lyrname, output.geom_type, output.field_map)
        open_file = f'{output.fpath} >> {output.lyrname}'
        self.open_files.append(open_file)
        self._key2openfile[key] = open_file
        self._key2hnd[key] = lyr
        self._ds2lyrs[ds].append(lyr)
        return lyr

    def close_vector_file(self, key: str, lyr: ogr.Layer) -> None:
        self._key2hnd.pop(key)
        open_file = self._key2openfile.pop(key)
        self.open_files.remove(open_file)
        ds = [k for k, v in self._ds2lyrs.items() if lyr in v][0]
        self._ds2lyrs[ds].remove(lyr)
        close_ds = not bool(self._ds2lyrs[ds])
        lyr = None
        if close_ds:
            dbkey = key.split(' >> ')[0]
            self._ds.pop(dbkey)
            if self.settings.gis_format == 'GPKG':
                ds.CommitTransaction()
            ds = None

    def open_vector_ds(self, key: str, dbpath: Path) -> ogr.DataSource:
        dbkey = key.split(' >> ')[0]
        ds = self._ds.get(dbkey)
        if ds is not None:
            return ds
        ds = open_vector_ds(dbpath)
        self._ds[dbkey] = ds
        self._ds2lyrs[ds] = []
        if self.settings.gis_format == 'GPKG':
            ds.StartTransaction()
        return ds

    def open_vector_lyr(self, key: str, ds: ogr.DataSource, lyrname: str, geom_type: int, field_map: dict) -> ogr.Layer:
        return open_vector_lyr(ds, lyrname, geom_type, field_map)
