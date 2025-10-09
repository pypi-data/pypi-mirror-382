from canopy.core.field import Field
from canopy.sources.source_abc import Source
from canopy.sources.registry import register_source
from canopy.source_data import get_source_data
import itertools

FREQS = {'HH': 'Half-hourly', 'HR': 'Hourly', 'DD': 'Daily', 'WW': 'Weekly', 'MM': 'Monthly', 'YY': 'Yearly', }

FIELDS = {
    'H': 'Sensible Heat Flux',
    'LE': 'Latent Heat Flux',
    'G': 'Ground Surface Heat Flux',
    'NEE': 'Net Ecosystem Exchange',
    'RECO': 'Ecosystem Respiration',
    'GPP': 'Gross Primary Producion',
}

FIELD_COLS = {
    'H': ('H_F_MDS', 'H_F_MDS_QC', 'H_CORR', 'H_CORR_25', 'H_CORR_75', 'H_RANDUNC'),
    'H_longfreq': ('H_F_MDS', 'H_F_MDS_QC', 'H_CORR', 'H_RANDUNC'),
    'LE': ('LE_F_MDS', 'LE_F_MDS_QC', 'LE_CORR', 'LE_CORR_25', 'LE_CORR_75', 'LE_RANDUNC'),
    'LE_longfreq': ('LE_F_MDS', 'LE_F_MDS_QC', 'LE_CORR', 'LE_RANDUNC'),
    'G': ('G_F_MDS', 'G_F_MDS_QC'),
    'NEE': (
        'NEE_VUT_REF', 'NEE_VUT_REF_QC', 'NEE_VUT_REF_RANDUNC',
        'NEE_VUT_05', 'NEE_VUT_16', 'NEE_VUT_25', 'NEE_VUT_50', 'NEE_VUT_75', 'NEE_VUT_84', 'NEE_VUT_95', 
        'NEE_VUT_05_QC', 'NEE_VUT_16_QC', 'NEE_VUT_25_QC', 'NEE_VUT_50_QC', 'NEE_VUT_75_QC', 'NEE_VUT_84_QC', 'NEE_VUT_95_QC', 
    ),
    'RECO': (
        'RECO_NT_VUT_REF', 'RECO_DT_VUT_REF',
        'RECO_NT_VUT_05', 'RECO_NT_VUT_16', 'RECO_NT_VUT_25', 'RECO_NT_VUT_50', 'RECO_NT_VUT_75', 'RECO_NT_VUT_84', 'RECO_NT_VUT_95', 
        'RECO_DT_VUT_05', 'RECO_DT_VUT_16', 'RECO_DT_VUT_25', 'RECO_DT_VUT_50', 'RECO_DT_VUT_75', 'RECO_DT_VUT_84', 'RECO_DT_VUT_95', 
        'RECO_SR', 'RECO_SR_N',
    ),
    'GPP': (
        'GPP_NT_VUT_REF', 'GPP_DT_VUT_REF',
        'GPP_NT_VUT_05', 'GPP_NT_VUT_16', 'GPP_NT_VUT_25', 'GPP_NT_VUT_50', 'GPP_NT_VUT_75', 'GPP_NT_VUT_84', 'GPP_NT_VUT_95', 
        'GPP_DT_VUT_05', 'GPP_DT_VUT_16', 'GPP_DT_VUT_25', 'GPP_DT_VUT_50', 'GPP_DT_VUT_75', 'GPP_DT_VUT_84', 'GPP_DT_VUT_95', 
    )
}


def _get_field_cols(field_name: str, freq: str):
    if field_name in ['H', 'LE'] and freq in ['WW', 'MM', 'YY']:
        field_name += '_longfreq'
    return FIELD_COLS[field_name]

@register_source('fluxnet2015')
class SourceFluxnet2015(Source):
    """
    Source object for Fluxnet2015 data
    """

    def __init__(self, path) -> None:
        super().__init__(path, get_source_data('fluxnet2015'))
        for field_name, freq in itertools.product(FIELDS, FREQS):
            field_id = f"{field_name}_{freq}"
            self.fields[field_id] = None
            self.is_loaded[field_id] = False


    def load_field(self, field_id: str):

        field_id = field_id.upper()
        field_name, freq = field_id.split('_')
        if field_name not in FIELDS:
            raise ValueError(f"Field {field_id} not in source.")
        
        if freq not in FREQS:
            raise ValueError(f"Freq must be one of {FREQS}.")

        field_cols = _get_field_cols(field_name, freq)
        field = Field.from_file(self._path, file_format = 'fluxnet2015', grid_type = 'sites',
                                cols = field_cols,
                                freq = freq)

        field.add_md('source', self.source)
        field.set_md('name', self.source_data['fields'][field_id]['name'])
        field.set_md('description', self.source_data['fields'][field_id]['description'])
        field.set_md('units', self.source_data['fields'][field_id]['units'])

        self.is_loaded[field_id] = True
        self.fields[field_id] = field

        return field

