import pandas as pd

from simera import UnitGenerator


class ScenarioItem:
    _allowed_apply_at = ['data', 'activity']

    def __init__(self, apply_at='data'):
        self.name = self.__class__.__name__
        self.apply_at = apply_at
        if self.apply_at not in self._allowed_apply_at:
            raise ValueError(f"Invalid apply_at value: {self.apply_at}. Must be one of {self._allowed_apply_at}")

    def __repr__(self):
        # Get all instance attributes except name and apply_at (which are always included)
        attrs = []
        for key, value in self.__dict__.items():
            if key not in ['name', 'apply_at']:
                attrs.append(f"{key}={value}")

        # Join all attributes
        attr_str = ', '.join(attrs)
        if attr_str:
            return f"{self.apply_at.title()}{self.name}({attr_str})"
        else:
            return f"{self.apply_at.title()}{self.name}"

    @classmethod
    def get_available_items(cls):
        """List of all available ScenarioItem subclass names."""
        return [subclass.__name__ for subclass in cls.__subclasses__()]

class ItemSetDeliveryFrequency(ScenarioItem):
    """
    Set delivery frequency for activities by grouping dates and selecting the minimum date per period.
    Can be configured using either a frequency string or specific working days.

    Parameters
    ----------
    date_column : str
        Name of the date column to modify. Must exist in DataFrame.
    frequency : str, optional
        Pandas frequency string for date grouping (e.g. '1W' for weekly).
        Ignored if working_days is specified. Cannot be used with working_days.
    working_days : list of int, optional
        List of working days (1=Monday to 7=Sunday) to map dates to.
        Dates are mapped to nearest previous working day.
        Cannot be used with frequency parameter.

    Notes
    -----
    Either frequency OR working_days must be specified, but not both.
    Creates a backup of original dates in 'old_{date_column}' column.
    
    Raises
    ------
    ValueError
        If neither nor both frequency/working_days specified
        If working_days contains invalid values
    KeyError 
        If date_column not found in DataFrame

    Frequency Examples
    ------------------
    Daily frequencies:
        '1D' or 'D' - Daily
        '2D' - Every 2 days
        '3D' - Every 3 days

    Weekly frequencies:
        '1W' or 'W' - Weekly (default)
        '2W' - Bi-weekly (every 2 weeks)
        '4W' - Every 4 weeks

    Monthly frequencies:
        '1M' or 'M' - Monthly (end of month)
        '2M' - Bi-monthly (every 2 months)
        '3M' or 'Q' - Quarterly (every 3 months)
        '6M' - Semi-annually (every 6 months) 
        'MS' - Monthly (start of month)
        '2MS' - Bi-monthly (start of month)

    Yearly frequencies:
        '1Y' or 'Y' - Yearly (end of year)
        '2Y' - Every 2 years
        'YS' - Yearly (start of year)

    Business frequencies:
        'B' or '1B' - Business daily
        '2B' - Every 2 business days
        'W-MON' - Weekly ending on Monday
        'W-FRI' - Weekly ending on Friday
        'BM' - Business month end
        'BMS' - Business month start
        'BQ' - Business quarter end
        'BA' - Business year end

    Hour/Minute frequencies:
        '1H' - Hourly
        '6H' - Every 6 hours
        '30T' or '30min' - Every 30 minutes

    Working Days Examples
    ---------------------
    [1, 3, 5] - Monday, Wednesday, Friday delivery days
        - Monday dates stay on Monday 
        - Tuesday dates move to Monday
        - Wednesday dates stay on Wednesday
        - Thursday dates move to Wednesday
        - Friday dates stay on Friday
        - Saturday and Sunday dates move to Friday

    [1] - Monday only deliveries
        - All dates in the week are moved to Monday

    [1, 5] - Monday and Friday deliveries
        - Monday-Tuesday dates move to Monday
        - Wednesday-Thursday dates move to Monday (nearest previous)
        - Friday-Sunday dates move to Friday

    Examples
    --------
    # Weekly delivery (default)
    item = ItemSetDeliveryFrequency('date_agi', '1W')
     
    # Monthly delivery at month start 
    item = ItemSetDeliveryFrequency('date_agi', 'MS')
    
    # Monday, Wednesday, Friday deliveries
    item = ItemSetDeliveryFrequency('date_agi', working_days=[1, 3, 5])
    
    # Monday only deliveries
    item = ItemSetDeliveryFrequency('date_agi', working_days=[1])
     
    # Tuesday and Thursday deliveries
    item = ItemSetDeliveryFrequency('date_agi', working_days=[2, 4])
    """
    
    def __init__(self, date_column, frequency=None, working_days=None):
        super().__init__(apply_at='data')
        if frequency is not None and working_days is not None:
            raise ValueError("Only one parameter can be used: either frequency or working_days")
        if frequency is None and working_days is None:
            raise ValueError("At least one parameter must be specified: either frequency or working_days")

        self.date_column = date_column
        self.frequency = frequency
        self.working_days = working_days


    def __call__(self, df, scenario):
        def _map_to_working_day(date, working_days_sorted):
            """Map a date to the nearest previous working day."""
            weekday = date.weekday() + 1  # Convert to 1-7 format (Monday=1)

            if weekday in working_days_sorted:
                return date

            # Find the nearest previous working day
            for i in range(1, 8):  # Check up to 7 days back
                prev_day = (weekday - i - 1) % 7 + 1
                if prev_day in working_days_sorted:
                    days_back = i
                    return date - pd.Timedelta(days=days_back)

            # This should never happen if working_days is not empty
            return date

        # Validate working_days parameter
        if self.working_days is not None:
            # Convert integer working_days to list
            if isinstance(self.working_days, int):
                self.working_days = [self.working_days]
            if not isinstance(self.working_days, list) or not self.working_days:
                raise ValueError("working_days must be a non-empty list")
            if not all(isinstance(day, int) and 1 <= day <= 7 for day in self.working_days):
                raise ValueError("working_days must contain integers between 1 (Monday) and 7 (Sunday)")

        if self.date_column not in df.columns:
            raise KeyError(f"date_column '{self.date_column}' not found in DataFrame columns: {list(df.columns)}")

        # Preserve original values in old_ column
        old_date_col = f'old_{self.date_column}'
        if old_date_col not in df.columns:
            # Find the position of the original column
            col_index = df.columns.get_loc(self.date_column)
            # Insert the old_ column right after the original column
            df.insert(col_index + 1, old_date_col, df[self.date_column].copy())
            # print(f"Created backup column: {old_date_col}")

        print(f"  Unique values in {self.date_column}: {df[self.date_column].nunique()} -> ", end='')

        if self.working_days is not None:
            # Working days aggregation
            working_days_sorted = sorted(self.working_days)
            df[self.date_column] = pd.to_datetime(df[self.date_column])
            df[self.date_column] = df[self.date_column].apply(lambda x: _map_to_working_day(x, working_days_sorted))
        else:
            # Regular frequency-based grouping
            df[self.date_column] = df.groupby(pd.Grouper(key=self.date_column, freq=self.frequency))[
                self.date_column].transform('min')

        print(f"{df[self.date_column].nunique()}")


