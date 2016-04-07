# AMD-GPU-INFO
View the current stats of your AMD GPU on your machine or every machine on you network

- Network Installation:
  - On master computer:
    - install Node.js
    - cd into server folder
    - run 'node server.js'
      - if a specific port or ip address is needed, open server.js and edit the port number or ip address
  - In browser, navigate to http://your_ip:your_web_port (Ex. http://192.168.1.140:8080)
    - default ports:
      - Web Server port: 8080 (Used to connect to server through browser)
      - Socket port: 8081 (Used on client machines when promted)
    - Add ip addresses of slave/worker computers or devies in ip accesslists
  - On Client machines:
    - run runable.exe
      - or install python and run 'python runable.py'
    - Enter the server machine's ip address
    - Enter the server machine's socket port number(Default:8081)
    - Enter the name for this machine
  

- Single Machine Installation:
  - Run runable.exe
  - or install python and run 'python runable.py'
  
- Details:
  - Clients send data every 5 seconds
  - Server refreshes 'Overview' page details every 5 seconds
  - Uses ADL found here https://github.com/mjmvisser/adl3
  - Python is required on all client machines or single installations
  - Node.js is required only on server machine
  - DO NOT RUN CLIENT BEFORE YOU ADD THEIR IP ON THE SERVER
  - Shut down the client before you shut down the server
    - No error detection is used when sockets abbrutly close, this may be implemented at a later time
  - Shut down server with ctrl + c in server machine's terminal or command prompt
