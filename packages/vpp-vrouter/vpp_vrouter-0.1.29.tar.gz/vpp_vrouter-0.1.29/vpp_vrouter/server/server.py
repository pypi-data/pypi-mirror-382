"""
Server that configures VPP
"""

import fnmatch
import logging
import os
import threading

from vpp_vrouter.common.utils import configure_main_logger, configure_pyro5_logging

configure_pyro5_logging()  # must be before any Pyro5 import to configure logging
logger = configure_main_logger("papi-server", logging.INFO)

from vpp_papi import VPPApiClient, VPPIOError

from vpp_vrouter.server import pyro
from vpp_vrouter.server import __version__  # dynamically resolved from package / pyproject
from vpp_vrouter.common.models import (
    SW_IF_INDEX,
    NO_INTERFACE_SW_INDEX,
    InterfaceType,
    InterfaceConfigurationItem,
    ApplyReply,
    State,
    AddConfigurationItemsReply,
    ConfigurationItemReply,
    ConfigurationItemDetail,
    GetConfigurationItemsReply,
    VPP_DUMP_KEY,
    DeleteConfigurationItemsReply,
    ACLConfigurationItem,
    ACL_INDEX,
    NO_ACL_INDEX,
    WireguardPeerConfigurationItem,
    WIREGUARD_PEER_INDEX,
    NO_WIREGUARD_PEER_INDEX,
    VPPConfigUpdater,
    UpdateConfigurationItemsReply,
    RunningPacketCapture,
    IF_STATUS_API_FLAG_ADMIN_UP,
    VPPStatsReply,
)
from vpp_vrouter.server.handlers import (
    InterfaceHandler,
    RouteHandler,
    ACLHandler,
    Nat44AddressPoolHandler,
    Nat44InterfaceHandler,
    DNat44Handler,
    WireguardPeerHandler,
    FRRHandler,
    FRRAgentClient,
    LCPHandler,
    RunningPacketCaptureHandler,
    LinuxDockerVethTunnelHandler,
    LinuxRouteHandler,
    DHCPHandler,
)


def _get_vpp_api_json_files(vpp_json_root_dir):
    """Get filenames of VPP API JSON files"""
    jsonfiles = []

    for root, dirnames, filenames in os.walk(vpp_json_root_dir):
        for filename in fnmatch.filter(filenames, "*.api.json"):
            jsonfiles.append(os.path.join(root, filename))

    if not jsonfiles:
        logger.error("no json api files found")
        exit(-1)
    return jsonfiles


