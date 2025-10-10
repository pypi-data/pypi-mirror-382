import pandas as pd
import numpy as np

class UnitGenerator:
    """
    Generates logistics units and calculations from shipment data.

    Calculates various logistics metrics including pallets, boxes, volumes, and weights
    from shipment data. Automatically resolves dependencies between calculations and
    supports both dictionary and DataFrame inputs.

    Supports calculations for:
    - Pallet equivalents and full pallets
    - Box counts (full, broken, by size category)
    - Volume and weight distributions
    - Special logistics units (clusters, shipment warehouse splits)

    Examples:
        Using with DataFrame:
        df = pd.DataFrame([
            {'qty': 150, 'qty_per_pal': 100, 'qty_per_box': 4, 'm3': 1.5},
            {'qty': 110, 'qty_per_pal': 100, 'qty_per_box': 4, 'm3': 0.8}
        ])
        generator = UnitGenerator(['pal_ful', 'box_ful'])
        result = generator.generate(df)

        Using with dictionary:
        data = {'qty': 150, 'qty_per_pal': 100, 'qty_per_box': 4, 'm3': 1.5}
        generator = UnitGenerator(['pal_ful', 'box_ful'])
        result = generator.generate(data)
    """
    EXTREME_BOX_MAX_DIM_CM = 170
    EXTREME_BOX_MAX_KG = 15
    BOX_SMALL_MAX_M3 = 1 / 90
    BOX_MEDIUM_MAX_M3 = 1 / 50
    AVG_M3_PER_CLUSTER_UKI = 6.5

    UNIT_AGGREGATION_FUNCTION = {
        'qty_per_box': 'first',
        'qty_per_pal': 'first',
        'box_height_cm': 'first',
        'box_length_cm': 'first',
        'box_width_cm': 'first',
        'qty': 'sum',
        'm3': 'sum',
        'kg': 'sum',
        'nns': 'sum',
    }

    def __init__(self, units: list|str):
        self.data = None
        self.is_dataframe = None
        self.units = [units] if isinstance(units, str) else units

    def _method_exists(self, unit_name: str) -> bool:
        """Check if a calculation method exists for the given unit name."""
        return hasattr(self, unit_name) and callable(getattr(self, unit_name))

    def _get_all_unit_methods(self) -> list[str]:
        """Get all calculation method names (unit methods) in the class."""
        # Get all methods that don't start with underscore and aren't special methods
        all_methods = [method for method in dir(self)
                      if not method.startswith('_')
                      and callable(getattr(self, method))
                      and method not in ['generate', 'show_required_components', 'show_all_components']]
        return all_methods

    def show_all_components(self) -> dict[str, str]:
        """
        List all potential base data components that could be required by any unit calculation.

        This analyzes all calculation methods in the UnitGenerator class and returns
        all unique base components (non-calculated fields) that any method might need.

        Returns:
            Dictionary mapping component names to their aggregation functions.

        Raises:
            ValueError: If a required component is not found in UNIT_AGGREGATION_FUNCTION.

        Example:
            generator = UnitGenerator(['pal_ful'])
            all_components = generator.show_all_components()
            # Returns all possible base components like: {'box_height_cm': 'first', 'box_length_cm': 'first',
            #   'box_width_cm': 'first', 'kg': 'sum', 'm3': 'sum', 'qty': 'sum', 'qty_per_box': 'first', 'qty_per_pal': 'first'}
        """
        import re
        import inspect

        def get_method_dependencies(unit: str) -> list[str]:
            """Extract dependencies from a method's source code."""
            if not self._method_exists(unit):
                return []

            method = getattr(self, unit)
            try:
                source = inspect.getsource(method)
                # Find all self.data['key'] or self.data["key"] patterns
                pattern = r"self\.data\[['\"](.*?)['\"]\]"
                dependencies = re.findall(pattern, source)
                return dependencies
            except (OSError, TypeError):
                # If source is not available (e.g., in console), detect dependencies dynamically
                return get_dependencies_by_execution(unit)

        def get_dependencies_by_execution(unit: str) -> list[str]:
            """Detect dependencies by attempting to execute the method with empty data."""
            accessed_keys = []

            class DataProxy:
                def __getitem__(self, key):
                    accessed_keys.append(key)
                    return 0

                def __contains__(self, key):
                    return False

                def groupby(self, key):
                    accessed_keys.append(key)
                    class MockGroupBy:
                        def transform(self, *args, **kwargs):
                            return 1
                    return MockGroupBy()

                def copy(self):
                    return self

            original_data = self.data
            original_is_dataframe = self.is_dataframe
            self.data = DataProxy()
            self.is_dataframe = False

            try:
                getattr(self, unit)()
            except (KeyError, AttributeError, TypeError, ZeroDivisionError):
                pass
            finally:
                self.data = original_data
                self.is_dataframe = original_is_dataframe

            return accessed_keys

        def get_base_components(unit: str, visited: set = None) -> set:
            """Recursively get base components for a unit."""
            if visited is None:
                visited = set()

            if unit in visited:
                return set()

            visited.add(unit)

            deps = get_method_dependencies(unit)

            base_components = set()
            for dep in deps:
                if self._method_exists(dep) and dep != unit:
                    # It's a calculated field (and not a self-reference), recurse
                    base_components.update(get_base_components(dep, visited))
                else:
                    # It's a base component (or a self-referencing method like qty() accessing self.data['qty'])
                    base_components.add(dep)

            return base_components

        # Get all unit methods
        all_units = self._get_all_unit_methods()

        # Collect all base components from all methods
        all_components = set()
        for unit in all_units:
            all_components.update(get_base_components(unit))

        # Build dictionary with aggregation functions
        result = {}
        for component in sorted(all_components):
            if component not in self.UNIT_AGGREGATION_FUNCTION:
                raise ValueError(f"Component '{component}' not found in UNIT_AGGREGATION_FUNCTION. "
                                 f"Please add it to UnitGenerator.UNIT_AGGREGATION_FUNCTION.")
            result[component] = self.UNIT_AGGREGATION_FUNCTION[component]

        return result

    def show_required_components(self) -> dict[str, str]:
        """
        List all unique calculation data items required to calculate requested outputs.

        Returns:
            Dictionary mapping component names to their aggregation functions.

        Raises:
            ValueError: If a required component is not found in UNIT_AGGREGATION_FUNCTION.

        Example:
            generator = UnitGenerator(['pal_ful', 'box_ful'])
            components = generator.show_required_components()
            # Returns: {'qty': 'sum', 'qty_per_pal': 'first', 'qty_per_box': 'first'}
        """
        import re
        import inspect

        def get_method_dependencies(unit: str) -> list[str]:
            """Extract dependencies from a method's source code."""
            if not self._method_exists(unit):
                return []

            method = getattr(self, unit)
            try:
                source = inspect.getsource(method)
                # Find all self.data['key'] or self.data["key"] patterns
                pattern = r"self\.data\[['\"](.*?)['\"]\]"
                dependencies = re.findall(pattern, source)
                return dependencies
            except (OSError, TypeError):
                # If source is not available (e.g., in console), detect dependencies dynamically
                return get_dependencies_by_execution(unit)

        def get_dependencies_by_execution(unit: str) -> list[str]:
            """Detect dependencies by attempting to execute the method with empty data."""
            # Create a proxy object that tracks what keys are accessed
            accessed_keys = []

            class DataProxy:
                def __getitem__(self, key):
                    accessed_keys.append(key)
                    # Return a dummy value that supports basic operations
                    return 0

                def __contains__(self, key):
                    return False

                def groupby(self, key):
                    accessed_keys.append(key)
                    # Return a mock object to continue execution
                    class MockGroupBy:
                        def transform(self, *args, **kwargs):
                            return 1
                    return MockGroupBy()

                def copy(self):
                    return self

            original_data = self.data
            original_is_dataframe = self.is_dataframe
            self.data = DataProxy()
            self.is_dataframe = False

            try:
                getattr(self, unit)()
            except (KeyError, AttributeError, TypeError, ZeroDivisionError):
                pass
            finally:
                self.data = original_data
                self.is_dataframe = original_is_dataframe

            return accessed_keys

        def get_all_dependencies(unit: str, visited: set = None) -> set:
            """Recursively get all dependencies for a unit."""
            if visited is None:
                visited = set()

            if unit in visited:
                return set()

            visited.add(unit)

            deps = get_method_dependencies(unit)

            all_deps = set()
            for dep in deps:
                if self._method_exists(dep) and dep != unit:
                    # It's a calculated field (and not a self-reference), recurse
                    all_deps.update(get_all_dependencies(dep, visited))
                else:
                    # It's a base component (or a self-referencing method)
                    all_deps.add(dep)

            return all_deps

        # Collect all required components for all requested units
        required_components = set()
        for unit in self.units:
            required_components.update(get_all_dependencies(unit))

        # Build dictionary with aggregation functions
        result = {}
        for component in sorted(required_components):
            if component not in self.UNIT_AGGREGATION_FUNCTION:
                raise ValueError(f"Component '{component}' not found in UNIT_AGGREGATION_FUNCTION. "
                                 f"Please add it to UnitGenerator.UNIT_AGGREGATION_FUNCTION.")
            result[component] = self.UNIT_AGGREGATION_FUNCTION[component]

        return result

    def generate(self, data: dict|pd.DataFrame) -> dict|pd.DataFrame:
        """Generate requested units and return data with calculated values."""
        self.data = data
        self.is_dataframe = isinstance(data, pd.DataFrame)

        # Create a copy of the data
        result = self.data.copy()
        working_data = self.data.copy()  # Separate working data for calculations

        # Calculate each requested unit
        for unit in self.units:
            if self._method_exists(unit):
                working_data = self._calculate_with_dependencies(unit, working_data)
                # Only add the requested unit to the final result
                result[unit] = working_data[unit]
            else:
                raise ValueError(f"No calculation method found for unit '{unit}'")
        return result

    def _calculate_with_dependencies(self, unit: str, current_data: dict|pd.DataFrame) -> dict|pd.DataFrame:
        """Calculate a unit, automatically resolving dependencies if missing."""
        max_attempts = 10  # Prevent infinite recursion
        attempt = 0

        while attempt < max_attempts:
            try:
                # Temporarily update self.data to include current calculated values
                original_data = self.data
                self.data = current_data

                calculated_value = getattr(self, unit)()
                current_data[unit] = calculated_value

                # Restore original data
                self.data = original_data
                return current_data

            except KeyError as e:
                # Extract the missing key from the error message
                missing_key = str(e).strip("'\"")

                # Check if we can calculate the missing key
                if self._method_exists(missing_key):
                    current_data = self._calculate_with_dependencies(missing_key, current_data)
                    attempt += 1
                else:
                    # Restore original data before raising error
                    self.data = original_data
                    raise KeyError(f"Cannot calculate '{unit}'. Missing required input '{missing_key}' and no calculation method available for it.")
            except Exception as e:
                # Restore original data before raising error
                self.data = original_data
                raise Exception(f"Error calculating '{unit}': {e}")

        # Restore original data before raising error
        self.data = original_data
        raise Exception(f"Maximum dependency resolution attempts reached for '{unit}'. Possible circular dependency.")

    def orderline(self):
        """Calculate orderline (with decimals)."""
        orderline = 1
        return orderline

    def qty(self):
        """Calculate qty (with decimals)."""
        qty = self.data['qty']
        return qty

    def m3(self):
        """Calculate m3 (with decimals)."""
        m3 = self.data['m3']
        return m3

    def kg(self):
        """Calculate kg (with decimals)."""
        kg = self.data['kg']
        return kg

    def nns(self):
        """Calculate nns (with decimals)."""
        nns = self.data['nns']
        return nns

    def pal_eqv(self):
        """Calculate pallet equivalent (with decimals)."""
        pal_eqv = self.data['qty'] / self.data['qty_per_pal']
        return pal_eqv

    def pal_ful(self):
        """Calculate full pallets (whole number)."""
        pal_ful = self.data['qty'] // self.data['qty_per_pal']
        return pal_ful

    def qty_inside_pal_ful(self):
        qty_inside_pal_ful = self.data['pal_ful'] * self.data['qty_per_pal']
        return qty_inside_pal_ful

    def qty_outside_pal_ful(self):
        qty_outside_pal_ful = self.data['qty'] - self.data['qty_inside_pal_ful']
        return qty_outside_pal_ful

    def box_eqv(self):
        """Calculate box equivalent outside full pallet (with decimals)."""
        box_eqv = self.data['qty_outside_pal_ful'] / self.data['qty_per_box']
        return box_eqv

    def box_ful(self):
        """Calculate full boxes (whole number) outside full pallet."""
        box_ful = self.data['qty_outside_pal_ful'] // self.data['qty_per_box']
        return box_ful

    def box_broken(self):
        """Calculate number of boxes that are broken."""
        box_broken = np.ceil(self.data['box_eqv'] - self.data['box_ful'])
        return box_broken

    def m3_per_box(self):
        """Calculate average m3 per box."""
        m3_per_box = self.data['m3'] / (self.data['qty'] / self.data['qty_per_box'])
        return m3_per_box

    def kg_per_box(self):
        """Calculate average m3 per box."""
        kg_per_box = self.data['kg'] / (self.data['qty'] / self.data['qty_per_box'])
        return kg_per_box

    def box_big(self):
        """Calculate number of boxes that are big."""
        box_big = (self.data['m3_per_box'] > self.BOX_MEDIUM_MAX_M3) * self.data['box_ful'] * (self.data['box_extreme'] == 0)
        return box_big

    def box_medium(self):
        """Calculate number of boxes that are medium."""
        box_medium = ((self.data['m3_per_box'] > self.BOX_SMALL_MAX_M3) & (self.data['m3_per_box'] <= self.BOX_MEDIUM_MAX_M3)) * self.data['box_ful'] * (self.data['box_extreme'] == 0)
        return box_medium

    def box_small(self):
        """Calculate number of boxes that are small."""
        box_small = (self.data['m3_per_box'] <= self.BOX_SMALL_MAX_M3) * self.data['box_ful'] * (self.data['box_extreme'] == 0)
        return box_small

    def box_maxdim(self):
        """Calculate maximum dimension of boxes."""
        if self.is_dataframe:
            box_maxdim = self.data[['box_length_cm', 'box_width_cm', 'box_height_cm']].max(axis=1)
        else:
            box_maxdim = max(self.data['box_length_cm'], self.data['box_width_cm'], self.data['box_height_cm'])
        return box_maxdim

    def box_extreme(self):
        """Calculate number of boxes that are extreme."""
        box_extreme = ((self.data['box_maxdim'] > self.EXTREME_BOX_MAX_DIM_CM) | (self.data['kg_per_box'] > self.EXTREME_BOX_MAX_KG)) * self.data['box_ful']
        return box_extreme

    def m3_inside_pal_ful(self):
        """Calculate m3 inside full pallet."""
        m3_inside_pal_ful = self.data['m3'] * (self.data['pal_ful'] / self.data['pal_eqv'])
        return m3_inside_pal_ful

    def m3_outside_pal_ful(self):
        """Calculate m3 outside full pallet."""
        m3_outside_pal_ful = self.data['m3'] - self.data['m3_inside_pal_ful']
        return m3_outside_pal_ful

    # Special cases
    def cluster_uki(self):
        # Calculated based on: 15 box per pallet and avg box size
        cluster_uki = self.data['m3'] * self.AVG_M3_PER_CLUSTER_UKI
        return cluster_uki

    def shipment_whs(self):
        # attention: ship_id is fixed!
        if self.is_dataframe:
            shipment_whs = 1 / self.data.groupby('ship_id').transform('size')
        else:
            shipment_whs = 1
        return shipment_whs