class ItemSetDestination(ScenarioItem):
    """
    Replace all columns starting with 'dest_' with user-provided values for selected rows.

    This class identifies all destination columns (those starting with 'dest_')
    and replaces their values with user-provided values. If a destination column is not specified
    in dest_values, it will be set to '#'. Row selection can be controlled through filters.

    Parameters
    ----------
    dest_values : dict, optional
        Dictionary mapping destination column names to their new values.
        Keys should be column names (without 'dest_' prefix or with it).
        If a 'dest_' column exists but is not in dest_values, it will be set to '#'.
        Example: {'shipto': '1234567', 'ctry': 'ES', 'city': 'Madrid'}

    filters : dict or list of dict, optional
        Row filtering criteria. Can be:
        - Single dict: {'column_name': 'value'} - applies to all dest_values
        - List of dicts: [{'column_name': 'value1'}, {'column_name': 'value2'}]
        - If None, applies to all rows

        Each filter dict can contain multiple conditions that are combined with AND logic.
        Example: {'dest_shipto': '1234567', 'dest_ctry': 'PT'}

    Notes
    -----
    Creates backup columns with 'old_dest_' prefix for all modified destination columns.
    Columns not specified in dest_values are set to '#' as default.

    Examples
    --------
    # Replace all dest_ columns for all rows
    item = ItemSetDestination(
        dest_values={'shipto': '9999999', 'ctry': 'ES', 'city': 'Madrid'}
    )

    # Replace dest_ columns for specific rows only
    item = ItemSetDestination(
        dest_values={'shipto': '1111111', 'ctry': 'PT'},
        filters={'dest_shipto': '1234567'}
    )

    # Multiple filters for different row groups
    item = ItemSetDestination(
        dest_values={'shipto': '2222222', 'ctry': 'FR'},
        filters=[
            {'dest_shipto': '1234567'},
            {'dest_ctry': 'PT', 'dest_city': 'Porto'}
        ]
    )
    """

    def __init__(self, dest_values=None, filters=None):
        super().__init__(apply_at='data')
        self.dest_values = dest_values
        self.filters = filters


    def __call__(self, df, scenario):
        # Find all columns starting with 'dest_'
        dest_columns = [col for col in df.columns if col.startswith('dest_')]

        if not dest_columns:
            print("  No columns starting with 'dest_' found in DataFrame")
            return

        # Preserve original values in old_dest_ columns
        for col in dest_columns:
            old_col = col.replace('dest_', 'old_dest_', 1)
            if old_col not in df.columns:
                # Find the position of the original column
                col_index = df.columns.get_loc(col)
                # Insert the old_ column right after the original column
                df.insert(col_index + 1, old_col, df[col].copy())

        # Normalize dest_values keys to include 'dest_' prefix
        normalized_dest_values = {}
        if self.dest_values:
            for key, value in self.dest_values.items():
                if key.startswith('dest_'):
                    normalized_dest_values[key] = value
                else:
                    normalized_dest_values[f'dest_{key}'] = value

        # Determine which rows to update
        if self.filters is None:
            # Apply to all rows
            mask = df.index
            print(f"  Applying to all {len(mask)} rows: ", end='')
        else:
            # Handle single filter dict or list of filter dicts
            filter_list = self.filters if isinstance(self.filters, list) else [self.filters]

            # Combine all filter conditions
            combined_mask = pd.Series(False, index=df.index)

            for filter_dict in filter_list:
                # Create mask for this filter (AND logic within each filter)
                filter_mask = pd.Series(True, index=df.index)
                for col, value in filter_dict.items():
                    if col in df.columns:
                        filter_mask &= (df[col] == value)
                    else:
                        print(f"Warning: Filter column '{col}' not found in DataFrame")
                        filter_mask = pd.Series(False, index=df.index)
                        break

                # Combine with overall mask (OR logic between filters)
                combined_mask |= filter_mask

            mask = df.index[combined_mask]
            print(f"  Applying to {len(mask)}/{len(df)} rows: ", end='')

        # Replace values in dest_ columns
        rows_updated = 0
        for col in dest_columns:
            if len(mask) > 0:  # Only update if there are rows to update
                if col in normalized_dest_values:
                    df.loc[mask, col] = normalized_dest_values[col]
                    print(f"{col}='{normalized_dest_values[col]}', ", end='')
                else:
                    df.loc[mask, col] = '#'
                    print(f"{col}='#', ", end='')
                rows_updated = len(mask)
        print('')


