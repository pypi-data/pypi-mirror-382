import pandas as pd
import copy
from tqdm import tqdm
from functools import reduce

from simera import UnitGenerator, Cost, Activity
from simera.utils import DataInputError
from simera.scenario_item import ScenarioItem

class Scenario:
    def __init__(
            self,
            scenario_id,
            scenario_name,
            data,
            scenario_items=None,
            activity_config=None,
            merge_activities_config=None,
            solve_immediately=False,
            merge_immediately=False,
            keep_cost_details=False,
            drop_units_components=True,
    ):
        # Input validation
        if not isinstance(data, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        if data.empty:
            raise ValueError("DataFrame cannot be empty")

        self.data = data.copy()

        self.scenario_id = str(scenario_id)
        self.scenario_name = scenario_name
        self.scenario_items = scenario_items

        self.activity_config = self.standardize_activity_config(activity_config)
        self.merge_activities_config = self.standardize_merge_activities_config(merge_activities_config)

        self.solve_immediately = solve_immediately
        self.merge_immediately = merge_immediately
        self.keep_cost_details = keep_cost_details
        self.drop_units_components = drop_units_components

        # To show initial counts before processing scenario items
        self._validate_groupby_columns()
        self._initial_activity_counter = {f'{activity}_id': self.data.groupby(self.activity_config[activity].get('groupby_columns'), as_index=False).ngroup().nunique() for activity in self.activity_config.keys()}

        self.apply_scenario_items_to_data()
        self.create_activity_id()
        self.create_activity_data()
        self.apply_scenario_items_to_activity()

        # Create activity objects that will be passed to calculate_cost()
        self.create_activity_objects()

        if self.solve_immediately:
            self.solve(self.keep_cost_details)

            if self.merge_immediately:
                self.merge_activities()


    def __repr__(self):
        num_items = len(self.scenario_items) if self.scenario_items else 0
        return f"Scenario <{self.scenario_id}: {self.scenario_name}> ({num_items} items)"

    def _validate_groupby_columns(self):
        """Validate that required columns exist in the DataFrame."""
        for activity, activity_items in self.activity_config.items():
            missing_columns = [col for col in activity_items.get('groupby_columns') if col not in self.data.columns]
            if missing_columns:
                raise ValueError(f"Missing groupby columns in Scenario data for activity '{activity}': {missing_columns}")

    @staticmethod
    def standardize_activity_config(activity_config: dict):
        activity_config = copy.deepcopy(activity_config)
        return activity_config

    @staticmethod
    def standardize_merge_activities_config(merge_activities_config: dict):
        merge_activities_config = copy.deepcopy(merge_activities_config)
        return merge_activities_config


    def apply_scenario_items_to_data(self):
        # Only scenario_items with apply_at == 'data' are used used
        if isinstance(self.scenario_items, ScenarioItem):
            self.scenario_items = [self.scenario_items]
        if self.scenario_items is not None:
            total_items = len(self.scenario_items)
        else:
            total_items = 0

        print(f"{'='*60}")
        print(f"Executing scenario: '{self.scenario_name}' with {total_items} items")
        print(f"{'='*60}")

        if self.scenario_items:
            for i, item in enumerate(self.scenario_items, 1):
                item_name = item.name
                print(f"({i}/{total_items}) {item_name} ({item.apply_at})")
                # Always put data and scenario in call
                if item.apply_at == 'data':
                    item(self.data, self)
                elif item.apply_at == 'activity':
                    # THis will execute preprocess() function to e.g. get required units components
                    print(f"  Preprocessing")
                    item.preprocess(self.data, self)
                else:
                    raise ValueError(f"apply_at must be 'data' or 'activity', not '{item.apply_at}'")
                print(f"{'-'*60}")
        else:
            print(f"No scenario items found\n{'-'*60}")

    def create_activity_id(self):
        print(f"{len(self.activity_config.keys())} Activities found: (Baseline → Scenario)")
        if self.activity_config:
            activity_counter = {}
            for pos, (activity, activity_items) in enumerate(self.activity_config.items()):
                # Keep old activity_id column for reference
                activity_id = f'{activity}_id'
                if activity_id in self.data.columns:
                    self.data.rename(columns={activity_id: f'old_{activity_id}'}, inplace=True)

                # Create ids
                groupby_columns = activity_items.get('groupby_columns')
                self.data.insert(pos, activity_id, self.data.groupby(groupby_columns, as_index=False).ngroup())

                # Count ids
                activity_counter[activity_id] = self.data[activity_id].nunique()

        for activity_id, count in activity_counter.items():
            print(f"  {activity_id}: {self._initial_activity_counter[activity_id]} → {count}")
        print(f"{'-'*60}")

    def create_activity_data(self):
        # New way of creating shipments (old concept)
        print('Creating activity data:')
        setattr(self, 'activity_data', {})
        for activity, activity_items in self.activity_config.items():
            print(f"  {activity}: ")
            # Get config for activity data
            activity_id = f'{activity}_id'
            data = activity_items.get('data', {})
            dims = data.get('dims', [])
            units = data.get('units', [])
            units_defaults = data.get('units_defaults', {})

            # Groupby --------------------------------------------------------------------------------------------------
            # Add activity_id to groupby.
            if activity_id not in dims:
                dims.insert(0, activity_id)

            # Add obligatory (ratesheet required) columns to groupby.
            # future: prepopulate if really needed for obligatory_column in ['dest_ctry', 'dest_zip']:
            for obligatory_column in []:
                if obligatory_column not in dims:
                    dims.append(obligatory_column)

            # Validate groupby columns exist
            missing_columns = [col for col in dims if col not in self.data.columns]
            if missing_columns:
                raise ValueError(f"Missing groupby columns in Scenario.data for activity '{activity}': {missing_columns}")

            # Units ----------------------------------------------------------------------------------------------------
            # Make sure at least one unit is specified
            if not units:
                raise ValueError(f"No units specified for activity '{activity}'")

            # Get required components to calculate activity units and check if are present in data
            required_components = UnitGenerator(units).show_required_components()
            # print(f'required components {required_components}: ', end='')
            missing_components_in_data = [comp for comp in required_components if comp not in self.data.columns]
            if missing_components_in_data:
                raise ValueError(f"Missing components in Scenario.data for activity '{activity}': {missing_components_in_data}")

            # Activity data --------------------------------------------------------------------------------------------
            df = self.data.groupby(dims, as_index=False).agg(required_components)
            # Calculate final units from components
            df = UnitGenerator(units).generate(df)

            # Adding units_defaults to activity data
            if units_defaults is not None:
                for col, val in units_defaults.items():
                    if col not in df.columns:
                        df[col] = val
                    else:
                        df.loc[df[col].isna(), col] = val

            # Add to Scenario activity_data
            self.activity_data.update({activity: df})

            # Summary:
            before = UnitGenerator(units).generate(self.data)
            after = UnitGenerator(units).generate(df)

            # Combine units and units_defaults for display
            all_units = list(units)
            if units_defaults:
                all_units.extend([col for col in units_defaults.keys() if col not in units])

            # Update units with units_defaults
            self.activity_config[activity]['data']['units'] = all_units

            for unit in all_units:
                before_val = f"{before[unit].sum():,.0f}" if unit in before.columns else "(default)"
                after_val = f"{after[unit].sum():,.0f}" if unit in after.columns else "(default)"
                print(f"    {unit}: {before_val} → {after_val}")

            # Drop units_components
            if self.drop_units_components:
                drop_columns = [col for col in df.columns if col not in units + list(units_defaults.keys()) + dims]
                df.drop(columns=drop_columns, inplace=True)

        if self.drop_units_components:
            print(f"  Dropped units components: {', '.join(drop_columns)}")

    def apply_scenario_items_to_activity(self):
        # Only scenario_items with apply_at == 'activity' are used.
        if self.scenario_items:
            scenario_items_at_activity = [item for item in self.scenario_items if item.apply_at == 'activity']
        else:
            scenario_items_at_activity = None

        print(f"{'-'*60}")
        print(f"Applying ScenarioItems to activity_data")

        if scenario_items_at_activity:
            for i, item in enumerate(scenario_items_at_activity, 1):
                total_items = len(scenario_items_at_activity)
                item_name = item.name
                print(f"({i}/{total_items}) {item_name} ({item.apply_at})")
                # Apply scenario item to activities
                for activity in item.activity:
                    if activity not in self.activity_config:
                        raise ValueError(f"activity '{activity}' not found in activity_config")

                    print(f"  {activity}: ", end='')
                    # Apply it on activity_data
                    item(self.activity_data.get(activity), self)
                print(f"{'-'*60}")
        else:
            print(f"  No scenario items found for activity level\n{'-'*60}")

    def create_activity_objects(self):
        print('Creating activity objects:')
        setattr(self, 'activity_objects', {})
        for activity, activity_data in self.activity_data.items():
            print(f"  {activity}: ", end='')
            activity_objects = []

            for row in activity_data.itertuples(index=False):
                # Create dict with 'dims' and 'units' keys
                input_data = {}

                # Get dims columns from config
                dims_cols = self.activity_config[activity]['data'].get('dims', [])
                input_data['dims'] = {col: getattr(row, col) for col in dims_cols if hasattr(row, col)}

                # Get units columns from config
                units_cols = self.activity_config[activity]['data'].get('units', [])
                input_data['units'] = {col: getattr(row, col) for col in units_cols if hasattr(row, col)}

                activity_objects.append(Activity(input_data))

            print(f"{len(activity_objects)} objects")
            self.activity_objects[activity] = activity_objects
        print(f"{'-'*60}")

    def solve(self, keep_cost_details: bool = True):
        print('Calculating activity cost:')
        setattr(self, 'activity_cost', {})
        setattr(self, 'activity_cost_best', {})
        setattr(self, 'activity_cost_missing', {})
        setattr(self, 'activity_cost_objects', {})
        for activity, activity_objects in self.activity_objects.items():
            print(f"  {activity}: ")
            activity_ratesheets = self.activity_config[activity]['cost']['ratesheets']
            must_match = self.activity_config[activity]['cost'].get('must_match')
            cost_summary_df, activities_with_cost, activities_without_ratesheets = self.calculate_cost(activity_objects, activity_ratesheets, must_match=must_match)
            self.activity_cost.update({activity: cost_summary_df})

            cost_best = cost_summary_df.sort_values(by=['activity_id', 'cost_total'], ascending=[True, True]).drop_duplicates(subset=['activity_id'], keep='first')
            self.activity_cost_best.update({activity: cost_best})

            self.activity_cost_missing.update({activity: activities_without_ratesheets})

            if keep_cost_details:
                self.activity_cost_objects.update({activity: activities_with_cost})
            else:
                self.activity_cost_objects.update({activity: 'keep_cost_details=False'})


    def merge_activities(self):
        print('Aggregating and merging activities:')
        setattr(self, 'activity_cost_aggregated', {})

        for activity, groupby_columns in self.merge_activities_config['aggregate_on'].items():
            print(f"  {activity}: ")
            if groupby_columns:
                df = self.activity_cost[activity].groupby(groupby_columns, as_index=False)['cost_total'].sum()
            else:
                df = self.activity_cost[activity].copy()
            df.rename(columns={'cost_total': f'cost_{activity}'}, inplace=True)
            self.activity_cost_aggregated.update({activity: df})

        # Merge dataframes from all activity_cost_aggregated
        if self.activity_cost_aggregated:
            merged_df = reduce(
                lambda left, right: pd.merge(left, right, on=self.merge_activities_config.get('merge_on'), how='left'),
                self.activity_cost_aggregated.values()
            )
        else:
            merged_df = pd.DataFrame()

        # todo: check if columns in left table were not duplicated
        # Drop where merge was not found
        print('    Combinations reduction: ', merged_df.shape[0], end='')
        for activity, _ in reversed(self.activity_cost_aggregated.items()):
            merged_df = merged_df.loc[~merged_df[f'cost_{activity}'].isna()]
            merged_df.insert(merged_df.columns.get_loc('total_packages') + 1, f'cost_{activity}', merged_df.pop(f'cost_{activity}'))
        print(' → ', merged_df.shape[0])
        # todo: report how many were droped
        merged_df.insert(merged_df.columns.get_loc('total_packages') + 1, 'cost_total', merged_df[[f'cost_{activity}' for activity in self.activity_cost_aggregated.keys()]].sum(axis=1))

        # Sort and pick best
        merged_df.sort_values(by=['activity_id', 'cost_total'], ascending=[True, True], inplace=True)
        merged_df_best = merged_df.drop_duplicates(subset=['activity_id'], keep='first')

        setattr(self, 'scenario_cost', merged_df)
        setattr(self, 'scenario_cost_best', merged_df_best)
        print(f'Done. Best cost = {merged_df_best.cost_total.sum():0,.0f}')

    @staticmethod
    def calculate_cost(activities_input, ratesheets_input, must_match: list[str] | None = None):
        """
        activities_input: iterable of activity objects
        ratesheets_input: iterable of ratesheet objects
        must_match: list of keys to additionally match on;
            any subset of ['src_site','trpmode'], or None for all.
            Note: 'dest_ctry' is ALWAYS applied.
        """
        activities_with_cost = []

        # Determine which fields to enforce:
        # dest_ctry is mandatory; src_site and trpmode are optional via must_match
        optional = {'src_site', 'trpmode'}
        if must_match is None:
            fields = {'dest_ctry'}
        else:
            fields = (set(must_match) & optional) | {'dest_ctry'}

        valid_combinations = []
        activities_with_ratesheets = 0
        activities_without_ratesheets = []
        for activity in activities_input:
            found = False
            for rs in ratesheets_input:
                checks = {
                    'src_site': activity.dims.get('src_site') in rs.shortcuts.src_sites,
                    'trpmode': activity.dims.get('trpmode') == rs.meta.service.get('trpmode'),
                    'dest_ctry': activity.dims.get('dest_ctry') in rs.shortcuts.dest_countries,
                }
                # require every field in `fields`
                if all(checks[f] for f in fields):
                    valid_combinations.append((activity, rs))
                    found = True
            if not found:
                activities_without_ratesheets.append(activity)
            else:
                activities_with_ratesheets += 1

        total = len(activities_input)
        with_rs = activities_with_ratesheets
        without_rs = len(activities_without_ratesheets)
        combos = len(valid_combinations)

        pct_with = (with_rs / total * 100) if total else 0
        pct_without = (without_rs / total * 100) if total else 0

        # neatly align the summary
        labels = [
            "Activities inserted",
            "Activities with ratesheets",
            "Activities without ratesheets",
        ]
        width = max(len(lbl) for lbl in labels)

        # ANSI color codes
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"
        color_text = RED if activities_without_ratesheets else GREEN

        print(
            f"{'    Activities inserted':<{width}}: {total}\n"
            f"{'    Activities with ratesheets':<{width}}: "
            f"{with_rs} ({pct_with:.1f}%) => {combos} combinations ({combos / total:0,.1f} per activity)\n"
            f"{f'    {color_text}Activities without ratesheets':<{width}}: "
            f"{without_rs} ({pct_without:.1f}%)\n{RESET}"
            f"{'    Matching on':<{width}}: {sorted(fields)}"
        )

        for activity, rs in tqdm(
                valid_combinations,
                desc=f"    Calculating activity-ratesheet costs",
                mininterval=1,
        ):
            activities_with_cost.append(Cost(activity, rs))

        print('    Creating cost summary dataframe... ', end='')

        cost_summary_df = pd.DataFrame([shp.cost_summary for shp in activities_with_cost])
        if cost_summary_df.empty:
            raise DataInputError(f'No cost found for selected activities. Make sure that zone can be found in the ratesheets.',
                                 solution=f'Typically: "dest_ctry"/"dest_zip" is not in activity_config.data.dims or "must_match" requires "src_site"/"trpmode"')
        cost_summary_df.sort_values(['activity_id', 'cost_total'], ignore_index=True, inplace=True)
        print(f"Done. Best cost = {cost_summary_df.sort_values(by=['activity_id', 'cost_total'], ascending=[True, True]).drop_duplicates(subset=['activity_id'], keep='first').cost_total.sum():0,.0f}")
        return cost_summary_df, activities_with_cost, activities_without_ratesheets


if __name__ == "__main__":
    # Testing
    from pathlib import Path
    from simera import Config, ZipcodeManager, RatesheetManager, Activity
    from simera.scenario_item import ItemSetValue, ItemSetDestination, ItemSetSource, ItemSetOutletClean, ItemSetDeliveryFrequency, ItemSetFullPalletsSimple

    sc = Config()
    zm = ZipcodeManager()
    rm_trp = RatesheetManager(sc.path.resources / 'ratesheets')
    rm_whs = RatesheetManager(sc.path.resources / 'ratesheets' / 'whs')
    # ratesheets_trp = rm_trp.read_excel_and_to_pickle('_transport_ltl_tsc-demo-par.pkl', ['!PAR', '!TSC_'])
    ratesheets_trp = rm_trp.read_pickle('_transport_ltl_tsc-demo-par.pkl')
    ratesheets_whs = rm_whs.read_excel_and_to_pickle('_warehouse_dc.pkl')

    # ======================================================================================================================
    DATA_DIR = Path(r'C:\Users\plr03474\NoOneDrive\Python\Simera_Projects\2025-09-22_IBE_Brico_Carrefour_Mercadona\data')
    df = pd.read_feather(DATA_DIR / 'data_20_initial_analysis_full.feather')
    df = df.loc[df.banner_text == 'mercadona'].copy()
    df.m3.sum()

    activity_config_input = {
        'ship': {
            'groupby_columns': ['src_site', 'date_agi', 'dest_shipto', 'dest_ctry', 'dest_zip', 'dest_city', 'dest_address'],
            'data': {
                'dims': ['src_site', 'dest_ctry', 'dest_zip', 'trpmode'],
                'units': ['m3', 'kg'],
                'units_defaults': {'shipment': 1, 'tsc_pkg_Lcm_100': 0},
            },
            'cost': {
                'ratesheets': ratesheets_trp,
                'must_match': ['trpmode'],
            }
        },
        'pick': {
            'groupby_columns': ['src_site', 'date_agi', 'dest_shipto', 'dest_ctry', 'dest_zip', 'dest_city', 'dest_address'],
            'data': {
                'dims': ['ship_id', 'src_site', 'dest_ctry', 'dest_zip', 'mat'],
                'units': ['kg', 'qty', 'm3', 'pal_ful', 'box_ful', 'box_big', 'box_medium', 'box_small', 'box_extreme', 'box_broken',
                          'orderline', 'shipment_whs', 'm3_outside_pal_ful', 'm3_inside_pal_ful', 'cluster_uki'],
                'units_defaults': {'putaway': 0, 'parcel': 0, 'm3_xd': 0},
            },
            'cost': {
                'ratesheets': ratesheets_whs,
                'must_match': [],
            }
        },
    }
    merge_activities_config = {
        'aggregate_on': {
            'ship': [],  # no aggregation needed before merging
            'pick': ['ship_id', 'src_site'],
        },
        'merge_on': ['ship_id', 'src_site'],
    }

    scenario_items = [
        ItemSetValue(values={'trpmode': 'LTL'}),
    ]
    scen0 = Scenario('00', 'Baseline', df, activity_config=activity_config_input, merge_activities_config=merge_activities_config, scenario_items=scenario_items, solve_immediately=True, merge_immediately=True, keep_cost_details=False)

    # scen0.solve(keep_cost_details=False)
    #
    # scenario_items = [
    #     ItemSetDestination(dest_values={'dest_soldto': '0072103949', 'dest_soldto_text': 'SONEPAR AUTOSTORE SAGUNTO', 'dest_segment': 'Wholesaler', 'dest_shipto': '0072103949', 'dest_shipto_text': 'SONEPAR AUTOSTORE SAGUNTO', 'dest_address': 'P.I.CAMI LA MAR E 28', 'dest_zip_initial': '46500', 'dest_zip': '46500', 'dest_city': 'SAGUNTO', 'dest_ctry': 'ES', 'dest_reg2': 'IBE'}),
    #     ItemSetValue(values={'trpmode': 'LTL'}),  # otherwise it's optimizing with PAR and customer is CDR050 not allowed)
    #     ItemSetDeliveryFrequency('date_agi', working_days=[1]),
    # ]
    #
    # scen1 = Scenario('10', 'Distributor', df, activity_config=activity_config_input, scenario_items=scenario_items, solve_immediately=True, keep_cost_details=False)
    #
    #
    # scenario_items = [
    #     ItemSetDeliveryFrequency('date_agi', working_days=[1, 4]),
    #     ItemSetDestination(dest_values={'ctry': 'PL', 'zip': '12345'}),
    #     ItemSetSource(src_values={'src_site': 'DC_PL_PILA'}),
    #     ItemSetValue(values={'trpmode': 'LTL'}),
    #     ItemSetOutletClean(activity='pick'),
    #     ItemSetFullPalletsSimple(activity=['pick']),
    # ]

    # scen1 = Scenario('01', '1x / week', df, scenario_items=scenario_items, activity_config=activity_config_input)

    # activities = scen1.activity_objects['ship']
    # activities = scen1.activity_objects['pick']
    # cost, a, b = calculate_cost(activities, ratesheets_trp)

    # xtodo: apply SceanrioItems on activity data
    #  ItemSetFullPalletsSimple - generate simply pal_eqv
    # todo: convert activity_data to Shipments

    # future: activity_configs dict
    #  name
    #  groupby_columns
    #  activity_mapper (show, lane, meta) + units
    #  ratesheets
    #  must_match (for calculate_cost)
    #  priority / filtering initial results (from calculate_cost)

    # Testing
    # activities = [Activity({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]},
    #                        'meta': {'trpmode': 'PAR'},
    #                        'units': {'tsc_pkg_Lcm_100': 0, 'm3': kg / 166, 'shipment': 1, 'kg': kg}}) for ctry in ['PL'] for kg in [1, 10, 110]]
    # cost, a, b = calculate_cost(activities, ratesheets_trp)

    # New version of Activity
    # activities = [Activity({'dims': {'src_site': 'DC_PL_PILA', 'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry], 'trpmode': 'PAR'},
    #                         'units': {'tsc_pkg_Lcm_100': 0, 'm3': kg / 166, 'shipment': 1, 'kg': kg}}) for ctry in ['PL'] for kg in [1, 10, 110]]
    # cost, a, b = calculate_cost(activities, ratesheets_trp, must_match=['trpmode', 'src_site'])