class ExtendedVPPClient:
    """Client based on fd.io VPP client that have extended capabilties.

    Don't interchange it with client.ExtendedVPPAPIClient. This client is extension of fd.io VPP client and serves as
    main implementation of Pyro5 server. This is where client.ExtendedVPPAPIClient to call end
    """

    def __init__(
        self,
        vpp_api_json_root_dir,
        vpp_socket_full_path,
        frr_agent_host="0.0.0.0",
        frr_agent_port=7777,
        dhcp_socket="/run/kea/control_socket_4",
    ):
        self._init_inner_vpp_client(vpp_api_json_root_dir, vpp_socket_full_path)
        self._frr_agent_host = frr_agent_host
        self._frr_agent_port = frr_agent_port
        self._dhcp_socket = dhcp_socket
        self._register_handlers()
        self._configuration_item_records = set()
        self._config_init_from_vpp_dump()
        self._config_init_from_frr_dump()
        self._configure_route_reflector()
        self._transaction_counter = 0

    def _init_inner_vpp_client(self, vpp_api_json_root_dir, vpp_socket_full_path):
        """Setup fd.io client"""
        self.inner_vpp_client = VPPApiClient(
            apifiles=_get_vpp_api_json_files(vpp_api_json_root_dir),
            server_address=vpp_socket_full_path,
        )
        try:
            rv = self.inner_vpp_client.connect("extended_vpp_client")
        except VPPIOError as e:
            logger.exception(f"can't connect to VPP due to ${e}")
            exit(-1)
        if rv != 0:
            logger.error(f"can't connect to VPP (return value ${rv}")
            exit(-1)
        # TODO: where to put vpp_client.disconnect()?

    def _register_handlers(self):
        self.handlers = [
            InterfaceHandler(self.inner_vpp_client, self.get_sw_if_index),
            RouteHandler(self.inner_vpp_client, self.get_sw_if_index),
            ACLHandler(self.inner_vpp_client, self.get_sw_if_index, self.get_acl_index),
            Nat44AddressPoolHandler(self.inner_vpp_client),
            Nat44InterfaceHandler(self.inner_vpp_client, self.get_sw_if_index),
            DNat44Handler(self.inner_vpp_client, self.get_sw_if_index),
            WireguardPeerHandler(
                self.inner_vpp_client,
                self.get_sw_if_index,
                self.get_wireguard_peer_index,
            ),
            LCPHandler(self.inner_vpp_client, self.get_sw_if_index),
            RunningPacketCaptureHandler(
                self.inner_vpp_client,
                self.get_sw_if_index,
                self.get_current_running_packet_capture,
            ),
            LinuxDockerVethTunnelHandler(),
            LinuxRouteHandler(),
            DHCPHandler(self._dhcp_socket),
        ]
        if (
            self._frr_agent_host
        ):  # enable FRR only if FRR Agent address is configured (non-empty string)
            self.handlers.append(FRRHandler(self._frr_agent_host, self._frr_agent_port))

    def _config_init_from_vpp_dump(self):
        """Read state from VPP instance and convert it to server state (ConfigurationItemRecord-s)"""
        for interface_detail in self.inner_vpp_client.api.sw_interface_dump():
            configuration_item = InterfaceConfigurationItem(
                name=interface_detail.interface_name,
                type=InterfaceType.get_from_vpp_str(
                    interface_detail.interface_dev_type
                ),
                enabled=(interface_detail.flags & IF_STATUS_API_FLAG_ADMIN_UP) != 0,
                # ignoring ip_addresses
            )
            self._configuration_item_records.add(
                ConfigurationItemRecord(
                    configuration_item,
                    self._get_handler(configuration_item),
                    init_state=State.APPLIED,
                    metadata={SW_IF_INDEX: interface_detail.sw_if_index},
                )
            )

    def _config_init_from_frr_dump(self):
        """Read state from FRR instance and convert it to server state (ConfigurationItemRecord-s)"""
        if not self._frr_agent_host:  # disabling FRR if not configured properly
            return
        frr_handler = [
            handler for handler in self.handlers if isinstance(handler, FRRHandler)
        ][0]
        self._configuration_item_records.add(
            ConfigurationItemRecord(
                frr_handler.dump_from_vpp({}),
                frr_handler,
                init_state=State.APPLIED,
                metadata={},
            )
        )

    def _configure_route_reflector(self):
        """Inform route reflector in FRR's agent how to connect back to this server.

        FRR starts first and this server is configured with info how to connect to FRR agent. However, the FRR agent
        needs to connect to this server too (learned BGP route must be copied into VPP using this server). So this
        method informs FRR's agent how to do it."""

        if not self._frr_agent_host:  # disabling FRR if not configured properly
            return
        try:
            with FRRAgentClient(
                frr_agent_host=self._frr_agent_host, frr_agent_port=self._frr_agent_port
            ) as client:
                client.configure_route_reflector(
                    papi_server_host=pyro.get_external_ip_address(),
                    papi_server_port=9999,
                )
        except Exception:
            logger.exception("can't configure FRR's route reflector")

    def get_sw_if_index(
        self, interface_name
    ):  # FIXME get this info somehow without compromising vpp_client API
        for record in self._configuration_item_records:
            if (
                isinstance(record.configuration_item, InterfaceConfigurationItem)
                and record.state == State.APPLIED
                and record.configuration_item.name == interface_name
            ):
                return record.metadata[SW_IF_INDEX]
        return NO_INTERFACE_SW_INDEX  # FIXME Or raise error?

    def get_acl_index(
        self, acl_name
    ):  # FIXME get this info somehow without compromising vpp_client API
        for record in self._configuration_item_records:
            if (
                isinstance(record.configuration_item, ACLConfigurationItem)
                and record.state == State.APPLIED
                and record.configuration_item.name == acl_name
            ):
                return record.metadata[ACL_INDEX]
        return NO_ACL_INDEX  # FIXME Or raise error?

    # FIXME get this info somehow without compromising vpp_client API
    def get_wireguard_peer_index(self, wg_peer_config_item):
        for record in self._configuration_item_records:
            if (
                isinstance(record.configuration_item, WireguardPeerConfigurationItem)
                and record.state == State.APPLIED
                and record.configuration_item == wg_peer_config_item
            ):
                return record.metadata[WIREGUARD_PEER_INDEX]
        return NO_WIREGUARD_PEER_INDEX  # FIXME Or raise error?

    def get_current_running_packet_capture(self):
        for record in self._configuration_item_records:
            if (
                isinstance(record.configuration_item, RunningPacketCapture)
                and record.state == State.APPLIED
            ):
                return record.configuration_item
        return None

    def get_vpp_stats(self, query) -> 'VPPStatsReply':
        """On-demand VPP statistics collection (transient query API only).

        Accepts a VPPStatsQuery and returns a VPPStatsReply. Legacy configuration-item
        based stats collection has been removed.
        """
        from datetime import datetime
        from vpp_vrouter.common.models import (
            VPPStatsReply,
            VPPStatsEntry,
            VPPStatsType,
            VPPCounterValue,
            VPPStatsQuery,
        )

        if not isinstance(query, VPPStatsQuery):
            raise TypeError(
                f"Unsupported stats query type: {type(query)}. Provide VPPStatsQuery"
            )
        try:

            logger.info(
                "Collecting VPP stats (transient) interfaces=%s patterns=%s include_errors=%s",
                query.interface_names,
                query.patterns,
                query.include_error_counters,
            )

            # Build patterns/paths
            stat_paths = set(query.patterns or [])

            # Interface specific paths (modern)
            for if_name in query.interface_names:
                # Base path (may expand depending on VPP version)
                stat_paths.add(f"/interfaces/{if_name}")
                for leaf in ("rx", "tx", "drops"):
                    stat_paths.add(f"/interfaces/{if_name}/{leaf}")

            # Legacy interface paths '/if/<leaf>' aggregate - always include if user requested interfaces but no explicit pattern
            if query.interface_names and not query.disable_legacy_interface_paths:
                for leaf in ("rx", "tx", "drops"):
                    stat_paths.add(f"/if/{leaf}")
                # include names vector for index-to-name mapping fallback
                stat_paths.add("/if/names")

            # Error counters (avoid broad '/err' root; use common specific prefixes)
            if query.include_error_counters:
                stat_paths.update({
                    "/err/ip4-input",
                    "/err/ip6-input",
                })

            # If nothing specified default to interface aggregates
            if not stat_paths:
                stat_paths.update({"/if/rx", "/if/tx", "/if/drops"})

            from vpp_papi.vpp_stats import VPPStats
            import os

            if not os.path.exists(query.stats_socket_path):
                raise FileNotFoundError(f"Stats socket not found: {query.stats_socket_path}")

            # Some versions of vpp_papi.vpp_stats.VPPStats expect the stats socket path
            # as a positional first argument; older/newer variants may use different
            # parameter names. Use a defensive instantiation strategy.
            try:
                stats_client = VPPStats(query.stats_socket_path)
            except TypeError:
                # Fallback: try without arguments (default path) and later verify path matches
                stats_client = VPPStats()
                if query.stats_socket_path != "/run/vpp/stats.sock":
                    logger.warning(
                        "Using default VPP stats socket; requested '%s' may be ignored by current vpp_papi version",
                        query.stats_socket_path,
                    )
            # Collect stats per-path to avoid one failing path aborting everything
            raw: dict = {}
            path_failures: dict = {}
            for p in sorted(stat_paths):
                try:
                    part = stats_client.dump([p])
                    raw.update(part)
                except Exception as pe:
                    path_failures[p] = str(pe)
            try:
                stats_client.disconnect()
            except Exception:
                pass
            timestamp = datetime.utcnow().isoformat()
            entries: list[VPPStatsEntry] = []

            def to_entry(name: str, value) -> VPPStatsEntry:
                """Simplified conversion aligned with direct dump usage.

                Rules:
                  - list of (packets, bytes) tuples => combined counter vector (per-thread, single interface)
                  - list of ints/floats => simple counter vector (per-thread, single interface) unless /err/ path
                  - list of strings => name vector
                  - dict (thread->list) retained (old heuristic) for completeness
                  - scalar numeric => scalar
                  - /err/ + list[int] => error vector
                """
                # Scalar
                if isinstance(value, (int, float)):
                    return VPPStatsEntry(name=name, type=VPPStatsType.SCALAR, scalar_value=float(value))

                # List based structures
                if isinstance(value, list):
                    # Detect combined vector presented as list of StatsTuple/dict objects (one per interface per thread?)
                    # Heuristic: entry like /interfaces/<if>/rx gives list length == threads, each element {packets, bytes}
                    if value and all(
                        (isinstance(x, (tuple, list)) and len(x) == 2 and all(isinstance(y, (int, float)) for y in x))
                        or (isinstance(x, dict) and {'packets', 'bytes'} <= set(x.keys()))
                        for x in value
                    ):
                        combined_vec = [[
                            VPPCounterValue(
                                packets=int(x[0] if not isinstance(x, dict) else x['packets']),
                                bytes=int(x[1] if not isinstance(x, dict) else x['bytes'])
                            )
                        ] for x in value]
                        return VPPStatsEntry(name=name, type=VPPStatsType.COUNTER_VECTOR_COMBINED, combined_counter_vec=combined_vec)

                    # /if/rx style: list per thread where each element is a list of per-interface dicts {'packets','bytes'}
                    if value and all(isinstance(thread_block, list) for thread_block in value):
                        # Check if first thread block looks like list of dict packets/bytes
                        first_block = value[0]
                        if first_block and all(isinstance(d, dict) and {'packets','bytes'} <= set(d.keys()) for d in first_block):
                            combined_vec: list[list[VPPCounterValue]] = []
                            for thread_block in value:
                                combined_vec.append([
                                    VPPCounterValue(packets=int(d['packets']), bytes=int(d['bytes'])) for d in thread_block
                                ])
                            return VPPStatsEntry(name=name, type=VPPStatsType.COUNTER_VECTOR_COMBINED, combined_counter_vec=combined_vec)

                    if value and all(isinstance(x, str) for x in value):
                        return VPPStatsEntry(name=name, type=VPPStatsType.NAME_VECTOR, name_vector=value)
                    if value and all(isinstance(x, (int, float)) for x in value):
                        if name.startswith('/err/'):
                            return VPPStatsEntry(name=name, type=VPPStatsType.ERROR_INDEX, error_vector=[int(x) for x in value])
                        simple_vec = [[int(x)] for x in value]
                        return VPPStatsEntry(name=name, type=VPPStatsType.COUNTER_VECTOR_SIMPLE, simple_counter_vec=simple_vec)

                # Dict heuristic (legacy path)
                if isinstance(value, dict):
                    thread_values = list(value.values())
                    if thread_values and all(isinstance(tv, list) for tv in thread_values):
                        first_list = thread_values[0]
                        if first_list and all(isinstance(x, (list, tuple)) and len(x) == 2 for x in first_list):
                            combined_vec = []
                            for thread_list in thread_values:
                                combined_vec.append([
                                    VPPCounterValue(packets=int(p), bytes=int(b)) for p, b in thread_list
                                ])
                            return VPPStatsEntry(name=name, type=VPPStatsType.COUNTER_VECTOR_COMBINED, combined_counter_vec=combined_vec)
                        elif first_list and all(isinstance(x, (int, float)) for x in first_list):
                            simple_vec = []
                            for thread_list in thread_values:
                                simple_vec.append([int(x) for x in thread_list])
                            return VPPStatsEntry(name=name, type=VPPStatsType.COUNTER_VECTOR_SIMPLE, simple_counter_vec=simple_vec)

                # Fallback to scalar zero
                return VPPStatsEntry(name=name, type=VPPStatsType.SCALAR, scalar_value=0.0)

            debug_lines = []
            if getattr(query, 'debug', False):
                debug_lines.append(f"Requested paths: {sorted(stat_paths)}")
                if path_failures:
                    debug_lines.append(f"Failed paths: {path_failures}")
            for name, value in raw.items():
                try:
                    entry = to_entry(name, value)
                    entries.append(entry)
                    if getattr(query, 'debug', False):
                        # Summarize shape
                        if isinstance(value, list):
                            sample = value[0] if value else None
                            debug_lines.append(
                                f"RAW {name}: list len={len(value)} sample_type={type(sample).__name__} sample={sample} mapped={entry.type.value}"
                            )
                        elif isinstance(value, dict):
                            keys_preview = list(value.keys())[:3]
                            debug_lines.append(
                                f"RAW {name}: dict threads={len(value)} keys_preview={keys_preview} mapped={entry.type.value}"
                            )
                        else:
                            debug_lines.append(
                                f"RAW {name}: type={type(value).__name__} value_preview={str(value)[:60]} mapped={entry.type.value}"
                            )
                except Exception as conv_e:
                    logger.warning("Failed to convert stat %s: %s", name, conv_e)
                    if getattr(query, 'debug', False):
                        debug_lines.append(f"ERROR converting {name}: {conv_e}")

            partial_success = bool(entries)
            reply = VPPStatsReply(
                success=partial_success,
                timestamp=timestamp,
                entries=entries,
                debug_info=debug_lines if getattr(query, 'debug', False) else [],
            )
            if not partial_success:
                reply.error = "All requested paths failed" if path_failures else "No statistics collected"
            logger.info("Collected %d VPP stats entries", len(entries))
            return reply
        except Exception as e:
            error_msg = f"Failed to get VPP stats: {e}"
            logger.error(error_msg, exc_info=True)
            return VPPStatsReply(
                success=False,
                error=error_msg,
                timestamp=datetime.now().isoformat(),
                entries=[],
            )

    def _get_handler(self, configuration_item):
        for handler in self.handlers:
            if handler.is_handling_configuration_item(configuration_item):
                return handler

    def add_configuration(
        self, *configuration_items, context: str = ""
    ) -> AddConfigurationItemsReply:
        """Server implementation for adding configuration items"""

        if not configuration_items:
            # nothing to apply, but that nothing is applied successfully
            return AddConfigurationItemsReply()

        # check duplicate config items
        duplicate_config_items = [
            record.get_configuration_item_reply()
            for configuration_item in configuration_items
            for record in self._configuration_item_records
            if configuration_item == record.configuration_item
        ]
        if (
            duplicate_config_items
        ):  # duplicate config items are expected to fail config item addition
            return AddConfigurationItemsReply(
                processing_error="Found duplicate config items.",
                all_added_items_applied_to_vpp=False,
                # TODO move duplicated items to processing error, make it Error instead of string?
                added_items=duplicate_config_items,
            )

        # update configuration
        added_config_record = []
        for configuration_item in configuration_items:
            metadata = {"context": context} if context else dict()
            new_record = ConfigurationItemRecord(
                configuration_item,
                self._get_handler(configuration_item),
                metadata=metadata,
            )
            added_config_record.append(new_record)
            self._configuration_item_records.add(new_record)

        # get all configuration that can be applied
        def get_what_can_be_directly_added_to_vpp():
            labels_of_applied_config = {
                label
                for conf_item in self._configuration_item_records
                if conf_item.state == State.APPLIED
                for label in conf_item.handler.get_labels(conf_item.configuration_item)
            }
            not_applied_conf_items = {
                conf_item
                for conf_item in self._configuration_item_records
                if conf_item.state
                not in [
                    State.APPLIED,
                    State.BLOCKED_BY_ADD_APPLY_FAILURE,
                    State.BLOCKED_BY_REMOVE_APPLY_FAILURE,
                ]
            }
            return [
                not_applied_conf_item
                for not_applied_conf_item in not_applied_conf_items
                if not_applied_conf_item.handler.get_dependency_labels(
                    not_applied_conf_item.configuration_item
                ).issubset(labels_of_applied_config)
            ]

        # applied configuration that is new/unblocked
        configuration_item_replies = []
        self._transaction_counter += 1
        ignore_for_blocked_records_output = set()
        # TODO rename transaction to "Config Application" ?
        #  (it is not really a transaction due to lack of rollback and final commit)
        logger.info(
            "{}\nTransaction {} started\n{}".format(
                "=" * 30, self._transaction_counter, "=" * 30
            )
        )
        while True:
            can_be_added = get_what_can_be_directly_added_to_vpp()
            if can_be_added:
                for index, to_add in enumerate(can_be_added):
                    try:
                        reply = to_add.handler.add_to_vpp(to_add.configuration_item)
                    except Exception as e:
                        logger.exception(
                            f"Exception raised while applying {to_add.configuration_item}"
                        )
                        reply = ApplyReply(success=False, error=repr(e))
                    if reply.success:
                        logger.info(
                            "\tSUCCESS: added to VPP config item {}".format(
                                repr(to_add.configuration_item)
                            )
                        )
                        to_add.state = State.APPLIED
                        to_add.metadata.update(reply.vpp_data)
                        configuration_item_replies.append(
                            to_add.get_configuration_item_reply()
                        )
                        try:
                            to_add.metadata[VPP_DUMP_KEY] = (
                                to_add.handler.dump_from_vpp(to_add.configuration_item)
                            )
                        except Exception as e:
                            logger.warning(
                                f"No dump data from VPP will be provided due to failure of dumping: {str(e)} "
                                + f"(dumping for configuration item {to_add.configuration_item})"
                            )
                    else:
                        logger.error(
                            "\tFAILED: adding to VPP config item {}\n\t\tREASON:{}".format(
                                repr(to_add.configuration_item), reply.error
                            )
                        )
                        to_add.state = State.BLOCKED_BY_ADD_APPLY_FAILURE
                        ignore_for_blocked_records_output.add(to_add)
                        configuration_item_replies.append(
                            to_add.get_configuration_item_reply(error=reply.error)
                        )
                        # TODO reapply of failing config? with some retry limit?
            else:
                # change state for new config items not picked for applying (=> they are blocked by something)
                for conf_item in self._configuration_item_records:
                    if conf_item.state == State.RECEIVED:
                        conf_item.state = State.BLOCKED

                self._print_blocked_records(
                    ignore_records=ignore_for_blocked_records_output
                )
                break
        logger.info(
            "{}\nTransaction {} ended\n{}\n".format(
                "=" * 30, self._transaction_counter, "=" * 30
            )
        )

        return AddConfigurationItemsReply(
            all_added_items_applied_to_vpp=not (
                False
                in [record.state == State.APPLIED for record in added_config_record]
            ),
            added_items=[
                record.get_configuration_item_detail() for record in added_config_record
            ],
            vpp_apply_success=not (
                True in [bool(reply.error) for reply in configuration_item_replies]
            ),
            vpp_apply_attempted_items=configuration_item_replies,
        )

    def _print_blocked_records(self, ignore_records=set()):
        """Retrieve and print configuration items that are for some reason blocked and prints them (as part
        of the transaction)"""

        labels_of_applied_config = {
            label
            for conf_item in self._configuration_item_records
            if conf_item.state == State.APPLIED
            for label in conf_item.handler.get_labels(conf_item.configuration_item)
        }
        for record in self._configuration_item_records.difference(ignore_records):
            match record.state:
                case State.BLOCKED:
                    logger.warning(
                        "\tBLOCKED: {}\n\t\tBY:{}".format(
                            repr(record.configuration_item),
                            repr(
                                record.handler.get_dependency_labels(
                                    record.configuration_item
                                ).difference(labels_of_applied_config)
                            ),
                        )
                    )
                case State.BLOCKED_BY_ADD_APPLY_FAILURE:
                    logger.warning(
                        "\tBLOCKED: {}\n\t\tBY: Transaction failure (while adding config)".format(
                            repr(record.configuration_item)
                        )
                    )
                case State.BLOCKED_BY_REMOVE_APPLY_FAILURE:
                    logger.warning(
                        "\tBLOCKED: {}\n\t\tBY: Transaction failure (while removing config)".format(
                            repr(record.configuration_item)
                        )
                    )

    def delete_configuration(
        self, *configuration_items
    ) -> DeleteConfigurationItemsReply:
        """Delete given configuration items from VPP and from VPP extended client.

        In case of problems deleting it from VPP, configuration item is not deleted from VPP extended client and
        its state changes to BLOCKED_BY_REMOVE_APPLY_FAILURE.

        Full cascade delete is not supported. That means that when configuration item that is not provided as input
        for this delete method depends on configuration item that should be deleted (=is input for this delete method)
        then it will not be deleted. However, if dependency is detected between input configuration items, their delete
        order is accordingly reordered. This means that if you provide all dependent configuration items as input, then
        everything will be removed in correct order and no leftover configuration items will be hanging (i.e. deleting
        only wireguard interface will not delete also dependent wireguard peers, but if you provide also peers in input
        then reordering will remove peers first and then wireguard interface and everything is correctly deleted)
        """
        # TODO full cascade removal of configuration is unsupported! (it should not be needed for failover case)
        if not configuration_items:
            # nothing to delete, but that nothing is deleted successfully
            return DeleteConfigurationItemsReply()

        # check for unknown config items
        record_configs = [
            record.configuration_item for record in self._configuration_item_records
        ]
        unknown_configs = [
            configuration_item
            for configuration_item in configuration_items
            if configuration_item not in record_configs
        ]
        if unknown_configs:
            return DeleteConfigurationItemsReply(
                # TODO move unknown items to processing error, make it Error instead of string?
                processing_error="Can't delete configuration item that was not previously added",
                vpp_apply_success=False,
                vpp_apply_attempted_items=unknown_configs,
            )

        # reordering of input configuration items according to dependencies (inverse order to adding config items)
        def dependency_based_reorder_for_delete(records):
            # computing correct ordering if we want to add configuration items
            ordered = []
            unordered = records.copy()
            while unordered:
                labels_from_unordered = {
                    label
                    for record in unordered
                    for label in record.handler.get_labels(record.configuration_item)
                }
                no_dependencies_records = [
                    record
                    for record in unordered
                    if not record.handler.get_dependency_labels(
                        record.configuration_item
                    ).intersection(labels_from_unordered)
                ]
                for record in no_dependencies_records:
                    ordered.append(record)
                    unordered.remove(record)

            # making from adding ordering the removal ordering
            ordered.reverse()

            return ordered

        # delete configuration items
        configuration_item_replies = []
        logger.info(
            "{}\nTransaction {} started\n{}".format(
                "=" * 30, self._transaction_counter, "=" * 30
            )
        )
        records_to_delete = [
            record
            for configuration_item in configuration_items
            for record in self._configuration_item_records
            if configuration_item == record.configuration_item
        ]
        for to_delete in dependency_based_reorder_for_delete(records_to_delete):
            try:
                reply = to_delete.handler.remove_from_vpp(to_delete.configuration_item)
            except Exception as e:
                logger.exception(
                    f"Exception raised while removing {to_delete.configuration_item}"
                )
                reply = ApplyReply(success=False, error=repr(e))
            if reply.success:
                logger.info(
                    "\tSUCCESS: removed from VPP config item {}".format(
                        repr(to_delete.configuration_item)
                    )
                )
                to_delete.metadata.update(reply.vpp_data)
                configuration_item_replies.append(
                    to_delete.get_configuration_item_reply()
                )
                self._configuration_item_records.discard(to_delete)
            else:
                logger.error(
                    "\tFAILED: removing from VPP config item {}\n\t\tREASON:{}".format(
                        repr(to_delete.configuration_item), reply.error
                    )
                )
                to_delete.state = State.BLOCKED_BY_REMOVE_APPLY_FAILURE
                configuration_item_replies.append(
                    to_delete.get_configuration_item_reply(error=reply.error)
                )

        logger.info(
            "{}\nTransaction {} ended\n{}\n".format(
                "=" * 30, self._transaction_counter, "=" * 30
            )
        )
        return DeleteConfigurationItemsReply(
            vpp_apply_success=not (
                True in [bool(reply.error) for reply in configuration_item_replies]
            ),
            vpp_apply_attempted_items=configuration_item_replies,
        )

    def update_configuration(
        self, old_configuration_item, new_configuration_item, context: str = ""
    ):
        """Server implementation for updating configuration items"""

        if self._get_handler(old_configuration_item) != self._get_handler(
            new_configuration_item
        ):
            return UpdateConfigurationItemsReply(
                processing_error="old and new configuration item must be of the same "
                "type (handled by the same handler)"
            )
        # handle generic case (=simple removal of old config item and adding new config item)
        handler = self._get_handler(old_configuration_item)
        if not isinstance(
            handler, VPPConfigUpdater
        ):  # no special update treatment -> plain delete and add
            delete_reply = self.delete_configuration(old_configuration_item)
            if (
                delete_reply.processing_error != ""
                or not delete_reply.vpp_apply_success
            ):
                return UpdateConfigurationItemsReply(
                    processing_error=delete_reply.processing_error,
                    vpp_apply_success=delete_reply.vpp_apply_success,
                    vpp_apply_attempted_items=delete_reply.vpp_apply_attempted_items,
                )
            add_reply = self.add_configuration(new_configuration_item, context=context)
            return UpdateConfigurationItemsReply(
                processing_error=add_reply.processing_error,
                all_updated_items_applied_to_vpp=add_reply.all_added_items_applied_to_vpp,
                updated_items=add_reply.added_items,
                vpp_apply_success=add_reply.vpp_apply_success,
                vpp_apply_attempted_items=add_reply.vpp_apply_attempted_items,
            )

        # handle special updates
        if isinstance(old_configuration_item, InterfaceConfigurationItem):
            # Note: the whole update was done to just update DPDK interface that is created by automatically by server
            # start -> making simplified update for this case:
            # 1. no unblocking of additional ConfigurationItems because DPDK interface exists before this update
            # 2. no blocking of this ConfigurationItem as DPDK interface doesn't depend on anything
            # -> can run handler's update_in_vpp method directly

            # check duplicate config items
            duplicate_config_items = [
                record.get_configuration_item_reply()
                for record in self._configuration_item_records
                if new_configuration_item == record.configuration_item
            ]
            if (
                duplicate_config_items
            ):  # duplicate config items are expected to fail config item addition
                return UpdateConfigurationItemsReply(
                    processing_error="Found duplicate config items.",
                    all_added_items_applied_to_vpp=False,
                    added_items=duplicate_config_items,
                )

            # update configuration
            records = [
                record
                for record in self._configuration_item_records
                if record.configuration_item == old_configuration_item
            ]
            if not records:
                return UpdateConfigurationItemsReply(
                    processing_error="Old configuration not found in server state records"
                )
            record = records[0]

            configuration_item_replies = []
            self._transaction_counter += 1
            logger.info(
                "{}\nTransaction {} started\n{}".format(
                    "=" * 30, self._transaction_counter, "=" * 30
                )
            )
            try:
                reply = handler.update_in_vpp(
                    old_configuration_item, new_configuration_item
                )
            except Exception as e:
                logger.exception(
                    f"Exception raised while updating {old_configuration_item} to "
                    f"{new_configuration_item}"
                )
                reply = ApplyReply(success=False, error=repr(e))
            if reply.success:
                logger.info(
                    "\tSUCCESS: updated VPP config item from {} to {}".format(
                        repr(old_configuration_item), repr(new_configuration_item)
                    )
                )
                record.state = State.APPLIED
                record.configuration_item = new_configuration_item
                configuration_item_replies.append(record.get_configuration_item_reply())
                record.metadata[VPP_DUMP_KEY] = handler.dump_from_vpp(
                    new_configuration_item
                )
                # Note: don't need to update sw_if_index in metadata as that didn't change
            else:
                logger.error(
                    "\tFAILED: updating VPP config item from {} to {}\n\t\tREASON:{}".format(
                        repr(old_configuration_item),
                        repr(new_configuration_item),
                        reply.error,
                    )
                )
                record.state = State.BLOCKED_BY_UPDATE_APPLY_FAILURE
                record.configuration_item = new_configuration_item
                configuration_item_replies.append(
                    record.get_configuration_item_reply(error=reply.error)
                )
            logger.info(
                "{}\nTransaction {} ended\n{}\n".format(
                    "=" * 30, self._transaction_counter, "=" * 30
                )
            )

            return UpdateConfigurationItemsReply(
                all_updated_items_applied_to_vpp=record.state == State.APPLIED,
                updated_items=[record.get_configuration_item_detail()],
                vpp_apply_success=not (
                    True in [bool(reply.error) for reply in configuration_item_replies]
                ),
                vpp_apply_attempted_items=configuration_item_replies,
            )

        # TODO implement generic code for special-written updates in handlers? (something like add_configuration
        #  but with handler.update_in_vpp(...) call, the InterfaceConfigurationItem is simplified case
        #  of the generic code)
        return UpdateConfigurationItemsReply(
            processing_error="Unhandled/Not implemented use case."
        )

    def get_configuration(self, sync_with_vpp=False) -> GetConfigurationItemsReply:
        # do synchronization with VPP
        if sync_with_vpp:
            self.sync_interfaces_with_vpp()

        # return inner state of server (with possible updated VPP state from previous step)
        return GetConfigurationItemsReply(
            items=[
                record.get_configuration_item_detail()
                for record in self._configuration_item_records
            ]
        )

    def sync_interfaces_with_vpp(self):
        for record in self._configuration_item_records:
            if isinstance(record.configuration_item, InterfaceConfigurationItem):
                record.metadata[VPP_DUMP_KEY] = record.handler.dump_from_vpp(
                    record.configuration_item
                )


