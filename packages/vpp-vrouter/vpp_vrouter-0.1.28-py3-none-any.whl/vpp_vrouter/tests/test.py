"""
Integration tests for all packages/modules of this repository.
The API integration test mostly test whether the configuration appears inside VPP and whether the API response is
correct. In certain cases also some pinging is tested, but mostly the VPP functionality testing (configure VPP and
test that VPP does what is should) is out of scope for these tests.
"""

import ipaddress
import logging
import multiprocessing
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from ipaddress import IPv4Network
from threading import Thread, Lock

from vpp_vrouter.common.models import (
    AddConfigurationItemsReply,
    ConfigurationItemDetail,
    State,
    SWInterfaceDetail,
    ConfigurationItemReply,
    IPRouteDetail,
    GetConfigurationItemsReply,
    InterfaceConfigurationItem,
    DeleteConfigurationItemsReply,
    ACLDetails,
    NAT44AddressDetails,
    NAT44InterfaceDetails,
    NAT44StaticMappingDetails,
    NAT44IdentityMappingDetails,
    WIREGUARD_PEER_INDEX,
    WireguardPeerDetail,
    FRRConfigurationItem,
    RouteConfigurationItem,
    InterfaceType,
    RouteType,
    LCPGlobalsConfigurationItem,
    LCPPairConfigurationItem,
    LCPHostInterfaceTypeEnum,
    HOST_SW_IF_INDEX,
    LCPPairDetail,
    UpdateConfigurationItemsReply,
    NOT_SET_MTU,
    DHCPConfigurationItem,
)
from vpp_vrouter.common.utils import configure_module_logger

CLIENT_DOCKER_TAG = "extended-papi-client:test"
SERVER_DOCKER_TAG = "extended-papi-server:test"
FRR_DOCKER_TAG = "frr:test"
DHCP_DOCKER_TAG = "dhcp:test"
VPP_IMAGE_TAG = "vpp:22.10.1-patched"
VPP_TEST_IMAGE_TAG = "vpp:test"

project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../."))
tests_dir_suffix = "tests"
tests_dir = os.path.join(project_root_dir, tests_dir_suffix)

# logger = configure_module_logger(__name__, logging.INFO)
logger = configure_module_logger(__name__, logging.DEBUG)

subprocess_output = (
    sys.stdout if logger.isEnabledFor(logging.DEBUG) else subprocess.DEVNULL
)
subprocess_error_output = (
    sys.stderr if logger.isEnabledFor(logging.DEBUG) else subprocess.DEVNULL
)