# Example usage
if __name__ == "__main__":

    # Example 0: Show all components and required components for each unit
    test1 = UnitGenerator(units=['m3'])
    print(test1.show_required_components())
    test1.generate(data={'m3': 1})
    print(test1.show_all_components())

    test2 = UnitGenerator(units=['pal_ful', 'pal_eqv'])
    print(test2.show_required_components())
    test2.generate(data={'qty_per_pal': 23, 'qty': 100})
    print(test2.show_all_components())

    # Example 1: Using DataFrame
    df = pd.DataFrame([
        {'ship_id': 1, 'qty': 150, 'kg': 120, 'm3': 10, 'qty_per_pal': 100, 'qty_per_box': 4},
        {'ship_id': 1, 'qty': 110, 'kg': 120, 'm3': 0.5, 'qty_per_pal': 100, 'qty_per_box': 4},
        {'ship_id': 2, 'qty': 110, 'kg': 120, 'm3': 0.2, 'qty_per_pal': 100, 'qty_per_box': 4},
    ])
    generator1 = UnitGenerator(units=['pal_ful', 'pal_eqv', 'box_ful', 'box_broken', 'qty_outside_pal_ful', 'orderline',
                                     'shipment_whs'])
    df_result = generator1.generate(data=df)

    # Example 2: Using dictionary
    generator2 = UnitGenerator(units=['pal_ful', 'pal_eqv', 'box_ful', 'box_broken', 'qty_outside_pal_ful', 'orderline',
                                     'm3_per_box', 'kg_per_box', 'box_big', 'box_medium', 'box_small', 'box_extreme'])
    dict_data = {'box_length_cm': 111, 'box_width_cm': 40, 'box_height_cm': 10, 'qty': 110, 'kg': 120, 'm3': 1, 'qty_per_pal': 100, 'qty_per_box': 4}
    generator2.generate(data=dict_data)
