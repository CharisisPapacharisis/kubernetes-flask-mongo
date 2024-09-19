# Kubernetes-Flask-Mongo project

## Overview
This project focuses on developing a small ToDo App in Python with the `Flask` framework, and dockerizing it, so it can run as a Docker container in our `Kubernetes` cluster, minikube.
This includes setting up a `Dockerfile` for the Flask application, that dictates **how** the image will be build.

A Dockerfile is a script containing a set of instructions to build a Docker image. It defines the environment and dependencies required for your application to run, such as the base OS, libraries, code, etc. It is primarily used to build a **single container**. It defines the image in **layers**, where each instruction adds a new layer on top of the previous one. This makes the image lightweight and efficient. Running a Dockerfile produces the same result every time, ensuring **consistent environments**.

As the backend of the flask application, we are using `MongoDB`. It also runs as a container in the cluster, and the official DockerHub image is used for that.


## Containerization 
I have followed three alternatives when it comes to deploying the frontend and backend in the cluster:

- docker-compose.yml file
- Kubernetes YAML files
- helm charts

The purpose of this was to experiment with different modes of containerization.

### Docker-Compose
Docker Compose is a tool for defining and running multi-container Docker applications. It allows you to manage multiple services (e.g., web server, database, cache) using a single configuration file, typically `docker-compose.yml`. It is primarily used for **local development** or smaller projects that don’t require complex orchestration or scaling.

**Key Features**
- `Multi-Container Setup`: Defines how multiple containers (services) like a web app, database, and cache work together.
- `Simple Networking`: It automatically creates a network for the services, making it easier for containers to communicate.
- `Volumes`: Supports mounting directories as volumes for persistent data.
- `Dependency Management`: Supports starting containers in a specific order using "depends_on".


### Kubernetes YAML
Kubernetes YAML files are used to describe and manage the desired state of Kubernetes objects like pods, services, deployments, and configmaps.
Kubernetes is a highly scalable orchestration platform for managing containers across a distributed system, typically used in production environments.
Kubernetes is ideal for **large-scale production deployments** where you need high availability, fault tolerance, and orchestration across multiple nodes (servers). It is used for cloud-native applications, microservices, and large distributed systems.

**Key Features**
- `Advanced Orchestration`: Supports scaling, load balancing, rolling updates, self-healing, and auto-recovery.
- `Declarative Configuration`: Defines the desired state (e.g., how many replicas, what image to use), and Kubernetes ensures the system matches that state.
- `Service Discovery and Networking`: Kubernetes handles networking between services via internal service discovery.
- `Volume Management`: Manages persistent storage via Kubernetes volumes or external cloud storage.


### Helm Chart
Helm is a package manager for Kubernetes. Helm uses charts (templates of Kubernetes YAML files) to deploy and manage applications.
Helm simplifies Kubernetes deployments by allowing you to reuse and manage complex sets of YAML files with more flexibility and configurability.
Helm is useful for **complex applications** that need reusable, configurable, and maintainable deployments. It’s particularly helpful when managing **large Kubernetes clusters** with multiple environments, services, and configurations.

**Key Features**
- `Templating`: Helm allows you to parameterize and template Kubernetes YAML files, making it easier to manage different environments (development, production) with one set of configuration files. Helm templates allow you to reuse your Kubernetes manifests across different environments by changing just a few values (e.g., image tag, replica count).
- `Versioning`: Helm provides versioning for charts, so you can manage upgrades and rollbacks easily.
- `Packaging`: Helm Charts package up Kubernetes resources (deployments, services, configmaps) into a single, reusable bundle.
- `Lifecycle Management`: Helm makes it easier to manage the lifecycle of Kubernetes applications, including upgrades, rollbacks, and deletion.


## Flask Application

This is the application folder structure: 
```
application/
│
├── static/
│   └── (image files for the app, like logos or icons)
│
├── templates/
│   ├── base.html
│   ├── list_todo.html
│   └── add_todo.html
│   └── update_todo.html
│
└── init.py
```

**Steps to reproduce**
- Create a folder for your project. This folder will contain all the files and subfolders needed for your Flask app.
- Set up a virtual environment for isolating your dependencies (Python, Flask, MongoDB driver, etc).
- Activate virtual env: 
```bash
venv\Scripts\activate
```
- Install required dependencies: 
```bash
pip install Flask pymongo
```
- Create init.py and subfolders
- Add your HTML templates to the `templates/` folder. These will be used to render different views for the to-do app (e.g., list, add, update tasks).
    - base.html: the base for the html page, including styling.
    - list_todo.html: Displays the list of to-do items.
    - add_todo.html: A form for adding new to-do items.
    - update_todo.html: A form for updating existing to-do items.
- Add any static assets (e.g. logos) in the `static/` folder.


**Explanation of init.py**

Initializes the Flask app. Then creates the connection to MongoDB, and tests that it is a successful connection. 
The MongoDB URI, username, and password are retrieved from environment variables using `os.getenv()`.
Then the code points to the "my_db" database and the "todos" collection where all your to-do items will be stored.

**Routes and Views**

- Home Route (/): Displays all the to-do items.
- Add New To-Do Item (/add): Displays a form for adding a new to-do item and handles the form submission. This route handles both GET (displaying the form) and POST (submitting the form) requests. The submitted data is inserted into the MongoDB collection.
- Delete To-Do Item (/delete/<id>): Deletes a specific to-do item based on its ID.
- Update To-Do Item (/update/<id>): Displays a form to update a specific to-do item and handles the form submission.


