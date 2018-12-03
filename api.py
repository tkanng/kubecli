from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

config.load_kube_config()
extensions_v1beta1 = client.ExtensionsV1beta1Api()
core_v1 = client.CoreV1Api()


gpu_name = "nvidia.com/gpu"
gpu_memory_name = "nvidia.com/gpu-memory"

shared_gpu_name = "nvidia.com/shared-gpu"
exclusive_gpu_name = "nvidia.com/exclusive-gpu"
gpu_free_memory_name = "nvidia.com/gpu-free-memory"
shared_gpu_memory_name = "nvidia.com/shared-gpu-memory"
shared_gpu_free_memory_name = "nvidia.com/shared-gpu-free-memory"

memory_name = "memory"
cpu_name = "cpu"


# extensionsV1beta1Api
def create_deployment(task_info):
    name = task_info.get('name')
    image = task_info.get('image')
    replicas = task_info.get('replicas')
    namespace = task_info.get('namespace')
    resource = task_info.get("resource")
    # Configureate Pod template container
    container = client.V1Container(
        name = name,
        image = image,
        ports = [client.V1ContainerPort(container_port = 80)],
        resources=resource)

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": task_info.get('name')}),
        spec=client.V1PodSpec(containers=[container]))

    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas = replicas,
        template = template)

    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name = name),
        spec=spec)

    try:
        api_response = extensions_v1beta1.create_namespaced_deployment(namespace = namespace, body=deployment)
        return api_response

    except ApiException as e:
        print(e)

def delete_deployment(task_info):
    name = task_info.get('name')
    namespace = task_info.get('namespace')
    # Delete deployment
    try:
        api_response = extensions_v1beta1.delete_namespaced_deployment(
            name = name,
            namespace = namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        return api_response
    except ApiException as e:
        print(e)

def get_deployments_info(task_info):
    namespace = task_info.get('namespace')
    try:
        if namespace == None:
            api_response = extensions_v1beta1.list_deployment_for_all_namespaces()
            return  api_response
        else:
            api_response = extensions_v1beta1.list_namespaced_deployment(namespace = namespace)
            return api_response
    except ApiException as e:
        print(e)

def get_deployment_info(task_info):
    name = task_info.get('name')
    namespace = task_info.get('namespace')

    try:
        api_response = extensions_v1beta1.read_namespaced_deployment(name = name, namespace = namespace)
        return api_response
    except ApiException as e:
        print(e)

def replace_deployment(task_info):
    name = task_info.get('name')
    image = task_info.get('image')
    replicas = task_info.get('replicas')
    namespace = task_info.get('namespace')

    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image=image,
        ports=[client.V1ContainerPort(container_port=80)])

    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": task_info.get('name')}),
        spec=client.V1PodSpec(containers=[container]))

    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=replicas,
        template=template)

    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    try:
        api_response = extensions_v1beta1.replace_namespaced_deployment(name = name, namespace=namespace, body = deployment)
        return api_response

    except ApiException as e:
        print(e)

## Core Api
def list_node():
    try:
        api_response = core_v1.list_node()
        return api_response
    except ApiException as e:
        print(e)

def list_node_requested_resources():
    # cpu, gpu unit 1
    # memory, gpu memory unit Ki M or G
    try:
        nodes = core_v1.list_node()
        requested  = []
        delete_key_list = [shared_gpu_name,exclusive_gpu_name,gpu_free_memory_name,shared_gpu_memory_name,shared_gpu_free_memory_name]
        memory_list = []

        # get gpu_info (gpu, shared-gpu, exclusive-gpu, gpu-memory)
        # for item in nodes.items:
        #     r = item.status.allocatable
        #     for k in delete_key_list:
        #         if k in r:
        #             del r[k]
        #     a = {}
        #     a["node_name"] = item.metadata.name
        #     a["resources"] = r
        #     allocatable.append(a)
        
        # get cpu and memory info

        for item in nodes.item:
            node_name = item.metadata.name
            podList = list_node_pod(node_name)
            for pod in podList.items:
                containers = pod.spec.containers
                for c in containers:
                    resources_limits = c.resources.limits  # type: dict(str, str)




    except ApiException as e:
        print(e)







def list_node_allocatable_resources():
    try:
        nodes = core_v1.list_node()
        allocatable = []
        delete_key_list = [shared_gpu_name,exclusive_gpu_name,gpu_free_memory_name,shared_gpu_memory_name,shared_gpu_free_memory_name]
        for item in nodes.items:
            r = item.status.allocatable
            for k in delete_key_list:
                if k in r:
                    del r[k]
            a = {}
            a["node_name"] = item.metadata.name
            a["resources"] = r
            allocatable.append(a)
        return allocatable
    except ApiException as e:
        print(e)


def list_node_pod(node_name):
    field_selector = "spec.nodeName="+node_name
    try:
        res = core_v1.list_pod_for_all_namespaces(include_uninitialized=True, field_selector=field_selector)
        return res
    except ApiException as e:
        print(e)


def list_deployment_pod(namespace, deployment_name):
    label_selector = 'app='+deployment_name
    try:
        res = core_v1.list_namespaced_pod(namespace=namespace, include_uninitialized=True, label_selector= label_selector)
        return res
    except ApiException as e:
        print(e)

def read_namespaced_pod_log():
    # TODO
    return

# Get container tty
def get_container_tty(namespace, pod, container=None):
    command = "kubectl -n {namespace} exec -it {pod}  {contianer} /bin/bash".format(namespace=namespace, pod=pod, container="" if container==None else "-c "+container)
    os.system(command)
