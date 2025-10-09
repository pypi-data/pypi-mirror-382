#
# SPDX-FileCopyrightText: Copyright (c) 2021-2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from verifier.config import (
    BaseSettings,
    info_log,
    __author__,
    __copyright__,
    __version__,
)
from verifier.utils import is_zeros
from verifier.exceptions import InvalidMeasurementIndexError


class Verifier:
    """ A class to match the runtime GPU measurements against the golden
    measurements.
    """

    def verify(self, settings):
        """ This methods compares the runtime measurement with the golden measurement in order to check if there is any discrepancy.

        Args:
            settings (config.HopperSettings): the object containing the various config info.

        Returns:
            [bool]: returns True if all the valid golden measurements values matches with the
            corresponding runtime measurements. Otherwise, returns False.
        """
        info_log.info("\tComparing measurements (runtime vs golden)")

        if len(self.runtime_measurements) == 0:
            info_log.warning("\t\t\tWarning : no measurements from attestation report received.")

        if len(self.golden_measurements) == 0:
            info_log.warning("\t\t\tWarning : no golden measurements from RIMs received.")

        # Make sure that active golden measurement are always less than or equal to run time measurement
        if len(self.golden_measurements) > len(self.runtime_measurements):
            info_log.info("\t\t\tWarning : Golden measurement are more than measurements in Attestation report.")
            return False

        list_of_mismatched_indexes = list()

        for i in self.golden_measurements:

            if i == 35 and not self.is_msr_35_valid:
                continue

            is_matching = False
            golden_measurement = self.golden_measurements[i]["measurement"]
            measurement_source = self.golden_measurements[i]["source"]

            for j in range(golden_measurement.get_number_of_alternatives()):

                if golden_measurement.get_value_at_index(j) == self.runtime_measurements[i] and \
                   golden_measurement.get_size() == len(self.runtime_measurements[i]) // 2:

                    is_matching = True

            if not is_matching:
                # Measurements are not matching.
                list_of_mismatched_indexes.append((i, measurement_source))

        if len(list_of_mismatched_indexes) > 0:
            
            info_log.info("""\t\t\tThe runtime measurements are not matching with the
                        golden measurements at the following indexes(starting from 0) :\n\t\t\t[""")
            
            list_of_mismatched_indexes.sort(key=lambda x: x[0]) # Sort by index
            
            for (idx, source) in list_of_mismatched_indexes:
                info_log.info(f'\t\t\t{idx} [{source}]')
            info_log.info("\t\t\t]")
            settings.mark_measurements_as_matching(False)
            return False
        else:
            info_log.info("\t\t\tThe runtime measurements are matching with the golden measurements.\
                            \n\t\tGPU is in expected state.")
            settings.mark_measurements_as_matching()
            return True
    
    def generate_golden_measurement_list(self, driver_golden_measurements, vbios_golden_measurements, settings):
        """ This method takes the driver and vbios golden measurements and
        combines them into a single dictionary with the measurement index as
        the key and the golden measurement object as the value.

        Args:
            driver_golden_measurements (dict): the dictionary containing the driver golden measurements.
            vbios_golden_measurements (dict): the dictionary containing the vbios golden measurements.
            settings (config.HopperSettings): the object containing the various config info.

        Raises:
            InvalidMeasurementIndexError: it is raised in case both the driver and vbios RIM file have 
                                          active measurement at the same index.
        """
        self.golden_measurements = dict()
        
        for gld_msr_idx in driver_golden_measurements:
            
            if driver_golden_measurements[gld_msr_idx].is_active():
                self.golden_measurements[gld_msr_idx] = {
                    "measurement": driver_golden_measurements[gld_msr_idx],
                    "source": "Driver"
                }

        for gld_msr_idx in vbios_golden_measurements:

            if vbios_golden_measurements[gld_msr_idx].is_active() and \
               gld_msr_idx in self.golden_measurements:
               settings.mark_no_driver_vbios_measurement_index_conflict(False)
               raise InvalidMeasurementIndexError(f"The driver and vbios RIM have measurement at the same index : {gld_msr_idx}")
            
            elif vbios_golden_measurements[gld_msr_idx].is_active():
                self.golden_measurements[gld_msr_idx] = {
                    "measurement": vbios_golden_measurements[gld_msr_idx],
                    "source": "Firmware"
                }
        
        settings.mark_no_driver_vbios_measurement_index_conflict()

    def __init__(self, attestation_report_obj, driver_rim_obj, vbios_rim_obj, settings):
        """ The constructor method for the Verifier class.

        Args:
            attestation_report_obj (AttestationReport): the attestation report.
            driver_rim_obj (rim.RIM): the driver RIM object containing the the driver golden measurements.
            vbios_rim_obj (rim.RIM): the vbios RIM object containing the vbios golden measurement.
            settings (config.HopperSettings): the object containing the various config info.
        """
        self.is_msr_35_valid = True

        if attestation_report_obj.get_response_message().get_opaque_data().get_data("OPAQUE_FIELD_ID_NVDEC0_STATUS") == BaseSettings.NVDEC_STATUS.DISABLED:
            self.is_msr_35_valid = False

        self.generate_golden_measurement_list(driver_rim_obj.get_measurements(), vbios_rim_obj.get_measurements(), settings)
        self.runtime_measurements = attestation_report_obj.get_measurements()
