from application import app

#You can utilize the below block, when using the solution with docker-compose.yml.
if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True)


#For kubernetes, I am adding the port where the app is expected to run. 
#if __name__ == "__main__":
#   app.run(host="0.0.0.0", debug=True, port=5000)