class ConfigurationItemRecord:
    """Server's inner state for one configuration item"""

    def __init__(
        self, configuration_item, handler, init_state=State.RECEIVED, metadata=dict()
    ):
        self.configuration_item = configuration_item
        self.handler = handler
        self.state = init_state
        self.metadata = metadata

    def get_configuration_item_reply(self, error="") -> ConfigurationItemReply:
        """Retrieves a ConfigurationItemReply view into/copy for given record"""
        return ConfigurationItemReply(
            config=self.configuration_item,
            state=self.state,
            metadata=self.metadata,
            error=error,
        )

    def get_configuration_item_detail(self) -> ConfigurationItemDetail:
        """Retrieves a ConfigurationItemDetail view into/copy for given record"""
        return ConfigurationItemDetail(
            config=self.configuration_item, state=self.state, metadata=self.metadata
        )


def papi_wrapper(vpp_client):
    """Creates Pyro5 wrapper class that has all api methods from old PAPI client exposed for clients of PAPI++ server"""

    class Wrapper(pyro.NamedWrapper):
        @staticmethod
        def name():
            return "papi"

    for attr_name in dir(vpp_client.inner_vpp_client.api):
        if (
            attr_name.find("__") == -1
        ):  # use only public VPP API attributes (callable API functions)
            setattr(
                Wrapper,
                attr_name,
                staticmethod(getattr(vpp_client.inner_vpp_client.api, attr_name)._func),
            )
    pyro.api_expose(Wrapper)
    return Wrapper


