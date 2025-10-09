#!/bin/bash

# set -euo pipefail

HOST_VPP0_NET=10.0.0
VPP0_VPP1_NET1=20.0.0
VPP0_VPP1_NET2=30.0.0
WG_NET=40.0.0

WG_LISTEN_PORT=50000

WG_PRIV_KEY1=cF9+SnI47vJ5qWcFsio/neXgKtGwVHZVakiV2koUgUc=
WG_PRIV_KEY2=gBSN1Fr8hwZCGXV6JjHjHWK4xCwnHf47ECqJA6bPI2M=

WG_PUB_KEY1=hyefQkAIZb2g4y4YZrKs3JrcQEx+n+R27SLM5gUHOyM=
WG_PUB_KEY2=hhZ/msx0T0yrwJersInVuLL2kd/l4WQ4fxOXsC4+LWw=

VPP1_SOCK='-s /run/vpp/cli-vpp1.sock'
VPP0_SOCK=""

VPP0_HOST_IF=vpp0host
HOST_VPP0_IF=hostvpp0

VPP0_VPP1_IF1=vpp0vpp1-1
VPP1_VPP0_IF1=vpp1vpp0-1

VPP0_VPP1_IF2=vpp0vpp1-2
VPP1_VPP0_IF2=vpp1vpp0-2

TEST_NET1=7.7.7
TEST_NET2=8.8.8

DST_ADDR1=192.168.160.101
DST_NET_1="$DST_ADDR1"/32

VPP_VER=2302

usage() {
    echo "Usage: sudo $0 <-a | -c | -e | -h | [-v <vpp-ver>] -i | -m | -p |-r | -t | u | -v | -w>"
    echo
    echo "Available options:"
    echo
    echo "-a              Ping test from VPP0: ping subnets in the Host and in VPP1"
    echo
    echo "-c              Configure - single VRF in VPP0"
    echo
    echo "-e              Configure NAT as shown in:"
    echo
    echo "-h              Show this help message"
    echo
    echo "-i              Install VPP packages with given version; if no version specified, 2302 is installed"
    echo
    echo "-m              Configure - multiple VRFs in VPP0"
    echo
    echo "-n <config-opt> Configure NAT"
    echo "                 - Option 1:  as specified in the documentation:"
    echo "                   https://github.com/FDio/vpp/blob/master/src/plugins/nat/nat44-ed/nat44_ed_doc.rst#dynamic-nat-minimal-required-configuration"
    echo "                 - Option 2:  Working config:"
     echo "                - Option 3:  Dynamic NAT with identity mapping for WG tunnel, enabled forwarding"
   echo
    echo "-p   Prep up traces on both VPPs"
    echo
    echo "-r   Remove VPP packages"
    echo
    echo "-t   Show the test bed topology"
    echo
    echo "-u   Unconfigure"
    echo
    echo "-v   VPP Version (Default: 2302)"
    echo
    echo "-w   Configure wireguard tunnel on VPP0 <-> VPP1 link #1 "
    echo

}

