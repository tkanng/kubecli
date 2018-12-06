from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
import util

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
gpu_devices_name = "nvidia.com/gpu-devices"

shared_cpu_name ='tusimple.com/shared-cpu'
exclusive_cpu_name = "tusimple.com/exclusive-cpu"

# extensionsV1beta1Api
# Tips: Deployment's pod only included 1 container
def create_deployment(task_info):
    name = task_info.get('name')
    image = task_info.get('image')
    replicas = task_info.get('replicas')
    namespace = task_info.get('namespace')
    resource = task_info.get("resource")
    # Configureate Pod template container
    # Container's name equals deployment's name
    container = client.V1Container(
        name = name,
        image = image,
        ports = [client.V1ContainerPort(container_port = 80)],
        resources=resource)
    # Create and configurate a spec section
    # Pod's name equals deployment's name
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
        if str(e.status) == "404" and e.reason =="Not Found":
            print("Deployment " + name + " not found.")
            return None
        else:
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
def get_pod_info(name, namespace):
    '''
    return: V1Pod
    '''
    res = core_v1.read_namespaced_pod(name, namespace)
    return res

def list_node():
    try:
        api_response = core_v1.list_node()
        return api_response
    except ApiException as e:
        print(e)


def list_node_allocated_resources():
    '''
    :return: dict(str(node_name), dict(resource_info))
    {'tusimple': {u'nvidia.com/gpu-memory': 0, u'nvidia.com/shared-gpu': 3, 'current_shared_physical_gpu': 3, 'current_used_gpu_memory': 0, 'current_exclusive_physical_gpu': 0}}
    '''
    try:
        nodes = core_v1.list_node()
        allocated  = {}
        for item in nodes.items:
            one_allocated={}
            node_name = item.metadata.name
            podList = list_node_pod(node_name)
            for pod in podList.items:
                containers = pod.spec.containers
                for c in containers:
                    resources_limits = c.resources.limits  # type: dict(str, str)
                    for k in resources_limits:
                        if one_allocated.get(k)!=None:
                            one_allocated[k] = one_allocated[k] + util.convert_str_to_num(resources_limits[k])
                        else:
                            one_allocated[k] = util.convert_str_to_num(resources_limits[k])
            r = item.status.allocatable
            physical_gpu = int(r[gpu_name]) if r.get(gpu_name)!=None else 0
            exclusive_gpu_allocatable = int(r[exclusive_gpu_name]) if r.get(exclusive_gpu_name)!=None else 0
            shared_gpu_allocatable = int(r[shared_gpu_name]) if r.get(shared_gpu_name) !=None else 0
            gpu_memory_capacity = util.convert_str_to_num(r[gpu_memory_name]) if r.get(gpu_memory_name)!=None else 0
            gpu_free_memory = util.convert_str_to_num(r[gpu_free_memory_name]) if r.get(gpu_free_memory_name)!=None else 0
            # physical gpu num
            current_shared_gpu_num = shared_gpu_allocatable - exclusive_gpu_allocatable
            # used gpu memory
            current_used_gpu_memory = gpu_memory_capacity - gpu_free_memory
            one_allocated["current_shared_physical_gpu"] = current_shared_gpu_num
            one_allocated["current_exclusive_physical_gpu"] = one_allocated[exclusive_gpu_name] if one_allocated.get(exclusive_gpu_name)!=None else 0
            one_allocated["current_used_gpu_memory"] = current_used_gpu_memory
            allocated[node_name] = one_allocated
        return allocated

    except ApiException as e:
        print(e)

# return dict{k:node_name, v:dict{}}
def list_node_allocatable_resources():
    '''
    :return: dict(str(node_name), dict(resource_info))
    {'tusimple': {u'ephemeral-storage': 37925506191, u'hugepages-1Gi': 0, u'tusimple.com/shared-cpu': 0, u'nvidia.com/gpu': 8, u'nvidia.com/gpu-memory': 93767860224, u'hugepages-2Mi': 0, u'tusimple.com/exclusive-cpu': 0, u'memory': 236562677760, u'GPU': 8, u'GPUMemory': 93767860224, u'pods': 110, u'cpu': 56}}
    '''
    try:
        nodes = core_v1.list_node()
        allocatable = {}
        delete_key_list = [shared_gpu_name,exclusive_gpu_name,gpu_free_memory_name,shared_gpu_memory_name,shared_gpu_free_memory_name,shared_cpu_name,exclusive_cpu_name,"GPU","GPUMemory"]
        for item in nodes.items:
            r = item.status.allocatable
            for k in delete_key_list:
                if k in r:
                    del r[k]
            for k in r:
               r[k] = util.convert_str_to_num(r[k])  # Convert quantity str to num 
            # Get GPU device detail
            gpus = item.metadata.annotations.get("GPUs")
            if gpus==None:
                r[gpu_devices_name] = ""
            else:
                r[gpu_devices_name] = gpus
            allocatable[item.metadata.name] = r
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
    # make sure that pod's label equals deployment name   
    label_selector = 'app='+deployment_name
    try:
        res = core_v1.list_namespaced_pod(namespace=namespace, include_uninitialized=True, label_selector= label_selector)
        return res
    except ApiException as e:
        print(e)

# Get container tty
def get_container_tty(namespace, pod, container=None):
    command = "kubectl -n {namespace} exec -it {pod}  {contianer} /bin/bash".format(namespace=namespace, pod=pod, container="" if container==None else "-c "+container)
    os.system(command)