def extended_papi_wrapper(vpp_client):
    """Creates Pyro5 wrapper class that has all the new api methods exposed for clients of PAPI++ server"""

    @pyro.api_expose
    class Wrapper(pyro.NamedWrapper):
        def __init__(self):
            # Note: synchronization could be implemented also in vpp_client because it is only one instance, it
            #  can be used different lock for readonly access,etc. ... using one lock here for simplicity and
            #  not complicating vpp_client
            self.lock = threading.Lock()

        @staticmethod
        def name():
            return "extended.papi"

        def add_configuration(
            self, *configuration_items, context: str = ""
        ) -> AddConfigurationItemsReply:
            try:
                self.lock.acquire(blocking=True)
                return vpp_client.add_configuration(
                    *configuration_items, context=context
                )
            except Exception:
                logger.exception("Exception in add_configuration")
            finally:
                self.lock.release()

        def delete_configuration(
            self, *configuration_items
        ) -> DeleteConfigurationItemsReply:
            try:
                self.lock.acquire(blocking=True)
                return vpp_client.delete_configuration(*configuration_items)
            except Exception:
                logger.exception("Exception in delete_configuration")
            finally:
                self.lock.release()

        def update_configuration(
            self, old_configuration_item, new_configuration_item, context: str = ""
        ):
            try:
                self.lock.acquire(blocking=True)
                return vpp_client.update_configuration(
                    old_configuration_item, new_configuration_item, context
                )
            except Exception:
                logger.exception("Exception in update_configuration")
            finally:
                self.lock.release()

        def get_configuration(self, sync_with_vpp=False) -> GetConfigurationItemsReply:
            try:
                self.lock.acquire(blocking=True)
                return vpp_client.get_configuration(sync_with_vpp=sync_with_vpp)
            except Exception:
                logger.exception("Exception in get_configuration")
            finally:
                self.lock.release()

        def get_vpp_stats(self, stats_config) -> VPPStatsReply:
            try:
                self.lock.acquire(blocking=True)
                return vpp_client.get_vpp_stats(stats_config)
            except Exception:
                logger.exception("Exception in get_vpp_stats")
            finally:
                self.lock.release()

    return Wrapper


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="PAPI++ server")
    parser.add_argument(
        "--frr_agent_host",
        help="Host (IP address) of FRR agent. (Basically FRR docker container ip address). "
        "Default setting(empty string) disables connections to FRR",
        type=str,
        default="",
    )
    parser.add_argument(
        "--frr_agent_port",
        help="Port that FRR agent listen to. (Exposed port from FRR docker container for agent)",
        type=int,
        default=7777,
    )
    parser.add_argument(
        "--dhcp_socket",
        help="Path to DHCP server control unix socket. (Exposed unix socket from DHCP docker container)",
        type=str,
        default="/run/kea/control_socket_4",
    )
    # add version args
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(__version__),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    vpp_client = ExtendedVPPClient(
        "/usr/share/vpp/api/",
        "/run/vpp/api.sock",
        frr_agent_host=args.frr_agent_host,
        frr_agent_port=args.frr_agent_port,
        dhcp_socket=args.dhcp_socket,
    )  # PAPI++ instance
    pyro.run_server_loop(papi_wrapper(vpp_client), extended_papi_wrapper(vpp_client))


def cli():
    args = parse_args()
    vpp_client = ExtendedVPPClient(
        "/usr/share/vpp/api/",
        "/run/vpp/api.sock",
        frr_agent_host=args.frr_agent_host,
        frr_agent_port=args.frr_agent_port,
    )  # PAPI++ instance
    pyro.run_server_loop(papi_wrapper(vpp_client), extended_papi_wrapper(vpp_client))


if __name__ == "__main__":
    main()
