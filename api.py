from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config("./config.yaml")
extensions_v1beta1 = client.ExtensionsV1beta1Api()
core_v1 = client.CoreV1Api()

def create_deployment(task_info):
    name = task_info.get('name')
    image = task_info.get('image')
    replicas = task_info.get('replicas')
    namespace = task_info.get('namespace')

    # Configureate Pod template container
    container = client.V1Container(
        name = name,
        image = image,
        ports = [client.V1ContainerPort(container_port = 80)])

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


def list_node():
    try:
        api_response = core_v1.list_node()
        return api_response
    except ApiException as e:
        print(e);