show_topology() {
    HOST_IP="$(ip address show | grep "inet " | grep "global" | grep -wv $HOST_VPP0_IF | awk '{ print $2 }')"

    echo
    echo "Single VRF topology:"
    echo
    echo "    +--------+               +--------+ .1         .2 +--------+"
    echo "    |        | .2         .1 |        +---------------+        |"
    echo "    |        |               |        |  $VPP0_VPP1_NET1.0/24  |        |"
    echo "    |  Host  +---------------+  VPP0  |               |  VPP1  |"
    echo "    |        |  $HOST_VPP0_NET.0/24  |        | .1         .2 |        |"
    echo "    |        |               |        +---------------+        |"
    echo "    +----+---+               +--------+  $VPP0_VPP1_NET2.0/24  +----+---+"
    echo "         |                                                 |"
    echo "         |                                                 |"
    echo " $HOST_IP                                 $DST_NET_1"
    echo "                                                      $TEST_NET1.7/24"
    echo "                                                      $TEST_NET2.8/24"
    echo
    echo "Multi-VRF VRF topology:"
    echo
    echo "    +--------+               +--------------------------+               +--------+"
    echo "    |        |               | +--------+    +--------+ |               |        |"
    echo "    |        |               | |        |    |        | | .1         .2 |        |"
    echo "    |        |               | |        +----+  VRF1  +-----------------+        |"
    echo "    |        |               | |        |    |        | |  $VPP0_VPP1_NET1.0/24  |        |"
    echo "    |        | .2         .1 | |  VRF0  |    +--------+ |               |        |"
    echo "    |  Host  +-----------------+        |    +--------+ |               |  VPP1  |"
    echo "    |        |  $HOST_VPP0_NET.0/24  | |        |    |        | | .1         .2 |        |"
    echo "    |        |               | |        +----+  VRF2  +-----------------+        |"
    echo "    |        |               | |        |    |        | |  $VPP0_VPP1_NET2.0/24  |        |"
    echo "    |        |               | +--------+    +--------+ |               |        |"
    echo "    |        |               |           VPP0           |               |        |"
    echo "    +----+---+               +--------------------------+               +----+---+"
    echo "         |                                                                   |"
    echo "         |                                                                   |"
    echo " $HOST_IP                                                   $DST_NET_1"
    echo "                                                                        $TEST_NET1.7/24"
    echo "                                                                        $TEST_NET2.8/24"

}

get_local_ip_address_and_subnet() {
    # Get the local IP address
    IFS='\/' read -ra IP_AND_MASK <<<"$(ip address show | grep "inet " | grep "scope global" | awk '{ print $2 }')"
    MY_IPADDR="${IP_AND_MASK[0]}"

    IFS='.' read -ra OCTETS <<<"$MY_IPADDR"
    HOST_SUBNET=$(printf "%s.%s.%s.0\/%s" "${OCTETS[0]}" "${OCTETS[1]}" "${OCTETS[2]}" "${IP_AND_MASK[1]}")
}