def setUpModule():
    # build vpp docker image
    try:
        subprocess.check_call(
            ["docker", "build", "-t", VPP_IMAGE_TAG, "-f", "vpp.Dockerfile", "."],
            cwd=os.path.join(project_root_dir, "docker", "vpp"),
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
    except:
        logger.exception("failed to build vpp docker image")
        raise

    # build vpp-test docker image
    try:
        subprocess.check_call(
            [
                "docker",
                "build",
                "-t",
                VPP_TEST_IMAGE_TAG,
                "-f",
                "vpp-test.Dockerfile",
                ".",
            ],
            cwd=os.path.join(project_root_dir, "docker", "vpp-test"),
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
    except:
        logger.exception("failed to build server docker image")
        raise

    # build server docker image
    try:
        subprocess.check_call(
            [
                "docker",
                "build",
                "-t",
                SERVER_DOCKER_TAG,
                "-f",
                "docker/server.Dockerfile",
                ".",
            ],
            cwd=project_root_dir,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
    except:
        logger.exception("failed to build server docker image")
        raise

    # build FRR docker image
    try:
        subprocess.check_call(
            [
                "docker",
                "build",
                "-t",
                FRR_DOCKER_TAG,
                "-f",
                "docker/frr/frr.Dockerfile",
                ".",
            ],
            cwd=project_root_dir,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
    except:
        logger.exception("failed to build FRR docker image")
        raise
    # build DHCP docker image
    try:
        subprocess.check_call(
            [
                "docker",
                "build",
                "-t",
                DHCP_DOCKER_TAG,
                "-f",
                "docker/dhcp/dhcp.Dockerfile",
                ".",
            ],
            cwd=project_root_dir,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
    except:
        logger.exception("failed to build FRR docker image")
        raise


# TODO test direct(non-extended) vpp client calls (using VPP client from fd.io)?


class FullyContainerizedTestCases(unittest.TestCase):
    """Tests in fully containerize environment (VPP is in container, Server is in container, Client is in container)"""

    def test_simple_configuration(self):
        test_file_path = os.path.join(tests_dir, "test_code.py")
        try:
            # setup VPP container
            self.vpp_popen = subprocess.Popen(
                "docker run --rm --privileged --name vpp "
                + "-v /usr/share/vpp/api:/usr/share/vpp/api-copy "
                + "-v /run/vpp:/run/vpp "
                + "-v /var/log/vpp:/var/log/vpp "
                + VPP_TEST_IMAGE_TAG,
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
            time.sleep(
                3
            )  # TODO do waiting on some condition instead of hardcoded waiting
            # FIXME: Manual one-time setup in OS: just add this to end of /etc/sudoers (using sudo visudo) to run
            #  "sudo chmod" without password:
            #   <current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/chmod
            subprocess.call("sudo /usr/bin/chmod o+w /run/vpp/*.sock", shell=True)

            # setup PAPI++ server container
            self.server_popen = subprocess.Popen(
                "docker run --rm --name server "
                + "-v /usr/share/vpp/api:/usr/share/vpp/api "
                + "-v /run/vpp:/run/vpp "
                +
                # "-p 9999:9999 " +
                # "-p 8888:8888 " +  # TODO explain why test doesn't need to publish anything but in some case in production this is needed
                SERVER_DOCKER_TAG,
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
            time.sleep(
                2
            )  # TODO do waiting on some condition instead of hardcoded waiting

            # prepare client test code that will use PAPI++ client library
            ip_address_str = (
                (
                    subprocess.check_output(
                        "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server",
                        shell=True,
                    )
                )
                .decode()
                .replace("\n", "")
            )
            client_test_code = f"""
from vpp_vrouter.common import models
from vpp_vrouter.client.client import ExtendedVPPAPIClient

with ExtendedVPPAPIClient(server_host="{ip_address_str}") as client:
    reply = client.add_configuration(
        models.InterfaceConfigurationItem(
            name="my-tap",
            enabled=True,
            ip_addresses=["10.0.1.0/24"],
            mtu=1400
        )
    )
            """
            with open(test_file_path, "w") as test_file:
                test_file.write(client_test_code)
            test_file_relative_path = os.path.join(tests_dir_suffix, "test_code.py")

            # run client test code (build it into docker image and run it)
            subprocess.check_call(
                f"docker build -t {CLIENT_DOCKER_TAG} "
                f'--build-arg test_code_file="{test_file_relative_path}" '
                "-f docker/client.Dockerfile .",
                shell=True,
                cwd=project_root_dir,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
            time.sleep(
                3
            )  # TODO do waiting on some condition instead of hardcoded waiting
            self.client_popen = subprocess.Popen(
                "docker run --name client " + CLIENT_DOCKER_TAG,
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
            time.sleep(
                3
            )  # TODO do waiting on some condition instead of hardcoded waiting

            # check VPP state for changes that should do the tested client code
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("tap0", interface_listing, "No tap was created")
            self.assertIn("up", interface_listing, "Tap state was not changed to UP")
            self.assertIn("1400", interface_listing, "Tap mtu was not changed")
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
        finally:
            # teardown
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
            if self.client_popen:
                try:
                    self.client_popen.terminate()
                    self.client_popen.wait()
                except:
                    logger.exception("can't teardown client docker process")
                    pass
            if self.server_popen:
                try:
                    self.server_popen.terminate()
                    self.server_popen.wait()
                except:
                    logger.exception("can't teardown server docker process")
                    pass
            if self.vpp_popen:
                try:
                    self.vpp_popen.terminate()
                    self.vpp_popen.wait()
                except:
                    logger.exception("can't teardown VPP docker process")
                    pass
            try:
                subprocess.call(
                    "docker rm -f client",
                    shell=True,
                    stdout=subprocess_output,
                    stderr=subprocess_error_output,
                )
            except:
                logger.exception("can't teardown client docker container")
                pass
            try:
                subprocess.call(
                    "docker rm -f server",
                    shell=True,
                    stdout=subprocess_output,
                    stderr=subprocess_error_output,
                )
            except:
                logger.exception("can't teardown client docker container")
                pass
            try:
                subprocess.call(
                    "docker rm -f vpp",
                    shell=True,
                    stdout=subprocess_output,
                    stderr=subprocess_error_output,
                )
            except:
                logger.exception("can't teardown client docker container")
                pass


class ContainerizedServerTestCases(unittest.TestCase):
    """Tests in half-containerize environment (VPP is in container, Server is in container, Client code is running
    locally)"""

    def setUp(self) -> None:
        self.vpp_popen = subprocess.Popen(
            "docker run --rm --privileged --name vpp "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api-copy "
            + "-v /run/vpp:/run/vpp "
            + "-v /var/log/vpp:/var/log/vpp "
            + VPP_TEST_IMAGE_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        # FIXME: Manual one-time setup in OS: just add this to end of /etc/sudoers (using sudo visudo) to run
        #  "sudo chmod" without password:
        #   <current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/chmod
        subprocess.call("sudo /usr/bin/chmod o+w /run/vpp/*.sock", shell=True)
        self.server_popen = subprocess.Popen(
            "docker run --rm --name server "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api "
            + "-v /run/vpp:/run/vpp "
            + "--network host "
            + SERVER_DOCKER_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        self.server_host = (
            (
                subprocess.check_output(
                    "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server",
                    shell=True,
                )
            )
            .decode()
            .replace("\n", "")
        )

    def tearDown(self) -> None:
        if self.server_popen:
            try:
                self.server_popen.terminate()
                self.server_popen.wait()
            except:
                logger.exception("can't teardown server docker process")
                pass
        if self.vpp_popen:
            try:
                self.vpp_popen.terminate()
                self.vpp_popen.wait()
            except:
                logger.exception("can't teardown VPP docker process")
                pass
        try:
            subprocess.call(
                "docker rm -f server",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown server docker container")
            pass
        try:
            subprocess.call(
                "docker rm -f vpp",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown vpp docker container")
            pass


class CommonClientFeaturesTestCases(ContainerizedServerTestCases):
    """Tests client features of the API that are independent of the configuration item's type."""

    def test_simple_client_call(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            tap_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"], mtu=1400
            )
            reply = client.add_configuration(tap_config)

            # checking client reply
            self.assertIsInstance(reply, AddConfigurationItemsReply, "Bad reply type")
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Simple tap apply to VPP failed (added items applied)",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Simple tap apply to VPP failed (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            self.assertEqual(
                len(reply.added_items), 1, "Only one config item was added"
            )
            self.assertIsInstance(
                reply.added_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.added_items[0].config,
                tap_config,
                "Added config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.added_items[0].state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                reply.added_items[0].metadata["sw_if_index"], 1, "Missing sw_if_index"
            )
            self.assertIsInstance(
                reply.added_items[0].metadata["vpp_dump"],
                SWInterfaceDetail,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                reply.added_items[0].metadata["vpp_dump"].sw_if_index,
                reply.added_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply",
            )

            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only one config item should be processed(applied to VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                tap_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when applying tap into VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                1,
                "Missing sw_if_index (processed config item)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["vpp_dump"].sw_if_index,
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply (processed config item)",
            )

        # check VPP state for changes that should do the tested client code
        interface_listing = subprocess.check_output(
            "docker exec vpp vppctl sh int", shell=True
        ).decode()
        self.assertIn("tap0", interface_listing, "No tap was created")
        self.assertIn("up", interface_listing, "Tap state was not changed to UP")
        self.assertIn("1400", interface_listing, "Tap mtu was not changed")
        logger.debug(
            "VPP interface listing:\n{} ".format(interface_listing.replace("\\n", "\n"))
        )

    def test_dependency_feature(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # adding route without corresponding interface in place
            route_config = models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                next_hop_address="192.0.3.1",
                outgoing_interface="my-tap",
            )
            reply = client.add_configuration(route_config)
            logger.debug("Added route config reply:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(reply, AddConfigurationItemsReply, "Bad reply type")
            self.assertFalse(
                reply.all_added_items_applied_to_vpp,
                "Route config item must be blocked by missing interface",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                0,
                "No config item should be processed(applied to VPP)",
            )
            self.assertEqual(
                reply.added_items[0].config,
                route_config,
                "Added route config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.added_items), 1, "Only one config item was added"
            )
            self.assertIsInstance(
                reply.added_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.added_items[0].config,
                route_config,
                "Added route config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.added_items[0].state,
                State.BLOCKED,
                "Config item should be BLOCKED by missing interface",
            )
            self.assertEqual(
                len(reply.added_items[0].metadata),
                0,
                "It is before application to VPP. There should be no metadata.",
            )

            # checking VPP state
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn(
                "10.1.3.0/24", route_listing, "Route should not be in VPP yet"
            )
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )

            # adding interface that is needed in previous route configuration
            interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            reply = client.add_configuration(interface_config)
            logger.debug("Added interface config reply:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(reply, AddConfigurationItemsReply, "Bad reply type")
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Tap interface apply to VPP failed (added items applied)",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to apply Route and/or Tap to VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.added_items), 1, "Only one config item was added"
            )
            self.assertIsInstance(
                reply.added_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.added_items[0].config,
                interface_config,
                "Added interface config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.added_items[0].state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                reply.added_items[0].metadata["sw_if_index"], 1, "Missing sw_if_index"
            )
            self.assertIsInstance(
                reply.added_items[0].metadata["vpp_dump"],
                SWInterfaceDetail,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                reply.added_items[0].metadata["vpp_dump"].sw_if_index,
                reply.added_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                2,
                "Only route and interface config item should be processed(applied to VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                interface_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when applying tap into VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                1,
                "Missing sw_if_index (processed config item)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["vpp_dump"].sw_if_index,
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply (processed config item)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[1],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].config,
                route_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].error,
                "",
                "There should be no error from VPP when applying route into VPP",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[1].metadata["vpp_dump"],
                IPRouteDetail,
                "Should be modeled class for route dump",
            )
            # Note: just basic dump check, other checks directly from VPP
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].metadata["vpp_dump"].prefix,
                IPv4Network(route_config.destination_network),
                "Should be modeled class for route dump",
            )

        # check VPP state for changes that should be applied by the tested client code
        interface_listing = subprocess.check_output(
            "docker exec vpp vppctl sh int", shell=True
        ).decode()
        self.assertIn("tap0", interface_listing, "No tap was created")
        self.assertIn("up", interface_listing, "Tap state was not changed to UP")
        logger.debug(
            "VPP's interface listing:\n{} ".format(
                interface_listing.replace("\\n", "\n")
            )
        )

        route_listing = subprocess.check_output(
            "docker exec vpp vppctl sh ip fib", shell=True
        ).decode()
        self.assertIn("10.1.3.0/24", route_listing, "No route was created")
        self.assertIn(
            "via 192.0.3.1 tap0",
            route_listing,
            "Added route doesn't redirect traffic to created tap",
        )
        logger.debug(
            "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
        )

    def test_configuration_duplicity_error(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            reply = client.add_configuration(interface_config)
            logger.debug("Reply of config's first addition:\n{} ".format(reply))
            self.assertEqual(
                reply.processing_error, "", "No processing error should occur"
            )

            reply = client.add_configuration(interface_config)
            logger.debug("Reply of config's duplicated addition:\n{} ".format(reply))
            self.assertIn(
                "duplicate",
                reply.processing_error.lower(),
                "Processing of configuration should return duplicity error for duplicate configuration",
            )

    def test_getting_user_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # initial get
            init_get_reply = client.get_configuration()
            logger.debug("Get configuration reply:\n{} ".format(init_get_reply))

            # check reply
            self.assertIsInstance(
                init_get_reply, GetConfigurationItemsReply, "Bad reply type"
            )
            for item in init_get_reply.items:
                self.assertIsInstance(item, ConfigurationItemDetail, "Bad item type")
                self.assertIsInstance(
                    item.config,
                    InterfaceConfigurationItem,
                    "Only interface config can be filled by initial VPP dump",
                )
                self.assertEqual(
                    item.state,
                    State.APPLIED,
                    "Interfaces from initial VPP dump must be in APPLIED state",
                )

            # add new config item and get config again
            interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            add_reply = client.add_configuration(interface_config)
            logger.debug("Add configuration reply:\n{} ".format(add_reply))
            get_reply = client.get_configuration()
            logger.debug("Get configuration reply:\n{} ".format(get_reply))

            # check reply
            self.assertEqual(
                len(
                    [
                        item
                        for item in init_get_reply.items
                        if item not in get_reply.items
                    ]
                ),
                0,
                "All initial config items should be also reply of later get_configuration call",
            )
            new_items = [
                item for item in get_reply.items if item not in init_get_reply.items
            ]
            self.assertEqual(len(new_items), 1, "Only on interface was added")
            self.assertIsInstance(
                new_items[0], ConfigurationItemDetail, "Bad item type"
            )
            self.assertEqual(
                new_items[0].config,
                interface_config,
                "Added config item and returned config item doesn't match",
            )
            self.assertIsNotNone(
                new_items[0].metadata.get("vpp_dump"),
                "added interface should have some dump from VPP",
            )
            self.assertEqual(
                new_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )

    def test_waiting_for_configuration_apply_to_vpp(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        # it is used for logical grouping of configuration here (grouping on client's user side),
        # but could hold any context information
        context = "1"
        log_lock = Lock()
        log = []

        def add_route(delay):
            time.sleep(delay)
            with log_lock:
                log.append("adding route")
            with ExtendedVPPAPIClient() as client:
                reply = client.add_configuration(
                    # adding configuration in wrong order just to see if dependencies work
                    models.RouteConfigurationItem(
                        destination_network="10.1.3.0/24",
                        next_hop_address="192.0.3.1",
                        outgoing_interface="my-tap",
                    ),
                    context=context,
                )
                logger.debug("Add route configuration reply:\n{} ".format(reply))
                time.sleep(
                    5
                )  # checking that running multiple clients from multiple threads doesn't raise Error
            pass

        def add_interface(delay):
            time.sleep(delay)
            with log_lock:
                log.append("adding interface")
            with ExtendedVPPAPIClient() as client:
                reply = client.add_configuration(
                    models.InterfaceConfigurationItem(
                        name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
                    ),
                    context=context,
                )
                logger.debug("Add interface configuration reply:\n{} ".format(reply))
                time.sleep(
                    5
                )  # checking that running multiple clients from multiple threads doesn't raise Error

        def wait_for_config(delay):
            time.sleep(delay)
            with log_lock:
                log.append("waiting for config")
            with ExtendedVPPAPIClient() as client:

                def check_application_to_vpp(config_item_details) -> bool:
                    applied_config_items_with_right_context = [
                        detail
                        for detail in config_item_details
                        if detail.metadata.get("context") == context
                        and detail.state == models.State.APPLIED
                    ]
                    # NOTE: filter by context is not enough as waiting thread start sooner than all context configuration
                    # is sent to vpp_client -> need to have more knowledge to wait properly (config item count in this case)
                    return len(applied_config_items_with_right_context) == 2

                client.wait_for_configuration(
                    configuration_check=check_application_to_vpp
                )
                with log_lock:
                    log.append("config is applied in VPP")
            pass

        threads = [
            Thread(name="Thread-wait", target=wait_for_config, args=(1,)),
            Thread(name="Thread-route", target=add_route, args=(2,)),
            Thread(name="Thread-interface", target=add_interface, args=(3,)),
        ]
        try:
            for t in threads:
                t.start()
        except Exception as e:
            logger.exception("Error: unable to start thread due to ", e)
        try:
            for t in threads:
                t.join()
        except Exception as e:
            logger.exception("Error: unable to join thread due to ", e)

        with log_lock:
            self.assertEqual(
                log,
                [
                    "waiting for config",
                    "adding route",
                    "adding interface",
                    "config is applied in VPP",
                ],
                "The wait should wait until all configuration is applied to VPP",
            )

    def test_delete_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            route_config = models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                next_hop_address="192.0.3.1",
                outgoing_interface="my-tap",
            )
            reply = client.add_configuration(interface_config, route_config)
            logger.debug("Added interface and route config reply:\n{} ".format(reply))

            # verify correct state of vpp before delete testing
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertIn("10.1.3.0/24", route_listing, "No route was created")
            self.assertIn(
                "via 192.0.3.1 tap0",
                route_listing,
                "Added route doesn't redirect traffic to created tap",
            )
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("tap0", interface_listing, "No interface was created")
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )

            # remove route
            reply = client.delete_configuration(interface_config, route_config)
            # Note: also testing reordering of configuration items for delete by their dependencies
            # interface should be deleted after route and not in the parameter order given to delete method
            logger.debug("Removed route config reply:\n{} ".format(reply))

            # check reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove Route from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                2,
                "Only route config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed route config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                route_config,
                "Added config item and returned processed config item doesn't match (route)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing route from VPP (route)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[1],
                ConfigurationItemReply,
                "Bad type of processed interface config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].config,
                interface_config,
                "Added config item and returned processed config item doesn't match (interface)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[1].error,
                "",
                "There should be no error from VPP when removing route from VPP (interface)",
            )

            # check vpp state
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn("10.1.3.0/24", route_listing, "Route was not deleted")
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertNotIn("tap0", interface_listing, "Interface was not deleted")
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )

            # check server state using get_configuration()
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len([item for item in reply.items if item.config == route_config]),
                0,
                "Route config item should not be retrievable by get_configuration "
                "because it was already removed",
            )
            self.assertEqual(
                len([item for item in reply.items if item.config == interface_config]),
                0,
                "Interface config item should not be retrievable by get_configuration "
                "because it was already removed",
            )

    def test_update_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=False, ip_addresses=[], mtu=NOT_SET_MTU
            )
            updated_interface_config = models.InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"], mtu=1234
            )
            reply = client.add_configuration(interface_config)
            logger.debug("Added interface reply:\n{} ".format(reply))

            # verify correct state of vpp before update testing
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("tap0", interface_listing, "No tap was created")
            self.assertNotIn(
                "up", interface_listing, "All interfaces should be down initially"
            )
            self.assertNotIn(
                f"{updated_interface_config.mtu}",
                interface_listing,
                "No interface should have the update MTU value",
            )
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            interface_address_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int addr", shell=True
            ).decode()
            self.assertNotIn(
                updated_interface_config.ip_addresses[0],
                interface_address_listing,
                "IP address of Tap should not be set yet",
            )
            logger.debug(
                "VPP's interface address listing:\n{} ".format(
                    interface_address_listing.replace("\\n", "\n")
                )
            )

            # update existing tap interface (without delete and adding it again)
            reply = client.update_configuration(
                interface_config, updated_interface_config
            )
            logger.debug("Updated interface reply:\n{} ".format(reply))

            # verify update reply
            self.assertIsInstance(
                reply, UpdateConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.all_updated_items_applied_to_vpp,
                "Simple tap update in VPP failed (updated items applied)",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Simple tap update in VPP failed (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            self.assertEqual(
                len(reply.updated_items), 1, "Only one config item was updated"
            )
            self.assertIsInstance(
                reply.updated_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.updated_items[0].config,
                updated_interface_config,
                "Updated config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.updated_items[0].state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                reply.updated_items[0].metadata["sw_if_index"], 1, "Missing sw_if_index"
            )
            self.assertIsInstance(
                reply.updated_items[0].metadata["vpp_dump"],
                SWInterfaceDetail,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                reply.updated_items[0].metadata["vpp_dump"].sw_if_index,
                reply.updated_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply",
            )

            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only one config item should be processed(applied to VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                updated_interface_config,
                "Updated config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when applying tap update into VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                1,
                "Missing sw_if_index (processed config item)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["vpp_dump"].sw_if_index,
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply (processed config item)",
            )

            # verify correct state of vpp after update
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("tap0", interface_listing, "No tap is present")
            self.assertIn("up", interface_listing, "Tap state was not changed to UP")
            self.assertIn(
                f"{updated_interface_config.mtu}",
                interface_listing,
                "Tap mtu was not changed",
            )
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            interface_address_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int addr", shell=True
            ).decode()
            self.assertIn(
                updated_interface_config.ip_addresses[0],
                interface_address_listing,
                "IP address of Tap should be set",
            )
            logger.debug(
                "VPP's interface address listing:\n{} ".format(
                    interface_address_listing.replace("\\n", "\n")
                )
            )

    def test_interface_sync_with_vpp(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            # setup wireguard
            wireguard_interface_config = models.InterfaceConfigurationItem(
                name="my-wg",
                enabled=True,
                ip_addresses=["10.100.1.1/24"],
                type=models.InterfaceType.WIREGUARD_TUNNEL,
                mtu=1420,  # leaving some room for encryption encapsulation so that packet don't break into segments
                link=models.WireguardInterfaceLink(
                    private_key="cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=",  # encoded in base64
                    port=50000,
                    src_addr=ipaddress.IPv4Address("10.100.0.1"),
                ),
            )
            wireguard_peer_config = models.WireguardPeerConfigurationItem(
                public_key="hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=",  # encoded in base64
                port=50000,
                endpoint=ipaddress.IPv4Address("10.100.0.2"),
                allowed_ips=["0.0.0.0/0"],
                wg_if_name=wireguard_interface_config.name,
            )
            reply = client.add_configuration(
                wireguard_interface_config, wireguard_peer_config
            )

            # check reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to configure wireguard interface inside VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to configure wireguard interface inside VPP  (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check vpp state
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("wg0", interface_listing, "No wireguard was created")
            self.assertIn(
                "up", interface_listing, "Wireguard state was not changed to UP"
            )
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )

            # check admin and link state through python API
            interface_detail = [
                item.metadata[models.VPP_DUMP_KEY]
                for item in client.get_configuration(sync_with_vpp=True).items
                if isinstance(item.config, models.InterfaceConfigurationItem)
                and isinstance(item.config.link, models.WireguardInterfaceLink)
                and isinstance(
                    item.metadata[models.VPP_DUMP_KEY], models.SWInterfaceDetail
                )
            ][0]
            self.assertTrue(
                interface_detail.is_admin_state_up(),
                "interface should be up (admin state) after python API configuration",
            )
            self.assertTrue(
                interface_detail.is_link_state_up(),
                "interface should be up (link state) after python API configuration",
            )

            # change interface state by not using API (poor simulation of link failure)
            subprocess.check_call(
                "docker exec vpp vppctl set interface state wg0 down", shell=True
            )

            # check again admin and link state through python API
            interface_detail = [
                item.metadata[models.VPP_DUMP_KEY]
                for item in client.get_configuration(sync_with_vpp=True).items
                if isinstance(item.config, models.InterfaceConfigurationItem)
                and isinstance(item.config.link, models.WireguardInterfaceLink)
                and isinstance(
                    item.metadata[models.VPP_DUMP_KEY], models.SWInterfaceDetail
                )
            ][0]
            self.assertFalse(
                interface_detail.is_admin_state_up(),
                "interface should be up (admin state) after link failure",
            )
            self.assertFalse(
                interface_detail.is_link_state_up(),
                "interface should be up (link state) after link failure",
            )

            # change interface state by not using API (poor simulation of link failure)
            subprocess.check_call(
                "docker exec vpp vppctl set interface state wg0 up", shell=True
            )

            # check again admin and link state through python API
            interface_detail = [
                item.metadata[models.VPP_DUMP_KEY]
                for item in client.get_configuration(sync_with_vpp=True).items
                if isinstance(item.config, models.InterfaceConfigurationItem)
                and isinstance(item.config.link, models.WireguardInterfaceLink)
                and isinstance(
                    item.metadata[models.VPP_DUMP_KEY], models.SWInterfaceDetail
                )
            ][0]
            self.assertTrue(
                interface_detail.is_admin_state_up(),
                "interface should be up (admin state) after link re-enabling",
            )
            self.assertTrue(
                interface_detail.is_link_state_up(),
                "interface should be up (link state) after link re-enabling",
            )


class InterfaceTestCases(ContainerizedServerTestCases):
    """Interface related tests

    For Tap tests look into CommonClientFeaturesTestCases class"""

    def test_add_loopback(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            loop_config = models.InterfaceConfigurationItem(
                name="my-loop",
                type=models.InterfaceType.SOFTWARE_LOOPBACK,
                enabled=True,
                ip_addresses=["10.0.1.0/24"],
                mtu=1400,
            )
            reply = client.add_configuration(loop_config)

            # checking client reply
            self.assertIsInstance(reply, AddConfigurationItemsReply, "Bad reply type")
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Simple loop apply to VPP failed (added items applied)",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Simple loop apply to VPP failed (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            self.assertEqual(
                len(reply.added_items), 1, "Only one config item was added"
            )
            self.assertIsInstance(
                reply.added_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.added_items[0].config,
                loop_config,
                "Added config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.added_items[0].state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                reply.added_items[0].metadata["sw_if_index"], 1, "Missing sw_if_index"
            )
            self.assertIsInstance(
                reply.added_items[0].metadata["vpp_dump"],
                SWInterfaceDetail,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                reply.added_items[0].metadata["vpp_dump"].sw_if_index,
                reply.added_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply",
            )

            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only one config item should be processed(applied to VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                loop_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when applying loop into VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                1,
                "Missing sw_if_index (processed config item)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["vpp_dump"].sw_if_index,
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply (processed config item)",
            )

        # check VPP state for changes that should do the tested client code
        interface_listing = subprocess.check_output(
            "docker exec vpp vppctl sh int", shell=True
        ).decode()
        self.assertIn("loop0", interface_listing, "No loop was created")
        self.assertIn("up", interface_listing, "Loop state was not changed to UP")
        self.assertIn("1400", interface_listing, "Loop mtu was not changed")
        logger.debug(
            "VPP interface listing:\n{} ".format(interface_listing.replace("\\n", "\n"))
        )

    def test_delete_loopback(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            loop_config = models.InterfaceConfigurationItem(
                name="my-loop",
                type=models.InterfaceType.SOFTWARE_LOOPBACK,
                enabled=True,
                ip_addresses=["10.0.1.0/24"],
                mtu=1234,
            )
            reply = client.add_configuration(loop_config)
            logger.debug("Added loop interface reply:\n{} ".format(reply))

            # verify correct state of vpp before delete testing
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("loop0", interface_listing, "No interface was created")
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )

            # remove route
            reply = client.delete_configuration(loop_config)
            logger.debug("Removed loop config reply:\n{} ".format(reply))

            # check reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove Route from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only interface config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed interface config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                loop_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing route from VPP",
            )

            # check vpp state
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertNotIn("loop0", interface_listing, "Interface was not deleted")
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )

            # check server state using get_configuration()
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len([item for item in reply.items if item.config == loop_config]),
                0,
                "Interface config item should not be retrievable by get_configuration "
                "because it was already removed",
            )

    def test_update_loopback(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface_config = models.InterfaceConfigurationItem(
                name="my-loop",
                type=models.InterfaceType.SOFTWARE_LOOPBACK,
                enabled=False,
                ip_addresses=[],
                mtu=NOT_SET_MTU,
            )
            updated_interface_config = models.InterfaceConfigurationItem(
                name="my-loop",
                type=models.InterfaceType.SOFTWARE_LOOPBACK,
                enabled=True,
                ip_addresses=["10.0.1.0/24"],
                mtu=1234,
            )
            reply = client.add_configuration(interface_config)
            logger.debug("Added interface reply:\n{} ".format(reply))

            # verify correct state of vpp before update testing
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("loop0", interface_listing, "No loop was created")
            self.assertNotIn(
                "up", interface_listing, "All interfaces should be down initially"
            )
            self.assertNotIn(
                f"{updated_interface_config.mtu}",
                interface_listing,
                "No interface should have the update MTU value",
            )
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            interface_address_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int addr", shell=True
            ).decode()
            self.assertNotIn(
                updated_interface_config.ip_addresses[0],
                interface_address_listing,
                "IP address of loop should not be set yet",
            )
            logger.debug(
                "VPP's interface address listing:\n{} ".format(
                    interface_address_listing.replace("\\n", "\n")
                )
            )

            # update existing loop interface (without delete and adding it again)
            reply = client.update_configuration(
                interface_config, updated_interface_config
            )
            logger.debug("Updated interface reply:\n{} ".format(reply))

            # verify update reply
            self.assertIsInstance(
                reply, UpdateConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.all_updated_items_applied_to_vpp,
                "Simple loop update in VPP failed (updated items applied)",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Simple loop update in VPP failed (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            self.assertEqual(
                len(reply.updated_items), 1, "Only one config item was updated"
            )
            self.assertIsInstance(
                reply.updated_items[0],
                ConfigurationItemDetail,
                "Bad type of added item in reply",
            )
            self.assertEqual(
                reply.updated_items[0].config,
                updated_interface_config,
                "Updated config item and returned config item doesn't match",
            )
            self.assertEqual(
                reply.updated_items[0].state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                reply.updated_items[0].metadata["sw_if_index"], 1, "Missing sw_if_index"
            )
            self.assertIsInstance(
                reply.updated_items[0].metadata["vpp_dump"],
                SWInterfaceDetail,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                reply.updated_items[0].metadata["vpp_dump"].sw_if_index,
                reply.updated_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply",
            )

            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only one config item should be processed(applied to VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                updated_interface_config,
                "Updated config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].state,
                State.APPLIED,
                "(processed) config item should be applied in VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when applying loop update into VPP",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                1,
                "Missing sw_if_index (processed config item)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].metadata["vpp_dump"].sw_if_index,
                reply.vpp_apply_attempted_items[0].metadata["sw_if_index"],
                "sw_if_index mismatch in reply (processed config item)",
            )

            # verify correct state of vpp after update
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int", shell=True
            ).decode()
            self.assertIn("loop0", interface_listing, "No loop is present")
            self.assertIn("up", interface_listing, "Loop state was not changed to UP")
            self.assertIn(
                f"{updated_interface_config.mtu}",
                interface_listing,
                "Loop mtu was not changed",
            )
            logger.debug(
                "VPP interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            interface_address_listing = subprocess.check_output(
                "docker exec vpp vppctl sh int addr", shell=True
            ).decode()
            self.assertIn(
                updated_interface_config.ip_addresses[0],
                interface_address_listing,
                "IP address of Loop should be set",
            )
            logger.debug(
                "VPP's interface address listing:\n{} ".format(
                    interface_address_listing.replace("\\n", "\n")
                )
            )


class RouteTestCases(ContainerizedServerTestCases):
    """Route related tests

    For simple route tests look into CommonClientFeaturesTestCases class"""

    def test_add_multipath_route(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface1_config = models.InterfaceConfigurationItem(
                name="tap1", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            interface2_config = models.InterfaceConfigurationItem(
                name="tap2", enabled=True, ip_addresses=["10.0.2.0/24"]
            )
            route_config = models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                multi_output_paths=[
                    models.RouteOutputPath(
                        next_hop_address="192.0.1.2",
                        outgoing_interface="tap1",
                        weight=10,
                    ),
                    models.RouteOutputPath(
                        next_hop_address="192.0.2.2",
                        outgoing_interface="tap2",
                        weight=10,
                    ),
                ],
            )
            reply = client.add_configuration(
                interface1_config, interface2_config, route_config
            )
            logger.debug(
                "Added interfaces and multipath route config reply:\n{} ".format(reply)
            )

            # verify correct state of vpp before delete testing
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertIn("10.1.3.0/24", route_listing, "No route was created")
            self.assertIn(
                "via 192.0.1.2 tap0",
                route_listing,
                "Added route doesn't redirect traffic to created tap0",
            )
            self.assertIn(
                "via 192.0.2.2 tap1",
                route_listing,
                "Added route doesn't redirect traffic to created tap1",
            )
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )

    def test_remove_multipath_route(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface1_config = models.InterfaceConfigurationItem(
                name="tap1", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            interface2_config = models.InterfaceConfigurationItem(
                name="tap2", enabled=True, ip_addresses=["10.0.2.0/24"]
            )
            route_config = models.RouteConfigurationItem(
                destination_network="10.1.3.0/24",
                multi_output_paths=[
                    models.RouteOutputPath(
                        next_hop_address="192.0.1.2",
                        outgoing_interface="tap1",
                        weight=10,
                    ),
                    models.RouteOutputPath(
                        next_hop_address="192.0.2.2",
                        outgoing_interface="tap2",
                        weight=10,
                    ),
                ],
            )
            reply = client.add_configuration(
                interface1_config, interface2_config, route_config
            )
            logger.debug(
                "Added interfaces and multipath route config reply:\n{} ".format(reply)
            )

            # verify correct state of vpp before delete testing
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertIn("10.1.3.0/24", route_listing, "No route was created")
            self.assertIn(
                "via 192.0.1.2 tap0",
                route_listing,
                "Added route doesn't redirect traffic to created tap0",
            )
            self.assertIn(
                "via 192.0.2.2 tap1",
                route_listing,
                "Added route doesn't redirect traffic to created tap1",
            )
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )

            # remove route
            reply = client.delete_configuration(route_config)
            logger.debug("Removed route config reply:\n{} ".format(reply))

            # check reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove Route from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only route config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed route config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                route_config,
                "Added config item and returned processed config item doesn't match (route)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing route from VPP (route)",
            )

            # check vpp state
            route_listing = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn("10.1.3.0/24", route_listing, "Route was not deleted")
            logger.debug(
                "VPP's route listing:\n{} ".format(route_listing.replace("\\n", "\n"))
            )

            # check server state using get_configuration()
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len([item for item in reply.items if item.config == route_config]),
                0,
                "Route config item should not be retrievable by get_configuration "
                "because it was already removed",
            )


