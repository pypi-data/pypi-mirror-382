"""Factory class to deal with NeXus Object Creation."""

from collections.abc import Iterable
from typing import Dict, List, Union

import numpy as np
from nexusformat.nexus import *

from assonant.data_classes import AssonantDataClass, Entry
from assonant.data_classes.components import (
    BVS,
    Attenuator,
    Beam,
    Beamline,
    BeamStopper,
    BendingMagnet,
    Collimator,
    Component,
    Cryojet,
    Detector,
    DetectorChannel,
    DetectorModule,
    DetectorROI,
    Dewar,
    FresnelZonePlate,
    GraniteBase,
    Grating,
    Mirror,
    Monochromator,
    MonochromatorCrystal,
    MonochromatorVelocitySelector,
    Pinhole,
    Sample,
    Sensor,
    Shutter,
    Slit,
    StorageRing,
    Undulator,
    Wiggler,
)
from assonant.data_classes.data_handlers import Axis, DataField, DataHandler, TimeSeries

from .exceptions import NeXusObjectFactoryError


class NeXusObjectFactory:
    """NeXus Object Factory Class.

    Class that implements the factory design pattern
    (https://refactoring.guru/design-patterns/factory-method) to fully abstract
    the procedure of creating NeXus object out of AssonantDataClass objects.
    """

    def create_nxobject(
        self, data_obj: AssonantDataClass, pack_into_nxroot: bool = False, convert_missing_data: bool = True
    ) -> NXobject:
        """Creates the respective Nexus object based on the passed AssonantDataClass specific type.

        Args:
            data_obj (AssonantDataClass): Data object which will be used for the
            NeXus object creation
            pack_into_nxroot (bool, optional): If returned object should be or not
            packed inside a NXroot. Defaults to False.
            convert_missing_data (bool, optional): If None values within DataField classes
            should be transformed or not in a np.nan value. Defaults to True.

        Raises:
            NeXusObjectFactoryError: The 'obj' argument type does not fit any of the
            supported types

        Returns:
            NXobject: NeXus object respective to the data object passed as the
            data_obj argument
        """
        # Control properti for missing vakue conversion within class methods
        self.convert_missing_data = convert_missing_data
        # print(data_obj, "==================================")
        if isinstance(data_obj, Entry):
            # print("Constructor Called: ExperimentEntry")
            nxobject = self._create_entry(data_obj)

            # Dev note: Special case for entry which all data is contained on its beamline field
            nxobject.insert(self.create_nxobject(data_obj.beamline))

        elif isinstance(data_obj, Beamline):
            # print("Constructor Called: Beamline")
            nxobject = self._create_beamline(data_obj)
        elif isinstance(data_obj, Sample):
            # print("Constructor Called: Sample")
            nxobject = self._create_sample(data_obj)
        elif isinstance(data_obj, Detector):
            # print("Constructor Called: Detector")
            nxobject = self._create_detector(data_obj)
        elif isinstance(data_obj, Monochromator):
            # print("Constructor Called: Monochromator")
            nxobject = self._create_monochromator(data_obj)
        elif isinstance(data_obj, BVS):
            # print("Constructor Called: BVS")
            nxobject = self._create_bvs(data_obj)
        elif isinstance(data_obj, Mirror):
            # print("Constructor Called: Mirror")
            nxobject = self._create_mirror(data_obj)
        elif isinstance(data_obj, Slit):
            # print("Constructor Called: Slit")
            nxobject = self._create_slit(data_obj)
        elif isinstance(data_obj, Axis):
            nxobject = self._create_axis(data_obj)
        elif isinstance(data_obj, TimeSeries):
            # print("Constructor Called: TimeSeries")
            nxobject = self._create_time_series(data_obj)
        elif isinstance(data_obj, DataField):
            # print("Constructor Called: Datafield")
            nxobject = self._create_data_field(data_obj)
        elif isinstance(data_obj, DetectorROI):
            # print("Constructor Called: DetectorROI")
            nxobject = self._create_detector_roi(data_obj)
        elif isinstance(data_obj, DetectorModule):
            # print("Constructor Called: DetectorModule")
            nxobject = self._create_detector_module(data_obj)
        elif isinstance(data_obj, DetectorChannel):
            # print("Constructor Called: DetectorChannel")
            nxobject = self._create_detector_channel(data_obj)
        elif isinstance(data_obj, MonochromatorCrystal):
            # print("Constructor Called: MonochromatorCrystal")
            nxobject = self._create_monochromator_crystal(data_obj)
        elif isinstance(data_obj, MonochromatorVelocitySelector):
            # print("Constructor Called: MonochromatorVelocitySelector")
            nxobject = self._create_monochromator_velocity_selector(data_obj)
        elif isinstance(data_obj, StorageRing):
            # print("Constructor Called: StorageRing")
            nxobject = self._create_storage_ring(data_obj)
        elif isinstance(data_obj, BendingMagnet):
            # print("Constructor Called: BendingMagnet")
            nxobject = self._create_bending_magnet(data_obj)
        elif isinstance(data_obj, Undulator):
            # print("Constructor Called: Undulator")
            nxobject = self._create_undulator(data_obj)
        elif isinstance(data_obj, Wiggler):
            # print("Constructor Called: Wiggler")
            nxobject = self._create_wiggler(data_obj)
        elif isinstance(data_obj, BeamStopper):
            # print("Constructor Called: BeamStopper")
            nxobject = self._create_beam_stopper(data_obj)
        elif isinstance(data_obj, Beam):
            # print("Constructor Called: Beam")
            nxobject = self._create_beam(data_obj)
        elif isinstance(data_obj, Shutter):
            # print("Constructor Called: Shutter")
            nxobject = self._create_shutter(data_obj)
        elif isinstance(data_obj, Collimator):
            # print("Constructor Called: Collimator")
            nxobject = self._create_collimator(data_obj)
        elif isinstance(data_obj, Attenuator):
            # print("Constructor Called: Attenuator")
            nxobject = self._create_attenuator(data_obj)
        elif isinstance(data_obj, Pinhole):
            # print("Constructor Called: Pinhole")
            nxobject = self._create_pinhole(data_obj)
        elif isinstance(data_obj, FresnelZonePlate):
            # print("Constructor Called: FresnelZonePlate")
            nxobject = self._create_fresnel_zone_plate(data_obj)
        elif isinstance(data_obj, Sensor):
            # print("Constructor Called: Sesor")
            nxobject = self._create_sensor(data_obj)
        elif isinstance(data_obj, Dewar):
            # print("Constructor Called: Dewar")
            nxobject = self._create_dewar(data_obj)
        elif isinstance(data_obj, Cryojet):
            # print("Constructor Called: Cryojet")
            nxobject = self._create_cryojet(data_obj)
        elif isinstance(data_obj, GraniteBase):
            # print("Constructor Called: GraniteBase")
            nxobject = self._create_granite_base(data_obj)
        elif isinstance(data_obj, Grating):
            # print("Constructor Called: Grating")
            nxobject = self._create_grating(data_obj)
        else:
            raise NeXusObjectFactoryError(
                f"NeXus object factory doesn't have an constructor method to deal with objects of type: {type(data_obj)}"
            )

        # Check if there are subgroups to be created based on special fields
        if hasattr(data_obj, "fields"):
            # print("Constructor Called: 'fields' Dictionary")
            nxobject = self._create_fields_from_dict(nxobject, data_obj.fields)

        if hasattr(data_obj, "positions"):
            # print("Constructor Called: Transformations")
            nxobject = self._create_transformations(nxobject, data_obj.positions)

        if hasattr(data_obj, "subcomponents"):
            # print("Constructor Called: Subcomponents")
            nxobject = self._create_subcomponents(nxobject, data_obj.subcomponents)

        return NXroot(nxobject) if pack_into_nxroot is True else nxobject

    def _create_entry(self, entry: Entry) -> NXentry:
        """Private method to create the NeXus object respective to any Entry data class.

        Args:
            entry (Entry): Data object containing entry data

        Returns:
            NXentry: NeXus object respective to the Entry data object
        """
        nxobject = NXentry(name=entry.name)
        return nxobject

    def _create_sample(self, sample: Sample) -> NXsample:
        """Private method to create the NeXus object respective to the Sample data class.

        Args:
            sample (Sample): Data object containing sample data

        Returns:
            NXsample: NeXus object respective to the Sample data object
        """
        nxobject = NXsample(name=sample.name)
        return nxobject

    def _create_detector(self, detector: Detector) -> NXdetector:
        """Private method to create the NeXus object respective to the Detector data class.

        Args:
            detector (Detector): Data object containing detector data

        Returns:
            NXdetector: NeXus object respective to the Detector data object
        """
        nxobject = NXdetector(name=detector.name)

        return nxobject

    def _create_monochromator(self, monochromator: Monochromator) -> NXmonochromator:
        """Private method to create the NeXus object respective to the Monochromator data class.

        Args:
            monochromator (Monochromator): Data object containing monochromator
            data

        Returns:
            NXmonochromator: NeXus object respective to the Monochromator data
            object
        """
        nxobject = NXmonochromator(name=monochromator.name)

        return nxobject

    def _create_bvs(self, bvs: BVS) -> NXdetector:
        """Private method to create the NeXus object respective to the BVS data class.

        Args:
            bvs (BVS): Data object containing BVS data

        Returns:
            NXdetector: NeXus object respective to the BVS data object
        """
        nxobject = NXdetector(name=bvs.name)

        return nxobject

    def _create_mirror(self, mirror: Mirror) -> NXmirror:
        """Private method to create the NeXus object respective to the Mirror data class.

        Args:
            mirror (Mirror): Data object containing mirror data

        Returns:
            NXmirror: NeXus object respective to the Mirror data object
        """
        nxobject = NXmirror(name=mirror.name)

        return nxobject

    def _create_slit(self, slit: Slit) -> NXslit:
        """Private method to create the NeXus object respective to the Slit data class.

        Args:
            slit (Slit): Data object containing slit data

        Returns:
            NXslit: NeXus object respective to the Slit data object
        """
        nxobject = NXslit(name=slit.name)

        return nxobject

    def _create_time_series(self, time_series: TimeSeries) -> NXlog:
        """Private method to create the NeXus object respective to the TimeSeries data class.

        Args:
            time_series (TimeSeries): Data object containing time_series data

        Returns:
            NXlog: NeXus object respective to the TimeSeries data object
        """
        nxobject = NXlog(
            value=self.create_nxobject(time_series.value),
            time=self.create_nxobject(time_series.timestamps),
        )

        return nxobject

    def _create_axis(self, axis: Axis) -> Union[NXfield, NXlog]:
        """Private method to create the NeXus object respective to the Axis data class.

        Args:
            axis (Axis): Data object containing data related to an axis

        Returns:
            Union[NXfield, NXlog]: NeXus object respective to the Axis data object. The
            returned object may change if depending if Axis 'value' field is was collected
            as a DataField or a TimeSeries.
        """
        if isinstance(axis.value, DataField):
            nxobject = self._create_data_field(axis.value)
            nxobject.attrs["transformation_type"] = axis.transformation_type.value
        elif isinstance(axis.value, TimeSeries):
            nxobject = self._create_time_series(axis.value)
            nxobject.value.attrs["transformation_type"] = axis.transformation_type.value

        return nxobject

    def _create_data_field(self, data_field: DataField) -> NXfield:
        """Private method to create the NeXus object respective to the Field data class.

        Args:
            data_field (DataField): Data object containing a single field
            data with its respective unit

        Returns:
            NXfield: NeXus object respective to the Field data object
        """

        if self.convert_missing_data is True:
            # print("Converting missing values from DataField...")
            data_field = self._convert_none_values_from_data_field(data_field=data_field)
            # print("Missing values conversion finished.")

        attrs = data_field.extra_metadata

        if data_field.unit is not None:
            attrs["unit"] = data_field.unit

        nxobject = NXfield(value=data_field.value, attrs=attrs)

        return nxobject

    def _create_detector_roi(self, detector_roi: DetectorROI) -> NXgroup:
        """Private method to create the NeXus object respective to the DetectorROI data class.

        Args:
            detector_roi (DetectorROI): Data object containing detector region of interest (ROI) data.

        Returns:
            NXgroup: NeXus object respective to the DetectorROI data object.
        """
        # Dev note: Currently, these type of data are stored in a contributed definition called NXregion. Due
        # to that the nexusformat package don't provide support for it so the nxclass attribute must be
        # set manually.
        nxobject = NXgroup(name=detector_roi.name, nxclass="NXregion")
        return nxobject

    def _create_detector_module(self, detector_module: DetectorModule) -> NXdetector_module:
        """Private method to create the NeXus object respective to the DetectorModule data class.

        Args:
            detector_module (DetectorModule): Data object containing detector module data.

        Returns:
            NXdetector_module: NeXus object respective to the DetectorModule data object.
        """
        nxobject = NXdetector_module(name=detector_module.name)
        return nxobject

    def _create_detector_channel(self, detector_channel: DetectorChannel) -> NXdetector_channel:
        """Private method to create the NeXus object respective to the DetectorChannel data class.

        Args:
            detector_channel (DetectorChannel): Data object containing detector channel data.

        Returns:
            NXdetector_channel: NeXus object respective to the DetectorChannel data object.
        """
        nxobject = NXdetector_channel(name=detector_channel.name)
        return nxobject

    def _create_monochromator_crystal(self, monochromator_crystal: MonochromatorCrystal) -> NXcrystal:
        """Private method to create the NeXus object respective to the MonochromatorCrystal data class.

        Args:
            monochromator_crystal (MonochromatorCrystal):  Data object containing monochromator crystal data.

        Returns:
            NXcrystal: NeXus object respective to the MonochromatorCrystal data object.
        """
        nxobject = NXcrystal(name=monochromator_crystal.name)
        return nxobject

    def _create_monochromator_velocity_selector(
        self, monochromator_velocity_selector: MonochromatorVelocitySelector
    ) -> NXvelocity_selector:
        """Private method to create the NeXus object respective to the MonochromatorVelocitySelector data class.

        Args:
            monochromator_velocity_selector (MonochromatorVelocitySelector): Data object containing monochromator
            velocity selector data.

        Returns:
            NXvelocity_selector: NeXus object respective to the MonochromatorVelocitySelector data object.
        """
        nxobject = NXvelocity_selector(name=monochromator_velocity_selector.name)
        return nxobject

    def _create_storage_ring(self, storage_ring: StorageRing) -> NXsource:
        """Private method to create the NeXus object respective to the StorageRing data class.

        Args:
            storage_ring (StorageRing): Data object containing storage ring data.

        Returns:
            NXsource: NeXus object respective to the StorageRing data object.
        """
        nxobject = NXsource(name=storage_ring.name)
        return nxobject

    def _create_bending_magnet(self, bending_magnet: BendingMagnet) -> NXbending_magnet:
        """Private method to create the NeXus object respective to the BendingMagnet data class.

        Args:
            bending_magnet (BendingMagnet): Data object containing bending magnet data.

        Returns:
            NXbending_magnet: NeXus object respective to the BendingMagnet data object.
        """
        nxobject = NXbending_magnet(name=bending_magnet.name)
        return nxobject

    def _create_undulator(self, undulator: Undulator) -> NXinsertion_device:
        """Private method to create the NeXus object respective to the Undulator data class.

        Args:
            undulator (Undulator): Data object containing undulator data.

        Returns:
            NXinsertion_device: NeXus object respective to the Undulator data object.
        """
        nxobject = NXinsertion_device(name=undulator.name, type="undulator")
        return nxobject

    def _create_wiggler(self, wiggler: Wiggler) -> NXinsertion_device:
        """Private method to create the NeXus object respective to the Wiggler data class.

        Args:
            wiggler (Wiggler): Data object containing wiggler data.

        Returns:
            NXinsertion_device: NeXus object respective to the Wiggler data object.
        """
        nxobject = NXinsertion_device(name=wiggler.name, type="wiggler")
        return nxobject

    def _create_beam_stopper(self, beam_stopper: BeamStopper) -> NXbeam_stop:
        """Private method to create the NeXus object respective to the BeamStopper data class.

        Args:
            beam_stopper (BeamStopper): Data object containing beam_stopper data.

        Returns:
            NXbeam_stop: NeXus object respective to the BeamStopper data object.
        """
        nxobject = NXbeam_stop(name=beam_stopper.name)
        return nxobject

    def _create_beam(self, beam: Beam) -> NXbeam:
        """Private method to create the NeXus object respective to the Beam data class.

        Args:
            beam (Beam): Data object containing beam data.

        Returns:
            NXbeam: NeXus object respective to the Beam data object.
        """
        nxobject = NXbeam(name=beam.name)
        return nxobject

    def _create_shutter(self, shutter: Shutter) -> NXbeam_stop:
        """Private method to create the NeXus object respective to the Shutter data class.

        Args:
            shutter (Shutter): Data object containing shutter data.

        Returns:
            NXbeam_stop: NeXus object respective to the Shutter data object.
        """
        nxobject = NXbeam_stop(name=shutter.name)
        return nxobject

    def _create_collimator(self, collimator: Collimator) -> NXcollimator:
        """Private method to create the NeXus object respective to the Collimator data class.

        Args:
            collimator (Collimator): Data object containing collimator data.

        Returns:
            NXcollimator: NeXus object respective to the Collimator data object.
        """
        nxobject = NXcollimator(name=collimator.name)
        return nxobject

    def _create_attenuator(self, attenuator: Attenuator) -> NXattenuator:
        """Private method to create the NeXus object respective to the Attenuator data class.

        Args:
            attenuator (Attenuator): Data object containing attenuator data.

        Returns:
            NXattenuator: NeXus object respective to the Attenuator data object.
        """
        nxobject = NXattenuator(name=attenuator.name)
        return nxobject

    def _create_pinhole(self, pinhole: Pinhole) -> NXpinhole:
        """Private method to create the NeXus object respective to the Pinhole data class.

        Args:
            pinhole (Pinhole): Data object containing pinhole data.

        Returns:
            NXpinhole: NeXus object respective to the Pinhole data object.
        """
        nxobject = NXpinhole(name=pinhole.name)
        return nxobject

    def _create_fresnel_zone_plate(self, fresnel_zone_plate: FresnelZonePlate) -> NXfresnel_zone_plate:
        """Private method to create the NeXus object respective to the FresnelZonePlate data class.

        Args:
            fresnel_zone_plate (FresnelZonePlate): Data object containing fresnel_zone_plate data.

        Returns:
            NXfresnel_zone_plate: NeXus object respective to the FresnelZonePlate data object.
        """
        nxobject = NXfresnel_zone_plate(name=fresnel_zone_plate.name)
        return nxobject

    def _create_sensor(self, sensor: Sensor) -> NXsensor:
        """Private method to create the NeXus object respective to the Sensor data class.

        Args:
            sensor (Sensor): Data object containing sensor data.

        Returns:
            NXsensor: NeXus object respective to the Sensor data object.
        """
        nxobject = NXsensor(name=sensor.name)
        return nxobject

    def _create_grating(self, grating: Grating) -> NXgrating:
        """Private method to create the NeXus object respective to the Grating data class.

        Args:
            grating (Grating): Data object containing grating data.

        Returns:
            NXgrating: NeXus object respective to the Grating data object.
        """
        nxobject = NXgrating(name=grating.name)
        return nxobject

    def _create_dewar(self, dewar: Dewar) -> NXgroup:
        """Private method to create the NeXus object respective to the Dewar data class.

        Args:
            dewar (Dewar): Data object containing dewar data.

        Returns:
            NXgroup: NeXus object respective to the Dewar data object.
        """
        # Dev note: Currently, there is no base or contributed definition on NeXus for this type of component.
        # Due to that, a temporary nxclass value will be set to allow future automatized replacement if a
        # standard for it is defined.
        nxobject = NXgroup(name=dewar.name, nxclass="NXcustom_dewar")
        return nxobject

    def _create_cryojet(self, cryojet: Cryojet) -> NXgroup:
        """Private method to create the NeXus object respective to the Cryojet data class.

        Args:
            cryojet (Cryojet): Data object containing dewar data.

        Returns:
            NXgroup: NeXus object respective to the Cryojet data object.
        """
        # Dev note: Currently, there is no base or contributed definition on NeXus for this type of component.
        # Due to that, a temporary nxclass value will be set to allow future automatized replacement if a
        # standard for it is defined.
        nxobject = NXgroup(name=cryojet.name, nxclass="NXcustom_cryojet")
        return nxobject

    def _create_granite_base(self, granite_base: GraniteBase) -> NXgroup:
        """Private method to create the NeXus object respective to the Cryojet data class.

        Args:
            granite_base (GraniteBase): Data object containing granite base data.

        Returns:
            NXgroup: NeXus object respective to the GraniteBase data object.
        """
        # Dev note: Currently, there is no base or contributed definition on NeXus for this type of component.
        # Due to that, a temporary nxclass value will be set to allow future automatized replacement if a
        # standard for it is defined.
        nxobject = NXgroup(name=granite_base.name, nxclass="NXcustom_granite_base")
        return nxobject

    def _create_beamline(self, beamline: Beamline) -> NXinstrument:
        """Private method to create the NeXus object respective to the Beamline data class.

        Args:
            beamline (Beamline): Data object containing beamline data.

        Returns:
            NXinstrument: NeXus object respective to the Beamline data object.
        """
        nxobject = NXinstrument(name="instrument")
        nxobject["name"] = beamline.name
        return nxobject

    def _create_transformations(self, nxobject: NXobject, positions: Dict[str, Axis]) -> NXobject:
        """Create a NXtransformations group to store positioning data passed as a list of Axis objects.

        Args:
            nxobject (NXobject): NeXus object containing current objects
            positions (dict[str, Axis]): Dict of Axis objects containing each of them the positioning data related to a
            specific monitored axis.

        Returns:
           NXobject: Respective NXobject with a NXcollection group containing all fields passed.
        """
        if positions != {}:
            nxtransformations = NXtransformations(name="transformations")
            for key in positions:
                try:
                    nxtransformations[key] = self.create_nxobject(positions[key])
                except Exception:
                    raise NeXusObjectFactoryError(
                        f"Error ocurred when creating NXobject for {key} Axis from {nxobject._name} object"
                    )
            nxobject.insert(nxtransformations)
        return nxobject

    def _create_fields_from_dict(self, nxobject: NXobject, data_dict: Dict[str, DataHandler]) -> NXobject:
        """Create fields to store data passed on 'fields' dictionary from object.

        Each key, value tuple from the dictionary will be converted in a field with name equal to the tuple key.

        Args:
            nxobject (NXobject): NeXus object containing current objects
            data_dict (Dict): Dictionary containing data that will be converted to group fields.

        Raises:
            NeXusObjectFactoryError: Happens when a not supported AssonantDataClass is used on "data" dict values.

        Returns:
            NXobject: NXobject passed as input with fields set in it based on passed dictionary.
        """
        if data_dict != {}:
            for key in data_dict.keys():
                if isinstance(data_dict[key], DataField):
                    nxobject[key] = self.create_nxobject(data_dict[key])
                elif isinstance(data_dict[key], TimeSeries):
                    nxobject[key] = self.create_nxobject(data_dict[key])
                else:
                    raise NeXusObjectFactoryError(f"Expected 'data_dict[{key}]' to be a DataField or a TimeSeries")
        return nxobject

    def _create_subcomponents(self, nxobject: NXobject, subcomponents: Dict[str, Component]) -> NXobject:
        """Private method to create NeXus objects relative to subcomponents from passed NXobject.

        Args:
            subcomponents (Dict[str, Component]): Dict containing Component object which will be
            converted to their respective NXobjects and inserted on passed NXobject.

        Returns:
            NXobject: Passed NXobject updated with subcomponents groups created into it.
        """
        if subcomponents != []:
            for subcomponent_name in subcomponents:
                nxobject.insert(self.create_nxobject(subcomponents[subcomponent_name]))
        return nxobject

    def _convert_none_values_from_list(self, lst: List) -> List:
        """Transform None value within a list into np.nan.

        Args:
            lst (List): List containing values to be verified.

        Raises:
            NeXusObjectFactoryError: Raised when any error occurs when iterating the list.

        Returns:
            List: List with None values transformed into np.nan.
        """
        try:
            return [value if value is not None else np.nan for value in lst]
        except Exception as e:
            raise NeXusObjectFactoryError(f"An error ocurred when iterating list of{type(lst)} type.") from e

    def _convert_none_values_from_dict(self, d: Dict) -> Dict:
        """Transform None value within a dictionary into np.nan.

        Args:
            d (Dict): Dictionary containing values to be verified.

        Raises:
            NeXusObjectFactoryError: Raised when any error occurs when iterating dictionary elements.

        Returns:
            Dict: Dictionary with None values transformed into np.nan.
        """
        try:
            for key in d:
                if isinstance(d[key], Iterable):
                    d[key] = self._convert_none_values_from_iterable(iterable=d[key])
                elif d[key] is None:
                    d[key] = np.nan
            return d
        except Exception as e:
            raise NeXusObjectFactoryError("An error ocurred when iterating dict.") from e

    def _convert_none_values_from_iterable(self, iterable: Iterable) -> Iterable:
        if isinstance(iterable, str):
            pass  # No changed needed for this cases
        elif isinstance(iterable, List) or isinstance(iterable, np.ndarray):
            iterable = self._convert_none_values_from_list(iterable)
        elif isinstance(iterable, Dict):
            iterable = self._convert_none_values_from_dict(iterable)
        else:
            raise NeXusObjectFactoryError(
                f"Iterable from type {type(iterable)} is not suported for None values convertion."
            )

        return iterable

    def _convert_none_values_from_data_field(self, data_field: DataField) -> DataField:
        """Transform None values within a DataField value field into np.nan.

        Args:
            data_field (DataField): DataField object which value field will be verified.

        Returns:
            DataField: DataField object with None values within its value field transformed into np.nan.
        """
        try:
            if isinstance(data_field.value, Iterable):
                data_field.value = self._convert_none_values_from_iterable(iterable=data_field.value)
            elif data_field.value is None:
                data_field.value = np.nan
        except Exception as e:
            raise NeXusObjectFactoryError("An error occured when converting DataField None values.") from e

        if data_field.unit is None:
            data_field.unit = np.nan

        if data_field.extra_metadata is None:
            data_field.extra_metadata = {}

        return data_field
