from typing import List, Set, Tuple, Union

from assonant.data_classes.components import Beamline, Component
from assonant.data_classes.entry import Entry
from assonant.data_classes.factories import AssonantComponentFactory
from assonant.metadata_retriever import AssonantMetadataRetriever

from .exceptions import AssonantHierarchizerError


class Hierarchizer:
    """Assonant Data Class Hierarchizer.

    Object responsible to automate the creation and mounting of the correct Components
    hierarchy based in a given schema.
    """

    def __init__(self, schema_file_path: str, metadata_retriever: AssonantMetadataRetriever = None):
        """Assonant Data Class Hierarchizer Constructor.

        Args:
            schema_file_path (str): Path to schema file.
            metadata_retriever (AssonantDataRetriever, optional): An already instantiate AssonantMetadataRetriever
            to be used. This can be used to avoid unneeded creation of new AssonantDatRetriever,
            which may generate some overhead due to accessing and parsing data source file.
            Defaults to None.
        """
        self.schema_file_path = schema_file_path

        if metadata_retriever is not None:
            self.metadata_retriever = metadata_retriever
        else:
            try:
                self.metadata_retriever = AssonantMetadataRetriever(self.schema_file_path)
            except Exception as e:
                raise AssonantHierarchizerError(
                    f"Failed to instantiate an AssonantDataRetriever for the data class Hierarchizer with {self.schema_file_path}"
                ) from e

    def _mount_tree_node_set(self, component_info_tuple: Tuple[str, Union[str, None]]) -> Set[str]:
        """Mount a set of tree nodes that connects component_info_tuple to its root component_info_tuple.

        PS: component_info_tuples may be created to allow achieving the root node. Due to that
        a metadata_retriever is needed to allow searching for missing nodes in the schema.

        Args:
            component_info_tuple (Tuple[str, Union[str, None]]): Tuple containing Component info.

        Returns:
            set[str]: Set containing all component_info_tuples that connect the passed component_info_tuple
            to its root node component_info_tuple.
        """
        # Auxiliar index naming for better code comprehension
        # COMPONENT_NAME = 0
        # COMPONENT_CLASS = 1
        COMPONENT_PARENT = 2

        # Check if component is the root node (No parent component)
        if component_info_tuple[COMPONENT_PARENT] is not None:
            # TODO: POSSIBLE ENHANCEMENT: CHECK IF COMPONENT INFO ALREADY DONT EXIST ON COMPONENT_INFO_SET
            parent_component_info = self.metadata_retriever.get_component_info(component_info_tuple[COMPONENT_PARENT])
            parent_component_info_tuple = (
                parent_component_info["component_info"]["name"],
                parent_component_info["component_info"]["class"],
                (
                    parent_component_info["component_info"]["subcomponent_of"]
                    if "subcomponent_of" in parent_component_info["component_info"].keys()
                    else None
                ),
            )
            set_of_tree_nodes = self._mount_tree_node_set(parent_component_info_tuple)
            set_of_tree_nodes.add(component_info_tuple)

        else:
            set_of_tree_nodes = set()
            set_of_tree_nodes.add(component_info_tuple)

        return set_of_tree_nodes

    def hierarchize_components(self, components: List[Component]) -> List[Component]:
        """Hierarchize passed Components according to subcomponents metadata.

        Args:
            components (List[Component]): List of Components that will be hierarchized.

        Returns:
            List[Component]: List of hierarchized Components.
        """

        # =============== UNION-FIND based algoritm solution ===============

        # Problem definition:
        # Data may be acquired in a sparse way where not all Components/SubComponents have data
        # collected and are required to be collected in all experiments.
        # To avoid situations where a Subcomponent have data collect but its parent Component not,
        # and the Subcomponent would be store in a different hierarchy
        # level when compared to situation where its parent Component has information collected,
        # this algorithm was developed. The idea is, without creating all
        # Components and Subcomponents possible and letting many empty if they don't have
        # data collected, guarantee that the collected data will be fit
        # the same hierarchy level no matter the situation. THis allow a standardization in the data
        # schema, and still allow non-collected data to simply not appear.
        #
        # Overall Idea of the algorithm
        # To achieve that, this algorithm get all collected Components, create sets with their
        # information an start to merge them until achieve disjoint sets, meaning
        # a root Component was found. The data retriever is needed here to query the reference schema
        # to allow filling empty roles in the hierarchy in order to allow
        # every Subcomponent to be connected to its root Component.
        # Below there are each step of the algorithm and a brief explanation
        # ===================================================================

        components_references = {}
        components_info_set = set()
        unchanged_components = []
        hierarchized_components = []

        # Step 0: Prepare data structure for Union-Find based algorithm
        for component in components:
            # Ignore Entry and Beamline!! They are special cases in the hierarchy!!!
            if isinstance(component, Entry) or isinstance(component, Beamline):
                unchanged_components.append(component)
            else:
                # Store reference to component in dict
                components_references[component.name] = component

                # Retrieve information about the component to get 'subcomponent of' information
                component_retrieved_info = self.metadata_retriever.get_component_info(component.name)

                # Add component information to set that will be used on further steps
                component_name = component_retrieved_info["component_info"]["name"]
                component_class = component_retrieved_info["component_info"]["class"]
                component_parent = (
                    component_retrieved_info["component_info"]["subcomponent_of"]
                    if "subcomponent_of" in component_retrieved_info["component_info"].keys()
                    else None
                )
                components_info_set.add((component.name, component_class, component_parent))

        forest_of_tree_node_sets = []

        # Step 1: Mount Each collected Component minimum hierarchy tree that connects each Component
        # to its respective root Component
        for component_info_tuple in components_info_set:
            forest_of_tree_node_sets.append(self._mount_tree_node_set(component_info_tuple))

        # print("Step1:", forest_of_tree_node_sets)

        # STEP 2: Unite tree sets until they are all disjoints
        solved_tree_node_sets = []

        while forest_of_tree_node_sets != []:

            # Get one node set
            chosen_tree_node_set = forest_of_tree_node_sets.pop()
            intersecting_set_found = False

            # Check if the chosen set intersects other existing set
            for tree_node_set in forest_of_tree_node_sets:
                if not chosen_tree_node_set.isdisjoint(tree_node_set):
                    # A intersecting set was found!

                    # Unite both sets
                    chosen_tree_node_set = chosen_tree_node_set.union(tree_node_set)

                    # Remove from list set that was united with chosen set to avoid duplication
                    forest_of_tree_node_sets.remove(tree_node_set)

                    # Add the United set to the pool of sets
                    forest_of_tree_node_sets.append(chosen_tree_node_set)
                    intersecting_set_found = True
                    break

            # If no intersecting set was found, it means that chosen set is solved
            if not intersecting_set_found:
                solved_tree_node_sets.append(chosen_tree_node_set)

        # print("Step2:", solved_tree_node_sets)

        # Step 3: Instantiate Components or reuse already instantiated ones and put subcomponents inside their parents
        for solved_tree_node_set in solved_tree_node_sets:
            root_node = None

            # Create all Components
            for node_tuple in solved_tree_node_set:
                component_name, component_class_name, component_parent_name = node_tuple
                # Check if Component was a intermediate Component in the hierarchy which no information was collected
                if component_name not in components_references.keys():
                    # Instantiate Component to fill hierarchy gaps
                    components_references[component_name] = AssonantComponentFactory.create_component_by_class_name(
                        component_class_name, component_name
                    )

            # Create Components/Subcomponents Hierarchy
            for node_tuple in solved_tree_node_set:
                component_name, component_class_name, component_parent_name = node_tuple
                if component_parent_name is None:
                    # Save reference for root node
                    root_node = components_references[component_name]
                else:
                    # Add component as subcomponent of its parent
                    components_references[component_parent_name].add_subcomponent(components_references[component_name])

            hierarchized_components.append(root_node)

        # print("Step3:", hierarchized_components)

        # Step 4: Concatenate Unchanged Components with Hierarchized Components

        # print("step4:", unchanged_components + hierarchized_components)

        return unchanged_components + hierarchized_components