class ACLTestCases(ContainerizedServerTestCases):
    def test_add_acl_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            # adding ACL config
            acl_input_interface_config = models.InterfaceConfigurationItem(
                name="acl-input-tap", enabled=True, ip_addresses=["10.100.1.1/24"]
            )
            acl_output_interface_config = models.InterfaceConfigurationItem(
                name="acl-output-tap", enabled=True, ip_addresses=["10.200.1.1/24"]
            )
            acl_config = models.ACLConfigurationItem(
                name="ACL1",
                ingress=["acl-input-tap"],
                egress=["acl-output-tap"],
                rules=[  # rules order and content don't have to make sense, just testing all config possibilities
                    models.ACLRuleConfigurationItem(
                        action=models.ACLAction.PERMIT,
                        refinement=models.IPSpecification(
                            addresses=models.IPAddresses(
                                destination_network=IPv4Network("10.200.1.0/24"),
                                source_network=IPv4Network("10.100.1.0/24"),
                            ),
                            protocol=models.ICMPProtocol(
                                icmpv6=False,
                                icmp_code_range=models.ICMPRange(first=1, last=2),
                                icmp_type_range=models.ICMPRange(first=3, last=4),
                            ),
                        ),
                    ),
                    models.ACLRuleConfigurationItem(
                        action=models.ACLAction.PERMIT,
                        refinement=models.IPSpecification(
                            addresses=None,
                            protocol=models.TCPProtocol(
                                destination_port_range=models.PortRange(
                                    lower_port=10, upper_port=11
                                ),
                                source_port_range=models.PortRange(
                                    lower_port=12, upper_port=13
                                ),
                                tcp_flags_mask=3,
                                tcp_flags_value=2,
                            ),
                        ),
                    ),
                    models.ACLRuleConfigurationItem(
                        action=models.ACLAction.PERMIT,
                        refinement=models.IPSpecification(
                            addresses=None,
                            protocol=models.UDPProtocol(
                                destination_port_range=models.PortRange(
                                    lower_port=20, upper_port=21
                                ),
                                source_port_range=models.PortRange(
                                    lower_port=22, upper_port=23
                                ),
                            ),
                        ),
                    ),
                    models.ACLRuleConfigurationItem(
                        action=models.ACLAction.PERMIT,
                        refinement=models.IPSpecification(
                            addresses=None,
                            protocol=models.OtherProtocol(protocol=94),  # IPIP protocol
                        ),
                    ),
                    models.ACLRuleConfigurationItem(  # Deny all other
                        action=models.ACLAction.DENY
                    ),
                ],
            )
            reply = client.add_configuration(
                acl_input_interface_config, acl_output_interface_config, acl_config
            )
            logger.debug(
                "Reply for adding ACL and interfaces linked to it:\n{} ".format(reply)
            )

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add ACL from VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add ACL from VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            added_acl_item = reply.added_items[2]
            self.assertEqual(
                added_acl_item.config,
                acl_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                added_acl_item.state,
                State.APPLIED,
                "Config item should be applied in VPP",
            )
            self.assertEqual(
                added_acl_item.metadata["acl_index"], 0, "Missing acl_index"
            )
            self.assertIsInstance(
                added_acl_item.metadata["vpp_dump"],
                ACLDetails,
                "bad type of vpp dump data",
            )
            self.assertEqual(
                added_acl_item.metadata["vpp_dump"].acl_index,
                added_acl_item.metadata["acl_index"],
                "acl_index mismatch in reply",
            )
            # resolving which tap is created first and therefore what interface sw_index it gets
            for item in reply.added_items[:2]:
                if item.config.name == acl_input_interface_config.name:
                    input_if_index = item.metadata["sw_if_index"]
                elif item.config.name == acl_output_interface_config.name:
                    output_if_index = item.metadata["sw_if_index"]

            # checking VPP
            acl_listing = subprocess.check_output(
                "docker exec vpp vppctl sh acl-plugin acl", shell=True
            ).decode()
            self.assertIn("acl-index 0", acl_listing, "ACL was not created")
            self.assertIn("tag {ACL1}", acl_listing, "ACL was not properly named")
            self.assertIn(
                f"applied inbound on sw_if_index: {input_if_index}",
                acl_listing,
                "Bad ingress ACL interface",
            )
            self.assertIn(
                f"applied outbound on sw_if_index: {output_if_index}",
                acl_listing,
                "Bad egress ACL interface",
            )
            self.assertIn(
                "0: ipv4 permit src 10.100.1.0/24 dst 10.200.1.0/24 proto 1 sport 3-4 dport 1-2",
                acl_listing,
                "Bad icmp rule",
            )
            self.assertIn(
                "1: ipv4 permit src 0.0.0.0/0 dst 0.0.0.0/0 proto 6 sport 12-13 dport 10-11 tcpflags 2 mask 3",
                acl_listing,
                "Bad tcp rule",
            )
            self.assertIn(
                "2: ipv4 permit src 0.0.0.0/0 dst 0.0.0.0/0 proto 17 sport 22-23 dport 20-21",
                acl_listing,
                "Bad udp rule",
            )
            self.assertIn(
                "3: ipv4 permit src 0.0.0.0/0 dst 0.0.0.0/0 proto 94 sport 0 dport 0",
                acl_listing,
                "Bad other protocole rule",
            )
            self.assertIn(
                "4: ipv4 deny src 0.0.0.0/0 dst 0.0.0.0/0 proto 0 sport 0 dport 0",
                acl_listing,
                "Bad no protocol rule",
            )
            logger.debug(
                "VPP's ACL listing:\n{} ".format(acl_listing.replace("\\n", "\n"))
            )

    def test_delete_acl_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            # adding ACL config
            acl_input_interface_config = models.InterfaceConfigurationItem(
                name="acl-input-tap", enabled=True, ip_addresses=["10.100.1.1/24"]
            )
            acl_output_interface_config = models.InterfaceConfigurationItem(
                name="acl-output-tap", enabled=True, ip_addresses=["10.200.1.1/24"]
            )
            acl_config = models.ACLConfigurationItem(
                name="ACL1",
                ingress=["acl-input-tap"],
                egress=["acl-output-tap"],
                rules=[
                    models.ACLRuleConfigurationItem(  # Deny all other
                        action=models.ACLAction.DENY
                    )
                ],
            )
            reply = client.add_configuration(
                acl_input_interface_config, acl_output_interface_config, acl_config
            )
            logger.debug(
                "Reply for adding ACL and interfaces linked to it:\n{} ".format(reply)
            )

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add ACL from VPP (apply_success)"
            )

            # checking VPP
            acl_listing = subprocess.check_output(
                "docker exec vpp vppctl sh acl-plugin acl", shell=True
            ).decode()
            self.assertIn("acl-index 0", acl_listing, "ACL was not created")

            # deleting ACL
            reply = client.delete_configuration(acl_config)
            logger.debug("Reply for deleting ACL:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success, "Failed to remove ACL from VPP (apply_success)"
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only ACL config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                acl_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing ACL from VPP",
            )

            # checking VPP
            acl_listing = subprocess.check_output(
                "docker exec vpp vppctl sh acl-plugin acl", shell=True
            ).decode()
            self.assertNotIn("acl-index 0", acl_listing, "ACL was not deleted")


