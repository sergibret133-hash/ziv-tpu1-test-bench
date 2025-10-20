"""
Listen for notifications at IPv4 & IPv6 interfaces
++++++++++++++++++++++++++++++++++++++++++++++++++

Receive SNMP TRAP messages with the following options:

* SNMPv1/SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:162
* over IPv6/UDP, listening at [::1]:162
* print received data on stdout

Either of the following Net-SNMP commands will send notifications to this
receiver:

| $ snmptrap -v1 -c public 127.0.0.1 1.3.6.1.4.1.20408.4.1.1.2 127.0.0.1 1 1 123 1.3.6.1.2.1.1.1.0 s test
| $ snmptrap -v2c -c public ::1 123 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.5.0 s test

Notification Receiver below uses two different transports for communication
with Notification Originators - UDP over IPv4 and UDP over IPv6.

"""  #
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from pysnmp.smi import builder, view, compiler, rfc1902
from datetime import datetime, timezone

# noinspection PyUnusedLocal
def __callback(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.PROTOCOL_MODULES:
            pMod = api.PROTOCOL_MODULES[msgVer]

        else:
            print("Unsupported SNMP version %s" % msgVer)
            return

        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )

        print(
            "Notification message from {}:{}: ".format(
                transportDomain, transportAddress
            )
        )

        reqPDU = pMod.apiMessage.get_pdu(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if msgVer == api.SNMP_VERSION_1:
                print(
                    "Enterprise: %s"
                    % (pMod.apiTrapPDU.get_enterprise(reqPDU).prettyPrint())
                )
                print(
                    "Agent Address: %s"
                    % (pMod.apiTrapPDU.get_agent_address(reqPDU).prettyPrint())
                )
                print(
                    "Generic Trap: %s"
                    % (pMod.apiTrapPDU.get_generic_trap(reqPDU).prettyPrint())
                )
                print(
                    "Specific Trap: %s"
                    % (pMod.apiTrapPDU.get_specific_trap(reqPDU).prettyPrint())
                )
                print(
                    "Uptime: %s" % (pMod.apiTrapPDU.get_timestamp(reqPDU).prettyPrint())
                )
                varBinds = pMod.apiTrapPDU.get_varbinds(reqPDU)

            else:
                varBinds = pMod.apiPDU.get_varbinds(reqPDU)

            print("Var-binds:")

            varBinds = [
                rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolve_with_mib(mibViewController)
                for x in varBinds
            ]


            for oid, val in varBinds:
                if("tpu1cNotifyTimeSecsUtc" in oid.prettyPrint()):
                    val= datetime.fromtimestamp(int(val), tz=timezone.utc)
                    print(f"{oid.prettyPrint()} = {val}")
                elif("1.3.6.1.4.1.6346.1.8" in val.prettyPrint()):
                    print(val.prettyPrint())
                    print(f"{oid.prettyPrint()} = Notification Type {mibViewController.get_node_location(val)[1]}")
                else:
                    print(f"{oid.prettyPrint()} = {val.prettyPrint()}")

    return wholeMsg
    

mibBuilder = builder.MibBuilder()
mibViewController = view.MibViewController(mibBuilder)
compiler.add_mib_compiler(
    mibBuilder,
    sources=["file:///C:/Users/sergio.bret/Documents/SNMP/compiled_mibs"],
)

# Pre-load MIB modules we expect to work with
mibBuilder.load_modules("DIMAT-BASE-MIB", "DIMAT-TPU1C-MIB")

transportDispatcher = AsyncioDispatcher()

transportDispatcher.register_recv_callback(__callback)

# UDP/IPv4
transportDispatcher.register_transport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().open_server_mode(("10.212.42.4", 162))
)

transportDispatcher.job_started(1)
try:
    print("This program needs to run as root/administrator to monitor port 162.")
    print("Started. Press Ctrl-C to stop")
    # Dispatcher will never finish as job#1 never reaches zero

    import threading
    import time

    threading.Thread(
        target=transportDispatcher.run_dispatcher, daemon=True
    ).start()
    
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Shutting down...")

finally:
    transportDispatcher.close_dispatcher()
    