install_vpp() {
    sudo apt update
    sudo apt install nmap
    sudo apt install git build-essential
    #curl -s https://packagecloud.io/install/repositories/fdio/"$VPP_VER"/script.deb.sh | sudo bash
    sudo apt-get update
    git clone https://gerrit.fd.io/r/vpp
    cd vpp
    git checkout stable/2206
    git apply ~/0001-nat44-ed-Determine-used-nat-pool-based-on-fib.patch
    make install-dep
    make pkg-deb
    cd build-root
    sudo apt install ./*.deb 
    sudo usermod -a -G vpp ubuntu
    newgrp vpp
    cd ~

}

create_vpp_interface() {
    case "$3" in
    "host")
        IF_NAME=$(sudo vppctl $5 create host-interface name "$1")
        ;;
    "loopback")
        IF_NAME=$(sudo vppctl $5 create loopback interface instance "$1")
        ;;
    *)
        echo >&2 "*** ERROR in create_vpp_interface(): Bad interface type '$3'."
        ;;
    esac

    sudo vppctl $5 set int state "$IF_NAME" up
    sudo vppctl $5 set int ip table "$IF_NAME" "$4"
    sudo vppctl $5 set int ip address "$IF_NAME" "$2"

    echo "$IF_NAME"
}


create_vpp_route() {
    sudo vppctl $5 ip route add "$1" table "$2" via "$3" "$4"
}
swap_routes() {
	echo "switching routes"
    TABLE_0=0
    sudo vppctl ip route del 7.7.7.0/24
    #sudo vppctl ip route del "$VPP0_VPP1_NET2".0/24

    #create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"
    create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "$VPP0_L2" "$VPP0_SOCK"
    #create_vpp_route "$TEST_NET2".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "$VPP0_L2" "$VPP0_SOCK"

	sleep 5
	sudo vppctl sh nat44 session
	
	echo "switching routes again"
    sudo vppctl ip route del 7.7.7.0/24
    sudo vppctl ip route del 8.8.8.0/24

    create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"
    create_vpp_route "$TEST_NET2".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"
	
	sleep 5
	sudo vppctl sh nat44 session
}

configure() {
    TABLE_0=0
    TABLE_1=0
    TABLE_2=0

    if [ "$1" == "m" ]; then
        echo "Adding FIB tables 1 and 2..."

        sudo vppctl ip table add 1
        sudo vppctl ip table add 2

        TABLE_1=1
        TABLE_2=2
    fi

    echo "Creating Host <-> VPP0 link..."
    sudo ip link add name "$VPP0_HOST_IF" type veth peer name "$HOST_VPP0_IF"
    sudo ip link set dev vpp0host up
    sudo ip link set dev hostvpp0 up
    sudo ip address add "$HOST_VPP0_NET".2/24 dev hostvpp0

    echo " . Creating '$VPP0_HOST_IF' in VPP0..."
    VPP0_HOST=$(create_vpp_interface "$VPP0_HOST_IF" "$HOST_VPP0_NET".1/24 "host" "$TABLE_0" "$VPP0_SOCK")

    echo "Adding routes to Host..."
    sudo ip route add "$TEST_NET1".0/24 via "$HOST_VPP0_NET".1 dev hostvpp0
    sudo ip route add "$TEST_NET2".0/24 via "$HOST_VPP0_NET".1 dev hostvpp0
    sudo ip route add "$VPP0_VPP1_NET1".0/24 via "$HOST_VPP0_NET".1 dev hostvpp0
    sudo ip route add "$VPP0_VPP1_NET2".0/24 via "$HOST_VPP0_NET".1 dev hostvpp0
    sudo ip route add "$DST_NET_1" via "$HOST_VPP0_NET".1 dev hostvpp0

    echo Starting VPP1...
    sudo /usr/bin/vpp -c startup1.conf
	sleep 5
	
    echo "Creating VPP0 <-> VPP1 link #1..."
    sudo ip link add name vpp0vpp1-1 type veth peer name vpp1vpp0-1
    sudo ip link set dev vpp0vpp1-1 up
    sudo ip link set dev vpp1vpp0-1 up
    echo " . Creating '$VPP0_VPP1_IF1' in VPP0..."
    VPP0_L1=$(create_vpp_interface "$VPP0_VPP1_IF1" "$VPP0_VPP1_NET1".1/24 "host" "$TABLE_1" "$VPP0_SOCK")
    echo " . Creating '$VPP1_VPP0_IF1' in VPP1..."
    VPP1_L1=$(create_vpp_interface "$VPP1_VPP0_IF1" "$VPP0_VPP1_NET1".2/24 "host" "$TABLE_0" "$VPP1_SOCK")

    echo "Creating VPP0 <-> VPP1 link #2..."
    sudo ip link add name vpp0vpp1-2 type veth peer name vpp1vpp0-2
    sudo ip link set dev vpp0vpp1-2 up
    sudo ip link set dev vpp1vpp0-2 up
    echo " . Creating '$VPP0_VPP1_IF2' in VPP0..."
    VPP0_L2=$(create_vpp_interface "$VPP0_VPP1_IF2" "$VPP0_VPP1_NET2".1/24 "host" "$TABLE_2" "$VPP0_SOCK")
    echo " . Creating '$VPP1_VPP0_IF2' in VPP1..."
    VPP1_L2=$(create_vpp_interface "$VPP1_VPP0_IF2" "$VPP0_VPP1_NET2".2/24 "host" "$TABLE_0" "$VPP1_SOCK")

    echo "Creating loopback interfaces in VPP1..."
    echo " . Creating '$TEST_NET1' in VPP1..."
    create_vpp_interface 1 "$TEST_NET1".7/24 "loopback" "$TABLE_0" "$VPP1_SOCK" >/dev/null
    echo " . Creating '$TEST_NET2' in VPP1..."
    create_vpp_interface 2 "$TEST_NET2".8/24 "loopback" "$TABLE_0" "$VPP1_SOCK" >/dev/null
    echo " . Creating '$DST_NET_1' in VPP1..."
    create_vpp_interface 3 "$DST_NET_1" "loopback" "$TABLE_0" "$VPP1_SOCK" >/dev/null

    echo "Adding routes to VPP0..."
    if [ "$1" == "m" ]; then
        create_vpp_route "$HOST_SUBNET" "$TABLE_0" "$HOST_VPP0_NET".2 "$VPP0_HOST" "$VPP0_SOCK"
        create_vpp_route "$HOST_SUBNET" "$TABLE_1" "$HOST_VPP0_NET".2 "next-hop-table $TABLE_0" "$VPP0_SOCK"

        create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "next-hop-table $TABLE_1" "$VPP0_SOCK"
        create_vpp_route "$TEST_NET1".0/24 "$TABLE_1" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"

        create_vpp_route "$TEST_NET2".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "next-hop-table $TABLE_2" "$VPP0_SOCK"
        create_vpp_route "$TEST_NET2".0/24 "$TABLE_2" "$VPP0_VPP1_NET2".2 "$VPP0_L2" "$VPP0_SOCK"

        create_vpp_route "$DST_NET_1" "$TABLE_0" "$VPP0_VPP1_NET1".2 "next-hop-table $TABLE_1" "$VPP0_SOCK"
        create_vpp_route "$DST_NET_1" "$TABLE_1" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"

        create_vpp_route "$VPP0_VPP1_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "next-hop-table $TABLE_1" "$VPP0_SOCK"
        create_vpp_route "$VPP0_VPP1_NET2".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "next-hop-table $TABLE_2" "$VPP0_SOCK"

        create_vpp_route "$HOST_VPP0_NET".0/24 "$TABLE_1" "$HOST_VPP0_NET".2 "next-hop-table $TABLE_0" "$VPP0_SOCK"
        create_vpp_route "$HOST_VPP0_NET".0/24 "$TABLE_2" "$HOST_VPP0_NET".2 "next-hop-table $TABLE_0" "$VPP0_SOCK"

    else
        create_vpp_route "$HOST_SUBNET" "$TABLE_0" "$HOST_VPP0_NET".2 "$VPP0_HOST" "$VPP0_SOCK"
        create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"
        #create_vpp_route "$TEST_NET1".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "$VPP0_L2" "$VPP0_SOCK"
        create_vpp_route "$TEST_NET2".0/24 "$TABLE_0" "$VPP0_VPP1_NET2".2 "$VPP0_L2" "$VPP0_SOCK"
        create_vpp_route "$DST_NET_1" "$TABLE_0" "$VPP0_VPP1_NET1".2 "$VPP0_L1" "$VPP0_SOCK"
    fi

    echo "Adding routes to VPP1..."
    echo "VPP1_L1: $VPP1_L1"
    create_vpp_route "$HOST_VPP0_NET".0/24 "$TABLE_0" "$VPP0_VPP1_NET1".1 "$VPP1_L1" "$VPP1_SOCK"
    create_vpp_route "$HOST_SUBNET" "$TABLE_0" "$VPP0_VPP1_NET1".1 "$VPP1_L1" "$VPP1_SOCK"
}

unconfigure() {
    echo "Restarting all VPPs..."
    ps -ef | grep vpp | awk '{print $2}' | xargs sudo kill

    echo "Deleting host routes..."
    sudo ip route delete "$TEST_NET1".0/24
    sudo ip route delete "$TEST_NET2".0/24
    sudo ip route delete "$VPP0_VPP1_NET1".0/24
    sudo ip route delete "$VPP0_VPP1_NET2".0/24
    sudo ip route delete "$DST_NET_1"

    echo "Deleting host interfaces..."
    sudo ip link del vpp0host
    sudo ip link del vpp0vpp1-1
    sudo ip link del vpp0vpp1-2

    # sudo service vpp restart
}

remove_vpp() {
    sudo apt-get remove --purge "vpp*"
    sudo rm /etc/apt/sources.list.d/fdio*.list
    sudo apt remove nmap --purge
}

prep_vpp_trace() {
    sudo vppctl $1 clear trace
    sudo vppctl $1 trace add af-packet-input 10
}

prep_vpp_traces() {
    echo "Prepping up traces on VPP0 and VPP1..."
    prep_vpp_trace "$VPP0_SOCK"
    prep_vpp_trace "$VPP1_SOCK"
}

configure_nat_opt_1() {
    echo "OPTION 1: Configuring twice-nat on two interfaces..."

    ETH0=$(sudo vppctl sh int | grep "$VPP0_HOST_IF" | awk '{ print $1 }')
    sudo vppctl set int nat44 in "$ETH0"
    ETH1=$(sudo vppctl sh int | grep "$VPP0_VPP1_IF1" | awk '{ print $1 }')
    sudo vppctl set int nat44 out "$ETH1"

    sudo vppctl nat44 add address 20.0.0.1
    sudo vppctl nat44 add address 192.168.160.101 twice-nat
    sudo vppctl nat44 add static mapping tcp local 10.0.0.2 5201 external 20.0.0.1 5201 twice-nat
}

configure_nat_opt_2() {
    echo "OPTION 2: Configuring twice-nat on two interfaces..."

    ETH0=$(sudo vppctl sh int | grep "$VPP0_HOST_IF" | awk '{ print $1 }')
    sudo vppctl set int nat44 out "$ETH0"
    ETH1=$(sudo vppctl sh int | grep "$VPP0_VPP1_IF1" | awk '{ print $1 }')
    sudo vppctl set int nat44 in "$ETH1"

    sudo vppctl nat44 add address 192.168.160.101
    sudo vppctl nat44 add address 20.0.0.1 twice-nat
    sudo vppctl nat44 add static mapping tcp local 20.0.0.2 5201 external 192.168.160.101 5201 twice-nat exact 20.0.0.1
}

configure_nat_opt_3() {
    ETH0=$(sudo vppctl sh int | grep "$VPP0_HOST_IF" | awk '{ print $1 }')
    sudo vppctl set int nat44 in "$ETH0"
    ETH1=$(sudo vppctl sh int | grep "$VPP0_VPP1_IF1" | awk '{ print $1 }')
    sudo vppctl set int nat44 out "$ETH1"
    
    ETH2=$(sudo vppctl sh int | grep "$VPP0_VPP1_IF2" | awk '{ print $1 }')
    sudo vppctl set int nat44 out "$ETH2"

    sudo vppctl nat44 add address 20.0.0.1
    sudo vppctl nat44 add address 30.0.0.1

    sudo vppctl nat44 add identity mapping external "$ETH1" udp "$WG_LISTEN_PORT"
    # sudo vppctl nat44 forwarding enable

    echo "OPTION 3: Configured dynamic NAT in: '$ETH0' <-> out: '$ETH1'..."


}

configure_nat() {
    # Clear all previous NAT44 configuration
    sudo vppctl nat44 disable
    # Enable NAT again
    sudo vppctl nat44 enable sessions 1000

    case "$1" in
    1)
        configure_nat_opt_1
        ;;
    2)
        configure_nat_opt_2
        ;;
    3)
        configure_nat_opt_3
        ;;
    *)
        echo >&2 "*** ERROR - Invalid configuration option"
        ;;
    esac

}

configure_wg_tunnel() {
    sudo vppctl $7 wireguard create listen-port "$WG_LISTEN_PORT" private-key "$3" src "$1"
    sudo vppctl $7 set int state wg0 up
    sudo vppctl $7 set int ip address wg0 "$5"/24
    sudo vppctl $7 wireguard peer add wg0 public-key "$4" endpoint "$2" allowed-ip 0.0.0.0/0 dst-port "$WG_LISTEN_PORT" persistent-keepalive 10
    
    sudo vppctl $7 ip route add "$6"/32 via "$6" wg0
}

configure_wireguard() {
    echo "Configuring Wireguard tunnel on VPP0 <-> VPP1 link #1"

    configure_wg_tunnel "$VPP0_VPP1_NET1".1 "$VPP0_VPP1_NET1".2 "$WG_PRIV_KEY1" "$WG_PUB_KEY2" "$WG_NET".1 "$WG_NET".2 "$VPP0_SOCK"
    configure_wg_tunnel "$VPP0_VPP1_NET1".2 "$VPP0_VPP1_NET2".1 "$WG_PRIV_KEY2" "$WG_PUB_KEY1" "$WG_NET".2 "$WG_NET".1 "$VPP1_SOCK"
# 
    echo "Reconfiguring routes to $TEST_NET2.0/24 on VPP0 and $HOST_VPP0_NET.0/24 on VPP1 to go over the WG tunnel"

    sudo vppctl "$VPP0_SOCK" ip route del "$TEST_NET2".0/24
    sudo vppctl "$VPP0_SOCK" ip route add "$TEST_NET2".0/24 via "$WG_NET".2 wg0
    sudo vppctl $VPP1_SOCK ip route del "$HOST_VPP0_NET".0/24
    sudo vppctl $VPP1_SOCK ip route add "$HOST_VPP0_NET".0/24 via "$WG_NET".1 wg0

}

ping_test() {
    echo "Pinging host HOST-VPP interface from VPP0:"
    sudo vppctl ping 10.0.0.2 repeat 2
    echo

    echo "Pinging VPP1-VPP0 interface #1 from VPP0:"
    sudo vppctl ping 20.0.0.2 repeat 2
    echo

    echo "Pinging VPP1-VPP0 interface #2 from VPP0:"
    sudo vppctl ping 30.0.0.2 repeat 2
    echo

    echo "Pinging VPP1 loopback interface #1 from VPP0:"
    sudo vppctl ping 7.7.7.7 repeat 2
    echo

    echo "Pinging VPP1 loopback interface #1 from VPP0:"
    sudo vppctl ping 8.8.8.8 repeat 2
    echo

    echo "Pinging host Ethernet interface from VPP0:"
    sudo vppctl ping "$MY_IPADDR" repeat 2
    echo

    echo "Pinging host Ethernet interface from VPP1:"
    sudo vppctl $VPP1_SOCK ping "$MY_IPADDR" repeat 2
    echo

    echo "Pinging destination on VPP1 from Host:"
    ping "$DST_ADDR1" -c 2 -W 2
    echo
    ping "$DST_ADDR1" -c 2 -I "$MY_IPADDR" -W 2
    echo
    echo "Pinging 8.8.8.8 from Host:"
    ping 8.8.8.8 -c 2 -W 2
    echo
    echo "Pinging 7.7.7. from Host:"
    ping 7.7.7.7 -c 2 -W 2
    echo
}

get_local_ip_address_and_subnet

while getopts "aehcimn:prstuv:w" opt; do
    case "$opt" in
    a)
        ping_test
        ;;
    h)
        usage
        exit 0
        ;;
    c)
        configure "s"
        ;;
    i)
        install_vpp
        ;;
    m)
        configure "m"
        ;;
    n)
        configure_nat "$OPTARG"
        ;;
    p)
        prep_vpp_traces
        ;;
    r)
        remove_vpp
        ;;
    u)
        unconfigure
        ;;
    v)
        VPP_VER=$OPTARG
        ;;
    t)
        show_topology
        ;;
    s)
        swap_routes
	;;	
    w)
        configure_wireguard
        ;;
    *)
        # getopts will have already displayed a "illegal option" error.
        echo
        usage
        exit 1
        ;;
    esac
done

if [ $# -eq 0 ]; then
    echo
    echo "An option must be specified"
    echo
    usage
fi