class ItemSetSource(ScenarioItem):
    """
    Replace all columns starting with 'src_' with user-provided values for selected rows.

    This class identifies all source columns (those starting with 'src_')
    and replaces their values with user-provided values. If a source column is not specified
    in src_values, it will be set to '#'. Row selection can be controlled through filters.

    Parameters
    ----------
    src_values : dict, optional
        Dictionary mapping source column names to their new values.
        Keys should be column names (without 'src_' prefix or with it).
        If a 'src_' column exists but is not in src_values, it will be set to '#'.
        Example: {'site': 'WAREHOUSE01', 'ctry': 'ES', 'city': 'Barcelona'}

    filters : dict or list of dict, optional
        Row filtering criteria. Can be:
        - Single dict: {'column_name': 'value'} - applies to all src_values
        - List of dicts: [{'column_name': 'value1'}, {'column_name': 'value2'}]
        - If None, applies to all rows

        Each filter dict can contain multiple conditions that are combined with AND logic.
        Example: {'src_site': 'OLD_WAREHOUSE', 'dest_ctry': 'ES'}

    Notes
    -----
    Creates backup columns with 'old_src_' prefix for all modified source columns.
    Columns not specified in src_values are set to '#' as default.

    Examples
    --------
    # Replace all src_ columns for all rows
    item = ItemSetSource(
        src_values={'site': 'NEW_WAREHOUSE', 'ctry': 'ES', 'city': 'Madrid'}
    )

    # Replace src_ columns for specific rows only
    item = ItemSetSource(
        src_values={'site': 'WAREHOUSE_B', 'ctry': 'PT'},
        filters={'src_site': 'OLD_WAREHOUSE'}
    )

    # Multiple filters for different row groups
    item = ItemSetSource(
        src_values={'site': 'CENTRAL_HUB', 'ctry': 'FR'},
        filters=[
            {'src_site': 'WAREHOUSE_A'},
            {'dest_ctry': 'FR', 'src_city': 'Lyon'}
        ]
    )
    """

    def __init__(self, src_values=None, filters=None):
        super().__init__(apply_at='data')
        self.src_values = src_values
        self.filters = filters


    def __call__(self, df, scenario):
        # Find all columns starting with 'src_'
        src_columns = [col for col in df.columns if col.startswith('src_')]

        if not src_columns:
            print("No columns starting with 'src_' found in DataFrame")
            return

        # Preserve original values in old_src_ columns
        for col in src_columns:
            old_col = col.replace('src_', 'old_src_', 1)
            if old_col not in df.columns:
                # Find the position of the original column
                col_index = df.columns.get_loc(col)
                # Insert the old_ column right after the original column
                df.insert(col_index + 1, old_col, df[col].copy())

        # Normalize src_values keys to include 'src_' prefix
        normalized_src_values = {}
        if self.src_values:
            for key, value in self.src_values.items():
                if key.startswith('src_'):
                    normalized_src_values[key] = value
                else:
                    normalized_src_values[f'src_{key}'] = value

        # Determine which rows to update
        if self.filters is None:
            # Apply to all rows
            mask = df.index
            print(f"  Applying to all {len(mask)} rows: ", end='')
        else:
            # Handle single filter dict or list of filter dicts
            filter_list = self.filters if isinstance(self.filters, list) else [self.filters]

            # Combine all filter conditions
            combined_mask = pd.Series(False, index=df.index)

            for filter_dict in filter_list:
                # Create mask for this filter (AND logic within each filter)
                filter_mask = pd.Series(True, index=df.index)
                for col, value in filter_dict.items():
                    if col in df.columns:
                        filter_mask &= (df[col] == value)
                    else:
                        print(f"Warning: Filter column '{col}' not found in DataFrame")
                        filter_mask = pd.Series(False, index=df.index)
                        break

                # Combine with overall mask (OR logic between filters)
                combined_mask |= filter_mask

            mask = df.index[combined_mask]
            print(f"  Applying to {len(mask)}/{len(df)} rows: ", end='')

        # Replace values in src_ columns
        rows_updated = 0
        for col in src_columns:
            if len(mask) > 0:  # Only update if there are rows to update
                if col in normalized_src_values:
                    df.loc[mask, col] = normalized_src_values[col]
                    print(f"{col}='{normalized_src_values[col]}', ", end='')
                else:
                    df.loc[mask, col] = '#'
                    print(f"{col}='#', ", end='')
                rows_updated = len(mask)
        print('')

