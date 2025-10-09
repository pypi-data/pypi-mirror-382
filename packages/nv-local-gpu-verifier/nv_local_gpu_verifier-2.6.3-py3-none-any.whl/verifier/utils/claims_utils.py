#
# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import hashlib
from datetime import datetime, timedelta
from typing import List, Any
import string
import uuid
from urllib import request
from urllib.error import HTTPError
import json
import base64
import jwt

from verifier.attestation import AttestationReport
from verifier.config import (
    BaseSettings,
    info_log,
    event_log,
)


class ClaimsUtils:
    """ A class to provide the required functionalities for claims related utility functions
    """

    @staticmethod
    def get_current_gpu_claims(settings, gpu_uuid: string = ""):
        """
            Method to translate GPU Attestation results to Claims object
            Args:
                settings:  Hopper Settings object
                gpu_uuid:  UUID of the GPU
        """
        if BaseSettings.CLAIMS_VERSION == "3.0":
            claims = {'measres': settings.check_if_measurements_are_matching(),
                      "x-nvidia-gpu-arch-check": settings.check_if_gpu_arch_is_correct(),
                      "x-nvidia-gpu-driver-version": settings.check_gpu_driver_version(),
                      "x-nvidia-gpu-vbios-version": settings.check_gpu_vbios_version(),
                      "x-nvidia-gpu-attestation-report-cert-chain":
                      {
                          "x-nvidia-cert-expiration-date": settings.check_gpu_attestation_report_cert_expiration_date(),
                          "x-nvidia-cert-status": settings.check_gpu_attestation_report_cert_status(),
                          "x-nvidia-cert-ocsp-status": settings.check_gpu_attestation_report_cert_ocsp_status(),
                          "x-nvidia-cert-revocation-reason": settings.check_gpu_attestation_report_cert_revocation_reason()
                      },
                      "x-nvidia-gpu-attestation-report-cert-chain-fwid-match": settings.check_if_gpu_attestation_report_cert_chain_fwid_matched(),
                      "x-nvidia-gpu-attestation-report-parsed": settings.check_if_attestation_report_parsed_successfully(),
                      "x-nvidia-gpu-attestation-report-nonce-match": settings.check_if_nonce_are_matching(),
                      "x-nvidia-gpu-attestation-report-signature-verified": settings.check_if_attestation_report_signature_verified(),
                      "x-nvidia-gpu-driver-rim-fetched": settings.check_if_driver_rim_fetched(),
                      "x-nvidia-gpu-driver-rim-schema-validated": settings.check_if_gpu_driver_rim_schema_validated(),
                      "x-nvidia-gpu-driver-rim-cert-chain":
                      {
                          "x-nvidia-cert-expiration-date": settings.check_gpu_driver_rim_cert_expiration_date(),
                          "x-nvidia-cert-status": settings.check_gpu_driver_rim_cert_status(),
                          "x-nvidia-cert-ocsp-status": settings.check_gpu_driver_rim_cert_ocsp_status(),
                          "x-nvidia-cert-revocation-reason": settings.check_gpu_driver_rim_cert_revocation_reason()
                      },
                      "x-nvidia-gpu-driver-rim-signature-verified": settings.check_if_gpu_driver_rim_signature_verified(),
                      "x-nvidia-gpu-driver-rim-version-match":settings.check_if_gpu_driver_rim_version_matched(),
                      "x-nvidia-gpu-driver-rim-measurements-available": settings.check_rim_driver_measurements_availability(),
                      "x-nvidia-gpu-vbios-rim-fetched": settings.check_if_vbios_rim_fetched(),
                      "x-nvidia-gpu-vbios-rim-schema-validated": settings.check_if_gpu_vbios_rim_schema_validated(),
                      "x-nvidia-gpu-vbios-rim-cert-chain":
                      {
                          "x-nvidia-cert-expiration-date": settings.check_gpu_vbios_rim_cert_expiration_date(),
                          "x-nvidia-cert-status": settings.check_gpu_vbios_rim_cert_status(),
                          "x-nvidia-cert-ocsp-status": settings.check_gpu_vbios_rim_cert_ocsp_status(),
                          "x-nvidia-cert-revocation-reason": settings.check_gpu_vbios_rim_cert_revocation_reason()
                      },
                      "x-nvidia-gpu-vbios-rim-version-match": settings.check_if_gpu_vbios_rim_version_matched(),
                      "x-nvidia-gpu-vbios-rim-signature-verified": settings.check_if_gpu_vbios_rim_signature_verified(),
                      "x-nvidia-gpu-vbios-rim-measurements-available": settings.check_rim_vbios_measurements_availability(),
                      "x-nvidia-gpu-vbios-index-no-conflict": settings.check_if_no_driver_vbios_measurement_index_conflict()
                      }
        elif BaseSettings.CLAIMS_VERSION == "2.0":
            claims = {'measres': settings.check_if_measurements_are_matching() or "fail",
                      "x-nvidia-gpu-arch-check": settings.check_if_gpu_arch_is_correct() or False,
                      "x-nvidia-gpu-driver-version": settings.check_gpu_driver_version() or "",
                      "x-nvidia-gpu-vbios-version": settings.check_gpu_vbios_version() or "",
                      "x-nvidia-gpu-attestation-report-cert-chain-validated": settings.check_if_gpu_attestation_report_cert_chain_validated() or False,
                      "x-nvidia-gpu-attestation-report-parsed": settings.check_if_attestation_report_parsed_successfully() or False,
                      "x-nvidia-gpu-attestation-report-nonce-match": settings.check_if_nonce_are_matching() or False,
                      "x-nvidia-gpu-attestation-report-signature-verified": settings.check_if_attestation_report_signature_verified() or False,
                      "x-nvidia-gpu-driver-rim-fetched": settings.check_if_driver_rim_fetched() or False,
                      "x-nvidia-gpu-driver-rim-schema-validated": settings.check_if_gpu_driver_rim_schema_validated() or False,
                      "x-nvidia-gpu-driver-rim-cert-validated": settings.check_if_gpu_driver_rim_cert_chain_validated() or False,
                      "x-nvidia-gpu-driver-rim-signature-verified": settings.check_if_gpu_driver_rim_signature_verified() or False,
                      "x-nvidia-gpu-driver-rim-measurements-available": settings.check_rim_driver_measurements_availability() or False,
                      "x-nvidia-gpu-vbios-rim-fetched": settings.check_if_vbios_rim_fetched() or False,
                      "x-nvidia-gpu-vbios-rim-schema-validated": settings.check_if_gpu_vbios_rim_schema_validated() or False,
                      "x-nvidia-gpu-vbios-rim-cert-validated": settings.check_if_gpu_vbios_rim_cert_chain_validated() or False,
                      "x-nvidia-gpu-vbios-rim-signature-verified": settings.check_if_gpu_vbios_rim_signature_verified() or False,
                      "x-nvidia-gpu-vbios-rim-measurements-available": settings.check_rim_vbios_measurements_availability() or False,
                      "x-nvidia-gpu-vbios-index-no-conflict": settings.check_if_no_driver_vbios_measurement_index_conflict() or False
                      }
        else:
            return {}
        if settings.check_if_measurements_are_matching() == "success":
            claims["secboot"] = True
            claims["dbgstat"] = "disabled"
        return claims

    def get_overall_claims(nonce):
        overallAttestationToken = {}
        overallAttestationToken["sub"] = "NVIDIA-PLATFORM-ATTESTATION"
        overallAttestationToken["nbf"] = datetime.utcnow() - timedelta(seconds=120)
        overallAttestationToken["exp"] = datetime.utcnow() + timedelta(hours=1)
        overallAttestationToken["iat"] = datetime.utcnow()
        overallAttestationToken["jti"] = str(uuid.uuid4())
        overallAttestationToken["x-nvidia-ver"] = BaseSettings.CLAIMS_VERSION
        overallAttestationToken["iss"] = "LOCAL_GPU_VERIFIER"
        overallAttestationToken["x-nvidia-overall-att-result"] = "false"
        overallAttestationToken["submods"] = {}
        overallAttestationToken["eat_nonce"] = nonce
        return overallAttestationToken

    @staticmethod
    def create_detached_eat_claims(attest_result: bool, gpu_claims_list: List[Any], nonce: str, hwmodel: str, oemid: str, ueid: str, driver_warnings: List[str], vbios_warnings: List[str]):

        """Utility method to create detached EAT claims for a specific attestation token.

        Args:
            attest_result (bool): Represents overall attestation result.
            gpu_claims_list (list): List of GPU claims.
            nonce (str): Nonce represented as string.
            hwmodel (str): Hardware model.
            oemid (str): OEM identifier.
            ueid (str): Unique Entity Identifier
            driver_warnings (list): List of driver-related warnings captured during Attestation.
            vbios_warnings (list): List of vBIOS-related warnings captured during Attestation.

        Returns:
            list: Detached claims represented as a array.
        """

        gpu_detached_claims = []
        overall_encoded_claim_arr = []
        overall_encoded_claim_arr.append("JWT")
        overall_claims = ClaimsUtils.get_overall_claims(nonce)
        overall_claims["x-nvidia-overall-att-result"] = attest_result

        gpu_claims_dict = {}
        submods_dict = {}
        for i, gpu_claims in enumerate(gpu_claims_list):
            warning = ""
            dict_key = "GPU-" + str(i)
            jwt.encode(gpu_claims, 'secret', "HS256")
            gpu_claims["eat_nonce"] = nonce
            gpu_claims["hwmodel"] = hwmodel[i] if i < len(hwmodel) else None
            gpu_claims["ueid"] = str(ueid[i]) if i < len(ueid) else ""
            gpu_claims["oemid"] = oemid[i] if i < len(oemid) else None
            gpu_claims["iss"] = "LOCAL_GPU_VERIFIER"
            if i < len(driver_warnings) and driver_warnings[i]:
                warning = driver_warnings[i]
            if i < len(vbios_warnings) and vbios_warnings[i]:
                warning += " " + vbios_warnings[i]
            if warning is not "":
                gpu_claims["x-nvidia-attestation-warning"] = warning
            gpu_claims_json = json.dumps(gpu_claims)
            submods_dict[dict_key] = ["DIGEST", ["SHA256", hashlib.sha256(gpu_claims_json.encode('utf-8')).hexdigest()]]
            gpu_claims["nbf"] = datetime.utcnow() - timedelta(seconds=120)
            gpu_claims["exp"] = datetime.utcnow() + timedelta(hours=1)
            gpu_claims["iat"] = datetime.utcnow()
            gpu_claims["jti"] = str(uuid.uuid4())
            gpu_claims_dict[dict_key] = jwt.encode(gpu_claims, 'secret', "HS256")

        overall_claims["submods"] = submods_dict
        overall_encoded_claim = jwt.encode(overall_claims,
                                           'secret',
                                           "HS256")
        overall_encoded_claim_arr.append(overall_encoded_claim)
        gpu_detached_claims.append(overall_encoded_claim_arr)
        gpu_detached_claims.append(gpu_claims_dict)
        #detached_eat_json = json.dumps(gpu_detached_claims, indent = 2) 
        return gpu_detached_claims
