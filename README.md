This project receives the Interpol red notice data from the Interpol API, parses it and sends it to the RabbitMQ queue.
Pika is used to send and receive data to the queue. The data from the queue is collected in a delta database and it is checked for changes in the data with comparisons. It provides access to the endpoints prepared for it according to the update status. SQLite is used as the database. The application publishes the data in an HTML page prepared with Flask. Changes detected with the Delta database will be given as a warning on this HTML page.


Clone the repository

- git clone https://github.com/eliften/Interpol_Api

- cd Interpol_Api

Build the Docker image and start the containers

- docker-compose up --build
