import itertools
import copy
from simera import Config
from simera.utils import DataInputError
import pandas as pd

sc = Config()

class Activity:
    """
    todo: update docstrings
    """
    # future: itertools.count is unique per python process. When moving to multiprocessing for cost,
    #  make sure it's not activity are created before split.
    _id_counter = itertools.count(1)

    # Class variables - defaults and choices
    # Note: config values are taken from sc.config (not from ratesheet) as ratesheet could have older version
    _config_choices_volume = sc.config.units_of_measure.get('choices').get('volume')
    _config_choices_weight = sc.config.units_of_measure.get('choices').get('weight')
    _config_choices_volume_and_weight = sc.config.units_of_measure.get('choices').get('volume_and_weight')
    _config_units_of_measure_conversions_volume = sc.config.units_of_measure['conversions']['volume']
    _config_units_of_measure_conversions_weight = sc.config.units_of_measure['conversions']['weight']

    def __init__(self, input_data):
        # Process input data into dict with meta, lane and cost keys. Probably will be extended with SubClasses
        self.id = next(Activity._id_counter)
        self.input_data = input_data
        self.dims = self._get_dims()
        self.units = self._get_units()

    def __repr__(self):
        dims_str = ', '.join(f"{k}={v}" for k, v in list(self.dims.items())[:2]) if self.dims else ""
        units_str = ', '.join(f"{k}={round(v, 3)}" for k, v in list(self.units.items())[:2]) if self.units else ""
        combined = ', '.join(filter(None, [dims_str, units_str]))
        return f"Activity <{self.id}><{combined}>"

    def _get_dims(self):
        dims = self.input_data.get('dims', {})
        return dims

    def _get_units(self):
        units = self.input_data.get('units', {})

        # Convert weight and volume units to 'default_in_calculation' units (m3 and kg). It's for chargeable_ratios
        converted_units = {}
        for unit in units.keys():
            if unit in self._config_choices_volume and unit != 'm3':
                ratio_to_m3 = self._config_units_of_measure_conversions_volume[unit]['m3']
                converted_units.update({'m3': units[unit] / ratio_to_m3})
                continue
            if unit in self._config_choices_weight and unit != 'kg':
                ratio_to_kg = self._config_units_of_measure_conversions_weight[unit]['kg']
                converted_units.update({'kg': units[unit] / ratio_to_kg})
        units.update(converted_units)
        return units

    @classmethod
    def from_dataframe(cls, scenario, shipment_config: dict):
        """
        Build shipments from a line-level dataframe (provided in scen.df) by grouping and aggregating.

        Example of shipment_config:
        shipment_config_whs = {
            'show': {'shipment_id': 'shipment_id', 'mat': 'mat', 'nns': 'nns'},
            'lane': {'dest_ctry': 'dest_ctry', 'dest_zip': 'dest_zip', 'src_site': 'src_site'},
            'meta': {},
            'units': {'m3': 'm3', 'kg': 'kg', 'qty': 'qty', 'qty_per_pal': 'qty_per_pal', 'qty_per_box': 'qty_per_box'},
            # Optional:
            'units_defaults': {'sets': 2},
            'agg': {'qty_per_pal': 'first', 'qty_per_box': 'first'},
            'generate_units': [todo: update this list with new functions],
        }

        Returns
        - shipments: list[Activity]
        - shipments_df: grouped/aggregated dataframe
        """
        df = scenario.data.copy()
        shipment_config = copy.deepcopy(shipment_config)
        numeric_columns = df.select_dtypes('number').columns.tolist()
        dims = []
        measures = {}
        renamed = {}
        units_defaults = shipment_config.get('units_defaults')

        for config_type, columns_mapping in shipment_config.items():
            if config_type in ['show', 'lane', 'meta', 'units']:
                for col_new_name, col_name in columns_mapping.items():
                    if col_name in numeric_columns:
                        measures.update({col_name: 'sum'})
                    else:
                        dims.append(col_name)
                    if col_new_name != col_name:
                        renamed.update({col_name: col_new_name})
        if (agg := shipment_config.get('agg')) is not None:
            measures.update(agg)
        all_used_columns = list(measures.keys()) + dims
        missing_cols = [col for col in all_used_columns if col not in df.columns.tolist()]

        if missing_cols:
            raise DataInputError(f"Shipment_config columns not found in dataset: {missing_cols}. Check for these types: [show, lane, meta, units]",
                               solution="Ensure all required columns are present in the DataFrame or update the shipment_config to use existing column names")

        shipments_df = df.groupby(dims, as_index=False).agg(measures).rename(columns=renamed)
        # Adding units_defaults to df_shipments
        if units_defaults is not None:
            for col, val in units_defaults.items():
                if col not in shipments_df.columns.tolist():
                    shipments_df[col] = val
                else:
                    shipments_df.loc[shipments_df[col].isna(), col] = val
            # update show config with units_defaults
            shipment_config['units'].update({k:k for k, v in units_defaults.items()})

        # Generate special ShipmentUnits
        generate_units = shipment_config.get('generate_units', [])
        if generate_units:
            for func in generate_units:
                keep_units_in_shipment, drop_units_in_shipment = func(shipments_df)
                print(f'Generating "{func.__name__}" units to shipments: {keep_units_in_shipment}')
                shipment_config['units'].update({unit: unit for unit in keep_units_in_shipment})
                # Remove units from shipment_config
                for unit in drop_units_in_shipment:
                    shipment_config['units'].pop(unit, None)

        shipments = []
        for row in shipments_df.itertuples(index=False):
            # Here we create dict with values - not names, so this sh_config is needed
            sh_config = {'units': shipment_config.get('units_defaults', {}).copy()}
            for config_type in ['show', 'lane', 'meta', 'units']:
                sh_config.update({config_type: {k: getattr(row, k) for k, v in shipment_config.get(config_type).items()}})
            sh = Activity(sh_config)
            shipments.append(sh)
        print(f'Created {len(shipments)} unique combinations.')
        # print(f'Created {len(shipments)} unique combinations with:\n{shipments_df.select_dtypes("number").sum()}')
        return shipments, shipments_df


if __name__ == '__main__':
    activities = [Activity({'dims': {'dest_ctry': ctry, 'dest_zip': '12344', 'trpmode': 'PAR'},
                            'units': {'m3': kg / 166, 'shipment': 1, 'kg': kg}}) for ctry in ['PL'] for kg in [1, 10, 110]]
