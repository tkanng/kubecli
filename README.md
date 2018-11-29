
submit and create a deployment for k8s 
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
$ python app.py submit --namespace=default --resource='{"cpu":"100m", "memory":"1Gi"}'  --name=redis --image=redis


delete a deployment for k8s
"""
    :param name: name of deployment
    {
        name: "redis"
    }
    
"""