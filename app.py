import fire
from api import *

class client(object):


    def submit(self, namespace, name, image, resource):
        """
          :param task_info: a dict representing the detail of a task, e.g.
               {
                   namespace: "default"
                   image: "redis",   # required
                   resource: {
                       cpu: 2000m,
                       gpu: 2000m,
                       mem: 2Gi
                   },
        """
        task_info = {}
        task_info['namespace'] = namespace
        task_info['name'] = name
        task_info['image'] = image
        task_info['resource'] = resource

        create_deployment(task_info)

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
        task_info['deploy_name'] = name
        task_info['namespace'] = namespace

        delete_deployment(task_info)

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
        """
        task_info = {}
        resp = get_deployments_info(task_info)
        print(resp)


if __name__ == '__main__':
    fire.Fire(client)
