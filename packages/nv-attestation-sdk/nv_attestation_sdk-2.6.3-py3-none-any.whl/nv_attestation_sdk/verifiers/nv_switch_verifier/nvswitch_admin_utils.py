#
# SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os
import secrets
import string
import sys
from urllib import request
from urllib.error import HTTPError
import json
import base64
import logging
import urllib

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.hashes import SHA384
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.x509 import ocsp, OCSPNonce, ExtensionNotFound
from cryptography import x509
from datetime import datetime

from nv_attestation_sdk.verifiers.nv_switch_verifier.attestation import AttestationReport
from nv_attestation_sdk.verifiers.nv_switch_verifier.config import (
    BaseSettings,
)
from nv_attestation_sdk.utils.headers import SERVICE_KEY_VALUE

from nv_attestation_sdk.verifiers.nv_switch_verifier.utils import (
    format_vbios_version,
    function_wrapper_with_timeout,
)
from nv_attestation_sdk.verifiers.nv_switch_verifier.exceptions import (
    NoCertificateError,
    IncorrectNumberOfCertificatesError,
    NonceMismatchError,
    SignatureVerificationError,
    RIMFetchError,
    InvalidNonceError
)
from nv_attestation_sdk.utils.logging_config import get_logger

logger = get_logger()


class NVSwitchAdminUtils:
    """ A class to provide the required functionalities to perform the Switch attestation.
    """

    @staticmethod
    def extract_fwid(cert):
        """ A static function to extract the FWID data from the given certificate.

        Args:
            cert (OpenSSL.crypto.X509): The certificate whose FWID data is needed to be fetched.

        Returns:
            [str]: the FWID as a hex string extracted from the certificate if
                   it is present otherwise returns an empty string.
        """
        result = ''
        # The OID for the FWID extension.
        TCG_DICE_FWID_OID = '2.23.133.5.4.1'
        cryptography_cert = cert.to_cryptography()

        for i in range(len(cryptography_cert.extensions)):
            oid_obj = (vars(cryptography_cert.extensions)['_extensions'][i]).oid
            if getattr(oid_obj, 'dotted_string') == TCG_DICE_FWID_OID:
                # The FWID data is the last 48 bytes.
                result = vars((vars(cryptography_cert.extensions)['_extensions'][i]).value)['_value'][-48:].hex()

        return result

    @staticmethod
    def verify_switch_certificate_chain(cert_chain, settings, attestation_report_fwid):
        """ A static function to perform the Switch certificate chain verification.

        Args:
            cert_chain (list): A list containing the certificate objects of the device certificate chain.
            settings (config.LS10Settings): the object containing the various config info.
            attestation_report_fwid (str): the hexadecimal string of the FWID in the attestation report.

        Returns:
            [bool]: True if the verification is successful, otherwise False.
        """
        # Skipping the comparision of FWID in the attestation certificate if the Attestation report does not contains the FWID.
        if attestation_report_fwid != '':
            if attestation_report_fwid != NVSwitchAdminUtils.extract_fwid(cert_chain[0]):
                logger.error(
                    "\t\tThe firmware ID in the device certificate chain is not matching with the one in the attestation report.")
                logger.debug(f"\t\tThe FWID read from the attestation report is : {attestation_report_fwid}")
                settings.mark_switch_attestation_report_cert_chain_fwid_matched(False)
                return False

            logger.info(
                "\t\tThe firmware ID in the device certificate chain is matching with the one in the attestation report.")

        settings.mark_switch_attestation_report_cert_chain_fwid_matched()
        return NVSwitchAdminUtils.verify_certificate_chain(cert_chain, settings,
                                                           BaseSettings.Certificate_Chain_Verification_Mode.SWITCH_ATTESTATION)

    @staticmethod
    def verify_certificate_chain(cert_chain, settings, mode):
        """ Performs the certificate chain verification.

        Args:
            cert_chain (list): the certificate chain as a list with the root
                               cert at the end of the list.
            settings (config.LS10Settings): the object containing the various config info.
            mode (<enum 'CERT CHAIN VERIFICATION MODE'>): Used to determine if the certificate chain
                            verification is for the Switch attestation certificate chain or RIM certificate chain
                            or the ocsp response certificate chain.

        Raises:
            NoCertificateError: it is raised if the cert_chain list is empty.
            IncorrectNumberOfCertificatesError: it is raised if the number of
                                certificates in cert_chain list is unexpected.

        Returns:
            [bool]: True if the verification is successful, otherwise False.
        """
        assert isinstance(cert_chain, list)

        number_of_certificates = len(cert_chain)
        switch_attestation_warning = ""

        logger.debug(f"verify_certificate_chain() called for {str(mode)}")
        logger.debug(f'Number of certificates : {number_of_certificates}')

        if number_of_certificates < 1:
            logger.error("\t\tNo certificates found in certificate chain.")
            raise NoCertificateError("\t\tNo certificates found in certificate chain.")

        if number_of_certificates != settings.MAX_CERT_CHAIN_LENGTH and mode == BaseSettings.Certificate_Chain_Verification_Mode.SWITCH_ATTESTATION:
            logger.error("\t\tThe number of certificates fetched from the Switch is unexpected.")
            raise IncorrectNumberOfCertificatesError(
                "\t\tThe number of certificates fetched from the Switch is unexpected.")

        store = crypto.X509Store()
        earliest_expiration_iso8601 = None
        expired = False
        index = number_of_certificates - 1
        while index > -1:
            expiration_iso8601 = datetime.strptime(cert_chain[index].get_notAfter().decode('ascii'),
                                                   '%Y%m%d%H%M%SZ').isoformat()
            if earliest_expiration_iso8601 is None or expiration_iso8601 < earliest_expiration_iso8601:
                earliest_expiration_iso8601 = expiration_iso8601

            if index == number_of_certificates - 1:
                # The root CA certificate is stored at the end in the cert chain.
                store.add_cert(cert_chain[index])
                index = index - 1
            else:
                try:
                    store_context = crypto.X509StoreContext(store, cert_chain[index])
                    store_context.verify_certificate()
                    store.add_cert(cert_chain[index])
                    index = index - 1
                except crypto.X509StoreContextError as e:
                    X509_V_ERR_CERT_HAS_EXPIRED = 10
                    if e.errors[0] == X509_V_ERR_CERT_HAS_EXPIRED:
                        expired = True
                        logger.debug(f'Certificate chain verification failed because of expired cert at index {index}.')
                        logger.error(e)
                        return False, expired, earliest_expiration_iso8601
                    else:
                        logger.debug(f'Cert chain verification is failing at index : {index}')
                        logger.error(e)
                        return False, expired, earliest_expiration_iso8601
        return True, expired, earliest_expiration_iso8601

    @staticmethod
    def convert_cert_from_cryptography_to_pyopenssl(cert):
        """ A static method to convert the "Cryptography" X509 certificate object to "pyOpenSSL"
        X509 certificate object.

        Args:
            cert (cryptography.hazmat.backends.openssl.x509._Certificate): the input certificate object.

        Returns:
            [OpenSSL.crypto.X509]: the converted X509 certificate object.
        """
        return crypto.load_certificate(type=crypto.FILETYPE_ASN1, buffer=cert.public_bytes(serialization.Encoding.DER))

    @staticmethod
    def ocsp_certificate_chain_validation(cert_chain, settings, mode):
        """ A static method to perform the ocsp status check of the input certificate chain along with the
        signature verification and the cert chain verification if the ocsp response message received.

        Args:
            cert_chain (list): the list of the input certificates of the certificate chain.
            settings (config.LS10Settings): the object containing the various config info.
            mode (<enum 'CERT CHAIN VERIFICATION MODE'>): Used to determine if the certificate chain
                            verification is for the Switch attestation certificate chain or RIM certificate chain
                            or the ocsp response certificate chain.

        Returns:
            [Bool]: True if the ocsp status of all the appropriate certificates in the
                    certificate chain, otherwise False.
        """
        assert isinstance(cert_chain, list)
        revoked_status = False
        start_index = 0
        switch_attestation_warning = ""
        ocsp_status = None
        revocation_reason = None

        if mode == BaseSettings.Certificate_Chain_Verification_Mode.SWITCH_ATTESTATION:
            start_index = 1

        end_index = len(cert_chain) - 1

        for i, cert in enumerate(cert_chain):
            cert_chain[i] = cert.to_cryptography()

        for i in range(start_index, end_index):
            request_builder = ocsp.OCSPRequestBuilder()
            request_builder = request_builder.add_certificate(cert_chain[i], cert_chain[i + 1], SHA384())
            if not settings.ocsp_nonce_disabled:
                nonce = NVSwitchAdminUtils.generate_nonce(BaseSettings.SIZE_OF_NONCE_IN_BYTES)
                request_builder = request_builder.add_extension(extval=OCSPNonce(nonce),
                                                                critical=True)

            request = request_builder.build()
            # Making the network call in a separate thread.
            ocsp_response = function_wrapper_with_timeout([NVSwitchAdminUtils.send_ocsp_request,
                                                           request.public_bytes(serialization.Encoding.DER),
                                                           "send_ocsp_request"],
                                                          logger,
                                                          BaseSettings.MAX_OCSP_TIME_DELAY)

            # Verifying the ocsp response certificate chain.
            ocsp_response_leaf_cert = crypto.load_certificate(type=crypto.FILETYPE_ASN1,
                                                              buffer=ocsp_response.certificates[0].public_bytes(
                                                                  serialization.Encoding.DER))

            ocsp_cert_chain = [ocsp_response_leaf_cert]

            for j in range(i, len(cert_chain)):
                ocsp_cert_chain.append(NVSwitchAdminUtils.convert_cert_from_cryptography_to_pyopenssl(cert_chain[j]))

            ocsp_cert_chain_verification_status, ocsp_cert_expired, ocsp_cert_expiration_date = NVSwitchAdminUtils.verify_certificate_chain(
                ocsp_cert_chain,
                settings,
                BaseSettings.Certificate_Chain_Verification_Mode.OCSP_RESPONSE)

            if not ocsp_cert_chain_verification_status:
                logger.error(
                    f"\t\tThe ocsp response certificate chain verification failed for {cert_chain[i].subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value}.")
                return False, switch_attestation_warning, ocsp_status, revocation_reason
            elif i == end_index - 1:
                logger.debug("\t\tSwitch Certificate OCSP Cert chain is verified")
            # Verifying the signature of the ocsp response message.
            if not NVSwitchAdminUtils.verify_ocsp_signature(ocsp_response):
                logger.error(
                    f"\t\tThe ocsp response response for certificate {cert_chain[i].subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value} failed due to signature verification failure.")
                return False, switch_attestation_warning, ocsp_status, revocation_reason
            elif i == end_index - 1:
                logger.debug("\t\tSwitch Certificate OCSP Signature is verified")

            try:
                if not settings.ocsp_nonce_disabled:
                    if nonce != ocsp_response.extensions.get_extension_for_class(OCSPNonce).value.nonce:
                        logger.error(
                            "\t\tThe nonce in the OCSP response message is not matching with the one passed in the OCSP request message.")
                        return False, switch_attestation_warning, ocsp_status, revocation_reason
                    elif i == end_index - 1:
                        logger.debug("\t\tSwitch Certificate OCSP Nonce is matching")
            except ExtensionNotFound:
                info_log.error(
                    "\t\tOCSP response does not contain a nonce extension. If OCSP nonce validation is not required in your environment, consider disabling the nonce check.")
                return False, switch_attestation_warning, ocsp_status, revocation_reason

            if ocsp_response.response_status != ocsp.OCSPResponseStatus.SUCCESSFUL:
                logger.error("\t\tCouldn't receive a proper response from the OCSP server.")
                return False, switch_attestation_warning, ocsp_status, revocation_reason

            # OCSP response can have 3 status - Good, Revoked (with a reason) or Unknown
            if ocsp_response.certificate_status != ocsp.OCSPCertStatus.GOOD:

                if x509.ReasonFlags.certificate_hold == ocsp_response.revocation_reason and \
                        BaseSettings.allow_hold_cert and \
                        (
                                mode == BaseSettings.Certificate_Chain_Verification_Mode.VBIOS_RIM_CERT):
                    warning = f"THE CERTIFICATE {cert_chain[i].subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value} IS REVOKED WITH THE STATUS AS 'CERTIFICATE_HOLD'."
                    logger.warning(
                        f"\t\t\tWARNING: {warning}")
                    ocsp_status = "revoked"
                    revocation_reason = ocsp_response.revocation_reason.name
                    switch_attestation_warning = warning
                    revoked_status = True
                elif ocsp_response.certificate_status == ocsp.OCSPCertStatus.UNKNOWN:
                    ocsp_status = "unknown"
                    logger.error(
                        f"\t\t\tTHE {cert_chain[i].subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value} certificate status is UNKNOWN")
                    return False, switch_attestation_warning, ocsp_status, revocation_reason
                else:
                    ocsp_status = "revoked"
                    revocation_reason = ocsp_response.revocation_reason.name
                    logger.error(
                        f"\t\t\tTHE {cert_chain[i].subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value} IS REVOKED FOR REASON : {ocsp_response.revocation_reason.name}")
                    return False, switch_attestation_warning, ocsp_status, revocation_reason

        if not revoked_status:
            logger.info(f"\t\t\tThe certificate chain revocation status verification successful.")
        else:
            logger.warning(
                f"\t\t\tThe certificate chain revocation status verification was not successful but continuing.")
        ocsp_status = ocsp_status or "good"
        return True, switch_attestation_warning, ocsp_status, revocation_reason

    @staticmethod
    def send_ocsp_request(data):
        """ A static method to prepare http request and send it to the ocsp server
        and returns the ocsp response message.

        Args:
            data (bytes): the raw ocsp request message.

        Returns:
            [cryptography.hazmat.backends.openssl.ocsp._OCSPResponse]: the ocsp response message object.
        """
        try:
            https_request = request.Request(BaseSettings.OCSP_URL, data)
            https_request.add_header("Content-Type", "application/ocsp-request")
            if BaseSettings.service_key:
                https_request.add_header("Authorization", SERVICE_KEY_VALUE.format(BaseSettings.service_key))

            with request.urlopen(
                    https_request) as https_response:  # nosec taken care of the security issue by checking for the url to start with "http"
                ocsp_response = ocsp.load_der_ocsp_response(https_response.read())

            return ocsp_response
        except Exception as e:
            raise Exception("OCSP request failed") from e

    @staticmethod
    def verify_ocsp_signature(ocsp_response):
        """ A static method to perform the signature verification of the ocsp response message.

        Args:
            ocsp_response (cryptography.hazmat.backends.openssl.ocsp._OCSPResponse): the input ocsp response message object.

        Returns:
            [Bool]: returns True if the signature verification is successful, otherwise returns False.
        """
        try:
            signature = ocsp_response.signature
            data = ocsp_response.tbs_response_bytes
            leaf_certificate = ocsp_response.certificates[0]
            leaf_certificate.public_key().verify(signature, data, ec.ECDSA(SHA384()))
            return True

        except InvalidSignature:
            return False

        except Exception as error:
            err_msg = "Something went wrong during ocsp signature verification."
            logger.error(error)
            return False

    @staticmethod
    def fetch_rim_file(file_id):
        """ A static method to fetch the RIM file with the given file id from the RIM service.

        Args:
            file_id (str): the RIM file id which need to be fetched from the RIM service.

        Returns:
            [str]: the content of the required RIM file as a string.
        """
        headers = {}
        if BaseSettings.service_key:
            headers['Authorization'] = SERVICE_KEY_VALUE.format(BaseSettings.service_key)

        try:
            req = urllib.request.Request(BaseSettings.RIM_SERVICE_BASE_URL + file_id, headers=headers)
            with request.urlopen(req) as https_response:
                data = https_response.read()
                json_object = json.loads(data)
                base64_data = json_object['rim']
                decoded_str = base64.b64decode(base64_data)
                return decoded_str.decode('utf-8')
        except HTTPError:
            logger.error("Could not fetch rim file from RIM service with id : " + file_id)
            raise RIMFetchError(f'Unable to fetch RIM file from RIM service: {file_id}')

    @staticmethod
    def get_vbios_rim_file_id(project, project_sku, chip_sku, vbios_version):
        """ A static method to generate the required VBIOS RIM file id which needs to be fetched from the RIM service
            according to the vbios flashed onto the system.

        Args:
            attestation_report (AttestationReport): the object representing the attestation report.

        Returns:
            [str]: the VBIOS RIM file id.
        """
        base_str = 'NV_SWITCH_BIOS_'

        return base_str + project + "_" + project_sku + "_" + chip_sku + "_" + vbios_version

    @staticmethod
    def get_vbios_rim_path(settings, attestation_report):
        """ A static method to determine the path of the appropriate VBIOS RIM file.

        Args:
            settings (config.LS10Settings): the object containing the various config info.
            attestation_report (AttestationReport): the object representing the attestation report

        Raises:
            RIMFetchError: it is raised in case the required VBIOS RIM file is not found.

        Returns:
            [str] : the path to the VBIOS RIM file.
        """
        project_sku = attestation_report.get_response_message().get_opaque_data().get_data(
            "OPAQUE_FIELD_ID_PROJECT_SKU")
        chip_sku = attestation_report.get_response_message().get_opaque_data().get_data("OPAQUE_FIELD_ID_CHIP_SKU")
        vbios_version = format_vbios_version(
            attestation_report.get_response_message().get_opaque_data().get_data("OPAQUE_FIELD_ID_VBIOS_VERSION"))
        vbios_version = vbios_version.replace(".", "").upper()

        project = BaseSettings.PROJECT
        project_sku = BaseSettings.PROJECT_SKU
        chip_sku = BaseSettings.CHIP_SKU

        rim_file_name = project + "_" + project_sku + "_" + chip_sku + "_" + vbios_version + "_" + settings.get_sku() + ".swidtag"
        list_of_files = os.listdir(settings.RIM_DIRECTORY_PATH)
        rim_path = os.path.join(settings.RIM_DIRECTORY_PATH, rim_file_name)

        if rim_file_name in list_of_files:
            return rim_path

        raise RIMFetchError(f"Could not find the required VBIOS RIM file : {rim_path}")

    @staticmethod
    def verify_attestation_report(attestation_report_obj, switch_leaf_certificate, nonce,
                                  vbios_version, settings):
        """ Performs the verification of the attestation report. This contains matching the nonce in the attestation report with
        the one generated by the cc admin, matching the driver version and vbios version in the attestation report with the one
        fetched from the driver. And then performing the signature verification of the attestation report.

        Args:
            attestation_report_obj (SpdmMeasurementResponseMessage): the object representing the attestation report.
            switch_leaf_certificate (OpenSSL.crypto.X509): the Switch leaf attestation certificate.
            nonce (bytes): the nonce generated by the cc_admin.
            vbios_version (str): the vbios version fetched from the Switch.
            settings (config.LS10Settings): the object containing the various config info.

        Raises:
            NonceMismatchError: it is raised in case the nonce generated by cc admin does not match with the one in the attestation report.
            VBIOSVersionMismatchError: it is raised in case of the vbios version does not matches with the one in the attestation report.
            SignatureVerificationError: it is raised in case the signature verification of the attestation report fails.

        Returns:
            [bool]: return True if the signature verification is successful.
        """
        assert isinstance(attestation_report_obj, AttestationReport)
        assert isinstance(switch_leaf_certificate, crypto.X509)
        assert isinstance(nonce, bytes) and len(nonce) == settings.SIZE_OF_NONCE_IN_BYTES
        # Here the attestation report is the concatenated SPDM GET_MEASUREMENTS request with the SPDM GET_MEASUREMENT
        # response message.
        request_nonce = attestation_report_obj.get_request_message().get_nonce()

        if len(nonce) > settings.SIZE_OF_NONCE_IN_BYTES or len(request_nonce) > settings.SIZE_OF_NONCE_IN_BYTES:
            err_msg = "\t\t Length of Nonce is greater than max nonce size allowed."
            logger.error(err_msg)
            raise InvalidNonceError(err_msg)
        # compare the generated nonce with the nonce of SPDM GET MEASUREMENT request message in the attestation report.
        if request_nonce != nonce:
            err_msg = "\t\tThe nonce in the SPDM GET MEASUREMENT request message is not matching with the generated nonce."
            logger.error(err_msg)
            settings.mark_nonce_as_matching(False)
            raise NonceMismatchError(err_msg)
        else:
            logger.info(
                "\t\tThe nonce in the SPDM GET MEASUREMENT request message is matching with the generated nonce.")
            settings.mark_nonce_as_matching()

        # Checking vbios version.
        vbios_version_from_attestation_report = attestation_report_obj.get_response_message().get_opaque_data().get_data(
            "OPAQUE_FIELD_ID_VBIOS_VERSION")
        vbios_version_from_attestation_report = format_vbios_version(vbios_version_from_attestation_report)
        logger.info(
            f'\t\tVBIOS version fetched from the attestation report : {vbios_version_from_attestation_report}')

        if vbios_version_from_attestation_report != vbios_version:
            err_msg = ("\t\tThe vbios version in attestation report is not matching with the vbios verison fetched "
                       "from the driver. This is expected and will be fixed in the next release.")
            logger.error(err_msg)
            settings.mark_attestation_report_vbios_version_as_matching(False)
            # TODO: Uncomment this exception once we have nscq API to retrieve vBIOS version
            # raise VBIOSVersionMismatchError(err_msg)

        logger.info("VBIOS version in attestation report is matching.")
        settings.mark_attestation_report_vbios_version_as_matching()

        # Performing the signature verification.
        attestation_report_verification_status = attestation_report_obj.verify_signature(
            switch_leaf_certificate.to_cryptography(),
            settings.signature_length,
            settings.HashFunction)
        if attestation_report_verification_status:
            logger.info("\t\tAttestation report signature verification successful.")
            settings.mark_attestation_report_signature_verified()
        else:
            err_msg = "\t\tAttestation report signature verification failed."
            logger.error(err_msg)
            settings.mark_attestation_report_signature_verified(False)
            raise SignatureVerificationError(err_msg)

        return attestation_report_verification_status

    @staticmethod
    def generate_nonce(size):
        """ Generates cryptographically strong nonce to be sent to the SPDM requester via the nvml api for the attestation report.

        Args:
            size (int): the number of random bytes to be generated.

        Returns:
            [bytes]: the bytes of length "size" generated randomly.
        """
        random_bytes = secrets.token_bytes(size)
        return random_bytes

    @staticmethod
    def validate_and_extract_nonce(nonce_hex_string):
        """ Validate and convert Nonce to bytes format

        Args:
            nonce_hex_string (string): 32 Bytes Nonce represented as Hex String

        Returns:
            [bytes]: Nonce represented as Bytes
        """
        if len(nonce_hex_string) == BaseSettings.SIZE_OF_NONCE_IN_HEX_STR and set(nonce_hex_string).issubset(
                string.hexdigits):
            return bytes.fromhex(nonce_hex_string)
        else:
            raise InvalidNonceError(
                "Invalid Nonce Size. The nonce should be 32 bytes in length represented as Hex String")

    def __init__(self, number_of_switches):
        """ It is the constructor for the CcAdminUtils.

        Args:
            number_of_switches (int): The number of the available Switches.
        """
        self.number_of_switches = number_of_switches
