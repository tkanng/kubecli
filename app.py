
from api import *

import yaml

import time

class Tclient(object):

    def submit(self, namespace, name, image, resource, replicas):
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
        print(resp)

    def delete(self, name, namespace):
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

        resp = delete_deployment(task_info)
        print(resp)

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
        print(resp)
        
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
        print(resp)

    def update_deployment(self, namespace, name, image, resource, replicas):
        """
          :param task_info: a dict representing the detail of a task, e.g.
               {
                   namespace: "default"
                   image: "redis",
                   replicas: 3
                   resource: {
                       cpu: 2000m,
                       gpu: 2000m,
                       mem: 2Gi
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
        print(resp)

    def list_node(self):
        resp = list_node()
        print(resp)
    def list_node_pod(self, node_name):
        resp = list_node_pod(node_name)
        print(resp)
        
    # def list_node_resources_usage(self):
    #     '''

    #     '''

    def list_node_allocatable_resources(self):
        resp = list_node_allocatable_resources()
        print(resp)

    def list_deployment_pod(self, namespace, deployment_name):
        return list_deployment_pod(namespace, deployment_name)

    def list_deployment_pod_name(self, namespace, deployment_name):
        res = list_deployment_pod(namespace, deployment_name)
        names = []
        for item in res.items:
            names.append(item.metadata.name)
        return names


if __name__ == '__main__':
    path = "/home/tusimple/my_k8s/yamls/gpu-test/initEnv/shared-gpu.yaml"
    tclient = Tclient()
    with open(path) as f:
        dep = yaml.load(f)
        namespace = "default"
        deploymentName = dep.get("metadata").get("name") 
        containers = dep.get("spec").get("template").get("spec").get("containers")
        replicas = dep.get("spec").get("replicas")
        # print("Deleting deployment")
        # tclient.delete(deploymentName, namespace)
        # print("*"*100)
        # tclient.submit(namespace,deploymentName,containers[0].get("image"),containers[0].get("resources"),replicas)
        # print("*"*100)
        # tclient.list_deployment_pod(namespace, deploymentName)
        print("*"*100)
        # res = tclient.list_deployment_pod_name(namespace, deploymentName)
        # print(res)
        # res = tclient.list_node_pod('tusimple')
        # print(res)

        tclient.list_node_allocatable_resources()
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