class ItemSetValue(ScenarioItem):
    """
    Set values for specified columns for selected rows.

    This class sets user-specified values for any columns in the DataFrame.
    Only the columns specified in the values dictionary will be modified.

    Parameters
    ----------
    values : dict, required
        Dictionary mapping column names to their new values.
        Keys should be exact column names that exist in the DataFrame.
        Example: {'banner': 'NEW_BANNER', 'dest_ctry': 'ES', 'volume': 100}

    filters : dict or list of dict, optional
        Row filtering criteria. Can be:
        - Single dict: {'column_name': 'value'} - applies to all values
        - List of dicts: [{'column_name': 'value1'}, {'column_name': 'value2'}]
        - If None, applies to all rows

        Each filter dict can contain multiple conditions that are combined with AND logic.
        Example: {'dest_shipto': '1234567', 'banner': 'OLD_BANNER'}

    Raises
    ------
    ValueError
        If values parameter is None or empty.

    Notes
    -----
    Creates backup columns with 'old_' prefix for all modified columns.
    Only columns specified in values dictionary are modified.

    Examples
    --------
    # Set values for specific columns on all rows
    item = ItemSetValue(
        values={'banner': 'NEW_BANNER', 'dest_ctry': 'ES', 'volume': 1000}
    )

    # Set values for specific columns on filtered rows
    item = ItemSetValue(
        values={'banner': 'PREMIUM', 'priority': 'HIGH'},
        filters={'dest_ctry': 'ES'}
    )

    # Multiple filters for different row groups
    item = ItemSetValue(
        values={'status': 'PROCESSED', 'updated_by': 'system'},
        filters=[
            {'banner': 'OLD_BANNER'},
            {'dest_ctry': 'PT', 'volume': 0}
        ]
    )
    """

    def __init__(self, values=None, filters=None):
        super().__init__(apply_at='data')
        if values is None or not values:
            raise ValueError("values parameter is required and cannot be empty")
        self.values = values
        self.filters = filters


    def __call__(self, df, scenario):
        # Check if all specified columns exist in the DataFrame
        missing_columns = [col for col in self.values.keys() if col not in df.columns]
        if missing_columns:
            print(f"Warning: The following columns are not in DataFrame and will be skipped: {missing_columns}")
            # Filter out missing columns
            valid_values = {col: val for col, val in self.values.items() if col in df.columns}
        else:
            valid_values = self.values

        if not valid_values:
            print("No valid columns found to update")
            return

        # Preserve original values in old_ columns
        for col in valid_values.keys():
            old_col = f'old_{col}'
            if old_col not in df.columns:
                # Find the position of the original column
                col_index = df.columns.get_loc(col)
                # Insert the old_ column right after the original column
                df.insert(col_index + 1, old_col, df[col].copy())

        # Determine which rows to update
        if self.filters is None:
            # Apply to all rows
            mask = df.index
            print(f"  Applying to all {len(mask)} rows: ", end='')
        else:
            # Handle single filter dict or list of filter dicts
            filter_list = self.filters if isinstance(self.filters, list) else [self.filters]

            # Combine all filter conditions
            combined_mask = pd.Series(False, index=df.index)

            for filter_dict in filter_list:
                # Create mask for this filter (AND logic within each filter)
                filter_mask = pd.Series(True, index=df.index)
                for col, value in filter_dict.items():
                    if col in df.columns:
                        filter_mask &= (df[col] == value)
                    else:
                        print(f"Warning: Filter column '{col}' not found in DataFrame")
                        filter_mask = pd.Series(False, index=df.index)
                        break

                # Combine with overall mask (OR logic between filters)
                combined_mask |= filter_mask

            mask = df.index[combined_mask]
            print(f"  Applying to {len(mask)}/{len(df)} rows: ", end='')

        # Set values for specified columns
        rows_updated = len(mask) if len(mask) > 0 else 0
        for col, value in valid_values.items():
            if len(mask) > 0:  # Only update if there are rows to update
                df.loc[mask, col] = value
                print(f"{col}='{value}', ", end='')
        print('')