class NATTestCases(ContainerizedServerTestCases):
    def test_add_nat_pool_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            config = models.Nat44AddressPoolConfigurationItem(
                name="tcp-service",
                first_ip=ipaddress.IPv4Address("10.0.0.100"),
                last_ip=ipaddress.IPv4Address("10.0.0.102"),
            )
            reply = client.add_configuration(config)
            logger.debug("Reply for adding NAT address pool:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add NAT address pool to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add NAT address pool to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertIsInstance(
                reply.added_items[0].metadata["vpp_dump"],
                list,
                "bad type of vpp dump data",
            )
            for details in reply.added_items[0].metadata["vpp_dump"]:
                self.assertIsInstance(
                    details, NAT44AddressDetails, "bad item type of vpp dump data"
                )
            self.assertListEqual(
                [details for details in reply.added_items[0].metadata["vpp_dump"]],
                [
                    NAT44AddressDetails(ip_address=ipaddress.IPv4Address("10.0.0.100")),
                    NAT44AddressDetails(ip_address=ipaddress.IPv4Address("10.0.0.101")),
                    NAT44AddressDetails(ip_address=ipaddress.IPv4Address("10.0.0.102")),
                ],
                "Bad vpp dump data",
            )

            # check VPP
            address_pool_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 addresses", shell=True
            ).decode()
            basic_addresses = address_pool_listing.split(
                "NAT44 twice-nat pool addresses"
            )[0]
            self.assertIn(
                "10.0.0.100", basic_addresses, "Missing first ip set for address pool"
            )
            self.assertIn(
                "10.0.0.101", basic_addresses, "Missing second ip set for address pool"
            )
            self.assertIn(
                "10.0.0.102", basic_addresses, "Missing third ip set for address pool"
            )
            logger.debug(
                "VPP's NAT44 address pool listing:\n{} ".format(
                    address_pool_listing.replace("\\n", "\n")
                )
            )

    def test_delete_nat_pool_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            config = models.Nat44AddressPoolConfigurationItem(
                name="tcp-service",
                first_ip=ipaddress.IPv4Address("10.0.0.100"),
                last_ip=ipaddress.IPv4Address("10.0.0.102"),
            )
            reply = client.add_configuration(config)
            logger.debug("Reply for adding NAT address pool:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add NAT address pool to VPP (apply_success)",
            )

            # check VPP (confirm state before delete)
            address_pool_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 addresses", shell=True
            ).decode()
            basic_addresses = address_pool_listing.split(
                "NAT44 twice-nat pool addresses"
            )[0]
            self.assertIn(
                "10.0.0.100", basic_addresses, "Missing first ip set for address pool"
            )
            logger.debug(
                "VPP's NAT44 address pool listing:\n{} ".format(
                    address_pool_listing.replace("\\n", "\n")
                )
            )

            # deleting NAT address pool
            reply = client.delete_configuration(config)
            logger.debug("Reply for deleting NAT address pool:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove NAT address pool from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only NAT address pool config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing NAT address pool from VPP",
            )

            # checking VPP
            address_pool_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 addresses", shell=True
            ).decode()
            basic_addresses = address_pool_listing.split(
                "NAT44 twice-nat pool addresses"
            )[0]
            self.assertNotIn(
                "10.0.0.100",
                basic_addresses,
                "At least one ip was not deleted from NAT44 address pool as it should have been",
            )
            logger.debug(
                "VPP's NAT44 address pool listing:\n{} ".format(
                    address_pool_listing.replace("\\n", "\n")
                )
            )

    def test_add_nat_interface_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            tap_out_config = models.InterfaceConfigurationItem(
                name="tap-nat-out", enabled=True, ip_addresses=["10.100.1.1/24"]
            )
            tap_in_config = models.InterfaceConfigurationItem(
                name="tap-nat-in", enabled=True, ip_addresses=["10.200.1.1/24"]
            )
            tap_out_nat_config = models.Nat44InterfaceConfigurationItem(
                name=tap_out_config.name, nat_outside=True
            )
            tap_in_nat_config = models.Nat44InterfaceConfigurationItem(
                name=tap_in_config.name, nat_inside=True
            )
            # add first tap (just to know which tap in VPP will be "tap0"(this one) and "tap1" the later one)
            reply = client.add_configuration(tap_out_config)
            logger.debug("Reply for configuring first tap:\n{} ".format(reply))
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add tap interface to VPP (apply_success)",
            )

            # add rest of the configuration
            reply = client.add_configuration(
                tap_out_nat_config, tap_in_nat_config, tap_in_config
            )
            logger.debug("Reply for configuring NAT interfaces:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add NAT interfaces to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to NAT interfaces to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            tap_out_nat_item = [
                item for item in reply.added_items if item.config == tap_out_nat_config
            ][0]
            self.assertIsInstance(
                tap_out_nat_item.metadata["vpp_dump"],
                NAT44InterfaceDetails,
                "bad type of vpp dump data",
            )

            # check VPP
            nat_interfaces_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 interfaces", shell=True
            ).decode()
            self.assertIn("tap0 out", nat_interfaces_listing, "Missing NAT output tap")
            self.assertIn("tap1 in", nat_interfaces_listing, "Missing NAT input tap")
            logger.debug(
                "VPP's NAT44 interfaces listing:\n{} ".format(
                    nat_interfaces_listing.replace("\\n", "\n")
                )
            )

    def test_delete_nat_interface_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            tap_in_config = models.InterfaceConfigurationItem(
                name="tap-nat-in", enabled=True, ip_addresses=["10.200.1.1/24"]
            )
            tap_in_nat_config = models.Nat44InterfaceConfigurationItem(
                name=tap_in_config.name, nat_inside=True
            )
            reply = client.add_configuration(tap_in_nat_config, tap_in_config)
            logger.debug("Reply for configuring NAT interface:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add NAT interface to VPP (apply_success)",
            )

            # check VPP (confirm state before delete)
            nat_interfaces_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 interfaces", shell=True
            ).decode()
            self.assertIn("tap0 in", nat_interfaces_listing, "Missing NAT input tap")
            logger.debug(
                "VPP's NAT44 interfaces listing:\n{} ".format(
                    nat_interfaces_listing.replace("\\n", "\n")
                )
            )

            # deleting NAT interface (only settings for NAT for given interface, not entire interface)
            reply = client.delete_configuration(tap_in_nat_config)
            logger.debug("Reply for deleting NAT interface:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove NAT interface from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only NAT interface config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                tap_in_nat_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing NAT interface from VPP",
            )

            # checking VPP
            nat_interfaces_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 interfaces", shell=True
            ).decode()
            self.assertNotIn(
                "tap0 in",
                nat_interfaces_listing,
                "NAT input tap was not deleted in VPP",
            )
            logger.debug(
                "VPP's NAT44 interfaces listing:\n{} ".format(
                    nat_interfaces_listing.replace("\\n", "\n")
                )
            )

    def test_add_dnat44_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            tcp_service_config = models.DNat44ConfigurationItem(
                label="tcp-service",
                static_mappings=[
                    models.StaticMapping(
                        external_ip=ipaddress.IPv4Address("80.80.80.80"),
                        external_port=8888,
                        protocol=models.ProtocolInNAT.TCP,
                        local_ips=[
                            models.LocalIP(
                                local_ip=ipaddress.IPv4Address("10.100.0.1"),
                                local_port=8000,
                            )
                        ],
                    )
                ],
                identity_mappings=[
                    models.IdentityMapping(
                        ip_address=ipaddress.IPv4Address("10.200.0.1"),
                        port=7000,
                        protocol=models.ProtocolInNAT.TCP,
                    )
                ],
            )
            reply = client.add_configuration(tcp_service_config)
            logger.debug("Reply for adding DNAT44 configuration:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add DNAT44 to VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add DNAT44 to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertIsInstance(
                reply.added_items[0].metadata["vpp_dump"],
                dict,
                "bad type of vpp dump data",
            )
            static_mappings = (
                reply.added_items[0].metadata["vpp_dump"].get("static_mappings")
            )
            self.assertIsInstance(
                static_mappings, list, "bad static mappings list type of vpp dump data"
            )
            self.assertIsInstance(
                static_mappings[0],
                NAT44StaticMappingDetails,
                "bad static mappings type of vpp dump data",
            )
            self.assertEqual(
                len(static_mappings), 1, "Only one static mapping was created"
            )
            self.assertEqual(
                static_mappings[0].tag,
                tcp_service_config.label,
                "Static mapping labeling mismatch",
            )

            identity_mappings = (
                reply.added_items[0].metadata["vpp_dump"].get("identity_mappings")
            )
            self.assertIsInstance(
                identity_mappings,
                list,
                "bad identity mappings list type of vpp dump data",
            )
            self.assertIsInstance(
                identity_mappings[0],
                NAT44IdentityMappingDetails,
                "bad identity mappings type of vpp dump data",
            )
            self.assertEqual(
                len(identity_mappings), 1, "Only one identity mapping was created"
            )
            self.assertEqual(
                identity_mappings[0].tag,
                tcp_service_config.label,
                "Identity mapping labeling mismatch",
            )

            # check VPP
            mapping_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 static mappings", shell=True
            ).decode()
            self.assertIn(
                "identity mapping TCP 10.200.0.1:7000 vrf 0",
                mapping_listing,
                "Missing identity mapping",
            )
            self.assertIn(
                "local 10.100.0.1:8000 external 80.80.80.80:8888 vrf 0",
                mapping_listing,
                "Missing static mapping",
            )
            logger.debug(
                "VPP's NAT44 mapping listing:\n{} ".format(
                    mapping_listing.replace("\\n", "\n")
                )
            )

    def test_delete_dnat44_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            tcp_service_config = models.DNat44ConfigurationItem(
                label="tcp-service",
                static_mappings=[
                    models.StaticMapping(
                        external_ip=ipaddress.IPv4Address("80.80.80.80"),
                        external_port=8888,
                        protocol=models.ProtocolInNAT.TCP,
                        local_ips=[
                            models.LocalIP(
                                local_ip=ipaddress.IPv4Address("10.100.0.1"),
                                local_port=8000,
                            )
                        ],
                    )
                ],
                identity_mappings=[
                    models.IdentityMapping(
                        ip_address=ipaddress.IPv4Address("10.200.0.1"),
                        port=7000,
                        protocol=models.ProtocolInNAT.TCP,
                    )
                ],
            )
            reply = client.add_configuration(tcp_service_config)
            logger.debug("Reply for adding DNAT44 configuration:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add DNAT44 to VPP (apply_success)"
            )

            # check VPP (confirm state before delete)
            mapping_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 static mappings", shell=True
            ).decode()
            self.assertIn(
                "identity mapping TCP 10.200.0.1:7000 vrf 0",
                mapping_listing,
                "Missing identity mapping",
            )
            self.assertIn(
                "local 10.100.0.1:8000 external 80.80.80.80:8888 vrf 0",
                mapping_listing,
                "Missing static mapping",
            )
            logger.debug(
                "VPP's NAT44 mapping listing:\n{} ".format(
                    mapping_listing.replace("\\n", "\n")
                )
            )

            # deleting DNAT44 config
            reply = client.delete_configuration(tcp_service_config)
            logger.debug("Reply for deleting DNAT44:\n{} ".format(reply))

            # checking reply
            self.assertIsInstance(
                reply, DeleteConfigurationItemsReply, "Bad reply type"
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove DNAT44e from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only DNAT44 config item should be processed(removed from VPP)",
            )
            self.assertIsInstance(
                reply.vpp_apply_attempted_items[0],
                ConfigurationItemReply,
                "Bad type of processed config item in reply",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].config,
                tcp_service_config,
                "Added config item and returned processed config item doesn't match",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when removing DNAT44 from VPP",
            )

            # checking VPP
            mapping_listing = subprocess.check_output(
                "docker exec vpp vppctl sh nat44 static mappings", shell=True
            ).decode()
            self.assertNotIn(
                "identity mapping TCP 10.200.0.1:7000 vrf 0",
                mapping_listing,
                "Removal of identity mapping failed",
            )
            self.assertNotIn(
                "local 10.100.0.1:8000 external 80.80.80.80:8888 vrf 0",
                mapping_listing,
                "Removal of static mapping failed",
            )
            logger.debug(
                "VPP's NAT44 mapping listing:\n{} ".format(
                    mapping_listing.replace("\\n", "\n")
                )
            )


