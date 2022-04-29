#### 环境配置

1. mahimahi 安装 (ubuntu)

> sudo apt install mahimahi

2. python依赖安装

> pip install -r requirements 

3. Redis安装 

4. 下载仿真平台代码

> git clone git@github.com:skywalker1996/CloudMotor.git


#### 文件夹介绍

* analysis：数据分析和绘图工具
* configs：配置管理
* logs：实验数据log
* results：结果记录
* tests：测试文件
* utils：工具代码

#### 核心代码文件

* motor.py : 电机模型类，电机参数都在这里调
* motorClient.py : 电机客户端类，负责接收服务器下发的决策并控制电机
* motorServer.py : 电机服务器类，负责PID控制和决策下发
* run_experiment.py : 运行实验脚本，会启动motorClient和motorServer

#### 使用流程

1. 编辑configs/configs_cloud.yaml

```
server:
  address:   
    local_ip: 127.0.0.1    //localhost ip，不用改
    ip: 100.64.0.4         //mahimahi默认ip，不用改
    port: 9990

client:
  address:
    local_ip: 127.0.0.1    //localhost ip，不用改
    ip: 172.30.38.194      //本机对外ip，需要改成自己的
    port: 9992
```

2. 编辑configs/global.yaml
```
  use_trace: 是否使用mahimahi trace，1为使用，0为不使用
  trace: trace文件位置
  base_delay: 基础时延，仅当use_trace为1时有效
  control_interval: 控制周期，单位为秒
  running_time: 实验运行时间，单位为秒
```

3. 运行实验
> python run_experiment.py

4. 分析实验数据
* 实验运行完后，会输出平均控制精度
* 实验数据会保存在logs文件夹下对应时间的文件夹中
* 每次跑完实验，最新的数据都会放在logs/current_log中
* analysis中有绘图的代码（plot.py），默认使用logs/current_log中的数据

![](/Users/zhijian/Desktop/Lab/GTS/Workspace/motor/analysis/2_03_005.png)