By default, Flask will run on http://127.0.0.1:5000/. You can visit this URL in a web browser to interact with your to-do list application.

If you want to create an image of the application, as per the Dockerfile, you can run:
```bash
docker build -t todoapp:1.0 .
```

## How to build images & run in containers

### Docker-Compose

To build both images (Flask app & mongoDB) at once, thanks to docker-compose, you can run:
```bash
docker-compose up --build 
```

This will pull the MongoDB image, and build both images. 

You can see the images being created by: 
```bash
docker images
```

Checking the containers that are running in your docker environment: 
```bash
docker ps
```

### Kubernetes YAML 

start your minikube cluster:
```bash
minikube start 
```

To ensure that Minikube can access the Docker image you've built locally, you can configure your terminal to use the Docker daemon inside Minikube. This allows you to build your images directly within the Minikube environment.

Run the following command:
```bash
eval $(minikube docker-env)
```

After running the above command, build your Docker image again. This time it will be available in Minikube's Docker registry:
```bash
docker build -t todoapp:1.0 .
```

You can now verify that, by:
```bash
docker ps
```

Create the namespace "development":
```bash
kubectl create namespace development
```

Ensure that minikube is running, and move to the path with all Kubernetes manifests/yaml files. You can "apply" all files:
```bash
kubectl apply -f .
```

In terms of the secrets (MongoDB credentials), you will need to encode them in base64 in advance, and add them in your "secret" yaml files.
Notice in the flask_app.yml that the references to the backend (client, username, password) are passed to container as environmental variables, within the "spec" block. In turn, these env variables are getting their value from the configmap and secret manifest files.

Now you can verify the available resources in Kubernetes, e.g. by running:

`kubectl get deployments`

`kubectl get pods`

`kubectl get services`

`kubectl get secrets`

`kubectl get configmaps`

In order to avoid providing the namespace argument, you can opt to switch content:
```bash
kubectl config set-context --current --namespace=development
```

You can also see details of a running pod, e.g.
```bash
kubectl describe pod [PODNAME]
``` 
or troubleshoot one, by looking at its logs: 
```bash
kubectl logs [PODNAME]
```
or log into a container running in the cluster, with the mongo shell (mongosh): 
```bash
kubectl exec -it <mongodb_pod_name> -- mongosh -u <username> -p <password> --authenticationDatabase admin
```

Some commands that you can run, after connecting to mongodb: 

`show dbs`

`use my_db`

`show collections`

Choose your collection and type the following to see all contents of that collection:

`db.todos.find()`

Now that everything has been deployed, you can access the UI of the app, by finding its service, and forwarding it to localhost:
```bash
minikube service flask-service-np -n development
```

At the end, you can delete all resources: 
```bash
kubectl delete all --all -n development
```


### Helm Charts

As said above, Helm is a package manager for Kubernetes that allows you to define, install, and upgrade applications using **charts**. 
A Helm **template** is a component of a Helm chart. It uses the Go templating engine to generate Kubernetes YAML manifests dynamically, based on customizable values provided by the user.

A **Helm chart** is essentially a **collection of files that define a Kubernetes application**. It typically includes:
- `templates/ directory`: Contains template files for resources like Deployments, Services, ConfigMaps, Secrets, etc.
- `values.yaml`: Default configuration values that can be overridden during installation or upgrade.
- `Chart.yaml`: Metadata about the chart (name, version, etc).

Using Helm templates, you can define a reusable set of Kubernetes manifests that can be parameterized for different environments (dev, staging, production, etc.) by passing values.

Firstly, install helm:
```bash
choco install kubernetes-helm  # For Windows
```

Then, create a new Helm chart for your application:
```bash
helm create helm-todoapp
```

This will create a directory structure like this:
```
helm-todoapp/
  ├── charts/
  ├── templates/
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   ├── configmap.yaml
  │   └── secret.yaml
  ├── values.yaml
  └── Chart.yaml
```
Replace the default Kubernetes resource templates (e.g. Deployments, Services) inside the `templates/` folder with your own, and use template variables to allow customization.
You can set those values as you prefer, utilizing the `values.yaml` file.

In terms of the secrets (MongoDB credentials), you will need to encode them in base64 in advance, and add them in your "secret" yaml template.

Create the namespace development
```bash
kubectl create namespace development
```

Once you've set up the Helm chart, you can install it with `helm install <release-name> ./helm-todoapp`, e.g.
```bash
helm install todoapp ./helm-todoapp
```

**Note**: A Helm `release` is an instance of a Helm `chart` running in your Kubernetes cluster. You can think of it as a deployment of your application (or set of Kubernetes resources) using a Helm chart. Multiple releases can be created from the same Helm chart, each with different configurations or even different versions.

List all releases:
```bash
helm list
```

If you're updating the chart, at a later stage, you can do:
```bash
helm upgrade todoapp ./helm-todoapp
```

Helm will generate the Kubernetes YAML from the templates and apply them to your cluster.

As before, now that everything has been deployed, you can access the UI of the app, by finding its service, and forwarding it to localhost:
```bash
kubectl get svc
minikube service todoapp-flask-service-np -n development
```

You can add your own todo tasks!

At the end, you can delete all resources. Find firstly which Helm releases are deployed to the cluster:
```bash
helm list
```

Use the helm uninstall command followed by the release name to remove the deployment and all associated resources:
```bash
helm uninstall todoapp
```

If the Helm release is in a specific namespace (other than the default), you can include the -n flag to specify the namespace:
```bash
helm uninstall todoapp -n development
```