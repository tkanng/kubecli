
from api import *

import yaml

import time

class Tclient(object):

    def __init__(self, submit_retry_time=4):
        self.submit_retry_time = submit_retry_time

    def submit(self, namespace, name, image, resource, replicas, blocking=False):
        """
          :param task_info: a dict representing the detail of a task, e.g.
               {
                   namespace: "default",
                   name:"redis",
                   image: "redis:1.0",
                   replicas: 3
                   resource:
                   {
                       'limits': 
                       {
                           'nvidia.com/shared-gpu': 3, 
                           'nvidia.com/gpu-memory': '0M',
                           'cpu':1,
                       }   
                    }
               }
        """
        task_info = {}
        task_info['namespace'] = namespace
        task_info['name'] = name   # Deployment name equals contianer name
        task_info['image'] = image
        task_info['resource'] = resource
        task_info['replicas'] = replicas
        resp = create_deployment(task_info)
        if blocking==False:
            return resp, None
        else:
            pod_names = self.list_deployment_pod_name(namespace, name)
            while len(pod_names)!=replicas:
                time.sleep(2)
                pod_names = self.list_deployment_pod_name(namespace, name)
            running_count = 0
            for _ in range(self.submit_retry_time):
                time.sleep(4)
                running_count = 0
                for pod_name in pod_names:
                    phase = get_pod_info(pod_name,namespace).status.phase
                    if phase =="Running":
                        running_count += 1
                if running_count ==len(pod_names):
                    break
            if running_count ==len(pod_names):
                print("Start deployment " + name + " successfully! ")
                return resp, True
            else:
                print("Failed to start deployment " + name + " ." + str(running_count) + " pods are running.")
                return resp, False

    def delete(self, name, namespace, blocking=False):
        """
            :param name: deploy_name
            {
                namespace: "default"
                name: "redis"
            }
            :return:
        """
        task_info = {}
        task_info['name'] = name
        task_info['namespace'] = namespace
        print("Deleteing deployment " + name)
        resp = delete_deployment(task_info)
        if blocking==False:
            return resp
        else:
            while self.get_deployment(name, namespace)!=None:
                time.sleep(3)
            print("Delete deployment " + name  + " successfully!")
            return resp

    def get_deployments(self, namespace=None):
        """
            :param namespace: get_namespaced_deployments_info
            {
                namespace: "default"
            }
            :return:
        """
        task_info = {}
        task_info['namespace'] = namespace

        resp = get_deployments_info(task_info)
        return resp
        
    def get_deployment(self, name, namespace):
        """
            :param name namespace: get one deployment
            :return:
            {
                name: "redis"
                namespace: "default"
            }
        """
        task_info = {}
        task_info['name'] = name
        task_info['namespace'] = namespace
        resp = get_deployment_info(task_info)
        return resp


    def update_deployment(self, namespace, name, image, resource, replicas):
        """
          :param task_info: a dict representing the detail of a task, e.g.
               {
                   namespace: "default"
                   image: "redis",
                   replicas: 3,
                   resource:
                   {
                       'limits': 
                       {
                           'nvidia.com/shared-gpu': 3, 
                           'nvidia.com/gpu-memory': '0M',
                           'cpu':1,
                       }   
                    },
               }
        """
        task_info = {}
        task_info['namespace'] = namespace
        task_info['name'] = name
        task_info['image'] = image
        task_info['resource'] = resource
        task_info['replicas'] = replicas

        resp = replace_deployment(task_info)
        return resp

    def list_node(self):
        resp = list_node()
        return resp

    def list_node_pod(self, node_name):
        resp = list_node_pod(node_name)
        return resp

    def list_node_allocatable_resources(self):
        print("*"*50 + " node allocatable resources: " + "*"*50)
        resp = list_node_allocatable_resources()
        print(resp)
    
    def list_node_allocated_resources(self):
        resp = list_node_allocated_resources()
        print("*"*50 + " node allocated resources: " + "*"*50)
        print(resp)
    def list_deployment_pod(self, namespace, deployment_name):
        return list_deployment_pod(namespace, deployment_name)

    def list_deployment_pod_name(self, namespace, deployment_name):
        res = list_deployment_pod(namespace, deployment_name)
        names = []
        for item in res.items:
            names.append(item.metadata.name)
            return names
        return names


