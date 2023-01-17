
# Fetch Rewards:

  

## Data Engineering Take Home: ETL off a SQS Queue

  

### Table of Contents:

0. Foreword

1. Environment Setup

a. Setting up Python3 Environment

b. Setting up Docker Environments

2. Execute Code

3. Further Questions

4. About the Person Behind the Code 🙋🏻‍♂️👨🏻‍💻

---

### 0. Foreword

I just quickly wanted to give you a heads-up that this was made and tested on macOS. Furthermore, this guide will be made for macOS. It should work on Windows, but the setup and running the code might be different. If you are on Linux, it will be mostly similar, except for installing Docker.

  

---

### 1. Environment Setup

#### a. Setting up Python3 Environment

Setting up your Python3 environment should be super simple. First, if you haven't already, open up the Terminal of your preference. Then, if you haven't already, download Homebrew using this command ```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```. This is a package manager, similar to apt-get on Linux. If you don't know what that is, it's like a command line app store. Now install Python3 using the command ```brew install python3```. It might auto update before installing, that's okay, just let it do its thing. Once it's done, you should be able to use pip3 and python3 to do the rest.

  

Before going further, let's quickly download the GitHub repository. This can be done in two ways, you could just use the download button, or paste this command in your terminal

```git clone https://github.com/JulianBeaulieu/Fetch-Rewards-Data-Engineering-Take-Home.git``` this is gonna take a second. Once it's done, cd into the repository (```cd Fetch-Rewards-Data-Engineering-Take-Home```). We are almost there, finally we need to install the packages required to run the python code. Simply do this by running the command ```pip3 install -r requirements.txt```. This should hopefully install everything you need to run the code!

  

#### b. Setting up Docker Environments

Setting up docker is quite easy on macOS. Simply go to the