class GRETestCases(ContainerizedServerTestCases):
    def test_add_gre_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            gre_interface_config = models.InterfaceConfigurationItem(
                name="my-gre",
                enabled=True,
                mtu=1480,
                ip_addresses=["10.100.1.1/24"],
                type=models.InterfaceType.GRE_TUNNEL,
                link=models.GREInterfaceLink(
                    type=models.GRELinkType.L3,
                    src_addr=ipaddress.IPv4Address("10.100.1.1"),
                    dst_addr=ipaddress.IPv4Address("10.100.1.10"),
                ),
            )
            reply = client.add_configuration(gre_interface_config)
            logger.debug("Reply for adding GRE interface:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add GRE tunnel to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add GRE tunnel to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check VPP
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh interface", shell=True
            ).decode()
            self.assertIn("gre0", interface_listing, "Missing GRE interface")
            self.assertIn(
                f"{gre_interface_config.mtu}",
                interface_listing,
                "GRE interface MTU was not set",
            )
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            gre_tunnel_listing = subprocess.check_output(
                "docker exec vpp vppctl sh gre tunnel",
                shell=True,
            ).decode()
            self.assertIn(
                f"{gre_interface_config.link.type.name}",
                gre_tunnel_listing,
                "Missing tunnel type for GRE tunnel",
            )
            self.assertIn(
                f"{str(gre_interface_config.link.src_addr)}",
                gre_tunnel_listing,
                "Missing source address for GRE tunnel",
            )
            self.assertIn(
                f"{str(gre_interface_config.link.dst_addr)}",
                gre_tunnel_listing,
                "Missing destination address for GRE tunnel",
            )
            logger.debug(
                "VPP's GRE tunnel listing:\n{}".format(
                    gre_tunnel_listing.replace("\\n", "\n")
                )
            )

    def test_delete_gre_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            gre_interface_config = models.InterfaceConfigurationItem(
                name="my-gre",
                enabled=True,
                mtu=1480,
                ip_addresses=["10.100.1.1/24"],
                type=models.InterfaceType.GRE_TUNNEL,
                link=models.GREInterfaceLink(
                    type=models.GRELinkType.L3,
                    src_addr=ipaddress.IPv4Address("10.100.1.1"),
                    dst_addr=ipaddress.IPv4Address("10.100.1.10"),
                ),
            )
            reply = client.add_configuration(gre_interface_config)
            logger.debug("Reply for adding GRE interface:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add GRE tunnel to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add GRE tunnel to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check VPP
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh interface", shell=True
            ).decode()
            self.assertIn("gre0", interface_listing, "Missing GRE interface")
            self.assertIn(
                f"{gre_interface_config.mtu}",
                interface_listing,
                "GRE interface MTU was not set",
            )
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            gre_tunnel_listing = subprocess.check_output(
                "docker exec vpp vppctl sh gre tunnel",
                shell=True,
            ).decode()
            self.assertIn(
                f"{gre_interface_config.link.type.name}",
                gre_tunnel_listing,
                "Missing tunnel type for GRE tunnel",
            )
            self.assertIn(
                f"{str(gre_interface_config.link.src_addr)}",
                gre_tunnel_listing,
                "Missing source address for GRE tunnel",
            )
            self.assertIn(
                f"{str(gre_interface_config.link.dst_addr)}",
                gre_tunnel_listing,
                "Missing destination address for GRE tunnel",
            )
            logger.debug(
                "VPP's GRE tunnel listing:\n{}".format(
                    gre_tunnel_listing.replace("\\n", "\n")
                )
            )

            reply = client.delete_configuration(gre_interface_config)
            logger.debug("Reply for deleting GRE interface:\n{} ".format(reply))

            # check reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove GRE tunnel from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check VPP
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh interface", shell=True
            ).decode()
            self.assertNotIn(
                "gre0",
                interface_listing,
                "Failed to remove GRE tunnel",
            )
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            gre_tunnel_listing = subprocess.check_output(
                "docker exec vpp vppctl sh gre tunnel",
                shell=True,
            ).decode()
            self.assertNotIn(
                f"{str(gre_interface_config.link.src_addr)}",
                gre_tunnel_listing,
                "Failed to remove GRE tunnel",
            )
            self.assertNotIn(
                f"{str(gre_interface_config.link.dst_addr)}",
                gre_tunnel_listing,
                "Failed to remove GRE tunnel",
            )
            logger.debug(
                "VPP's GRE tunnel listing:\n{}".format(
                    gre_tunnel_listing.replace("\\n", "\n")
                )
            )


class WireguardTestCases(ContainerizedServerTestCases):
    def test_add_wireguard_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            wireguard_interface_config = models.InterfaceConfigurationItem(
                name="my-wg",
                enabled=True,
                ip_addresses=["10.100.1.1/24"],
                type=models.InterfaceType.WIREGUARD_TUNNEL,
                mtu=1420,  # leaving some room for encryption encapsulation so that packet don't break into segments
                link=models.WireguardInterfaceLink(
                    private_key="cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=",  # encoded in base64
                    port=50001,
                    src_addr=ipaddress.IPv4Address("10.100.0.1"),
                ),
            )
            wireguard_peer_config = models.WireguardPeerConfigurationItem(
                public_key="hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=",  # encoded in base64
                port=50002,
                endpoint=ipaddress.IPv4Address("10.100.0.2"),
                allowed_ips=["0.0.0.0/0"],
                wg_if_name=wireguard_interface_config.name,
                persistent_keepalive=11,
            )
            reply = client.add_configuration(
                wireguard_interface_config, wireguard_peer_config
            )
            logger.debug("Reply for adding wireguard:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add wireguard to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add wireguard to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                reply.added_items[1].metadata.get(WIREGUARD_PEER_INDEX),
                0,
                "Wireguard peer index is missing",
            )
            self.assertIsInstance(
                reply.added_items[1].metadata["vpp_dump"],
                WireguardPeerDetail,
                "Bad vpp dump",
            )

            # check VPP
            interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh interface", shell=True
            ).decode()
            self.assertIn(
                f"{wireguard_interface_config.mtu}",
                interface_listing,
                "Wireguard interface MTU was not set",
            )
            logger.debug(
                "VPP's interface listing:\n{} ".format(
                    interface_listing.replace("\\n", "\n")
                )
            )
            wireguard_interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard interface", shell=True
            ).decode()
            self.assertIn(
                "wg0", wireguard_interface_listing, "Missing wireguard interface"
            )
            self.assertIn(
                f"private-key:{wireguard_interface_config.link.private_key}",
                wireguard_interface_listing,
                "Missing private-key for wireguard interface",
            )
            self.assertIn(
                f"port:{wireguard_interface_config.link.port}",
                wireguard_interface_listing,
                "Missing port for wireguard interface",
            )
            self.assertIn(
                f"src:{str(wireguard_interface_config.link.src_addr)}",
                wireguard_interface_listing,
                "Missing source address for wireguard interface",
            )
            logger.debug(
                "VPP's wireguard interface listing:\n{} ".format(
                    wireguard_interface_listing.replace("\\n", "\n")
                )
            )

            wireguard_peer_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard peer", shell=True
            ).decode()
            self.assertIn(
                "wg0",
                wireguard_peer_listing,
                "Peer missing link to wireguard interface",
            )
            self.assertIn(
                "endpoint:["
                f"{str(wireguard_interface_config.link.src_addr)}:{wireguard_interface_config.link.port}->"
                f"{str(wireguard_peer_config.endpoint)}:{wireguard_peer_config.port}]",
                wireguard_peer_listing,
                "Missing correct endpoint linking in wireguard peer",
            )
            self.assertIn(
                f"keep-alive:{wireguard_peer_config.persistent_keepalive}",
                wireguard_peer_listing,
                "Missing keepalive in wireguard peer",
            )
            self.assertIn(
                f"key:{wireguard_peer_config.public_key}",
                wireguard_peer_listing,
                "Missing public key in wireguard peer",
            )
            self.assertIn(
                f"allowed-ips: {str(wireguard_peer_config.allowed_ips[0])}",
                wireguard_peer_listing,
                "Missing allowed ips in wireguard peer",
            )
            logger.debug(
                "VPP's wireguard peer listing:\n{} ".format(
                    wireguard_peer_listing.replace("\\n", "\n")
                )
            )

    def test_delete_wireguard_configuration(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            wireguard_interface_config = models.InterfaceConfigurationItem(
                name="my-wg",
                enabled=True,
                ip_addresses=["10.100.1.1/24"],
                type=models.InterfaceType.WIREGUARD_TUNNEL,
                link=models.WireguardInterfaceLink(
                    private_key="cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=",  # encoded in base64
                    port=50001,
                    src_addr=ipaddress.IPv4Address("10.100.0.1"),
                ),
            )
            wireguard_peer_config = models.WireguardPeerConfigurationItem(
                public_key="hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=",  # encoded in base64
                port=50002,
                endpoint=ipaddress.IPv4Address("10.100.0.2"),
                allowed_ips=["0.0.0.0/0"],
                wg_if_name=wireguard_interface_config.name,
                persistent_keepalive=11,
            )
            reply = client.add_configuration(
                wireguard_interface_config, wireguard_peer_config
            )
            logger.debug("Reply for adding wireguard:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add wireguard to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add wireguard to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check VPP (checking correct state after addition and before delete)
            wireguard_interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard interface", shell=True
            ).decode()
            self.assertIn(
                "wg0", wireguard_interface_listing, "Missing wireguard interface"
            )
            logger.debug(
                "VPP's wireguard interface listing:\n{} ".format(
                    wireguard_interface_listing.replace("\\n", "\n")
                )
            )

            wireguard_peer_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard peer", shell=True
            ).decode()
            self.assertIn(
                "wg0",
                wireguard_peer_listing,
                "Peer missing link to wireguard interface",
            )
            logger.debug(
                "VPP's wireguard peer listing:\n{} ".format(
                    wireguard_peer_listing.replace("\\n", "\n")
                )
            )

            reply = client.delete_configuration(
                wireguard_interface_config, wireguard_peer_config
            )
            logger.debug("Reply for deleting wireguard:\n{} ".format(reply))

            # check reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove wireguard from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check VPP
            wireguard_interface_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard interface", shell=True
            ).decode()
            self.assertNotIn(
                "wg0",
                wireguard_interface_listing,
                "Wireguard interface was not removed",
            )
            logger.debug(
                "VPP's wireguard interface listing:\n{} ".format(
                    wireguard_interface_listing.replace("\\n", "\n")
                )
            )

            wireguard_peer_listing = subprocess.check_output(
                "docker exec vpp vppctl sh wireguard peer", shell=True
            ).decode()
            self.assertNotIn(
                "wg0", wireguard_peer_listing, "Wireguard peer was not removed"
            )
            logger.debug(
                "VPP's wireguard peer listing:\n{} ".format(
                    wireguard_peer_listing.replace("\\n", "\n")
                )
            )