def test(counts, memorys,shared,replicas=1):
    test_gpu_name = shared_gpu_name if shared else exclusive_gpu_name
    for i in range(len(counts)):
        resource = {
            "limits":{
                 test_gpu_name: str(counts[i]), 
                 gpu_memory_name: '{}M'.format(memorys[i]),
            }
        }
        name = "{mode}-c-{count}-m-{memory}".format(mode="shared" if shared else "exclusive", count=counts[i], memory=memorys[i])
        _, result = tclient.submit(namespace,name,image,resource,replicas,blocking=True)
        if result==False:
            # Failed to start the deployment, delete the deployment
            tclient.delete(name, namespace, blocking=True) 
            continue
        podNames = tclient.list_deployment_pod_name(namespace,name)
        print("PodNames: " + str(podNames))
        phase = get_pod_info(podNames[0],namespace).status.phase
        print("Pods phase: " + phase)
        time.sleep(10)
        tclient.list_node_allocatable_resources()
        tclient.list_node_allocated_resources()      
        tclient.delete(name, namespace,blocking=True)


if __name__ == '__main__':
    tclient = Tclient()
    namespace = "default"
    image = "tensorflow/tensorflow:latest-gpu"
    replicas = 1
    print("initializing test environment")
    shared_name = "shared-gpu"
    tclient.get_deployment(shared_name, namespace)
    
    # resource = {
    #     "limits":{
    #          shared_gpu_name: 3, 
    #          gpu_memory_name: '0M',
    #     }
    # }
    # tclient.submit(namespace,shared_name,image,resource,1, blocking=True)
    # exclusive_name = "exclusive-gpu"
    # resource = {
    #     "limits":{
    #          exclusive_gpu_name: 3, 
    #          gpu_memory_name: '0M',
    #     }
    # }
    # tclient.submit(namespace,exclusive_name,image,resource,1,blocking=True)

    # try:
    #     print("*"*50+"shared count" +"*"*50)
    #     print("*"*100)
    #     counts = [1,5,6]
    #     test(counts, [0]*len(counts), True)
        
    #     print("*"*50+"exclusive count"  +"*"*50)
    #     print("*"*100)
    #     counts = [2,4,1]
    #     test(counts, [0]*len(counts), False)
        
    #     print("*"*50+"shared memory" +"*"*50)
    #     print("*"*100)
    #     counts = [2,2,3,5,5]
    #     memorys = [22,30,33,55,60]
    #     test(counts, memorys, True)
        
    #     print("*"*50+"exclusive memory" +"*"*50)
    #     print("*"*100)
    #     counts = [1,1]
    #     memorys = [11,12]
    #     test(counts, memorys, False)
    # finally:
    #     tclient.delete(shared_name, namespace)
    #     tclient.delete(exclusive_name, namespace)

    # while True:
    #     time.sleep(2)
    #     tclient.list_node_allocatable_resources()
    #     tclient.list_node_allocated_resources()
    # print("Deleting deployment")
    # tclient.delete(deploymentName, namespace)
    # print("*"*100)
    # tclient.submit(namespace,deploymentName,containers[0].get("image"),containers[0].get("resources"),replicas)
    # print("*"*100)
    # tclient.list_deployment_pod(namespace, deploymentName)
    # res = tclient.list_deployment_pod_name(namespace, deploymentName)
    # print(res)
    # res = tclient.list_node_pod('tusimple')
    # print(res)
    # tclient.list_node_allocatable_resources()
    # print("*"*100)
    # tclient.list_node_allocatable_resources()
    # print("*"*100)
    # tclient.list_node_allocated_resources()
    # print("Sleep 30s")
    # time.sleep(30)
    # print("Updating deployment")
    # tclient.update_deployment(namespace, deploymentName, containers[0].get("image"),{},replicas)
    # print("Sleep 30s")
    # time.sleep(30)
    # print("Deleting deployment")
    # tclient.delete(deploymentName, namespace)
    # tclient.list_node()
    # tclient.list_node_metadata_and_status()