class ItemSetOutletClean(ScenarioItem):
    """
    Update Scenario.pick_id_columns so that any 'dest_' column reference becomes 'old_dest_'.
    Ensures the required 'old_dest_*' columns exist in the DataFrame by creating them
    from their corresponding 'dest_*' columns when missing.

    This class requires access to the Scenario instance and modifies pick_id_columns
    configuration to use historical destination values instead of current ones.

    Notes
    -----
    This class requires both df and scenario parameters when called.
    Creates 'old_dest_*' columns from 'dest_*' columns if they don't exist.
    Modifies the scenario's pick_id_columns configuration.

    Examples
    --------
    >>> # Force outlet clean operation
    >>> item = ItemSetOutletClean()
    """

    def __init__(self, activity):
        super().__init__(apply_at='data')
        self.activity = activity


    def __call__(self, df, scenario):

        if self.activity not in scenario.activity_config:
            raise ValueError(f"activity '{self.activity}' not found in activity_config")
        original_cols = list(scenario.activity_config[self.activity].get('groupby_columns', {}))
        new_cols = []

        for col in original_cols:
            if isinstance(col, str) and col.startswith('dest_'):
                dest_col = col
                old_col = col.replace('dest_', 'old_dest_', 1)

                # Ensure the old_col exists; if missing, create it by copying dest_col
                if old_col not in df.columns:
                    if dest_col in df.columns:
                        dest_idx = df.columns.get_loc(dest_col)
                        df.insert(dest_idx + 1, old_col, df[dest_col].copy())
                    else:
                        # If the original dest_ column doesn't exist, still create an empty old_ column
                        # to avoid downstream errors; fill with NA
                        df[old_col] = pd.NA

                new_cols.append(old_col)
            else:
                new_cols.append(col)

        # Apply updates to the scenario
        scenario.activity_config[self.activity].update({'groupby_columns': new_cols})
        print(f"  {self.activity}: {original_cols} -> {new_cols}")


