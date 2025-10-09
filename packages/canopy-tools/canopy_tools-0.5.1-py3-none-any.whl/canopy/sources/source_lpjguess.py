import os
import glob
from typing import Any
from canopy.core.field import Field
from canopy.sources.source_abc import Source
from canopy.sources.registry import register_source
from canopy.source_data import get_source_data


@register_source('lpjguess')
class SourceLPJGuess(Source):
    """
    Source object for LPJ-GUESS output
    """

    _formats = {
            "lpjg_annual": [ "aaet", "agpp", "aiso", "amon_mt1", "amon_mt2", "amon", "annual_burned_area", "anpp",
                             "cflux", "cmass", "cpool", "cton_leaf", "dens", "diam", "doc", "fpc", "lai", "nflux",
                             "ngases", "nlitter", "nmass", "npool", "nsources", "nuptake", "soil_nflux", "soil_npool",
                             "tot_runoff",
                            ],

            "lpjg_monthly": [ "maet", "mald", "mch4_diffusion", "mch4_ebullition",
                              "mch4", "mch4_plant", "mevap", "mgpp", "mintercep", "miso", "mlai",
                              "mmon_mt1", "mmon_mt2", "mmon", "mnee", "mnpp", "monthly_burned_area", "mpet",
                              "mra", "mrh", "mrunoff", "msnowdepth", "mwcont_lower", "mwcont_upper", "mwtp",
                            ]
            }


    def __init__(self, path: str) -> None:
        """
        Parameters
        ----------
        path: str
            The path of the directory that contains the LPJ-GUESS output
        """
        super().__init__(path, get_source_data('lpjguess'))

        self._field_paths = {}
        self._field_formats = {}
        self._unknown_format = []

        # In LPJ-GUESS each variable is outputted to a different file. The file names
        #   (minus the extension) are the same as the keys used to register the fields
        #   in the JSON model description file.
        paths = glob.glob(path + "/*.out") + glob.glob(path + "/*.out.gz")
        for file_path in paths:
            field_id = os.path.basename(file_path).replace(".out", "").replace(".gz", "")
            for file_format, file_list in self._formats.items():
                if field_id in file_list:
                    # I ignore typing errors referring to dynamically set _fields attribute in __init__ method
                    self._fields[field_id] = None # type: ignore
                    self._field_paths[field_id] = file_path
                    self._field_formats[field_id] = file_format
                    self.is_loaded[field_id] = False
                else:
                    self._unknown_format.append(field_id)

        if len(self._fields) == 0: # type: ignore
            raise ValueError(f"No data, or no readable data, found in {path}")

        self._fields = dict(sorted(self._fields.items())) # type: ignore
        self._unknown_format.sort()


    @property
    def unknown_format(self) -> list[str]:
        """Contains a list of files in the source folder whose format is unknown."""
        return self._unknown_format


    def load_field(self, field_id: str):
        """Load a field from this source.

        Parameters
        ----------
        field_id : str
            The field string identifier (coincides with the file name without extensions).
        """
        if field_id not in self.fields:
            raise KeyError(f"Field '{field_id}' not found in source.")
        field = Field.from_file(self._field_paths[field_id], file_format = self._field_formats[field_id])
        # Check if a field with field_id is registered, and copy the metadata
        if field_id in self.source_data['fields']:
            field.add_md('source', self.source)
            field.set_md('name', self.source_data['fields'][field_id]['name'])
            field.set_md('description', self.source_data['fields'][field_id]['description'])
            field.set_md('units', self.source_data['fields'][field_id]['units'])

        self.is_loaded[field_id] = True
        self.fields[field_id] = field

        return field