class LCPTestCases(ContainerizedServerTestCases):
    def test_globals_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            lcp_globals_config = LCPGlobalsConfigurationItem(
                default_namespace="test",
                lcp_sync=True,  # Enables copying of changes made in VPP into their Linux counterpart
                # sub-interface creation in VPP automatically creates a Linux Interface Pair(LIP) and
                # its companion Linux network interface
                lcp_auto_subint=True,
            )
            # checking vpp state before setting it
            lcp_global_vpp_state = subprocess.check_output(
                "docker exec vpp vppctl show lcp", shell=True
            ).decode()
            self.assertIn(
                "lcp default netns '<unset>'",
                lcp_global_vpp_state,
                "No default namespace should be initially set",
            )
            self.assertIn(
                "lcp lcp-sync off",
                lcp_global_vpp_state,
                "LCP-sync should be initially disabled",
            )
            self.assertIn(
                "lcp lcp-auto-subint off",
                lcp_global_vpp_state,
                "LCP-auto-subint should be initially disabled",
            )
            logger.debug(
                "VPP's lcp global config:\n{} ".format(
                    lcp_global_vpp_state.replace("\\n", "\n")
                )
            )

            # setting global LCP configuration
            reply = client.add_configuration(lcp_globals_config)
            logger.debug("Reply for setting LCP global config:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add LCP global config to VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add LCP global config to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # checking vpp state
            lcp_global_vpp_state = subprocess.check_output(
                "docker exec vpp vppctl show lcp", shell=True
            ).decode()
            self.assertIn(
                f"lcp default netns '{lcp_globals_config.default_namespace}'",
                lcp_global_vpp_state,
                "default namespace is not set correctly",
            )
            self.assertIn(
                "lcp lcp-sync {}".format(
                    "on" if lcp_globals_config.lcp_sync else "off"
                ),
                lcp_global_vpp_state,
                "LCP-sync is not set correctly",
            )
            self.assertIn(
                "lcp lcp-auto-subint {}".format(
                    "on" if lcp_globals_config.lcp_auto_subint else "off"
                ),
                lcp_global_vpp_state,
                "LCP-auto-subint is not set correctly",
            )
            logger.debug(
                "VPP's lcp global config:\n{} ".format(
                    lcp_global_vpp_state.replace("\\n", "\n")
                )
            )

    def test_pair_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface_config = InterfaceConfigurationItem(
                name="my-tap", enabled=True, ip_addresses=["10.0.1.0/24"]
            )
            lcp_pair_config = LCPPairConfigurationItem(
                interface=interface_config.name,
                mirror_interface_host_name=f"host-{interface_config.name}",
                mirror_interface_type=LCPHostInterfaceTypeEnum.TAP,
                host_namespace="",  # current/default linux namespace
            )
            reply = client.add_configuration(interface_config, lcp_pair_config)
            logger.debug("Reply for adding LCP pair:\n{} ".format(reply))

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add LCP pair to VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add LCP pair to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertIsNotNone(
                reply.added_items[1].metadata.get(HOST_SW_IF_INDEX),
                "sw_if_index of vpp part of mirror tap tunnel not returned in reply",
            )
            self.assertIsInstance(
                reply.added_items[1].metadata["vpp_dump"], LCPPairDetail, "Bad vpp dump"
            )

            # wait for LCP to appear in VPP listing
            retry = 10
            while retry and (
                "itf-pair"
                not in subprocess.check_output(
                    "docker exec vpp vppctl sh lcp", shell=True
                ).decode()
            ):
                retry -= 1
                time.sleep(0.5)

            # check vpp
            lcp_pair_listing = subprocess.check_output(
                "docker exec vpp vppctl sh lcp", shell=True
            ).decode()
            self.assertIn(
                "itf-pair: [0] tap0 tap1 host-my-tap 3 type tap",
                lcp_pair_listing,
                "Missing added LCP pair",
            )
            logger.debug(
                "VPP's lcp pair listing:\n{} ".format(
                    lcp_pair_listing.replace("\\n", "\n")
                )
            )

            # check linux namespace
            linux_interface_listing = subprocess.check_output(
                "docker exec vpp ip addr sh", shell=True
            ).decode()
            self.assertIn(
                "host-my-tap",
                linux_interface_listing,
                "Missing linux host mirrored interface from LCP pair",
            )
            logger.debug(
                "Linux interface listing:\n{} ".format(
                    linux_interface_listing.replace("\\n", "\n")
                )
            )

            # delete LCP pair
            reply = client.delete_configuration(interface_config, lcp_pair_config)

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove LCP pair from VPP (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # wait for LCP to disappear in VPP listing
            retry = 10
            while retry and (
                "itf-pair"
                in subprocess.check_output(
                    "docker exec vpp vppctl sh lcp", shell=True
                ).decode()
            ):
                retry -= 1
                time.sleep(0.5)

            # check vpp
            lcp_pair_listing = subprocess.check_output(
                "docker exec vpp vppctl sh lcp", shell=True
            ).decode()
            self.assertNotIn(
                "itf-pair: [0] tap0 tap1 host-my-tap 3 type tap",
                lcp_pair_listing,
                "LCP pair not removed",
            )
            logger.debug(
                "VPP's lcp pair listing:\n{} ".format(
                    lcp_pair_listing.replace("\\n", "\n")
                )
            )

            # check linux namespace
            linux_interface_listing = subprocess.check_output(
                "docker exec vpp ip addr sh", shell=True
            ).decode()
            self.assertNotIn(
                "host-my-tap",
                linux_interface_listing,
                "Not removed linux host mirrored interface from removed LCP pair",
            )
            logger.debug(
                "Linux interface listing:\n{} ".format(
                    linux_interface_listing.replace("\\n", "\n")
                )
            )


class FRRTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.vpp_popen = subprocess.Popen(
            "docker run --rm --privileged --name vpp "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api-copy "
            + "-v /run/vpp:/run/vpp "
            + "-v /var/log/vpp:/var/log/vpp "
            + VPP_TEST_IMAGE_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        # FIXME: Manual one-time setup in OS: just add this to end of /etc/sudoers (using sudo visudo) to run
        #  "sudo chmod" without password:
        #   <current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/chmod
        #
        subprocess.call("sudo /usr/bin/chmod o+w /run/vpp/*.sock", shell=True)
        self.frr_popen = subprocess.Popen(
            "docker run --rm --privileged "
            + "-p 6666:6666 -p 7777:7777 "
            + "--name frr "
            + FRR_DOCKER_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        self.frr_ip_address = (
            (
                subprocess.check_output(
                    "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' frr",
                    shell=True,
                )
            )
            .decode()
            .replace("\n", "")
        )
        self.server_popen = subprocess.Popen(
            "docker run --rm --name server "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api "
            + "-v /run/vpp:/run/vpp "
            + SERVER_DOCKER_TAG
            + f" python -m vrouter.server.server --frr_agent_host={self.frr_ip_address} "
            + "--frr_agent_port=7777",
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        self.server_host = (
            (
                subprocess.check_output(
                    "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server",
                    shell=True,
                )
            )
            .decode()
            .replace("\n", "")
        )

    def tearDown(self) -> None:
        if self.server_popen:
            try:
                self.server_popen.terminate()
                self.server_popen.wait()
            except:
                logger.exception("can't teardown server docker process")
                pass
        if self.vpp_popen:
            try:
                self.vpp_popen.terminate()
                self.vpp_popen.wait()
            except:
                logger.exception("can't teardown VPP docker process")
                pass
        if self.frr_popen:
            try:
                self.frr_popen.terminate()
                self.frr_popen.wait()
            except:
                logger.exception("can't teardown FRR docker process")
                pass
        try:
            subprocess.call(
                "docker rm -f server",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown server docker container")
            pass
        try:
            subprocess.call(
                "docker rm -f vpp",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown vpp docker container")
            pass
        try:
            subprocess.call(
                "docker rm -f frr",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown frr docker container")
            pass

    def test_frr_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # PAPI++ server gets the default initial FRR configuration at startup -> ideal start for FRR config addition
            frr_init_config = [
                config_detail.config
                for config_detail in client.get_configuration().items
                if isinstance(config_detail.config, FRRConfigurationItem)
            ][0]

            # appending some bgp configuration to initial FRR config
            # (FRR config is updated, but that means just means delete of old config and add of new one. In case of FRR,
            # the delete does nothing because FRR need to have always some configuration. That means that only addition of
            # FRR configuration matters.)
            append_to_frr_config = (
                """ 
router bgp 100
 !
 address-family ipv4 unicast
  distance bgp 100 100 100
 exit-address-family
exit
!       
                """.strip(
                    "\n "
                )
                + "\n"
            )
            new_frr_config = FRRConfigurationItem(
                config=frr_init_config.config + append_to_frr_config
            )
            reply = client.update_configuration(frr_init_config, new_frr_config)

            # checking reply
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to remove config to FRR (apply_success)",
            )
            self.assertTrue(
                reply.all_updated_items_applied_to_vpp,
                "Failed to update config to FRR (added items applied)",
            )

            # check FRR
            running_frr_config = subprocess.check_output(
                """docker exec frr vtysh -c "write terminal" """, shell=True
            ).decode()
            self.assertIn(
                append_to_frr_config, running_frr_config, "Missing added configuration"
            )
            self.assertEqual(
                running_frr_config.replace(new_frr_config.config, "")
                .replace(" ", "")
                .replace("\n", ""),
                "Buildingconfiguration...Currentconfiguration:end",
                "FRR contains more configuration than expected",
            )
            logger.debug(
                "FRR's config:\n{} ".format(running_frr_config.replace("\\n", "\n"))
            )

    def test_route_reflector(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        # test variables
        route_destination_network = "1.2.3.4/32"
        ## real interface name in FRR linux namespace, also logical interface name in VPP config(not real VPP name!!!)
        interface_name = "my-interface"
        interface_ip_address_with_mask = "10.100.0.1/24"

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # create pair of interfaces for route referencing (one in vpp and one in FRR container linux namespace)
            try:
                subprocess.check_call(
                    f"docker exec frr ip link add {interface_name} type dummy",
                    shell=True,
                )
                subprocess.check_call(
                    f"docker exec frr ip link set {interface_name} up", shell=True
                )
                subprocess.check_call(
                    f"docker exec frr ip addr add {interface_ip_address_with_mask} dev {interface_name}",
                    shell=True,
                )
            except Exception:
                self.fail("failed to setup help interface in FRR linux namespace")
            reply = client.add_configuration(
                InterfaceConfigurationItem(
                    type=InterfaceType.TAP,
                    name=interface_name,
                    enabled=True,
                    ip_addresses=[interface_ip_address_with_mask],
                )
            )
            self.assertTrue(
                reply.processing_error == ""
                and reply.all_added_items_applied_to_vpp
                and reply.vpp_apply_success,
                "failed to setup help interface in VPP",
            )

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len(
                    [
                        item
                        for item in reply.items
                        if isinstance(item.config, RouteConfigurationItem)
                    ]
                ),
                0,
                "No route should be configured/reflected on server side",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn(
                route_destination_network,
                vpp_routes,
                "VPP should not contain the route yet",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))

            # inserting route into FRR container namespace (simulating FRR)
            self.assertEqual(
                subprocess.call(
                    f"docker exec frr ip route add {route_destination_network} dev {interface_name} proto 188",
                    shell=True,
                ),
                0,
                "failed to insert OSPF route into FRR linux namespace",
            )

            # wait for route reflector to catch linux namespace route change and push it into PAPI++ server
            retry = 10
            while retry and not [
                item
                for item in client.get_configuration().items
                if isinstance(item.config, RouteConfigurationItem)
            ]:
                retry -= 1
                time.sleep(0.5)

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            configured_routes = [
                item
                for item in reply.items
                if isinstance(item.config, RouteConfigurationItem)
            ]
            self.assertEqual(
                len(configured_routes),
                1,
                "Route should be reflected from FRR's route reflector on PAPI++ server side",
            )
            expected_route = RouteConfigurationItem(
                type=RouteType.INTRA_VRF,
                destination_network=f"{route_destination_network}",
                next_hop_address="",
                outgoing_interface=interface_name,
                weight=1,
            )
            self.assertEqual(
                configured_routes[0].config,
                expected_route,
                "reflected route is not configured as expected",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertIn(
                route_destination_network,
                vpp_routes,
                "VPP should contain the reflected route",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))

            # removing route from FRR container namespace (simulating FRR)
            self.assertEqual(
                subprocess.call(
                    f"docker exec frr ip route del {route_destination_network} dev {interface_name} proto 188",
                    shell=True,
                ),
                0,
                "failed to remove OSPF route from FRR linux namespace",
            )

            # wait for route reflector to catch linux namespace route change and push it into PAPI++ server
            retry = 10
            while retry and [
                item
                for item in client.get_configuration().items
                if isinstance(item.config, RouteConfigurationItem)
            ]:
                retry -= 1
                time.sleep(0.5)

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len(
                    [
                        item
                        for item in reply.items
                        if isinstance(item.config, RouteConfigurationItem)
                    ]
                ),
                0,
                "No route should be configured/reflected on server side after reflected route removal",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn(
                route_destination_network,
                vpp_routes,
                "VPP should not contain the route anymore",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))

    def test_route_reflector_ip_address_replacement(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        # test variables
        original_route_destination_network = "1.2.3.4/32"
        replaced_route_destination_network = "2.3.4.5/32"
        ## real interface name in FRR linux namespace, also logical interface name in VPP config(not real VPP name!!!)
        interface_name = "my-interface"
        interface_ip_address_with_mask = "10.100.0.1/24"

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # create pair of interfaces for route referencing (one in vpp and one in FRR container linux namespace)
            try:
                subprocess.check_call(
                    f"docker exec frr ip link add {interface_name} type dummy",
                    shell=True,
                )
                subprocess.check_call(
                    f"docker exec frr ip link set {interface_name} up", shell=True
                )
                subprocess.check_call(
                    f"docker exec frr ip addr add {interface_ip_address_with_mask} dev {interface_name}",
                    shell=True,
                )
            except Exception:
                self.fail("failed to setup help interface in FRR linux namespace")
            reply = client.add_configuration(
                InterfaceConfigurationItem(
                    type=InterfaceType.TAP,
                    name=interface_name,
                    enabled=True,
                    ip_addresses=[interface_ip_address_with_mask],
                )
            )
            self.assertTrue(
                reply.processing_error == ""
                and reply.all_added_items_applied_to_vpp
                and reply.vpp_apply_success,
                "failed to setup help interface in VPP",
            )

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len(
                    [
                        item
                        for item in reply.items
                        if isinstance(item.config, RouteConfigurationItem)
                    ]
                ),
                0,
                "No route should be configured/reflected on server side",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn(
                original_route_destination_network,
                vpp_routes,
                "VPP should not contain the original route",
            )
            self.assertNotIn(
                replaced_route_destination_network,
                vpp_routes,
                "VPP should not contain the replaced route yet",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))

            # configuring route reflector for ip address replacing
            # NOTE: this is testing quick and dirty code solution!!! #TODO change me when proper solution in tested code is there
            try:
                subprocess.check_call(
                    [
                        "docker",
                        "exec",
                        "-t",
                        "frr",
                        "sh",
                        "-c",
                        "touch /rr-ip-replace.txt;echo '"
                        + original_route_destination_network
                        + "=>"
                        + replaced_route_destination_network
                        + "' >> /rr-ip-replace.txt;"
                        "",
                    ],
                    stdout=subprocess_output,
                    stderr=subprocess_error_output,
                )
            except:
                logger.exception("failed to set ip-replace file")
                raise

            # inserting route into FRR container namespace (simulating FRR)
            self.assertEqual(
                subprocess.call(
                    f"docker exec frr ip route add {original_route_destination_network} dev {interface_name} proto 188",
                    shell=True,
                ),
                0,
                "failed to insert OSPF route into FRR linux namespace",
            )

            # wait for route reflector to catch linux namespace route change and push it into PAPI++ server
            retry = 10
            while retry and not [
                item
                for item in client.get_configuration().items
                if isinstance(item.config, RouteConfigurationItem)
            ]:
                retry -= 1
                time.sleep(0.5)

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            configured_routes = [
                item
                for item in reply.items
                if isinstance(item.config, RouteConfigurationItem)
            ]
            self.assertEqual(
                len(configured_routes),
                1,
                "Route should be reflected from FRR's route reflector on PAPI++ server side",
            )
            expected_route = RouteConfigurationItem(
                type=RouteType.INTRA_VRF,
                destination_network=f"{replaced_route_destination_network}",
                next_hop_address="",
                outgoing_interface=interface_name,
                weight=1,
            )
            self.assertEqual(
                configured_routes[0].config,
                expected_route,
                "reflected route is not configured as expected",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertIn(
                replaced_route_destination_network,
                vpp_routes,
                "VPP should contain the reflected route",
            )
            self.assertNotIn(
                original_route_destination_network,
                vpp_routes,
                "VPP should not contain the original route",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))

            # removing route from FRR container namespace (simulating FRR)
            self.assertEqual(
                subprocess.call(
                    f"docker exec frr ip route del {original_route_destination_network} dev {interface_name} proto 188",
                    shell=True,
                ),
                0,
                "failed to remove OSPF route from FRR linux namespace",
            )

            # wait for route reflector to catch linux namespace route change and push it into PAPI++ server
            retry = 10
            while retry and [
                item
                for item in client.get_configuration().items
                if isinstance(item.config, RouteConfigurationItem)
            ]:
                retry -= 1
                time.sleep(0.5)

            # check server state
            reply = client.get_configuration()
            logger.debug("Get config reply:\n{} ".format(reply))
            self.assertEqual(
                len(
                    [
                        item
                        for item in reply.items
                        if isinstance(item.config, RouteConfigurationItem)
                    ]
                ),
                0,
                "No route should be configured/reflected on server side after reflected route removal",
            )

            # check VPP state
            vpp_routes = subprocess.check_output(
                "docker exec vpp vppctl sh ip fib", shell=True
            ).decode()
            self.assertNotIn(
                original_route_destination_network,
                vpp_routes,
                "VPP should not contain the original route",
            )
            self.assertNotIn(
                replaced_route_destination_network,
                vpp_routes,
                "VPP should not contain the replaced route anymore",
            )
            logger.debug("vpp routes:\n{} ".format(vpp_routes))


class DHCPTestCases(unittest.TestCase):
    def setUp(self) -> None:
        # NOTE: vpp is not needed for DHCP functionality check but it is needed to start server
        self.vpp_popen = subprocess.Popen(
            "docker run --rm --privileged --name vpp "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api-copy "
            + "-v /run/vpp:/run/vpp "
            + "-v /var/log/vpp:/var/log/vpp "
            + VPP_TEST_IMAGE_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        # FIXME: Manual one-time setup in OS: just add this to end of /etc/sudoers (using sudo visudo) to run
        #  "sudo chmod" without password:
        #   <current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/chmod
        #
        subprocess.call("sudo /usr/bin/chmod o+w /run/vpp/*.sock", shell=True)
        ## for DEV env setup
        # local_kea_dir = "/home/dev/tmp/kea"
        # print(subprocess.call("/usr/bin/rm -rf " + local_kea_dir, shell=True))
        # print(subprocess.call("/usr/bin/mkdir -p " + local_kea_dir, shell=True))
        # print(subprocess.call("/usr/bin/chmod -R o+rwx " + local_kea_dir, shell=True))
        self.local_kea_dir_obj = tempfile.TemporaryDirectory(prefix="dhcp-test")
        local_kea_dir = self.local_kea_dir_obj.name
        subprocess.call("/usr/bin/chmod -R o+rwx " + local_kea_dir, shell=True)

        # TODO change to temporal directory
        self.dhcp_popen = subprocess.Popen(
            "docker run --rm --privileged --network none "
            + f"-v {local_kea_dir}:/run/kea "
            + "--name dhcp "
            + DHCP_DOCKER_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        self.server_popen = subprocess.Popen(
            "docker run --rm --name server "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api "
            + "-v /run/vpp:/run/vpp "
            + f"-v {local_kea_dir}:/run/kea "
            + SERVER_DOCKER_TAG
            + " python -m vrouter.server.server "
            # socket is defined in kea-dhcp4.conf and extracted by docker volume feature into host-located directory
            + f"--dhcp_socket=/run/kea/control_socket_4 ",
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        self.server_host = (
            (
                subprocess.check_output(
                    "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' server",
                    shell=True,
                )
            )
            .decode()
            .replace("\n", "")
        )

    def tearDown(self) -> None:
        if self.server_popen:
            try:
                self.server_popen.terminate()
                self.server_popen.wait()
            except:
                logger.exception("can't teardown server docker process")
                pass
        if self.vpp_popen:
            try:
                self.vpp_popen.terminate()
                self.vpp_popen.wait()
            except:
                logger.exception("can't teardown VPP docker process")
                pass
        if self.dhcp_popen:
            try:
                self.dhcp_popen.terminate()
                self.dhcp_popen.wait()
            except:
                logger.exception("can't teardown DHCP docker process")
                pass
        try:
            subprocess.call(
                "docker rm -f server",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown server docker container")
            pass
        try:
            subprocess.call(
                "docker rm -f vpp",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown vpp docker container")
            pass
        try:
            subprocess.call(
                "docker rm -f dhcp",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown dhcp docker container")
            pass
        try:
            self.local_kea_dir_obj.cleanup()
        except:
            logger.exception(
                "can't teardown kea runtime directory exposed from DHCP container"
            )
            pass

    def test_dhcp_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            dhcp_config = """ 
{
    "Dhcp4": {
        "subnet4": [
            {
                "subnet": "10.0.1.0/24",
                "pools": [
                    {
                        "pool": "10.0.1.1-10.0.1.250"
                    }
                ],
                "interface": "lo",
                "reservations-global": false,
                "reservations-in-subnet": true,
                "reservations-out-of-pool": false,
                "reservations": [
                {
                    "hw-address": "54:bf:64:d4:f3:45",
                    "ip-address": "10.0.1.100",
                    "hostname": "usdn-client-01-test",
                    "option-data": [
                       {
                            "code": 3,
                            "data": "10.0.1.254",
                            "name": "routers"
                       },
                       {
                            "code": 6,
                            "data": "8.8.8.8",
                            "name": "domain-name-servers"
                       },
                       {
                            "code": 15,
                            "data": "my.client.example.org",
                            "name": "domain-name"
                       },
                       {
                            "code": 26,
                            "data": "1498",
                            "name": "interface-mtu"
                       },
                       {
                            "code": 42,
                            "data": "185.125.190.58, 185.125.190.57",
                            "name": "ntp-servers"
                       }
                    ]
                }]
            }
        ],
        "interfaces-config": {
            "interfaces": [
                "lo"
            ],
            "dhcp-socket-type": "raw",
            "service-sockets-max-retries": 5,
            "service-sockets-require-all": false
        },
        "control-socket": {
            "socket-type": "unix",
            "socket-name": "/run/kea/control_socket_4"
        },
        "renew-timer": 1000,
        "rebind-timer": 2000,
        "valid-lifetime": 4000,
        "loggers": [
            {
                "name": "kea-dhcp4",
                "output_options": [
                    {
                        "output": "stdout"
                    }
                ],
                "severity": "DEBUG",
                "debuglevel": 7
            }
        ],
        "lease-database": {
            "type": "memfile",
            "persist": true,
            "name": "/var/lib/kea/dhcp4.leases"
        }
    }
}
            """
            reply = client.add_configuration(DHCPConfigurationItem(config=dhcp_config))
            print(reply)

            # checking reply
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to add config to DHCP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add config to DHCP (added items applied)",
            )

            # check DHCP
            # waiting for periodic script in DHCP docker to fix permissions for socket
            time.sleep(2)

            # save current running config to file (inside docker)
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.local_kea_dir_obj.name + "/control_socket_4")
            client.sendall(
                """{"command": "config-write","arguments": {"filename": "/tmp/config-modified.json"}}""".encode()
            )
            time.sleep(
                1
            )  # wait for response but ignore it (allow DHCP to reply before closing socket from client side)
            client.close()

            # check save running config
            retrieved_config = subprocess.check_output(
                "docker exec dhcp cat /tmp/config-modified.json", shell=True
            ).decode()
            self.assertIn(
                "10.0.1.0/24", retrieved_config, "config is not correctly applied"
            )

    def test_json_invalid_dhcp_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            invalid_dhcp_config = """ 
{
    "Dhcp4": {
        "subnet4": [
    }
}
            """
            reply = client.add_configuration(
                DHCPConfigurationItem(config=invalid_dhcp_config)
            )
            print(reply)

            # checking reply
            self.assertFalse(
                reply.vpp_apply_success,
                "Failed to detect problems with input config (apply_success)",
            )
            self.assertFalse(
                reply.all_added_items_applied_to_vpp,
                "Failed to detect problems with input config (added items applied)",
            )
            self.assertIn(
                "Config is not parsable json",
                reply.vpp_apply_attempted_items[0].error,
                "Result has incorrect error message",
            )

    def test_logically_invalid_dhcp_configuration(self):
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            invalid_dhcp_config = """ 
{
    "Dhcp4": {
        "control-socket": {
            "socket-type": "unix",
            "socket-name": "/run/kea/control_socket_4"
        },
        "loggers": [
            {
                "name": "kea-dhcp4",
                "output_options": [
                    {
                        "output": "stdout"
                    }
                ],
                "severity": "DEBUG",
                "debuglevel": 7
            }
        ],
        "lease-database": {
            "type": "!!!non existing lease database type!!!"
        }
    }
}
            """
            reply = client.add_configuration(
                DHCPConfigurationItem(config=invalid_dhcp_config)
            )
            print(reply)

            # checking reply
            self.assertFalse(
                reply.vpp_apply_success,
                "Failed to detect problems with input config (apply_success)",
            )
            self.assertFalse(
                reply.all_added_items_applied_to_vpp,
                "Failed to detect problems with input config (added items applied)",
            )
            self.assertIn(
                "Remote validation of config failed",
                reply.vpp_apply_attempted_items[0].error,
                "Result has incorrect error message (not mentioned remote validation as source of failure)",
            )
            self.assertIn(
                # tested message is from DHCP server -> can fail when DHCP server implementation changes
                "unknown backend database type",
                reply.vpp_apply_attempted_items[0].error,
                "Result has incorrect error message (not mentioned expected problematic json field)",
            )


class PacketCapturingTestCases(ContainerizedServerTestCases):
    def test_simple_packet_capture(self):
        """Tests simple packet capture with active packet flow to capture"""

        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # configure packet capturing and interface for traffic flow
            tap_tunnel_config = models.InterfaceConfigurationItem(
                name="my-tap",
                enabled=True,
                ip_addresses=["10.0.1.1/24"],
            )
            pcap_config = models.RunningPacketCapture(
                output_file_prefix="example",
                max_packets_to_capture="10",
                capture_rx_packets=True,
                capture_tx_packets=True,
                capture_dropped_packets=True,
                capture_only_from_interface=tap_tunnel_config.name,
                # or models.PCAP_ANY_INTERFACE to capture from all interfaces
                capture_by_matching_rules=[
                    models.L2PacketMatchingRule(
                        # src_physical_address="",  # i.e. "02:fe:c2:6c:9d:bb" or "" to ignore
                        # dest_physical_address="",  # i.e. "02:fe:56:ac:8f:8a" or "" to ignore
                        protocol=0x800
                        # L2's IP4 (https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def)
                        # or don't do capture by protocol by using models.NO_PROTOCOL
                    ),
                    models.L3PacketMatchingRule(
                        # src_ipv4_address="",  # i.e. "10.0.1.2" or "" to ignore
                        dest_ipv4_address=tap_tunnel_config.ip_addresses[0][
                            :-3
                        ],  # i.e. "10.0.1.1" or "" to ignore
                        protocol=1,
                        # L3's ICMP (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
                        # or don't do capture by protocol by using models.NO_PROTOCOL
                    ),
                ],
            )

            # setup the vpp end of tap tunnel
            reply = client.add_configuration(tap_tunnel_config)

            # check reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add tap to VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add tap to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # setup the linux end of tap tunnel (Note: this is not part of API as it is not needed for failover usecase,
            # just for testing)
            try:
                subprocess.check_call("docker exec vpp ip link set tap0 up", shell=True)
                subprocess.check_call(
                    "docker exec vpp ip addr add 10.0.1.2/24 dev tap0", shell=True
                )
            except Exception as e:
                self.fail(f"failed to setup the linux end of tap: {e}")

            # start capturing
            reply = client.add_configuration(pcap_config)

            # check reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to start packet capturing inside VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to start packet capturing inside VPP  (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # make some traffic by pinging
            ping_count = 2
            try:
                subprocess.check_call(
                    f"docker exec vpp ping -c {ping_count} -i 0.2 "
                    f"{tap_tunnel_config.ip_addresses[0][:-3]}",
                    shell=True,
                )
            except Exception as e:
                self.fail(f"failed to ping ({e})")

            # stop capturing (and store result to file)
            # (Note: removal of tap interface is not present as it is not important/VPP container will
            # clean it up anyway)
            reply = client.delete_configuration(pcap_config)

            # check reply (common parts)
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to stop packet capturing (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only packet capture stopping should be processed(removed from VPP)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when stopping packet capturing",
            )

            # check reply (capture parts)
            capture_reply = reply.vpp_apply_attempted_items[0].metadata
            # Note: packet count = ICMP request and reply -> ping_count * 2, ignoring ARP packets (only ICMP protocol
            # is filtered)
            self.assertEqual(
                capture_reply["count_of_captured_packets"],
                ping_count * 2,
                "Captured packet count reported by VPP CLI doesn't match executed pings",
            )
            self.assertIsInstance(
                capture_reply["packet_capture_output_file"],
                str,
                "FullPath packet capture file name should be string",
            )
            self.assertNotEqual(
                capture_reply["packet_capture_output_file"],
                "FullPath packet capture file name should not be empty",
            )

            # check packet capture output file (with tcpdump)
            try:
                subprocess.check_call(
                    f"docker exec vpp test -f {capture_reply['packet_capture_output_file']}",
                    shell=True,
                )
            except Exception:
                self.fail("packet capture output file doesn't exist")
            tcpdump_output = subprocess.check_output(
                f"docker exec vpp tcpdump -nr "
                f"{capture_reply['packet_capture_output_file']}",
                shell=True,
            ).decode()
            logger.debug(
                "tcpdump_output:\n{} ".format(tcpdump_output.replace("\\n", "\n"))
            )
            self.assertEqual(
                tcpdump_output.count("\n"),
                ping_count * 2,
                "Pcap output file has unexpected count of packets",
            )
            src_ip = "10.0.1.2"
            dst_ip = tap_tunnel_config.ip_addresses[0][:-3]
            self.assertEqual(
                tcpdump_output.count(f"{src_ip} > {dst_ip}: ICMP echo request"),
                2,
                "Pcap is missing some ICMP echo requests",
            )
            self.assertEqual(
                tcpdump_output.count(f"{dst_ip} > {src_ip}: ICMP echo reply"),
                2,
                "Pcap is missing some ICMP echo replies",
            )

    def test_filtering_out_all_packets(self):
        """Tests packet capturing with active packet flow to capture, but with filters that block to capture any traffic.

        This is needed due to different handling from VPP side when no packets are captured
        """

        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # configure packet capturing and interface for traffic flow
            tap_tunnel_config = models.InterfaceConfigurationItem(
                name="my-tap",
                enabled=True,
                ip_addresses=["10.0.1.1/24"],
            )
            pcap_config = models.RunningPacketCapture(
                output_file_prefix="example",
                max_packets_to_capture="10",
                capture_rx_packets=True,
                capture_tx_packets=True,
                capture_dropped_packets=True,
                capture_only_from_interface=tap_tunnel_config.name,
                # or models.PCAP_ANY_INTERFACE to capture from all interfaces
                capture_by_matching_rules=[
                    models.L3PacketMatchingRule(
                        # not defined IP address -> ping packets won't have it -> will filter out all traffic
                        dest_ipv4_address="1.2.3.4"
                    )
                ],
            )

            # setup the vpp end of tap tunnel
            reply = client.add_configuration(tap_tunnel_config)

            # check reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add tap to VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add tap to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # setup the linux end of tap tunnel (Note: this is not part of API as it is not needed for failover usecase,
            # just for testing)
            try:
                subprocess.check_call("docker exec vpp ip link set tap0 up", shell=True)
                subprocess.check_call(
                    "docker exec vpp ip addr add 10.0.1.2/24 dev tap0", shell=True
                )
            except Exception as e:
                self.fail(f"failed to setup the linux end of tap: {e}")

            # start capturing
            reply = client.add_configuration(pcap_config)

            # check reply
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to start packet capturing inside VPP (apply_success)",
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to start packet capturing inside VPP  (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # make some traffic by pinging
            ping_count = 2
            try:
                subprocess.check_call(
                    f"docker exec vpp ping -c {ping_count} -i 0.2 "
                    f"{tap_tunnel_config.ip_addresses[0][:-3]}",
                    shell=True,
                )
            except Exception as e:
                self.fail(f"failed to ping ({e})")

            # stop capturing (and store result to file)
            # (Note: removal of tap interface is not present as it is not important/VPP container will
            # clean it up anyway)
            reply = client.delete_configuration(pcap_config)

            # check reply (common parts)
            self.assertTrue(
                reply.vpp_apply_success,
                "Failed to stop packet capturing (apply_success)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )
            self.assertEqual(
                len(reply.vpp_apply_attempted_items),
                1,
                "Only packet capture stopping should be processed(removed from VPP)",
            )
            self.assertEqual(
                reply.vpp_apply_attempted_items[0].error,
                "",
                "There should be no error from VPP when stopping packet capturing",
            )

            # check reply (capture parts)
            capture_reply = reply.vpp_apply_attempted_items[0].metadata
            # Note: packet count = ICMP request and reply -> ping_count * 2, ignoring ARP packets (only ICMP protocol
            # is filtered)
            self.assertEqual(
                capture_reply["count_of_captured_packets"],
                0,
                "There should be no captured packets",
            )
            self.assertIsInstance(
                capture_reply["packet_capture_output_file"],
                str,
                "FullPath packet capture file name should be string",
            )
            self.assertEqual(
                capture_reply["packet_capture_output_file"],
                "",
                "No fullPath to packet capture file should be given as no packets were captured and "
                "therefore no write to file happened",
            )

    def test_capture_api_calls(self):
        """Tests whether different capture filters are correctly applied to VPP

        This doesn't test the actual VPP functionality of capturing the packets correctly according to given filters.
        This test should just prevent possible problems with VPP CLI changes (or our code changes to current VPP CLI)
        """

        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient(server_host=self.server_host) as client:
            # configure interface that capturing can reference
            tap_tunnel_config = models.InterfaceConfigurationItem(
                name="my-tap",
                enabled=True,
                ip_addresses=["10.0.1.1/24"],
            )

            # setup the vpp end of tap tunnel
            reply = client.add_configuration(tap_tunnel_config)

            # check reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add tap to VPP (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add tap to VPP (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            cases = (
                {
                    "name": "rx only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_rx_packets=True,
                        capture_tx_packets=False,
                        capture_dropped_packets=False,
                    ),
                },
                {
                    "name": "tx only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_rx_packets=False,
                        capture_tx_packets=True,
                        capture_dropped_packets=False,
                    ),
                },
                {
                    "name": "dropped only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_rx_packets=False,
                        capture_tx_packets=False,
                        capture_dropped_packets=True,
                    ),
                },
                {
                    "name": "rx,tx,drop",
                    "pcap_config": models.RunningPacketCapture(
                        capture_rx_packets=True,
                        capture_tx_packets=True,
                        capture_dropped_packets=True,
                    ),
                },
                {
                    "name": "using one interface",
                    "pcap_config": models.RunningPacketCapture(
                        capture_only_from_interface="my-tap"
                    ),
                },
                {
                    "name": "full L3 rule",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L3PacketMatchingRule(
                                src_ipv4_address="1.2.3.4",
                                dest_ipv4_address="2.3.4.5",
                                protocol=1,
                                # ICMP (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
                            )
                        ]
                    ),
                },
                {
                    "name": "L3 rule - src only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L3PacketMatchingRule(
                                src_ipv4_address="1.2.3.4",
                            )
                        ]
                    ),
                },
                {
                    "name": "L3 rule - dst only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L3PacketMatchingRule(
                                dest_ipv4_address="2.3.4.5",
                            )
                        ]
                    ),
                },
                {
                    "name": "L3 rule - protocol only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L3PacketMatchingRule(
                                protocol=1
                                # ICMP (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
                            )
                        ]
                    ),
                },
                {
                    "name": "full L2 rule",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L2PacketMatchingRule(
                                src_physical_address="F8-DC-E7-A6-28-87",
                                dest_physical_address="A0-91-85-16-DD-2A",
                                protocol=0x800,
                                # 2048 https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def
                            )
                        ]
                    ),
                },
                {
                    "name": "L2 rule - src only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L2PacketMatchingRule(
                                src_physical_address="F8-DC-E7-A6-28-87",
                            )
                        ]
                    ),
                },
                {
                    "name": "L2 rule - dst only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L2PacketMatchingRule(
                                dest_physical_address="A0-91-85-16-DD-2A",
                            )
                        ]
                    ),
                },
                {
                    "name": "L2 rule - protocol only",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L2PacketMatchingRule(
                                protocol=0x800
                                # 2048 https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def
                            )
                        ]
                    ),
                },
                {
                    "name": "full L3 and L2 rule",
                    "pcap_config": models.RunningPacketCapture(
                        capture_by_matching_rules=[
                            models.L2PacketMatchingRule(
                                src_physical_address="F8-DC-E7-A6-28-87",
                                dest_physical_address="A0-91-85-16-DD-2A",
                                protocol=0x800,
                                # 2048 https://github.com/FDio/vpp/blob/stable/2206/src/vnet/ethernet/types.def
                            ),
                            models.L3PacketMatchingRule(
                                src_ipv4_address="1.2.3.4",
                                dest_ipv4_address="2.3.4.5",
                                protocol=1,
                                # ICMP (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml)
                            ),
                        ]
                    ),
                },
            )

            for case in cases:
                with self.subTest(case["name"]):
                    # start capturing
                    reply = client.add_configuration(case["pcap_config"])

                    # check reply
                    self.assertTrue(
                        reply.vpp_apply_success,
                        "Failed to start packet capturing inside VPP (apply_success)",
                    )
                    self.assertTrue(
                        reply.all_added_items_applied_to_vpp,
                        "Failed to start packet capturing inside VPP  (added items applied)",
                    )
                    self.assertEqual(
                        reply.processing_error,
                        "",
                        "No error from server internal processing should be here.",
                    )

                    # stop capturing (and store result to file)
                    reply = client.delete_configuration(case["pcap_config"])

                    # check reply (common parts)
                    self.assertTrue(
                        reply.vpp_apply_success,
                        "Failed to stop packet capturing (apply_success)",
                    )
                    self.assertEqual(
                        reply.processing_error,
                        "",
                        "No error from server internal processing should be here.",
                    )
                    self.assertEqual(
                        len(reply.vpp_apply_attempted_items),
                        1,
                        "Only packet capture stopping should be processed(removed from VPP)",
                    )
                    self.assertEqual(
                        reply.vpp_apply_attempted_items[0].error,
                        "",
                        "There should be no error from VPP when stopping packet capturing",
                    )

                    # check reply (capture parts)
                    capture_reply = reply.vpp_apply_attempted_items[0].metadata
                    self.assertEqual(
                        capture_reply["count_of_captured_packets"],
                        0,
                        "There should be no captured packets",
                    )
                    self.assertEqual(
                        capture_reply["packet_capture_output_file"],
                        "",
                        "No fullPath to packet capture file should be given as no packets were "
                        "captured and therefore no write to file happened",
                    )


class LinuxConfigurationTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.vpp_popen = subprocess.Popen(
            "docker run --rm --privileged --name vpp "
            + "-v /usr/share/vpp/api:/usr/share/vpp/api-copy "
            + "-v /run/vpp:/run/vpp "
            + "-v /var/log/vpp:/var/log/vpp "
            + VPP_TEST_IMAGE_TAG,
            shell=True,
            stdout=subprocess_output,
            stderr=subprocess_error_output,
        )
        time.sleep(3)  # TODO do waiting on some condition instead of hardcoded waiting
        # FIXME: Manual one-time setup in OS: just add this to end of /etc/sudoers (using sudo visudo) to run
        #  "sudo chmod" without password:
        #   <current_user_name> ALL=(ALL:ALL) NOPASSWD: /usr/bin/chmod
        subprocess.call("sudo /usr/bin/chmod o+w /run/vpp/*.sock", shell=True)

        # start server in host (=not within docker container due to network namespaces visibility and
        # docker usage through linux cmd line)
        def run_server(delay):
            subprocess.check_call(
                """poetry run python3 -m vrouter.server.server """,
                cwd=project_root_dir,
                shell=True,
            )

        self.server_process = multiprocessing.Process(
            name="Server-process", target=run_server, args=(1,)
        )
        self.server_process.start()
        time.sleep(5)  # TODO do waiting on some condition instead of hardcoded waiting

    def tearDown(self) -> None:
        # kill the server
        try:
            self.server_process.terminate()
        except Exception as e:
            print("Error: unable to terminate server due to ", e)
        subprocess.call(
            """kill $(ps aux | grep 'poetry run python3 \-m vrouter.server.server' | awk '{print $2}')""",
            shell=True,
        )
        subprocess.call(
            """kill $(ps aux | grep 'python3 \-m vrouter.server.server' | awk '{print $2}')""",
            shell=True,
        )

        if self.vpp_popen:
            try:
                self.vpp_popen.terminate()
                self.vpp_popen.wait()
            except:
                logger.exception("can't teardown VPP docker process")
                pass
        try:
            subprocess.call(
                "docker rm -f vpp",
                shell=True,
                stdout=subprocess_output,
                stderr=subprocess_error_output,
            )
        except:
            logger.exception("can't teardown vpp docker container")
            pass

    def test_veth_tunnel(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            veth_tunnel_config = models.LinuxDockerVethTunnelConfigurationItem(
                docker_container_name="vpp",  # using VPP container also for veth tunnel testing
                host_interface_name="my-host-veth",
                docker_interface_name="my-veth",
                host_interface_ip_addresses=["10.0.1.1/24"],
                docker_interface_ip_addresses=["10.0.1.2/24"],
            )

            # add veth tunnel between VPP docker container and docker host
            reply = client.add_configuration(veth_tunnel_config)

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add veth tunnel (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add veth tunnel (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check linux namespace
            docker_interface_listing = subprocess.check_output(
                f"docker exec {veth_tunnel_config.docker_container_name} ip addr sh",
                shell=True,
            ).decode()
            self.assertIn(
                veth_tunnel_config.docker_interface_name,
                docker_interface_listing,
                "Missing veth tunnel end in docker container",
            )
            self.assertIn(
                veth_tunnel_config.docker_interface_ip_addresses[0],
                docker_interface_listing,
                "IP address not correctly configured for veth tunnel end in docker container",
            )
            self.assertEqual(
                docker_interface_listing.count("state UP"),
                2,
                "Veth tunnel end in docker container is not enabled (it should be up together "
                "with default docker eth0 interface)",
            )
            logger.debug(
                "Interface listing from docker container:\n{} ".format(
                    docker_interface_listing.replace("\\n", "\n")
                )
            )
            host_interface_listing = subprocess.check_output(
                "ip addr sh", shell=True
            ).decode()
            self.assertIn(
                veth_tunnel_config.host_interface_name,
                host_interface_listing,
                "Missing veth tunnel end in host",
            )
            self.assertIn(
                veth_tunnel_config.host_interface_ip_addresses[0],
                host_interface_listing,
                "IP address not correctly configured for veth tunnel end in host",
            )
            self.assertIn(
                "state UP",
                subprocess.check_output(
                    f"ip addr sh {veth_tunnel_config.host_interface_name}", shell=True
                ).decode(),
                "Veth tunnel end in docker container is not enabled (it should be up together "
                "with default docker eth0 interface)",
            )
            logger.debug(
                "Interface listing from host:\n{} ".format(
                    host_interface_listing.replace("\\n", "\n")
                )
            )

            # ping through the veth tunnel
            try:
                subprocess.check_call(
                    f"docker exec vpp ping -c 3 -i 0.2 "
                    f"{veth_tunnel_config.host_interface_ip_addresses[0][:-3]}",
                    shell=True,
                )
            except Exception as e:
                self.fail(f"failed to ping through the veth tunnel ({e})")

            # remove veth tunnel
            reply = client.delete_configuration(veth_tunnel_config)

            # checking reply
            self.assertTrue(reply.vpp_apply_success, "Failed to remove veth tunnel")
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check linux namespace
            docker_interface_listing = subprocess.check_output(
                f"docker exec {veth_tunnel_config.docker_container_name} ip addr sh",
                shell=True,
            ).decode()
            self.assertNotIn(
                veth_tunnel_config.docker_interface_name,
                docker_interface_listing,
                "Veth tunnel end in docker container was not removed",
            )
            logger.debug(
                "Interface listing from docker container:\n{} ".format(
                    docker_interface_listing.replace("\\n", "\n")
                )
            )
            host_interface_listing = subprocess.check_output(
                "ip addr sh", shell=True
            ).decode()
            self.assertNotIn(
                veth_tunnel_config.host_interface_name,
                host_interface_listing,
                "Veth tunnel end in host was not removed",
            )
            logger.debug(
                "Interface listing from host:\n{} ".format(
                    host_interface_listing.replace("\\n", "\n")
                )
            )

    def test_linux_route_in_container(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            route_config = models.LinuxRouteConfigurationItem(
                docker_container_name="vpp",  # using VPP container also for route testing
                destination_network="10.0.1.0/24",
                outgoing_interface="eth0",
            )

            # add linux route
            reply = client.add_configuration(route_config)

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add route (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add route (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check container interfaces
            route_listing = subprocess.check_output(
                f"docker exec {route_config.docker_container_name} ip route sh",
                shell=True,
            ).decode()
            self.assertIn(
                route_config.destination_network
                + " dev "
                + route_config.outgoing_interface,
                route_listing,
                "Missing route in docker container",
            )
            logger.debug(
                "Route listing from docker container:\n{} ".format(
                    route_listing.replace("\\n", "\n")
                )
            )

            # remove route
            reply = client.delete_configuration(route_config)

            # checking reply
            self.assertTrue(reply.vpp_apply_success, "Failed to remove route")
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check container interfaces
            route_listing = subprocess.check_output(
                f"docker exec {route_config.docker_container_name} ip route sh",
                shell=True,
            ).decode()
            self.assertNotIn(
                route_config.destination_network
                + " dev "
                + route_config.outgoing_interface,
                route_listing,
                "Route was not removed from docker container",
            )
            logger.debug(
                "Route listing from docker container:\n{} ".format(
                    route_listing.replace("\\n", "\n")
                )
            )

    def test_linux_route_in_host(self):
        from vpp_vrouter.common import models
        from vpp_vrouter.client.client import ExtendedVPPAPIClient

        with ExtendedVPPAPIClient() as client:
            interface_name = (
                subprocess.check_output(
                    "ip addr show | awk '/inet.*brd/{print $NF; exit}'", shell=True
                )
                .decode()
                .replace("\n", "")
            )
            route_config = models.LinuxRouteConfigurationItem(
                docker_container_name="",  # install route in host
                destination_network="10.0.1.0/24",
                outgoing_interface=interface_name,
            )

            # add linux route
            reply = client.add_configuration(route_config)

            # checking reply
            self.assertTrue(
                reply.vpp_apply_success, "Failed to add route (apply_success)"
            )
            self.assertTrue(
                reply.all_added_items_applied_to_vpp,
                "Failed to add route (added items applied)",
            )
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check container interfaces
            route_listing = subprocess.check_output("ip route sh", shell=True).decode()
            self.assertIn(
                route_config.destination_network
                + " dev "
                + route_config.outgoing_interface,
                route_listing,
                "Missing route in host",
            )
            logger.debug(
                "Route listing from host:\n{} ".format(
                    route_listing.replace("\\n", "\n")
                )
            )

            # remove route
            reply = client.delete_configuration(route_config)

            # checking reply
            self.assertTrue(reply.vpp_apply_success, "Failed to remove route")
            self.assertEqual(
                reply.processing_error,
                "",
                "No error from server internal processing should be here.",
            )

            # check container interfaces
            route_listing = subprocess.check_output("ip route sh", shell=True).decode()
            self.assertNotIn(
                route_config.destination_network
                + " dev "
                + route_config.outgoing_interface,
                route_listing,
                "Route was not removed from host",
            )
            logger.debug(
                "Route listing from host:\n{} ".format(
                    route_listing.replace("\\n", "\n")
                )
            )


if __name__ == "__main__":
    unittest.main()
