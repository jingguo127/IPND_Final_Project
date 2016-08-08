# IPND_Final_Project
<h2>This project is the final project of Udacity Intro to Programming Nanodegree</h2>
<h3>How to set up</h3>
<p>
1. First you need to create a database called 'tournament4'in Postgresql. If you want to name it an other name,</br>
   please make sure that you have changed the default parameter of the connect method in <b>tournament.py</b>
</p>
<p>
2. Then navigate to the directory of those files, then open psql and use <b>\c tournament4</b> to connect the database.  
</p>
<p>
3. After you connect with the DB, type <b>\i tournament.sql</b> to create the initial tables and views.
</p>
<p>
4. All set up is done, you can run the <b>tournament_test.py</b> in python to test the program.
</p>
<p>
5. The <b>test.sql</b> is for conviently import an odd number of players and their two round matches' record.</br>
   in order to help users to test the 'bye' implementation. 
</p>
<h3>Version_1.3 changes</h3>
<p>
1. Entirely changed the database schema. Now the database only store the data of objective facts</br>
   such as id, name, matches' result.
</p>
<p>
2. Added a couple of views to support the aggregating and sorting.
</p>
<p>
3. Changed python code to fit for this schema design. No more spaghettis:)
</p>
