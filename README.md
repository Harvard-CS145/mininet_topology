# Project 0: Get started with Mininet and Topology Configurations

## Objectives

* Get familiar with the experiment environment: Mininiet, Topology configurations, controller, etc.
* Create your own circle topology
* Run example applications on the simple topology and learn how to read their performance numbers
* This project will not be graded but it will serve as the basis for future projects.

## Tutorial: The line topology example

To start this tutorial, you will first need to get the [infrastructure setup](https://github.com/minlanyu/cs145-site/blob/spring2023/infra.md) and learn the [Github setup](https://cs61.seas.harvard.edu/site/2021/SetupGitHub/). 

and clone this repository with submodules
```
git clone --recurse-submodules <this repository>
```

### Networking terms

We start by defining a few networking terms used in this project. Note that the description here is not precise but just a way for you to understand the problem. You will learn the actual meanings of the terms after a few lectures in the class. For now, you can imagine a *topology* just as a graph, where *switches* and *hosts* are nodes in the graph, and they are connected by *links*. *Hosts* are those nodes at the edge of the graph. They can generate traffic and run applications. *Switches* are internal nodes in the graph that connect *hosts* or *switches* together. *Port* indicates the end of each link at a *node*.  

The job of networking is to deliver messages along a path of multiple nodes to finally reach the destination. This is a distributed process. That is, every node in the graph independently decide where to *forward* messages and together they deliver the message to the destination. To achieve this, each node will decide locally which *port* (i.e., link) to send the message based on its destination. This is called a *forwarding rule*. Your job would be program the forwarding rules. 

### Step 1: Create the line topology in Mininet

Let's first create the physical topology of the network in [Mininet](http://mininet.org/). The Mininet program automatically creates a virtual topology based on a *JSON configuration file*.
The JSON configuration file should:
- Define hosts and switches.
- Define the links, i.e., how hosts and switches connect with each other to form your topology.

As an example, we provide you with a line topology in the file `topology/p4app_line.json`. 
The line topology has three hosts ("h1", "h2" and "h3") and three switches ("s1", "s2", and "s3"). There are five links: one connecting "h1" and "s1", "h2" and "s2", "h3" and "s3", "s1" and "s2", "s2" and "s3".

<img src="./figures/line_topo.png" width="500">

In this configuration file `topology/p4app_line.json`, `topology` includes `assignment_strategy`, `links`, `hosts`, and `switches`. The `assignment_strategy` indicates all the switches run at layer 2 (`l2`). We put the three hosts in the `hosts` subfield, and put the three switches in the `switches` subfield. We also put the five links in the `links` subfield.

**Run Mininet with the topology**
```
sudo p4run --config topology/p4app_line.json
```
You will see the `mininet>` prompt if the command ran successfully.
You can choose different `json` files for differnet topologies.

**Verify your topology**
In the Mininet CLI, you can check out the nodes and links you create by running the following commands:

- `nodes`: list all the hosts and switches you just created.
- `net`: list all the links you just created. For example,

    ```
    h1 h1-eth0:t1-eth1
    # h1-eth0 means port 0 of host h1. t1-eth1 means port 1 of switch t1. The two ports are connected.
    a1 lo:  a1-eth1:t1-eth3 a1-eth2:t2-eth3 a1-eth3:c1-eth1 a1-eth4:c2-eth1
    # e.g., a1-eth1 means port1 of switch a1, which is connected to t1-eth3, i.e., the port3 of switch t1
    ```

- `links`: list all the links you just created.
- `help`: list all the supported commands.
- `exit`: quit the Mininet CLI.

For more information on how to use Mininet and other useful commands you can check out the [walkthough](http://mininet.org/walkthrough/) and [Mininet documentation](https://github.com/mininet/mininet/wiki/Documentation).


### Step 2: Create networking software to run on the topology

There are two pieces of software that can control traffic in the topology. The first is a *controller program*, which is responsible of running routing algorithms, generating forwarding rules, and installing the rules into the tables at switches. The second is a *p4 program* that specifies packet processing logics at switches.  
For the line topology, we provide the controller program at `controller/controller_line.py` and the p4 program at `p4src/l2fwd.p4`. We do not need to touch the p4 program in this project. Basically, the p4 program defines a **dmac** table which maps the destination MAC address to the output port. 

Now let's delve more into the controller code. The controller implements the `route` function which installs entries in Table *dmac* to forward traffic. The table includes a group of *forwarding rules* that tell a node which *port* to send the traffic based on the destination (*MAC address*).
Our controller file already implemented some small functions that use the `Topology` and `SimpleSwitchAPI` objects from the `p4utils library` (this library locates in `/home/p4/p4-tools/p4-utils/README.md`, and you can also check the library in this [online site](https://github.com/minlanyu/cs145-site/blob/master/p4-utils/README.md)). 
At a high level, the `route` function uses `table_add` function to insert forwarding rules. 
```
def table_add(self, table_name, action_name, match_keys, action_params=[], prio=None):
        "Add entry to a match table: table_add <table name> <action name> <match fields> => <action parameters> [priority]"
```
(You can find other functions and their definitions at [here](https://github.com/minlanyu/cs145-site/blob/master/p4-utils/p4utils/utils/runtime_API.py#L920), you can also check `/home/p4/p4-tools/p4-utils/p4utils/utils/runtime_API.py#L920` locally if you are curious).

For example, 
```
controller.table_add("dmac", "forward", ["00:00:0a:00:00:01"], ["1"])
```
This line adds a rule in the `dmac` table, with the `forward` action. The rule says that if you receive a packet whose destination MAC address `dmac` is `"00:00:0a:00:00:01"`, `forward` the packet to port `"1"`.

In Mininet, by default hosts get assigned MAC addresses using the following pattern: `00:00:<IP address to hex>`. For example if h1 IP's address were `10.0.1.5` the MAC address would be: `00:00:0a:00:01:05`. The default IP address of host hX is `10.0.0.X`.

To find out the port mappings for each switch, you can check the messages printed by when running the `p4run` command in Step 1:
	
```
Switch port mapping:
s1:  1:h1	2:h2
```

You can also find out the port mappings using the `links` or  `net` CLI commands in the mininet terminal:

```
mininet> links
h1-eth0<->s1-eth1 (OK OK) 
h2-eth0<->s2-eth1 (OK OK) 
h3-eth0<->s3-eth1 (OK OK) 
s1-eth2<->s2-eth2 (OK OK) 
s2-eth3<->s3-eth2 (OK OK) 
```

**Run the controller**

You should start by setting up the topology by running the above *p4run* command. Then start *another* terminal, and run
```
./controller/controller_line.py
```

**Verify your controller**
If your controller installs routing rules successfully, hosts should be able to communicate with each other. 
To test the connectivity between all pairs of hosts, you can run the following commands in Mininet CLI 
- `pingall`: ping between any host pair
If `pingall` fails, you will see prompt stopped. (ctrl + c will kill the `pingall` command).

For debugging, you can also run:
- `h1 ping h2`: ping h2 from h1, to test the connectivity between two hosts
- `h1 <commands>`: run a command on host h1.

## Your Task: Build the Circle Topology

In this project, your task is to build the circle topology in `topology/p4app_circle.json` as shown in the following figure.
<img src="./figures/circle_topo.png" width="500">

You **only** need to write your own code in places marked with a ``TODO`` (ie, the `topology` field). 

Next, you need to write forwarding rules for the circle topology in `controller/controller_circle.json`. You **only** need to write your own code in places marked with a ``TODO`` (i.e., within the `route` function). 

### Testing
You can test your solution in the following steps:
1. Start the topology
	```
	sudo p4run --config topology/p4app_circle.json
	```
2. Run the controller
	```
	./controller/controller_circle.py
	```
3. We provide you with a testing script in `test_scripts/test_circle_topo.py`. Run it and your network should pass all tests.
	```
	./test_scripts/test_circle_topo.py
	```

## Running Applications on your network

These applications will also be used in future projects.

Although you are running a network in your laptop, you can run networked applications on the hosts as if you are running a real network. Here we introduce three applications that are representative for data center traffic: video streaming, Memcached and Iperf. The goal here is for you to get familiar with these applications so that we can use them to evaluate our network design in futurre projects.

Video streaming runs a server with video files. Any client can connect to the video server to get the video streams.

Memcached is an in-memory key-value store system, which distributes key-value pairs across different servers. Memcached mainly has two operations: `set` and `get`. Usually the key-value pair is a very short message, and thus for each operation, the system only generates a short TCP message, which makes the TCP flow short (less than 200 Byte). For more information, please refer to [Memcached website](http://memcached.org/). 

Iperf is a measurement tool for measuring IP network bandwidth. We usually run Iperf in two servers, and let those two servers to send packets as fast as possible, so that Iperf could measure the maximum bandwidth between the two servers. For more information, please refer to [Iperf website](https://iperf.fr/).

These applications are representative networked applications. Memcached represents those applications that have lots of small messages; while video streaming and iperf send long persistent flows.

### Video streaming
> _Note: To avoid GUI/X11 Forwarding issues, please run the video streaming client directly in the VM._

**Start a video streaming server at host `h1`**
```
./apps/start_vid_server.sh h1 10.0.0.1 
```
This command starts a video streaming server at host `h1`, and the IP address of `h1` is `10.0.0.1`. 

**Open the terminal for host `h2` in the mininet terminal**

Note that for video streaming, you need to run mininet in graphical interface. 
```
mininet> xterm h2
```
You will see another terminal (xterm) popped up, which belongs to host `h2`.

**Start the client for `h2` at xterm**

In the terminal popped up, type:
```
./apps/start_vid_client.sh h2 10.0.0.1
```
This command opens a Chrome web browser on host `h2` which visits a video website served on `10.0.0.1`. If you ran your server on a host other than `h1`, then change `10.0.0.1` to that IP.
Try playing the video. You should see something like this:

<img src="./figures/video.png" width="600">

**Measure video streaming performance**

You can measure how the performance of the video stream changes as you increase and decrease the link bandwidth.
You can set the link bandwidth in the topology configuration file before starting a new mininet network as follows
```
"topology": {
    "assignment_strategy": "l2",
    "links": [["h1", "s1", {"bw": 1}], ["h2", "s2", {"bw": 1}], ["h3", "s3", {"bw": 1}], ["s1", "s2", {"bw": 1}], ["s2", "s3", {"bw": 1}]],
    ...
}
```
The `bw` field defines the link bandwidth, whose unit is Mbps.

Question: IlliniFlix reports the bandwidth usage for its video streaming. How do the buffer level and the bandwidth change over 100 Kbps, 1 Mbps, 2 Mbps, and 4 Mbps link bandwidth settings? Do you notice any differences in the video quality?

### Memcached

**Generate request trace**

We provide a trace generator which generate requests for Memcached and Iperf, which is located in `apps/trace/` directory. You can check `apps/trace/README.md` for detailed instructions.

For example, if you want to run Memcached on host 'h1', 'h2', and 'h3', run Iperf on host `h1` and `h3`, and generate a trace for 60 seconds, you can first edit apps/trace/project0.json:

```
{
    "flow_groups": [
        {
            "start_time": 0,
            "length": 60000000,
            "src_host_list": ["h1", "h3"],
            "dst_host_list": ["h1", "h3"],
            "flow_size_distribution": {
                "type": "constant",
                "value": 10000000
            },
            "flow_gap_distribution": {
                "type": "constant",
                "value": 2000000
            },
            "flowlet_size_distribution": {
                "type": "constant",
                "value": 0
            },
            "flowlet_gap_distribution": {
                "type": "constant",
                "value": 0
            }
        }
    ],
    "mc_host_list": ["h1", "h2", "h3"],
    "mc_gap_distribution": {
        "type": "constant",
        "value": 1000000
    },
    "length": 60000000,
    "output": "./apps/trace/project0.trace"
}
```

And then type:

```
./apps/trace/generate_trace.py apps/trace/project0.trace
```

After generating the trace, you will find a file named `project0.trace` in `apps/trace` directory. 

**Run Memcached and Iperf**

We provide an easy script to run Memcached and Iperf servers and clients on hosts:
```
./apps/send_traffic.py --trace ./apps/trace/project0.trace
```
The script will send traffic for 60 seconds. After finishing running, you will get the measurement results, including the latency of memcached requests and the throughput of iperf requests.
```
########### Traffic Sender ############
Trace file: ./apps/trace/project0.trace
Host list: dict_keys(['h1', 'h2', 'h3'])
Traffic duration: 78.0 seconds
Log directory: logs
start iperf and memcached servers
Wait 5 sec for iperf and memcached servers to start
Start iperf and memcached clients
Run iperf client on host h1
Run iperf client on host h2
Run iperf client on host h3
Wait for experiment to finish
Stop everything
Average latency of Memcached Requests: 66828.3 us
Average throughput of Iperf Traffic: 392.4096666666666 kbps
```

**Check logs**
The result files in `logs` directory has more details on the memcached latency and iperf throughput. In this directory, you can find files like `hX_iperf.log` or `hX_mc.log`.
In files `hX_iperf.log`, each line represents the average throughput of one iperf request, which is issued by host `hX`.
In files `hX_mc.log`, each line represents the request latency of one memcached request, which is issued by host `hX`.

Question: You can compare the latency of the memcached traffic that shares the link with iperf with the latency for those memcached traffic that doesn't share the link. Why do you see the differences?

*Note*: if you are using Windows laptop, please be aware about that Windows and Linux handle newlines differently. Windows uses `\r\n` at the end of a line, while Linux uses `\n`. Therefore, please do not edit those files in your Windows host. If you want to use some text editor to edit the files in the VM through SSH or SFTP, be sure to set the correct newline symbol.

## Debugging and Troubleshooting

We maintain a list of debugging and troubleshooting tips [here](debug.md).
**These debugging tips will be useful for all future projects. Please come back and revisit this in future projects**

## Submission and Grading
Project 0 won't be graded. 

### Survey

Please fill up the survey when you finish your project.

[Survey link](https://docs.google.com/forms/d/e/1FAIpQLSf5l5XFowublpGOJB6uja5j_5uYW05YfAocjEOOw45ZWqoDrg/viewform?usp=pp_url)
