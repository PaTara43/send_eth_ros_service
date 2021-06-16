# send_eth_ros_service
Infura credentials in config file

```bash
pip3 install -r reqirements.txt
#copy to catkin_ws/src, make executable, build (python3!!)
rosrun send_eth send_eth_server.py
```

In a separate terminal
```bash
rosservice call /send_eth 
"source_address: ''
target_address: ''
sum: 0.0
private_key: ''"
```