class ItemSetFullPalletsSimple(ScenarioItem):
    """
    ItemSetFullPalletsSimple class is designed to update columns in a dataframe
    based on specific business logic, particularly for activity data. It ensures that
    specific columns are reset to zero and a new column 'pal_ful' is created.

    This class is initialized with a default or user-specified list of column names
    to reset, and it operates upon being called with a dataframe. It ensures the
    presence of required columns in the dataframe and applies the transformations
    accordingly.

    :ivar set_zeros_columns: List of dataframe column names to reset to zero. Defaults
        to ['box_ful', 'box_broken', 'box_big', 'box_medium', 'box_small',
        'box_extreme'] if not provided.
    :type set_zeros_columns: list[str]
    """
    def __init__(self, activity, set_zeros_columns=None):
        super().__init__(apply_at='activity')
        if isinstance(activity, str):
            activity = [activity]
        self.activity = activity
        if set_zeros_columns is None:
            set_zeros_columns = ['box_ful', 'box_broken', 'box_big', 'box_medium', 'box_small', 'box_extreme']
        self.set_zeros_columns = set_zeros_columns

    def preprocess(self, df, scenario):
        # This makes sure all the unit components are generated in activity data
        required_activity_units = ['pal_eqv']
        for activity in self.activity:
            activity_units = scenario.activity_config[activity].get('data', {}).get('units', [])
            for unit in required_activity_units:
                if unit not in activity_units:
                    activity_units.append(unit)
                    print(f"  Added unit '{unit}' to activity '{activity}'")

    def __call__(self, df, scenario):
        # Make sure pal_eqv exist by putting that to preprocess
        df['pal_ful'] = df['pal_eqv']
        for col in self.set_zeros_columns:
            if col in df.columns:
                df[col] = 0
                print(f"{col}→0, ", end='')
        print(f"pal_ful→{df['pal_ful'].sum():0,.0f}")


if __name__ == '__main__':
    pass

    # Attention:
    #  activity level ScenarioItems should have function preprocess_data(df, scenario) to be called before the item is applied
