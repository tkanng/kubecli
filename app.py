import fire
from api import *

class client(object):


    def submit(self, namespace, name, image, resource, replicas):
        """
          :param task_info: a dict representing the detail of a task, e.g.
               {
                   namespace: "default"
                   image: "redis",
                   resource: {
                       cpu: 2000m,
                       gpu: 2000m,
                       mem: 2Gi
                   },
                   replicas: 3
               }
        """
        task_info = {}
        task_info['namespace'] = namespace
        task_info['name'] = name
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

    def get_deployments(self, namespace):
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

    def get_deployments(self):
        """
            :param namespace: get_deployments_info_for_all_namespace, none args needed for this query
            :return:
            {
                ...
            }
        """
        task_info = {}
        resp = get_deployments_info(task_info)
        print(resp)

    def get_deployment(self, name, namespace):
        """
            :param name namespace: get one deployment
            :return:
            {
                ...
            }
        """
        task_info = {}
        task_info['name'] = name
        task_info['namespace'] = namespace
        resp = get_deployment_info(task_info)
        print(resp)

if __name__ == '__main__':
    fire.Fire(client)