[Docker](https://docs.docker.com/desktop/install/mac-install/) website and download the right version for your Mac. After downloading the Docker app, double click on the Docker.dmg file, and then drag and drop the file into your **Application** folder. After it has finished copying the file into your folder, double click to open up docker and make sure the app works. Once that is done, open up the terminal of your choosing. Type the command ``` which docker``` in your terminal and look for a response saying something similar to ```/usr/local/bin/docker```. Really, you are looking for anything which is a file path and not an error.

  

Now that we know that we have Docker installed, we need to download the Docker Images, which we will need to run the app. These two Docker Images contain the SQS server and the Postgres Server. To do that, paste the following two commands in your terminal: ```docker pull fetchdocker/data-takehome-postgres``` and ```docker pull fetchdocker/data-takehome-localstack```. Wait until the downloads have completed (This might take a minute).<br><br>

<img  src="images/waiting.gif"  alt="Waiting"  style="width:200px;"/>

<br>

Done? Great!<br>

  

Now we need to install one or two more things. First, we need to install postgres on our mac using homebrew: ```brew install postgresql```. Next, we need to install the AWS CLI: ```pip3 install awscli-local```.

  

The last thing we need to do is start up the servers using docker. To do this, cd to the GitHub repository we downloaded previously, then run the following command ```docker compose up ``` and that's it! Now you should be able to use the servers.

  

If you want to see the Data in the Postgres server, enter this command ```psql -d postgres -U postgres -p 5432 -h localhost -W``` in your terminal, and enter the password ```postgres```. You should now see that the input type changes to look like this: ```postgres=#```, this is how you know you have successfully connected to the Postgres database and are able to run commands. To see a current snapshot of what is in the database, simply enter ```SELECT * FROM user_logins;```. This should give you a nice table view of the current ... well ... table.

  

---

### 2. Execute Code

If you made it until here, executing the code is a piece of cake. Simply run ```python3 Driver.py```. It will automatically start the code and let you know that it's running and that you can stop it at anytime by hitting any key, or by pressing ```ctrl``` + ```c```. After it is done transferring the data from the SQS server to the Postgress server, it will ask you if you would like to see the contents of the table it just wrote too. You can enter y or n, to either see it or not. After that, the program ends.

  

---

### 3. Further Questions

 - How would you deploy this application in production?
	 - There are a couple of ways I would run  this in production, all of which will depend on how much data is being created. If it's not that much, I would schedule a server to run this once a day during off-peak hours, to not stress the systems more than it has to. If a lot of data is created, it might make more sense  to periodically check the SQS queue for fullness and then run the script. If the amount of data being created is so much, that the script would be started constantly, it might make sense to actually dedicate a small server instance to it, to continually grab the information off of the SQS queue. Really all depends on how quickly data is gathering. 
	 
 - What other components would you want to add to make this production ready?
	 - I would want to discuss the masking of data with the data scientist who will be working with this data. Currently, I implemented two different algorithms which can be switched by adding a parameter in the code. The first one is by taking a string and returning the byte array as an integer. The second way is by using sha256 to encode the string. Both of these can be decoded if desired, but sha256 might be more unique than the first method. This is definitely something  I would want to update to make this production ready.
	 - I think  concerning adding things,  I would add more try/except blocks to make sure it can handle a wider variety of errors and thus prevent it from crashing and burning.

 - How can this application scale with a growing dataset. 
	 - In principle this should be quite easy to scale. The first way to do this is to simply run more instances of the script. It's single threaded, so unless you have a single thread available, this should run nicely on a normal CPU. The bottleneck here could become the AWS and the Postgres server, since they might get overwhelmed by requests. Alternatively, one could multi-thread the fetching, masking and inserting using jobs. To not have to run multiple instances of the same script.
   
 - How can PII be recovered later on?
	 - To decode ```int.from_bytes(value.encode(), 'little')``` one could use python code similar to ```encoded_value.to_bytes(len(value), 'big').decode()```
	 - If  ```hashlib.sha256(value.encode()).hexdigest()``` is used, one would need to have the original inputs, such as ``device_id``   and then match the masked value to the newly created hash. This makes it very secure to store, but hard to recovered if the original input is lost. I added this in the event that the first way was not secure enough, though this might be too secure.
	 
 - What are the assumptions you made?
	 - One assumption I made is that using Python3 is fast enough. Python3 is by far not the fastest language out there, so if speed is important, this might need to be re-implemented in something like Java or C++. I heard that Rust is incredibly quick as well, but I have never worked with Rust before, so I can't really talk to the benefits of using that over something like Java or C++.
	 - Another assumption I made is that this is made to be run by a person, and not continuously on a server in production. If this was supposed to be run in production, I would not add the option to see the table after it finishes running. I would probably also change the output, and maybe add some other output to let an engineer know it's running and hasn't encountered any issues. And  if it does, it should output it and continue working if it still can. Maybe even add a function that notifies an engineer if an error is encountered so that they can look into it. This is something we did a lot at Amazon when I interned there.
	 - The ``user_logins`` table has a field called ``create_date``. I was not able to find a ``create_date`` in any of the responses from the AWS SQS Queue server, so I set that field to the date on which the code was run. I also only added month, day, and year. This is something that can be changed in the future and something I would ask the data scientist how they would like to have as it is a very quick fix to make.

---

### 4. About the Person Behind the Code 🙋🏻‍♂️👨🏻‍💻
Hey there, I just wanted to introduce myself, and say thank you for considering me for the position of Data Engineer. I really enjoyed this take home exercise, it's definitely a nice change from the Hackerrank challenges!

My name is Julian Beaulieu and I just graduated from Texas A&M University with a Masters of Science in Computer Science. I have had an internship at Amazon, which I really enjoyed, and I have done a plethora of side projects. Such as working with a non-profit, doing some minor freelance work, or just building things like my app LinkHub because I saw the need for it. I really like machine learning, and data science, but I also do occasionally enjoy building websites and apps. 

Anyway, thank you again for taking your time to read through this README, I tried to make it as verbose as possible because sometimes it's easier to dumb things down than to assume someone knows it and then it takes extra long to fill in that gap. I also made the comments a bit more verbose than I would typically make them to make following the code a bit easier, I do hope it would also be more or less understandable without most of them. I hope you have a great rest of your day!

~ Julian 