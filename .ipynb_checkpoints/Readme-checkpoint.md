
### CloudMotor实验平台

* 项目已上传github：https://github.com/skywalker1996/CloudMotor

#### 环境配置

1. mahimahi 安装 (ubuntu)

> sudo apt install mahimahi

2. python依赖安装

> pip install -r requirements 

3. 安装Redis

4. 下载仿真平台代码

> git clone git@github.com:skywalker1996/CloudMotor.git


#### 文件夹介绍

* configs：配置管理
* logs：保存实验数据记录数据
* model：机器学习模型
* results：分析结果目录
* tests：测试文件
* utils：工具代码

#### 核心代码文件

* model/motor.py : 电机模型类，电机参数都在这里调
* utils/networkSim.py : 网络仿真类，负责输出实时的时延和丢包
* motorClient.py : 电机客户端类，负责接收服务器下发的决策并控制电机
* motorServer.py : 电机服务器类，负责PID控制和决策下发
* run_experiment.py : 运行实验脚本，会启动motorClient和motorServer

#### 使用流程

1. 编辑configs/address_cloud.yaml
 
```
server:
  address:   
    local_ip: 127.0.0.1    //localhost ip，不用改
    ip: 100.64.0.4         //mahimahi默认ip，不用改
    port: 9990

client:
  address:
    local_ip: 127.0.0.1    //localhost ip，不用改
    ip: 172.30.38.194      //本机ip，需要改成自己的
    port: 9992

redis:
  address:           
    ip: xxx      // redis ip, 需要改成自己的
    port: 6379   // redis 默认端口号
```

2. 编辑configs/global.yaml
```
experiment:
  name: 每次实验需要取一个name，会自动创建name文件夹来存放实验数据           
  use_mahimahi: 是否使用mahimahi，填false
  batch_experiment: 是否进行批量实验，填true
  running_time: 单个epoch的运行时间，单位为秒

# 目前不使用mahimahi，不用管这里
mahimahi:
  trace: trace文件路径
  base_delay: mahimahi链路基础时延

batch_experiment_params:
  delay_mean: [0,100,5]   #[start, end, step_size]
  loss_mean: [5,50,5]     #[start, end, step_size]
  control_interval: [10,10,1]    #[start, end, step_size]
  epoch: 1   #单组参数运行的epoch次数

```

3. 运行实验
> python run_experiment.py

4. 分析实验数据
* 实验运行完后，实验数据会保存在logs/{experiment_name}文件夹下
* 运行results/analysis.py，需要修改里面的experiment_name，指定TIME_START和TIME_END    
> analysis.py输入输出分别为：    
input_dir = f"../logs/{EXPERIMENT_NAME}"    
output_file = f"./datasets/{EXPERIMENT_NAME}_{TIME_START}_{TIME_END}.csv"

* results中有绘图的代码（plot1、plot2等）








