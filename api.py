from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config("./config.yaml")
extensions_v1beta1 = client.ExtensionsV1beta1Api()

def create_deployment(task_info):
    # Configureate Pod template container
    container = client.V1Container(
        name=task_info.get('name'),
        image=task_info.get('image'),
        ports=[client.V1ContainerPort(container_port=80)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": task_info.get('name')}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=3,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=task_info.get('name')),
        spec=spec)

    try:
        api_response = extensions_v1beta1.create_namespaced_deployment("default", body=deployment)
    except ApiException as e:
        print(e)

def delete_deployment(DEPLOYMENT_NAME):
    # Delete deployment
    try:
        api_response = extensions_v1beta1.delete_namespaced_deployment(
            name=DEPLOYMENT_NAME,
            namespace="default",
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
    except ApiException as e:
        print(e)



