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

    def delete(self, name):
        """

            :param name: deploy_name
            :return:
        """
        task_info = {}
        task_info['deploy_name'] = name

        delete_deployment(task_info)

if __name__ == '__main__':
    fire.Fire(client)
